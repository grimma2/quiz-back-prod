from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
import ssl


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz.settings')

app = Celery('quiz',
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    }
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.update(result_extended=True)
