"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

from .. import loader, utils
import asyncio
import requests
import json

# requires: requests json

@loader.tds
class BCheckMod(loader.Module):
    """Массовая проверка участников чата на наличие слитых номеров."""
    strings = {"name":"BCheck"}

    async def bcheckcmd(self, message):
        """.bcheck - Проверить всех участников чата"""
        await message.edit('<b>Проверяю участников этого замечательного чата на наличие слитых номеров... Возможно, придется немного подождать, если чатик большой...</b>')

        check_result = "Результат поиска: "

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.1&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await message.edit(check_result + '\n\nИдет проверка...')
            await asyncio.sleep(1)


        if check_result == "Результат поиска: ":
            check_result = "Результат: <code>Ничего не найдено</code>"

        await message.edit(check_result) 

    async def bchecksilentcmd(self, message):
        """.bchecksilent - Проверить всех участников чата (Тихий режим)"""
        await message.delete()
        msg = await message.client.send_message('me', 'Начинаю проверку в чате')
        check_result = "Результат поиска в чате: "

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.1&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"
                await msg.edit(check_result + '\n\nИдет проверка...')
            await asyncio.sleep(1)


        if check_result == "Результат поиска в чате: ":
            check_result += "<code>Ничего не найдено</code>"

        await msg.edit(check_result)

