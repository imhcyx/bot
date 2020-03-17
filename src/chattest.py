from handler import HandlerHelper
from db import Session

session = Session()
hh = HandlerHelper(
    session,
    lambda x: print('task added'),
    lambda x: print('response sent')
)
fm = hh.fm()
uid = 123456
gid = 0

while True:
    msg = input('%d @ %d> ' % (uid, gid))
    if msg.startswith('#uid '):
        uid = int(msg.split(' ')[1])
    elif msg.startswith('#gid '):
        gid = int(msg.split(' ')[1])
    else:
        resp = fm.handle(msg, uid, gid)
        print(resp)