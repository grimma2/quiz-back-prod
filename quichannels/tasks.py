import asyncio
import websockets
import time

from celery.contrib.abortable import AbortableTask
from quiz.celery import app


class WebsocketSenders:
    HOST = 'localhost:8000'
    LOOP = asyncio.get_event_loop()

    @classmethod
    def send_code(cls, code: str) -> None:

        async def code_sender():
            async with websockets.connect(f'ws://{cls.HOST}/timer/') as websocket:
                await websocket.send(code)
                await websocket.recv()

        cls.LOOP.run_until_complete(code_sender())


@app.task(bind=True, base=AbortableTask)
def set_timer(self, time_for: float, code):
    try:
        time.sleep(time_for - 2)
    except ValueError:
        pass
    if self.is_aborted():
        return

    WebsocketSenders.send_code(code)
