from cirno import Cirno
from db import Session

class CirnoTest(Cirno):
    def send_resp(self, resp):
        print(resp.text)

cirno = CirnoTest()
uid = 123456
gid = 0

while True:
    text = input('%d @ %d> ' % (uid, gid))
    if text.startswith('#uid '):
        uid = int(text.split(' ')[1])
    elif text.startswith('#gid '):
        gid = int(text.split(' ')[1])
    else:
        event = {
            'post_type': 'message',
            'message_type': 'group' if gid else 'private',
            'user_id': uid,
            'group_id': gid,
            'message': text,
        }
        cirno.handle_event(event)