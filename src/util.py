def parse_command(msg):
    arg = []
    word = ''
    quote = False
    for i in range(len(msg)):
        c = msg[i]
        if c == '"':
            quote = not quote
        elif c == ' ' and not quote:
            if word != '':
                arg.append(word)
                word = ''
        else:
            word += c
    if word != '':
        arg.append(word)
    return arg

class Task:
    def __init__(self, uid, gid, callback):
        self._uid = uid
        self._gid = gid
        self._callback = callback
    
    def uid(self):
        return self._uid
    
    def gid(self):
        return self._gid
    
    def callback(self, param):
        self._callback(param)

class SystemTask(Task):
    def __init__(self, uid, gid, callback, cmd):
        Task.__init__(self, uid, gid, callback)
        self._cmd = cmd
    
    def cmd(self):
        return self._cmd