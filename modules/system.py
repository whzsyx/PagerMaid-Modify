from pyrogram import Client, filters
from main import cmd, par, des
from sys import exit
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from platform import node
from getpass import getuser
from os import remove


async def execute(command, pass_error=True):
    """ Executes command and returns output, with the option of enabling stderr. """
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result


cmd.extend(['sh'])
par.extend(['<命令>'])
des.extend(['在 Telegram 上远程执行 Shell 命令。'])


async def attach_log(client, plaintext, chat_id, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    await client.send_document(
        chat_id,
        file_name,
        reply_to_message_id=reply_id,
        caption=caption
    )
    remove(file_name)


@Client.on_message(filters.me & filters.command('sh', list('.:!')))
async def sh(client, message):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = message.text[4:]
    hostname = node()

    if not command:
        await message.edit("`出错了呜呜呜 ~ 无效的参数。`")
        return

    await message.edit(
        f"`{user}`@{hostname} ~"
        f"\n> `$` {command}"
    )

    result = await execute(command)

    if result:
        if len(result) > 4096:
            await attach_log(client, result, message.chat_id, "output.log", message.message_id)
            return

        await message.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `#` {command}"
            f"\n`{result}`"
        )
    else:
        return


cmd.extend(['restart'])
par.extend([''])
des.extend(['使 PagerMaid-Modify 重新启动。'])


@Client.on_message(filters.me & filters.command('restart', list('.:!')))
async def restart(client, message):
    """ To re-execute PagerMaid. """
    if not message.text[0].isalpha():
        await message.edit("尝试重新启动 PagerMaid-Modify 。")
        exit()