from pyrogram import Client
from configparser import RawConfigParser

cmd, par, des = [], [], []
# [Basic]
prefix_str: str = "!"
config = RawConfigParser()
config.read("config.ini")
prefix_str = config.get("basic", "prefix", fallback=prefix_str)

if __name__ == "__main__":
    Client("pagermaid").run()
