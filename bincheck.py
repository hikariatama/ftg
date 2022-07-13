#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/fluency/240/000000/sim-card-chip.png
# meta developer: @hikarimods

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
            "💳 <b>To get bin info, you need to specify Bin of card (first 6 digits)</b>"
        ),
    }

    strings_ru = {
        "args": "💳 <b>Для получения информации БИН укажи первые 6 цифр карты</b>",
        "_cmd_doc_bincheck": "[bin] - Получить информацию БИН",
        "_cls_doc": "Показать информацию БИН о банковской карте",
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
