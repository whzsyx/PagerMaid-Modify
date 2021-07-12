import io, sys, traceback
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


async def sh_eval(message, args, origin_text):
    """ Run python commands from Telegram. """
    try:
        cmd = origin_text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.edit('参数错误。')
        return
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, message, bot)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "**>>>** ```{}``` \n```{}```".format(
            cmd,
            evaluation,
        )
    )
    if len(final_output) > 4096:
        await message.edit("**>>>** ```{}```".format(cmd))
        await attach_log(bot, evaluation, message.chat.id, "output.log", message.message_id)
    else:
        await message.edit(final_output)


async def aexec(code, event, client):
    exec(
        f"async def __aexec(e, client): "
        + "\n msg = context = e"
        + "\n reply = context.reply_to_message"
        + "\n chat = e.chat"
        + "".join(f"\n {l}" for l in code.split("\n")),
    )

    return await locals()["__aexec"](event, client)


reg_handler('sh', sh)
reg_handler('restart', restart)
reg_handler('eval', sh_eval)
des_handler('sh', '在 Telegram 上远程执行 Shell 命令。')
des_handler('restart', '使 PagerMaid-Modify 重新启动。')
des_handler('eval', '在 Telegram 上远程执行 Python 命令。')
par_handler('sh', '<命令>')
par_handler('restart', '')
par_handler('eval', '<命令>')
