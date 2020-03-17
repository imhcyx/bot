import asyncio
import websockets
import json

from config import cfg
from db import Session
from handler import HandlerHelper
from util import SystemTask

async def recv_worker(ws, handler):
    while True:
        handler.handle_event(json.loads(await ws.recv()))

async def task_worker(ws, task_q):
    while True:
        task = await task_q.get()
        if isinstance(task, SystemTask):
            try:
                proc = await asyncio.create_subprocess_shell(
                    task.cmd(),
                    stdout=asyncio.subprocess.PIPE
                )
                await asyncio.wait_for(proc, 15)
                s = proc.stdout.read()
                task.callback(s)
            except asyncio.TimeoutError:
                proc.kill()
                task.callback('Timeout')

async def send_worker(ws, send_q):
    while True:
        api = await send_q.get()
        await asyncio.sleep(1)
        await ws.send(json.dumps(api))

async def main():
    session = Session()
    async with websockets.connect(cfg['ws'], ping_interval=None) as ws:
        print('connection established')
        send_q = asyncio.Queue()
        task_q = asyncio.Queue()
        handler = HandlerHelper(
            session,
            lambda resp: send_q.put_nowait(resp), 
            lambda task: task_q.put_nowait(task)
        )
        recv_t = asyncio.create_task(recv_worker(ws, handler))
        task_t = asyncio.create_task(task_worker(ws, task_q))
        send_t = asyncio.create_task(send_worker(ws, send_q))
        await recv_t
        await task_t
        await send_t

asyncio.run(main())