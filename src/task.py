import asyncio

class Task:
    def __init__(self, uid, gid, callback):
        self.__uid = uid
        self.__gid = gid
        self.__callback = callback
    
    @property
    def uid(self):
        return self.__uid
    
    @property
    def gid(self):
        return self.__gid
    
    async def handle(self):
        pass

class SystemTask(Task):
    def __init__(self, cmd, uid, gid, callback, timeout=30):
        self.__cmd = cmd
        self.__uid = uid
        self.__gid = gid
        self.__callback = callback
        self.__timeout = timeout

    async def handle(self):
        try:
            proc = await asyncio.create_subprocess_shell(
                self.__cmd,
                stdout=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(proc.wait(), self.__timeout)
            b = await proc.stdout.read()
            self.__callback(b.decode())
        except asyncio.TimeoutError:
            proc.kill()
            self.__callback('%d seconds timeout exceeded' % self.__timeout)