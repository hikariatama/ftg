__version__ = (3, 0, 2)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/sticker.png
# meta banner: https://mods.hikariatama.ru/badges/sticks.jpg
# meta developer: @hikarimods
# scope: ffmpeg
# scope: disable_onload_docs
# requires: Pillow moviepy emoji requests_toolbelt
# scope: hikka_min 1.3.3

import asyncio
import io
import re
import logging
import math
import os
import random
import time
import requests
from requests_toolbelt import MultipartEncoder
import grapheme
import moviepy.editor as mp
import emoji
from PIL import Image, ImageChops, ImageFont, ImageDraw

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
from ..inline.types import InlineCall


# https://gist.github.com/turicas/1455973


class ImageText:
    def __init__(
        self,
        size: tuple,
        mode: str = "RGBA",
        background: tuple = (0, 0, 0, 0),
        encoding: str = "utf8",
    ):
        self.size = size
        self.image = Image.new(mode, self.size, color=background)
        self.draw = ImageDraw.Draw(self.image)
        self.encoding = encoding

    def get_font_size(
        self,
        text: str,
        font: ImageFont,
        max_width: int = None,
        max_height: int = None,
    ) -> int:
        if max_width is None and max_height is None:
            raise ValueError("You need to pass max_width or max_height")
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or (
            max_height is not None and text_size[1] > max_height
        ):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % text_size)

        while True:
            if (max_width is not None and text_size[0] >= max_width) or (
                max_height is not None and text_size[1] >= max_height
            ):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(
        self,
        coordinates: tuple,
        text: str,
        font_stream: io.BytesIO,
        font_size: int = 11,
        color: tuple = (0, 0, 0),
        max_width: int = None,
        max_height: int = None,
    ) -> int:
        x, y = coordinates
        # if isinstance(text, str):
        #     text = text.decode(self.encoding)
        if font_size == "fill" and (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_stream, max_width, max_height)
        text_size = self.get_text_size(font_stream, font_size, text)
        font_stream.seek(0)
        font = ImageFont.truetype(font_stream, font_size)
        if x == "center":
            x = (self.size[0] - text_size[0]) / 2
        if y == "center":
            y = (self.size[1] - text_size[1]) / 2
        self.draw.text((x, y), text, font=font, fill=color)
        return text_size

    def get_text_size(self, font_stream: io.BytesIO, font_size: int, text: str) -> int:
        font_stream.seek(0)
        font = ImageFont.truetype(font_stream, font_size)
        return font.getsize(text)

    def write_text_box(
        self,
        coordinates: tuple,
        text: str,
        box_width: int,
        font_stream: io.BytesIO,
        font_size: int = 11,
        color: tuple = (0, 0, 0),
        place: str = "center",
        justify_last_line: bool = False,
    ):
        x, y = coordinates
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = " ".join(line + [word])
            size = self.get_text_size(font_stream, font_size, new_line)
            text_height = size[1]
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [" ".join(line) for line in lines if line]
        height = y
        for index, line in enumerate(lines):
            height += text_height
            if place == "left":
                self.write_text((x, height), line, font_stream, font_size, color)
            elif place == "right":
                total_size = self.get_text_size(font_stream, font_size, line)
                x_left = x + box_width - total_size[0]
                self.write_text((x_left, height), line, font_stream, font_size, color)
            elif place == "center":
                total_size = self.get_text_size(font_stream, font_size, line)
                x_left = int(x + ((box_width - total_size[0]) / 2))
                self.write_text((x_left, height), line, font_stream, font_size, color)
            elif place == "justify":
                words = line.split()
                if (index == len(lines) - 1 and not justify_last_line) or len(
                    words
                ) == 1:
                    self.write_text((x, height), line, font_stream, font_size, color)
                    continue
                line_without_spaces = "".join(words)
                total_size = self.get_text_size(
                    font_stream, font_size, line_without_spaces
                )
                space_width = (box_width - total_size[0]) / (len(words) - 1.0)
                start_x = x
                for word in words[:-1]:
                    self.write_text(
                        (start_x, height), word, font_stream, font_size, color
                    )
                    word_size = self.get_text_size(font_stream, font_size, word)
                    start_x += word_size[0] + space_width
                last_word_size = self.get_text_size(font_stream, font_size, words[-1])
                last_word_x = x + box_width - last_word_size[0]
                self.write_text(
                    (last_word_x, height), words[-1], font_stream, font_size, color
                )
        return (box_width, height - y)


