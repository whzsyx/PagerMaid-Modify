""" Module to automate message deletion. """
from pyrogram import Client, filters
from main import cmd, par, des, prefix_str
from asyncio import sleep
from pyrogram.errors import ChatAdminRequired


cmd.extend(['prune'])
par.extend([''])
des.extend(['以此命令回复某条消息，将删除最新一条消息至该条消息之间的所有消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能'
            '会触发删除消息过快限制。（非群组管理员只删除自己的消息）'])


@Client.on_message(filters.me & filters.command('prune', list(prefix_str)))
async def prune(client, message):
    """ Purge every single message after the message you replied to. """
    if not message.reply_to_message:
        await message.edit("出错了呜呜呜 ~ 没有回复的消息。")
        return
    input_chat = message.chat.id
    messages = []
    count = 0
    async for msg in client.iter_history(input_chat, offset_id=message.reply_to_message.message_id, reverse=True):
        messages.append(msg.message_id)
        count += 1
        if len(messages) == 100:
            await client.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await client.delete_messages(input_chat, messages)
    notification = await send_prune_notify(client, message.chat.id, count, count)
    await sleep(.5)
    await notification.delete()


cmd.extend(['prune'])
par.extend(['<数量>'])
des.extend(['删除当前对话您发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快限制。入群消息非管理员'
            '无法删除。（倒序）当数字足够大时即可实现删除所有消息。'])


@Client.on_message(filters.me & filters.command('selfprune', list(prefix_str)))
async def selfprune(client, message):
    """ Deletes specific amount of messages you sent. """
    if not len(message.text.split()) == 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        count = int(message.text.split()[1])
        await message.delete()
    except ValueError:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    count_buffer = 0
    me = await client.get_me()
    async for msg in client.search_messages(message.chat.id, from_user=me.id):
        if count_buffer == count:
            break
        await msg.delete()
        count_buffer += 1
    notification = await send_prune_notify(client, message.chat.id, count_buffer, count)
    await sleep(.5)
    await notification.delete()


cmd.extend(['yourprune'])
par.extend(['<数量>'])
des.extend(['删除当前对话您回复用户所发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快'
            '限制。（倒序、需要删除消息权限）当数字足够大时即可实现删除所有消息。'])


@Client.on_message(filters.me & filters.command('yourprune', list(prefix_str)))
async def yourprune(client, message):
    """ Deletes specific amount of messages someone sent. """
    if not message.reply_to_message:
        await message.edit("出错了呜呜呜 ~ 没有回复的消息。")
        return
    target = message.reply_to_message
    if not len(message.text.split()) == 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        count = int(message.text.split()[1])
        await message.delete()
    except ValueError:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    except:
        pass
    count_buffer = 0
    async for msg in client.search_messages(message.chat.id, from_user=target.from_user.id):
        if count_buffer == count:
            break
        await msg.delete()
        count_buffer += 1
    notification = await send_prune_notify(client, message.chat.id, count_buffer, count)
    await sleep(.5)
    await notification.delete()


cmd.extend(['del'])
par.extend([''])
des.extend(['删除当前对话您回复的那条消息。（需要回复一条消息）'])


@Client.on_message(filters.me & filters.command('del', list(prefix_str)))
async def delete(client, message):
    """ Deletes the message you replied to. """
    if message.reply_to_message:
        target = message.reply_to_message
        try:
            await target.delete()
            await message.delete()
        except ChatAdminRequired:
            await message.edit("出错了呜呜呜 ~ 缺少删除此消息的权限。")
    else:
        await message.delete()


async def send_prune_notify(client, cid, count_buffer, count):
    return await client.send_message(
        cid,
        "删除了 "
        + str(count_buffer) + " / " + str(count)
        + " 条消息。"
    )