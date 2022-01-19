"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
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
    'template': "👮‍♂️ <b>Info about {0}</b>\n\n<b>👀 Dependencies:</b>\n{1}\n<b>🔰 Safe dependencies:</b>\n{2}\n{3}", 
    'no_file': '<b>What should I check?... 🗿</b>', 
    'cannot_check_file': '<b>Cannot check file...</b>'}

    async def modinfocmd(self, message):
        """<reply_to_file|file> - Check the file for malisious code"""
        # await utils.answer(message, '<code>Got command</code>')

        TEMPLATE = self.strings('template', message)
        reply = await message.get_reply_message()

        media = message.media if not reply else reply.media
        try:
            file = await message.client.download_file(media)
        except:
            await utils.answer(message, self.strings('no_file', message))
            return
        # await utils.answer(message, '<code>Parsing file</code>')

        try:
            code = file.decode('utf-8').replace('\r\n', '\n')
        except:
            await utils.answer(message, self.strings('cannot_check_file', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        # await utils.answer(message, '<code>File parsed</code>')

        try:
            mod_name = re.search(
                r"""strings[ ]*=[ ]*{.*?name['"]:[ ]*['"](.*?)['"]""", code, flags=re.S).group(1)
        except:
            mod_name = "Unknown"

        # await utils.answer(message, '<code>Got mod name</code>')


        import_regex = [r'^[^#]rom ([^\n\r]*) import [^\n\r]*$',
                        r'^[^#]mport ([^\n\r]*)[^\n\r]*$', r"""__import__[(]['"]([^'"]*)['"][)]"""]
        imports = []
        for import_re in import_regex:
            imports += re.findall(import_re, code, flags=re.M | re.DOTALL)

        if '..' in imports:
            del imports[imports.index('..')]

        imports_formatted = ""
        safe = ['time', 'asyncio', 're', 'json', 'hashlib', 'PIL']
        safe_imports = ""
        for dependency in imports:
            if dependency in safe:
                safe_imports += f"    🦊 <code>{dependency}</code>\n"
            else:
                imports_formatted += f"    ▫️ <code>{dependency}</code>\n"

        if not imports_formatted:
            imports_formatted = "<i>No</i>"

        if not safe_imports:
            safe_imports = "<i>No</i>"


        # await utils.answer(message, '<code>Parsed imports</code>')


        comments = ""

        if 'requests' in imports:
            comments += "🔅 Library <b>requests</b>. Sends data to server\n"
        if 'urllib' in imports or 'urllib3' in imports:
            comments += "🔅 Library <b>urllib</b>. Sends data to server\n"
        if 'base64' in imports:
            comments += "🔅 Library <b>base64</b>. Can be used to hide malicious code\n"
        if 'while True' in code or 'while 1' in code:
            comments += "🔅 <b>Infinite loop</b>\n"
        if '.edit(' in code:
            comments += "🔅 <b>Editing via message.edit</b>\n"
        if re.search(r'@.*?[bB][oO][tT]', code) is not None:
            comments += "🔅 <b>Bot-abuse</b>\n"
        if 'allmodules' in code:
            comments += "🔅 <b>Calling another modules' commands</b>\n"

        api_endpoint = 'https://hikariatama.ru/ftg/mods/check?hash='
        sha1 = hashlib.sha1()
        sha1.update(code.encode('utf-8'))
        check_res = requests.get(api_endpoint + str(sha1.hexdigest())).text
        if check_res == 'db':
            comments += '\n✅ <b><u>Module is downloaded from @hikarimods_database and does not contain scam.</u> Hash confirmed</b>'


        elif check_res == 'yes':
            comments += '\n✅ <b><u>Module is created by @hikariatama.</u> Hash confirmed</b>'
        # await utils.answer(message, '<code>Sending report</code>')


        await utils.answer(message, TEMPLATE.format(mod_name, imports_formatted, safe_imports, comments))
