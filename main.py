#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from pyrogram import Client, idle

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