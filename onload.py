#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/onload_icon.png
# meta banner: https://mods.hikariatama.ru/badges/onload.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class OnloadExecutorMod(loader.Module):
    """Executes selected commands after every userbot restart"""

    strings = {"name": "OnloadExecutor"}

    async def client_ready(self, client, _):
        self.c, _ = await utils.asset_channel(
            client,
            "hikka-onload",
            (
                "All commands from this chat will be executed once Hikka is started, be"
                " careful!"
            ),
            archive=True,
            avatar="https://raw.githubusercontent.com/hikariatama/assets/master/hikka-onload.png",
            _folder="hikka",
        )

        async for message in client.iter_messages(self.c):
            if (getattr(message, "raw_text", "") or "").startswith(self.get_prefix()):
                try:
                    m = await client.send_message("me", message.raw_text)
                    await self.allmodules.commands[message.raw_text[1:].split()[0]](m)
                    logger.debug("Registered onload command")
                    await m.delete()
                except Exception:
                    logger.exception(
                        f"Exception while executing command {message.raw_text[:15]}..."
                    )
