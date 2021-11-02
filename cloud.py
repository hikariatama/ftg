"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: ModuleCloud
#<3 pic: https://img.icons8.com/fluency/48/000000/cloud-storage.png
#<3 desc: Облако модулей, верифицированных @innocoffee

from .. import loader, utils
from time import time
import asyncio
import re
import json
import requests
import telethon
import io


@loader.tds
class modCloudMod(loader.Module):
    strings = {"name": "ModuleCloud", 
    'no_file': '<b>Мне какой файл отправлять, не подскажешь?... 🗿</b>', 
    'cannot_check_file': '<b>Не могу прочитать файл...</b>',
    'cannot_join': '<b>Не могу вступить в чат. Может, ты в бане?</b>',
    'sent': '<b>Файл отправлен на проверку</b>',
    'tag': '<b>🦊 @innocoffee_alt, модуль на добавление в базу</b>'
    }


    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def addmodcmd(self, message):
        """.addmod <reply_to_file|file> - Send module to @innomods_support to add to database"""
        reply = await message.get_reply_message()
        if not reply:
            media = message.media
            msid = message.id
        else:
            media = reply.media
            msid = reply.id
        try:
            file = await message.client.download_file(media)
        except:
            await utils.answer(message, self.strings('no_file', message))
            return

        async def send(client):
            await client.forward_messages('t.me/innomods_support', [msid], utils.get_chat_id(message))
            await client.send_message('t.me/innomods_support', self.strings('tag', message))
            await utils.answer(message, self.strings('sent', message))

        # await send(self.client)

        try:
            await send(self.client)
        except:
            try:
                await self.client(telethon.tl.functions.channels.JoinChannelRequest(await self.client.get_entity('t.me/innomods_support')))
            except:
                await utils.answer(message, self.strings('cannot_join', message))
                return

            await send(self.client)

    async def verifmodcmd(self, message):
        """.verifmod <filename>;<title>;<description>;<tags> - Verfiy module [only for @innomods admins]"""
        args = utils.get_args_raw(message).split(';')
        filename, title, description, tags = args
        reply = await message.get_reply_message()
        if not reply: return

        media = reply.media
        msid = reply.id
        try:
            file = await self.client.download_file(media)
        except:
            await utils.answer(message, self.strings('no_file', message))
            return

        try:
            code = file.decode('utf-8').replace('\r\n', '\n')
        except:
            await utils.answer(message, self.strings('cannot_check_file', message))
            await asyncio.sleep(3)
            await message.delete()
            return


        open('/tmp/cloud_file.py', 'wb').write(file)

        x0_file = io.BytesIO(file)
        x0_file.name = filename
        try:
            x0at = requests.post('https://x0.at', files={'file': x0_file})
            url = x0at.text
        except ConnectionError as e:
            url = ''

        x0_file = io.BytesIO(file)
        x0_file.name = filename

        commands = ""
        for command in re.findall(r'[\n][ \t]+async def (.*?)cmd', code):
            commands += '<code>.' + command + '</code>\n'

        await message.delete()
        await self.client.send_file('t.me/innomods_database', x0_file, caption=f'🦊 <b><u>{title}</u></b>\n<i>{description}</i>\n\n📋 <b><u>Команды:</u></b>\n{commands}\n🚀 <code>.dlmod {url}</code>\n#' + ' #'.join(tags.split(',')))
