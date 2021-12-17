"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: NoMeta
#<3 pic: https://img.icons8.com/fluency/50/000000/v-live.png
#<3 desc: Отключает уведомления и вразумляет людей не писать "Привет, Hi" и др.

from .. import loader, utils

@loader.tds
class NoMetaMod(loader.Module):
    """Отключает уведомления и вразумляет людей не писать "Привет, Hi" и др."""

    strings = {
        "name": "NoMeta",
        "no_meta": "<b>👾 <u>Please!</u></b>\n<b>NoMeta</b> aka <i>'Hello', 'Hi' etc.</i>\nAsk <b>directly</b>, what you want from me.",
        "no_meta_ru": "<b>👾 <u>Пожалуйста!</u></b>\n<b>Не нужно лишних сообщений</b> по типу <i>'Привет', 'Хай' и др.</i>\nСпрашивай(-те) <b>конкретно</b>, что от меня нужно."
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def nometacmd(self, message):
        """Если кто-то отправил мету по типу 'Привет', эта команда его вразумит"""
        await self.client.send_message(message.peer_id, self.strings('no_meta'), reply_to=getattr(message, 'reply_to_msg_id', None))
        await message.delete()

    async def watcher(self, message):
        try:
            text = message.raw_text
        except:
            return

        if not message.is_private: return

        meta = [
            'привет', 'хай', 'hi', 'hello', 'hey there',
            'konichiwa', 'hey'
        ]

        meta_ru = [
            'хелло', 'хеллоу', 'хэллоу',
            'коничива', 'алоха', 'слушай', 'о', 'слуш',
            'м?', 'а?', 'хей', 'хэй', 'йо', 'йоу',
            'прив', 'дан', 'yo'
        ]

        if message.raw_text.lower() in meta:
            await self.client.send_message(message.peer_id, self.strings('no_meta'), reply_to=message.id)
            await self.client.send_read_acknowledge(message.chat_id, clear_mentions=True)

        if message.raw_text.lower() in meta_ru:
            await self.client.send_message(message.peer_id, self.strings('no_meta_ru'), reply_to=message.id)
            await self.client.send_read_acknowledge(message.chat_id, clear_mentions=True)
