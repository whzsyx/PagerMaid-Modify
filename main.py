#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from random import randint

from pyrogram import Client, idle

from plugins import glovar
from plugins.functions.etc import delay

# Enable logging
logger = logging.getLogger(__name__)

# Config session
app = Client(
    session_name="pagermaid"
)
app.start()

# Hold
idle()

# Stop
app.stop()