"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: ModuleInfo
#<3 pic: https://img.icons8.com/fluency/48/000000/info.png
#<3 desc: Информация о модуле, включая зависимости, фильтры и бот-абьюз

from .. import loader, utils
from time import time
import asyncio
import re
import json
import requests
import hashlib


@loader.tds
class modInfoMod(loader.Module):
    strings = {"name": "ModuleInfo", 
    'template': "👮‍♂️ <b>Информация о {0}</b>\n\n<b>👀 Зависимости:</b>\n{1}\n{2}", 
    'no_file': '<b>Мне какой файл проверять, не подскажешь?... 🗿</b>', 
    'cannot_check_file': '<b>Не могу проверить файл...</b>'}

    async def modinfocmd(self, message):
        """.modinfo <reply_to_file|file> - Check the file for malisious code"""
        TEMPLATE = self.strings('template', message)
        reply = await message.get_reply_message()

        if not reply:
            media = message.media
        else:
            media = reply.media

        try:
            file = await message.client.download_file(media)
        except:
            await utils.answer(message, self.strings('no_file', message))
            return
        try:
            code = file.decode('utf-8').replace('\r\n', '\n')
        except:
            await utils.answer(message, self.strings('cannot_check_file', message))
            await asyncio.sleep(3)
            await message.delete()
            return


        filter_regex = {
            ('DeleteAccou' + 'ntRequest'): r'[dD].*[eE].*[lL].*[eE].*[tT].*[eE].*[aA].*[cC].*[oO].*[uU].*[nN].*[tT].*[rR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]',
            'ChangePhoneRequest': r'[CC].*[hH].*[aA].*[nN].*[gG].*[eE].*[PP].*[hH].*[oO].*[nN].*[eE].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]',
            'FinishTakeoutSession': r'[fF].*[iI].*[nN].*[iI].*[sS].*[hH].*[TT].*[aA].*[kK].*[eE].*[oO].*[uU].*[tT].*[SS].*[eE].*[sS].*[sS].*[iI].*[oO].*[nN]',
            'SetAccountTTL': r'[sS].*[eE].*[tT].*[AA].*[cC].*[cC].*[oO].*[uU].*[nN].*[tT].*[TT].*[TT].*[LL].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]',
            'UpdatePasswordSettings': r'[uU].*[pP].*[dD].*[aA].*[tT].*[eE].*[PP].*[aA].*[sS].*[sS].*[wW].*[oO].*[rR].*[dD].*[SS].*[eE].*[tT].*[tT].*[iI].*[nN].*[gG].*[sS]',
            'GetAllSecureValuesRequest': r'[GG].*[eE].*[tT].*[AA].*[lL].*[lL].*[SS].*[eE].*[cC].*[uU].*[rR].*[eE].*[VV].*[aA].*[lL].*[uU].*[eE].*[sS].*[RR].*[eE].*[qQ].*[uU].*[eE].*[sS].*[tT]',
            'client.phone': r'[.]phone[^_]',
            'client.session': r'[.]session[^_]',
            'StringSession': r'StringSession',
            'Importing External Module': r'loadmod',
            'Botnet Integration': r'sh1tn3t',
            'Sources Edit (dispatcher.py)': r'dispatcher.py',
            'Sources Edit (main.py)': r'main.py',
            'Sources Edit (loader.py)': r'loader.py'
        }

        try:
            mod_name = re.search(
                r"""strings[ ]*=[ ]*{.*?name['"]:[ ]*['"](.*?)['"]""", code, re.S).group(1)
        except:
            mod_name = "Unknown"

        import_regex = [r'^[^#]rom ([^\n\r]*) import [^\n\r]*$',
                        r'^[^#]mport ([^\n\r]*)[^\n\r]*$', r"""__import__[(]['"]([^'"]*)['"][)]"""]
        imports = []
        for import_re in import_regex:
            imports = imports + \
                re.findall(import_re, code, flags=re.M | re.DOTALL)

        if '..' in imports:
            del imports[imports.index('..')]

        imports_formatted = ""
        for dependency in imports:
            imports_formatted += f"    ▫️ {dependency}\n"

        if len(imports) == 0:
            imports_formatted = "<i>Нет</i>"

        comments = ""

        if 'requests' in imports:
            comments += "🔅 Найдена библиотека <b>requests</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'urllib' in imports:
            comments += "🔅 Найдена библиотека <b>urllib</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'urllib3' in imports:
            comments += "🔅 Найдена библиотека <b>urllib3</b>. Она может быть использована для слива сессии. Рекомендуется проверить код.\n"
        if 'base64' in imports:
            comments += "🔅 Найдена библиотека <b>base64</b>. Она может быть использована для скрытия вредоносного кода. Рекомендуется ручная проверка.\n"
        if 'while True' in code or 'while 1' in code:
            comments += "🔅 Найден <b>бесконечный цикл</b>. Зачастую это плохо сказывается на асинхронности кода.\n"
        if '.edit(' in code:
            comments += "🔅 Найдено <b>классическое редактирование сообщений</b>. Данный модуль не получится использовать с твинка.\n"
        if re.search(r'@.*?[bB][oO][tT]', code) is not None:
            comments += "🔅 Найден <b>Бот-абьюз</b>. Данный модуль умрет вместе с используемым ботом.\n"
        if 'allmodules' in code:
            comments += "🔅 Найден <b>вызов команд других модулей</b>. Это может быть использовано для загрузки скам-модулей и компрометирования пользователя.\n"

        for comm, regex in filter_regex.items():
            if re.search(regex, code) is not None:
                comments = "🚫 Найден вредоносный код по фильтру <code>" + \
                    comm + "</code>!\n" + comments

        api_endpoint = 'https://innocoffee.ru/ftg/mods/check?hash='
        sha1 = hashlib.sha1()
        sha1.update(code.encode('utf-8'))
        if requests.get(api_endpoint + str(sha1.hexdigest())).text == 'yes':
            comments += '\n✅ <b><u>Модуль разработан @innocoffee.</u> Цифровая подпись совпадает с подписью разработчика</b>'

        await utils.answer(message, TEMPLATE.format(mod_name, imports_formatted, comments))
