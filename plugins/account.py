from struct import error as StructError
from os import remove
from main import bot, reg_handler, des_handler, par_handler


async def profile(message, args, origin_text):
    """ Queries profile of a user. """
    if len(message.text.split()) > 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    await message.edit("正在生成用户简介摘要中 . . .")
    if message.reply_to_message:
        reply_message = message.reply_to_message
        target_user = reply_message.from_user
    else:
        if len(message.text.split()) == 2:
            user = message.text.split()[1]
            if user.isnumeric():
                user = int(user)
        else:
            user_object = await bot.get_me()
            user = user_object.id
        if message.entities is not None:
            if message.mentioned:
                user_object = message.entities[0].user
                user = user_object.id
        try:
            user_object = await bot.get_users(user)
            target_user = await bot.get_users(user_object.id)
        except (TypeError, ValueError, OverflowError, StructError) as exception:
            if str(exception).startswith("Cannot find any entity corresponding to"):
                await message.edit("出错了呜呜呜 ~ 指定的用户不存在。")
                return
            if str(exception).startswith("No user has"):
                await message.edit("出错了呜呜呜 ~ 指定的道纹不存在。")
                return
            if str(exception).startswith("Could not find the input entity for") or isinstance(exception, StructError):
                await message.edit("出错了呜呜呜 ~ 无法通过此 UserID 找到对应的用户。")
                return
            if isinstance(exception, OverflowError):
                await message.edit("出错了呜呜呜 ~ 指定的 UserID 已超出长度限制，您确定输对了？")
                return
            raise exception
    user_type = "Bot" if target_user.is_bot else "用户"
    username_system = f"@{target_user.username}" if target_user.username is not None else (
        "喵喵喵 ~ 好像没有设置")
    first_name = target_user.first_name.replace("\u2060", "")
    last_name = target_user.last_name.replace("\u2060", "") if target_user.last_name is not None else (
        "喵喵喵 ~ 好像没有设置"
    )
    verified = "是" if target_user.is_verified else "否"
    restricted = "是" if target_user.is_restricted else "否"
    caption = f"**用户简介:** \n" \
              f"道纹: {username_system} \n" \
              f"ID: {target_user.id} \n" \
              f"名字: {first_name} \n" \
              f"姓氏: {last_name} \n" \
              f"官方认证: {verified} \n" \
              f"受限制: {restricted} \n" \
              f"类型: {user_type} \n" \
              f"[{first_name}](tg://user?id={target_user.id})"
    try:
        photo = await bot.get_profile_photos(target_user.id, limit=1)
        photo = await bot.download_media(photo[0].file_id, 'photo.jpg')
    except:
        pass
    try:
        reply_to = message.reply_to_message.message_id
        try:
            await bot.send_photo(
                message.chat.id,
                'downloads/photo.jpg',
                caption=caption,
                reply_to_message_id=reply_to
            )
            await message.delete()
            try:
                remove(photo)
            except:
                pass
            return
        except TypeError:
            await message.edit(caption)
    except:
        try:
            await bot.send_photo(
                message.chat.id,
                'downloads/photo.jpg',
                caption=caption
            )
            await message.delete()
            try:
                remove(photo)
            except:
                pass
            return
        except TypeError:
            await message.edit(caption)


reg_handler('profile', profile)
des_handler('profile', '生成一位用户简介 ~ 消息有点长。')
par_handler('profile', '<username>')
