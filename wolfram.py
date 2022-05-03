# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/344/wolfram-alpha.png
# meta developer: @hikariatama
# scope: hikka_only
# requires: aiohttp urllib Pillow

from .. import loader, utils
from telethon.tl.types import Message

import logging
import random
import aiohttp
import json
from urllib.parse import quote_plus
from PIL import Image, ImageOps, ImageEnhance
import tempfile
import io
import requests
import os

logger = logging.getLogger(__name__)

appids = [
    "26LQEH-YT3P6T3YY9",
    "K49A6Y-4REWHGRWW6",
    "J77PG9-UY8A3WQ2PG",
    "P3WLYY-2G9GA6RQGE",
    "P7JH3K-27RHWR53JQ",
    "L349HV-29P5JV8Y7J",
    "77PP56-XLQK5GKUAA",
    "59EQ3X-HE26TY2W64",
    "8Q68TL-QA8W9GEXAA",
    "KQRKKJ-8WHPY395HA",
    "AAT4HU-Q3RETTGY93",
    "7JKH84-T648HW2UV9",
    "WYEQU3-2T55JP3WUG",
    "T2XT8W-57PJW3L433",
]


async def wolfram_compute(query: str) -> tuple:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "GET",
                "https://api.wolframalpha.com/v2/query?"
                "scantimeout=30&"
                "podtimeout=30&"
                "formattimeout=30&"
                "parsetimeout=30&"
                "totaltimeout=30&"
                "podstate=Show+all+steps&"
                "output=json&"
                f"input={quote_plus(query)}&"
                f"appid={random.choice(appids)}",
            ) as resp:
                answer = await resp.text()

                answer = json.loads(answer)

                result = f"<b>🔎 Query: </b><code>{utils.escape_html(query)}</code>\n"
                result += "<b>😼 Result:</b>\n"
                images = []

                for pod in answer["queryresult"]["pods"]:
                    if pod["title"] in {"Result", "Solution", "Exact result"}:
                        result += "\n".join(
                            [
                                f"<code>{utils.escape_html(subpod['plaintext'])}</code>\n"
                                if "plaintext" in subpod
                                else ""
                                for subpod in pod["subpods"]
                            ]
                        )

                for pod in reversed(answer["queryresult"]["pods"]):
                    if "subpods" in pod and pod["title"] != "Input":
                        images += [
                            subpod["img"]["src"]
                            for subpod in pod["subpods"]
                            if "img" in subpod and "src" in subpod["img"]
                        ]

                if not images:
                    try:
                        images = [
                            next(
                                subpod["img"]["src"]
                                for subpod in next(
                                    pod["subpods"]
                                    for pod in answer["queryresult"]["pods"]
                                    if pod["title"] == "Input"
                                )
                                if "img" in subpod and "src" in subpod["img"]
                            )
                        ]
                    except Exception:
                        pass

                if images:
                    files = []
                    for image in images:
                        with tempfile.TemporaryDirectory() as d:
                            ImageEnhance.Brightness(
                                ImageOps.invert(
                                    ImageOps.expand(
                                        Image.open(
                                            io.BytesIO(
                                                (
                                                    await utils.run_sync(requests.get, image)
                                                ).content
                                            )
                                        ),
                                        border=50,
                                        fill="white",
                                    ).convert("RGB")
                                )
                            ).enhance(1.2).save(os.path.join(d, "wolfram.png"))

                            with open(os.path.join(d, "wolfram.png"), "rb") as f:
                                files += [f.read()]

                    images = files

                return result, images or None
    except Exception:
        logger.exception("Wolfram query processing error")


@loader.tds
class WolframAlphaMod(loader.Module):
    """Solves hard math questions"""

    strings = {
        "name": "WolframAlpha",
        "computing": (
            "🧠 <b>I'm doing my best to solve this problem...</b>|"
            "🧠 <b>Meh, mafs again...</b>|"
            "🧠 <b>Oh no, it's very hard problem. I need some time to solve it...</b>|"
            "🧠 <b>I'm a math god and Im gonna help u...</b>|"
            "🧠 <b>ACTIVATING MATH GOD MODE</b>|"
            "🧠 <b>Beep-boop calculating</b>|"
            "🧠 <b>Can't solve this by urself? Meh, k, I'll help</b>"
        ),
        "hard": "🤯 <b>I don't know how to solve this problem</b>",
    }

    strings_ru = {
        "hard": "🤯 <b>Я не знаю, как решить эту задачу</b>",
        "_cmd_doc_wolfram": "Решить математическую задачу",
        "_cls_doc": "Решает математические задачи",
        "computing": (
            "🧠 <b>Делаю все, чтобы решить эту математическую задачу...</b>|"
            "🧠 <b>Блин, опять математика...</b>|"
            "🧠 <b>Ой, это очень сложная задача. Дай мне немного времени...</b>|"
            "🧠 <b>Я бог математики и я помогу тебе...</b>|"
            "🧠 <b>АКТИВИРУЮ РЕЖИМ БОГА МАТЕМАТИКИ</b>|"
            "🧠 <b>Бип-буп решаю</b>|"
            "🧠 <b>Не можешь решить сам? Мэх, ладно, помогу...</b>"
        ),
    }

    async def client_ready(self, client, db):
        self._client = client

    async def wolframcmd(self, message: Message):
        """Solve mathematic problem"""
        args = utils.get_args_raw(message)
        if not args:
            args = "x ^ 2 + y ^ 2 = 1"

        message = await utils.answer(
            message,
            random.choice(self.strings("computing").split("|")),
        )
        answer = await wolfram_compute(args)
        if not answer:
            await utils.answer(message, self.strings("hard"))
            return

        if not answer[1]:
            await utils.answer(message, answer[0])
        else:
            await message.delete()
            await self._client.send_message(message.peer_id, answer[0], file=answer[1])
