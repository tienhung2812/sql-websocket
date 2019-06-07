import os
import datetime
import pwd

DATABASES = {
    'NAME': 'ws',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'localhost',
    'PORT': '8888'
}

SSL = False
PEM_PATH = None

WEBSOCKET = {
    'HOST': '0.0.0.0',
    'PORT': '6789'
}
