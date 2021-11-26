"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: RateMod
#<3 pic: https://img.icons8.com/fluency/48/000000/heart-with-pulse.png
#<3 desc: Показать оценку модуля

from .. import loader, utils
import requests
import re
import hashlib

URL_REGEX = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

@loader.tds
class RateModuleMod(loader.Module):
    strings = {
        "name": "RateMod", 
        'template': "👮‍♂️ <b>Module </b><code>{}</code><b> score:</b>\n{} {} <b>[{}]</b>\n\n{}", 
        'no_file': '<b>What should I check?... 🗿</b>', 
        'cannot_check_file': '<b>Cannot check file...</b>'
    }

    async def client_ready(self, client, db):
        self.client = client

    async def ratemodcmd(self, message):
        """<reply_to_file|file|link|reply_to_link> - Rate code"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply and not getattr(reply, 'media', None) and not getattr(message, 'media', None) and not args and not re.match(URL_REGEX, args):
            return await utils.answer(message, self.strings('no_file'))

        checking = getattr(reply, 'media', None) if getattr(reply, 'media', None) is not None else (getattr(message, 'media', None) if getattr(message, 'media', None) is not None else (args if args and re.match(URL_REGEX, args) else 0))
        if type(checking) is int:
            return await utils.answer(message, self.strings('no_file'))

        if type(checking) is not str:
            try:
                file = await self.client.download_file(getattr(reply, 'media', None) if getattr(reply, 'media', None) is not None else getattr(message, 'media', None))
            except:
                return await utils.answer(message, self.strings('cannot_check_file', message))

            try:
                code = file.decode('utf-8').replace('\r\n', '\n')
            except:
                return await utils.answer(message, self.strings('cannot_check_file', message))

        else:
            try:
                code = (await utils.run_sync(requests.get, args)).text
            except:
                return await utils.answer(message, self.strings('cannot_check_file', message))
        
        try:
            mod_name = re.search(r"""strings[ ]*=[ ]*{.*?name['"]:[ ]*['"](.*?)['"]""", code, flags=re.S).group(1)
        except:
            mod_name = "Unknown"

        import_regex = [r'^[^#]rom ([^\n\r]*) import [^\n\r]*$', r'^[^#]mport ([^\n\r]*)[^\n\r]*$', r"""__import__[(]['"]([^'"]*)['"][)]"""]
        imports = [re.findall(import_re, code, flags=re.M | re.DOTALL) for import_re in import_regex]

        if '..' in imports: del imports[imports.index('..')]

        splitted = [_ for _ in list(
            zip(
                list(
                    map(lambda x: len(re.findall(r'[ \t]+(if|elif|else).+:', x)),
                        re.split(r'[ \t]*async def .*?cmd\(', code)
                    )
                ),
                [''] + re.findall(r'[ \t]*async def (.*?)cmd\(', code)
            )
        ) if _[0] > 10]

        comments = ""

        score = 5.
        if len(imports) > 10:
            comments += f"🔻 <code>{{-0.1}}</code> <b>A lot of imports ({len(imports)}) </b><i>[affects memory usage]</i>\n"
            score -= .1
        if 'requests' in imports and 'utils.run_sync' not in code:
            comments += "🔻 <code>{-0.5}</code> <b>Synchronous requests</b> <i>[stops runtime]</i>\n"
            score -= .5
        if 'while True' in code or 'while 1' in code:
            comments += "🔻 <code>{-0.5}</code> <b>Infinite loop</b> <i>[could stop runtime]</i>\n"
            score -= .5
        if '.edit(' in code:
            comments += "🔻 <code>{-0.3}</code> <b>Classic edits</b> <i>[module won't work with twinks]</i>\n"
            score -= .3
        if '.client' in code.replace('self.client', ''):
            comments += "🔻 <code>{deprecated}</code> <b>message.client</b> <i><s>[module won't work with twinks]</s></i>\n"
            score -= 0
        if re.search(r'@.*?[bB][oO][tT]', code) is not None:
            bots = ' | '.join(re.findall(r'@.*?[bB][oO][tT]', code))
            comments += f"🔻 <code>{{-0.5}}</code> <b>Bot abuse (</b><code>{bots}</code><b>)</b> <i>[module will die with abusing bot]</i>\n"
            score -= .5
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^" \t]', code) is not None:
            undoc = ' | '.join([_ for _ in re.findall(r'[ \t]+async def (.*?)cmd.*\n[ \t]+[^" \t]', code)])
            comments += f"🔻 <code>{{-0.5}}</code> <b>No docs (</b><code>{undoc}</code><b>)</b> <i>[all commands should be documented]</i>\n"
            score -= .5
        if 'time.sleep' in code or 'from time import sleep' in code:
            comments += "🔻 <code>{-0.5}</code> <b>Synchronous sleep</b> <i>[stops runtime]</i>\n"
            score -= .5
        if [_ for _ in code.split('\n') if len(_) > 300]:
            ll = max([len(_) for _ in code.split('\n') if len(_) > 300])
            comments += f"🔻 <code>{{-0.1}}</code> <b>Long lines ({ll})</b> <i>[affects code readability]</i>\n"
            score -= .1
        if re.search(r'[\'"] ?\+ ?.*? ?\+ ?[\'"]', code) is not None:
            comments += "🔻 <code>{-0.2}</code> <b>Avoiding f-strings</b> <i>[can cause exceptions, affects readability]</i>\n"
            score -= .2
        if splitted:
            comments += f"🔻 <code>{{-0.3}}</code> <b>Long 'if' trees (</b><code>{' | '.join([f'{chain} in {fun}' for chain, fun in splitted])}</code><b>)</b> <i>[affects readability and runtime]</i>\n"
            score -= .3
        if 'utils.answer' in code:
            comments += "🔸 <code>{+0.3}</code> <b>utils.answer</b> <i>[compatibility with twinks]</i>\n"
            score += .3
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^" \t]', code) is None:
            comments += "🔸 <code>{+0.2}</code> <b>Full docstrings</b> <i>[all commands are documented]</i>\n"
            score += .2
        if 'self.client' in code:
            comments += "🔸 <code>{+0.2}</code> <b>Accessing client via self.client</b> <i>[compatibility with twinks]</i>\n"
            score += .2
        if 'requests' in imports and 'utils.run_sync' in code or 'aiohttp' in imports:
            comments += "🔸 <code>{+0.3}</code> <b>Asynchronous requests</b> <i>[don't stop runtime]</i>\n"
            score += .3


        api_endpoint = 'https://innocoffee.ru/ftg/mods/check?hash='
        sha1 = hashlib.sha1()
        sha1.update(code.encode('utf-8'))
        try:
            check_res = (await utils.run_sync(requests.get, api_endpoint + str(sha1.hexdigest()))).text
        except:
            check_res = ""

        if check_res in ['yes', 'db']:
            comments += "🔸 {+1.0} Module is verified"
            score += 1.0

        score = round(score, 1)

        score = min(score, 5.0)
        await utils.answer(message, self.strings('template').format(mod_name, '⭐️' * round(score), score, ['Very bad', 'Bad', 'Moderate', 'Middle', 'Good', 'Perfect'][round(score)], comments))
