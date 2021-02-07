import logging
import re
from copy import deepcopy
from subprocess import run, PIPE

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(filters.outgoing & filters.command(["hello"], '-'))
def hello(client: Client, message: Message) -> bool:
    message.reply('hello!')
    return True