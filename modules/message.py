import json
from requests import get
from pyrogram import Client, filters
from main import cmd, par, des

cmd.extend(['id'])
par.extend([''])
des.extend(['获取一条消息的各种信息。'])


@Client.on_message(filters.me & filters.command('id', list('.:!')))
async def userid(client, message):
    """ Query the UserID of the sender of the message you replied to. """
    msg = message.reply_to_message
    text = "Message ID: `" + str(message.message_id) + "`\n\n"
    text += "**Chat**\nid:`" + str(message.chat.id) + "`\n"
    msg_from = message.chat if message.chat else (await message.get_chat())
    if message.chat.type == 'private' or message.chat.type == 'bot':
        try:
            text += "first_name: `" + msg_from.first_name + "`\n"
        except TypeError:
            text += "**死号**\n"
        if msg_from.last_name:
            text += "last_name: `" + msg_from.last_name + "`\n"
        if msg_from.username:
            text += "username: @" + msg_from.username + "\n"
        if msg_from.language_code:
            text += "language_code: `" + msg_from.language_code + "`\n"
    if message.chat.type == 'group' or message.chat.type == 'supergroup' or message.chat.type == 'channel':
        text += "title: `" + msg_from.title + "`\n"
        if msg_from.username:
            text += "username: @" + msg_from.username + "\n"
        text += "dc: `" + str(msg_from.dc_id) + "`\n"
    if msg:
        text += "\n以下是被回复消息的信息\nMessage ID: `" + str(msg.message_id) + "`\n\n**User**\nid: `" + str(msg.from_user.id) + "`"
        if msg.from_user.is_bot:
            text += "\nis_bot: 是"
        try:
            text += "\nfirst_name: `" + msg.from_user.first_name + "`"
        except TypeError:
            text += "\n**死号**"
        if msg.from_user.last_name:
            text += "\nlast_name: `" + msg.from_user.last_name + "`"
        if msg.from_user.username:
            text += "\nusername: @" + msg.from_user.username
        if msg.from_user.language_code:
            text += "\nlanguage_code: `" + msg.from_user.language_code + "`"
        if msg.forward_from:
            if str(msg.forward_from_chat.id).startswith('-100'):
                text += "\n\n**Forward From Channel**\nid: `" + str(
                    msg.forward_from_chat.id) + "`\ntitle: `" + msg.forward_from_chat.title + "`"
                if msg.forward_from_chat.username:
                    text += "\nusername: @" + msg.forward_from_chat.username
                text += "\nmessage_id: `" + str(msg.forward_from_message_id) + "`"
                if msg.forward_signature:
                    text += "\npost_author: `" + msg.forward_signature + "`"
                text += "\ndate: `" + str(msg.forward_date) + "`"
            else:
                if msg.forward_from:
                    text += "\n\n**Forward From User**\nid: `" + str(
                        msg.forward_from.id) + "`"
                    if msg.forward_from.is_bot:
                        text += "\nis_bot: 是"
                    try:
                        text += "\nfirst_name: `" + msg.forward_from.first_name + "`"
                    except TypeError:
                        text += "\n**死号**"
                    if msg.forward_from.last_name:
                        text += "\nlast_name: `" + msg.forward_from.last_name + "`"
                    if msg.forward_from.username:
                        text += "\nusername: @" + msg.forward_from.username
                    if msg.forward_from.language_code:
                        text += "\nlanguage_code: `" + msg.forward_from.language_code + "`"
                    text += "\ndate: `" + str(msg.forward_date) + "`"
    await message.edit(text)


cmd.extend(['re'])
par.extend(['<次数>'])
des.extend(['在当前会话复读回复的消息。（需要回复一条消息）'])


@Client.on_message(filters.me & filters.command('re', list('.:!')))
async def re(client, message):
    """ Forwards a message into this group """
    reply = message.reply_to_message
    if reply:
        if len(message.text.split()) == 1:
            num = 1
        else:
            try:
                num = int(message.text.split()[1])
                if num > 100:
                    await message.edit('呜呜呜出错了...这个数字太大惹')
                    return True
            except:
                await message.edit('呜呜呜出错了...可能参数包含了数字以外的符号')
                return True
        await message.delete()
        for nums in range(0, num):
            await client.forward_messages(message.chat.id, message.chat.id, reply.message_id)
    else:
        await message.edit("出错了呜呜呜 ~ 您好像没有回复一条消息。")


cmd.extend(['hitokoto'])
par.extend([''])
des.extend(['每日一言。'])


@Client.on_message(filters.me & filters.command('hitokoto', list('.:!')))
async def hitokoto(client, message):
    """ Get hitokoto.cn """
    hitokoto_while = 1
    try:
        hitokoto_json = json.loads(get("https://v1.hitokoto.cn/?charset=utf-8").content.decode("utf-8"))
    except ValueError:
        while hitokoto_while < 10:
            hitokoto_while += 1
            try:
                hitokoto_json = json.loads(get("https://v1.hitokoto.cn/?charset=utf-8").content.decode("utf-8"))
                break
            except:
                continue
    hitokoto_json_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    hitokoto_type_list = ['动画', '漫画', '游戏', '文学', '原创', '来自网络', '其他', '影视', '诗词', '网易云', '哲学', '抖机灵']
    hitokoto_type = hitokoto_type_list[hitokoto_json_list.index(hitokoto_json['type'])]
    await message.edit(f"{hitokoto_json['hitokoto']} - {hitokoto_json['from']}（{str(hitokoto_type)}）")