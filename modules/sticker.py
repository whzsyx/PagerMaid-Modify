""" PagerMaid module to handle sticker collection. """

import certifi
import ssl
from asyncio import sleep
from os import remove
from urllib import request
from io import BytesIO
from PIL import Image
from math import floor
from pyrogram import Client, filters
from main import cmd, par, des, prefix_str

cmd.extend(['sticker'])
par.extend(['<emoji>'])
des.extend(['收集回复的图像/贴纸作为贴纸，通过参数指定 emoji 以设置非默认的 emoji。'])
sticker_process = False


@Client.on_message(filters.me & filters.command('sticker', list(prefix_str)))
async def sticker(client, message):
    """ Fetches images/stickers and add them to your pack. """
    user = await client.get_me()
    if not user.username:
        user.username = user.first_name
    msg = message.reply_to_message
    custom_emoji = False
    animated = False
    emoji = ""
    try:
        await message.edit("收集图像/贴纸中 . . .")
    except:
        pass
    if msg and (msg.document or msg.photo or msg.sticker):
        photo = await client.download_media(msg)
        try:
            await message.edit("下载图片中 . . .")
        except:
            pass
        if msg.sticker:
            emoji = msg.sticker.emoji
            custom_emoji = True
            if msg.sticker.is_animated:
                animated = True
    else:
        try:
            await message.edit("`出错了呜呜呜 ~ 请回复带有图片/贴纸的消息。`")
        except:
            pass
        return

    if photo:
        split_strings = message.text.split()
        if not custom_emoji:
            emoji = "👀"
        pack = 1
        sticker_already = False
        if len(split_strings) == 3:
            pack = split_strings[2]
            emoji = split_strings[1]
        elif len(split_strings) == 2:
            if split_strings[1].isnumeric():
                pack = int(split_strings[1])
            else:
                emoji = split_strings[1]

        pack_name = f"{user.username}_{pack}"
        pack_title = f"@{user.username} 的私藏 ({pack})"
        command = '/newpack'
        file = BytesIO()

        if not animated:
            try:
                await message.edit("调整图像大小中 . . .")
            except:
                pass
            image = await resize_image(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            pack_name += "_animated"
            pack_title += " (animated)"
            command = '/newanimated'

        response = request.urlopen(
            request.Request(f'http://t.me/addstickers/{pack_name}'),
            context=ssl.create_default_context(cafile=certifi.where()))
        if not response.status == 200:
            try:
                await message.edit("连接到 Telegram 服务器失败 . . .")
            except:
                pass
            return
        http_response = response.read().decode("utf8").split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in \
                http_response:
            for _ in range(20):  # 最多重试20次
                if not sticker_process:
                    try:
                        await client.send_message('Stickers', '/addsticker')
                        await client.read_history('Stickers')
                        await client.send_message('Stickers', pack_name)
                        await client.read_history('Stickers')
                        async for msg in client.iter_history('Stickers', limit=1):
                            chat_response = msg
                        while chat_response.text == "Whoa! That's probably enough stickers for one pack, give it a break. \
                                            A pack can't have more than 120 stickers at the moment.":
                            pack += 1
                            pack_name = f"{user.username}_{pack}"
                            pack_title = f"@{user.username} 的私藏 ({pack})"
                            try:
                                await message.edit("切换到私藏 " + str(pack) + " 上一个贴纸包已满 . . .")
                            except:
                                pass
                            await client.send_message('Stickers', pack_name)
                            await client.read_history('Stickers')
                            async for msg in client.iter_history('Stickers', limit=1):
                                chat_response = msg
                            if chat_response.text == "Invalid pack selected.":
                                await add_sticker(client, command, pack_title, pack_name, animated, message,
                                                  file, emoji, photo)
                                try:
                                    await message.edit(
                                        f"这张图片/贴纸已经被添加到 [这个](t.me/addstickers/{pack_name}) 贴纸包。")
                                except:
                                    pass
                                return
                        await upload_sticker(client, animated, message, file, photo)
                        await client.read_history('Stickers')
                        await client.send_message('Stickers', emoji)
                        await client.read_history('Stickers')
                        await client.send_message('Stickers', '/done')
                        await client.read_history('Stickers')
                        break
                    except Exception:
                        raise
                else:
                    if not sticker_already:
                        try:
                            await message.edit("另一个命令正在添加贴纸, 重新尝试中")
                        except:
                            pass
                        sticker_already = True
                    else:
                        pass
                    await sleep(.5)
        else:
            try:
                await message.edit("贴纸包不存在，正在创建 . . .")
            except:
                pass
            async with client.conversation('Stickers') as conversation:
                await add_sticker(client, command, pack_title, pack_name, animated, message,
                                  file, emoji, photo)

        try:
            await message.edit(
                f"这张图片/贴纸已经被添加到 [这个](t.me/addstickers/{pack_name}) 贴纸包。")
        except:
            pass
        await sleep(5)
        try:
            await message.delete()
        except:
            pass


async def add_sticker(client, command, pack_title, pack_name, animated, message, file, emoji, photo):
    await client.send_message('Stickers', command)
    await client.read_history('Stickers')
    await client.send_message('Stickers', pack_title)
    await client.read_history('Stickers')
    await upload_sticker(client, animated, message, file, photo)
    await client.read_history('Stickers')
    await client.send_message('Stickers', emoji)
    await client.read_history('Stickers')
    await client.send_message('Stickers', "/publish")
    await client.read_history('Stickers')
    if animated:
        await client.send_message('Stickers', f"<{pack_title}>")
    await client.send_message('Stickers', "/skip")
    await client.read_history('Stickers')
    await client.send_message('Stickers', pack_name)
    await client.read_history('Stickers')


async def upload_sticker(client, animated, message, file, photo):
    if animated:
        try:
            await message.edit("上传动图中 . . .")
        except:
            pass
        await client.send_document("Stickers", photo)
        remove(photo)
    else:
        file.seek(0)
        try:
            await message.edit("上传图片中 . . .")
        except:
            pass
        await client.send_document("Stickers", file)


async def resize_image(photo):
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)

    return image
