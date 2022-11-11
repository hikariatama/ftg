#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/porn_icon.png
# meta banner: https://mods.hikariatama.ru/badges/porn.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import io
import logging
import random
import string
import time
from typing import List
from urllib.parse import quote

import requests
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


class PornVideo:
    def __init__(
        self,
        title: str,
        keywords: str,
        views: int,
        rate: str,
        url: str,
        embed: str,
        default_thumb: dict,
        length_min: str,
        **_,
    ):
        """
        :param title: title of the video
        :param keywords: keywords of the video
        :param views: views of the video
        :param rate: rate of the video
        :param url: url of the video
        :param embed: embed of the video
        :param default_thumb: default thumbnail of the video
        :param length_min: length of the video
        """
        self.title = title
        self.keywords = list(
            map(
                lambda x: "".join(
                    [
                        i if i in string.ascii_letters + string.digits else "_"
                        for i in x.strip()
                    ]
                ),
                keywords.split(","),
            )
        )
        self.views = views
        if views > 1000:
            self.views = str(round(views / 1000, 1)) + "k"

        self.rate = float(rate)
        self.url = url
        self.embed = embed
        self.thumb = default_thumb["src"]
        self.info = (
            f"🔞 <b>{utils.escape_html(title)}</b>\n\n<b>💫 Rating: {rate}\n👀 Views:"
            f" {self.views}</b>\n<b>⌚️ Duration:"
            f" {length_min}</b>\n\n<i>#{' #'.join(self.keywords)}</i>"
        )
        self._headers = {
            "host": "www.eporner.com",
            "referer": self.embed,
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
                " like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            ),
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "cache-control": "no-cache",
        }

    def convert_hash(self, hash_: str) -> str:
        """
        Process hash
        :param hash_: hash to convert
        :return: converted hash
        """

        def dec_to_36(dec: int) -> str:
            """
            Dec to 36-numeric string
            :param dec: dec to convert
            :return: converted string
            """
            digits = string.digits + string.ascii_lowercase
            x = dec % len(digits)
            rest = dec // len(digits)
            return digits[x] if rest == 0 else dec_to_36(rest) + digits[x]

        return "".join([dec_to_36(int(x, 16)) for x in utils.chunks(hash_, 8)]).lower()

    async def _get_media_url(self) -> str:
        """
        Gets the media url of the video
        :return: url of the video
        """
        init = await utils.run_sync(requests.get, self.embed, headers=self._headers)

        qualities = ["360p", "480p", "720p"]

        res = (
            await utils.run_sync(
                requests.get,
                (
                    f"https://www.eporner.com/xhr/video/{self.embed.strip('/').split('/')[-1]}?"
                    + "&".join(
                        f"{k}={v}"
                        for k, v in {
                            "hash": self.convert_hash(
                                next(
                                    line.split("'")[1]
                                    for line in init.text.splitlines()
                                    if line.strip().startswith("EP.video.player.hash")
                                )
                            ),
                            "domain": "www.eporner.com",
                            "pixelRatio": 1.5,
                            "playerWidth": 0,
                            "playerHeight": 0,
                            "fallback": False,
                            "embed": True,
                            "supportedFormats": "hls,dash,mp4",
                            "_": str(round(time.time()))
                            + str(random.randint(100, 999)),
                        }.items()
                    )
                ),
                headers=self._headers,
                cookies=init.cookies,
                allow_redirects=True,
            )
        ).json()["sources"]["mp4"]

        return res[
            next(
                (quality for quality in qualities if quality in res),
                list(res.keys())[0],
            )
        ]["src"]


