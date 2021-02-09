from pyrogram import Client, filters
from main import cmd, par, des, prefix_str

cmd.extend(['help'])
par.extend(['<命令>'])
des.extend(['显示命令列表或单个命令的帮助。'])


@Client.on_message(filters.me & filters.command('help', list(prefix_str)))
async def help_com(client, message):
    if len(message.text.split()) == 2:
        command = message.text.split()[1]
        if command in cmd:
            parameters = par[cmd.index(command)]
            description = des[cmd.index(command)]
            await message.edit(f'**Beta 使用方法:** `{list(prefix_str)[0]}{command} {parameters}`\
            \n{description}')
            return
        else:
            await message.edit("无效的参数")
            return
    result = "**命令列表: \n**"
    for command in cmd:
        result += "`" + str(command)
        result += "`, "
    await message.edit(result[:-2] + f"\n**发送 \"{list(prefix_str)[0]}help <命令>\" 以-查看特定命令的-帮助。** [源代码]("
                                     f"https://t.me/PagerMaid_Modify)",
                       disable_web_page_preview=True)
