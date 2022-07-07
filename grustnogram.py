# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://grustnogram.ru/favicon/ms-icon-144x144.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.12
# requires: Pillow requests_toolbelt

__version__ = (1, 0, 1)

import asyncio
import io
import json
import logging
import random
import string
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFont
from requests_toolbelt import MultipartEncoder
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

fnt = requests.get(
    "https://github.com/hikariatama/assets/raw/master/EversonMono.ttf"
).content

font = lambda size: ImageFont.truetype(  # noqa: E731
    io.BytesIO(fnt),
    size,
    encoding="UTF-8",
)


async def create_badge(data) -> bytes:
    SIZE = (1200, 300)
    INNER_MARGIN = (30, 30)

    thumb = Image.open(
        io.BytesIO((await utils.run_sync(requests.get, data["avatar"])).content)
    )

    im = Image.new("RGB", SIZE, (11, 11, 11))
    draw = ImageDraw.Draw(im)

    thumb_size = SIZE[1] - INNER_MARGIN[1] * 2

    thumb = thumb.resize((thumb_size, thumb_size))
    # thumb = add_corners(thumb, 10)

    im.paste(thumb, INNER_MARGIN)

    tpos = (
        INNER_MARGIN[0] + thumb_size + INNER_MARGIN[0] + 8,
        INNER_MARGIN[1],
    )

    draw.text(tpos, f'{data["name"]}', (255, 255, 255), font=font(64))
    link_pos = tpos[1] + 8 + font(64).getsize(data["name"])[1]
    draw.text(
        (tpos[0], link_pos),
        f'https://grustnogram.ru/u/{data["nickname"]}',
        (220, 220, 220),
        font=font(32),
    )

    offset = link_pos + 16 + font(32).getsize(data["nickname"])[1]
    for line in textwrap.wrap(
        data["about"], width=(SIZE[0] - tpos[0]) // font(32).getsize("a")[0]
    ):
        draw.text(
            (
                tpos[0],
                offset,
            ),
            line,
            (180, 180, 180),
            font=font(32),
        )
        offset += font(32).getsize(line)[1]

    offset += 16

    draw.text(
        (tpos[0], offset),
        f'Followers: {data["followers"]} / Follow: {data["follow"]}',
        (150, 150, 150),
        font=font(26),
    )

    img = io.BytesIO()
    im.save(img, format="PNG")
    return img.getvalue()


