"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: YooMoney
#<3 pic: https://img.icons8.com/fluency/48/000000/coin-wallet.png
#<3 desc: Отправить ссылку на оплату на твой ЮМани кошелек

from .. import loader, utils
import asyncio
import os
try:
    from yoomoney import Quickpay
except ImportError:
    os.popen('python3 -m pip install yoomoney').read()
    from yoomoney import Quickpay

class TikTokMod(loader.Module):
    """Отправить ссылку на оплату Yoomoney"""
    strings = {'name': 'Yoomoney', 
    'payme': "<b>🦊 {}\n💳<a href=\"{}\">Оплатить {} RUB 💳</a></b>", 
    'args': "<b>🦊 Неверные аргументы</b>", 
    'no_account': "<b>🦊 Тебе нужно указать счет ЮМани в конфиге модуля</b>"}


    def __init__(self):
        self.config = loader.ModuleConfig("account", '', lambda: "Счет Yoomoney (16 цифр)")

    @loader.unrestricted
    async def yoopaycmd(self, message):
        """<sum> <title>;<comment> - Отправить ссылку на оплату
Пример: .yoopay 100 На кофе;Братан, купи мне кофе, вот ссылка"""
        if len(self.config['account']) != 16:
            await utils.answer(message, self.strings('no_account', message))
            return

        args = utils.get_args_raw(message)
        try:
            amount, titlecomm = args.split(' ', 1)
            amount = int(amount)
            title, comment = titlecomm.split(';', 1)
            if amount < 2:
                await utils.answer(message, self.strings('args', message))
                return
        except:
            await utils.answer(message, self.strings('args', message))
            return

        quickpay = Quickpay(
            receiver=self.config['account'],
            quickpay_form="shop",
            targets=title,
            paymentType="SB",
            sum=amount,
            label="Перевод физлицу"
        )
        await utils.answer(message, self.strings('payme', message).format(comment, quickpay.redirected_url, amount))
