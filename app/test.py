import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


def storeValueRedis(key, value):
    redis_client.set(key, value)


def getStoredValueRedis(key):
    redis_client.get(key).decode("utf-8")