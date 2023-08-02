import asyncio
import websockets
import time

from celery.contrib.abortable import AbortableTask
from quiz.celery import app
from quiz.settings import DEBUG


class WebsocketSenders:
    HOST = 'localhost:8000' if DEBUG else 'quiz-game1.ru'
    LOOP = asyncio.get_event_loop()

    @classmethod
    def send_code(cls, code: str) -> None:

        async def code_sender():
            protocol = 'ws' if DEBUG else 'wss'
            async with websockets.connect(f'{protocol}://{cls.HOST}/api/timer/') as websocket:
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
