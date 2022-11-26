__version__ = (2, 1, 1)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/playstation-buttons.png
# meta banner: https://mods.hikariatama.ru/badges/inline_spotify.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.5.3

import asyncio
import logging
import time
from math import ceil
from typing import Union

from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall, InlineMessage

logger = logging.getLogger(__name__)


def create_bar(pb):
    try:
        percentage = ceil(pb["progress_ms"] / pb["item"]["duration_ms"] * 100)
        bar_filled = ceil(percentage / 10)
        bar_empty = 10 - bar_filled
        bar = "".join("─" for _ in range(bar_filled))
        bar += "🞆"
        bar += "".join("─" for _ in range(bar_empty))

        bar += (
            f' {pb["progress_ms"] // 1000 // 60:02}:{pb["progress_ms"] // 1000 % 60:02} /'
        )
        bar += (
            f' {pb["item"]["duration_ms"] // 1000 // 60:02}:{pb["item"]["duration_ms"] // 1000 % 60:02}'
        )
    except Exception:
        bar = "──────🞆─── 0:00 / 0:00"

    return bar


@loader.tds
class InlineSpotifyMod(loader.Module):
    """EXTENSION for SpotifyNow mod, that allows you to send interactive player."""

    strings = {
        "name": "InlineSpotify",
        "input": "🎧 Enter the track name",
        "search": "🔎 Search",
        "listening_to": "I'm listening to",
        "download": "📥 Download",
    }

    strings_ru = {
        "input": "🎧 Введи название трека",
        "search": "🔎 Поиск",
        "_cmd_doc_splayer": (
            "Отправляет интерактивный плеер Spotify (активен в течение 5 минут!)"
        ),
        "_cls_doc": (
            "Дополнение для модуля SpotifyNow, позволяющее вызвать интерактивный плеер."
        ),
        "listening_to": "Сейчас я слушаю",
        "download": "📥 Скачать",
    }

    strings_it = {
        "input": "🎧 Inserisci il nome della traccia",
        "search": "🔎 Cerca",
        "_cmd_doc_splayer": (
            "Invia un player Spotify interattivo (attivo per 5 minuti!)"
        ),
        "_cls_doc": (
            "Estensione per il modulo SpotifyNow, che consente di inviare un player"
            " interattivo."
        ),
        "listening_to": "Sto ascoltando",
        "download": "📥 Scarica",
    }

    strings_es = {
        "input": "🎧 Introduzca el nombre de la pista",
        "search": "🔎 Buscar",
        "_cmd_doc_splayer": (
            "Envía un reproductor de Spotify interactivo (¡activo durante 5 minutos!)"
        ),
        "_cls_doc": (
            "Extensión para el módulo SpotifyNow, que permite enviar un reproductor"
            " interactivo."
        ),
        "listening_to": "Estoy escuchando",
        "download": "📥 Descargar",
    }

    strings_uz = {
        "input": "🎧 Ishora nomini kiriting",
        "search": "🔎 Qidirish",
        "_cmd_doc_splayer": (
            "Qo'llab-quvvatlash uchun Spotify interaktiv oynasini yuboring (5 daqiqada"
            " faol!)"
        ),
        "_cls_doc": (
            "SpotifyNow moduli uchun kengaytma, interaktiv oynani yuborish mumkin."
        ),
        "listening_to": "Meni eshitib turaman",
        "download": "📥 Yuklab oling",
    }

    strings_tr = {
        "input": "🎧 Parçanın adını girin",
        "search": "🔎 Ara",
        "_cmd_doc_splayer": (
            "Etkileşimli bir Spotify oynatıcı gönderir (5 dakika boyunca etkin!)"
        ),
        "_cls_doc": (
            "SpotifyNow modülü eklentisi, etkileşimli bir oynatıcı göndermenizi sağlar."
        ),
        "listening_to": "Şu anda dinliyorum",
        "download": "📥 İndir",
    }

    strings_kk = {
        "input": "🎧 Тақырып атауын енгізіңіз",
        "search": "🔎 іздеу",
        "_cmd_doc_splayer": (
            "Spotify интерактивті ойынды жіберіңіз (5 минутта белсенді!)"
        ),
        "_cls_doc": (
            "SpotifyNow модулі қосымшасы, интерактивті ойынды жіберуге мүмкіндік"
            " береді."
        ),
        "listening_to": "Ағымда маңызды болатындыңызды көрудіңіз керек",
        "download": "📥 Жүктеу",
    }

    strings_de = {
        "input": "🎧 Geben Sie den Namen des Tracks ein",
        "search": "🔎 Suche",
        "_cmd_doc_splayer": (
            "Sendet einen interaktiven Spotify-Player (aktiv für 5 Minuten!)"
        ),
        "_cls_doc": (
            "Erweiterung für das SpotifyNow-Modul, das es ermöglicht, einen"
            " interaktiven Player zu senden."
        ),
        "listening_to": "Ich höre zu",
        "download": "📥 Herunterladen",
    }

    async def _reload_sp(self, once: bool = False):
        while True:
            self.sp = getattr(self.lookup("SpotifyMod"), "sp", None)
            if once:
                break

            await asyncio.sleep(5)

    async def client_ready(self):
        self.sp = None

        self._tasks = [asyncio.ensure_future(self._reload_sp())]
        await self._reload_sp(True)

        self._active_forms = []

    async def on_unload(self):
        for task in self._tasks:
            task.cancel()

    async def inline_close(self, call: InlineCall):
        if any(
            call.form.get("uid") == getattr(i, "unit_id", None)
            for i in self._active_forms
        ):
            self._active_forms.remove(
                next(
                    i
                    for i in self._active_forms
                    if call.form.get("uid") == getattr(i, "unit_id", None)
                )
            )

        await call.delete()

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
                uid = getattr(call, "unit_id", call.form["id"])

            until = time.time() + 5 * 60
            while (
                any(uid == i.unit_id for i in self._active_forms)
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

                full_name = f"{', '.join(artists)} - {track}"

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
                            "text": self.strings("search"),
                            "input": self.strings("input"),
                            "handler": self.sp_play_track,
                        },
                        {
                            "text": self.strings("download"),
                            "callback": self._download,
                            "args": (full_name,),
                        },
                        {"text": "🔗 Link", "url": f"https://song.link/s/{track_id}"},
                    ],
                    [{"text": "🚫 Close", "callback": self.inline_close}],
                ]

                text = (
                    f"🎧 <b>{self.strings('listening_to')} {full_name}</b>\n<code>{create_bar(pb)}</code><a"
                    f" href='https://song.link/s/{track_id}'>\u206f</a>"
                )

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

    async def _download(self, call: InlineCall, track: str):
        await call.answer(self.strings("download"))
        await self.allmodules.commands["sfind"](
            await call.form["caller"].reply(
                f"<code>{self.get_prefix()}sfind {utils.escape_html(track)}</code>"
            )
        )

    @loader.command(
        ru_doc="Отправляет интерактивный плеер Spotify (активен в течение 5 минут!)",
        it_doc="Invia un player interattivo di Spotify (attivo per 5 minuti!)",
        de_doc="Sendet einen interaktiven Spotify-Player (aktiv für 5 Minuten!)",
        tr_doc="Etkin Spotify oynatıcı gönderir (5 dakika boyunca aktif!)",
        uz_doc="Faol Spotify oynatuvchisini yuboradi (5 daqiqada aktiv!)",
        es_doc=(
            "Envía un reproductor interactivo de Spotify (activo durante 5 minutos!)"
        ),
        kk_doc="Интерактивті Spotify ойындысын жібереді (5 минутта актив!)",
    )
    async def splayer(self, message: Message):
        """Send interactive Spotify player (active only for 5 minutes!)"""
        form = await self.inline.form(
            "<b>🐻 Bear with us, while player is loading...</b>", message=message
        )

        self._active_forms += [form]
        self._tasks += [asyncio.ensure_future(self.inline_iter(form))]
