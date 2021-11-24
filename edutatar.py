"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: eduTatar
#<3 pic: https://img.icons8.com/fluency/48/000000/dictionary.png
#<3 desc: Удобный клиент edu.tatar.ru прямо в Telegram

from .. import loader, utils
import asyncio
import re
import json
import requests
from datetime import datetime, timedelta
import time

proxy = {
    'https': 'https://node-ru-240.astroproxy.com:10293'
}

filters = {
    'Иностранный язык (английский)': '🇺🇸 Англ',
    'Физическая культура': '⛹️‍♂️ PE',
    'Физика': '⚛️ Физон',
    'Литература': '📕 Лит-ра',
    'Математика': '📐 Maths',
    'Основы безопасности жизнедеятельности': '🧰 ОБЖ',
    'Родной язык': '🗣 Родной',
    'История': '⚒ История',
    'Родная литература': '📖 Родн.лит',
    'География': '🗺 Гео',
    'Информатика': '💻 IT',
    'Обществознание': '⚖️ Общество',
    'Русский язык': '✍️ Русский',
    'Химия': '🧪 Химия',
    'Биология': '🧬 Био',
    'Технология': '🔩 Технология'
}


@loader.tds
class eduTatarMod(loader.Module):
    strings = {"name": "eduTatar",
    'login_pass_not_specified': '<b>Необходимо указать логин и пароль от edu.tatar.ru в конфиге</b>',
    'loading_info': "<b>Гружу информацию с edu.tatar.ru, пять сек...</b>",
    'host_error': 'Error occured while parsing. Maybe edutatar host is down?',
    'no_hw': "Нет д\\з"}

    def __init__(self):
        self.config = loader.ModuleConfig("edu_tatar_login", False, lambda: "Login from edu.tatar.ru", "edu_tatar_pass", False, lambda: "Password from edu.tatar.ru",
                                          "marks_parse_delay", 300, lambda: "Delay for parsing new marks in seconds")

    async def client_ready(self, client, db):
        self.db = db
        self.sess = {"DNSID": db.get('eduTatar', 'sess', None)}
        if self.sess['DNSID'] is None:
            await self.revoke_token()

        self.client = client
        asyncio.ensure_future(self.parse_marks_async())

    async def parse_marks_async(self):
        while True:
            await self.check_marks()
            await asyncio.sleep(self.config['marks_parse_delay'])

    async def eduweekcmd(self, message):
        """Show schedule for a week"""
        if not self.config['edu_tatar_login'] or not self.config['edu_tatar_pass']:
            await utils.answer(message, self.strings('login_pass_not_specified', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        await utils.answer(message, self.strings('loading_info', message))
        data = await self.scrape_week()
        await utils.answer(message, data)

    async def edudaycmd(self, message):
        """<day:integer{0,}> - Show schedule for today"""
        if not self.config['edu_tatar_login'] or not self.config['edu_tatar_pass']:
            await utils.answer(message, self.strings('login_pass_not_specified', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        args = utils.get_args_raw(message)
        if args == "":
            offset = 0

        try:
            offset = abs(int(args))
            offset = offset * 60 * 60 * 24
        except:
            pass

        now = datetime.now()
        today = now - timedelta(hours=now.hour,
                                minutes=now.minute, seconds=now.second)
        day = time.mktime(today.timetuple()) + offset
        day_datetime = datetime.utcfromtimestamp(day)
        await utils.answer(message, self.strings('loading_info', message))
        weekdays = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday']
        data = f'📚 <b>{weekdays[day_datetime.weekday() + 1]}</b> 📚\n\n' + await self.scrape_date(day)
        await utils.answer(message, data)

    async def edutermcmd(self, message):
        """Get term grades"""
        if not self.config['edu_tatar_login'] or not self.config['edu_tatar_pass']:
            await utils.answer(message, self.string('login_pass_not_specified', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        await utils.answer(message, self.strings('loading_info', message))
        data = await self.scrape_term(utils.get_args_raw(message))
        await utils.answer(message, data)

    async def revoke_token(self):
        try:
            answ = await utils.run_sync(requests.post, 'https://edu.tatar.ru/logon', headers={
                'Host': 'edu.tatar.ru',
                'Connection': 'keep-alive',
                'Content-Length': '52',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'Origin': 'https://edu.tatar.ru',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-GPC': '1',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Referer': 'https://edu.tatar.ru/logon',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9'
            }, data={'main_login2': self.config['edu_tatar_login'], 'main_password2': self.config['edu_tatar_pass']}, allow_redirects=True, proxies=proxy)
        except requests.exceptions.ProxyError:
            return self.strings('host_error')

        if 'DNSID' in dict(answ.cookies):
            self.sess = dict(answ.cookies)
        else:
            raise ValueError('Failed logging in')

        self.db.set('eduTatar', 'sess', self.sess['DNSID'])

    async def check_marks(self):
        marks_tmp = self.db.get('eduTatar', 'marks', {}).copy()
        await self.scrape_term('')
        marks_new = self.db.get('eduTatar', 'marks', {}).copy()
        for subject, current_marks_2 in list(marks_new.items()):
            if subject not in marks_tmp:
                current_marks_1 = []
            else:
                current_marks_1 = marks_tmp[subject]

            try:
                subject = filters[subject]
            except KeyError:
                pass

            for i in range(min(len(current_marks_1), len(current_marks_2))):
                if current_marks_1[i] != current_marks_2[i]:
                    await self.client.send_message('@userbot_notifies_bot', utils.escape_html(f'<b>{subject}: {current_marks_1[i]}->{current_marks_2[i]}\n</b><code>{" ".join(list(map(str, current_marks_2)))}</code>'))
                    await asyncio.sleep(.5)

            for i in range(min(len(current_marks_1), len(current_marks_2)), len(current_marks_2)):
                await self.client.send_message('@userbot_notifies_bot', utils.escape_html(f'<b>{subject}: {current_marks_2[i ]}\n</b><code>{" ".join(list(map(str, current_marks_2)))}</code>'))
                await asyncio.sleep(.5)

    async def scrape_date(self, date):
        try:
            answ = await utils.run_sync(requests.get, 'https://edu.tatar.ru/user/diary/day?for=' + str(date), cookies=self.sess, headers={
                'Host': 'edu.tatar.ru',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-GPC': '1',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Referer': 'https://edu.tatar.ru/user/diary/week',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9'
            }, proxies=proxy)
        except requests.exceptions.ProxyError:
            return self.strings('host_error')

        day = re.findall(
            r'<td style=.vertical.*?>.*?<td style=.vertical.*?middle.*?>(.*?)</td>.*?<p>(.*?)</p>.*?</tr>', answ.text.replace('\n', ''))
        if len(day) < 5:
            await self.revoke_token()
            return await self.scrape_date(date)
        ans = ""
        for sub in day:
            hw = sub[1].strip()
            if hw == "":
                hw = self.strings('no_hw')
            subject = sub[0].strip()
            for from_, to_ in filters.items():
                subject = subject.replace(from_, to_)
            ans += ' <b>' + subject + '</b> - <i>' + hw + '</i>\n'

        return ans

    async def scrape_week(self):
        now = datetime.now()
        monday = now - timedelta(days=now.weekday(), hours=now.hour,
                                 minutes=now.minute, seconds=now.second)
        monday = time.mktime(monday.timetuple())

        week = ""
        weekdays = ['Понедельник', 'Вторник',
                    'Среда', 'Четверг', 'Пятница', 'Суббота']
        for i in range(6):
            week += f"📚 <b>{weekdays[i]}</b> 📚\n"
            week += await self.scrape_date(monday + 60 * 60 * 24 * i)

        return week

    async def scrape_term(self, args):
        try:
            answ = await utils.run_sync(requests.get, 'https://edu.tatar.ru/user/diary/term', cookies=self.sess, headers={
                'Host': 'edu.tatar.ru',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-GPC': '1',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Referer': 'https://edu.tatar.ru/user/diary/week',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9'
            }, proxies=proxy)
        except requests.exceptions.ProxyError:
            return self.strings('host_error')

        term = "<b>={ Табель успеваемости }=</b>\n"
        rows = re.findall(r'<tr>.*?<td>(.*?)</td>(.*?)</tr>',
                          answ.text.replace('\n', ''))
        cols = {}
        for row in rows[1:-1]:
            subject = row[0]
            processing = row[1][:row[1].find(
                '<!--')].replace('<td>', '').replace(' ', '')
            marks_temp = list(
                filter(lambda a: a != '', processing.split('</td>')))
            marks_tmp = ' '.join(marks_temp[:-1])
            marks_db = self.db.get('eduTatar', 'marks', {})
            if '-n' in args:
                marks = str(marks_tmp.count('5')) + ' | ' + str(marks_tmp.count('4')) + \
                    ' | ' + str(marks_tmp.count('3')) + ' | ' + \
                    str(marks_tmp.count('2')) + " |"
            else:
                marks = marks_tmp

            marks_db[subject] = marks_tmp.split()
            self.db.set('eduTatar', 'marks', marks_db)

            marks += " <b>=" + \
                marks_temp[-1] + ' | ' + \
                str(round(float(marks_temp[-1]) + 0.001)) + '</b>'
            marks = marks.replace('\t', '')
            marks = re.sub(r'[ ]{2,}', '', marks)
            for from_, to_ in filters.items():
                subject = subject.replace(from_, to_)
            cols[subject] = marks

        try:
            maxelem = max(
                list(map(len, list(map(lambda a: a.split(' ')[1], list(cols.keys()))))))
            maxelem_val = max(
                list(map(len, list(map(lambda a: a.split('<b>', 1)[0], list(cols.values()))))))
        except ValueError:
            time.sleep(5)
            return await self.scrape_term(args)
        # print(maxelem)
        offset = " " * (maxelem - 7)
        if '-n' in args:
            term += f'<code>  Subject{offset}   5 | 4 | 3 | 2 | Result</code>\n<code>' + ('=' * (maxelem - 7 + 33)) + '</code>\n'
        else:
            term += "\n"

        for sub, marks in cols.items():
            offset = ' ' * (maxelem - len(sub.split(' ')[1]))
            offset_val = ' ' * (maxelem_val - len(marks.split('<b>', 1)[0]))
            term += f'<code>{sub}:{offset} {marks.split("<b>", 1)[0]}{offset_val}</code><b>{marks.split("<b>", 1)[1]}\n'

        return term
