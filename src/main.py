import asyncio
import websockets
import json

from db import Session
session = Session()

from handler import HandlerManager

hm = HandlerManager(session)

async def recv_worker(ws, q):
    while True:
        api = hm.handle_event(json.loads(await ws.recv()))
        if api:
            await q.put(api)
            await q.join()

async def send_worker(ws, q):
    while True:
        api = await q.get()
        await asyncio.sleep(1)
        await ws.send(json.dumps(api))
        q.task_done()

async def main():
    async with websockets.connect('ws://localhost:6700', ping_interval=None) as ws:
        print('connection established')
        q = asyncio.Queue()
        recv_task = asyncio.create_task(recv_worker(ws, q))
        send_task = asyncio.create_task(send_worker(ws, q))
        await recv_task
        await send_task

asyncio.run(main())