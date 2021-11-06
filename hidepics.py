"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: HidePics
#<3 pic: https://img.icons8.com/fluency/48/000000/porn-folder.png
#<3 desc: Сохраняет картиночки интимного характера в чате и скрывает их

from .. import loader, utils
import asyncio
import os
import requests
import re
import telethon
import io
import time
import json
import logging
logger = logging.getLogger(__name__)
try:
    import hashlib
except:
    os.popen('python3 -m pip install hashlib').read()
    import hashlib
# try:
#     from PIL import Image
# except:
#     os.popen('python3 -m pip install Pillow').read()
#     from PIL import Image
# import imghdr
# try:
#     import magic
# except:
#     os.popen('python3 -m pip install python-magic').read()
#     import magic
#requires: hashlib Pillow


TEMPLATE = """
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<style>
@media screen and (min-width: 736px) {
    img {
        height: 100vh;
    }
}

@media screen and (max-width: 736px) {
    img {
        width: 100vw;
    }
}
</style>
</head>
<body>
<script>
    var pics = [^s^];
    for(var i = 0; i < pics.length; i++) {
        document.querySelector('body').innerHTML += '<img src="' + pics[i] + '"><br>';
    }
</script>
</body>
</html>
"""

@loader.tds
class HidePicsMod(loader.Module):
    """Сохраняет картиночки интимного характера в чате и скрывает их"""
    strings = {"name":"HidePics",
    "args": "🦊 <b>No args specified</b>", 
    "cat_exists": "🦊 <b>Category exists</b>",
    "cat_created": "🦊 <b>Category created</b>",
    "upload_error": "🦊 <b>x0 upload error</b>",
    "key_updated": "🦊 <b>Key updated</b>", 
    "read_error": "🦊 <b>Error while reading link</b>\n<code>{}</code>",
    "not_an_image": "🦊 <b>Not an image ({})</b>"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.chats = db.get('HidePics', 'chats', {})
        self.db.set('HidePics', 'wait', False)

    async def hpnewcatcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args', message))
            return

        # await self.client(telethon.functions.messages.CreateChatRequest(users=[], title='ftg-hidepics-' + args))
        ch = (await self.client(telethon.functions.channels.CreateChannelRequest(f"ftg-hidepics-{args}", "Just friendly chat"))).updates[1].channel_id
        self.chats[ch] = f"ftg-hidepics-{args}"
        self.db.set('HidePics', 'chats', self.chats)
        await utils.answer(message, self.strings('cat_created', message))


    # async def testcmd(self, message):
    #     entity = await self.client.get_entity(message.peer_id)
    #     await message.delete()
    #     await self.client.send_message('me', await self.find_db(entity))
    #     await self.save_db(entity, await self.find_db(entity))

    async def find_db(self, entity):
        msgs = self.client.iter_messages(
            entity=entity,
            reverse=True
        )
        res = ""
        async for msg in msgs:
            if getattr(msg, 'message', False) and msg.message.startswith('📤'):
                res += '|' + msg.message[1:]
                # result = ""
                # final = []
                # for link in res:
                    # mime = magic.Magic(mime=True)
                    # result += str(imghdr.what(io.BytesIO(requests.get('https://x0.at/' + link + '.jpg').content))) + " "
                    # result += str(magic.from_buffer(requests.get('https://x0.at/' + link).content)) + "\n"
                    # final.append(link)
                # await self.client.send_file('me', result.encode('utf-8'))

        return res[1:]


    async def save_db(self, entity, data):
        msgs = await self.client.get_messages(
            entity=entity,
            reverse=True
        )
        counter = 0
        data_remaining = data
        for msg in msgs:
            if getattr(msg, 'message', False) and msg.message.startswith('📤'):
                if data_remaining == "":
                    await self.client.send_message('me', str(msg))
                    await msg.delete()
                    continue

                await msg.edit('<code>📤' + data_remaining[:4000] + '</code>')
                if len(data_remaining) < 4000:
                    data_remaining = ""
                else:
                    data_remaining = data_remaining[4000:]
                counter += 1

        if data_remaining != "":
            await self.client.send_message(entity, '<code>📤' + data_remaining + '</code>')


    async def hpsetkeycmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args', message))
            return
        hash_object = hashlib.md5(args.encode('utf-8'))
        self.db.set('HidePics', 'key', str(hash_object.hexdigest()))
        await utils.answer(message, self.strings('key_updated', message))
        

    async def watcher(self, message):
        try:
            entity = message.peer_id
            if type(entity) is not telethon.tl.types.PeerChannel:
                return

            title = self.chats[str(entity.channel_id)]
            if not title.startswith('ftg-hidepics-'):
                return
        except:
            return

        while self.db.get('HidePics', 'wait', False):
            await asyncio.sleep(.1)
        self.db.set('HidePics', 'wait', True)

        await message.delete()

        hash_object = hashlib.md5(message.text.encode('utf-8'))
        if self.db.get('HidePics', 'key', '') == str(hash_object.hexdigest()):
            # html = io.BytesIO(TEMPLATE.replace('^s^', ','.join(['"https://x0.at/' + _ + '.jpg"' for _ in (await self.find_db(entity)).split('|')])).encode('utf-8'))
            # html.name = 'output.html'
            # msg = await self.client.send_file(entity, html)
            # await asyncio.sleep(10)
            # await msg.delete()
            await self.client.send_message('@userbot_notifies_bot', '.hp_r ' + (await self.find_db(entity)))
            self.db.set('HidePics', 'wait', False)
            return

        if message.media and type(message.media) is telethon.tl.types.MessageMediaPhoto:
            file = await self.client.download_file(message.media)
        elif 'http' in getattr(message, 'text', ''):
            try:
                # await self.client.send_message('me', re.sub(r'<.*?>', '', message.text))
                r = requests.get(re.sub(r'<.*?>', '', message.text))
                file = r.content
            except Exception as e:
                await self.client.send_message(entity, self.strings('read_error', message).format(e))
                self.db.set('HidePics', 'wait', False)
                return
        else:
            self.db.set('HidePics', 'wait', False)
            return

        x0_file = io.BytesIO(file)
        x0_file.name = str(time.time()).replace('.', '')
        try:
            x0at = requests.post('https://x0.at', files={'file': x0_file})
            url = x0at.text.replace('\n', '')
        except ConnectionError as e:
            self.db.set('HidePics', 'wait', False)
            await self.client.send_message(utils.get_chat_id(message), self.strings('upload_error', message))
            return

        ext = url.split('/', 3)[3].split('.')[1]
        if ext not in ['jpeg', 'png']:
            ms = await self.client.send_message(entity, self.strings('not_an_image', message).format(url))
            self.db.set('HidePics', 'wait', False)
            await asyncio.sleep(10)
            await ms.delete()
            return 

        db = (await self.find_db(entity)).split('|')
        if len(db) == 1 and db[0] == '':
            db = []
        db.append(url.replace('https://x0.at/', ''))
        await self.save_db(entity, '|'.join(db))

        
        self.db.set('HidePics', 'wait', False)



