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

# meta pic: https://img.icons8.com/fluency/240/000000/sticker.png
# meta developer: @hikarimods
# scope: ffmpeg
# scope: disable_onload_docs
# requires: Pillow moviepy emoji

import asyncio
import io
import logging
import os
import random
import time

import moviepy.editor as mp
from emoji import distinct_emoji_lis
from PIL import Image
from telethon.errors.rpcerrorlist import RPCError
from telethon.tl.functions.messages import (
    ClearRecentStickersRequest,
    GetStickerSetRequest,
    InstallStickerSetRequest,
    UninstallStickerSetRequest,
    UploadMediaRequest,
)
from telethon.tl.types import (
    InputDocument,
    InputMediaUploadedDocument,
    InputPeerSelf,
    InputStickerSetShortName,
    Message,
)
from telethon.utils import get_input_document

from .. import loader, utils

logger = logging.getLogger(__name__)


class HikariException(Exception):
    pass


@loader.tds
class StickManagerMod(loader.Module):
    """Sticker manager with video stickers support and friendly design"""

    strings = {
        "name": "StickManager",
        "no_args": "🚫 <b>This command requires arguments</b>",
        "no_such_pack": "🚫 <b>Stickerset not found</b>",
        "stickersets_added": "🌁 <code>{}</code><b> stickerset(-s) added, </b><code>{}</code><b> removed!</b>",
        "no_stickersets_to_import": "🚫 <b>No stickersets to import</b>",
        "no_stickersets": "🚫 <b>You have no stickersets</b>",
        "alias_removed": "✅ <b>Alias </b><code>{}</code><b> removed</b>",
        "remove_alias_404": "🚫 <b>No pack has alias </b><code>{}</code>",
        "pack404": "🚫 <b>Pack </b><code>{}</code><b> not found</b>",
        "created_alias": "{} <b>Created alias for {}. Access it with </b><code>{}</code>",
        "packs_header": "👨‍🎤 <b>Active Stickerpacks:</b>\n\n",
        "default": "{} <b>Set pack {} as default</b>",
        "packremoved": "{} <b>Removed pack {}</b>",
        "error": "🚫 <b>{}</b>",
        "kang": '{} <b>Sticker added to <a href="https://t.me/addstickers/{}">pack</a></b>\n<i>中国語で再び侮辱された 😥</i>',
        "created": '{} <b>Created new pack {} <a href="https://t.me/addstickers/{}">add</a></b>',
        "bot": "🤖 <b>Bot token saved</b>",
        "alias_exists": "🚫 <b>Alias </b><code>{}</code><b> exists</b>",
        "stickrm": "{} <b>Sticker removed from pack</b>\n<i>中国語で再び侮辱された 😥</i>",
        "processing": "👩‍🎤 <b>私はアニメの猫の男の子が大好きです! 処理...</b>",
        "processing_gif": "🧑🏻‍🎤 <b>処理中、お待ちください...</b>",
        "cleaned": "⏳ <b>最近使用したステッカーのリストがクリアされました.</b>",
    }

    strings_ru = {
        "no_args": "🚫 <b>Эта команда требует аргументы</b>",
        "no_such_pack": "🚫 <b>Стикерпак не найден</b>",
        "stickersets_added": "🌁 <code>{}</code><b> стикерпак(-ов) добавлено, </b><code>{}</code><b> удалено!</b>",
        "no_stickersets_to_import": "🚫 <b>Нет стикерпаков для импорта</b>",
        "no_stickersets": "🚫 <b>У тебя нет стикерпаков</b>",
        "alias_removed": "✅ <b>Алиас </b><code>{}</code><b> удален</b>",
        "remove_alias_404": "🚫 <b>Нет стикерпака с алиасом </b><code>{}</code>",
        "pack404": "🚫 <b>Стикерпак </b><code>{}</code><b> не найден</b>",
        "created_alias": "{} <b>Создан алиас для {}. Алиас: </b><code>{}</code>",
        "packs_header": "👨‍🎤 <b>Активные стикерпаки:</b>\n\n",
        "default": "{} <b>Пак {} установлен в качестве основного</b>",
        "packremoved": "{} <b>Пак {} удален</b>",
        "error": "🚫 <b>{}</b>",
        "bot": "🤖 <b>Токен бота сохранен</b>",
        "alias_exists": "🚫 <b>Алиас </b><code>{}</code><b> уже существует</b>",
        "stickrm": "{} <b>Стикер удален из пака</b>\n<i>中国語で再び侮辱された 😥</i>",
        "_cmd_doc_newpack": "<short_name> <имя> [-a <алиас>] - Создать новый стикерпак",
        "_cmd_doc_newvidpack": "<short_name> <имя> [-a <алиас>] - Создать новый видео стикерпак",
        "_cmd_doc_syncpacks": "Синхронизировать стикерпаки с @stickers",
        "_cmd_doc_packs": "Показать доступные стикерпаки",
        "_cmd_doc_stickalias": "<алиас> [short_name] - Добавить или удалить алиас",
        "_cmd_doc_stickdef": "<short_name|алиас> - Установить основной стикерпак",
        "_cmd_doc_rmpack": "<short_name|алиас> - Удалить стикерпак",
        "_cmd_doc_unstick": "<reply> - Удалить стикер из стикерпака",
        "_cmd_doc_stick": "[эмодзи] [short_name|алиас] - Добавить стикер в стикерпак",
        "_cmd_doc_rmrecent": "Очистить недавно использованные стикеры",
        "_cls_doc": "Управление стикерпаками с поддержкой видеопаков и дружелюбным интерфейсом",
    }

    def find(self, args: str) -> str or False:
        if args in self.stickersets:
            p = self.stickersets[args].copy()
            p.update({"shortname": args})
            return p

        for shortname, info in self.stickersets.copy().items():
            if info["alias"] == args:
                info.update({"shortname": shortname})
                return info

        return False

    async def prepare(self, message: Message) -> InputDocument:
        dl = io.BytesIO(await self._client.download_file(message.media, bytes))
        dl.seek(0)
        img = Image.open(dl)

        w, h = img.size
        if w > h:
            img = img.resize((512, int(h * (512 / w))), Image.ANTIALIAS)
        else:
            img = img.resize((int((w * (512 / h))), 512), Image.ANTIALIAS)

        dst = io.BytesIO()
        img.save(dst, "PNG")
        mime = "image/png"

        file = await self._client.upload_file(dst.getvalue())
        file = InputMediaUploadedDocument(file, mime, [])
        document = await self._client(UploadMediaRequest(InputPeerSelf(), file))
        document = get_input_document(document)

        return document

    async def prepare_vid(self, message: Message) -> InputDocument:
        dl = await self._client.download_file(message.media, bytes)

        with open("sticker.mp4", "wb") as f:
            f.write(dl)

        clip = mp.VideoFileClip("sticker.mp4")

        clip = clip.subclip(0, 3)

        w, h = clip.size

        size = f"512:{int(h * (512 / w))}" if w > h else f"{int(w * (512 / h))}:512"

        clip.write_videofile(
            "sticker.webm",
            audio=False,
            codec="libvpx-vp9",
            logger=None,
            fps=15,
            preset="faster",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-vf", f"scale={size}"],
        )

        clip.close()

        os.remove("sticker.mp4")

        return "sticker.webm"

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.stickersets = self.get("stickersets", {})
        self.default = self.get("default", None)

        if not self.default and self.stickersets:
            self.default = list(self.stickersets.keys())[0]

        self.emojies = list("🌌🌃🏙🌇🌆🌁🌉🎑🏞🎆🌅🌄🌠🎇🗾")

    async def newpackcmd(self, message: Message):
        """<short_name> <name> [-a <alias>] - Create new pack"""
        args = utils.get_args_raw(message)
        if "-a" in args:
            alias = args[args.find("-a") + 3 :]
            args = args[: args.find("-a")]
        else:
            alias = None

        args = args.split(maxsplit=1)
        reply = await message.get_reply_message()

        if not args or len(args) < 2:
            await utils.answer(
                message,
                self.strings("error").format(
                    "Usage: .newpack &lt;short_name&gt; &lt;name&gt;"
                ),
            )
            return

        if not reply or not reply.media:
            await utils.answer(
                message, self.strings("error").format("Reply to a photo required")
            )
            return

        message = await utils.answer(message, self.strings("processing"))

        shortname, name = args
        shortname, name = shortname.strip().lower(), name.strip()

        stick = await self.prepare(reply)
        assert stick

        async with self._client.conversation("@stickers") as conv:
            try:
                m = await conv.send_message("/cancel")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message("/newpack")
                r = await conv.get_response()

                if (
                    "Now choose a name" not in r.raw_text
                    and "выберите название для нового" not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while creating pack"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message(name)
                r = await conv.get_response()

                if (
                    "Now send me" not in r.raw_text
                    and "будущий стикер" not in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Error when typing name")

                await m.delete()
                await r.delete()

                m = await conv.send_file(stick, force_document=True)
                r = await conv.get_response()

                if not (
                    "Now send me an emoji" in r.raw_text
                    or ("Пожалуйста" in r.raw_text and "смайл" in r.raw_text)
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Error when sending file")

                await m.delete()
                await r.delete()

                m = await conv.send_message("🔆")
                r = await conv.get_response()

                if "/publish" not in r.raw_text:
                    raise HikariException("UNEXPECTED_ANSWER - No publish option")

                await m.delete()
                await r.delete()

                m = await conv.send_message("/publish")
                r = await conv.get_response()

                if "/skip" not in r.raw_text:
                    raise HikariException("UNEXPECTED_ANSWER - No skip option")

                await m.delete()
                await r.delete()

                m = await conv.send_message("/skip")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message(shortname)
                r = await conv.get_response()

                if (
                    "this short name is already taken" in r.raw_text
                    or "Увы, такой адрес уже занят." in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Occupied shortname")

                await m.delete()
                await r.delete()
            except HikariException as e:
                await utils.answer(message, f"🚫 <code>{e}</code>")
                return

        await self._client(
            InstallStickerSetRequest(
                stickerset=InputStickerSetShortName(shortname), archived=False
            )
        )

        if len(self.stickersets) >= len(self.emojies):
            emoji = random.choice(self.emojies)
        else:
            emoji = self.emojies[len(self.stickersets) + 1]

        self.stickersets[shortname] = {"title": name, "emoji": emoji, "alias": alias}

        self.set("stickersets", self.stickersets)

        await utils.answer(
            message,
            self.strings("created").format(
                emoji,
                name,
                shortname,
            ),
        )

    async def newvidpackcmd(self, message: Message):
        """<short_name> <name> [-a <alias>] - Create new video stickers pack"""
        args = utils.get_args_raw(message)
        if "-a" in args:
            alias = args[args.find("-a") + 3 :]
            args = args[: args.find("-a")]
        else:
            alias = None

        args = args.split(maxsplit=1)
        reply = await message.get_reply_message()

        if not args or len(args) < 2:
            await utils.answer(
                message,
                self.strings("error").format(
                    "Usage: .newvidpack &lt;short_name&gt; &lt;name&gt;"
                ),
            )
            return

        if not reply or not reply.media:
            await utils.answer(
                message, self.strings("error").format("Reply to a gif is required")
            )
            return

        shortname, name = args

        message = await utils.answer(message, self.strings("processing"))

        stick = await self.prepare_vid(reply)
        assert stick

        async with self._client.conversation("@stickers") as conv:
            try:
                m = await conv.send_message("/cancel")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message("/newvideo")
                r = await conv.get_response()

                if (
                    "A new set" not in r.raw_text
                    and "Создается новый набор видеостикеров." not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while creating pack"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message(name)
                r = await conv.get_response()

                if (
                    "Now send me the vide" not in r.raw_text
                    and "Теперь пришлите, пожалуйста, будущий стикер — файл в формате .WEBM"
                    not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while entering name"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_file(stick, force_document=True)
                r = await conv.get_response()

                if (
                    "Now send me an emoji" not in r.raw_text
                    and "Пожалуйста, отправьте мне новый смайл, который соответствует этому видеостикеру."
                    not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while sending file"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message("🔆")
                r = await conv.get_response()

                if "/publish" not in r.raw_text:
                    raise HikariException("UNEXPECTED_ANSWER - No publish option")

                await m.delete()
                await r.delete()

                m = await conv.send_message("/publish")
                r = await conv.get_response()

                if "/skip" not in r.raw_text:
                    raise HikariException("UNEXPECTED_ANSWER - Broke after /publish")

                await m.delete()
                await r.delete()

                m = await conv.send_message("/skip")
                r = await conv.get_response()

                if (
                    "provide a short name" not in r.raw_text
                    and "короткое название" not in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Broke after /skip")

                await m.delete()
                await r.delete()

                m = await conv.send_message(shortname)
                r = await conv.get_response()

                if (
                    "this short name is already taken" in r.raw_text
                    or "Увы, такой адрес уже занят." in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Occupied shortname")

                if (
                    "Kaboom" not in r.raw_text
                    and "успешно опубликован" not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Unknown confirmation error (Kaboom)"
                    )

                await m.delete()
                await r.delete()
            except HikariException as e:
                await utils.answer(message, f"🚫 <code>{e}</code>")
                return

        await self._client(
            InstallStickerSetRequest(
                stickerset=InputStickerSetShortName(shortname), archived=False
            )
        )

        if len(self.stickersets) >= len(self.emojies):
            emoji = random.choice(self.emojies)
        else:
            emoji = self.emojies[len(self.stickersets) + 1]

        self.stickersets[shortname] = {
            "title": name,
            "emoji": emoji,
            "alias": alias,
            "video": True,
        }

        self.set("stickersets", self.stickersets)

        await utils.answer(
            message, self.strings("created").format(emoji, name, shortname)
        )

    async def syncpackscmd(self, message: Message):
        """Sync existing stickersets with @stickers"""
        q = 0

        message = await utils.answer(message, self.strings("processing"))

        async with self._client.conversation("@stickers") as conv:
            m = await conv.send_message("/cancel")
            r = await conv.get_response()

            await m.delete()
            await r.delete()

            m = await conv.send_message("/packstats")
            r = await conv.get_response()

            packs = []
            for row in [
                [btn.text for btn in row.buttons] for row in r.reply_markup.rows
            ]:
                for btn in row:
                    packs += [btn]
                    if btn in self.stickersets:
                        continue

                    try:
                        stickerset = await self._client(
                            GetStickerSetRequest(
                                stickerset=InputStickerSetShortName(btn),
                                hash=round(time.time()),
                            )
                        )
                    except Exception:
                        continue

                    if len(self.stickersets) >= len(self.emojies):
                        emoji = random.choice(self.emojies)
                    else:
                        emoji = self.emojies[len(self.stickersets) + 1]

                    self.stickersets[btn] = {
                        "title": stickerset.set.title,
                        "emoji": emoji,
                        "alias": None,
                    }

                    q += 1

            await m.delete()
            await r.delete()

            m = await conv.send_message("/cancel")
            r = await conv.get_response()

            await m.delete()
            await r.delete()

        d = 0
        for pack in list(self.stickersets.keys()).copy():
            if pack not in packs:
                del self.stickersets[pack]
                d += 1

        self.set("stickersets", self.stickersets)

        await utils.answer(message, self.strings("stickersets_added").format(q, d))

    async def packscmd(self, message: Message):
        """Short available stickersets"""
        if not self.stickersets:
            await utils.answer(message, self.strings("no_stickersets"))
            return

        res = self.strings("packs_header")
        for shortname, info in self.stickersets.items():
            alias = (
                f' (<code>{utils.escape_html(info["alias"])}</code>)'
                if info["alias"]
                else f" (<code>{utils.escape_html(shortname)}</code>)"
            )
            res += f"{info['emoji']} <b>{utils.escape_html(info['title'])}</b> <a href=\"https://t.me/addstickers/{shortname}\">add</a>{alias}\n"

        await utils.answer(message, res)

    async def stickaliascmd(self, message: Message):
        """<alias> [short_name] - Add or remove alias"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        args = args.split(maxsplit=1)
        if len(args) == 1:
            for shortname, info in self.stickersets.items():
                if info["alias"] == args[0]:
                    self.stickersets[shortname]["alias"] = None
                    self.set("stickersets", self.stickersets)
                    await utils.answer(
                        message, self.strings("alias_removed").format(args[0])
                    )
                    return

            await utils.answer(
                message, self.strings("remove_alias_404").format(args[0])
            )
            return
        else:
            alias, pack = args
            if pack not in self.stickersets:
                await utils.answer(message, self.strings("pack404").format(pack))
                return

            if any(alias == pack["alias"] for pack in self.stickersets.values()):
                await utils.answer(message, self.strings("alias_exists").format(alias))
                return

            self.stickersets[pack]["alias"] = alias
            self.set("stickersets", self.stickersets)
            await utils.answer(
                message,
                self.strings("created_alias").format(
                    self.stickersets[pack]["emoji"],
                    utils.escape_html(self.stickersets[pack]["title"]),
                    alias,
                ),
            )

    async def stickdefcmd(self, message: Message):
        """<short_name|alias> - Set default stickerpack"""
        args = utils.get_args_raw(message)
        pack = self.find(args)
        if not pack:
            await utils.answer(message, self.strings("pack404").format(args))
            return

        self.default = pack["shortname"]
        self.set("default", self.default)
        await utils.answer(
            message,
            self.strings("default").format(
                pack["emoji"],
                utils.escape_html(pack["title"]),
            ),
        )

    async def rmpackcmd(self, message: Message):
        """<short_name|alias> - Remove stickerpack"""
        args = utils.get_args_raw(message)
        pack = self.find(args)
        if not pack:
            await utils.answer(message, self.strings("pack404").format(args))
            return

        try:
            await self._client(
                UninstallStickerSetRequest(
                    stickerset=InputStickerSetShortName(pack["shortname"])
                )
            )
        except RPCError:
            await utils.answer(
                message, self.strings("pack404").format(pack["shortname"])
            )
            return

        message = await utils.answer(message, self.strings("processing"))

        async with self._client.conversation("@stickers") as conv:
            try:
                m = await conv.send_message("/cancel")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message("/delpack")
                r = await conv.get_response()

                if (
                    "Choose the sticker set" not in r.raw_text
                    and "который хотите удалить" not in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - After /delpack")

                await m.delete()
                await r.delete()

                m = await conv.send_message(pack["shortname"])
                r = await conv.get_response()

                if (
                    "you selected the set" not in r.raw_text
                    and "Вы выбрали набор" not in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - After sending shortname")

                await m.delete()
                await r.delete()

                if "Вы выбрали набор" not in r.raw_text:
                    m = await conv.send_message("Yes, I am totally sure.")
                else:
                    m = await conv.send_message("Да, удалите этот набор.")

                r = await conv.get_response()

                if (
                    "The sticker set is gon" not in r.raw_text
                    and "Набор стикеров был удален." not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Confirmation did not work"
                    )

                await m.delete()
                await r.delete()
            except HikariException as e:
                await utils.answer(message, f"🚫 <code>{e}</code>")
                return

        del self.stickersets[pack["shortname"]]
        self.set("stickersets", self.stickersets)
        await utils.answer(
            message,
            self.strings("packremoved").format(
                pack["emoji"],
                utils.escape_html(pack["title"]),
            ),
        )

    async def unstickcmd(self, message: Message):
        """<reply> - Remove sticker from pack"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("error").format("Reply required"))
            return

        async with self._client.conversation("@stickers") as conv:
            try:
                m = await conv.send_message("/cancel")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message("/delsticker")
                r = await conv.get_response()

                if not (
                    ("Choose a sticker" in r.raw_text)
                    or ("Выберите нужный набор") in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while starting action"
                    )

                await m.delete()
                await r.delete()

                m = await self._client.forward_messages(
                    "@stickers", [reply.id], message.peer_id
                )
                r = await conv.get_response()

                if not (
                    ("I have deleted that sticker" in r.raw_text)
                    or ("Стикер успешно удален") in r.raw_text
                ):
                    raise HikariException("UNEXPECTED_ANSWER - Sticker not deleted")

                await m[0].delete()
                await r.delete()
            except HikariException as e:
                await utils.answer(message, f"🚫 <code>{e}</code>")
                return

        await utils.answer(
            message, self.strings("stickrm").format(random.choice(self.emojies))
        )
        await asyncio.sleep(7)
        await message.delete()

    async def stickcmd(self, message: Message):
        """[emoji] [short_name|alias] - Add sticker to pack. If not specified - default"""
        if not self.stickersets:
            await utils.answer(message, self.strings("no_stickersets"))
            return

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(
                message, self.strings("error").format("Reply to sticker required")
            )
            return

        pack, emoji = None, None
        if len(args.split()) > 1:
            pack = self.find(args.split(maxsplit=1)[1])
            if pack:
                emoji = args.split(maxsplit=1)[0]
            else:
                pack = self.find(args)
                if not pack:
                    await utils.answer(message, self.strings("pack404").format(args))
                    return

        elif args:
            pack = self.find(args)
            if not pack:
                pack = self.find(self.default)
                emoji = args

        if not pack:
            pack = self.find(self.default)

        if not pack:
            await utils.answer(
                message, self.strings("error").format("Default pack doesn't exist")
            )
            return

        if not emoji or not "".join(distinct_emoji_lis(emoji)):
            emoji = pack["emoji"]

        emoji = "".join(distinct_emoji_lis(emoji))

        if getattr(getattr(reply.media, "document", None), "mime_type", "").startswith(
            "video"
        ):
            if "video" not in pack:
                pack = [
                    self.find(_) for _, p in self.stickersets.items() if "video" in p
                ]
                if not pack:
                    await utils.answer(
                        message,
                        self.strings("error").format(
                            "Can't add video sticker - no video stickersets"
                        ),
                    )
                    return

                pack = pack[0]

            message = await utils.answer(message, self.strings("processing_gif"))
            stick = await self.prepare_vid(reply)
        else:
            message = await utils.answer(message, self.strings("processing"))
            stick = await self.prepare(reply)

        async with self._client.conversation("@stickers") as conv:
            try:
                m = await conv.send_message("/cancel")
                r = await conv.get_response()

                await m.delete()
                await r.delete()

                m = await conv.send_message("/addsticker")
                r = await conv.get_response()

                if (
                    "Choose a sticker set" not in r.raw_text
                    and "Выберите набор стикеров." not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while starting action"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message(pack["shortname"])
                r = await conv.get_response()

                if "Alright!" not in r.raw_text and "будущий стикер" not in r.raw_text:
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while choosing pack"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_file(stick, force_document=True)
                r = await conv.get_response()

                if (
                    "Now send me an emoji" not in r.raw_text
                    and "Пожалуйста, пришлите смайл" not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while sending file"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message(emoji)
                r = await conv.get_response()

                if (
                    "There we go" not in r.raw_text
                    and "Стикер был добавлен в набор" not in r.raw_text
                ):
                    raise HikariException(
                        "UNEXPECTED_ANSWER - Error while sending emoji"
                    )

                await m.delete()
                await r.delete()

                m = await conv.send_message("/done")
                r = await conv.get_response()

                if "OK" not in r.raw_text and "Готово!" not in r.raw_text:
                    raise HikariException("UNEXPECTED_ANSWER - Error on confirmation")

                await m.delete()
                await r.delete()
            except HikariException as e:
                await utils.answer(message, f"🚫 <code>{e}</code>")
                return

        await utils.answer(
            message, self.strings("kang").format(pack["emoji"], pack["shortname"])
        )
        await asyncio.sleep(7)
        await message.delete()

    async def rmrecentcmd(self, message: Message):
        """Clear recently used stickers"""
        await self._client(ClearRecentStickersRequest(attached=False))
        await utils.answer(message, self.strings("cleaned"))
