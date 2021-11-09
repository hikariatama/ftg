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
import hashlib
import base64

#requires: hashlib base64


@loader.tds
class modCloudMod(loader.Module):
    strings = {"name": "ModuleCloud", 
    'no_file': '<b>Мне какой файл отправлять, не подскажешь?... 🗿</b>', 
    'cannot_check_file': '<b>Не могу прочитать файл...</b>',
    'cannot_join': '<b>Не могу вступить в чат. Может, ты в бане?</b>',
    'sent': '<b>Файл отправлен на проверку</b>',
    'tag': '<b>🦊 @innocoffee_alt, модуль на добавление в базу</b>',
    'upload_error': '🦊 <b>Upload error</b>',
    'args': '🦊 <b>Args not specified</b>',
    'mod404': '🦊 <b>No results found in database</b>'
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


    async def cloudcmd(self, message):
        """.cloud <command \\ mod_name> - Lookup mod in @innomods_database"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args', message))
            return

        entity = await self.client.get_entity("@innomods_database")
        try:
            msgs = await self.client.get_messages(entity, limit=100)
        except:
            try:
                await self.client(telethon.tl.functions.channels.JoinChannelRequest(entity))
            except:
                await utils.answer(message, self.strings('cannot_join', message))
                return
            msgs = await self.client.get_messages(entity, limit=100)

        for msg in msgs:
            if args.lower() in re.sub(r'<.*?>', '', msg.text.lower()):
                await utils.answer(message, msg.text)
                # await self.client.forward_messages(utils.get_chat_id(message), [msg.id], entity)
                # await message.delete()
                return

        await utils.answer(message, self.strings('mod404', message))



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


        sha1 = hashlib.sha1()
        sha1.update(code.encode('utf-8'))
        file_hash = str(sha1.hexdigest())
        open('/root/ftg/verified_mods.db', 'a').write(file_hash + '\n')

        encoded_string = base64.b64encode(file)
        stout = encoded_string.decode("utf-8")
        TOKEN = open('/root/ftg/git.token', 'r').read()
        USERNAME = 'innocoffee-ftg'
        REPO = 'host'
        url = f'https://api.github.com/repos/{USERNAME}/{REPO}/contents/{filename}'
        head = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
        git_data = '{"message": "Upload file", "content":' + '"' + stout + '"' + '}'
        r = requests.put(url, headers=head, data=git_data)
        url = f'https://github.com/innocoffee-ftg/host/raw/master/{filename}'

        commands = ""
        for command in re.findall(r'[\n][ \t]+async def ([^\(]*?)cmd', code):
            commands += '<code>.' + command + '</code>\n'

        await message.delete()
        await self.client.send_message('t.me/innomods_database', f'🦊 <b><u>{title}</u></b>\n<i>{description}</i>\n\n📋 <b><u>Команды:</u></b>\n{commands}\n🚀 <code>.dlmod {url}</code>\n\n#' + ' #'.join(tags.split(',')))
