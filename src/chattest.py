from command import CommandManager
from db import Session

session = Session()
cm = CommandManager(session)
uid = 0

while True:
    msg = input('%d> ' % uid)
    if msg.startswith('#uid '):
        uid = int(msg.split(' ')[1])
    else:
        resp = cm.handle_message(msg, uid)
        print(resp)