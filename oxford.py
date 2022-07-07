# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-smashingstocks-circular-smashing-stocks/452/external-mortarboard-education-smashingstocks-circular-smashing-stocks.png
# scope: inline
# scope: hikka_only
# meta developer: @hikarimods
# requires: bs4

import asyncio
from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall

from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

import logging
import grapheme
import random

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer": "https://www.oxfordlearnersdictionaries.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
}


async def search(term: str) -> str:
    res = await utils.run_sync(
        requests.get,
        f"https://www.oxfordlearnersdictionaries.com/search/english/direct/?q={quote_plus(term)}",
        headers=DEFAULT_HEADERS,
    )

    soup = BeautifulSoup(res.text, "html.parser")

    if "spellcheck" in res.url:
        try:
            possible = [
                a.get("href").split("?q=")[1]
                for a in soup.find("ul", {"class": "result-list"}).find_all("a")
            ]
        except Exception:
            return {"ok": False, "possible": ["emptiness"]}

        return {"ok": False, "possible": possible}

    try:
        soup.find("div", {"class": "idioms"}).clear()
    except AttributeError:
        pass

    return {
        "ok": True,
        "definitions": [
            definition.get_text()
            for definition in soup.find_all("span", {"class": "def"})
        ],
        "part_of_speech": soup.find("span", {"class": "pos"}).get_text(),
        "pronunciation": soup.find("span", {"class": "phon"}).get_text(),
        "term": term,
    }


@loader.tds
class OxfordMod(loader.Module):
    """Quickly access word definitions in Oxford Learners dictionary"""

    strings = {
        "name": "Oxford",
        "no_exact": "😔 <b>There is no definition for {}</b>\n<b>Maybe, you meant:</b>",
        "match": '{} <b><a href="{}">{}</a></b> [{}] <i>({})</i>\n\n{}',
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:oxford")
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

        self.allmodules._hikari_stats += ["oxford"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def _search(self, call: InlineCall, term: str):
        result = await search(term)
        await call.edit(self.format_match(result))

    def format_match(self, match: dict) -> str:
        return self.strings("match").format(
            random.choice(
                list(
                    grapheme.graphemes(
                        "👩‍🎓🧑‍🎓👨‍🎓👨‍🏫🧑‍🏫👩‍🏫🤵‍♀️🤵🤵‍♂️💁‍♀️💁‍♂️🙋‍♂️🙋‍♀️🙍‍♀️🙎‍♂️"
                    )
                )
            ),
            f"https://www.oxfordlearnersdictionaries.com/search/english/direct/?q={match['term']}",
            utils.escape_html(match["term"]),
            utils.escape_html(match["pronunciation"]),
            utils.escape_html(match["part_of_speech"]),
            "\n\n".join(
                [
                    f"<i>{i + 1}. {utils.escape_html(definition)}</i>"
                    for i, definition in enumerate(match["definitions"])
                ]
            ),
        )

    async def oxfordcmd(self, message: Message):
        """<mean> - Search word in Oxford Learner's dictionary"""
        args = utils.get_args_raw(message)
        if not args:
            args = "emptiness"

        result = await search(args)
        if not result["ok"]:
            await self.inline.form(
                self.strings("no_exact").format(utils.escape_html(args)),
                message,
                reply_markup=utils.chunks(
                    [
                        {"text": term, "callback": self._search, "args": (term,)}
                        for term in result["possible"]
                    ],
                    2,
                ),
            )
            return

        await utils.answer(message, self.format_match(result))