@loader.tds
class GrustnoGramMod(loader.Module):
    """Grustnogram.ru Telegram client"""

    strings = {
        "name": "GrustnoGram",
        "invalid_args": "🚫 <b>Invalid args. Pass email and password, separated by space</b>",
        "api_error": "🚫 <b>API error.</b>\n<pre>{}</pre>",
        "auth_successful": "🖤 <b>Auth successful as {}</b>",
        "no_photo": "🚫 <b>You need to reply to a photo</b>",
        "published": '🖤 <b><a href="https://grustnogram.ru/p/{}">Post</a> successfully published</b>',
        "delete": "🗑 Delete",
        "deleted": "🖤 <b>Post deleted</b>",
        "notif_follow": '🖤 <b><a href="https://grustnogram.ru/u/{0}">{0}</a> is now sad with you</b>',
        "notif_like": '🖤 <b><a href="https://grustnogram.ru/u/{0}">{0}</a> have broken heart from your <a href="https://grustnogram.ru/p/{1}">post</a></b>',
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:grustnogram")
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

        self.allmodules._hikari_stats += ["grustnogram"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

        if not self.get("email") or not self.get("password"):
            self.sadauthcmd = self.sadauthcmd_
        else:
            self._register()

        self._task = asyncio.ensure_future(self._poller())

    async def on_unload(self):
        if hasattr(self, "_task"):
            self._task.cancel()

    def _register(self):
        self.sadmecmd = self.sadmecmd_
        self.saduploadcmd = self.saduploadcmd_

    async def _login(self, email: str, password: str) -> dict:
        return (
            await utils.run_sync(
                requests.post,
                "https://api.grustnogram.ru/sessions",
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": "Hikka Userbot",
                },
                data=json.dumps({"email": email, "password": password}).encode(),
            )
        ).json()

    async def _get_self(self) -> dict:
        return (
            await utils.run_sync(
                requests.get,
                "https://api.grustnogram.ru/users/self",
                headers={
                    "accept": "application/json",
                    "user-agent": "Hikka Userbot",
                    "access-token": self.get("token", "undefined"),
                },
            )
        ).json()

    async def _publish(self, media: bytes, caption: str) -> dict:
        boundary = "----WebKitFormBoundary" + "".join(
            random.sample(string.ascii_letters + string.digits, 16)
        )

        m = MultipartEncoder(
            fields={"file": ("image.jpg", io.BytesIO(media), "image/jpg")},
            boundary=boundary,
        )

        res = (
            await utils.run_sync(
                requests.post,
                "https://media.grustnogram.ru/cors.php",
                headers={
                    "accept": "application/json, text/plain, */*",
                    "user-agent": "Hikka Userbot",
                    "access-token": self.get("token", "undefined"),
                    "content-type": m.content_type,
                },
                data=m,
            )
        ).json()

        if any(res["err_msg"]):
            raise RuntimeError(f"Can't upload image {json.dumps(res, indent=4)}")

        url = res["data"]

        return (
            await utils.run_sync(
                requests.post,
                "https://api.grustnogram.ru/posts",
                headers={
                    "accept": "application/json",
                    "user-agent": "Hikka Userbot",
                    "access-token": self.get("token", "undefined"),
                },
                data=json.dumps(
                    {"filter": 1, "text": caption, "media": [url]}
                ).encode(),
            )
        ).json()

    async def _delete(self, id_: int) -> dict:
        return (
            await utils.run_sync(
                requests.delete,
                f"https://api.grustnogram.ru/posts/{id_}",
                headers={
                    "accept": "application/json",
                    "user-agent": "Hikka Userbot",
                    "access-token": self.get("token", "undefined"),
                },
            )
        ).json()

    async def sadauthcmd_(self, message: Message):
        """<email> <password> - Auth on grustnogram.ru"""
        args = utils.get_args_raw(message)
        try:
            email, password = args.split(maxsplit=1)
        except Exception:
            await utils.answer(message, self.strings("invalid_args"))
            return

        result = await self._login(email, password)

        if any(result["err_msg"]):
            await self._api_error(message, result)
            return

        token = result["data"]["access_token"]

        self.set("email", email)
        self.set("password", password)
        self.set("token", token)

        await utils.answer(
            message,
            self.strings("auth_successful").format(
                (await self._get_self())["data"]["name"]
            ),
        )
        self._register()

    async def sadmecmd_(self, message: Message):
        """Get sad banner"""
        await message.delete()
        me = (await self._get_self())["data"]
        await self._client.send_file(
            message.peer_id,
            file=await create_badge(me),
            caption=f"https://grustnogram.ru/u/{me['nickname']}",
        )

    async def _api_error(self, message: Message, result: dict):
        await utils.answer(
            message,
            self.strings("api_error").format(
                json.dumps(
                    result,
                    indent=4,
                ),
            ),
        )

    async def inline_delete(self, call: InlineCall, id_: int):
        result = await self._delete(id_)
        if any(result["err_msg"]):
            await self._api_error(call, result)
            return

        await call.edit(self.strings("deleted"))
        await call.unload()

    async def _poller(self):
        try:
            while True:
                if not self.get("token"):
                    await asyncio.sleep(10)
                    continue

                res = (
                    await utils.run_sync(
                        requests.get,
                        "https://api.grustnogram.ru/status",
                        headers={
                            "accept": "application/json",
                            "user-agent": "Hikka Userbot",
                            "access-token": self.get("token", "undefined"),
                        },
                    )
                ).json()

                if not res["data"]["notifications_count"]:
                    await asyncio.sleep(30)
                    continue

                logger.debug(
                    f"Got {res['data']['notifications_count']} notification(-s) from GrustnoGram"
                )

                res = (
                    await utils.run_sync(
                        requests.get,
                        "https://api.grustnogram.ru/notifications",
                        headers={
                            "accept": "application/json",
                            "user-agent": "Hikka Userbot",
                            "access-token": self.get("token", "undefined"),
                        },
                    )
                ).json()

                if any(res["data"]):
                    for notification in res["data"]:
                        if int(notification["data"]["read"]):
                            continue

                        if notification["type"] == "follow":
                            await self.inline.bot.send_message(
                                self._tg_id,
                                self.strings("notif_follow").format(
                                    notification["data"]["nickname"]
                                ),
                                parse_mode="HTML",
                                disable_web_page_preview=True,
                            )
                        elif notification["type"] == "like":
                            await self.inline.bot.send_message(
                                self._tg_id,
                                self.strings("notif_like").format(
                                    notification["data"]["nickname"],
                                    notification["data"]["post_url"],
                                ),
                                parse_mode="HTML",
                                disable_web_page_preview=True,
                            )
                        else:
                            logger.warning(
                                f"Unknown notification type {json.dumps(notification, indent=4)}"
                            )

                await asyncio.sleep(10)
        except Exception:
            logger.exception("GrustnoGram poller got himself in trouble!")

    async def saduploadcmd_(self, message: Message):
        """Upload image to Grustnogram"""
        reply = await message.get_reply_message()
        if not reply or not reply.photo:
            await utils.answer(message, self.strings("no_photo"))
            return

        media = await self._client.download_file(reply.media, bytes)

        caption = getattr(reply, "raw_text", None) or ""
        result = await self._publish(media, caption)

        if any(result["err_msg"]):
            await self._api_error(message, result)
            return

        await self.inline.form(
            message=message,
            text=self.strings("published").format(result["data"]["url"]),
            reply_markup={
                "text": self.strings("delete"),
                "callback": self.inline_delete,
                "args": (result["data"]["id"],),
            },
        )
