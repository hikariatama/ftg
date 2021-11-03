"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Carbon
#<3 pic: https://img.icons8.com/fluency/48/000000/code.png
#<3 desc: Делает красивые Code Сниппеты.

import os
from .. import loader, utils
import time

try:
    from pyppeteer import launch
except:
    os.popen('python3 -m pip install pyppeteer').read()
    from pyppeteer import launch


try:
    import urllib.parse
except:
    os.popen('python3 -m pip install urllib').read()
    import urllib.parse



def hex2rgb(h):
    h = h.lstrip('#')
    return ('rgb'+str(tuple(int(h[i:i+2], 16) for i in (0, 2, 4))))

def checkHex(s):
    for ch in s:
        if ((ch < '0' or ch > '9') and (ch < 'A' or ch > 'F')):  
            return False
    return True


def createURLString(code):
    base_url = "https://carbon.now.sh/"
    first = True
    base_url += "?code=" + urllib.parse.quote_plus(code)
    return base_url

async def open_carbonnowsh(url):
    browser = await launch(defaultViewPort=None,
                           handleSIGINT=False,
                           handleSIGTERM=False,
                           handleSIGHUP=False,
                           headless=True,
                           args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await page._client.send('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': '/tmp/'
    })
    await page.goto(url, timeout=20000)
    return browser, page


async def get_response(url, path):
    browser, page = await open_carbonnowsh(url)
    element = await page.querySelector("#export-container  .container-bg")
    img = await element.screenshot({'path': '/tmp/' + path})
    await browser.close()
    img = open('/tmp/' + path, 'rb').read()
    os.popen('rm /tmp/' + path)
    return img


@loader.tds
class CarbonMod(loader.Module):
    strings = {
        'name': 'Carbon', 
        'args': '🦊 <b>No args specified</b>',
        'loading': '🦊 <b>Loading...</b>'
    }
    async def carboncmd(self, message):
        """.carbon <code> - Сделать красивую фотку кода"""
        args = utils.get_args_raw(message)
        await utils.answer(message, self.strings('loading', message))
        # await utils.answer(message, createURLString(args))
        img = await get_response(createURLString(args), str(time.time()).replace('.', '') + '.png')
        await message.delete()
        await message.client.send_message(utils.get_chat_id(message), file=img)

