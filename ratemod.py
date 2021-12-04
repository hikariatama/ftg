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
        'template': "👮‍♂️ <b>Оценка модуля </b><code>{}</code><b>:</b>\n{} {} <b>[{}]</b>\n\n{}", 
        'no_file': '<b>А какой модуль проверять?... 🗿</b>', 
        'cannot_check_file': '<b>Ошибка проверки</b>'
    }

    async def client_ready(self, client, db):
        self.client = client

    async def ratemodcmd(self, message):
        """<reply_to_file|file|link> - Оценить код, а также дать рекомендации по исправлениям в коде"""
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

        score = 4.6
        if len(imports) > 10:
            comments += f"🔻 <code>{{-0.1}}</code> <b>Большое кол-во зависимостей ({len(imports)}) </b><i>[занимает память]</i>\n"
            score -= .1
        if 'requests' in imports and 'utils.run_sync' not in code:
            comments += "🔻 <code>{-0.5}</code> <b>Синхронные запросы</b> <i>[останавливает выполнение]</i>\n"
            score -= .5
        if 'while True' in code or 'while 1' in code:
            comments += "🔻 <code>{-0.1}</code> <b>Бесконечный цикл</b> <i>[останавливает выполнение*]</i>\n"
            score -= .1
        if '.edit(' in code:
            comments += "🔻 <code>{-0.3}</code> <b>Классическое message.edit</b> <i>[модуль не будет работать с твинков]</i>\n"
            score -= .3
        if re.search(r'@.*?[bB][oO][tT]', code) is not None:
            bots = ' | '.join(re.findall(r'@.*?[bB][oO][tT]', code))
            comments += f"🔻 <code>{{-0.2}}</code> <b>Бот-абьюз (</b><code>{bots}</code><b>)</b> <i>[модуль умрет вместе с используемым ботом]</i>\n"
            score -= .2
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^\'" \t]', code) is not None:
            undoc = ' | '.join([_ for _ in re.findall(r'[ \t]+async def (.*?)cmd.*\n[ \t]+[^" \t]', code)])
            comments += f"🔻 <code>{{-0.4}}</code> <b>Нет докстрингов (</b><code>{undoc}</code><b>)</b> <i>[все команды должны быть задокументированы]</i>\n"
            score -= .4
        if 'time.sleep' in code or 'from time import sleep' in code:
            comments += "🔻 <code>{-0.5}</code> <b>Синхронный сон (</b><code>time.sleep</code><b>) замените на (</b><code>await asyncio.sleep</code><b>)</b> <i>[останавливает выполнение]</i>\n"
            score -= .5
        if [_ for _ in code.split('\n') if len(_) > 300]:
            ll = max([len(_) for _ in code.split('\n') if len(_) > 300])
            comments += f"🔻 <code>{{-0.1}}</code> <b>Длинные строки ({ll})</b> <i>[влияет на читаемость]</i>\n"
            score -= .1
        if re.search(r'[\'"] ?\+ ?.*? ?\+ ?[\'"]', code) is not None:
            comments += "🔻 <code>{-0.1}</code> <b>Избегание f-строк</b> <i>[вызывает проблемы, влияет на читаемость]</i>\n"
            score -= .1
        if splitted:
            comments += f"🔻 <code>{{-0.2}}</code> <b>Большие 'if' деревья (</b><code>{' | '.join([f'{chain} в {fun}' for chain, fun in splitted])}</code><b>)</b> <i>[влияет на читаемость и выполнение]</i>\n"
            score -= .2
        if '== None' in code or '==None' in code:
            comments += f"🔻 <code>{{-0.3}}</code> <b>Сравнение типов через ==</b> <i>[влияет на качество кода, вызывает проблемы]</i>\n"
            score -= .3
        if 'is not None else' in code:
            comments += f"🔻 <code>{{-0.1}}</code> <b>Неуместное использование тернарного оператора (</b><code>if some_var is not None else another</code> <b>-></b> <code>some_var or another</code><b>)</b> <i>[влияет на качество кода]</i>\n"
            score -= .1
        if 'utils.answer' in code and '.edit(' not in code:
            comments += "🔸 <code>{+0.3}</code> <b>utils.answer</b> <i>[совместимость с твинками]</i>\n"
            score += .3
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^\'" \t]', code) is None:
            comments += "🔸 <code>{+0.3}</code> <b>Докстринги</b> <i>[все команды задокументированы]</i>\n"
            score += .3
        if 'requests' in imports and 'utils.run_sync' in code or 'aiohttp' in imports:
            comments += "🔸 <code>{+0.3}</code> <b>Асинхронные запросы</b> <i>[не останавливает выполнение]</i>\n"
            score += .3


        api_endpoint = 'https://innocoffee.ru/ftg/mods/check?hash='
        sha1 = hashlib.sha1()
        sha1.update(code.encode('utf-8'))
        try:
            check_res = (await utils.run_sync(requests.get, api_endpoint + str(sha1.hexdigest()))).text
        except:
            check_res = ""

        if check_res in ['yes', 'db']:
            comments += "🔸 <code>{+1.0}</code> <b>Модуль верифицирован</b> <i>[в нем нет скама]</i>\n"
            score += 1.0

        score = round(score, 1)

        score = min(score, 5.)
        await utils.answer(message, self.strings('template').format(mod_name, '⭐️' * round(score), score, ['Говнище', 'Очень плохо', 'Плохо', 'К пиву пойдет', 'Нормально', 'Четко'][round(score)], comments))
