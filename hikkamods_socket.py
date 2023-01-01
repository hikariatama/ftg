#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

__version__ = (2, 0, 1)

# scope: hikka_min 1.2.10

# meta developer: @hikarimods
# requires: rsa base64

import asyncio
import base64
import logging
import random
import re
from typing import Optional

import rsa
from telethon.tl.types import Message

from .. import loader, main, translations, utils

logger = logging.getLogger(__name__)

pubkey = rsa.PublicKey(
    7110455561671499155469672749235101198284219627796886527432331759773809536504953770286294224729310191037878347906574131955439231159825047868272932664151403,
    65537,
)

REGEXES = [
    re.compile(
        r"https:\/\/github\.com\/([^\/]+?)\/([^\/]+?)\/raw\/(?:main|master)\/([^\/]+\.py)"
    ),
    re.compile(
        r"https:\/\/raw\.githubusercontent\.com\/([^\/]+?)\/([^\/]+?)\/(?:main|master)\/([^\/]+\.py)"
    ),
]


@loader.tds
class HikkaModsSocketMod(loader.Module):
    """Gives @hikkamods_bot a right to download modules from official modules aggregator and autoupdate them
    """

    strings = {"name": "HikkaModsSocket"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "autoupdate",
                False,
                "Do you want to autoupdate modules? (Join @heta_updates in order for"
                " this option to take effect) ⚠️ Use at your own risk!",
                validator=loader.validators.Boolean(),
            )
        )

    async def client_ready(self, *_):
        if self.config["autoupdate"] and hasattr(self, "request_join"):
            await self.request_join(
                "@heta_updates",
                "This channel is the source of update notifications",
            )

        if self.get("nomute"):
            return

        await utils.dnd(self._client, "@hikkamods_bot", archive=False)
        self.set("nomute", True)

    @loader.loop(interval=60 * 60 * 6, autostart=True, wait_before=True)
    async def stats_collector(self):
        if not self._db.get(main.__name__, "stats", True):
            raise loader.StopLoop

        logger.debug("Sending additional stats")
        for module in [
            mod.__origin__
            for mod in self.allmodules.modules
            if utils.check_url(mod.__origin__)
        ]:
            try:
                await self.lookup("loader")._send_stats(module)
            except Exception:
                logger.debug(f"Failed to send stats for {module}", exc_info=True)

    async def _load_module(self, url: str, message: Optional[Message] = None):
        loader_m = self.lookup("loader")

        await loader_m.download_and_install(url, None)

        if getattr(loader_m, "_fully_loaded", getattr(loader_m, "fully_loaded", False)):
            getattr(
                loader_m,
                "_update_modules_in_db",
                getattr(loader_m, "update_modules_in_db", lambda: None),
            )()

        if message:
            if any(link == url for link in loader_m.get("loaded_modules", {}).values()):
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_load {message.raw_text.splitlines()[2].strip()}",
                )
            else:
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_fload {message.raw_text.splitlines()[2].strip()}",
                )

    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return

        if message.sender_id == 5519484330 and message.raw_text.startswith("#install"):
            await message.delete()

            fileref = (
                message.raw_text.split("#install:")[1].strip().splitlines()[0].strip()
            )
            sig = base64.b64decode(message.raw_text.splitlines()[1].strip().encode())
            try:
                rsa.verify(
                    rsa.compute_hash(fileref.encode("utf-8"), "SHA-1"), sig, pubkey
                )
            except rsa.pkcs1.VerificationError:
                logger.error(f"Got message with non-verified signature ({fileref=})")
                return

            await self._load_module(f"https://heta.hikariatama.ru/{fileref}", message)
        elif message.sender_id == 5519484330 and message.raw_text.startswith(
            "#setlang"
        ):
            lang = message.raw_text.split()[1]
            self._db.set(translations.__name__, "lang", lang)
            await self.allmodules.reload_translations()
            await self._client.inline_query("@hikkamods_bot", "#confirm_setlang")
        elif (
            utils.get_chat_id(message) == 1688624566
            and "Heta url: " in message.raw_text
        ):
            url = message.raw_text.split("Heta url: ")[1].strip()
            heta_dev, heta_repo, heta_mod = (
                url.lower().split("hikariatama.ru/")[1].split("/")
            )

            if heta_dev == "hikariatama" and heta_repo == "ftg":
                urls = [f"https://mods.hikariatama.ru/{heta_mod}", url]
                if any(
                    getattr(module, "__origin__", None).lower().strip("/") in urls
                    for module in self.allmodules.modules
                ):
                    await self._load_module(urls[0])
                    await asyncio.sleep(random.randint(1, 10))
                    await self._client.inline_query(
                        "@hikkamods_bot",
                        f"#confirm_update_noheta {url.split('hikariatama.ru/')[1]}",
                    )
                    return

            if any(
                getattr(module, "__origin__", "").lower().strip("/")
                == url.lower().strip("/")
                for module in self.allmodules.modules
            ):
                await self._load_module(url)
                await asyncio.sleep(random.randint(1, 10))
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_update {url.split('hikariatama.ru/')[1]}",
                )
                return

            for module in self.allmodules.modules:
                link = getattr(module, "__origin__", "").lower().strip("/")
                for regex in REGEXES:
                    if regex.search(link):
                        dev, repo, mod = regex.search(link).groups()
                        if dev == heta_dev and repo == heta_repo and mod == heta_mod:
                            await self._load_module(link)
                            await asyncio.sleep(random.randint(1, 10))
                            await self._client.inline_query(
                                "@hikkamods_bot",
                                "#confirm_update_noheta"
                                f" {url.split('hikariatama.ru/')[1]}",
                            )
                            return
