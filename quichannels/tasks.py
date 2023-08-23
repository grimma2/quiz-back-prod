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
    def send_code(cls, code: str) -> None:

        async def code_sender():
            async with websockets.connect(f'{cls.PROTOCOL}//{cls.HOST}/api/timer/') as websocket:
                await websocket.send(code)
                await websocket.recv()

        cls.LOOP.run_until_complete(code_sender())

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
def set_timer(self, time_for: int, code: str, hints: dict[str, int]):
    start_from = perf_counter()
    print(f'time: {time_for}')
    print(f'hints: {hints} {hints.keys()}')

    time_for += 1
    for second in range(1, time_for):
        print(second)
        if self.is_aborted():
            return
        elif str(second) in hints:
            print('hint send')
            send_hint.apply_async(kwargs={'code': code, 'hint_pk': hints[str(second)]})
            print('after call new task')
        else:
            print(f'else: {str(second) in hints}, {str(second)}, {hints}')

        # get negatiation between second and time what takes for above code to execute
        print(f'время, которое отнимается от 1: {perf_counter() - start_from}')
        sleep(1 - (perf_counter() - start_from))
        # renew timer for measure every iteration of loop
        start_from = perf_counter()

    WebsocketSenders.send_code(code)
