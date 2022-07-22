#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta title: VoiceChat Beta
# meta pic: https://img.icons8.com/arcade/344/experimental-medium-volume-arcade.png
# meta banner: https://mods.hikariatama.ru/badges/voicechat.jpg
# meta developer: @hikarimods
# requires: py-tgcalls youtube_dl

import asyncio
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

from .. import loader, utils
from ..inline.types import InlineCall

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
        self._app = PyTgCalls(client)
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

    async def qaddcmd(self, message: Message):
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

    async def qaddvcmd(self, message: Message):
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

    async def qnextcmd(self, message: Message):
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

    async def qpausecmd(self, message: Message):
        """Pause current chat's queue"""
        chat_id = utils.get_chat_id(message)
        with contextlib.suppress(Exception):
            await self._app.pause_stream(chat_id)

        msg, markup = self._get_inline_info(chat_id)
        with contextlib.suppress(Exception):
            await self._forms[chat_id].delete()
        self._forms[chat_id] = await utils.answer(message, msg, reply_markup=markup)

    async def qstopcmd(self, message: Message):
        """Stop current chat's queue"""
        await self._inline__stop(message, utils.get_chat_id(message))

    async def qresumecmd(self, message: Message):
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