class PornManager:
    def __init__(self):
        ...

    def _from_json(self, json: dict) -> List[PornVideo]:
        """
        Convert API data from json to Python OOP objects
        :param json: Json data from API
        :return: List of obj:`PornVideo`
        """

        return [PornVideo(**item) for item in json]

    async def search(self, query: str, gay: bool) -> List[PornVideo]:
        """
        Search for porn videos
        :param query: Search query
        :param gay: Are you searching for gay content
        :return: List of obj:`PornVideo`
        """

        return self._from_json(
            (
                await utils.run_sync(
                    requests.get,
                    f"https://www.eporner.com/api/v2/video/search/?query={quote(query)}&per_page=30&page=1&thumbsize=big&order=top-weekly&gay={'2' if gay else '0'}&lq=0&format=json",
                )
            ).json()["videos"]
        )


@loader.tds
class PornMod(loader.Module):
    """Sends adult content directly to Telegram. Use with caution"""

    strings = {
        "name": "Porn",
        "args": "🚫 <b>Specify search query</b>",
        "404": "🚫 <b>No results found</b>",
        "downloading_porn": "🚍 <b>Downloading your porn...</b>",
        "page404": "🚫 Page doesn't exist",
        "back": "👈 Back",
        "next": "👉 Next",
        "download": "Download",
        "close": "🔻 Close",
    }

    strings_ru = {
        "args": "🚫 <b>Укажи поисковый запрос</b>",
        "404": "🚫 <b>Результатов не найдено</b>",
        "downloading_porn": "🚍 <b>Скачиваю твою порнушку...</b>",
        "page404": "🚫 Страница не существует",
        "back": "👈 Назад",
        "next": "👉 Далее",
        "download": "Скачать",
        "close": "🔻 Закрыть",
        "_cls_doc": (
            "Позволяет просматривать и скачивать контент для взрослых напрямую в"
            " Телеграм"
        ),
        "_cmd_doc_porn": (
            "<запрос> - Показать порнушку по запросу (будь осторожен в публичных чатах)"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "gay",
                False,
                "Are you gay?",
                validator=loader.validators.Boolean(),
            )
        )

    async def client_ready(self, *_):
        self.porn = PornManager()

    async def _download_video(self, call: InlineCall, video: PornVideo):
        await call.edit(
            self.strings("downloading_porn"),
            gif="https://c.tenor.com/TAIxD-ulneYAAAAC/anime-anime-background.gif",
        )

        vid = io.BytesIO(
            (await utils.run_sync(requests.get, await video._get_media_url())).content
        )
        vid.name = "video.mp4"

        await self._client.send_file(call.form["chat"], vid, caption=video.info)
        await call.delete()

    async def _display_video(
        self,
        call: InlineCall,
        results: list,
        index: int,
    ):
        if index not in range(len(results)):
            await call.answer(self.strings("page404"))
            return

        try:
            await call.edit(
                results[index].info,
                reply_markup=self._get_markup(results, index),
                photo=results[index].thumb,
            )
        except Exception:
            return await self._display_video(call, results, index)

    def _get_markup(self, results: list, index: int) -> dict:
        return [
            [
                *(
                    [
                        {
                            "text": self.strings("back"),
                            "callback": self._display_video,
                            "args": (results, index - 1),
                        }
                    ]
                    if index > 0
                    else []
                ),
                {
                    "text": (
                        f"{'🏳️‍🌈' if self.config['gay'] else '🔞'} {self.strings('download')}"
                    ),
                    "callback": self._download_video,
                    "args": (results[index],),
                },
                *(
                    [
                        {
                            "text": self.strings("next"),
                            "callback": self._display_video,
                            "args": (results, index + 1),
                        }
                    ]
                    if index + 1 < len(results)
                    else []
                ),
            ],
            [{"text": self.strings("close"), "action": "close"}],
        ]

    async def porncmd(self, message: Message):
        """<query> - Send adult content gallery (be aware using in public chats)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        results = await self.porn.search(args, self.config["gay"])

        if not results:
            await utils.answer(message, self.strings("404"))
            return

        await self.inline.form(
            message=message,
            text=results[0].info,
            reply_markup=self._get_markup(results, 0),
            photo=results[0].thumb,
        )
