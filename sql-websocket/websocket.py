#!/usr/bin/env python

import asyncio
import json
import logging
import threading
import websockets
import select
import time
from message import Message
import settings
from db import psql

logging.basicConfig()


class Websocket:
    def __init__(self):
        self.host = settings.WEBSOCKET['HOST']
        self.port = settings.WEBSOCKET['PORT']
        self.db = psql.Database(
            host=settings.DATABASES['HOST'],
            port=settings.DATABASES['PORT'],
            dbname=settings.DATABASES['NAME'],
            user=settings.DATABASES['USER'],
            password=settings.DATABASES['PASSWORD']
        )

        self.db.connect()
        self.db.create_notify_channel()
        self.channel_name = settings.DB_CHANNEL_NAME
        self.function_name = settings.DB_FUNCTION_NAME

        t = threading.Thread(target=self.start_binding)
        t.start()


        self.watch_list = {}
        self.STATE = {'value': 0}
        self.USERS = set()
        self.thread = []
        self.watch_table = {}

    def get_table_from_user_path(self, path):
        # For example '/user/table'
        try:
            return path.split('/')[2]
        except:
            print("Path not valid")
            return None

    def state_event(self):
        return json.dumps({'type': 'state', **self.STATE})

    def users_event(self):
        return json.dumps({'type': 'users', 'count': len(self.USERS)})

    async def notify_state(self, table, message):
        """[Notify state]

        Arguments:
            table {[type]} -- [description]
            message {[type]} -- [description]
        """
        if self.watch_list[table]['USERS']:       # asyncio.wait doesn't accept an empty list
            await asyncio.wait([user.send(message) for user in self.watch_list[table]['USERS']])

    async def notify_users(self, table):
        """[Notify user]

        Arguments:
            table {[type]} -- [description]
        """
        if self.watch_list[table]['USERS']:       # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await asyncio.wait([user.send(message) for user in self.watch_list[table]['USERS']])

    async def register(self, websocket, path):
        """[Register user into table watch list]

        Arguments:
            websocket {[type]} -- [description]
            path {[type]} -- [description]
        """

        table = self.get_table_from_user_path(path)
        if table not in self.watch_list:
            self.binding(table, 'ALL')

        self.watch_list[table]['USERS'].add(websocket)
        await self.notify_users(table)

    async def unregister(self, websocket, path):
        """[Unregister user into table watch list]

        Arguments:
            websocket {[type]} -- [description]
            path {[type]} -- [description]
        """

        table = self.get_table_from_user_path(path)

        self.watch_list[table]['USERS'].remove(websocket)
        await self.notify_users(table)

    def notify(self, notify):
        msg = Message(notify)
        print(msg.get_message_in_str())

    def start_binding(self):
        """[Create binding on a channel]

        Keyword Arguments:
            binding_channel {str} -- [Channel name] (default: {'watch_realtime_table'})
        """
        channel = self.channel_name
        print("Start binding channel %s" % channel)
        self.db.cur.execute("LISTEN "+channel+";")

        print("Waiting for notifications on channel '%s'" %
              (channel))

        while True:
            if select.select([self.db.con], [], [], 5) == ([], [], []):
                print("Timeout: %s" % channel)
            else:
                self.db.con.poll()
                while self.db.con.notifies:
                    notify = self.db.con.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid,
                          notify.channel, notify.payload)
                    self.notify(notify)

    def add_table_to_watch_list(self, watch_table):

        self.watch_list[watch_table.table] = {}
        self.watch_list[watch_table.table][watch_table.name] = watch_table

    def binding(self, table, action):
        try:
            actions = action
            if action.upper() == 'ALL':
                actions = ['INSERT', 'UPDATE', 'DELETE']
            
            wt = self.db.create_binding_function(table, actions)
            if wt:
                self.add_table_to_watch_list(wt)
                # time.sleep((0.05))
            self.watch_list[wt.table]['USERS'] = set()

        except Exception as e:
            print("BINDIND ERROR ", e)

    def process_data(self, data, path):
        # if path in self.watch_table:
        pass

    async def database_notify(self, websocket, path):
        # register(websocket) sends user_event() to websocket
        if 'user' in path:
            await self.register(websocket, path)
        try:
            await websocket.send(self.state_event())
            async for message in websocket:
                data = json.loads(message)

                self.process_data(data, path)
        finally:
            if 'user' in path:
                await self.unregister(websocket, path)

    def start(self):
        try:
            if settings.SSL:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(
                    pathlib.Path(__file__).with_name(settings.PEM_PATH))

                start_server = websockets.serve(
                    self.database_notify, self.host, self.port, ssl=ssl_context)
            else:
                start_server = websockets.serve(
                    self.database_notify, self.host, self.port)

            print("Websocket is running on %s:%s" % (self.host, self.port))
            asyncio.get_event_loop().run_until_complete(
                start_server)
            asyncio.get_event_loop().run_forever()

        except KeyboardInterrupt:
            print("\nStopping Websocket")
