"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Carbon
#<3 pic: https://img.icons8.com/fluency/48/000000/code.png
#<3 desc: Делает красивые Code Сниппеты.

import os
from .. import loader, utils
import time

import urllib.parse
import requests
import logging

#requires: urllib requests

logger = logging.getLogger(__name__)

@loader.tds
class CarbonMod(loader.Module):
    strings = {
        'name': 'Carbon', 
        'args': '🦊 <b>No args specified</b>',
        'loading': '🦊 <b>Loading...</b>'
    }

    async def client_ready(self, client, db):
        self.client = client

    async def carboncmd(self, message):
        """.carbon <code> - Сделать красивую фотку кода"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings('loading', message))
        try:
            message = message[0]
        except:
            pass

        url = 'https://carbonnowsh.herokuapp.com/?code=' + urllib.parse.quote_plus(args).replace('%0A', '%250A').replace('%23', '%2523').replace('%2F', '%252f')
        logger.info('[Carbon]: Fetching url ' + url)

        await self.client.send_message(utils.get_chat_id(message), file=requests.get(url).content)
        await message.delete()
