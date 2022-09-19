# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-flat-vinzence-studio/344/external-erotic-erotic-stuff-flat-vinzence-studio-11.png
# meta banner: https://mods.hikariatama.ru/badges/xvideos.jpg
# meta developer: @hikarimods
# scope: hikka_min 1.2.11

import asyncio
from urllib.parse import quote_plus
from .. import loader, utils
from ..inline.types import InlineCall
from telethon.tl.types import Message
import logging
import requests
import re


logger = logging.getLogger(__name__)


class Video:
    def __init__(
        self,
        page_url: str,
        thumb_url: str,
        title: str,
        duration: str,
        views: str,
    ):
        self.page_url = page_url
        thumb_url = thumb_url.strip("/").split("/")
        num = next(i for i, item in enumerate(thumb_url) if item.startswith("thumbs"))
        dir_ = re.search(r"(\d+)", thumb_url[num])[1]
        thumb_url[num] = "videopreview"
        self.thumb_url = (
            "/".join(thumb_url[:-2])
            + "/"
            + thumb_url[-1].split(".")[0]
            + "_"
            + dir_
            + ".mp4"
        )
        self.title = title
        self.duration = duration
        self.views = views
        self.info = (
            f'🎬 <b><a href="{page_url}">{title}</a></b>\n\n🕔 <b>Duration:'
            f" </b><code>{duration}</code>\n👥 <b>Views:</b> <code>{views}</code>"
        )

    async def get_stream(self) -> str:
        return re.search(
            r'"contentUrl": "(https:\/\/.*?)",',
            (await utils.run_sync(requests.get, self.page_url)).text,
        )[1]

    def __str__(self):
        return f"<Adult Video: {self.title}>"

    def __repr__(self):
        return f"<Adult Video: {self.title}>"


class XVideos:
    async def fetch_thumbs(self, query: str, gay: bool = False) -> list:
        res = await utils.run_sync(
            requests.get,
            f"https://www.xvideos.com/switch-sexual-orientation/{'gay/gay' if gay else 'straight/straight'}",
            headers={"Referer": f"https://www.xvideos.com/?k={quote_plus(query)}"},
            allow_redirects=False,
        )

        if res.status_code == 302:
            res = await utils.run_sync(
                requests.get,
                "https://www.xvideos.com" + res.headers["Location"],
                cookies=res.cookies,
                headers={
                    "Referer": f"https://www.xvideos.com/?k={quote_plus(query)}",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        " (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
                    ),
                },
            )

        return [
            Video(f"https://www.xvideos.com{link[0]}", *link[1:])
            for link in re.findall(
                # Пиздец регулярка, да?
                r"thumb-inside.*?<a"
                r' href="(\/video[0-9]{5,}.*?)".*?data-src="(https:\/\/.*?)".*?title="(.*?)".*?class="duration">(.*?)<\/span>.*?<\/span>'
                r' ([^<]*?) <span class="[^"]+?">Views',
                res.text,
            )
        ]


@loader.tds
class XVideosMod(loader.Module):
    """Disclaimer: For adult auditory only (18+)"""

    strings = {
        "name": "XVideos",
        "xvid_no_query": "🚫 <b>No query specified</b>",
        "404": "🚫 <b>No results found</b>",
        "18+": (
            "🍓 <b>Please, confirm that you are over 18 years old. Simply standby.</b>"
        ),
        "18+_btn": "🔞 I am younger than 18 y.o",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "gay",
                False,
                "Use gay thread",
                validator=loader.validators.Boolean(),
            )
        )

    async def client_ready(self, *_):
        self.xvideos = XVideos()

    async def _display_video(
        self,
        call: InlineCall,
        results: list,
        index: int,
    ):
        if index not in range(len(results)):
            await call.answer("🚫 Page doesn't exist")
            return

        try:
            await call.edit(
                results[index].info,
                reply_markup=self._get_markup(results, index),
                video=results[index].thumb_url,
            )
        except Exception:
            return await self._display_video(call, results, index)

    def _get_markup(self, results: list, index: int) -> dict:
        return [
            [
                *(
                    [
                        {
                            "text": "👈 Back",
                            "callback": self._display_video,
                            "args": (results, index - 1),
                        }
                    ]
                    if index > 0
                    else []
                ),
                {
                    "text": f"{'🏳️‍🌈' if self.config['gay'] else '🔞'} Watch",
                    "url": results[index].page_url,
                },
                *(
                    [
                        {
                            "text": "👉 Next",
                            "callback": self._display_video,
                            "args": (results, index + 1),
                        }
                    ]
                    if index + 1 < len(results)
                    else []
                ),
            ],
            [{"text": "🔻 Close", "action": "close"}],
        ]

    async def xvidcmd(self, message: Message):
        """<query> - search for videos"""
        if not self.get("verified"):
            form = await self.inline.form(
                message=message,
                text=self.strings("18+"),
                reply_markup={
                    "text": self.strings("18+_btn"),
                    "action": "close",
                },
                gif="https://avatars.mds.yandex.net/get-zen_doc/3588827/pub_5efab624cdd4d637ce0fc4b3_5efab62a71854f76fa04878b/orig",
            )

            await asyncio.sleep(5)

            if not await form.edit(
                self.strings("18+") + "\n\n<i>🕔 Wait 5 more seconds</i>",
                reply_markup={
                    "text": self.strings("18+_btn"),
                    "action": "close",
                },
            ):
                return

            await asyncio.sleep(5)

            if not await form.edit(
                "🔞 <b>You can now access adult content</b>",
                gif="https://i.pinimg.com/originals/55/6d/04/556d04b83f7face17400c621f92f11dd.gif",
            ):
                return

            self.set("verified", True)
            await form.delete()

        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("xvid_no_query"))
            return

        videos = await self.xvideos.fetch_thumbs(query, self.config["gay"])

        if not videos:
            await utils.answer(message, self.strings("404"))
            return

        await self.inline.form(
            message=message,
            text=videos[0].info,
            reply_markup=self._get_markup(videos, 0),
            video=videos[0].thumb_url,
        )
