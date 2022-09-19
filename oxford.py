#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/oxford_icon.png
# meta banner: https://mods.hikariatama.ru/badges/oxford.jpg
# meta developer: @hikarimods
# requires: bs4
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.3.0

from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall

from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

import grapheme
import random

DEFAULT_HEADERS = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/92.0.4515.131 Safari/537.36"
    ),
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

    parts_of_speech = {
        "noun": "существительное",
        "pronoun": "местоимение",
        "verb": "глагол",
        "adjective": "прилагательное",
        "adverb": "наречие",
        "preposition": "предлог",
        "conjunction": "союз",
        "interjection": "междометие",
        "determiner": "определитель",
        "auxiliary verb": "вспомогательный глагол",
        "modal verb": "модальный глагол",
        "phrasal verb": "фразеологизм",
        "idiom": "идиома",
        "phrase": "фраза",
        "abbreviation": "аббревиатура",
        "article": "артикль",
        "collocation": "коллокация",
        "exclamation": "восклицание",
        "expression": "выражение",
    }

    strings = {
        "name": "Oxford",
        "no_exact": "😔 <b>There is no definition for </b><code>{}</code>\n<b>Maybe, you meant:</b>",
        "match": '{} <b><a href="{}">{}</a></b> [{}] <i>({})</i>\n\n{}',
        **{key: key for key in parts_of_speech},
    }

    strings_ru = {
        "_cls_doc": "Быстрый доступ к определениям слов в образовательном Оксфордском словаре",
        "no_exact": "😔 <b>Нет определения для </b><code>{}</code>\n<b>Возможно, вы имели в виду:</b>",
        **parts_of_speech,
    }

    async def _search(self, call: InlineCall, term: str):
        result = await search(term)
        await call.edit(self.format_match(result))

    def format_match(self, match: dict) -> str:
        return self.strings("match").format(
            random.choice(
                [
                    "<emoji document_id=5188448663982055338>{}</emoji>",
                    "<emoji document_id=5472411062412254753>{}</emoji>",
                    "<emoji document_id=5208541547489927655>{}</emoji>",
                    "<emoji document_id=5206186681346039457>{}</emoji>",
                    "<emoji document_id=5190925490017279861>{}</emoji>",
                    "<emoji document_id=5211151105194467156>{}</emoji>",
                    "<emoji document_id=5204128352629169390>{}</emoji>",
                    "<emoji document_id=5211062143536864914>{}</emoji>",
                ]
            ).format(
                random.choice(
                    list(
                        grapheme.graphemes(
                            "👩‍🎓🧑‍🎓👨‍🎓👨‍🏫🧑‍🏫👩‍🏫🤵‍♀️🤵🤵‍♂️💁‍♀️💁‍♂️🙋‍♂️🙋‍♀️🙍‍♀️🙎‍♂️"
                        )
                    )
                )
            ),
            f"https://www.oxfordlearnersdictionaries.com/search/english/direct/?q={match['term']}",
            utils.escape_html(match["term"]),
            utils.escape_html(match["pronunciation"]),
            utils.escape_html(self.strings(match["part_of_speech"])),
            "\n\n".join(
                [
                    "<emoji document_id=4974629970623071075>▫️</emoji><i>"
                    f" {utils.escape_html(definition)}</i>"
                    for definition in match["definitions"]
                ]
            ),
        )

    @loader.command(ru_doc="<слово> - Поиск слова в образовательном Оксфордском словаре")
    async def oxford(self, message: Message):
        """<term> - Search word in Oxford Learner's Dictionary"""
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
