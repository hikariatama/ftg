#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/emoji/256/000000/waving-hand-emoji.png
# meta developer: @hikarimods

from telethon.tl.types import Message

from .. import loader


@loader.tds
class NoMetaMod(loader.Module):
    """Warns people about Meta messages"""

    strings = {
        "name": "NoMeta",
        "no_meta": (
            "<b>👾 <u>Please!</u></b>\n<b>NoMeta</b> aka <i>'Hello', 'Hi' etc.</i>\nAsk"
            " <b>directly</b>, what do you want from me."
        ),
        "no_meta_ru": (
            "<b>👾 <u>Пожалуйста!</u></b>\n<b>Не нужно лишних сообщений</b> по типу"
            " <i>'Привет', 'Хай' и др.</i>\nСпрашивай(-те) <b>конкретно</b>, что от"
            " меня нужно."
        ),
    }

    @loader.unrestricted
    async def nometacmd(self, message: Message):
        """Если кто-то отправил мету по типу 'Привет', эта команда его вразумит"""
        await self._client.send_message(
            message.peer_id,
            self.strings("no_meta"),
            reply_to=getattr(message, "reply_to_msg_id", None),
        )
        await message.delete()

    async def watcher(self, message: Message):
        if not getattr(message, "raw_text", False):
            return

        if not message.is_private:
            return

        meta = ["hi", "hello", "hey there", "konichiwa", "hey"]

        meta_ru = [
            "привет",
            "хай",
            "хелло",
            "хеллоу",
            "хэллоу",
            "коничива",
            "алоха",
            "слушай",
            "о",
            "слуш",
            "м?",
            "а?",
            "хей",
            "хэй",
            "йо",
            "йоу",
            "прив",
            "дан",
            "yo",
            "ку",
        ]

        if message.raw_text.lower() in meta:
            await self._client.send_message(
                message.peer_id, self.strings("no_meta"), reply_to=message.id
            )
            await self._client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )

        if message.raw_text.lower() in meta_ru:
            await self._client.send_message(
                message.peer_id, self.strings("no_meta_ru"), reply_to=message.id
            )
            await self._client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )
