__version__ = (1, 0, 1)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/plasticine/400/000000/spotify--v2.png
# meta banner: https://mods.hikariatama.ru/badges/spotify.jpg
# meta developer: @hikarimods
# requires: spotipy Pillow
# scope: hikka_only
# scope: hikka_min 1.2.10

import asyncio
import functools
import io
import logging
import re
import time
import traceback
from math import ceil
import contextlib
from types import FunctionType

import requests
import spotipy
from PIL import Image, ImageDraw, ImageFont
from telethon.tl.types import Message
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors.rpcerrorlist import FloodWaitError

from .. import loader, utils

logger = logging.getLogger(__name__)
logging.getLogger("spotipy").setLevel(logging.CRITICAL)


SIZE = (1200, 320)
INNER_MARGIN = (16, 16)

TRACK_FS = 48
ARTIST_FS = 32


@loader.tds
class SpotifyMod(loader.Module):
    """Display beautiful spotify now bar. Author: @fuccsoc. Rework: @hikariatama"""

    strings = {
        "name": "SpotifyNow",
        "need_auth": (
            "🚫 <b>Execute </b><code>.sauth</code><b> before using this action.</b>"
        ),
        "on-repeat": "🔂 <b>Set on-repeat.</b>",
        "off-repeat": "🔁 <b>Stopped track repeat.</b>",
        "skipped": "⏭ <b>Skipped track.</b>",
        "err": (
            "🚫 <b>Error occurred. Make sure the track is playing!</b>\n<code>{}</code>"
        ),
        "already_authed": "🚫 <b>You are already authentificated</b>",
        "authed": "🎧 <b>Auth successful</b>",
        "playing": "🎧 <b>Playing...</b>",
        "back": "🔙 <b>Switched to previous track</b>",
        "paused": "⏸ <b>Pause</b>",
        "deauth": "🚪 <b>Unauthentificated</b>",
        "restarted": "🔙 <b>Playing track from the beginning</b>",
        "auth": (
            '🔐 <a href="{}">Proceed here</a>, approve request, then <code>.scode'
            " https://...</code> with redirected url"
        ),
        "liked": "❤️ <b>Liked current playback</b>",
        "autobio": "🎧 <b>Spotify autobio {}</b>",
        "404": "🚫 <b>No results</b>",
        "playing_track": "🎹 <b>{} added to queue</b>",
        "no_music": "🚫 <b>No music is playing!</b>",
        "searching": "🔍 <b>Searching...</b>",
    }

    strings_ru = {
        "need_auth": (
            "🚫 <b>Выполни </b><code>.sauth</code><b> перед выполнением этого"
            " действия.</b>"
        ),
        "on-repeat": "🔂 <b>Повторение включено.</b>",
        "off-repeat": "🔁 <b>Повторение выключено.</b>",
        "skipped": "⏭ <b>Трек переключен.</b>",
        "err": (
            "🚫 <b>Произошла ошибка. Убедитесь, что музыка играет!</b>\n<code>{}</code>"
        ),
        "already_authed": "🚫 <b>Уже авторизован</b>",
        "authed": "🎧 <b>Успешная аутентификация</b>",
        "playing": "🎧 <b>Играю...</b>",
        "back": "🔙 <b>Переключил назад</b>",
        "paused": "⏸ <b>Пауза</b>",
        "deauth": "🚪 <b>Авторизация отменена</b>",
        "restarted": "🔙 <b>Начал трек сначала</b>",
        "liked": '❤️ <b>Поставил "Мне нравится" текущему треку</b>',
        "autobio": "🎧 <b>Обновление био включено {}</b>",
        "404": "🚫 <b>Нет результатов</b>",
        "playing_track": "🎹 <b>{} добавлен в очередь</b>",
        "no_music": "🚫 <b>Музыка не играет!</b>",
        "_cmd_doc_sfind": "Найти информацию о треке",
        "_cmd_doc_sauth": "Первый этап аутентификации",
        "_cmd_doc_scode": "Второй этап аутентификации",
        "_cmd_doc_unauth": "Отменить аутентификацию",
        "_cmd_doc_sbio": "Включить автоматическое био",
        "_cmd_doc_stokrefresh": "Принудительное обновление токена",
        "_cmd_doc_snow": "Показать карточку текущего трека",
        "_cls_doc": (
            "Тулкит для Spotify. Автор идеи: @fuccsoc. Реализация: @hikariatama"
        ),
    }

    def __init__(self):
        self._client_id = "e0708753ab60499c89ce263de9b4f57a"
        self._client_secret = "80c927166c664ee98a43a2c0e2981b4a"
        self.scope = (
            "user-read-playback-state playlist-read-private playlist-read-collaborative"
            " app-remote-control user-modify-playback-state user-library-modify"
            " user-library-read"
        )
        self.sp_auth = spotipy.oauth2.SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri="https://fuccsoc.com/",
            scope=self.scope,
        )
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "AutoBioTemplate",
                "🎧 {} ───○ 🔊 ᴴᴰ",
                lambda: "Template for Spotify AutoBio",
            )
        )

    def create_bar(self, current_playback: dict) -> str:
        try:
            percentage = ceil(
                current_playback["progress_ms"]
                / current_playback["item"]["duration_ms"]
                * 100
            )
            bar_filled = ceil(percentage / 10)
            bar_empty = 10 - bar_filled
            bar = "".join("─" for _ in range(bar_filled)) + "🞆"
            bar += "".join("─" for _ in range(bar_empty))

            bar += (
                f' {current_playback["progress_ms"] // 1000 // 60:02}:{current_playback["progress_ms"] // 1000 % 60:02} /'
            )
            bar += (
                f' {current_playback["item"]["duration_ms"] // 1000 // 60:02}:{current_playback["item"]["duration_ms"] // 1000 % 60:02}'
            )
        except Exception:
            bar = "──────🞆─── 0:00 / 0:00"

        return bar

    @staticmethod
    def create_vol(vol: int) -> str:
        volume = "─" * (vol * 4 // 100)
        volume += "○"
        volume += "─" * (4 - vol * 4 // 100)
        return volume

    async def create_badge(self, thumb_url: str, title: str, artist: str) -> bytes:
        thumb = Image.open(
            io.BytesIO((await utils.run_sync(requests.get, thumb_url)).content)
        )

        im = Image.new("RGB", SIZE, (30, 30, 30))
        draw = ImageDraw.Draw(im)

        thumb_size = SIZE[1] - INNER_MARGIN[1] * 2

        thumb = thumb.resize((thumb_size, thumb_size))

        im.paste(thumb, INNER_MARGIN)

        tpos = INNER_MARGIN
        tpos = (
            tpos[0] + thumb_size + INNER_MARGIN[0] + 8,
            thumb_size // 2 - (TRACK_FS + ARTIST_FS) // 2,
        )

        draw.text(tpos, title, (255, 255, 255), font=self.font)
        draw.text(
            (tpos[0], tpos[1] + TRACK_FS + 8),
            artist,
            (180, 180, 180),
            font=self.font_smaller,
        )

        img = io.BytesIO()
        im.save(img, format="PNG")
        return img.getvalue()

    @loader.loop(interval=90)
    async def autobio(self):
        try:
            current_playback = self.sp.current_playback()
            track = current_playback["item"]["name"]
            track = re.sub(r"([(].*?[)])", "", track).strip()
        except Exception:
            return

        bio = self.config["AutoBioTemplate"].format(f"{track}")

        try:
            await self._client(
                UpdateProfileRequest(about=bio[: 140 if self._premium else 70])
            )
        except FloodWaitError as e:
            logger.info(f"Sleeping {max(e.seconds, 60)} bc of floodwait")
            await asyncio.sleep(max(e.seconds, 60))
            return

    async def _dl_font(self):
        font = (
            await utils.run_sync(
                requests.get,
                "https://github.com/hikariatama/assets/raw/master/ARIALUNI.TTF",
            )
        ).content

        self.font_smaller = ImageFont.truetype(
            io.BytesIO(font), ARTIST_FS, encoding="UTF-8"
        )
        self.font = ImageFont.truetype(io.BytesIO(font), TRACK_FS, encoding="UTF-8")
        self.font_ready.set()

    async def client_ready(self, client, db):
        self.font_ready = asyncio.Event()
        asyncio.ensure_future(self._dl_font())

        self._premium = getattr(await client.get_me(), "premium", False)
        try:
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        except Exception:
            self.set("acs_tkn", None)
            self.sp = None

        if self.get("autobio", False):
            self.autobio.start()

        with contextlib.suppress(Exception):
            await utils.dnd(client, "@DirectLinkGenerator_Bot", archive=True)

        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    def tokenized(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if not args[0].get("acs_tkn", False) or not args[0].sp:
                await utils.answer(args[1], args[0].strings("need_auth"))
                return

            return await func(*args, **kwargs)

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def error_handler(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception(traceback.format_exc())
                with contextlib.suppress(Exception):
                    await utils.answer(
                        args[1],
                        args[0].strings("err").format(traceback.format_exc()),
                    )

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def autodelete(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            a = await func(*args, **kwargs)
            with contextlib.suppress(Exception):
                await asyncio.sleep(10)
                await args[1].delete()

            return a

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    @error_handler
    @tokenized
    @autodelete
    async def srepeatcmd(self, message: Message):
        """🔂"""
        self.sp.repeat("track")
        await utils.answer(message, self.strings("on-repeat"))

    @error_handler
    @tokenized
    @autodelete
    async def sderepeatcmd(self, message: Message):
        """🔁"""
        self.sp.repeat("context")
        await utils.answer(message, self.strings("off-repeat"))

    @error_handler
    @tokenized
    @autodelete
    async def snextcmd(self, message: Message):
        """⏭"""
        self.sp.next_track()
        await utils.answer(message, self.strings("skipped"))

    @error_handler
    @tokenized
    @autodelete
    async def spausecmd(self, message: Message):
        """⏸"""
        self.sp.pause_playback()
        await utils.answer(message, self.strings("paused"))

    @error_handler
    @tokenized
    @autodelete
    async def splaycmd(self, message: Message, from_sq: bool = False):
        """▶️"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not args:
            if not reply or "https://open.spotify.com/track/" not in reply.text:
                self.sp.start_playback()
                await utils.answer(message, self.strings("playing"))
                return
            else:
                args = re.search('https://open.spotify.com/track/(.+?)"', reply.text)[1]

        try:
            track = self.sp.track(args)
        except Exception:
            search = self.sp.search(q=args, type="track", limit=1)
            if not search:
                await utils.answer(message, self.strings("404"))
            try:
                track = search["tracks"]["items"][0]
            except Exception:
                await utils.answer(message, self.strings("404"))
                return

        self.sp.add_to_queue(track["id"])

        if not from_sq:
            self.sp.next_track()

        await message.delete()
        await self._client.send_file(
            message.peer_id,
            await self.create_badge(
                track["album"]["images"][0]["url"],
                track["name"],
                ", ".join([_["name"] for _ in track["artists"]]),
            ),
            caption=self.strings("playing_track").format(track["name"]),
        )

    @error_handler
    @tokenized
    @autodelete
    async def sfindcmd(self, message: Message):
        """Find info about track"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("404"))

        message = await utils.answer(message, self.strings("searching"))

        try:
            track = self.sp.track(args)
        except Exception:
            search = self.sp.search(q=args, type="track", limit=1)
            if not search:
                await utils.answer(message, self.strings("404"))
            try:
                track = search["tracks"]["items"][0]
                assert track
            except Exception:
                await utils.answer(message, self.strings("404"))
                return

        await self._open_track(track, message)

    async def _open_track(
        self,
        track: dict,
        message: Message,
        override_text: str = None,
    ):
        name = track.get("name")
        track_url = track.get("external_urls", {}).get("spotify", None)
        artists = [
            artist["name"] for artist in track.get("artists", []) if "name" in artist
        ]

        full_song_name = f"{name} - {', '.join(artists)}"

        url = await self.musicdl.dl(full_song_name)

        params = {
            "text": override_text
            or (
                (
                    f"🗽 <b>{utils.escape_html(full_song_name)}</b>"
                    if artists
                    else f"🗽 <b>{utils.escape_html(track)}</b>"
                )
                if track
                else ""
            ),
            "message": message,
            "reply_markup": {
                "text": "🎧 Listen on Spotify",
                "url": track_url,
            },
            "silent": True,
        }

        try:
            assert await self.inline.form(
                **params,
                audio=(
                    {
                        "url": url or track["preview_url"],
                        "title": name,
                        "performer": ", ".join(artists),
                    }
                    if url or track["preview_url"]
                    else {
                        "url": "https://siasky.net/RAALHGo4TQq8kJidWt5RXGsYs8_0r2tLREY_wvnAllGHSA",
                        "title": "Preview not available",
                        "performer": "",
                        "duration": 6,
                    }
                ),
            )
        except Exception:
            await self.inline.form(**params)

    @error_handler
    @tokenized
    async def sqcmd(self, message: Message):
        """🔎"""
        await self.splaycmd(message, True)

    @error_handler
    @tokenized
    @autodelete
    async def sbackcmd(self, message: Message):
        """⏮"""
        self.sp.previous_track()
        await utils.answer(message, self.strings("back"))

    @error_handler
    @tokenized
    @autodelete
    async def sbegincmd(self, message: Message):
        """⏪"""
        self.sp.seek_track(0)
        await utils.answer(message, self.strings("restarted"))

    @error_handler
    @tokenized
    @autodelete
    async def slikecmd(self, message: Message):
        """❤️"""
        cupl = self.sp.current_playback()
        self.sp.current_user_saved_tracks_add([cupl["item"]["id"]])
        await utils.answer(message, self.strings("liked"))

    @error_handler
    async def sauthcmd(self, message: Message):
        """First stage of auth"""
        if self.get("acs_tkn", False) and not self.sp:
            await utils.answer(message, self.strings("already_authed"))
        else:
            self.sp_auth.get_authorize_url()
            await utils.answer(
                message,
                self.strings("auth").format(self.sp_auth.get_authorize_url()),
            )

    @error_handler
    @autodelete
    async def scodecmd(self, message: Message):
        """Second stage of auth"""
        url = message.message.split(" ")[1]
        code = self.sp_auth.parse_auth_response_url(url)
        self.set("acs_tkn", self.sp_auth.get_access_token(code, True, False))
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    @autodelete
    async def unauthcmd(self, message: Message):
        """Deauth from Spotify API"""
        self.set("acs_tkn", None)
        del self.sp
        await utils.answer(message, self.strings("deauth"))

    @error_handler
    @tokenized
    @autodelete
    async def sbiocmd(self, message: Message):
        """Toggle bio playback streaming"""
        current = self.get("autobio", False)
        new = not current
        self.set("autobio", new)
        await utils.answer(
            message,
            self.strings("autobio").format("enabled" if new else "disabled"),
        )

        if new:
            self.autobio.start()
        else:
            self.autobio.stop()

    @error_handler
    @tokenized
    @autodelete
    async def stokrefreshcmd(self, message: Message):
        """Force refresh token"""
        self.set(
            "acs_tkn",
            self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
        )
        self.set("NextRefresh", time.time() + 45 * 60)
        self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        await utils.answer(message, self.strings("authed"))

    @error_handler
    async def snowcmd(self, message: Message):
        """Show current playback badge"""
        current_playback = self.sp.current_playback()

        try:
            device = (
                current_playback["device"]["name"]
                + " "
                + current_playback["device"]["type"].lower()
            )
        except Exception:
            device = None

        volume = current_playback.get("device", {}).get("volume_percent", 0)

        try:
            playlist_id = current_playback["context"]["uri"].split(":")[-1]
            playlist = self.sp.playlist(playlist_id)

            playlist_name = playlist.get("name", None)

            try:
                playlist_owner = (
                    f'<a href="https://open.spotify.com/user/{playlist["owner"]["id"]}">{playlist["owner"]["display_name"]}</a>'
                )
            except KeyError:
                playlist_owner = None
        except Exception:
            playlist_name = None
            playlist_owner = None

        try:
            track = current_playback["item"]["name"]
            track_id = current_playback["item"]["id"]
        except Exception:
            await utils.answer(message, self.strings("no_music"))
            return

        track_url = (
            current_playback.get("item", {})
            .get("external_urls", {})
            .get("spotify", None)
        )

        artists = [
            artist["name"]
            for artist in current_playback.get("item", {}).get("artists", [])
            if "name" in artist
        ]

        try:
            result = (
                (
                    f"🦉 <b>{utils.escape_html(track)} -"
                    f" {utils.escape_html(' '.join(artists))}</b>"
                    if artists
                    else f"🦉 <b>{utils.escape_html(track)}</b>"
                )
                if track
                else ""
            )
            icon = "🖥" if "computer" in str(device) else "🗣"
            result += f"\n{icon} <code>{device}</code>" if device else ""
            result += (
                "\n🎑 <b>Playlist</b>: <a"
                f' href="https://open.spotify.com/playlist/{playlist_id}">{playlist_name}</a>'
                if playlist_name and playlist_id
                else ""
            )
            result += f"\n🫂 <b>Owner</b>: {playlist_owner}" if playlist_owner else ""
            result += (
                f"\n\n<code>{self.create_bar(current_playback)}</code>"
                f" {self.create_vol(volume)} 🔊"
            )

        except Exception:
            result = self.strings("no_music")

        message = await utils.answer(
            message, result + "\n\n<i>Loading audio file...</i>"
        )
        await self._open_track(current_playback["item"], message, result)

    async def watcher(self, message: Message):
        """Watcher is used to update token"""
        if not self.sp:
            return

        if self.get("NextRefresh", False):
            ttc = self.get("NextRefresh", 0)
            crnt = time.time()
            if ttc < crnt:
                self.set(
                    "acs_tkn",
                    self.sp_auth.refresh_access_token(
                        self.get("acs_tkn")["refresh_token"]
                    ),
                )
                self.set("NextRefresh", time.time() + 45 * 60)
                self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])
        else:
            self.set(
                "acs_tkn",
                self.sp_auth.refresh_access_token(self.get("acs_tkn")["refresh_token"]),
            )
            self.set("NextRefresh", time.time() + 45 * 60)
            self.sp = spotipy.Spotify(auth=self.get("acs_tkn")["access_token"])

    async def on_unload(self):
        with contextlib.suppress(Exception):
            self.autobio.stop()
