import os
from celery.schedules import crontab

class DBConfig:
    NAME = os.environ.get('POSTGRES_DB')
    USER = os.environ.get('POSTGRES_DB')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    HOST = os.environ.get('POSTGRES_HOST')
    PORT = os.environ.get('POSTGRES_PORT')
    URL = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

class AppConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = DBConfig.URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Broker:
    HOST = os.environ.get("REDIS_HOST")
    PORT = os.environ.get("REDIS_PORT")
    DB = os.environ.get("REDIS_DB")

class Worker:
    broker_url = f'redis://{Broker.HOST}:{Broker.PORT}'
    result_backend = broker_url
    accept_content = ['application/json']
    task_serializer = 'json'
    result_serializer = 'json'
    imports = ('tasks')
    result_expires = 30
    timezone = 'Europe/Berlin'
    beat_schedule = {
        'download-olx-house': {
            'task': 'tasks.download_olx_houses',
            'schedule': crontab(minute=50, hour=18),
        }
    }
