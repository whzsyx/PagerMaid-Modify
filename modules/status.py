from pyrogram import Client, filters, __version__
from main import cmd, par, des, prefix_str, redis
from modules.system import execute
from platform import python_version, uname
from sys import platform
from speedtest import Speedtest
from datetime import datetime
from pathlib import Path
from re import sub
from os import remove, popen
from wordcloud import WordCloud


cmd.extend(['sysinfo'])
par.extend([''])
des.extend(['通过 neofetch 检索系统信息。'])


@Client.on_message(filters.me & filters.command('sysinfo', list(prefix_str)))
async def sysinfo(client, message):
    """ Retrieve system information via neofetch. """
    if platform == 'win32':
        await message.edit(f"此命令暂不支持 win 系统。")
        return
    await message.edit("加载系统信息中 . . .")
    result = await execute("neofetch --config none --stdout")
    await message.edit(f"`{result}`")


cmd.extend(['status'])
par.extend([''])
des.extend(['输出 PagerMaid-Modify 的运行状态。'])


@Client.on_message(filters.me & filters.command('status', list(prefix_str)))
async def status(client, message):
    redis_con = '在线' if redis_status() else "离线"
    await message.edit(
        f"**PagerMaid-Modify Beta 运行状态** \n"
        f"主机名: `{uname().node}` \n"
        f"主机平台: `{platform}` \n"
        f"Kernel 版本: `{uname().release}` \n"
        f"Python 版本: `{python_version()}` \n"
        f"Library 版本: `{__version__}` \n"
        f"Redis 状态: `{redis_con}`"
    )


cmd.extend(['speedtest'])
par.extend([''])
des.extend(['执行 speedtest 脚本并发送结果。'])


@Client.on_message(filters.me & filters.command('speedtest', list(prefix_str)))
async def speedtest(client, message):
    """ Tests internet speed using speedtest. """
    await message.edit("执行测试脚本 . . .")
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    await message.edit(
        f"**Speedtest** \n"
        f"Upload: `{unit_convert(result['upload'])}` \n"
        f"Download: `{unit_convert(result['download'])}` \n"
        f"Latency: `{result['ping']}` \n"
        f"Timestamp: `{result['timestamp']}`"
    )


cmd.extend(['ping'])
par.extend([''])
des.extend(['计算运行 PagerMaid-Modify 的服务器和 Telegram 服务器之间的延迟。'])


@Client.on_message(filters.me & filters.command('ping', list(prefix_str)))
async def ping(client, message):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await message.edit("Pong!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await message.edit(f"Pong!|{duration}")


cmd.extend(['topcloud'])
par.extend([''])
des.extend(['生成一张资源占用的词云图片。'])


@Client.on_message(filters.me & filters.command('topcloud', list(prefix_str)))
async def topcloud(client, message):
    """ Generates a word cloud of resource-hungry processes. """
    if platform == 'win32':
        await message.edit(f"此命令暂不支持 win 系统。")
        return
    await message.edit("生成图片中 . . .")
    command_list = []
    if not Path('/usr/bin/top').is_symlink():
        output = str(await execute("top -b -n 1")).split("\n")[7:]
    else:
        output = str(await execute("top -b -n 1")).split("\n")[4:]
    for line in output[:-1]:
        line = sub(r'\s+', ' ', line).strip()
        fields = line.split(" ")
        try:
            if fields[11].count("/") > 0:
                command = fields[11].split("/")[0]
            else:
                command = fields[11]

            cpu = float(fields[8].replace(",", "."))
            mem = float(fields[9].replace(",", "."))

            if command != "top":
                command_list.append((command, cpu, mem))
        except BaseException:
            pass
    command_dict = {}
    for command, cpu, mem in command_list:
        if command in command_dict:
            command_dict[command][0] += cpu
            command_dict[command][1] += mem
        else:
            command_dict[command] = [cpu + 1, mem + 1]

    resource_dict = {}

    for command, [cpu, mem] in command_dict.items():
        resource_dict[command] = (cpu ** 2 + mem ** 2) ** 0.5

    width, height = None, None
    try:
        width, height = ((popen("xrandr | grep '*'").read()).split()[0]).split("x")
        width = int(width)
        height = int(height)
    except BaseException:
        pass
    if not width or not height:
        width = int("1920")
        height = int("1080")
    background = "#101010"
    margin = int("20")

    cloud = WordCloud(
        background_color=background,
        width=width - 2 * int(margin),
        height=height - 2 * int(margin)
    ).generate_from_frequencies(resource_dict)

    cloud.to_file("cloud.png")
    await message.edit("正在上传图片中 . . .")
    await client.send_photo(
        message.chat.id,
        "cloud.png",
        caption="正在运行的进程。"
    )
    remove("cloud.png")
    await message.delete()


def unit_convert(byte):
    """ Converts byte into readable formats. """
    power = 2 ** 10
    zero = 0
    units = {
        0: '',
        1: 'Kb/s',
        2: 'Mb/s',
        3: 'Gb/s',
        4: 'Tb/s'}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"


def redis_status():
    try:
        redis.ping()
        return True
    except BaseException:
        return False
