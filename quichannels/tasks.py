import asyncio
import websockets
from time import sleep, perf_counter
import json

from celery.contrib.abortable import AbortableTask
from quiz.celery import app
from quiz.settings import DEBUG


class WebsocketSenders:
    HOST = 'localhost:8000' if DEBUG else 'quiz-game1.ru'
    PROTOCOL = 'ws:' if DEBUG else 'wss:'
    LOOP = asyncio.get_event_loop()

    @classmethod
    def send_hint_for_team(cls, code: str, hint_pk: int) -> None:

        async def hint_sender():
            async with websockets.connect(f'{cls.PROTOCOL}//{cls.HOST}/api/next-hint/') as websocket:
                await websocket.send(f'{hint_pk}, {code}')
                await websocket.recv()
                
        cls.LOOP.run_until_complete(hint_sender())


@app.task
def send_hint(code, hint_pk):
    WebsocketSenders.send_hint_for_team(code=code, hint_pk=hint_pk)


@app.task(bind=True, base=AbortableTask)
def set_timer(self, code: str, hints: dict[str, int]):
    start_from = perf_counter()
    second = 1

    while True:
        if self.is_aborted():
            return
        elif str(second) in hints:
            hint_pk = hints.pop(str(second))
            send_hint.apply_async(kwargs={'code': code, 'hint_pk': hint_pk})

            if hints == {}:
                return

        second += 1

        # get negatiation between second and time what takes for above code to execute
        sleep(1 - (perf_counter() - start_from))
        # renew timer for measure every iteration of loop
        start_from = perf_counter()
