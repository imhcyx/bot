class Message:
    def __init__(self, cirno, event):
        text = event.get('message')
        uid = event.get('user_id')
        gid = event.get('group_id')
        self.__uid = uid
        self.__gid = gid
        self.__cirno = cirno
        self.__text = text
        self.__user = cirno.user_from_id(uid) if uid else None
        self.__group = cirno.group_from_id(gid) if gid else None
    
    def reply(self, text, delay=0):
        self.__cirno.send_resp(Response(
            text=text,
            uid=self.__uid,
            gid=self.__gid,
            delay=delay
        ))
    
    @property
    def cirno(self):
        return self.__cirno
    
    @property
    def text(self):
        return self.__text
    
    @property
    def user(self):
        return self.__user
    
    @property
    def group(self):
        return self.__group

class Response:
    def __init__(self, text, uid, gid, delay):
        self.__text = text
        self.__uid = uid
        self.__gid = gid
        self.__delay = delay
    
    @property
    def text(self):
        return self.__text

    @property
    def delay(self):
        return self.__delay

    def to_json(self):
        return {
            'action': 'send_group_msg' if self.__gid else 'send_private_msg',
            'params': {
                'user_id': self.__uid,
                'group_id': self.__gid,
                'message': self.__text
            }
        }