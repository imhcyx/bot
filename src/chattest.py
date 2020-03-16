from command import CommandManager

cm = CommandManager()
uid = 0

while True:
    msg = input('%d> ' % uid)
    if msg.startswith('#uid '):
        uid = int(msg.split(' ')[1])
    else:
        resp = cm.handle_command(msg, uid)
        print(resp)