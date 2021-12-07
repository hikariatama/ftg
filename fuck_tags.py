"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: FuckTags
#<3 pic: https://img.icons8.com/fluency/48/000000/radio-waves.png
#<3 desc: "Не тегайте меня блять!"

from .. import loader, utils
import asyncio
import telethon

@loader.tds
class FuckTagsMod(loader.Module):
    """Не тегайте меня блять!"""
    strings = {"name":"FuckTags",
    "args": "🦊 <b>Incorrect args specified</b>", 
    "on": "🦊 <b>Now I ignore tags in this chat</b>",
    "off": "🦊 <b>Now I don't ignore tags in this chat</b>",
    "on_strict": "🦊 <b>Now I automatically read messages in this chat</b>",
    "off_strict": "🦊 <b>Now I don't automatically read messages in this chat</b>",
    "do_not_tag_me": "🦊 <b>Please, do not tag me.</b>"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self._ratelimit = []

    async def fucktagscmd(self, message):
        """<chat|optional> - Включить \\ выключить возможность тегать вас"""
        args = utils.get_args_raw(message)
        try:
            try:
                args = int(args)
            except:
                pass
            cid = (await self.client.get_entity(args)).id
        except:
            cid = utils.get_chat_id(message)

        self._ratelimit = list(set(self._ratelimit) - set([cid]))

        if cid not in self.db.get('FuckTags', 'tags', []):
            self.db.set('FuckTags', 'tags', self.db.get('FuckTags', 'tags', []) + [cid])
            await utils.answer(message, self.strings('on', message))
        else:
            self.db.set('FuckTags', 'tags', list(set(self.db.get('FuckTags', 'tags', [])) - set([cid])))
            await utils.answer(message, self.strings('off', message))

    async def fuckallcmd(self, message):
        """<chat|optional> - Включить \\ выключить режим авточтения в чате"""
        args = utils.get_args_raw(message)
        try:
            try:
                args = int(args)
            except:
                pass
            cid = (await self.client.get_entity(args)).id
        except:
            cid = utils.get_chat_id(message)

        if cid not in self.db.get('FuckTags', 'strict', []):
            self.db.set('FuckTags', 'strict', self.db.get('FuckTags', 'strict', []) + [cid])
            await utils.answer(message, self.strings('on_strict', message))
        else:
            self.db.set('FuckTags', 'strict', list(set(self.db.get('FuckTags', 'strict', [])) - set([cid])))
            await utils.answer(message, self.strings('off_strict', message))

    async def fuckchatscmd(self, message):
        """Показать активные авточтения в чатах"""
        res = "<b>== FuckTags ==</b>\n"
        for chat in self.db.get('FuckTags', 'tags', []):
            try:
                c = await self.client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + '\n'
            except:
                res += str(chat) + '\n'

        res += "\n<b>== FuckMessages ==</b>\n"
        for chat in self.db.get('FuckTags', 'strict', []):
            try:
                c = await self.client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + '\n'
            except:
                res += str(chat) + '\n'

        await utils.answer(message, res)


    async def watcher(self, message):
        try:
            if utils.get_chat_id(message) in self.db.get('FuckTags', 'tags', []) and message.mentioned:
                await self.client.send_read_acknowledge(message.chat_id, message, clear_mentions=True)
                if utils.get_chat_id(message) not in self._ratelimit:
                    msg = await utils.answer(message, self.strings('do_not_tag_me', message))
                    self._ratelimit.append(utils.get_chat_id(message))
                    await asyncio.sleep(3)
                    try:
                        msg = msg[0]
                    except:
                        pass

                    await msg.delete()
            elif utils.get_chat_id(message) in self.db.get('FuckTags', 'strict', []):
                await self.client.send_read_acknowledge(message.chat_id, message)
        except:
            pass


