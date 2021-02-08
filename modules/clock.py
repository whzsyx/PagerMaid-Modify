""" This module handles world clock related utility. """

from datetime import datetime
from pytz import country_names, country_timezones, timezone
from pyrogram import Client, filters
from main import cmd, par, des


cmd.extend(['time'])
par.extend(['<地区>'])
des.extend(['显示特定区域的时间，如果参数为空，则默认显示中国。'])


@Client.on_message(filters.me & filters.command('time', list('.:!')))
async def time(client, message):
    """ For querying time. """
    if len(message.text.split()) > 2:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    if len(message.text.split()) == 2:
        country = message.text.split()[1].title()
    else:
        country = 'China'
    time_form = "%I:%M %p"
    date_form = "%A %d/%m/%y"
    if not country:
        time_zone = await get_timezone('China')
        await message.edit(
            f"**Time in {'China'}**\n"
            f"`{datetime.now(time_zone).strftime(date_form)} "
            f"{datetime.now(time_zone).strftime(time_form)}`"
        )
        return

    time_zone = await get_timezone(country)
    if not time_zone:
        await message.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    try:
        country_name = country_names[country]
    except KeyError:
        country_name = country

    await message.edit(f"**{country_name} 时间：**\n"
                       f"`{datetime.now(time_zone).strftime(date_form)} "
                       f"{datetime.now(time_zone).strftime(time_form)}`")


async def get_timezone(target):
    """ Returns timezone of the parameter in command. """
    if "(Uk)" in target:
        target = target.replace("Uk", "UK")
    if "(Us)" in target:
        target = target.replace("Us", "US")
    if " Of " in target:
        target = target.replace(" Of ", " of ")
    if "(Western)" in target:
        target = target.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in target:
        target = target.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in target:
        target = target.replace("Nl", "NL")

    for country_code in country_names:
        if target == country_names[country_code]:
            return timezone(country_timezones[country_code][0])
    try:
        if country_names[target]:
            return timezone(country_timezones[target][0])
    except KeyError:
        return