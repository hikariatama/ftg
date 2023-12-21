__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/serverinfo_icon.png
# meta banner: https://mods.hikariatama.ru/badges/serverinfo.jpg
# meta developer: @hikarimods
# requires: psutil
# scope: hikka_only
# scope: hikka_min 1.2.10

import contextlib
import os
import platform
import sys

import psutil
from telethon.tl.types import Message

from .. import loader, utils


def bytes_to_megabytes(b: int) -> int:
    return round(b / 1024 / 1024, 1)


@loader.tds
class serverInfoMod(loader.Module):
    """Show server info"""

    strings = {
        "name": "ServerInfo",
        "loading": (
            "<emoji document_id=5271897426117009417>🚘</emoji> <b>Loading server"
            " info...</b>"
        ),
        "servinfo": (
            "<emoji document_id=5271897426117009417>🚘</emoji> <b>Server"
            " Info</b>:\n\n<emoji document_id=5172854840321114816>💻</emoji> <b>CPU:"
            " {cpu} Cores {cpu_load}%</b>\n<emoji"
            " document_id=5174693704799093859>💻</emoji> <b>RAM: {ram} /"
            " {ram_load_mb}MB"
            " ({ram_load}%)</b>\n\n<emoji document_id=5172474181664637769>💻</emoji>"
            " <b>Kernel: {kernel}</b>\n{arch_emoji} <b>Arch: {arch}</b>\n<emoji"
            " document_id=5172622400986022463>💻</emoji> <b>OS: {os}</b>\n\n<emoji"
            " document_id=5172839378438849164>💻</emoji> <b>Python: {python}</b>"
        ),
    }

    strings_ru = {
        "loading": (
            "<emoji document_id=5271897426117009417>🚘</emoji> <b>Загрузка информации о"
            " сервере...</b>"
        ),
        "servinfo": (
            "<emoji document_id=5271897426117009417>🚘</emoji> <b>Информация о сервере"
            "</b>:\n\n<emoji document_id=5172854840321114816>💻</emoji> <b>CPU:"
            " {cpu} ядер(-ро) {cpu_load}%</b>\n<emoji"
            " document_id=5174693704799093859>💻</emoji> <b>RAM: {ram} /"
            " {ram_load_mb}MB"
            " ({ram_load}%)</b>\n\n<emoji document_id=5172474181664637769>💻</emoji>"
            " <b>Kernel: {kernel}</b>\n{arch_emoji} <b>Arch: {arch}</b>\n<emoji"
            " document_id=5172622400986022463>💻</emoji> <b>OS: {os}</b>\n\n<emoji"
            " document_id=5172839378438849164>💻</emoji> <b>Python: {python}</b>"
        ),
        "_cls_doc": "Показывает информацию о сервере",
    }

    @loader.command(ru_doc="Показать информацию о сервере")
    async def serverinfo(self, message: Message):
        """Show server info"""
        message = await utils.answer(message, self.strings("loading"))

        inf = {
            "cpu": "n/a",
            "cpu_load": "n/a",
            "ram": "n/a",
            "ram_load_mb": "n/a",
            "ram_load": "n/a",
            "kernel": "n/a",
            "arch_emoji": "n/a",
            "arch": "n/a",
            "os": "n/a",
        }

        with contextlib.suppress(Exception):
            inf["cpu"] = psutil.cpu_count(logical=True)

        with contextlib.suppress(Exception):
            inf["cpu_load"] = psutil.cpu_percent()

        with contextlib.suppress(Exception):
            inf["ram"] = bytes_to_megabytes(
                psutil.virtual_memory().total - psutil.virtual_memory().available
            )

        with contextlib.suppress(Exception):
            inf["ram_load_mb"] = bytes_to_megabytes(psutil.virtual_memory().total)

        with contextlib.suppress(Exception):
            inf["ram_load"] = psutil.virtual_memory().percent

        with contextlib.suppress(Exception):
            inf["kernel"] = utils.escape_html(platform.release())

        with contextlib.suppress(Exception):
            inf["arch"] = utils.escape_html(platform.architecture()[0])

        inf["arch_emoji"] = (
            "<emoji document_id=5172881503478088537>💻</emoji>"
            if "64" in (inf.get("arch", "") or "")
            else "<emoji document_id=5174703196676817427>💻</emoji>"
        )

        with contextlib.suppress(Exception):
            system = os.popen("cat /etc/*release").read()
            b = system.find('DISTRIB_DESCRIPTION="') + 21
            system = system[b : system.find('"', b)]
            inf["os"] = utils.escape_html(system)

        with contextlib.suppress(Exception):
            inf["python"] = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )

        await utils.answer(message, self.strings("servinfo").format(**inf))
