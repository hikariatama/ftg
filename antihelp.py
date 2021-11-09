"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: AntiHelp
#<3 pic: https://img.icons8.com/fluency/48/000000/manual.png
#<3 desc: Автоматически удаляет .help из чата по прошествии определенного времени

from .. import loader, utils
import telethon
import logging
import os
import time
import re
import asyncio

logger = logging.getLogger(__name__)


@loader.tds
class AntiHelpMod(loader.Module):
    """Автоматически удаляет .help из чата по прошествии определенного времени"""
    strings = {
        'name': 'AntiHelp', 
        'as_on': '🦊 <b>Anti Help On</b>',
        'as_off': '🦊 <b>Anti Help Off</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.me = str((await client.get_me()).id)
        self.chats = db.get('AntiHelp', 'chats', [])


    async def antihelpcmd(self, message):
        """.antihelp - Toggle antihelp in current chat"""
        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats.append(chat)
            await utils.answer(message, self.strings('as_on', message))
        else:
            self.chats.remove(chat)
            await utils.answer(message, self.strings('as_off', message))

        self.db.set('AntiHelp', 'chats', self.chats)

    async def antihelpchatscmd(self, message):
        """.antihelpchats - List chats, where antihelp is active"""
        res = f"🦊 <b>AntiHelp is active in {len(self.chats)} chats:</b>\n\n"
        for chat in self.chats:
            chat_obj = await self.client.get_entity(int(chat))
            if getattr(chat_obj, 'title', False):
                chat_name = chat_obj.title
            else:
                chat_name = chat_obj.first_name

            res += "    ◾️ " + chat_name + "\n"

        await utils.answer(message, res)


    async def watcher(self, message):
        try:
            cid = str(utils.get_chat_id(message))

            if cid not in self.chats:
                return

            search = getattr(message, 'message', '') + getattr(message, 'caption', '')
            if '@' in search:
                search = search[:search.find('@')]
                tagged = True
            else:
                tagged = False

            if search in ['.help', '!help', '1help', ',help', 'zhelp', '.хелп']:
                logger.debug(f'[AntiHelp]: Removing 1 message from {cid}')
                await message.delete()
                if tagged:
                    try:
                        await self.allmodules.commands['warn'](await self.client.send_message(message.peer_id, f'.warn {message.from_id} calling help of another member'))
                    except:
                        pass
                    await asyncio.sleep(2)
                    async for msg in self.client.iter_messages(int(cid), offset_id=message.id, reverse=True):
                        if msg is telethon.tl.types.Message and msg.reply_to.reply_to_msg_id == message.id:
                            await self.client.delete_messages(int(cid), [msg])
        except:
            logger.exception('debugging')
            pass
