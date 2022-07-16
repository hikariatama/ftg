# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/ios-filled/344/tidal.png
# meta developer: @hikarimods
# requires: tidalapi
# scope: hikka_min 1.2.10

import asyncio
from .. import loader, utils
from ..inline.types import InlineCall
from telethon.tl.types import Message
import logging
import tidalapi

logger = logging.getLogger(__name__)


@loader.tds
class TidalMod(loader.Module):
    """API wrapper over TIDAL Hi-Fi music streaming service"""

    strings = {
        "name": "Tidal",
        "args": "🚫 <b>Specify search query</b>",
        "404": "🚫 <b>No results found</b>",
        "oauth": "🔑 <b>Login to TIDAL</b>\n\n<i>This link will expire in 5 minutes</i>",
        "oauth_btn": "🔑 Login",
        "success": "✅ <b>Successfully logged in!</b>",
        "error": "🚫 <b>Error logging in</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Searching...</b>",
        "tidal_like_btn": "🖤 Like",
        "tidal_dislike_btn": "💔 Dislike",
        "auth_first": "🚫 <b>You need to login first</b>",
    }

    async def client_ready(self, client, db):
        self._faved = []

        self.tidal = tidalapi.Session()
        login_credentials = (
            self.get("session_id"),
            self.get("token_type"),
            self.get("access_token"),
            self.get("refresh_token"),
        )

        if all(login_credentials):
            try:
                await utils.run_sync(self.tidal.load_oauth_session, *login_credentials)
                assert await utils.run_sync(self.tidal.check_login)
            except Exception:
                logger.exception("Error loading OAuth session")

        if not self.get("muted"):
            try:
                await utils.dnd(client, "@hikka_musicdl_bot", archive=True)
                await utils.dnd(client, "@DirectLinkGenerator_Bot", archive=True)
            except Exception:
                pass

            self.set("muted", True)

        self._obtain_faved.start()
        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    @loader.loop(interval=60)
    async def _obtain_faved(self):
        if not await utils.run_sync(self.tidal.check_login):
            return

        self._faved = list(
            map(
                int,
                (
                    await utils.run_sync(
                        self.tidal.request,
                        "GET",
                        f"users/{self.tidal.user.id}/favorites/ids",
                    )
                ).json()["TRACK"],
            )
        )

    def _save_session_info(self):
        self.set("token_type", self.tidal.token_type)
        self.set("session_id", self.tidal.session_id)
        self.set("access_token", self.tidal.access_token)
        self.set("refresh_token", self.tidal.refresh_token)

    async def tlogincmd(self, message: Message):
        """Open OAuth window to login into TIDAL"""
        result, future = self.tidal.login_oauth()
        form = await self.inline.form(
            message=message,
            text=self.strings("oauth"),
            reply_markup={
                "text": self.strings("oauth_btn"),
                "url": f"https://{result.verification_uri_complete}",
            },
            gif="https://i.gifer.com/8Z2a.gif",
        )

        outer_loop = asyncio.get_event_loop()

        def callback(*args, **kwargs):
            nonlocal form, outer_loop
            if self.tidal.check_login():
                asyncio.ensure_future(
                    form.edit(
                        self.strings("success"),
                        gif="https://c.tenor.com/IrKex2lXvR8AAAAC/sparkly-eyes-joy.gif",
                    ),
                    loop=outer_loop,
                )
                self._save_session_info()
            else:
                asyncio.ensure_future(form.edit(self.strings("error")), loop=outer_loop)

        future.add_done_callback(callback)

    async def tidalcmd(self, message: Message):
        """<query> - Search TIDAL"""
        if not await utils.run_sync(self.tidal.check_login):
            await utils.answer(message, self.strings("auth_first"))
            return

        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("searching"))

        result = await utils.run_sync(self.tidal.search, "track", query, limit=1)
        if not result or not result.tracks:
            await utils.answer(message, self.strings("404"))
            return

        track = result.tracks[0]
        full_name = f"{track.artist.name} - {track.name}"

        meta = (
            await utils.run_sync(
                self.tidal.request,
                "GET",
                f"tracks/{track.id}",
            )
        ).json()

        tags = []

        if meta.get("explicit"):
            tags += ["#explicit🤬"]

        if meta.get("audioQuality"):
            tags += [f"#{meta['audioQuality']}🔈"]

        if isinstance(meta.get("audioModes"), list):
            for tag in meta["audioModes"]:
                tags += [f"#{tag}🎧"]

        if track.id in self._faved:
            tags += ["#favorite🖤"]

        if tags:
            tags = "\n\n" + "\n".join(
                ["  ".join(chunk) for chunk in utils.chunks(tags, 2)]
            )

        text = self.strings("search").format(utils.escape_html(full_name)) + tags

        message = await utils.answer(
            message, text + "\n\n<i>Downloading audio file...</i>"
        )
        url = await self.musicdl.dl(full_name)

        await self.inline.form(
            message=message,
            text=text,
            **(
                {
                    "audio": {
                        "url": url,
                        "title": track.name,
                        "performer": track.artist.name,
                    }
                }
                if url
                else {}
            ),
            silent=True,
            reply_markup=[
                [
                    {
                        "text": self.strings("tidal_btn"),
                        "url": f"https://listen.tidal.com/track/{track.id}",
                    },
                    *(
                        [
                            {
                                "text": self.strings("tidal_like_btn"),
                                "callback": self._like,
                                "args": (track, text),
                            }
                        ]
                        if track.id not in self._faved
                        else [
                            {
                                "text": self.strings("tidal_dislike_btn"),
                                "callback": self._dislike,
                                "args": (track, text),
                            }
                        ]
                    ),
                ],
            ],
        )

    async def _like(self, call: InlineCall, track: tidalapi.Track, text: str):
        try:
            await utils.run_sync(self.tidal.user.favorites.add_track, track.id)
        except Exception:
            logger.exception("Error liking track")
            await call.answer("🚫 Error!")
        else:
            await call.answer("💚 Liked!")
            await call.edit(
                text,
                reply_markup=[
                    [
                        {
                            "text": self.strings("tidal_btn"),
                            "url": f"https://listen.tidal.com/track/{track.id}",
                        },
                        {
                            "text": self.strings("tidal_dislike_btn"),
                            "callback": self._dislike,
                            "args": (track, text),
                        },
                    ],
                ],
            )

    async def _dislike(self, call: InlineCall, track: tidalapi.Track, text: str):
        try:
            await utils.run_sync(self.tidal.user.favorites.remove_track, track.id)
        except Exception:
            logger.exception("Error disliking track")
            await call.answer("🚫 Error!")
        else:
            await call.answer("💔 Disliked!")
            await call.edit(
                text,
                reply_markup=[
                    [
                        {
                            "text": self.strings("tidal_btn"),
                            "url": f"https://listen.tidal.com/track/{track.id}",
                        },
                        {
                            "text": self.strings("tidal_like_btn"),
                            "callback": self._like,
                            "args": (track, text),
                        },
                    ],
                ],
            )
