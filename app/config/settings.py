import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AppConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")

class DBConfig:
    NAME = os.environ.get('POSTGRES_DB')
    USER = os.environ.get('POSTGRES_DB')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    HOST = os.environ.get('POSTGRES_HOST')
    PORT = os.environ.get('POSTGRES_PORT')
    URL = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

class Broker:
    HOST = os.environ.get("REDIS_HOST")
    PORT = os.environ.get("REDIS_PORT")
    DB = os.environ.get("REDIS_DB")

class Worker:
    BROKER_URL = f'redis://redis:{Broker.PORT}/0'
    RESULT_BACKEND = BROKER_URL
    ACCEPT_CONTENT = ['application/json']
    TASK_SERIALIZER = 'json'
    RESULT_SERIALIZER = 'json'


