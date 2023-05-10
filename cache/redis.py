from redis import Redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)
cache = None


def init_redis():
    global cache
    cache = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    if Redis.ping(cache):
        print("Redis is running")
    else:
        print("Redis is not running")


def get_redis() -> Redis:
    return cache
