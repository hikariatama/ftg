#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/fluency/240/000000/spell-check.png
# meta banner: https://mods.hikariatama.ru/badges/speller.jpg
# meta developer: @hikarimods
# scope: hikka_only
# requires: requests cloudscraper requests_toolbelt aiohttp bs4 langid

import asyncio
import random
import re
import string
from typing import Union

import aiohttp
import cloudscraper
import langid
import requests
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
from telethon.tl.types import Message

from .. import loader, utils

URL = "https://services.gingersoftware.com/Ginger/correct/jsonSecured/GingerTheTextFull"  # noqa
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"


class GingerIt(object):
    def __init__(self):
        self.url = URL
        self.api_key = API_KEY
        self.api_version = "2.0"
        self.lang = "US"

    def parse(self, text, verify=True):
        session = cloudscraper.create_scraper()
        request = session.get(
            self.url,
            params={
                "lang": self.lang,
                "apiKey": self.api_key,
                "clientVersion": self.api_version,
                "text": text,
            },
            verify=verify,
        )
        data = request.json()
        return self._process_data(text, data)

    @staticmethod
    def _change_char(original_text, from_position, to_position, change_with):
        return "{}{}{}".format(
            original_text[:from_position], change_with, original_text[to_position + 1 :]
        )

    def _process_data(self, text, data):
        result = text
        corrections = []

        for suggestion in reversed(data["Corrections"]):
            start = suggestion["From"]
            end = suggestion["To"]

            if suggestion["Suggestions"]:
                suggest = suggestion["Suggestions"][0]
                result = self._change_char(result, start, end, suggest["Text"])

                corrections.append(
                    {
                        "start": start,
                        "text": text[start : end + 1],
                        "correct": suggest.get("Text", None),
                        "definition": suggest.get("Definition", None),
                    }
                )

        return {"text": text, "result": result, "corrections": corrections}


async def process(text: str) -> str:
    fields = {"mytext": text, "autofix": "1", "lang_var": "Russian"}

    boundary = "----WebKitFormBoundary" + "".join(
        random.sample(string.ascii_letters + string.digits, 16)
    )

    m = MultipartEncoder(fields=fields, boundary=boundary)

    a = requests.post(
        "https://www.russiancorrector.com",
        headers={
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.russiancorrector.com",
            "Content-Type": m.content_type,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
                " like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-GPC": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.russiancorrector.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        },
        data=m,
    ).text

    url = "https://www.russiancorrector.com" + re.search(
        r"var url = \'(.+?)\'", a
    ).group(1)

    res = "__wait__123"
    while res == "__wait__123":
        async with aiohttp.ClientSession() as session:
            async with session.request("GET", url) as resp:
                res = await resp.text()
                if res != "__wait__123":
                    break

        await asyncio.sleep(1)

    return res


def parse(text: str) -> Union[bool, str]:
    if "We could not find any errors in your text" in text:
        return False

    soup = BeautifulSoup(text, "html.parser")

    for misspell in soup.find_all("div", class_="misspelling"):
        try:
            misspell.replace_with(
                misspell.find("li", class_="replace-option").get_text() or ""
            )
        except Exception:
            misspell.replace_with("")

    return (
        re.sub(r" {2,}", " ", soup.get_text().strip().replace("\n", " "))
        .replace("Types and number of errors found: ", "")
        .replace(
            "Autocorrect: Check box to correct errors automatically, where possible.A"
            " list of all corrected errors will be shown on the results page. Submit",
            "",
        )
        .strip()
    )


@loader.tds
class SpellCheckMod(loader.Module):
    """Just a simple two-lang spell checker"""

    strings = {
        "name": "SpellCheck",
        "processing": (
            "👩‍🏫 <b>Let me take a look... Seems like this message is misspelled!</b>"
        ),
    }

    strings_ru = {
        "processing": "👩‍🏫 <b>Дай глянуть. Похоже, тут есть ошибки!</b>",
        "_cmd_doc_spell": "Проверить сообщение на грамотность",
        "_cls_doc": "Проверяет правописание",
    }

    async def spellcmd(self, message: Message):
        """Perform spell check on reply"""
        reply = await message.get_reply_message()
        if not reply or not getattr(reply, "raw_text", False):
            await message.delete()

        message = await utils.answer(message, self.strings("processing"))
        text = reply.text

        tt = langid.classify(text)[0]
        if tt == "en":
            spell_checker = GingerIt()
            result = spell_checker.parse(text)
            corrected_text = result["result"]
        elif tt == "ru":
            corrected_text = parse(await process(text))
        else:
            await message.delete()
            return

        if corrected_text == text or not corrected_text:
            await message.delete()

        await utils.answer(message, f"✍️ {corrected_text}")
