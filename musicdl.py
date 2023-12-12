# Name: musicdl
# Description: Download music by hikariatama (modded by @y9chebupelka)
# Commands:
# .mdl
# meta developer: @chepuxmodules

from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class MusicDLMod(loader.Module):
    """Download music by hikariatama (modded by @y9chebupelka)"""

    strings = {
        "name": "MusicDL",
        "args": "<emoji document_id=5327801429111349563>🤦</emoji> <b>Arguments not specified</b>",
        "loading": "<emoji document_id=5325920220550799029>🤓</emoji> <b>Loading...</b>",
        "404": "🚫 <b>Music </b><code>{}</code><b> not found</b>",
    }

    strings_ru = {
        "args": "<emoji document_id=5327801429111349563>🤦</emoji> <b>Не указаны аргументы</b>",
        "loading": "<emoji document_id=5325920220550799029>🤓</emoji> <b>Загрузка...</b>",
        "404": "<emoji document_id=5325960528818872589>💢</emoji> <b>Песня </b><code>{}</code><b> не найдена</b>",
    }

    async def client_ready(self, *_):
        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    @loader.command(ru_doc="<название> - Скачать песню")
    async def mdl(self, message: Message):
        """<name> - Download track"""
        # Если команда была в ответ на сообщение с названием музыки, то берем его как аргумент
        if message.is_reply:
            reply = await message.get_reply_message()
            args = reply.raw_text
        else:
            # Иначе берем аргумент из сообщения
            args = utils.get_args_raw(message)
        # Если аргумент не указан, то показываем ошибку
        if not args:
            await utils.answer(message, self.strings["args"])
            return
        # Добавляем эту строку, чтобы удалить .m из аргументов
        args = args.replace(".m", "") # Удаляем .m из аргументов
        # Иначе показываем сообщение о загрузке
        message = await utils.answer(message, self.strings["loading"])
        # Используем библиотеку musicdl для скачивания музыки
        result = await self.musicdl.dl(args, only_document=True)
        # Если результат не найден, то показываем ошибку
        if not result:
            await utils.answer(message, self.strings["404"].format(args))
            return
        # Иначе отправляем файл с музыкой
        await self._client.send_file(
            message.peer_id,
            result,
            caption=f"<emoji document_id=5325965837398450115>😎</emoji> <b>{args.title()}</b>", # Добавляем название музыки в подпись и делаем его жирным
            reply_to=getattr(message, "reply_to_msg_id", None),
        )
        # Если сообщение было отправлено нами, то удаляем его
        if message.out:
            await message.delete()