logger = logging.getLogger(__name__)

distinct_emoji_list = getattr(
    emoji,
    "distinct_emoji_lis",
    getattr(emoji, "distinct_emoji_list", None),
)

if distinct_emoji_list is None:
    raise ImportError


class HikariException(Exception):
    pass


@loader.tds
class StickManagerMod(loader.Module):
    """Sticker manager with video stickers support and friendly design"""

    strings = {
        "name": "StickManager",
        "no_args": "🚫 <b>This command requires arguments</b>",
        "no_such_pack": "🚫 <b>Stickerset not found</b>",
        "stickersets_added": (
            "🌁 <code>{}</code><b> stickerset(-s) added, </b><code>{}</code><b>"
            " removed!</b>"
        ),
        "no_stickersets_to_import": "🚫 <b>No stickersets to import</b>",
        "no_stickersets": "🚫 <b>You have no stickersets</b>",
        "alias_removed": "✅ <b>Alias </b><code>{}</code><b> removed</b>",
        "remove_alias_404": "🚫 <b>No pack has alias </b><code>{}</code>",
        "pack404": "🚫 <b>Pack </b><code>{}</code><b> not found</b>",
        "created_alias": (
            "{} <b>Created alias for {}. Access it with </b><code>{}</code>"
        ),
        "packs_header": "👨‍🎤 <b>Active Stickerpacks:</b>\n\n",
        "default": "{} <b>Set pack {} as default</b>",
        "packremoved": "{} <b>Removed pack {}</b>",
        "error": "🚫 <b>{}</b>",
        "kang": (
            "<emoji document_id='6334599075337340489'>🍵</emoji> <b>Sticker added to <a"
            ' href="https://t.me/addstickers/{}">pack</a></b>'
        ),
        "created": (
            "<emoji document_id='5370900768796711127'>🍾</emoji> <b>Created new pack {}"
            ' <a href="https://t.me/addstickers/{}">add</a></b>'
        ),
        "alias_exists": "🚫 <b>Alias </b><code>{}</code><b> exists</b>",
        "stickrm": "{} <b>Sticker removed from pack</b>",
        "need_reply": "🚫 <b>Reply to use this command</b>",
        "cleaned": "⏳ <b>Recents cleared.</b>",
        "processing": "👩‍🎤 <b>Processing media...</b>",
        "processing_gif": "🧑🏻‍🎤 <b>Processing video...</b>",
        "rmbg": (
            "<emoji document_id='6048696253632482685'>✂️</emoji> <b>Removing"
            " background...</b>"
        ),
        "trimming": (
            "<emoji document_id='6037132221691727143'>✂️</emoji> <b>Trimming...</b>"
        ),
        "outline": (
            "<emoji document_id='6048640560791555243'>🖌</emoji> <b>Adding"
            " outline...</b>"
        ),
        "adding_text": (
            "<emoji document_id='6048366494633430880'>🅰️</emoji> <b>Adding text...</b>"
        ),
        "exporting": (
            "<emoji document_id='6048887676029898150'>📥</emoji> <b>Exporting...</b>"
        ),
        "confirm_remove": "🚫 <b>Are you sure you want to delete pack {}?</b>",
        "remove": "🚫 Delete",
        "cancel": "🔻 Cancel",
        "deleting_pack": "😓 <b>Deleting pack...</b>",
    }

    strings_ru = {
        "no_args": "🚫 <b>Эта команда требует аргументы</b>",
        "no_such_pack": "🚫 <b>Стикерпак не найден</b>",
        "stickersets_added": (
            "🌁 <code>{}</code><b> стикерпак(-ов) добавлено, </b><code>{}</code><b>"
            " удалено!</b>"
        ),
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
        "alias_exists": "🚫 <b>Алиас </b><code>{}</code><b> уже существует</b>",
        "stickrm": "{} <b>Стикер удален из пака</b>",
        "_cls_doc": (
            "Управление стикерпаками с поддержкой видеопаков и дружелюбным интерфейсом"
        ),
        "need_reply": "🚫 <b>Необходим ответ на сообщение</b>",
        "cleaned": "⏳ <b>Недавние очищены.</b>",
        "processing": "👩‍🎤 <b>Обрабатываю медиа...</b>",
        "processing_gif": "🧑🏻‍🎤 <b>Обрабатываю видео...</b>",
        "rmbg": (
            "<emoji document_id='6048696253632482685'>✂️</emoji> <b>Убираю фон...</b>"
        ),
        "trimming": (
            "<emoji document_id='6037132221691727143'>✂️</emoji> <b>Подрезаю"
            " края...</b>"
        ),
        "outline": (
            "<emoji document_id='6048640560791555243'>🖌</emoji> <b>Добавлю"
            " окантовку...</b>"
        ),
        "adding_text": (
            "<emoji document_id='6048366494633430880'>🅰️</emoji> <b>Накладываю"
            " текст...</b>"
        ),
        "exporting": (
            "<emoji document_id='6048887676029898150'>📥</emoji> <b>Экспортирую...</b>"
        ),
        "confirm_remove": "🚫 <b>Вы уверены, что хотите удалить пак {}?</b>",
        "remove": "🚫 Удалить",
        "cancel": "🔻 Отмена",
        "deleting_pack": "😓 <b>Удаляю пак...</b>",
    }

    def find(self, args: str) -> str:
        if args in self.stickersets:
            p = self.stickersets[args].copy()
            p.update({"shortname": args})
            return p

        for shortname, info in self.stickersets.copy().items():
            if info["alias"] == args:
                info.update({"shortname": shortname})
                return info

        return False

    @staticmethod
    def trim(image: Image) -> Image:
        bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
        diff = ImageChops.difference(image, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            bbox = (
                bbox[0] - 5 if bbox[0] >= 5 else 0,
                bbox[1] - 5 if bbox[1] >= 5 else 0,
                bbox[2] + 5 if bbox[2] + 5 <= image.width else image.width,
                bbox[3] + 5 if bbox[3] + 5 <= image.height else image.height,
            )
            return image.crop(bbox)

        return image

    @staticmethod
    def stroke(
        image: Image,
        strokeSize: int = 5,
        color: tuple = (255, 255, 255),
    ) -> Image:
        # Create a disc kernel
        kernel = []
        kernelSize = math.ceil(strokeSize) * 2 + 1  # Should always be odd
        kernelRadius = strokeSize + 0.5
        kernelCenter = kernelSize / 2 - 1
        pixelRadius = 1 / math.sqrt(math.pi)
        for x in range(kernelSize):
            kernel.append([])
            for y in range(kernelSize):
                distanceToCenter = math.sqrt(
                    (kernelCenter - x + 0.5) ** 2 + (kernelCenter - y + 0.5) ** 2
                )
                if distanceToCenter <= kernelRadius - pixelRadius:
                    value = 1  # This pixel is fully inside the circle
                elif distanceToCenter <= kernelRadius:
                    value = min(
                        1,
                        (kernelRadius - distanceToCenter + pixelRadius)
                        / (pixelRadius * 2),
                    )  # Mostly inside
                elif distanceToCenter <= kernelRadius + pixelRadius:
                    value = min(
                        1,
                        (pixelRadius - (distanceToCenter - kernelRadius))
                        / (pixelRadius * 2),
                    )  # Mostly outside
                else:
                    value = 0  # This pixel is fully outside the circle
                kernel[x].append(value)
        kernelExtent = int(len(kernel) / 2)
        imageWidth, imageHeight = image.size
        outline = image.copy()
        outline.paste((0, 0, 0, 0), [0, 0, imageWidth, imageHeight])
        imagePixels = image.load()
        outlinePixels = outline.load()
        # Morphological grayscale dilation
        for x in range(imageWidth):
            for y in range(imageHeight):
                highestValue = 0
                for kx in range(-kernelExtent, kernelExtent + 1):
                    for ky in range(-kernelExtent, kernelExtent + 1):
                        kernelValue = kernel[kx + kernelExtent][ky + kernelExtent]
                        if (
                            x + kx >= 0
                            and y + ky >= 0
                            and x + kx < imageWidth
                            and y + ky < imageHeight
                            and kernelValue > 0
                        ):
                            highestValue = max(
                                highestValue,
                                min(
                                    255,
                                    int(
                                        round(
                                            imagePixels[x + kx, y + ky][3] * kernelValue
                                        )
                                    ),
                                ),
                            )
                outlinePixels[x, y] = (color[0], color[1], color[2], highestValue)
        outline.paste(image, (0, 0), image)
        return outline

    @loader.command(ru_doc="<реплай> - Убрать фон с картинки")
    async def rmbg(self, message: Message):
        """<reply> - Remove background from image"""
        reply = await message.get_reply_message()
        if not reply or not reply.photo and not reply.sticker:
            await utils.answer(message, self.strings("need_reply"))
            return

        message = await utils.answer(message, self.strings("rmbg"))

        photo = io.BytesIO()
        photo.name = "photo.webp"
        Image.open(
            await (self.remove_bg_api if self.config["use_api"] else self.remove_bg)(
                io.BytesIO(await self._client.download_media(reply, bytes))
            )
        ).save(photo, "WEBP")
        photo.seek(0)
        await self._client.send_file(
            message.peer_id,
            photo,
            reply_to=reply.id,
        )
        if message.out:
            await message.delete()

    async def prepare(
        self,
        status: Message,
        message: Message,
        outline: bool = False,
        remove_bg: bool = False,
        text: str = None,
        only_bytes: bool = False,
    ) -> InputDocument:
        dl = io.BytesIO(await self._client.download_file(message.media, bytes))
        dl.seek(0)

        if remove_bg:
            status = await utils.answer(status, self.strings("rmbg"))
            dl = await (
                self.remove_bg_api if self.config["use_api"] else self.remove_bg
            )(dl)
            dl.seek(0)

        status = await utils.answer(status, self.strings("trimming"))
        img = await utils.run_sync(self.trim, Image.open(dl))

        if outline:
            status = await utils.answer(status, self.strings("outline"))
            img = await utils.run_sync(self.stroke, img, self.config["stroke_size"])

        if text:
            status = await utils.answer(status, self.strings("adding_text"))
            await self._font_ready.wait()
            new_img = Image.new("RGBA", (img.width, img.height), (255, 255, 255, 0))
            proportions = img.width / img.height
            image_text = ImageText(new_img.size)
            self._raw_font.seek(0)
            image_text.write_text_box(
                (0, 0),
                text,
                new_img.width - 8,
                self._raw_font,
                max(
                    self.config["font_size"],
                    40
                    if len(text) < 5
                    else 35
                    if len(text) < 10
                    else 30
                    if len(text) < 15
                    else 25
                    if len(text) < 20
                    else self.config["font_size"],
                ),
                (255, 255, 255),
                "center",
            )
            image_text.image = await utils.run_sync(self.trim, image_text.image)
            img = img.resize(
                (
                    round((img.height - image_text.image.height) * proportions),
                    round(img.height - image_text.image.height),
                )
            )
            new_img.paste(
                img,
                ((new_img.width - img.width) // 2, image_text.image.height + 8),
                mask=img,
            )
            new_img.paste(
                image_text.image,
                (
                    (new_img.width - image_text.image.width) // 2,
                    4,
                    (new_img.width - image_text.image.width) // 2
                    + image_text.image.width,
                    image_text.image.height + 4,
                ),
                mask=image_text.image,
            )
            img = new_img

        w, h = img.size
        if w > h:
            img = img.resize((512, int(h * (512 / w))), Image.ANTIALIAS)
        else:
            img = img.resize((int((w * (512 / h))), 512), Image.ANTIALIAS)

        dst = io.BytesIO()
        img.save(dst, "PNG")
        mime = "image/png"

        status = await utils.answer(status, self.strings("exporting"))

        if only_bytes:
            return dst.getvalue()

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

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "font_size",
                18,
                "Font size of text to apply to image",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "stroke_size",
                5,
                "Stroke size to apply to image",
                validator=loader.validators.Integer(minimum=5),
            ),
            loader.ConfigValue(
                "use_api",
                False,
                "Use API to remove background, not bot",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        self.stickersets = self.pointer("stickersets", {})
        self.default = self.get("default", None)

        if not self.default and self.stickersets:
            self.default = list(self.stickersets.keys())[0]

        self.emojies = list(
            grapheme.graphemes("🌌🌃🏙🌇🌆🌁🌉🎑🏞🎆🌅🌄🌠🎇🗾🐭🐱🐶🐹🐰🦊🐻🐼🐻‍❄️🐨🐯🦁🐮🐷🐸🐵🙉🐥🦆🦄🐴🐗🐺🦇🦉🦅")
        )

        self._font_ready = asyncio.Event()

        asyncio.ensure_future(self._dl_font())

    async def _dl_font(self):
        self._raw_font = io.BytesIO(
            (
                await utils.run_sync(
                    requests.get,
                    "https://0x0.st/oLI7.ttf",
                )
            ).content
        )
        self._font_ready.set()

    @loader.command(
        ru_doc="<short_name> <название> [-a <алиас>] - Создать новый стикерпак"
    )
    async def newpack(self, message: Message):
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

        stick = await self.prepare(message, reply)
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

        await utils.answer(
            message,
            self.strings("created").format(
                name,
                shortname,
            ),
        )

    @loader.command(
        ru_doc="<short_name> <имя> [-a <алиас>] - Создать новый видео стикерпак"
    )
    async def newvidpack(self, message: Message):
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

        await utils.answer(message, self.strings("created").format(name, shortname))

    @loader.command(ru_doc="Синхронизировать стикерпаки с @stickers")
    async def syncpacks(self, message: Message):
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
        for pack in list(self.stickersets).copy():
            if pack not in packs:
                self.stickersets.pop(pack)
                d += 1

        await utils.answer(message, self.strings("stickersets_added").format(q, d))

    @loader.command(ru_doc="Показать доступные стикерпаки")
    async def packs(self, message: Message):
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
            res += (
                f"{info['emoji']} <b>{utils.escape_html(info['title'])}</b> <a"
                f' href="https://t.me/addstickers/{shortname}">add</a>{alias}\n'
            )

        await utils.answer(message, res)

    @loader.command(ru_doc="<алиас> [short_name] - Добавить или удалить алиас")
    async def stickalias(self, message: Message):
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
            await utils.answer(
                message,
                self.strings("created_alias").format(
                    self.stickersets[pack]["emoji"],
                    utils.escape_html(self.stickersets[pack]["title"]),
                    alias,
                ),
            )

    @loader.command(ru_doc="<short_name|алиас> - Установить стандартный стикерпак")
    async def stickdef(self, message: Message):
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

    @loader.command(ru_doc="<short_name|алиас> - Удалить стикерпак")
    async def rmpack(self, message: Message):
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

        await self.inline.form(
            message=message,
            text=self.strings("confirm_remove").format(pack["title"]),
            reply_markup=[
                {
                    "text": self.strings("remove"),
                    "callback": self._remove,
                    "args": (pack,),
                },
                {"text": self.strings("cancel"), "action": "close"},
            ],
        )

    async def _remove(self, call: InlineCall, pack: dict):
        call = await utils.answer(call, self.strings("deleting_pack"))

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
                await utils.answer(call, f"🚫 <code>{e}</code>")
                return

        self.stickersets.pop(pack["shortname"])
        await utils.answer(
            call,
            self.strings("packremoved").format(
                pack["emoji"],
                utils.escape_html(pack["title"]),
            ),
        )

    @loader.command(ru_doc="<реплай> - Удалить стикер из пака")
    async def unstick(self, message: Message):
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

    async def remove_bg(self, image: io.BytesIO) -> io.BytesIO:
        todel = []
        async with self._client.conversation("@removefundobot") as conv:
            m = await conv.send_file(image)
            r = await conv.get_response()

            if not r.document:
                todel += [r]
                r = await conv.get_response()

            todel += [m]
            todel += [r]

            if not r.document:
                raise RuntimeError("Unable to remove background from image")

            im = io.BytesIO(await self._client.download_media(r, bytes))

            for i in todel:
                await i.delete()

            return im

    @staticmethod
    async def remove_bg_api(photo: bytes) -> str:
        HEADERS = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            ),
        }

        response1 = await utils.run_sync(
            requests.get,
            "https://icons8.com/bgremover",
            headers=HEADERS,
        )
        _jwt_token = response1.cookies.get("i8remover")
        response2 = await utils.run_sync(
            requests.post,
            "https://api-bgremover-origin.icons8.com/api/frontend/v1/batches",
            headers={"Authorization": f"Bearer {_jwt_token}"},
            cookies=response1.cookies,
        )
        _id = response2.json()["id"]

        fields = {
            "image": ("hikka.jpg", photo, "image/jpeg"),
        }

        boundary = "----WebKitFormBoundary" + utils.rand(16)
        m = MultipartEncoder(fields=fields, boundary=boundary)

        await utils.run_sync(
            requests.post,
            f"https://api-bgremover-origin.icons8.com/api/frontend/v1/batches/{_id}",
            headers={
                "Authorization": f"Bearer {_jwt_token}",
                "content-type": m.content_type,
                "connection": "keep-alive",
            },
            data=m,
            cookies=response1.cookies,
        )

        url = ".jpg"

        for _ in range(3):
            if not url.endswith(".jpg"):
                break

            await asyncio.sleep(2)

            response4 = await utils.run_sync(
                requests.get,
                "https://icons8.com/bgremover",
                headers=HEADERS,
                cookies=response1.cookies,
            )

            url = re.search(
                r'Processed transparent png file" src="(.*?)"',
                response4.text,
            ).group(1)

        url = url.replace("&amp;", "&")

        return io.BytesIO(
            (
                await utils.run_sync(
                    requests.get,
                    url,
                    cookies=response1.cookies,
                    headers=HEADERS,
                )
            ).content
        )

    @loader.command(
        ru_doc=(
            "[эмодзи] [short_name|алиам] [-o - добавить окантовку] [-r - убрать фон]"
            " [-q - Не добавлять в пак, а просто отправить стикер] [-t <текст> -"
            " наложить текст] - Добавить стикер \ картинку в пак. Если не указано в"
            " какой, будет использован стандартный\nПример:\n.stick mypack -b -r -q -t"
            " Привет, мир!"
        )
    )
    async def stick(self, message: Message):
        """[emoji] [short_name|alias] [-o - add outline] [-r - remove background] [-q - Do not add sticker to pack, just send it] [-t <text> - add text] - Add sticker to pack. If not specified - default
        Example:
        .stick mypack -b -r -q -t Hello world!"""
        if not self.stickersets:
            await utils.answer(message, self.strings("no_stickersets"))
            return

        args = utils.get_args_raw(message)

        args = f" {args} "

        if " -o" in args:
            args = args.replace(" -o", "")
            outline = True
        else:
            outline = False

        if " -r" in args:
            args = args.replace(" -r", "")
            remove_bg = True
        else:
            remove_bg = False

        if " -q" in args:
            args = args.replace(" -q", "")
            quiet = True
        else:
            quiet = False

        if " -t" in args:
            text = args[args.index(" -t") + 3 :]
            args = args[: args.index(" -t")]
        else:
            text = None

        args = args.strip()

        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(
                message,
                self.strings("error").format("Reply to sticker required"),
            )
            return

        if not quiet:
            pack, emoji = None, None
            if len(args.split()) > 1:
                pack = self.find(args.split(maxsplit=1)[1])
                if pack:
                    emoji = args.split(maxsplit=1)[0]
                else:
                    pack = self.find(args)
                    if not pack:
                        await utils.answer(
                            message, self.strings("pack404").format(args)
                        )
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

            if not emoji or not "".join(distinct_emoji_list(emoji)):
                emoji = pack["emoji"]

            emoji = "".join(distinct_emoji_list(emoji))

        if getattr(getattr(reply.media, "document", None), "mime_type", "").startswith(
            "video"
        ):
            if quiet or outline or remove_bg or text:
                await utils.answer(
                    message,
                    self.strings("error").format(
                        "Arguments for video stickers are not supported"
                    ),
                )
                return

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
            stick = await self.prepare(message, reply, outline, remove_bg, text, quiet)

        if quiet:
            file = io.BytesIO()
            Image.open(io.BytesIO(stick)).save(file, "webp")
            file.name = "sticker.webp"
            file.seek(0)
            await self._client.send_file(
                message.peer_id,
                file,
                reply_to=message.reply_to_msg_id,
            )
            if message.out:
                await message.delete()

            return

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
            message,
            self.strings("kang").format(pack["shortname"]),
        )

    @loader.command(ru_doc="Очистить недавно использованные стикеры")
    async def rmrecent(self, message: Message):
        """Clear recently used stickers"""
        await self._client(ClearRecentStickersRequest(attached=False))
        await utils.answer(message, self.strings("cleaned"))
