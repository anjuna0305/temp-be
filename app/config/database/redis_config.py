import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def set_value(key, value):
    try:
        r.set(key, value)
        return True
    except Exception as e:
        print(f"Error setting value: {e}")
        return False


def get_value(key):
    try:
        value = r.get(key)
        return int(value)
    except Exception as e:
        print(f"Error getting value: {e}")
        return None
