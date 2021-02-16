import logging, os, shutil
from typing import Dict, List, Union, Awaitable, Callable
from pyrogram import Client, filters
from pyrogram.types import Message
from configparser import RawConfigParser
from redis import StrictRedis
from pathlib import Path
from sys import exit

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
bot = Client("pagermaid", ipv6=ipv6)
handler_map: Dict[str, Callable[[Message, List[str], str], Awaitable[None]]] = {}
des_map: Dict[str, str] = {}
par_map: Dict[str, str] = {}


if os.path.exists('modules/plugins'):
    os.system('mv -f modules/plugins/version.json plugins/plugins/version.json')
    os.system('rm -rf modules/plugins')
    exit()


def reg_handler(cmd: str, handler: Callable[[Message, List[str], str], Awaitable[None]]) -> None:
    global handler_map
    if handler_map.get(cmd) is not None:
        return
    handler_map[cmd] = handler


def des_handler(cmd: str, des: str) -> None:
    global des_map
    if des_map.get(cmd) is not None:
        return
    des_map[cmd] = des


def par_handler(cmd: str, par: str) -> None:
    global par_map
    if par_map.get(cmd) is not None:
        return
    par_map[cmd] = par


@bot.on_message(filters.me)
async def handle_text(client, message):
    global handler_map
    text = message.text
    for prefix in list(prefix_str):
        if not text.startswith(prefix):
            return

    try:
        args = text[1:].lstrip().split(' ')[1:]
    except:
        return

    for command in handler_map:
        for prefix in list(prefix_str):
            if text.split()[0] == (prefix + command):
                await handler_map[command](message, args, text)
            elif text.startswith(prefix + 'help'):
                if len(message.text.split()) == 2:
                    command = message.text.split()[1]
                    if command in handler_map:
                        parameters = par_map[command]
                        description = des_map[command]
                        await message.edit(f'**使用方法:** `{list(prefix_str)[0]}{command} {parameters}`\
                             \n{description}')
                        return
                    else:
                        await message.edit("无效的参数")
                        return
                result = "**Beta 命令列表: **\n"
                for command in handler_map:
                    result += "`" + str(command)
                    result += "`, "
                await message.edit(result[:-2] + f"\n**发送 \"{list(prefix_str)[0]}help <命令>\" 以-查看特定命令的-帮助。** [源代码]("
                                                 f"https://t.me/PagerMaid_Modify)",disable_web_page_preview=True)


if __name__ == "__main__":
    for module_path in sorted(Path('plugins'.replace(".", "/")).rglob("*.py")):
        with open(module_path, "r", encoding="utf-8") as f:
            module_content = f.read()
            exec(module_content)
    bot.run()