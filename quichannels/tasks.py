import time
from celery.contrib.abortable import AbortableTask
from quiz.celery import app
from game.utils import WebsocketSenders


@app.task(bind=True, base=AbortableTask)
def set_timer(self, time_for: float, code):
    try:
        time.sleep(time_for - 2)
    except ValueError:
        pass
    if self.is_aborted():
        return

    WebsocketSenders.send_code(code)


@app.task
def send_state_to_consumer(state: str, game_pk: int):
    WebsocketSenders.send_state(state=state, game_pk=game_pk)
