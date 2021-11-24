"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: TikTok
#<3 pic: https://img.icons8.com/fluency/48/000000/tiktok.png
#<3 desc: Скачивает видосы из ТикТок без watermark

from .. import loader, utils
import asyncio

class TikTokMod(loader.Module):
    """Скачивает видео из TikTok без watermark"""
    strings = {'name': 'TikTok', 
    'loading': "<b>🦊 Подгружаю видосик с ТикТока</b>", 
    'no_link': "<b>🦊 Ты не указал ссылку</b>"}

    async def ttcmd(self, message):
        """<link> - Скачать видео с ТикТок без рекламы"""
        await utils.answer(message, self.strings('loading', message))
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('no_link', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        cb_query = await message.client.inline_query('tikdobot', args)
        await message.client.send_file(message.to_id, cb_query[1].result.content.url)
        await message.delete()
