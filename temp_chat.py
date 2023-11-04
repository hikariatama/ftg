__version__ = (3, 0, 0)

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://github.com/hikariatama/Hikka
# 🔑 https://creativecommons.org/licenses/by-nc-nd/4.0/
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta pic: https://static.hikari.gay/temp_chat_icon.png
# meta banner: https://mods.hikariatama.ru/badges/temp_chat.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.3

import asyncio
import datetime
import logging
import re
import time
import typing

import requests
from hikkatl.tl.functions.channels import (
    CreateChannelRequest,
    DeleteChannelRequest,
    EditPhotoRequest,
)
from hikkatl.tl.functions.messages import ExportChatInviteRequest
from hikkatl.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


class TmpChatInfo(typing.NamedTuple):
    until: int
    title: str


@loader.tds
class TmpChats(loader.Module):
    """Creates temprorary chats"""

    strings = {
        "name": "TmpChats",
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>This chat is being deleted...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Args are incorrect<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat not found</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Chat </b><code>{}</code><b> will now live forever!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>An error occured while deleting this temp chat. Please, do it"
            " manually.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>This chat will be permanently deleted"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> have been created</b>',
        "delete_error_me": "🚫 <b>Error occured while deleting chat {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Creating temporary chat...</b>",
    }

    strings_ru = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Чат удаляется...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Неверные аргументы</b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Чат не найден</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Чат </b><code>{}</code><b> будет жить вечно!</b>",
        "delete_error": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Произошла ошибка удаления чата. Сделай это вручную.</b>",
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Этот чат будет удален"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Чат <a href="{}">{}</a> создан</b>',
        "delete_error_me": "🚫 <b>Произошла ошибка при удалении чата {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Создание временного чата...</b>",
        "_cmd_doc_tmpchat": "<время> <название> - Создать новый временный чат",
        "_cmd_doc_tmpcurrent": "<время> - Создать новый временный чат",
        "_cmd_doc_tmpchats": "Показать временные чаты",
        "_cmd_doc_tmpcancel": "[chat-id] - Отменить удаление чата.",
        "_cmd_doc_tmpctime": "<chat_id> <новое время> - Изменить время жизни чата",
        "_cls_doc": "Создает временные чаты во избежание мусорки в Телеграме.",
    }

    strings_de = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Dieser Chat wird gelöscht...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Argumente sind falsch<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat nicht gefunden</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Chat </b><code>{}</code><b> wird jetzt für immer leben!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Es ist ein Fehler beim Löschen dieses temporären Chats aufgetreten. Bitte tun Sie es"
            " manuell.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Dieser Chat wird dauerhaft gelöscht"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> wurde erstellt</b>',
        "delete_error_me": "🚫 <b>Fehler beim Löschen des Chats {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Erstelle temporären Chat...</b>",
        "_cmd_doc_tmpchat": "<Zeit> <Titel> - Erstellt neuen temporären Chat",
        "_cmd_doc_tmpcurrent": "<Zeit> - Erstellt neuen temporären Chat",
        "_cmd_doc_tmpchats": "Liste temporärer Chats",
        "_cmd_doc_tmpcancel": "[Chat-ID] - Deaktiviert das Löschen des Chats nach Ablauf der Zeit.",
        "_cmd_doc_tmpctime": "<Chat-ID> <Neue Zeit> - Ändert die Löschzeit des Chats",
        "_cls_doc": "Erstellt temporäre Chats, um den Müll in Telegram zu vermeiden.",
    }

    strings_tr = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Bu sohbet siliniyor...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Argümanlar yanlış<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Sohbet bulunamadı</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Sohbet </b><code>{}</code><b> artık sonsuza kadar yaşayacak!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Bu geçici sohbeti silerken bir hata oluştu. Lütfen bunu yapın"
            " manuel.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Bu sohbet kalıcı olarak silinecek"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Sohbet <a href="{}">{}</a> oluşturuldu</b>',
        "delete_error_me": "🚫 <b>Sohbeti silerken hata oluştu {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Geçici sohbet oluşturuluyor...</b>",
        "_cmd_doc_tmpchat": "<zaman> <başlık> - Yeni geçici sohbet oluştur",
        "_cmd_doc_tmpcurrent": "<zaman> - Yeni geçici sohbet oluştur",
        "_cmd_doc_tmpchats": "Geçici sohbetleri listele",
        "_cmd_doc_tmpcancel": "[sohbet-id] - Süre dolduktan sonra sohbeti silmeyi devre dışı bırakın.",
        "_cmd_doc_tmpctime": "<sohbet_id> <yeni zaman> - Sohbet silme süresini değiştir",
        "_cls_doc": "Telegram'daki çöpleri önlemek için geçici sohbetler oluşturur.",
    }

    strings_uz = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Ushbu chat o'chirilmoqda...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Argumetlar noto'g'ri<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat topilmadi</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Chat </b><code>{}</code><b> doimiy yashashga o'tkazildi!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Bu vaqtli chatni o'chirishda xatolik yuz berdi. Iltimos, uni bajarib ko'ring"
            " qo'llanma.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Bu chat doimiy ravishda o'chiriladi"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> yaratildi</b>',
        "delete_error_me": "🚫 <b>Chatni o'chirishda xatolik yuz berdi {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Vaqtli chat yaratilmoqda...</b>",
        "_cmd_doc_tmpchat": "<vaqt> <nomi> - Yangi vaqtli chat yaratish",
        "_cmd_doc_tmpcurrent": "<vaqt> - Yangi vaqtli chat yaratish",
        "_cmd_doc_tmpchats": "Vaqtli chatlarni ro'yxatdan o'tkazish",
        "_cmd_doc_tmpcancel": "[chat-id] - Vaqt tugaganidan so'ng chatni o'chirishni bekor qilish.",
        "_cmd_doc_tmpctime": "<chat_id> <yangi vaqt> - Chatni o'chirish vaqti o'zgartirish",
        "_cls_doc": "Telegramdagi axlatni oldini olish uchun vaqtli chatlar yaratadi.",
    }

    strings_it = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Questa chat sta per essere eliminata...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Gli argomenti sono sbagliati<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat non trovata</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>La chat </b><code>{}</code><b> vivrà per sempre!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Si è verificato un errore durante l'eliminazione di questa chat temporanea. Per favore, fallo"
            " manuale.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Questa chat verrà eliminata"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> è stata creata</b>',
        "delete_error_me": "🚫 <b>Errore durante l'eliminazione della chat {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Creazione chat temporanea...</b>",
        "_cmd_doc_tmpchat": "<tempo> <titolo> - Crea nuova chat temporanea",
        "_cmd_doc_tmpcurrent": "<tempo> - Crea nuova chat temporanea",
        "_cmd_doc_tmpchats": "Elenco chat temporanee",
        "_cmd_doc_tmpcancel": "[chat-id] - Disabilita l'eliminazione della chat dopo il tempo specificato.",
        "_cmd_doc_tmpctime": "<chat_id> <nuovo tempo> - Modifica il tempo di eliminazione della chat",
        "_cls_doc": "Crea chat temporanee per evitare la spazzatura in Telegram.",
    }

    strings_es = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Este chat está siendo eliminado...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Los argumentos son incorrectos<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat no encontrado</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>El chat </b><code>{}</code><b> ahora vivirá para siempre!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Se ha producido un error al eliminar este chat temporal. Por favor, hágalo"
            " manualmente.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Este chat será eliminado"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> ha sido creado</b>',
        "delete_error_me": "🚫 <b>Error al eliminar el chat {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Creando chat temporal...</b>",
        "_cmd_doc_tmpchat": "<tiempo> <título> - Crea un nuevo chat temporal",
        "_cmd_doc_tmpcurrent": "<tiempo> - Crea un nuevo chat temporal",
        "_cmd_doc_tmpchats": "Lista de chats temporales",
        "_cmd_doc_tmpcancel": "[chat-id] - Desactiva la eliminación del chat después del tiempo especificado.",
        "_cmd_doc_tmpctime": "<chat_id> <nuevo tiempo> - Cambia el tiempo de eliminación del chat",
        "_cls_doc": "Crea chats temporales para evitar la basura en Telegram.",
    }

    strings_fr = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Ce chat est en train d'être supprimé...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Les arguments sont incorrects<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Chat introuvable</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Le chat </b><code>{}</code><b> vivra maintenant pour toujours!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Une erreur s'est produite lors de la suppression de ce chat temporaire. S'il vous plaît, faites-le"
            " manuellement.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Ce chat sera définitivement supprimé"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Chat <a href="{}">{}</a> a été créé</b>',
        "delete_error_me": "🚫 <b>Une erreur s'est produite lors de la suppression du chat {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Création du chat temporaire...</b>",
        "_cmd_doc_tmpchat": "<temps> <titre> - Crée un nouveau chat temporaire",
        "_cmd_doc_tmpcurrent": "<temps> - Crée un nouveau chat temporaire",
        "_cmd_doc_tmpchats": "Liste des chats temporaires",
        "_cmd_doc_tmpcancel": "[chat-id] - Désactive la suppression du chat après le délai spécifié.",
        "_cmd_doc_tmpctime": "<chat_id> <nouveau temps> - Modifie le temps de suppression du chat",
        "_cls_doc": "Crée des chats temporaires pour éviter les déchets dans Telegram.",
    }

    strings_kk = {
        "chat_is_being_removed": "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Бұл сөйлеу өшірілуде...</b>",
        "args": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Аргументтер дұрыс емес<b>",
        "chat_not_found": "<emoji document_id=5462882007451185227>🚫</emoji> <b>Сөйлеу табылмады</b>",
        "tmp_cancelled": "<emoji document_id=5463081281048818043>✅</emoji> <b>Сөйлеу </b><code>{}</code><b> қазірдің күніне дейін өмір сүрер!</b>",
        "delete_error": (
            "<emoji document_id=5463358164705489689>⛔️</emoji> <b>Осы уақыттың сөйлеуін жою кезінде қате пайда болды. Өтінемін, оны"
            " қолмен орындаңыз.</b>"
        ),
        "temp_chat_header": (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Бұл сөйлеу өшіріледі"
            " {}.</b>"
        ),
        "chat_created": '<emoji document_id=5465465194056525619>👍</emoji> <b>Сөйлеу <a href="{}">{}</a> жасалды</b>',
        "delete_error_me": "🚫 <b>Сөйлеуді жою кезінде қате пайда болды {}</b>",
        "creating": "<emoji document_id=5416081784641168838>🟢</emoji> <b>Уақытша сөйлеу жасау...</b>",
        "_cmd_doc_tmpchat": "<уақыт> <атауы> - Жаңа уақытша сөйлеу жасау",
        "_cmd_doc_tmpcurrent": "<уақыт> - Жаңа уақытша сөйлеу жасау",
        "_cmd_doc_tmpchats": "Уақытша сөйлеулер тізімі",
        "_cmd_doc_tmpcancel": "[сөйлеу-ID] - Уақыт аяқталғаннан кейін сөйлеуді жоюды өшіру.",
        "_cmd_doc_tmpctime": "<сөйлеу_ID> <жаңа уақыт> - Сөйлеуді жою уақытын өзгерту",
        "_cls_doc": "Telegramдағы тығыздықты алу үшін уақытша сөйлеулер жасайды.",
    }

    def __init__(self):
        self._chats: typing.Dict[str, TmpChatInfo] = None

    async def client_ready(self):
        self._chats = self.pointer("chats", {}, item_type=TmpChatInfo)

    @staticmethod
    def extract_time(t: str) -> int:
        """
        Tries to export time from text
        """
        try:
            if not str(t)[:-1].isdigit():
                return 0

            if "d" in str(t):
                t = int(t[:-1]) * 60 * 60 * 24

            if "h" in str(t):
                t = int(t[:-1]) * 60 * 60

            if "m" in str(t):
                t = int(t[:-1]) * 60

            if "s" in str(t):
                t = int(t[:-1])

            t = int(re.sub(r"[^0-9]", "", str(t)))
        except ValueError:
            return 0

        return t

    @loader.loop(interval=60, autostart=True)
    async def chats_handler_async(self):
        for chat, info in dict(self._chats).items():
            if info.until > time.time():
                continue

            try:
                await self._client.send_message(
                    int(chat),
                    self.strings("chat_is_being_removed"),
                )
                await asyncio.sleep(1)
                await self._client(DeleteChannelRequest(int(chat)))
            except Exception:
                logger.exception("Failed to delete chat")
                await self.inline.bot.send_message(
                    self._tg_id,
                    self.strings("delete_error_me").format(
                        utils.escape_html(info.title)
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

            self._chats.pop(chat)

    @loader.command()
    async def tmpchat(self, message: Message):
        """<time> <title> - Create new temporary chat"""
        if not (args := utils.get_args_raw(message)) or len(args.split()) < 2:
            await utils.answer(message, self.strings("args"))
            return

        until, title = args.split(maxsplit=1)
        if until != "0" and not (until := self.extract_time(until)):
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("creating"))

        channel = (
            await self._client(
                CreateChannelRequest(
                    title,
                    "",
                    megagroup=True,
                )
            )
        ).chats[0]

        await self._client(
            EditPhotoRequest(
                channel=channel,
                photo=await self._client.upload_file(
                    (
                        await utils.run_sync(
                            requests.get,
                            f"https://api.dicebear.com/7.x/shapes/png?seed={utils.rand(10)}",
                        )
                    ).content,
                    file_name="photo.png",
                ),
            )
        )

        await self._client.delete_messages(channel, 2)
        await utils.answer(
            message,
            self.strings("chat_created").format(
                (await self._client(ExportChatInviteRequest(channel))).link,
                utils.escape_html(title),
            ),
        )

        if until != "0":
            await (
                await (
                    await self._client.send_message(
                        channel.id,
                        self.strings("temp_chat_header").format(
                            datetime.datetime.utcfromtimestamp(
                                time.time() + until + 10800
                            ).strftime("%d.%m.%Y %H:%M:%S"),
                        ),
                    )
                ).pin()
            ).delete()

            self._chats[str(channel.id)] = TmpChatInfo(until + time.time(), title)

    @loader.command()
    async def tmpcurrent(self, message: Message):
        """<time> - Make current chat temporary"""
        if not (args := utils.get_args_raw(message)) or not (
            until := self.extract_time(args)
        ):
            await utils.answer(message, self.strings("args"))
            return

        channel_id = utils.get_chat_id(message)

        await utils.answer(
            message,
            self.strings("temp_chat_header").format(
                datetime.datetime.utcfromtimestamp(
                    time.time() + until + 10800
                ).strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )

        self._chats[str(channel_id)] = TmpChatInfo(
            until + time.time(),
            (await self._client.get_entity(channel_id)).title,
        )

    @loader.command()
    async def tmpchats(self, message: Message):
        """List temp chats"""
        text = (
            "<emoji document_id=5778550614669660455>⏲</emoji> <b>Temporary Chats</b>\n"
        )
        for chat, info in dict(self._chats).items():
            text += (
                f"<b>{utils.escape_html(info.title)}</b> (<code>{chat}</code>)<b>:"
                f" {datetime.datetime.utcfromtimestamp(info.until).strftime('%d.%m.%Y %H:%M:%S')}.</b>\n"
            )

        await utils.answer(message, text)

    @loader.command()
    async def tmpcancel(self, message: Message):
        """[chat-id] - Disable deleting chat by id, or current chat if unspecified."""
        if (args := utils.get_args_raw(message)) not in self._chats:
            args = str(utils.get_chat_id(message))

        if args not in self._chats:
            await utils.answer(message, self.strings("chat_not_found"))
            return

        await utils.answer(
            message,
            self.strings("tmp_cancelled").format(
                utils.escape_html(self._chats[args].title)
            ),
        )
        self._chats.pop(args)

    @loader.command()
    async def tmpctime(self, message: Message):
        """[chat_id] <new_time> - Change chat deletion time"""
        if not (args := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("args"))
            return

        args = args.split()

        if len(args) >= 2:
            chat = args[0]
            new_time = self.extract_time(args[1])
        else:
            chat = str(utils.get_chat_id(message))
            new_time = self.extract_time(args[0])

        if chat not in self._chats:
            await utils.answer(message, self.strings("chat_not_found"))
            return

        self._chats[chat] = TmpChatInfo(
            new_time + time.time() + 10800,
            (await self._client.get_entity(int(chat))).title,
        )

        await utils.answer(
            message,
            self.strings("temp_chat_header").format(
                datetime.datetime.utcfromtimestamp(
                    new_time + time.time() + 10800
                ).strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )
