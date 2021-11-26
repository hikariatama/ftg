"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Wolfram
#<3 pic: https://img.icons8.com/fluency/48/000000/wolfram-alpha.png
#<3 desc: Быстрый поиск в wolframalpha.com

from .. import loader, utils
import requests
from urllib.parse import quote_plus
from pyppeteer import launch
import time
import os
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.getLogger('websockets.protocol').setLevel(logging.ERROR)

#requires: pyppeteer

async def webshot(url: str, width: int = 1200, height: int = 800, query: str = "") -> bytes:
    browser = await launch({'executablePath': '/snap/bin/chromium'})
    page = await browser.newPage()
    await page.setViewport({'width': width, 'height': height})
    await page.goto(url)
    await page.type('input', query)
    await page.click('button[type=submit]')
    path = f'/tmp/{str(time.time()).replace(".", "")}.png'
    await page.screenshot({'path': path})
    await browser.close()
    d = open(path, 'rb').read()
    os.remove(path)
    return d


@loader.tds
class WolframMod(loader.Module):
    strings = {
        "name": "Wolfram"
    }

    async def client_ready(self, client, db):
        self.client = client
        self.endpoints = [
            "WolfreeAlpha.on.fleek.co", 
            "WolfreeAlpha.netlify.app", 
            "WolfreeAlpha.vercel.app", 
            "WolfreeAlpha.gitlab.io", 
            "WolfreeAlpha.github.io", 
            "Wolfree.on.fleek.co", 
            "Wolfree.netlify.app", 
            "Wolfree.vercel.app", 
            "Wolfree.gitlab.io"
        ]

        self.link = "https://{}/input/?lang=en&i={}"

    async def wolframcmd(self, message):
        """<query> - Search in wolframalpha.com"""
        args = utils.get_args_raw(message)
        endpoint = self.endpoints[0]
        link = self.link.format(endpoint, '')
        await self.client.send_file(message.peer_id, await webshot(link, query=quote_plus(args)))
        await message.delete()
        
