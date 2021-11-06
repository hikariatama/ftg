"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Lawyer
#<3 pic: https://img.icons8.com/fluency/48/000000/tongue-out.png
#<3 desc: Получение информации с consultant.ru

from .. import loader, utils
import io
import json
import urllib.parse
import requests
import re

#requires: requests urllib

@loader.tds
class LawyerMod(loader.Module):
    """Получение информации с consultant.ru"""
    strings = {
        'name': 'Lawyer',
        'args': '🦊 <b>Incorrect args</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def lawcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args'))
            return

        main = requests.get('https://www.consultant.ru/search/?q=%D0%A3%D0%9A+%D0%A0%D0%A4+272', headers={
                'Host': 'www.consultant.ru', 
                'Connection': 'keep-alive', 
                'Pragma': 'no-cache', 
                'Cache-Control': 'no-cache', 
                'Upgrade-Insecure-Requests': '1', 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 
                'Sec-GPC': '1', 
                'Sec-Fetch-Site': 'same-origin', 
                'Sec-Fetch-Mode': 'navigate', 
                'Sec-Fetch-User': '?1', 
                'Sec-Fetch-Dest': 'document', 
                'Referer': 'https://www.consultant.ru/search/?q=272', 
                'Accept-Encoding': 'gzip, deflate, br', 
                'Accept-Language': 'en-US,en;q=0.9'
                }).cookies

        search = requests.get('https://www.consultant.ru/search/?q=' + urllib.parse.quote_plus(args), headers={
                'Host': 'www.consultant.ru', 
                'Connection': 'keep-alive', 
                'Accept': 'application/json, text/plain, */*', 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 
                'X-Requested-With': 'XMLHttpRequest', 
                'Sec-GPC': '1', 
                'Sec-Fetch-Site': 'same-origin', 
                'Sec-Fetch-Mode': 'cors', 
                'Sec-Fetch-Dest': 'empty', 
                'Referer': 'https://www.consultant.ru/search/?q=' + urllib.parse.quote_plus(args), 
                'Accept-Encoding': 'gzip, deflate, br', 
                'Accept-Language': 'en-US,en;q=0.9'
            }, cookies=main).json()

        logger.info(search)

        await utils.answer(message, re.sub(r'<.*?>', '', search['results']))
