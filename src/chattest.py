from filter import FilterManager
from db import Session

session = Session()
fm = FilterManager(session)
uid = 123456
gid = 0

while True:
    msg = input('%d @ %d> ' % (uid, gid))
    if msg.startswith('#uid '):
        uid = int(msg.split(' ')[1])
    if msg.startswith('#gid '):
        gid = int(msg.split(' ')[1])
    else:
        resp = fm.handle(msg, uid, gid)
        print(resp)