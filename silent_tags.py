"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: SilentTags
#<3 pic: https://img.icons8.com/fluency/48/000000/witch.png
#<3 desc: Для тех, кто не любит, когда их тегают

from .. import loader, utils
from telethon.tl.functions.channels import CreateChannelRequest
import logging

logger = logging.getLogger(__name__)

@loader.tds
class SilentTagsMod(loader.Module):
    """Для тех, кто не любит, когда их тегают"""

    strings = {
        "name": "SilentTags",
        "tagged": "<b>👋🏻 Тебя отметили в <a href=\"{}\">{}</a> by <a href=\"tg://user?id={}\">{}</a></b>\n<code>Message:</code>\n{}\n<b>Link: <a href=\"https://t.me/c/{}/{}\">click</a></b>",
        "tag_mentioned": "<b>👾 [Silent Tags]: Пользователь не получил уведомление об этом упоминании. Дождитесь ответа.</b>", 
        "stags_status": "<b>👾 Silent Tags are {}</b>"
    }

    async def find_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == "silent-tags-log":
                return d.entity

        return (await self.client(CreateChannelRequest("silent-tags-log", f"Messages with @{self.un} will appear here", megagroup=True))).chats[0]


    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.stags = db.get('SilentTags', 'stags', False)
        self.un = (await client.get_me()).username
        if self.un is None:
            raise Exception('You cannot load this module because you do not have username')
            return

        self.c = await self.find_db()

    async def stagscmd(self, message):
        """<on\\off> - Toggle notifications about tags"""
        args = utils.get_args_raw(message)

        if args not in ["on", "off"]:
            await utils.answer(message, self.strings("stags_status", message).format('active' if self.stags else 'inactive'))
            return

        args = True if args == "on" else False
        self.db.set('SilentTags', "stags", args)
        self.stags = args
        await utils.answer(message, self.strings('stags_status').format("now on" if args else "now off", message))

    async def watcher(self, message):
        try:
            if message.mentioned and self.stags:
                await self.client.send_read_acknowledge(message.chat_id, clear_mentions=True)
                cid = utils.get_chat_id(message)

                if message.is_private:
                    ctitle = 'pm'
                else:
                    chat = await message.get_chat()
                    grouplink = f'https://t.me/{chat.username}' if getattr(chat, "username", None) is not None else ""
                    ctitle = chat.title if getattr(chat, 'title', None) is not None else chat.first_name

                uid = message.from_id

                try:
                    user = await self.client.get_entity(message.from_id)
                    uname = user.first_name
                except:
                    uname = 'Unknown user'

                await self.client.send_message(self.c, self.strings('tagged').format(grouplink, ctitle, uid, uname, message.text, cid, message.id), link_preview=False)
                await utils.answer(message, self.strings('tag_mentioned'))
        except Exception as e:
            logger.exception(e)
