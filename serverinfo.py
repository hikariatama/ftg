# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/server-shutdown.png
# meta developer: @hikariatama
# scope: hikka_only
# requires: psutil

import os
import platform
import sys

import psutil
from telethon.tl.types import Message

from .. import loader, utils


def b2mb(b):
    return round(b / 1024 / 1024, 1)


def find_lib(lib: str) -> str:
    try:
        if lib == "Telethon":
            lib = "Telethon | grep -v Telethon-Mod"
        ver = os.popen(f"python3 -m pip freeze | grep {lib}").read().split("==")[1]
        if "\n" in ver:
            return ver.split("\n")[0]
        return ver
    except Exception:
        return "Not Installed"


@loader.tds
class serverInfoMod(loader.Module):
    """Show server info"""

    strings = {
        "name": "ServerInfo",
        "loading": "<b>👾 Loading server info...</b>",
        "servinfo": "<b><u>👾 Server Info:</u>\n\n<u>🗄 Used resources:</u>\n    CPU: {} Cores {}%\n    RAM: {} / {}MB ({}%)\n\n<u>🧾 Dist info</u>\n    Kernel: {}\n    Arch: {}\n    OS: {}\n\n<u>📦 Python libs:</u>\n    Telethon: {}\n    Telethon-Mod: {}\n    Python-Git: {}\n    Python: {}\n    Pip: {}</b>",
    }

    strings_ru = {
        "loading": "<b>👾 Загрузка информации о сервере...</b>",
        "servinfo": "<b><u>👾 Информация о сервере:</u>\n\n<u>🗄 Задействованные ресурсы:</u>\n    CPU: {} ядер {}%\n    RAM: {} / {}MB ({}%)\n\n<u>🧾 Информация о ядре</u>\n    Kernel: {}\n    Arch: {}\n    OS: {}\n\n<u>📦 Библиотеки Python:</u>\n    Telethon: {}\n    Telethon-Mod: {}\n    Python-Git: {}\n    Python: {}\n    Pip: {}</b>",
        "_cmd_doc_serverinfo": "Показать информацию о сервере",
        "_cls_doc": "Показывает информацию о сервере",
    }

    async def serverinfocmd(self, message: Message):
        """Show server info"""
        message = await utils.answer(message, self.strings("loading"))

        inf = []

        try:
            inf.append(psutil.cpu_count(logical=True))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(psutil.cpu_percent())
        except Exception:
            inf.append("n/a")

        try:
            inf.append(
                b2mb(psutil.virtual_memory().total - psutil.virtual_memory().available)
            )
        except Exception:
            inf.append("n/a")

        try:
            inf.append(b2mb(psutil.virtual_memory().total))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(psutil.virtual_memory().percent)
        except Exception:
            inf.append("n/a")

        try:
            inf.append(utils.escape_html(platform.release()))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(utils.escape_html(platform.architecture()[0]))
        except Exception:
            inf.append("n/a")

        try:
            system = os.popen("cat /etc/*release").read()
            b = system.find('DISTRIB_DESCRIPTION="') + 21
            system = system[b : system.find('"', b)]
            inf.append(utils.escape_html(system))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(find_lib("Telethon"))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(find_lib("Telethon-Mod"))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(find_lib("python-git"))
        except Exception:
            inf.append("n/a")

        try:
            inf.append(
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
        except Exception:
            inf.append("n/a")

        try:
            inf.append(os.popen("python3 -m pip --version").read().split()[1])
        except Exception:
            inf.append("n/a")

        await utils.answer(message, self.strings("servinfo").format(*inf))
