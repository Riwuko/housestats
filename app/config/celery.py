# import os
# from celery import Celery

# app = Celery(include=('tasks',))
# app.conf.beat_schedule = {
#   'refresh': {
#     'task': 'refresh',
#     'schedule': float(os.environ['NEWSPAPER_SCHEDULE']),
#     'args': (os.environ['NEWSPAPER_URLS'].split(','),)
#   },
# }

from celery import Celery
from .settings import Worker


celery_app = Celery('tasks', broker=Worker.BROKER_URL, backend=Worker.RESULT_BACKEND)
# celery_app.autodiscover_tasks()
