import asyncio
import websockets
import json

from config import cfg
from model import User, Group
from db import Session
from filter import default_filters
from message import Message, Response
from runtime import UserData

async def _recv_worker(ws, cirno):
    while True:
        cirno.handle_event(json.loads(await ws.recv()))

async def _send_worker(ws, send_q):
    while True:
        resp = await send_q.get()
        await asyncio.sleep(resp.delay)
        await ws.send(json.dumps(resp.to_json()))

async def _task_worker(task):
    await task.handle()

async def _timeout_worker(timeout, func):
    await asyncio.sleep(timeout)
    func()

class Cirno:
    def __init__(self):
        self.__running = False
        self.__sess = Session()
        self.__filters = default_filters
        self.__send_q = None
        self.__runtime_users = {}
    
    async def run(self):
        async with websockets.connect(cfg['ws'], ping_interval=None) as ws:
            print('connection established')
            self.__send_q = asyncio.Queue()
            coroutines = [
                _recv_worker(ws, cirno),
                _send_worker(ws, self.__send_q),
            ]
            tasks = [asyncio.create_task(c) for c in coroutines]
            self.__running = True
            for task in tasks:
                await task

    def handle_event(self, event):
        post_type = event.get('post_type')
        if post_type == 'message':
            msg = Message(self, event)
            self.__filters.handle(msg)
    
    def send_resp(self, resp):
        if self.__running:
            self.__send_q.put_nowait(resp)
    
    def send_msg(self, text, uid, gid=None, delay=0):
        resp = Response(
            text=text,
            uid=uid,
            gid=gid,
            delay=delay
        )
        self.send_resp(resp)
    
    def add_task(self, task):
        asyncio.create_task(_task_worker(task))
    
    def set_timeout(self, timeout, func):
        asyncio.create_task(_timeout_worker(timeout, func))
    
    @property
    def sess(self):
        return self.__sess
    
    def user_from_id(self, id):
        sess = self.__sess
        query = sess.query(User).filter_by(id=id)
        if query.count() == 0:
            user = User(id=id)
            sess.add(user)
            sess.commit()
        else:
            user = query.one()
        if id in self.__runtime_users:
            user.runtime = self.__runtime_users[id]
        else:
            user.runtime = UserData()
            self.__runtime_users[id] = user.runtime
        return user
    
    def group_from_id(self, id):
        sess = self.__sess
        query = sess.query(Group).filter_by(id=id)
        if query.count() == 0:
            group = Group(id=id)
            sess.add(group)
            sess.commit()
        else:
            group = query.one()
        return group

if __name__ == "__main__":
    cirno = Cirno()
    asyncio.run(cirno.run())