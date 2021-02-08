from pyrogram import Client, filters, __version__
from main import cmd, par, des
from modules.system import execute
from platform import python_version, uname
from sys import platform
from speedtest import Speedtest
from datetime import datetime


cmd.extend(['sysinfo'])
par.extend([''])
des.extend(['通过 neofetch 检索系统信息。'])


@Client.on_message(filters.me & filters.command('sysinfo', list('.:!')))
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


@Client.on_message(filters.me & filters.command('status', list('.:!')))
async def status(client, message):
    await message.edit(
        f"**PagerMaid-Modify Beta 运行状态** \n"
        f"主机名: `{uname().node}` \n"
        f"主机平台: `{platform}` \n"
        f"Kernel 版本: `{uname().release}` \n"
        f"Python 版本: `{python_version()}` \n"
        f"Library 版本: `{__version__}`"
    )


cmd.extend(['speedtest'])
par.extend([''])
des.extend(['执行 speedtest 脚本并发送结果。'])


@Client.on_message(filters.me & filters.command('speedtest', list('.:!')))
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


@Client.on_message(filters.me & filters.command('ping', list('.:!')))
async def ping(client, message):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await message.edit("Pong!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await message.edit(f"Pong!|{duration}")


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
