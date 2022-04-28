# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/coin-wallet.png
# meta developer: @hikariatama

from .. import loader, utils
from yoomoney import Quickpay
from telethon.tl.types import Message

@loader.tds
class YooMoneyMod(loader.Module):
    """Send Yoomoney pay link"""

    strings = {
        "name": "Yoomoney",
        "payme": '<b>🦊 {}\n💳<a href="{}">Оплатить {} RUB 💳</a></b>',
        "args": "<b>🦊 Incorrect args</b>",
        "no_account": "<b>🦊 You need to configure module</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "account", "", lambda: "Yoomoney wallet (16 digits)"
        )

    @loader.unrestricted
    async def yoopaycmd(self, message: Message):
        """<sum> <title> ; <comment> - Send payment link
        E.g: .yoopay 100 For coffee ; Bro, buy me a coffe, here is the link"""
        if len(self.config["account"]) != 16:
            await utils.answer(message, self.strings("no_account", message))
            return

        args = utils.get_args_raw(message)
        try:
            amount, titlecomm = args.split(" ", 1)
            amount = int(amount)
            title, comment = titlecomm.split(";", 1)
            if amount < 2:
                await utils.answer(message, self.strings("args", message))
                return
        except Exception:
            await utils.answer(message, self.strings("args", message))
            return

        quickpay = Quickpay(
            receiver=self.config["account"],
            quickpay_form="shop",
            targets=title.strip(),
            paymentType="SB",
            sum=amount,
            label="Перевод физлицу",
        )
        await utils.answer(
            message,
            self.strings("payme", message).format(
                comment.strip(), quickpay.redirected_url, amount
            ),
        )
