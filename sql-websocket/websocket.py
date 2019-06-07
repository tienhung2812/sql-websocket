#!/usr/bin/env python

import asyncio
import json
import logging

import websockets

import notify
import settings
from db import psql

logging.basicConfig()


class Websocket:
    def __init__(self):
        self.host = settings.WEBSOCKET['HOST']
        self.port = settings.WEBSOCKET['PORT']
        self.db = psql.Database(
            host = settings.DATABASES['HOST'],
            port = settings.DATABASES['PORT'],
            dbname= settings.DATABASES['NAME'],
            user= settings.DATABASES['USER'],
            password= settings.DATABASES['PASSWORD']
        )

        self.db.connect()

        self.watch_list = {}


    def binding(self,table,action):
        wt = db.create_binding_function(table,action)
        self.watch_list[wt.name] = wt
        return wt

    def start_binding(self,wt):
        db.binding_callback(wt,callback)

    def start(self):   
        try:
            if settings.SSL:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(
                pathlib.Path(__file__).with_name(settings.PEM_PATH))

                start_server = websockets.serve(
                    notify.Notify.database_notify, self.host, self.port, ssl=ssl_context)
            else:
                start_server = websockets.serve(notify.Notify.database_notify, self.host, self.port)

            print("Websocket is running on %s:%s"%(self.host,self.port))
            asyncio.get_event_loop().run_until_complete(
                start_server)
            asyncio.get_event_loop().run_forever()
            
        except KeyboardInterrupt:
            print("\nStopping Websocket")
