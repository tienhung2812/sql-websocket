#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys
import select
import psycopg2.extensions


class Database:
    def __init__(self, host='localhost', port='8888', dbname='ws', user='postgres', password='postgres'):
        """Initial Database utils

        Keyword Arguments:
            host {str} -- [Host url] (default: {'localhost'})
            port {str} -- [Port] (default: {'8888'})
            dbname {str} -- [Database name] (default: {'ws'})
            user {str} -- [User] (default: {'postgres'})
            password {str} -- [Password] (default: {'postgres'})
        """
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

        self.watch_list = []

        self.binding_channel = 'watch_realtime_table'

    def connect(self):
        """[Connect to database]
        """
        connection_str = "host='"+self.host+"' "
        connection_str += "port='" + self.port+"' "
        connection_str += "dbname='" + self.dbname+"' "
        connection_str += "user='"+self.user+"' "
        connection_str += "password='"+self.password+"'"

        self.con = None
        try:
            self.con = psycopg2.connect(connection_str)
            self.cur = self.con.cursor()
            self.con.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        except psycopg2.DatabaseError as e:
            if self.con:
                self.con.rollback()

            print('Error %s' % e)
            sys.exit(1)

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        res = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        return res

    def execute(self, sql, params=[]):
        """[Execute SQL command]

        Arguments:
            sql {[type]} -- [SQL command]

        Keyword Arguments:
            params {list} -- [description] (default: {[]})
        """
        try:
            self.cur.execute(sql, params)
            # self.con.commit()
        except Exception as e:
            print(e)

    def fetch_sql(self):
        """[Query data]

        Returns:
            [list] -- [Query result]
        """
        rows = []
        try:
            self.cur.execute(sql, params)
            rows = self.dictfetchall(self.cur)
        except Exception as e:
            print(e)
        return rows

    def teardown(self):
        """[Close database connection]
        """
        if self.con:
            self.con.close()

    def binding(self, watch_table):
        """[Create binding on a channel]

        Keyword Arguments:
            binding_channel {str} -- [Channel name] (default: {'watch_realtime_table'})
        """
        channel = watch_table.channel_name

        self.cur.execute("LISTEN "+channel+";")

        print("Waiting for notifications on channel '%s'" %
              (channel))
        while True:
            if select.select([self.con], [], [], 5) == ([], [], []):
                print("Timeout")
            else:
                self.con.poll()
                while self.con.notifies:
                    notify = self.con.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid,
                          notify.channel, notify.payload)

    def binding_callback(self, watch_table, callback):
        """[Binding with call back]

        Arguments:
            watch_table {[Watch Table]} -- [Watch Table Object]
            callback {function} -- [Callback function]
        """

        channel = watch_table.channel_name
        self.cur.execute("LISTEN "+channel+";")

        print("Waiting for notifications on channel '%s'" %
              (self.binding_channel))

        while True:
            if select.select([self.con], [], [], 5) == ([], [], []):
                print("Timeout")
            else:
                self.con.poll()
                while self.con.notifies:
                    notify = self.con.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid,
                          notify.channel, notify.payload)

                    callback(notify)

    def create_binding_function(self, table, action):
        """[Create binding function]

        Arguments:
            table {[str]} -- [Table name]
            action {[str]} -- [On action]
        """

        wt = WatchTable(table,action)
        sql = """CREATE FUNCTION %(function_name)s() RETURNS trigger AS $$
            DECLARE
            BEGIN
                PERFORM pg_notify('%(channel_name)s', row_to_json(NEW)::text);
                RETURN new;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER %(trigger_name)s AFTER %(action)s ON %(table)s
            FOR EACH ROW EXECUTE PROCEDURE %(function_name)s();""" % {
                "function_name": wt.function_name,
                "trigger_name": wt.trigger_name,
                "channel_name": wt.channel_name,
                "table": wt.table,
                "action": wt.action
                }
        self.execute(sql)
        self.watch_list.append(wt)
        return wt

class WatchTable:
    def __init__(self,table, action):
        self.table = table
        self.name = '%(table)s_on_%(action)s'%{'table':table, 'action':action}
        self.function_name = 'notify_trigger_%s' % self.name
        self.trigger_name = 'watch_%s_trigger' % self.name
        self.channel_name = 'watch_%s_table' % self.name
        self.action = action

    def __str__(self):
        return self.name

# db = Database()
# db.connect()
# db.create_binding_function('realtime_table','UPDATE')
# db.binding()
# db.execute("INSERT INTO realtime_table (title, year, producer) VALUES ('UA502', 'Bananas', '1971-07-13');")