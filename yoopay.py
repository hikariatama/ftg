# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-photo3ideastudio-flat-photo3ideastudio/512/000000/external-payment-supermarket-photo3ideastudio-flat-photo3ideastudio.png
# meta developer: @hikariatama
# scope: hikka_only
# scope: hikka_min 1.1.14

from telethon.tl.types import Message
from yoomoney import Quickpay

from .. import loader, utils


@loader.tds
class YooMoneyMod(loader.Module):
    """Send Yoomoney pay link"""

    strings = {
        "name": "Yoomoney",
        "payme": '<b>🦊 {}\n💳<a href="{}">Pay {} RUB 💳</a></b>',
        "args": "<b>🚫 Incorrect args</b>",
        "no_account": "<b>🚫 You need to configure module</b>",
    }

    strings_ru = {
        "payme": '<b>🦊 {}\n💳<a href="{}">Оплатить {} RUB 💳</a></b>',
        "hikka.modules.yoopay.args": "<b>🚫 Неверные аргументы</b>",
        "hikka.modules.yoopay.no_account": "<b>🚫 Необходима конфигурация модуля</b>",
        "hikka.modules.yoopay._cmd_doc_yoopay": "<сумма> <заголовок> ; <комментарий> - Отправить ссылку на оплату\nПример: .yoopay 100 На кофе ; Бро, купи мне кофейку, вот ссылка",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("account", "", lambda: "Yoomoney wallet (16 digits)")
        )

    @loader.unrestricted
    async def yoopaycmd(self, message: Message):
        """<sum> <title> ; <comment> - Send payment link
        E.g: .yoopay 100 For coffee ; Bro, buy me a coffe, here is the link"""
        if len(str(self.config["account"])) != 16:
            await utils.answer(message, self.strings("no_account"))
            return

        args = utils.get_args_raw(message)
        try:
            amount, titlecomm = args.split(" ", 1)
            amount = int(amount)
            title, comment = titlecomm.split(";", 1)
            if amount < 2:
                await utils.answer(message, self.strings("args"))
                return
        except Exception:
            await utils.answer(message, self.strings("args"))
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
            self.strings("payme").format(
                comment.strip(),
                quickpay.redirected_url,
                amount,
            ),
        )
