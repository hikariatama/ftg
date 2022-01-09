"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

# <3 title: OSINT
# <3 pic: https://img.icons8.com/fluency/48/000000/bank-card-back-side.png
# <3 desc: Поиск информации о чем угодно в сети

from .. import loader, utils
from tld import get_tld
from netaddr import IPAddress, AddrFormatError
import logging
import re
import os
import requests
import bs4
import io
import imghdr

logger = logging.getLogger(__name__)

def sherlock(username, installed=False):
    if not os.path.isdir('sherlock'):
        if installed: return '🚫 Cannot install Sherlock'
        git = 'https://github.com/sherlock-project/sherlock.git'
        logger.info(os.popen(f'git clone {git}').read())
        logger.info(
            os.popen(
                'python3 -m pip install -r sherlock/requirements.txt'
            ).read()
        )


    output = os.popen(f'cd sherlock && python3 sherlock {username}').read().strip()
    res = ""
    for line in output.split('\n'):
        if line.startswith('[+]'):
            line = line.split(maxsplit=1)[1].split(': ')
            res += f"<a href=\"{line[1]}\">{line[0]}</a> | "

    if res.endswith(' | '): res = res[:-3]
    return res

async def vk_id_from_uname(args):
    return (await utils.run_sync(requests.get, f'https://api.vk.com/method/utils.resolveScreenName?access_token=e2e890f2e2e890f2e2e890f244e292c56fee2e8e2e890f2834217249e2ed7089f4f1069&screen_name={args}&v=5.131')).json()['response']['object_id']

@loader.tds
class OSINTMod(loader.Module):
    """OSINT инструмент"""
    strings = {
        'name': 'OSINT',
        'args': '🧠 <b>You need to provide output to check</b>'
    }

    async def InfoVkUser_bot(self, target):
        async with self.client.conversation('@InfoVkUser_bot') as conv:
            m = await conv.send_message(target)
            res = await conv.get_response()
            await m.delete()
            await conv.mark_read()
            if 'Проверьте набранный вами' in res.text:
                await res.delete()
                return 'Not found'
            
            if 'скрыта настройками' in res.text:
                await res.delete()
                return 'Private'

            await res.click(1)
            await res.delete()
            res = await conv.get_response()
            await res.delete()
            res = res.text
            if len(res.split('\n')) > 5:
                res = '\n'.join(res.split('\n')[-5:])

            return res

    async def vk_interests(self, target):
        url = f"http://ininterests.com/user{target}"
        ans = ""
        res = await utils.run_sync(requests.get, url)
        res.encoding = res.apparent_encoding

        res = res.text

        if 'Пользователь с номером' in res and 'отсутствует' in res:
            return 'Not Found'

        # res = res[res.find('<h1>')-10:]

        soup = bs4.BeautifulSoup(res, "html.parser")

        r = [_.text for _ in soup.find_all('p')]
        r = r[r.index('Ярославская область')+1:r.index('Откуда взялась эта информация, Вы узнаете в разделе "Чему посвящен этот сайт?"')]
        ans = '\n'.join(r)

        return ans


    async def vk_profile_pics(self, target):
        url = f"https://bigbookname.com/user/id-{target}"
        res = await utils.run_sync(requests.get, url)
        res = res.text
        res = res[res.find('<div class="photos">') + 20:res.find('</div>', res.find('<div class="photos">') + 20)]
        photos = re.findall(r'http[s]?:\/\/.*?[.]jpg', res)
        return '\n'.join(list(set(photos)))


    async def client_ready(self, client, db):
        self.db = db
        self.client = client


    async def sherlockcmd(self, message):
        """OSINT search of username in 300+ services [sherlock]"""
        args = utils.get_args_raw(message)

        res = f"<b>🚬 Running sherlock on </b><code>{args}</code><b></b>\n"
        await utils.answer(message, res)
        res += "\n" + await utils.run_sync(sherlock, args)
        await utils.answer(message, res)


    async def vkcmd(self, message):
        """OSINT search of VK user"""
        args = utils.get_args_raw(message)
        async def answer(text):
            nonlocal message
            msg = await utils.answer(message, text)
            try:
                message = msg[0]
            except: message = msg

        base = '⏳ <b>OSINT in progress...</b>'
        res = f"Check result for {args}:\n"

        await answer(base + "\n<b>Processing 🫐 Source 1...</b>")

        vk_id = await vk_id_from_uname(args)
        ans = await self.InfoVkUser_bot(args)

        res += f"VK-ID: {vk_id}\n\n🫐 Source 1:\n{ans}\n-------------------\n"

        await answer(base + "\n<b>Processing 🍇 Source 2...</b>")
        interests = await self.vk_interests(vk_id)
        res += f"🍇 Source 2:\n{interests}\n-------------------\n"

        await answer(base + "\n<b>Processing 🍓 Source 3...</b>")
        photos = await self.vk_profile_pics(vk_id)
        res += f"🍓 Source 3:\n{photos}\n-------------------\n"


        report = io.BytesIO(res.encode('utf-8'))
        report.name = 'innomods-osint-report.txt'

        await message.delete()
        await self.client.send_message(message.peer_id, f"🐙 <b>OSINT report for </b><code>{args}</code>", file=report)


    async def vkphotoscmd(self, message):
        """OSINT search + download of VK user photos from leaked tracker"""
        args = utils.get_args_raw(message)
        await utils.answer(message, f'🌇 <b>Downloading avatars from </b><code>{args}</code>...')
        avas = (await self.vk_profile_pics(await vk_id_from_uname(args))).split()
        res = []

        for ava in avas:
            im = (await utils.run_sync(requests.get, ava)).content
            f = io.BytesIO(im)
            t = imghdr.what(f)
            if t in ['jpeg', 'png', 'gif']:
                f.name = f'img.{t.replace("jpeg", "jpg")}'
                res.append(f)

        await self.client.send_file(message.peer_id, res)
        await message.delete()

