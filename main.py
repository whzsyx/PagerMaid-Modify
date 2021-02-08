from pyrogram import Client
from configparser import RawConfigParser
from redis import StrictRedis

cmd, par, des = [], [], []
# [Basic]
prefix_str: str = "!"
# [Redis]
redis_host: str = "localhost"
redis_port: str = "6379"
redis_db: str = "14"
config = RawConfigParser()
config.read("config.ini")
prefix_str = config.get("basic", "prefix", fallback=prefix_str)
redis_host = config.get("redis", "redis_host", fallback=redis_host)
redis_port = config.get("redis", "redis_port", fallback=redis_port)
redis_db = config.get("redis", "redis_db", fallback=redis_db)
redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

if __name__ == "__main__":
    Client("pagermaid").run()
