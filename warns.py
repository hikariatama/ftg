"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: InnoWarns
#<3 pic: https://img.icons8.com/fluency/48/000000/mail-error.png
#<3 desc: Система предупреждений для твоего чата

from .. import loader, utils
import time
import asyncio
import re
import json
import requests
import telethon
import io


@loader.tds
class InnoWarnsMod(loader.Module):
    """Warns system for your chat"""
    strings = {
        "name": "InnoWarns", 
        'args': '🦊 <b>Args not specified</b>',
        'no_reason': 'Not specified',
        'warn': '🦊 <b><a href="tg://user?id={}">{}</a></b> got {}/{} warn\nReason: <b>{}</b>',
        'chat_not_in_db': '🦊 <b>This chat has no warns yet</b>',
        'no_warns': '🦊 <b><a href="tg://user?id={}">{}</a> has no warns yet</b>', 
        'warns': '🦊 <b><a href="tg://user?id={}">{}</a> has {}/{} warns</b>\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>{}</i>',
        'warns_adm': '🦊 Warns in this chat:\n',
        'dwarn': '🦊 <b>Removed last warn from <a href="tg://user?id={}">{}</a>',
        'clrwarns': '🦊 <b>Removed all warns from <a href="tg://user?id={}">{}</a>',
        'new_a': '🦊 <b>New action when warns limit is reached for this chat: "{}"</b>',
        'new_l': '🦊 <b>New warns limit for this chat: "{}"</b>',
        'warns_limit': '🦊 <b><a href="tg://user?id={}">{}</a> reached warns limit.\nAction: I {}</b>'
    }


    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.chats = db.get('InnoWarns', 'chats', {})


    async def warncmd(self, message):
        """.warn <reply | user_id | username> <reason | optional> - Warn specified user"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
            if args:
                reason = args
            else:
                reason = self.strings('no_reason')
        else:
            try:
                user = await self.client.get_entity(args.split(maxsplit=1)[0])
            except IndexError:
                return await utils.answer(message, self.strings('args', message))

            try:
                reason = args.split(maxsplit=1)[1]
            except IndexError:
                reason = self.strings('no_reason')

        if cid not in self.chats:
            self.chats[cid] = {
                'a': 'mute', 
                'l': 5,
                'w': {}
            }

        if user.id not in self.chats[cid]['w']:
            self.chats[cid]['w'][user.id] = []
        self.chats[cid]['w'][user.id].append(reason)

        if len(self.chats[cid]['w'][user.id]) >= self.chats[cid]['l']:
            action = self.chats[cid]['a']
            user_name = user.first_name
            user = user.id
            if action == "kick":
                await self.client.kick_participant(int(cid), int(user))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'kicked him'))
            elif action == "ban":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'banned him for 15 mins'))
            elif action == "mute":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, send_messages=True)))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'muted him for 15 mins'))
            
            await message.delete()
            self.chats[cid]['w'][user] = []
        else:
            await utils.answer(message, self.strings('warn', message).format(user.id, user.first_name, len(self.chats[cid]['w'][user.id]), self.chats[cid]['l'], reason))
        self.db.set('InnoWarns', 'chats', self.chats)

    @loader.unrestricted
    async def warnscmd(self, message):
        """.warns <reply | user_id | username | optional> - Show warns in chat, or for specified user"""
        if message.is_private:
            await message.delete()
            return

        cid = utils.get_chat_id(message)
        async def check_admin(user_id):
            async for member in self.client.iter_participants(cid, filter=telethon.tl.types.ChannelParticipantsAdmins):
                if member.id == user_id:
                    return True
            return False

        async def send_user_warns(usid):
            if str(cid) not in self.chats:
                await utils.answer(message, self.strings('chat_not_in_db', message))
                return
            elif usid not in self.chats[str(cid)]['w'] or len(self.chats[str(cid)]['w'][usid]) == 0:
                user_obj = await self.client.get_entity(usid)
                await utils.answer(message, self.strings('no_warns', message).format(user_obj.id, user_obj.first_name))
            else:
                user_obj = await self.client.get_entity(usid)
                await utils.answer(message, self.strings('warns', message).format(user_obj.id, user_obj.first_name, len(self.chats[str(cid)]['w'][usid]), self.chats[str(cid)]['l'], '\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 '.join(self.chats[str(cid)]['w'][usid])))

        if not await check_admin(message.from_id):
            await send_user_warns(message.from_id)
        else:
            reply = await message.get_reply_message()
            args = utils.get_args_raw(message)
            if not reply and not args:
                res = self.strings('warns_adm', message)
                for user, warns in self.chats[str(cid)]['w'].items():
                    user_obj = await self.client.get_entity(user)
                    res += "🐺 <b><a href=\"tg://user?id=" + str(user_obj.id) + "\">" + getattr(user_obj, 'first_name', '') + ' ' + (user_obj.last_name if getattr(user_obj, 'last_name', '') is not None else '') + '</a></b>\n'
                    for warn in warns:
                        res += "<code>   </code>🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>" + warn + '</i>\n'

                await utils.answer(message, res)
                return
            elif reply:
                await send_user_warns(reply.from_id)
            elif args:
                await send_user_warns(args)

    async def dwarncmd(self, message):
        """.dwarn <reply | user_id | username> - Remove last warn from user"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
        else:
            try:
                user = await self.client.get_entity(args)
            except IndexError:
                return await utils.answer(message, self.strings('args', message))

        if cid not in self.chats:
            return await utils.answer(message, self.strings('chat_not_in_db', message))

        if user.id not in self.chats[cid]['w']:
            return await utils.answer(message, self.strings('no_warns', user.id, user.first_name))

        del self.chats[cid]['w'][user.id][-1]
        await utils.answer(message, self.strings('dwarn', message).format(user.id, user.first_name))
        self.db.set('InnoWarns', 'chats', self.chats)

    async def clrwarnscmd(self, message):
        """.clrwarns <reply | user_id | username> - Remove all warns from user"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
        else:
            try:
                user = await self.client.get_entity(args)
            except IndexError:
                return await utils.answer(message, self.strings('args', message))

        if cid not in self.chats:
            return await utils.answer(message, self.strings('chat_not_in_db', message))

        if user.id not in self.chats[cid]['w']:
            return await utils.answer(message, self.strings('no_warns').format(user.id, user.first_name))

        del self.chats[cid]['w'][user.id]
        await utils.answer(message, self.strings('clrwarns', message).format(user.id, user.first_name))
        self.db.set('InnoWarns', 'chats', self.chats)

    async def warnsactioncmd(self, message):
        """.warnsaction <mute | kick | ban> - Action when warns limit is reached"""
        if message.is_private:
            await message.delete()
            return

        args = utils.get_args_raw(message)
        if not args or args not in ['mute', 'kick', 'ban']:
            return await utils.answer(message, self.strings('args', message))

        cid = utils.get_chat_id(message)

        if str(cid) not in self.chats:
            self.chats[str(cid)] = {
                'a': 'mute', 
                'l': 5,
                'w': {}
            }

        self.chats[str(cid)]['a'] = args
        await utils.answer(message, self.strings('new_a', message).format(args))

    async def warnslimitcmd(self, message):
        """.warnslimit <limit:int> - Warns limit for current chat"""
        if message.is_private:
            await message.delete()
            return

        args = utils.get_args_raw(message)
        try:
            args = int(args)
        except:
            return await utils.answer(message, self.strings('args', message))

        cid = utils.get_chat_id(message)

        if str(cid) not in self.chats:
            self.chats[str(cid)] = {
                'a': 'mute', 
                'l': 5,
                'w': {}
            }

        self.chats[str(cid)]['l'] = args
        await utils.answer(message, self.strings('new_l', message).format(args))

