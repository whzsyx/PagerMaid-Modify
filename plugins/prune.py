""" Module to automate message deletion. """
from main import bot, reg_handler, des_handler, par_handler
from asyncio import sleep
from pyrogram.errors import ChatAdminRequired


async def prune(message, args, origin_text):
    """ Purge every single message after the message you replied to. """
    if not message.reply_to_message:
        await message.edit("出错了呜呜呜 ~ 没有回复的消息。")
        return
    input_chat = message.chat.id
    messages = []
    count = 0
    async for msg in bot.iter_history(input_chat, offset_id=message.reply_to_message.message_id, reverse=True):
        messages.append(msg.message_id)
        count += 1
        if len(messages) == 100:
            await bot.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await bot.delete_messages(input_chat, messages)
    notification = await send_prune_notify(bot, message.chat.id, count, count)
    await sleep(.5)
    await notification.delete()


async def selfprune(message, args, origin_text):
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
    me = await bot.get_me()
    async for msg in bot.search_messages(message.chat.id, from_user=me.id):
        if count_buffer == count:
            break
        await msg.delete()
        count_buffer += 1
    notification = await send_prune_notify(bot, message.chat.id, count_buffer, count)
    await sleep(.5)
    await notification.delete()


async def yourprune(message, args, origin_text):
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
    async for msg in bot.search_messages(message.chat.id, from_user=target.from_user.id):
        if count_buffer == count:
            break
        await msg.delete()
        count_buffer += 1
    notification = await send_prune_notify(bot, message.chat.id, count_buffer, count)
    await sleep(.5)
    await notification.delete()


async def delete(message, args, origin_text):
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


reg_handler('prune', prune)
reg_handler('selfprune', selfprune)
reg_handler('yourprune', yourprune)
reg_handler('del', delete)
des_handler('prune', '以此命令回复某条消息，将删除最新一条消息至该条消息之间的所有消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能'
            '会触发删除消息过快限制。（非群组管理员只删除自己的消息）')
des_handler('selfprune', '删除当前对话您发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快限制。入群消息非管理员'
            '无法删除。（倒序）当数字足够大时即可实现删除所有消息。')
des_handler('yourprune', '删除当前对话您回复用户所发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快'
            '限制。（倒序、需要删除消息权限）当数字足够大时即可实现删除所有消息。')
des_handler('del', '删除当前对话您回复的那条消息。（需要回复一条消息）')
par_handler('prune', '')
par_handler('selfprune', '<数量>')
par_handler('yourprune', '<数量>')
par_handler('del', '')
