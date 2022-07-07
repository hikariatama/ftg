#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/shuffle.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.0.29

import asyncio
import logging
from random import choice, randint

from .. import loader, utils
from ..inline.types import InlineQuery

logger = logging.getLogger(__name__)


@loader.tds
class InlineRandomMod(loader.Module):
    """Random tools for your userbot"""

    strings = {"name": "InlineRandom"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:inline_random")
        )

    async def stats_task(self):
        await asyncio.sleep(60)
        await self._client.inline_query(
            "@hikkamods_bot",
            f"#statload:{','.join(list(set(self.allmodules._hikari_stats)))}",
        )
        delattr(self.allmodules, "_hikari_stats")
        delattr(self.allmodules, "_hikari_stats_task")

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["inline_random"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    @loader.inline_everyone
    async def coin_inline_handler(self, query: InlineQuery) -> dict:
        """Heads or tails?"""

        r = "🦅 Heads" if randint(0, 1) else "🪙 Tails"

        return {
            "title": "Toss a coin",
            "description": "Trust in the God of luck, and he will be by your side!",
            "message": f"<i>The God of luck tells us...</i> <b>{r}</b>",
            "thumb": "https://img.icons8.com/external-justicon-flat-justicon/64/000000/external-coin-pirates-justicon-flat-justicon-1.png",
        }

    @loader.inline_everyone
    async def random_inline_handler(self, query: InlineQuery) -> dict:
        """[number] - Send random number less than specified"""

        if not query.args:
            return

        a = query.args

        if not str(a).isdigit():
            return

        return {
            "title": f"Toss random number less or equal to {a}",
            "description": "Trust in the God of luck, and he will be by your side!",
            "message": f"<i>The God of luck screams...</i> <b>{randint(1, int(a))}</b>",
            "thumb": "https://img.icons8.com/external-flaticons-flat-flat-icons/64/000000/external-numbers-auction-house-flaticons-flat-flat-icons.png",
        }

    @loader.inline_everyone
    async def choice_inline_handler(self, query: InlineQuery) -> dict:
        """[args, separated by comma] - Make a choice"""

        if not query.args or not query.args.count(","):
            return

        a = query.args

        return {
            "title": "Choose one item from list",
            "description": "Trust in the God of luck, and he will be by your side!",
            "message": f"<i>The God of luck whispers...</i> <b>{choice(a.split(',')).strip()}</b>",
            "thumb": "https://img.icons8.com/external-filled-outline-geotatah/64/000000/external-choice-customer-satisfaction-filled-outline-filled-outline-geotatah.png",
        }

    @loader.inline_everyone
    async def person_inline_handler(self, query: InlineQuery) -> dict:
        """This person doesn't exist"""

        return {
            "photo": f"https://thispersondoesnotexist.com/image?id={utils.rand(10)}",
            "title": "This person doesn't exist",
        }
