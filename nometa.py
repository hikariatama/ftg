#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html


# meta pic: https://static.dan.tatar/nometa_icon.png
# meta banner: https://mods.hikariatama.ru/badges/nometa.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.3.0

from telethon.tl.types import Message

from .. import loader, utils


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

    @loader.command(ru_doc="Показать сообщение с предупреждением о мете")
    @loader.unrestricted
    async def nometacmd(self, message: Message):
        """Show message about NoMeta"""
        await self._client.send_message(
            message.peer_id,
            self.strings("no_meta"),
            reply_to=getattr(message, "reply_to_msg_id", None),
        )
        if message.out:
            await message.delete()

    @loader.tag("only_messages", "only_pm", "in")
    async def watcher(self, message: Message):
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
            "yo",
            "ку",
        ]

        if message.raw_text.lower() in meta:
            await utils.answer(message, self.strings("no_meta"))
            await self._client.send_read_acknowledge(
                message.chat_id,
                clear_mentions=True,
            )

        if message.raw_text.lower() in meta_ru:
            await utils.answer(message, self.strings("no_meta_ru"))
            await self._client.send_read_acknowledge(
                message.chat_id, clear_mentions=True
            )
