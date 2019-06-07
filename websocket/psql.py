#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys
import select
import psycopg2.extensions


class Database:
    def __init__(self):
        self.host = 'localhost'
        self.port = '8888'
        self.dbname = 'ws'
        self.user = 'postgres'
        self.password = 'postgres'
        self.binding_channel = 'watch_realtime_table'
        connection_str = "host='"+self.host+"' "
        connection_str += "port='" + self.port+"' "
        connection_str += "dbname='" + self.dbname+"' "
        connection_str += "user='"+self.user+"' "
        connection_str += "password='"+self.password+"'"
        self.con = None
        try:
            self.con = psycopg2.connect(connection_str)
            self.cur = self.con.cursor()
            self.con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
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
        rows = []
        try:
            self.cur.execute(sql, params)
            # self.con.commit()
        except Exception as e:
            print(e)
        return rows

    def fetch_sql(self):
        rows = []
        try:
            self.cur.execute(sql, params)
            rows = self.dictfetchall(self.cur)
        except Exception as e:
            print(e)
        return rows

    def teardown(self):
        if self.con:
            self.con.close()

    def binding(self):
        self.cur.execute("LISTEN "+self.binding_channel+";")

        print("Waiting for notifications on channel '%s'"%(self.binding_channel))
        while True:
            if select.select([self.con], [], [], 5) == ([], [], []):
                print("Timeout")
            else:
                self.con.poll()
                while self.con.notifies:
                    notify = self.con.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid,
                          notify.channel, notify.payload)


db = Database()
db.binding()
# db.execute("INSERT INTO realtime_table (title, year, producer) VALUES ('UA502', 'Bananas', '1971-07-13');")
