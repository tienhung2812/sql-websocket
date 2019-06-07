import asyncio
import json
import logging
import websockets
import utils
import settings


class Notify:
    def __init__(self):

        self.STATE = {'value': 0}
        
        self.USERS = set()

        self.watch_table = {}


