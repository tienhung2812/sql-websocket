import json

class Message:
    def __init__(self,notify,watch_table):
        """[summary]
        
        Arguments:
            notify {[type]} -- [description]
            watch_table {[type]} -- [description]
        """
        self.message_id = notify.id
        self.channel = notify.channel
        self.payload = notify.payload
        self.action = watch_table.action
        self.table = watch_table.table

    def get_message_in_str(self):
        """[Turn Message to json for send message]
        
        Returns:
            [json] -- [description]
        """
        return json.dumps({
            "payload":self.payload,
            "table":self.table,
            "action":self.action
        })

    def parse_payload(self):
        """[return payload with json]
        
        Returns:
            [json] -- [description]
        """
        return json.loads(self.payload)