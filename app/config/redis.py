import redis as r

from .settings import Broker

redis_app = r.Redis(host=Broker.HOST, port=Broker.PORT, db=Broker.DB)
