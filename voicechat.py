__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/voicechat_icon.png
# meta banner: https://mods.hikariatama.ru/badges/voicechat.jpg
# meta developer: @hikarimods
# requires: py-tgcalls youtube_dl
# scope: hikka_only
# scope: hikka_min 1.2.10

import asyncio
import atexit
import contextlib
import os
import re
import tempfile
import logging
import shutil

from telethon.tl.types import Message, DocumentAttributeFilename
from telethon.tl.functions.phone import CreateGroupCallRequest

from pytgcalls import PyTgCalls, types, StreamType
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError
from pytgcalls.binding import Binding
from pytgcalls.environment import Environment
from pytgcalls.handlers import HandlersHolder
from pytgcalls.types import Cache
from pytgcalls.types.call_holder import CallHolder
from pytgcalls.types.update_solver import UpdateSolver
from pytgcalls.methods import Methods
from pytgcalls.scaffold import Scaffold
from pytgcalls.mtproto import MtProtoClient

from .. import loader, utils
from ..inline.types import InlineCall
from ..tl_cache import CustomTelegramClient

from youtube_dl import YoutubeDL

logging.getLogger("pytgcalls").setLevel(logging.ERROR)


@loader.tds
class VoiceChatMod(loader.Module):
    """Toolkit for VoiceChats handling"""

    strings = {
        "name": "VoiceChat",
        "already_joined": "🚫 <b>You are already in VoiceChat</b>",
        "joined": "🎙 <b>Joined VoiceChat</b>",
        "no_reply": "🚫 <b>Reply to a message</b>",
        "no_queue": "🚫 <b>No queue</b>",
        "queue": "🎙 <b>Queue</b>:\n\n{}",
        "queueadd": "🎧 <b>{} added to queue</b>",
        "queueaddv": "🎬 <b>{} added to queue</b>",
        "downloading": "📥 <b>Downloading...</b>",
        "playing": "🎶 <b>Playing {}</b>",
        "playing_with_next": "🎶 <b>Playing {}</b>\n➡️ <b>Next: {}</b>",
        "pause": "🎵 Pause",
        "play": "🎵 Play",
        "mute": "🔇 Mute",
        "unmute": "🔈 Unmute",
        "next": "➡️ Next",
        "stopped": "🚨 <b>Stopped</b>",
        "stop": "🚨 Stop",
        "choose_delete": "♻️ <b>Choose a queue item to delete</b>",
    }

    strings_ru = {
        "already_joined": "🚫 <b>Уже в голосовом чате</b>",
        "joined": "🎙 <b>Присоединился к голосовому чату</b>",
        "no_reply": "🚫 <b>Ответьте на сообщение</b>",
        "no_queue": "🚫 <b>Очередь пуста</b>",
        "queue": "🎙 <b>Очередь</b>:\n\n{}",
        "queueadd": "🎧 <b>{} добавлен в очередь</b>",
        "queueaddv": "📼 <b>{} добавлен в очередь</b>",
        "downloading": "📥 <b>Загрузка...</b>",
        "playing": "🎶 <b>Играет {}</b>",
        "playing_with_next": "🎶 <b>Играет {}</b>\n➡️ <b>Далее: {}</b>",
        "pause": "🎵 Пауза",
        "play": "🎵 Играть",
        "mute": "🔇 Заглушить",
        "unmute": "🔈 Включить",
        "next": "➡️ Далее",
        "stopped": "🚨 <b>Остановлено</b>",
        "stop": "🚨 Остановить",
        "choose_delete": "♻️ <b>Выберите элемент очереди для удаления</b>",
    }

    strings_de = {
        "already_joined": "🚫 <b>Du bist bereits in einem Sprachchat</b>",
        "joined": "🎙 <b>In Sprachchat beigetreten</b>",
        "no_reply": "🚫 <b>Antworte auf eine Nachricht</b>",
        "no_queue": "🚫 <b>Keine Warteschlange</b>",
        "queue": "🎙 <b>Warteschlange</b>:\n\n{}",
        "queueadd": "🎧 <b>{} zur Warteschlange hinzugefügt</b>",
        "queueaddv": "📼 <b>{} zur Warteschlange hinzugefügt</b>",
        "downloading": "📥 <b>Herunterladen...</b>",
        "playing": "🎶 <b>Spiele {}</b>",
        "playing_with_next": "🎶 <b>Spiele {}</b>\n➡️ <b>Nächster: {}</b>",
        "pause": "🎵 Pause",
        "play": "🎵 Spielen",
        "mute": "🔇 Stumm",
        "unmute": "🔈 Ton",
        "next": "➡️ Nächster",
        "stopped": "🚨 <b>Gestoppt</b>",
        "stop": "🚨 Stoppen",
        "choose_delete": "♻️ <b>Wähle einen Eintrag aus der Warteschlange zum Löschen</b>",
    }

    strings_tr = {
        "already_joined": "🚫 <b>Zaten sesli sohbette</b>",
        "joined": "🎙 <b>Sesli sohbete katıldı</b>",
        "no_reply": "🚫 <b>Bir mesaja yanıt verin</b>",
        "no_queue": "🚫 <b>Kuyruk yok</b>",
        "queue": "🎙 <b>Kuyruk</b>:\n\n{}",
        "queueadd": "🎧 <b>{} kuyruğa eklendi</b>",
        "queueaddv": "📼 <b>{} kuyruğa eklendi</b>",
        "downloading": "📥 <b>İndiriliyor...</b>",
        "playing": "🎶 <b>Oynatılıyor {}</b>",
        "playing_with_next": "🎶 <b>Oynatılıyor {}</b>\n➡️ <b>Sonraki: {}</b>",
        "pause": "🎵 Duraklat",
        "play": "🎵 Oynat",
        "mute": "🔇 Sessiz",
        "unmute": "🔈 Sesi aç",
        "next": "➡️ Sonraki",
        "stopped": "🚨 <b>Durduruldu</b>",
        "stop": "🚨 Durdur",
        "choose_delete": "♻️ <b>Silinecek kuyruk öğesini seçin</b>",
    }

    strings_uz = {
        "already_joined": "🚫 <b>Siz allaqachon g‘ovushda</b>",
        "joined": "🎙 <b>G‘ovushga qo‘shildi</b>",
        "no_reply": "🚫 <b>Xabarga javob bering</b>",
        "no_queue": "🚫 <b>Navbat yo‘q</b>",
        "queue": "🎙 <b>Navbat</b>:\n\n{}",
        "queueadd": "🎧 <b>{} navbatga qo‘shildi</b>",
        "queueaddv": "📼 <b>{} navbatga qo‘shildi</b>",
        "downloading": "📥 <b>Yuklanmoqda...</b>",
        "playing": "🎶 <b>O‘ynatilmoqda {}</b>",
        "playing_with_next": "🎶 <b>O‘ynatilmoqda {}</b>\n➡️ <b>Keyingi: {}</b>",
        "pause": "🎵 To‘xtatish",
        "play": "🎵 O‘ynatish",
        "mute": "🔇 Sessiz",
        "unmute": "🔈 Suv",
        "next": "➡️ Keyingi",
        "stopped": "🚨 <b>To‘xtatildi</b>",
        "stop": "🚨 To‘xtatish",
        "choose_delete": "♻️ <b>O‘chirish uchun navbatdagi elementni tanlang</b>",
    }

    strings_hi = {
        "already_joined": "🚫 <b>आप पहले से ही एक वाणिज्यिक चैट में हैं</b>",
        "joined": "🎙 <b>वाणिज्यिक चैट में शामिल हो गए</b>",
        "no_reply": "🚫 <b>एक संदेश पर उत्तर दें</b>",
        "no_queue": "🚫 <b>कोई पंक्ति नहीं</b>",
        "queue": "🎙 <b>पंक्ति</b>:\n\n{}",
        "queueadd": "🎧 <b>{} पंक्ति में जोड़ा गया</b>",
        "queueaddv": "📼 <b>{} पंक्ति में जोड़ा गया</b>",
        "downloading": "📥 <b>डाउनलोड हो रहा है...</b>",
        "playing": "🎶 <b>खेला जा रहा है {}</b>",
        "playing_with_next": "🎶 <b>खेला जा रहा है {}</b>\n➡️ <b>अगला: {}</b>",
        "pause": "🎵 रोकें",
        "play": "🎵 खेलो",
        "mute": "🔇 मौन",
        "unmute": "🔈 आवाज",
        "next": "➡️ अगला",
        "stopped": "🚨 <b>रोक दिया</b>",
        "stop": "🚨 रोकें",
        "choose_delete": "♻️ <b>हटाने के लिए पंक्ति आइटम का चयन करें</b>",
    }

    _calls = {}
    _muted = {}
    _forms = {}
    _queue = {}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "silent_queue",
                False,
                "Do not notify about track changes in chat",
                validator=loader.validators.Boolean(),
            )
        )

    async def client_ready(self, client, db):
        # Monkeypatch pytgcalls MtProtoClient to support hikka's custom one

        class HikkaTLClient(MtProtoClient):
            def __init__(
                self,
                cache_duration: int,
                client: CustomTelegramClient,
            ):
                self._bind_client = None
                from pytgcalls.mtproto.telethon_client import TelethonClient

                self._bind_client = TelethonClient(
                    cache_duration,
                    client,
                )

        class CustomPyTgCalls(PyTgCalls):
            def __init__(
                self,
                app: CustomTelegramClient,
                cache_duration: int = 120,
                overload_quiet_mode: bool = False,
                # BETA SUPPORT, BY DEFAULT IS DISABLED
                multi_thread: bool = False,
            ):
                Methods.__init__(self)
                Scaffold.__init__(self)
                self._app = HikkaTLClient(
                    cache_duration,
                    app,
                )
                self._is_running = False
                self._env_checker = Environment(
                    self._REQUIRED_NODEJS_VERSION,
                    self._REQUIRED_PYROGRAM_VERSION,
                    self._REQUIRED_TELETHON_VERSION,
                    self._app.client,
                )
                self._call_holder = CallHolder()
                self._cache_user_peer = Cache()
                self._wait_result = UpdateSolver()
                self._on_event_update = HandlersHolder()
                self._binding = Binding(
                    overload_quiet_mode,
                    multi_thread,
                )

                def cleanup():
                    if self._async_core is not None:
                        self._async_core.cancel()

                atexit.register(cleanup)

        # //

        self._app = CustomPyTgCalls(client)
        self._dir = tempfile.mkdtemp()
        await self._app.start()
        self._app._on_event_update.add_handler("STREAM_END_HANDLER", self.stream_ended)
        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    async def stream_ended(self, client: PyTgCalls, update: types.Update):
        chat_id = update.chat_id
        with contextlib.suppress(IndexError):
            self._queue[chat_id].pop(0)

        if not self._queue.get(chat_id):
            with contextlib.suppress(Exception):
                await client.leave_group_call(chat_id)
            return

        self._queue[chat_id][0]["playing"] = True

        if self._queue[chat_id][0]["audio"]:
            await self.play(chat_id, self._queue[chat_id][0]["data"])
        else:
            if self._queue[chat_id][0]["youtube"]:
                await self.play_video_yt(chat_id, self._queue[chat_id][0]["data"])
            else:
                await self.play_video(chat_id, self._queue[chat_id][0]["data"])

    async def _play(
        self,
        chat_id: int,
        stream,
        stream_type,
        reattempt: bool = False,
    ):
        self._muted.setdefault(chat_id, False)
        try:
            await self._app.join_group_call(
                chat_id,
                stream,
                stream_type=stream_type,
            )
        except AlreadyJoinedError:
            await self._app.change_stream(chat_id, stream)
        except NoActiveGroupCall:
            if reattempt:
                raise

            await self._client(CreateGroupCallRequest(chat_id))
            await self._play(chat_id, stream, stream_type, True)

    def _get_fn(self, message: Message) -> str:
        filename = None
        with contextlib.suppress(Exception):
            attr = next(
                attr for attr in getattr(message, "document", message).attributes
            )
            filename = (
                getattr(attr, "performer", "") + " - " + getattr(attr, "title", "")
            )

        if not filename:
            with contextlib.suppress(Exception):
                filename = next(
                    attr
                    for attr in getattr(message, "document", message).attributes
                    if isinstance(attr, DocumentAttributeFilename)
                ).file_name

        return filename

    @loader.command(
        ru_doc="<ответ на песню или ее имя> - Добавить песню в очередь прослушивания чата",
        de_doc="<auf eine Musik oder ihren Namen antworten> - Fügen Sie eine Musik in die Warteschlange für die Wiedergabe im Chat hinzu",
        tr_doc="<şarkıya veya adına yanıt> - Sohbette dinleme sırasına şarkı ekleyin",
        hi_doc="<एक गाने या उसके नाम पर उत्तर> - चैट में प्लेबैक के लिए गाने को लंबित करने के लिए गाने को लंबित करें",
        uz_doc="<musiqaga yoki uning nomiga javob> - Chatda o'qish uchun musiqani qo'shing",
    )
    async def qadd(self, message: Message):
        """<reply to song or its name> - Add song to chat's voicechat queue"""
        reply = await message.get_reply_message()
        song = utils.get_args_raw(message)
        if (not reply or not reply.media) and not song:
            await utils.answer(message, self.strings("no_reply"))
            return

        message = await utils.answer(message, self.strings("downloading"))
        filename = None

        if not reply or not reply.media and song:
            song, filename = await self._download_audio(song, message)
            if not song:
                await utils.answer(message, self.strings("no_reply"))
                return

        if song:
            raw_data = song
        else:
            raw_data = await self._client.download_file(reply.document, bytes)

            filename = self._get_fn(reply)

        if not filename:
            filename = "Some cool song"

        filename = re.sub(r"\(.*?\)", "", filename)

        chat_id = utils.get_chat_id(message)

        self._queue.setdefault(chat_id, []).append(
            {"data": raw_data, "filename": filename, "playing": False, "audio": True}
        )

        if not any(i["playing"] for i in self._queue[chat_id]):
            self._queue[chat_id][-1]["playing"] = True
            await self.play(chat_id, raw_data)

        await utils.answer(message, self.strings("queueadd").format(filename))

    @loader.command(
        ru_doc="<ответ на видео или ссылка на YouTube> - Добавить видео в очередь чата",
        de_doc="<auf ein Video oder einen YouTube-Link antworten> - Fügen Sie ein Video in die Warteschlange des Chats ein",
        tr_doc="<bir videoya veya YouTube bağlantısına yanıt> - Bir videoyu sohbet sırasına ekleyin",
        hi_doc="<एक वीडियो या YouTube लिंक पर उत्तर> - चैट की लंबित को एक वीडियो जोड़ें",
        uz_doc="<videoga yoki YouTube havolasiga javob> - Chatni qo'shish uchun video qo'shing",
    )
    async def qaddv(self, message: Message):
        """<reply to video or yt link> - Add video to chat's voicechat queue"""
        reply = await message.get_reply_message()
        link = utils.get_args_raw(message)
        if (not reply or not reply.media) and not link:
            await utils.answer(message, self.strings("no_reply"))
            return

        filename = None
        message = await utils.answer(message, self.strings("downloading"))
        if reply and reply.media:
            raw_data = await self._client.download_file(reply.document, bytes)

            filename = self._get_fn(reply)

        else:
            raw_data = link
            with contextlib.suppress(Exception):
                with YoutubeDL() as ydl:
                    filename = ydl.extract_info(link, download=False).get(
                        "title",
                        None,
                    )

        if not filename:
            filename = "Some cool video"

        filename = re.sub(r"\(.*?\)", "", filename)

        chat_id = utils.get_chat_id(message)

        self._queue.setdefault(chat_id, []).append(
            {
                "data": raw_data,
                "filename": filename,
                "playing": False,
                "audio": False,
                "youtube": not (reply and reply.media),
            }
        )

        if not any(i["playing"] for i in self._queue[chat_id]):
            self._queue[chat_id][-1]["playing"] = True
            if self._queue[chat_id][-1]["youtube"]:
                await self.play_video_yt(chat_id, raw_data)
            else:
                await self.play_video(chat_id, raw_data)

        await utils.answer(message, self.strings("queueadd").format(filename))

    @loader.command(
        ru_doc="Переключить трек",
        de_doc="Track wechseln",
        tr_doc="Parçayı değiştir",
        hi_doc="ट्रैक बदलें",
        uz_doc="Trackni o'zgartiring",
    )
    async def qnext(self, message: Message):
        """Skips current audio in queue"""
        chat_id = utils.get_chat_id(message)

        if len(self._queue.get(chat_id, [])) <= 1:
            await utils.answer(message, self.strings("no_queue"))
            return

        self._queue[chat_id].pop(0)
        self._queue[chat_id][0]["playing"] = True
        if self._queue[chat_id][0]["audio"]:
            await self.play(chat_id, self._queue[chat_id][0]["data"])
        else:
            if self._queue[chat_id][0]["youtube"]:
                await self.play_video_yt(chat_id, self._queue[chat_id][0]["data"])
            else:
                await self.play_video(chat_id, self._queue[chat_id][0]["data"])

        await message.delete()

    async def _download_audio(self, name: str, message: Message) -> bytes:
        result = await self.musicdl.dl(name, only_document=True)
        try:
            return await self._client.download_file(result, bytes), self._get_fn(result)
        except Exception:
            return None, None

    async def vcqcmd(self, message: Message):
        """Get current chat's queue"""
        chat_id = utils.get_chat_id(message)
        if not self._queue.get(chat_id):
            await utils.answer(message, self.strings("no_queue"))
            return

        await utils.answer(
            message,
            self.strings("queue").format(
                "\n".join(
                    [
                        ("🎧" if i["playing"] else "🕓")
                        + ("" if i["audio"] else "🎬")
                        + f" {i['filename']}"
                        for i in self._queue[chat_id]
                    ]
                )
            ),
        )

    async def qrmcmd(self, message: Message):
        """Remove song from queue"""
        if not self._queue.get(chat_id) or all(
            i["playing"] for i in self._queue[chat_id]
        ):
            await utils.answer(message, self.strings("no_queue"))
            return

        chat_id = utils.get_chat_id(message)
        await self.inline.form(
            message=message,
            text=self.strings("choose_delete"),
            reply_markup=utils.chunks(
                [
                    {
                        "text": ("🎧" if i["audio"] else "🎬") + i["filename"],
                        "callback": self._inline__delete,
                        "args": (chat_id, index),
                    }
                    for index, i in enumerate(self._queue[chat_id])
                    if not i["playing"]
                ],
                2,
            ),
        )

    async def _inline__delete(self, call: InlineCall, chat_id: int, index: int):
        del self._queue[chat_id][index]
        await call.answer("OK")
        await call.delete()

    async def _inline__pause(self, call: InlineCall, chat_id: int):
        await self._app.pause_stream(chat_id)
        msg, markup = self._get_inline_info(chat_id)
        await call.edit(msg, reply_markup=markup)

    async def _inline__play(self, call: InlineCall, chat_id: int):
        await self._app.resume_stream(chat_id)
        msg, markup = self._get_inline_info(chat_id)
        await call.edit(msg, reply_markup=markup)

    async def _inline__mute(self, call: InlineCall, chat_id: int):
        await self._app.mute_stream(chat_id)
        self._muted[chat_id] = True
        msg, markup = self._get_inline_info(chat_id)
        await call.edit(msg, reply_markup=markup)

    async def _inline__unmute(self, call: InlineCall, chat_id: int):
        await self._app.unmute_stream(chat_id)
        self._muted[chat_id] = False
        msg, markup = self._get_inline_info(chat_id)
        await call.edit(msg, reply_markup=markup)

    async def _inline__stop(self, call: InlineCall, chat_id: int):
        with contextlib.suppress(KeyError):
            del self._queue[chat_id]

        with contextlib.suppress(KeyError):
            del self._forms[chat_id]

        with contextlib.suppress(KeyError):
            del self._muted[chat_id]

        await self._app.leave_group_call(chat_id)
        await utils.answer(call, self.strings("stopped"))

    async def _inline__next(self, call: InlineCall, chat_id: int):
        self._queue[chat_id].pop(0)
        self._queue[chat_id][0]["playing"] = True
        if self._queue[chat_id][0]["audio"]:
            await self.play(chat_id, self._queue[chat_id][0]["data"])
        else:
            if self._queue[chat_id][0]["youtube"]:
                await self.play_video_yt(chat_id, self._queue[chat_id][0]["data"])
            else:
                await self.play_video(chat_id, self._queue[chat_id][0]["data"])

        msg, markup = self._get_inline_info(chat_id)
        await call.edit(msg, reply_markup=markup)

    def _get_inline_info(self, chat_id: int) -> tuple:
        if not self._queue.get(chat_id):
            return None, None

        if len(self._queue[chat_id]) == 1:
            msg = self.strings("playing").format(
                utils.escape_html(self._queue[chat_id][0]["filename"]),
            )
        else:
            msg = self.strings("playing_with_next").format(
                utils.escape_html(self._queue[chat_id][0]["filename"]),
                utils.escape_html(self._queue[chat_id][1]["filename"]),
            )

        try:
            is_playing = self._app.get_call(chat_id).status == "playing"
        except Exception:
            is_playing = True

        markup = [
            [
                {
                    "text": self.strings("stop"),
                    "callback": self._inline__stop,
                    "args": (chat_id,),
                },
            ],
            [
                *(
                    [
                        {
                            "text": self.strings("pause"),
                            "callback": self._inline__pause,
                            "args": (chat_id,),
                        }
                    ]
                    if is_playing
                    else [
                        {
                            "text": self.strings("play"),
                            "callback": self._inline__play,
                            "args": (chat_id,),
                        }
                    ]
                ),
                *(
                    [
                        {
                            "text": self.strings("mute"),
                            "callback": self._inline__mute,
                            "args": (chat_id,),
                        }
                    ]
                    if not self._muted.get(chat_id, False)
                    else [
                        {
                            "text": self.strings("unmute"),
                            "callback": self._inline__unmute,
                            "args": (chat_id,),
                        }
                    ]
                ),
            ],
            *(
                [
                    [
                        {
                            "text": self.strings("next"),
                            "callback": self._inline__next,
                            "args": (chat_id,),
                        }
                    ]
                ]
                if len(self._queue[chat_id]) > 1
                else []
            ),
        ]

        return msg, markup

    @loader.command(
        ru_doc="Приостановить воспроизведение",
        de_doc="Pausiere die Wiedergabe",
        tr_doc="Oynatmayı duraklat",
        hi_doc="प्लेबैक को रोकें",
        uz_doc="Oynatmani to'xtatish",
    )
    async def qpause(self, message: Message):
        """Pause current chat's queue"""
        chat_id = utils.get_chat_id(message)
        with contextlib.suppress(Exception):
            await self._app.pause_stream(chat_id)

        msg, markup = self._get_inline_info(chat_id)
        with contextlib.suppress(Exception):
            await self._forms[chat_id].delete()
        self._forms[chat_id] = await utils.answer(message, msg, reply_markup=markup)

    @loader.command(
        ru_doc="Остановить воспроизведение",
        de_doc="Stoppe die Wiedergabe",
        tr_doc="Oynatmayı durdur",
        hi_doc="प्लेबैक को बंद करें",
        uz_doc="Oynatmani to'xtatish",
    )
    async def qstop(self, message: Message):
        """Stop current chat's queue"""
        await self._inline__stop(message, utils.get_chat_id(message))

    @loader.command(
        ru_doc="Продолжить воспроизведение",
        de_doc="Fahre die Wiedergabe fort",
        tr_doc="Oynatmaya devam et",
        hi_doc="प्लेबैक को फिर से शुरू करें",
        uz_doc="Oynatmani davom ettirish",
    )
    async def qresume(self, message: Message):
        """Resume current chat's queue"""
        chat_id = utils.get_chat_id(message)
        with contextlib.suppress(Exception):
            await self._app.resume_stream(chat_id)

        msg, markup = self._get_inline_info(chat_id)
        with contextlib.suppress(Exception):
            await self._forms[chat_id].delete()
        self._forms[chat_id] = await utils.answer(message, msg, reply_markup=markup)

    async def play(self, chat_id: int, array: bytes):
        file = os.path.join(self._dir, f"{utils.rand(8)}.ogg")
        with open(file, "wb") as f:
            f.write(array)

        await self._play(
            chat_id,
            types.AudioPiped(file, types.HighQualityAudio()),
            StreamType().pulse_stream,
        )
        await asyncio.sleep(1)
        if not self.config["silent_queue"]:
            msg, markup = self._get_inline_info(chat_id)
            with contextlib.suppress(Exception):
                await self._forms[chat_id].delete()
            self._forms[chat_id] = await self.inline.form(
                message=chat_id, text=msg, reply_markup=markup
            )

    async def play_video(self, chat_id: int, array: bytes):
        file = os.path.join(self._dir, f"{utils.rand(8)}.mp4")
        with open(file, "wb") as f:
            f.write(array)

        await self._play(
            chat_id,
            types.AudioVideoPiped(
                file,
                types.HighQualityAudio(),
                types.HighQualityVideo(),
            ),
            StreamType().pulse_stream,
        )
        await asyncio.sleep(1)
        if not self.config["silent_queue"]:
            msg, markup = self._get_inline_info(chat_id)
            with contextlib.suppress(Exception):
                await self._forms[chat_id].delete()
            self._forms[chat_id] = await self.inline.form(
                message=chat_id, text=msg, reply_markup=markup
            )

    async def play_video_yt(self, chat_id: int, link: str):
        proc = await asyncio.create_subprocess_exec(
            "youtube-dl",
            "-g",
            "-f",
            "worst",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        await self._play(
            chat_id,
            types.AudioVideoPiped(
                stdout.decode().split("\n")[0],
                types.HighQualityAudio(),
                types.HighQualityVideo(),
            ),
            StreamType().pulse_stream,
        )
        await asyncio.sleep(1)
        if not self.config["silent_queue"]:
            msg, markup = self._get_inline_info(chat_id)
            with contextlib.suppress(Exception):
                await self._forms[chat_id].delete()
            self._forms[chat_id] = await self.inline.form(
                message=chat_id,
                text=msg,
                reply_markup=markup,
            )

    async def on_unload(self):
        shutil.rmtree(self._dir)
        for chat_id in self._muted:
            await self._app.leave_group_call(chat_id)
