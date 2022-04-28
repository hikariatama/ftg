__version__ = (2, 0, 0)

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/cute-clipart/64/000000/playstation-buttons.png
# meta developer: @hikariatama
# scope: inline
# scope: hikka_only

from .. import loader
from telethon.tl.types import Message
from ..inline.types import InlineCall, InlineMessage
from typing import Union
import logging
import asyncio
import time
from math import ceil

logger = logging.getLogger(__name__)


def create_bar(pb):
    try:
        percentage = ceil(pb["progress_ms"] / pb["item"]["duration_ms"] * 100)
        bar_filled = ceil(percentage / 10)
        bar_empty = 10 - bar_filled
        bar = "".join("─" for _ in range(bar_filled))
        bar += "🞆"
        bar += "".join("─" for _ in range(bar_empty))

        bar += f' {pb["progress_ms"] // 1000 // 60:02}:{pb["progress_ms"] // 1000 % 60:02} /'
        bar += f' {pb["item"]["duration_ms"] // 1000 // 60:02}:{pb["item"]["duration_ms"] // 1000 % 60:02}'
    except Exception:
        bar = "──────🞆─── 0:00 / 0:00"

    return bar


@loader.tds
class InlineSpotifyMod(loader.Module):
    """EXTENSION for SpotifyNow mod, that allows you to send interactive player."""

    strings = {"name": "InlineSpotify"}

    async def _reload_sp(self, once=False):
        while True:
            for mod in self.allmodules.modules:
                if mod.strings("name") == "SpotifyNow":
                    self.sp = mod.sp
                    break

            if once:
                break

            await asyncio.sleep(5)

    async def client_ready(self, client, db):
        self.sp = None

        self._tasks = [asyncio.ensure_future(self._reload_sp())]
        await self._reload_sp(True)

        self._active_forms = []

    async def on_unload(self):
        for task in self._tasks:
            task.cancel()

    async def inline_close(self, call: InlineCall):
        if any(
            call.form["id"] == getattr(i, "unit_uid", None) for i in self._active_forms
        ):
            self._active_forms.remove(
                next(
                    i
                    for i in self._active_forms
                    if call.form["id"] == getattr(i, "unit_uid", None)
                )
            )

        await call.delete()

    @staticmethod
    async def _empty(self, *args, **kwargs):
        ...

    async def sp_previous(self, call: InlineCall):
        self.sp.previous_track()
        await self.inline_iter(call, True)

    async def sp_next(self, call: InlineCall):
        self.sp.next_track()
        await self.inline_iter(call, True)

    async def sp_pause(self, call: InlineCall):
        self.sp.pause_playback()
        await self.inline_iter(call, True)

    async def sp_play(self, call: InlineCall):
        self.sp.start_playback()
        await self.inline_iter(call, True)

    async def sp_shuffle(self, call: InlineCall, state: bool):
        self.sp.shuffle(state)
        await self.inline_iter(call, True)

    async def sp_repeat(self, call: InlineCall, state: bool):
        self.sp.repeat(state)
        await self.inline_iter(call, True)

    async def sp_play_track(self, call: InlineCall, query: str):
        try:
            track = self.sp.track(query)
        except Exception:
            search = self.sp.search(q=query, type="track", limit=1)
            try:
                track = search["tracks"]["items"][0]
            except Exception:
                return

        self.sp.add_to_queue(track["id"])
        self.sp.next_track()

    async def inline_iter(
        self,
        call: Union[InlineCall, InlineMessage],
        once: bool = False,
        uid: str = False,
    ):
        try:
            if not uid:
                uid = getattr(call, "unit_uid", call.form["id"])

            until = time.time() + 5 * 60
            while (
                any(uid == i.unit_uid for i in self._active_forms)
                and until > time.time()
                or once
            ):
                pb = self.sp.current_playback()
                is_resuming = (
                    "actions" in pb
                    and "disallows" in pb["actions"]
                    and "resuming" in pb["actions"]["disallows"]
                    and pb["actions"]["disallows"]["resuming"]
                )

                try:
                    artists = [artist["name"] for artist in pb["item"]["artists"]]
                except Exception:
                    artists = []

                try:
                    track = pb["item"]["name"]
                    track_id = pb["item"]["id"]
                except Exception:
                    track = ""
                    track_id = ""

                keyboard = [
                    [
                        {"text": "🔁", "callback": self.sp_repeat, "args": (False,)}
                        if pb["repeat_state"]
                        else {"text": "🔂", "callback": self.sp_repeat, "args": (True,)},
                        {"text": "⏮", "callback": self.sp_previous},
                        {"text": "⏸", "callback": self.sp_pause}
                        if is_resuming
                        else {"text": "▶️", "callback": self.sp_play},
                        {"text": "⏭", "callback": self.sp_next},
                        {"text": "↩️", "callback": self.sp_shuffle, "args": (False,)}
                        if pb["shuffle_state"]
                        else {
                            "text": "🔀",
                            "callback": self.sp_shuffle,
                            "args": (True,),
                        },
                    ],
                    [
                        {
                            "text": "🔎 Search",
                            "input": "🎧 Enter the name of track",
                            "handler": self.sp_play_track,
                        },
                        {"text": "🔗 Link", "url": f"https://song.link/s/{track_id}"},
                    ],
                    [{"text": "🚫 Close", "callback": self.inline_close}],
                ]

                text = f"🎧 <b>{', '.join(artists)} - {track}</b>\n<code>{create_bar(pb)}</code><a href='https://song.link/s/{track_id}'>\u206f</a>"

                await call.edit(
                    text,
                    reply_markup=keyboard,
                    disable_web_page_preview=False,
                )

                if once:
                    break

                await asyncio.sleep(10)
        except Exception:
            logger.exception("BRUH")

    async def splayercmd(self, message: Message):
        """Send interactive Spotify player (active only for 5 minutes!)"""
        form = await self.inline.form(
            "<b>🐻 Bear with us, while player is loading...</b>",
            message=message,
            reply_markup=[[{"text": "Loading", "callback": self._empty}]],
            ttl=10 * 60,
        )

        self._active_forms += [form]
        self._tasks += [asyncio.ensure_future(self.inline_iter(form))]
