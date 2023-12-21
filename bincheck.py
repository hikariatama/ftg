#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/bincheck_icon.png
# meta banner: https://mods.hikariatama.ru/badges/bincheck.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import json

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class BinCheckerMod(loader.Module):
    """Show bin info about card"""

    strings = {
        "name": "BinCheck",
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>To get bin info, you"
            " need to specify Bin of card (first 6 digits)</b>"
        ),
    }

    strings_ru = {
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>Для получения"
            " информации БИН укажи первые 6 цифр карты</b>"
        ),
        "_cmd_doc_bincheck": "[bin] - Получить информацию БИН",
        "_cls_doc": "Показать информацию БИН о банковской карте",
    }

    strings_de = {
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>Um die Bin-Info zu"
            " erhalten, musst du die Bin der Karte (erste 6 Ziffern) angeben</b>"
        ),
        "_cmd_doc_bincheck": "[bin] - Erhalte Bin-Info",
        "_cls_doc": "Zeigt Bin-Info über eine Bankkarte an",
    }

    strings_hi = {
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>बिन जानकारी प्राप्त"
            " करने के लिए, आपको कार्ड का बिन (पहले 6 अंक) निर्दिष्ट करना होगा</b>"
        ),
        "_cmd_doc_bincheck": "[bin] - बिन जानकारी प्राप्त करें",
        "_cls_doc": "बैंक कार्ड के बारे में बिन जानकारी दिखाएं",
    }

    strings_uz = {
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>Bin haqida ma'lumot"
            " olish uchun, siz karta bin (birinchi 6 raqam) belgilashingiz kerak</b>"
        ),
        "_cmd_doc_bincheck": "[bin] - Bin haqida ma'lumot olish",
        "_cls_doc": "Bank karta haqida bin ma'lumotini ko'rsatish",
    }

    strings_tr = {
        "args": (
            "<emoji document_id=5765086867154276106>💳</emoji> <b>Bin bilgisi almak"
            " için, kartın bin (ilk 6 rakam) belirtmeniz gerekir</b>"
        ),
        "_cmd_doc_bincheck": "[bin] - Bin bilgisi al",
        "_cls_doc": "Banka kartı hakkında bin bilgisi göster",
    }

    @loader.unrestricted
    async def bincheckcmd(self, message: Message):
        """[bin] - Get card Bin info"""
        args = utils.get_args_raw(message)
        try:
            args = int(args)
            if args < 100000 or args > 999999:
                raise Exception()
        except Exception:
            await utils.answer(message, self.strings("args"))
            return

        async def bincheck(cc):
            try:
                ans = json.loads(
                    (
                        await utils.run_sync(
                            requests.get, f"https://bin-checker.net/api/{str(cc)}"
                        )
                    ).text
                )

                return (
                    "<b><u>Bin: %s</u></b>\n<code>\n🏦 Bank: %s\n🌐 Payment system: %s"
                    " [%s]\n✳️ Level: %s\n⚛️ Country: %s </code>"
                    % (
                        cc,
                        ans["bank"]["name"],
                        ans["scheme"],
                        ans["type"],
                        ans["level"],
                        ans["country"]["name"],
                    )
                )
            except Exception:
                return "BIN data unavailable"

        await utils.answer(message, await bincheck(args))
