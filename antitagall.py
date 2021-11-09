"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: AntiTagAll
#<3 pic: https://img.icons8.com/fluency/48/000000/manual.png
#<3 desc: Банит тех, кто выполняет TagAll

from .. import loader, utils
import telethon
import logging
import os
import time
import re

logger = logging.getLogger(__name__)


@loader.tds
class AntiTagAllMod(loader.Module):
    """Банит тех, кто выполняет TagAll"""
    strings = {
        'name': 'AntiTagAll', 
        'atagall_on': '🦊 <b>AntiTagAll On\nAction: {}</b>',
        'atagall_off': '🦊 <b>AntiTagAll Off</b>',
        'tagall_detected': '🦊 <b>Seems like <a href="tg://user?id={}">{}</a> used TagAll.\n👊 Action: I {}</b>', 
        'args': '🦊 <b>Args are incorrect</b>',
        'action_set': '🦊 <b>Action set to "{}"</b>',
        'range_set': '🦊 <b>Current limit is {} per {}</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.me = str((await client.get_me()).id)
        self.chats = db.get('AntiTagAll', 'chats', {})


    async def antitagallcmd(self, message):
        """.antitagall - Toggle antitagall in current chat"""
        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = 'delmsg'
            await utils.answer(message, self.strings('atagall_on', message).format('delmsg'))
        else:
            del self.chats[chat]
            await utils.answer(message, self.strings('atagall_off', message))

        self.db.set('AntiTagAll', 'chats', self.chats)

    async def atagallactioncmd(self, message):
        """.atagallaction <mute | ban | kick | warn | delmsg> - Set action raised on tagall for current chat"""
        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg']:
            await utils.answer(message, self.strings('args', message))
            return

        self.chats[chat] = args
        self.db.set('AntiTagAll', 'chats', self.chats)
        await utils.answer(message, self.strings('action_set', message).format(args))


    async def atagallchatscmd(self, message):
        """.atagallchats - List chats, where antitagall is active"""
        res = f"🦊 <b>AntiTagAll is active in {len(self.chats)} chats:</b>\n\n"
        for chat in self.chats:
            chat_obj = await self.client.get_entity(int(chat))
            if getattr(chat_obj, 'title', False):
                chat_name = chat_obj.title
            else:
                chat_name = chat_obj.first_name

            res += "    🐲 " + chat_name + "\n"

        await utils.answer(message, res)


    async def watcher(self, message):
        try:
            cid = str(utils.get_chat_id(message))

            if cid not in self.chats:
                return

            action = self.chats[cid]

            user = message.from_id

            user_obj = await self.client.get_entity(int(user))
            user_name = getattr(user_obj, 'first_name', '') + ' ' + (user_obj.last_name if getattr(user_obj, 'last_name', '') is not None else '')
            if getattr(message, 'entities', None) is None:
                return
            mentions = [_ for _ in message.entities if type(_) is telethon.tl.types.MessageEntityMention or type(_) is telethon.tl.types.MessageEntityMentionName]
            # logger.info(message.entities)
            if len(mentions) < 5:
                return

            try:
                await message.delete()
            except:
                pass

            self.warn = ('warn' in self.allmodules.commands)

            if action == "delmsg":
                await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'deleted message'))
            elif action == "kick":
                await self.client.kick_participant(int(cid), int(user))
                await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'kicked him'))
            elif action == "ban":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'banned him for 15 mins'))
            elif action == "mute":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, send_messages=True)))
                await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'muted him for 15 mins'))
            elif action == "warn":
                if not self.warn:
                    await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'should have warned him, but Warns is not installed'))
                else:
                    warn_msg = await self.client.send_message(int(cid), f'.warn {user} tagall')
                    await self.allmodules.commands['warn'](warn_msg)
                    await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'warned him'))
            else:
                await self.client.send_message(int(cid), self.strings('tagall_detected').format(user, user_name, 'just chill 😶‍🌫️ '))
        except:
            logger.exception('error')
            pass
