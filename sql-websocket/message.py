import json

class Message:
    def __init__(self,notify):
        """[summary]
        
        Arguments:
            notify {[type]} -- [description]
            watch_table {[type]} -- [description]
        """
        """[Example]
        {
            "timestamp" : 2019-06-11 10:41:42.201576+07,
            "operation" : INSERT,
            "schema" : public,
            "table" : realtime_table,
            "data" : {
                "id" : 43,
                "title" : 5,
                "year" : 2,
                "producer" : 3
            }
        }
        """ 
        self.payload = json.loads(notify.payload)
        self.data = self.payload['data']
        self.message_id = self.data['id']
        self.table = self.payload['table']
        
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