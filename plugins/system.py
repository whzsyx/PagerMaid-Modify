from main import bot, reg_handler, des_handler, par_handler
from sys import exit, platform
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from platform import node
from getpass import getuser
from os import remove


async def execute(command, pass_error=True):
    """ Executes command and returns output, with the option of enabling stderr. """
    if not platform == 'win32':
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
    else:
        import subprocess
        subprocess.Popen('dir', shell=True)
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        sub.wait()
        stdout = sub.communicate()
        result = str(stdout[0].decode('gbk').strip())
    return result


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


async def sh(message, args, origin_text):
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
            await attach_log(bot, result, message.chat.id, "output.log", message.message_id)
            return

        await message.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `#` {command}"
            f"\n`{result}`"
        )
    else:
        return


async def restart(message, args, origin_text):
    """ To re-execute PagerMaid. """
    if not message.text[0].isalpha():
        await message.edit("尝试重新启动 PagerMaid-Modify Beta 。")
        exit()


reg_handler('sh', sh)
reg_handler('restart', restart)
des_handler('sh', '在 Telegram 上远程执行 Shell 命令。')
des_handler('restart', '使 PagerMaid-Modify 重新启动。')
par_handler('sh', '<命令>')
par_handler('restart', '')
