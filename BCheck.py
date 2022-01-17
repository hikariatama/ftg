"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: BCheck
#<3 pic: https://img.icons8.com/fluency/48/000000/cat-eyes.png
#<3 desc: Массовое сканирование чата на наличие слитых номеров.

from .. import loader, utils
import asyncio
import requests
import json

# requires: requests json

@loader.tds
class BCheckMod(loader.Module):
    """Массовая проверка участников чата на наличие слитых номеров."""
    strings = {"name":"BCheck", 
    'checking': '<b>Проверяю участников этого замечательного чата на наличие слитых номеров... Возможно, придется немного подождать, если чатик большой...</b>', 
    'check_in_progress': 'Идет проверка...', 
    'search_header': "Результат поиска: ",
    'not_found': "Результат: <code>Ничего не найдено</code>", 
    'check_started': 'Начинаю проверку в чате'}

    async def bcheckcmd(self, message):
        """Проверить всех участников чата"""
        await utils.answer(message, self.strings('checking'))

        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await message.edit(check_result + '\n\n' + self.strings('check_in_progress'))
            await asyncio.sleep(1)


        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await message.edit(check_result) 

    async def bchecksilentcmd(self, message):
        """Проверить всех участников чата (Тихий режим)"""
        await message.delete()
        msg = await message.client.send_message('me', self.strings('check_started', message))
        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await msg.edit(check_result + '\n\n' + self.strings('check_in_progress', message))
            await asyncio.sleep(1)


        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await msg.edit(check_result)

