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
        """<code> - Сделать красивую фотку кода"""
        args = utils.get_args_raw(message)
        
        try:
            code_from_message = (await self.client.download_file(message.media)).decode('utf-8')
        except:
            code_from_message = ""
        

        try:
            reply = await message.get_reply_message()
            code_from_reply = (await self.client.download_file(reply.media)).decode('utf-8')
        except:
            code_from_reply = ""
        
        args = args or code_from_message or code_from_reply

        message = await utils.answer(message, self.strings('loading', message))
        try:
            message = message[0]
        except:
            pass

        await self.client.send_message(utils.get_chat_id(message), file=(await utils.run_sync(requests.post, 'https://carbonara-42.herokuapp.com/api/cook', json={'code': args})).content)
        await message.delete()
