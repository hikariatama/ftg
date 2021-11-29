"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

# <3 title: BinCheck
# <3 pic: https://img.icons8.com/fluency/48/000000/bank-card-back-side.png
# <3 desc: Информация Bin о карте

from .. import loader, utils
import requests
import json

@loader.tds
class BinCheckerMod(loader.Module):
    """Информация Bin о карте"""
    strings = {
        'name': 'BinCheck',
        'args': '💳 <b>To get bin info, you need to specify Bin of card (first 6 digits)</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def bincheckcmd(self, message):
        """Get card Bin info"""
        args = utils.get_args_raw(message)
        try:
            args = int(args)
            if args < 100000 or args > 999999:
                raise Exception()
        except: return await utils.answer(message, self.strings('args'))

        async def bincheck(cc):
            try:
                ans = json.loads((await utils.run_sync(requests.get, 'https://bin-checker.net/api/' + str(cc))).text)
                return "<b><u>Bin: %s</u></b>\n<code>\n🏦 Bank: %s\n🌐 Payment system: %s [%s]\n✳️ Level: %s\n⚛️ Country: %s </code>" % (cc, ans['bank']['name'], ans['scheme'], ans['type'], ans['level'], ans['country']['name'])
            except:
                return 'BIN data unavailable'

        return await utils.answer(message, await bincheck(args))


