import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


def store_value_redis(key, value):
    redis_client.set(key, value)


def get_stored_value_redis(key):
    value = redis_client.get(key)
    if value is None:
        return None  # Or return a default value, or raise an exception
    else:
        return value.decode("utf-8")
