import json

class Message:
    def __init__(self,notify):
        """[summary]
        
        Arguments:
            notify {[type]} -- [description]
            watch_table {[type]} -- [description]
        """
        
        self.payload = json.loads(notify.payload)
        self.message_id = self.payload['id']
        self.table = self.payload['table']
        self.data = self.payload['data']
        self.action = self.payload['operation']


    def get_message_in_str(self):
        """[Turn Message to json for send message]
        
        Returns:
            [json] -- [description]
        """
        return json.dumps({
            "payload":self.data,
            "table":self.table,
            "action":self.action
        })

    def parse_payload(self):
        """[return payload with json]
        
        Returns:
            [json] -- [description]
        """
        return json.loads(self.payload)