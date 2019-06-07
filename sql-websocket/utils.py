from db import psql
import settings

class DatabaseUtils:
    def __init__(self):
        db = psql.Database(
            host = settings.DATABASES['HOST'],
            port = settings.DATABASES['PORT'],
            dbname= settings.DATABASES['NAME'],
            user= settings.DATABASES['USER'],
            password= settings.DATABASES['PASSWORD']
        )

        db.connect()

        self.watch_list = {}

    def create_binding(self,table,action):
        wt = db.create_binding_function(table,action)
        self.watch_list[wt.name] = wt

    def start_binding(self,wt,callback):
        db.binding_callback(wt,callback)

    def __exit__(self, exc_type, exc_value, traceback):
        db.teardown()

