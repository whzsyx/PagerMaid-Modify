import logging
from typing import Union
from pyrogram import Client
from configparser import RawConfigParser
from redis import StrictRedis

cmd, par, des = [], [], []
# [Basic]
prefix_str: str = "!"
ipv6: Union[bool, str] = "False"
# [Redis]
redis_host: str = "localhost"
redis_port: str = "6379"
redis_db: str = "14"
config = RawConfigParser()
config.read("config.ini")
prefix_str = config.get("basic", "prefix", fallback=prefix_str)
ipv6 = config.get("basic", "ipv6", fallback=ipv6)
ipv6 = eval(ipv6)
redis_host = config.get("redis", "redis_host", fallback=redis_host)
redis_port = config.get("redis", "redis_port", fallback=redis_port)
redis_db = config.get("redis", "redis_db", fallback=redis_db)
redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
    filename="log",
    filemode="a"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    Client("pagermaid", ipv6=ipv6).run()
