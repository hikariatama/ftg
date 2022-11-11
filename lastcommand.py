#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/lastcommand_icon.png
# meta banner: https://mods.hikariatama.ru/badges/lastcommand.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

from telethon.tl.types import Message

from .. import loader


@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""

    strings = {"name": "LastCommand"}
    strings_ru = {
        "_cls_doc": "Выполняет последнюю команду",
        "_cmd_doc_lc": "Выполнить последнюю команду",
    }
    strings_de = {
        "_cls_doc": "Führt den letzten Befehl aus",
        "_cmd_doc_lc": "Letzten Befehl ausführen",
    }
    strings_tr = {
        "_cls_doc": "Son komutu çalıştırır",
        "_cmd_doc_lc": "Son komutu çalıştır",
    }
    strings_hi = {
        "_cls_doc": "अंतिम आदेश निष्पादित करें",
        "_cmd_doc_lc": "अंतिम आदेश निष्पादित करें",
    }
    strings_uz = {
        "_cls_doc": "Oxirgi buyruqni bajarish",
        "_cmd_doc_lc": "Oxirgi buyruqni bajarish",
    }

    async def client_ready(self):
        orig_dispatch = self.allmodules.dispatch

        def _disp_wrap(command: callable) -> tuple:
            txt, func = orig_dispatch(command)

            if "lc" not in txt:
                self.allmodules.last_command = func

            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message: Message):
        """Execute last command"""
        await self.allmodules.last_command(message)
