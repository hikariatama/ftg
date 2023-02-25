__version__ = (2, 0, 8)

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

# meta pic: https://0x0.st/oRer.webp
# meta banner: https://mods.hikariatama.ru/badges/nekospy_beta.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.1
# requires: python-magic

import asyncio
import datetime
import io
import json
import logging
import mimetypes
import os
import time
import typing
import zlib
from pathlib import Path

import magic
from telethon.tl.types import (
    InputDocumentFileLocation,
    InputPhotoFileLocation,
    Message,
    UpdateDeleteChannelMessages,
    UpdateDeleteMessages,
    UpdateEditChannelMessage,
    UpdateEditMessage,
)
from telethon.utils import get_display_name

from .. import loader, utils
from ..database import Database
from ..pointers import PointerList
from ..tl_cache import CustomTelegramClient

logger = logging.getLogger(__name__)


def get_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())


def sizeof_fmt(num: int, suffix: str = "B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class CacheManager:
    def __init__(self, client: CustomTelegramClient, db: Database):
        self._client = client
        self._db = db
        self._cache_dir = Path.home().joinpath(".nekospy")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def purge(self):
        for _file in self._cache_dir.iterdir():
            if _file.is_dir():
                for _child in _file.iterdir():
                    _child.unlink()

                _file.rmdir()

    def stats(self) -> tuple:
        dirsize = sizeof_fmt(get_size(self._cache_dir))
        messages_count = len(list(self._cache_dir.iterdir()))
        try:
            oldest_message = datetime.datetime.fromtimestamp(
                max(map(os.path.getctime, self._cache_dir.iterdir()))
            ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            oldest_message = "n/a"

        return dirsize, messages_count, oldest_message

    def gc(self, max_age: int, max_size: int) -> None:
        """Clean the cache"""
        for _file in self._cache_dir.iterdir():
            if _file.is_file():
                if _file.stat().st_mtime < time.time() - max_age:
                    _file.unlink()
            else:
                for _child in _file.iterdir():
                    if (
                        _child.is_file()
                        and _child.stat().st_mtime < time.time() - max_age
                    ):
                        _child.unlink()

        while get_size(self._cache_dir) > max_size:
            min(
                self._cache_dir.iterdir(),
                key=lambda x: x.stat().st_mtime,
            ).unlink()

    async def store_message(self, message: Message, no_repeat: bool = False) -> bool:
        """Store a message in the cache"""
        if not hasattr(message, "id"):
            return False

        _dir = self._cache_dir.joinpath(str(utils.get_chat_id(message)))
        _dir.mkdir(parents=True, exist_ok=True)
        _file = _dir.joinpath(str(message.id))

        try:
            if message.sender_id is not None:
                sender = await self._client.get_entity(message.sender_id, exp=0)

            chat = await self._client.get_entity(utils.get_chat_id(message), exp=0)

            if message.sender_id is None:
                sender = chat
        except ValueError:
            if no_repeat:
                logger.debug("Failed to get sender/chat, skipping", exc_info=True)
                return False

            await asyncio.sleep(5)
            return await self.store_message(message, True)

        is_chat: bool = message.is_group or message.is_channel

        try:
            text: str = message.text
        except AttributeError:
            text: str = message.raw_text

        message_data = {
            "url": await utils.get_message_link(message),
            "text": text,
            "sender_id": sender.id,
            "sender_bot": not not getattr(sender, "bot", False),
            "sender_name": utils.escape_html(get_display_name(sender)),
            "sender_url": utils.get_entity_url(sender),
            "chat_id": chat.id,
            **(
                {
                    "chat_name": utils.escape_html(get_display_name(chat)),
                    "chat_url": utils.get_entity_url(chat),
                }
                if is_chat
                else {}
            ),
            "assets": await self._extract_assets(message),
            "is_chat": is_chat,
            "via_bot_id": not not message.via_bot_id,
        }

        _file.write_bytes(zlib.compress(json.dumps(message_data).encode("utf-8")))
        return True

    async def fetch_message(
        self,
        chat_id: typing.Optional[int],
        message_id: int,
    ) -> typing.Optional[dict]:
        """Fetch a message from the cache"""
        if chat_id:
            _dir = self._cache_dir.joinpath(str(chat_id))
            _file = _dir.joinpath(str(message_id))
        else:
            for _dir in self._cache_dir.iterdir():
                _file = _dir.joinpath(str(message_id))
                if _file.exists():
                    break
            else:
                _file = None

        if not _file or not _file.exists():
            return None

        return json.loads(zlib.decompress(_file.read_bytes()).decode("utf-8"))

    async def _extract_assets(self, message: Message) -> typing.Dict[str, str]:
        return {
            attribute: {
                "id": value.id,
                "access_hash": value.access_hash,
                "file_reference": bytearray(value.file_reference).hex(),
                "thumb_size": getattr(value, "thumb_size", ""),
            }
            for attribute, value in filter(
                lambda x: x[1],
                {
                    arg: getattr(message, arg)
                    for arg in {
                        "photo",
                        "audio",
                        "document",
                        "sticker",
                        "video",
                        "voice",
                        "video_note",
                        "gif",
                    }
                }.items(),
            )
        }


@loader.tds
class NekoSpyBeta(loader.Module):
    """Sends you deleted and / or edited messages from selected users"""

    rei = "<emoji document_id=5418198632287443057>👩‍🎤</emoji>"
    groups = "<emoji document_id=5416121680592380517>👥</emoji>"
    pm = "<emoji document_id=5417994032930364867>👤</emoji>"

    strings = {
        "name": "NekoSpy",
        "state": f"{rei} <b>Spy mode is now {{}}</b>",
        "spybl": f"{rei} <b>Current chat added to blacklist for spying</b>",
        "spybl_removed": f"{rei} <b>Current chat removed from blacklist for spying</b>",
        "spybl_clear": f"{rei} <b>Ignore list for spying cleared</b>",
        "spywl": f"{rei} <b>Current chat added to whitelist for spying</b>",
        "spywl_removed": f"{rei} <b>Current chat removed from whitelist for spying</b>",
        "spywl_clear": f"{rei} <b>Include list for spying cleared</b>",
        "whitelist": f"\n{rei} <b>Tracking only messages from:</b>\n{{}}",
        "always_track": f"\n{rei} <b>Always tracking messages from:</b>\n{{}}",
        "blacklist": f"\n{rei} <b>Ignoring messages from:</b>\n{{}}",
        "chat": f"{groups} <b>Tracking messages in groups</b>\n",
        "pm": f"{pm} <b>Tracking messages in personal messages</b>\n",
        "mode_off": f"{pm} <b>Not tracking messages </b><code>{{}}spymode</code>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> deleted <a href="{message_url}">message</a> in'
            " pm. Content:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{message_url}">Message</a> in chat <a href="{}">{}</a> by <a'
            ' href="{}">{}</a> has been deleted. Content:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> edited <a href="{message_url}">message</a> in pm.'
            " Old content:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{message_url}">Message</a> in chat <a href="{}">{}</a> by <a'
            ' href="{}">{}</a> has been edited. Old content:</b>\n{}'
        ),
        "on": "on",
        "off": "off",
        "cfg_enable_pm": "Enable spy mode in Personal messages",
        "cfg_enable_groups": "Enable spy mode in Groups",
        "cfg_whitelist": "List of chats to include messages from",
        "cfg_blacklist": "List of chats to exclude messages from",
        "cfg_always_track": (
            "List of chats to always track messages from, no matter what"
        ),
        "cfg_log_edits": "Log information about messages being edited",
        "cfg_ignore_inline": "Ignore inline messages (sent using @via bots)",
        "cfg_fw_protect": "Interval of messages sending to prevent floodwait",
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> sent you a self-destructing"
            " media</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Saving"
            " self-destructing media</b>\n"
        ),
        "cfg_save_sd": "Save self-destructing media",
        "max_cache_size": "Maximum size of cache directory",
        "max_cache_age": "Maximum age of cache records",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Cache"
            " stats</b>\n\n<emoji document_id=5783078953308655968>📊</emoji> <b>Total"
            " cache size: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Saved messages: {}"
            " pcs.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>Oldest"
            " message: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Cache has successfully"
            " been purged</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Invalid time</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Restoring messages</b>"
        ),
        "restored": (
            f"{rei} <b>Messages has successfully been restored. They will be delivered"
            " to hikka-nekospy channel soon.</b>"
        ),
        "recent_maximum": "Maximum time to restore messages from in seconds",
    }

    strings_ru = {
        "on": "включен",
        "off": "выключен",
        "state": f"{rei} <b>Режим слежения теперь {{}}</b>",
        "spybl": f"{rei} <b>Текущий чат добавлен в черный список для слежения</b>",
        "spybl_removed": (
            f"{rei} <b>Текущий чат удален из черного списка для слежения</b>"
        ),
        "spybl_clear": f"{rei} <b>Черный список для слежения очищен</b>",
        "spywl": f"{rei} <b>Текущий чат добавлен в белый список для слежения</b>",
        "spywl_removed": (
            f"{rei} <b>Текущий чат удален из белого списка для слежения</b>"
        ),
        "spywl_clear": f"{rei} <b>Белый список для слежения очищен</b>",
        "whitelist": (
            f"\n{rei} <b>Слежу только"
            " за сообщениями от пользователей / групп:</b>\n{}"
        ),
        "always_track": (
            f"\n{rei} <b>Всегда слежу за сообщениями от пользователей /"
            " групп:</b>\n{}"
        ),
        "blacklist": (
            f"\n{rei} <b>Игнорирую сообщений от пользователей / групп:</b>\n{{}}"
        ),
        "chat": f"{groups} <b>Слежу за сообщениями в группах</b>\n",
        "pm": f"{pm} <b>Слежу за сообщениями в личных сообщениях</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> удалил <a href="{message_url}">сообщение</a> в'
            " личке. Содержимое:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{message_url}">Сообщение</a> в чате <a href="{}">{}</a> от'
            ' <a href="{}">{}</a> было удалено. Содержимое:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> отредактировал <a'
            ' href="{message_url}">сообщение</a> в личке. Старое содержимое:</b>\n{}'
        ),
        "edited_chat": (
            '🔏 <b><a href="{message_url}">Сообщение</a> в чате <a href="{}">{}</a> от'
            ' <a href="{}">{}</a> было отредактировано. Старое содержимое:</b>\n{}'
        ),
        "mode_off": f"{pm} <b>Не отслеживаю сообщения </b><code>{{}}spymode</code>\n",
        "cfg_enable_pm": "Включить режим шпиона в личных сообщениях",
        "cfg_enable_groups": "Включить режим шпиона в группах",
        "cfg_whitelist": "Список чатов, от которых нужно сохранять сообщения",
        "cfg_blacklist": "Список чатов, от которых нужно игнорировать сообщения",
        "cfg_always_track": (
            "Список чатов, от которых всегда следует отслеживать сообщения,"
            " несмотря ни на что"
        ),
        "cfg_log_edits": "Сохранять отредактированные сообщения",
        "cfg_ignore_inline": "Игнорировать сообщения из инлайн-режима",
        "cfg_fw_protect": "Защита от флудвейтов при пересылке",
        "_cls_doc": (
            "Сохраняет удаленные и/или отредактированные сообщения от выбранных"
            " пользователей"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> отправил вам самоуничтожающееся"
            " медиа</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Сохраняю"
            " самоуничтожающиеся медиа</b>\n"
        ),
        "cfg_save_sd": "Сохранять самоуничтожающееся медиа",
        "max_cache_size": "Максимальный размер кеша",
        "max_cache_age": "Максимальный срок хранения кэша",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Статистика"
            " кэша</b>\n\n<emoji document_id=5783078953308655968>📊</emoji> <b>Общий"
            " размер кэша: {}</b>\n<emoji document_id=5974220038956124904>📥</emoji>"
            " <b>Сохраненные сообщения: {} шт.</b>\n<emoji"
            " document_id=5974081491901091242>🕒</emoji> <b>Самое старое сообщение:"
            " {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Кэш успешно очищен</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Неверное время</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Восстановление"
            " сообщений</b>"
        ),
        "restored": (
            f"{rei} <b>Сообщения успешно восстановлены. Они будут доставлены в канал"
            " hikka-nekospy в ближайшее время.</b>"
        ),
        "recent_maximum": "Максимальное время восстановления сообщений в секундах",
    }

    strings_fr = {
        "on": "allumé",
        "off": "éteint",
        "state": f"{rei} <b>Le mode espionnage est maintenant {{}}</b>",
        "spybl": (
            f"{rei} <b>Le chat actuel a été ajouté à la liste noire de surveillance</b>"
        ),
        "spybl_removed": (
            f"{rei} <b>Le chat actuel a été supprimé de la liste noire de"
            " surveillance</b>"
        ),
        "spybl_clear": f"{rei} <b>La liste noire de surveillance a été effacée</b>",
        "spywl": (
            f"{rei} <b>Le chat actuel a été ajouté à la liste blanche de"
            " surveillance</b>"
        ),
        "spywl_removed": (
            f"{rei} <b>Le chat actuel a été supprimé de la liste blanche de"
            " surveillance</b>"
        ),
        "spywl_clear": f"{rei} <b>La liste blanche de surveillance a été effacée</b>",
        "whitelist": (
            f"\n{rei} <b>Je surveille uniquement"
            " les messages d'utilisateurs / groupes:</b>\n{}"
        ),
        "always_track": (
            f"\n{rei} <b>Je surveille toujours les messages d'utilisateurs /"
            " groupes:</b>\n{}"
        ),
        "blacklist": (
            f"\n{rei} <b>Je ignore les messages des utilisateurs / groupes:</b>\n{{}}"
        ),
        "chat": f"{groups} <b>Je surveille les messages de groupes</b>\n",
        "pm": f"{pm} <b>Je surveille les messages de messages privés</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> a supprimé <a href="{message_url}">message</a> en'
            " privé. Contenu:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{message_url}">Message</a> dans le chat <a href="{}">{}</a>'
            ' de <a href="{}">{}</a> a été supprimé. Contenu:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> a modifié <a'
            ' href="{message_url}">message</a> en privé. Ancien contenu:</b>\n{}'
        ),
        "edited_chat": (
            '🔏 <b><a href="{message_url}">Message</a> dans le chat <a href="{}">{}</a>'
            ' de <a href="{}">{}</a> a été modifié. Ancien contenu:</b>\n{}'
        ),
        "mode_off": (
            f"{pm} <b>Ne pas surveiller les messages </b><code>{{}}spymode</code>\n"
        ),
        "cfg_enable_pm": "Activer le mode espion dans les messages privés",
        "cfg_enable_groups": "Activer le mode espion dans les groupes",
        "cfg_whitelist": "Liste des chats dont les messages doivent être enregistrés",
        "cfg_blacklist": "Liste des chats dont les messages doivent être ignorés",
        "cfg_always_track": (
            "Liste des chats dont les messages doivent toujours être surveillés,"
            " indépendamment de tout"
        ),
        "cfg_log_edits": "Enregistrer les messages modifiés",
        "cfg_ignore_inline": "Ignorer les messages du mode en ligne",
        "cfg_fw_protect": "Protection contre les floodways lors de la rétroaction",
        "_cls_doc": (
            "Enregistre les messages supprimés et / ou modifiés des utilisateurs"
            " sélectionnés"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> vous a envoyé un média"
            " auto-destructeur</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Enregistrement"
            " les médias auto-destructeurs</b>\n"
        ),
        "cfg_save_sd": "Enregistrer les médias auto-destructeurs",
        "max_cache_size": "Taille maximale du cache",
        "max_cache_age": "Durée maximale de conservation du cache",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Statistiques de"
            " cache</b>\n\n<emoji document_id=5783078953308655968>📊</emoji> <b>Taille"
            " totale du cache: {}</b>\n<emoji document_id=5974220038956124904>📥</emoji>"
            " <b>Messages enregistrés: {} pièce.</b>\n<emoji"
            " document_id=5974081491901091242>🕒</emoji> <b>Le plus ancien message:"
            " {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Cache nettoyé avec"
            " succès</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Heure non valide</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Restauration des"
            " messages</b>"
        ),
        "restored": (
            f"{rei} <b>Les messages ont été restaurés avec succès. Ils seront livrés"
            " dans le canal hikka-nekospy dans un proche avenir.</b>"
        ),
        "recent_maximum": "Temps maximum de récupération des messages en secondes",
    }

    strings_it = {
        "on": "attivato",
        "off": "disattivato",
        "state": f"{rei} <b>Modalità di tracciamento ora {{}}</b>",
        "spybl": (
            f"{rei} <b>Il gruppo corrente è stato aggiunto alla lista nera di"
            " tracciamento</b>"
        ),
        "spybl_removed": (
            f"{rei} <b>Il gruppo corrente è stato rimosso dalla lista nera di"
            " tracciamento</b>"
        ),
        "spybl_clear": f"{rei} <b>Lista nera di tracciamento ripulita</b>",
        "spywl": (
            f"{rei} <b>Il gruppo corrente è stato aggiunto alla lista bianca di"
            " tracciamento</b>"
        ),
        "spywl_removed": (
            f"{rei} <b>Il gruppo corrente è stato rimosso dalla lista bianca di"
            " tracciamento</b>"
        ),
        "spywl_clear": f"{rei} <b>Lista bianca di tracciamento ripulita</b>",
        "whitelist": (
            f"\n{rei} <b>Sto tracciando solo messaggi da utenti / gruppi:</b>\n{{}}"
        ),
        "always_track": (
            f"\n{rei} <b>Sto tracciando sempre messaggi da utenti / gruppi:</b>\n{{}}"
        ),
        "blacklist": f"\n{rei} <b>Ignoro messaggi da utenti / gruppi:</b>\n{{}}",
        "chat": f"{groups} <b>Sto tracciando i messaggi nei gruppi</b>\n",
        "pm": f"{pm} <b>Sto tracciando i messaggi nei messaggi privati</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> ha cancellato <a href="{message_url}">il'
            " messaggio</a> in privato. Contenuto:</b>\n{}"
        ),
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> ha eliminato <a'
            ' href="{message_url}">un messaggio</a> in privato. Contenuto:</b>\n{}'
        ),
        "deleted_chat": (
            '🗑 <b><a href="{message_url}">Un messaggio</a> nel gruppo <a'
            ' href="{}">{}</a> da <a href="{}">{}</a> è stato eliminato.'
            " Contenuto:</b>\n{}"
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> ha modificato <a href="{message_url}">un'
            " messaggio</a> in privato. Vecchio contenuto:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{message_url}">Un messaggio</a> nel gruppo <a'
            ' href="{}">{}</a> da <a href="{}">{}</a> è stato modificato. Vecchio'
            " contenuto:</b>\n{}"
        ),
        "mode_off": (
            f"{pm} <b>Non sto tenendo traccia dei messaggi"
            " </b><code>{}spymode</code>\n"
        ),
        "cfg_enable_pm": "Attiva modalità spia nei messaggi privati",
        "cfg_enable_groups": "Attiva modalità spia nei gruppi",
        "cfg_whitelist": "Lista dei gruppi da cui tenere traccia dei messaggi",
        "cfg_blacklist": "Lista dei gruppi da cui ignorare i messaggi",
        "cfg_always_track": (
            "Lista dei gruppi da cui tenere traccia dei messaggi,"
            " non importa quello che succede"
        ),
        "cfg_log_edits": "Salva i messaggi modificati",
        "cfg_ignore_inline": "Ignora i messaggi in modalità inline",
        "cfg_fw_protect": "Protezione contro floodwate ai messaggi inoltrati",
        "_cls_doc": "Salva i messaggi eliminati e/o modificati da utenti selezionati",
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> ti ha inviato un media"
            " che si autodistrugge</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Salvo"
            " i media che si autodistruggono</b>\n"
        ),
        "cfg_save_sd": "Salva i media che si autodistruggono",
        "max_cache_size": "Dimensione massima della directory cache",
        "max_cache_age": "Età massima dei record della cache",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Statistiche della"
            " cache</b>\n\n<emoji document_id=5783078953308655968>📊</emoji>"
            " <b>Dimensione totale della cache: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Messaggi salvati: {}"
            " pezzi.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>Messaggio"
            " più vecchio: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>La cache è stata"
            " pulita con successo</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Tempo non valido</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Sto ripristinando i"
            " messaggi</b>"
        ),
        "restored": (
            f"{rei} <b>I messaggi sono stati ripristinati con successo. Saranno"
            " recapitati al canale hikka-nekospy a breve.</b>"
        ),
        "recent_maximum": "Tempo massimo per ripristinare i messaggi in secondi",
    }

    strings_de = {
        "on": "Aktiviert",
        "off": "Deaktiviert",
        "state": f"{rei} <b>Der Tracking-Modus ist jetzt {{}}.</b>",
        "spybl": (
            f"{rei} <b>Der aktuelle Chat wurde zur Spionage-Blacklist hinzugefügt.</b>"
        ),
        "spybl_removed": (
            f"{rei} <b>Der aktuelle Chat wurde von der Spionage-Blacklist entfernt.</b>"
        ),
        "spybl_clear": f"{rei} <b>Die Spionage-Blacklist wurde geleert.</b>",
        "spywl": (
            f"{rei} <b>Der aktuelle Chat wurde zur Spionage-Whitelist hinzugefügt.</b>"
        ),
        "spywl_removed": (
            f"{rei} <b>Der aktuelle Chat wurde von der Spionage-Whitelist entfernt.</b>"
        ),
        "spywl_clear": f"{rei} <b>Die Spionage-Whitelist wurde geleert.</b>",
        "whitelist": f"\n{rei} <b>Ich beobachte nur Nachrichten von:</b>\n{{}}",
        "always_track": f"\n{rei} <b>Ich beobachte immer Nachrichten von:</b>\n{{}}",
        "blacklist": f"\n{rei} <b>Ich ignoriere Nachrichten von:</b>\n{{}}",
        "chat": f"{groups} <b>Ich beobachte Nachrichten in Gruppen.</b>\n",
        "pm": f"{pm} <b>Ich beobachte Nachrichten in privaten Nachrichten.</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> hat eine private <a'
            ' href="{message_url}">Nachricht</a> gelöscht. Inhalt:</b>\n{}'
        ),
        "deleted_chat": (
            '🗑 <b>Die <a href="{message_url}">Nachricht</a> im Chat <a href="{}">{}</a>'
            ' von <a href="{}">{}</a> wurde gelöscht. Inhalt:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> hat eine private <a'
            ' href="{message_url}">Nachricht</a> bearbeitet. Alte Nachricht:</b>\n{}'
        ),
        "edited_chat": (
            '🔏 <b>Die <a href="{message_url}">Nachricht</a> im Chat <a href="{}">{}</a>'
            ' von <a href="{}">{}</a> wurde bearbeitet. Alte Nachricht:</b>\n{}'
        ),
        "mode_off": (
            f"{pm} <b>Ich beobachte"
            " Nachrichten nicht mehr. </b><code>{}spymode</code>\n"
        ),
        "cfg_enable_pm": "Aktivieren Sie den Spionage-Modus in privaten Nachrichten",
        "cfg_enable_groups": "Aktivieren Sie den Spionage-Modus in Gruppen",
        "cfg_whitelist": (
            "Liste der Gruppen, von denen Nachrichten gespeichert werden sollen"
        ),
        "cfg_blacklist": (
            "Liste der Gruppen, von denen Nachrichten ignoriert werden sollen"
        ),
        "cfg_always_track": (
            "Liste der Gruppen, von denen immer Nachrichten verfolgt werden sollen,"
            " egal was passiert"
        ),
        "cfg_log_edits": "Gespeicherte bearbeitete Nachrichten",
        "cfg_ignore_inline": "Ignoriere Nachrichten aus Inline-Modus",
        "cfg_fw_protect": "Schutz vor Floodwässern beim Weiterleiten",
        "_cls_doc": (
            "Speichert gelöschte bearbeitete Nachrichten von ausgewählten Benutzern"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> hat Ihnen ein selbstzerstörendes"
            " Medium gesendet</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Speichere"
            " selbstzerstörende Medien</b>\n"
        ),
        "cfg_save_sd": "Speichern Sie selbstzerstörende Medien",
        "max_cache_size": "Maximale Größe des Zwischenspeicherverzeichnisses",
        "max_cache_age": "Maximale Altersgrenze für Zwischenspeicherdatensätze",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Zwischenspeicher"
            " Statistik</b>\n\n<emoji"
            " document_id=5783078953308655968>📊</emoji> <b>Gesamtgröße des"
            " Zwischenspeichers: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Gespeicherte Nachrichten: {}"
            " Stück.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>Älteste"
            " Nachricht: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Zwischenspeicher wurde"
            " erfolgreich bereinigt</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Ungültige Zeit</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Wiederherstellung"
            " von Nachrichten</b>"
        ),
        "restored": (
            f"{rei} <b>Nachrichten wurden erfolgreich wiederhergestellt. Sie werden"
            " bald an den hikka-nekospy-Kanal geliefert.</b>"
        ),
        "recent_maximum": (
            "Maximale Zeit, um Nachrichten in Sekunden wiederherzustellen"
        ),
    }

    strings_uz = {
        "on": "yoqildi",
        "off": "o'chirildi",
        "state": f"{rei} <b>Shu paytda spy rejimi {{}}</b>",
        "spybl": f"{rei} <b>Ushbu chat spay rejimining qora ro'yxatiga qo'shildi</b>",
        "spybl_removed": (
            f"{rei} <b>Ushbu chat spay rejimining qora ro'yxatidan olib tashlandi</b>"
        ),
        "spybl_clear": f"{rei} <b>Spay rejimining qora ro'yxati tozalandi</b>",
        "spywl": f"{rei} <b>Ushbu chat spay rejimining oq ro'yxatiga qo'shildi</b>",
        "spywl_removed": (
            f"{rei} <b>Ushbu chat spay rejimining oq ro'yxatidan olib tashlandi</b>"
        ),
        "spywl_clear": f"{rei} <b>Spay rejimining oq ro'yxati tozalandi</b>",
        "whitelist": f"\n{rei} <b>Faqat kelgan xabarlarni kuzatish</b>\n{{}}",
        "always_track": f"\n{rei} <b>Har doim kelgan xabarlarni kuzatish</b>\n{{}}",
        "blacklist": f"\n{rei} <b> kelgan xabarlarni o'chirish</b>\n{{}}",
        "chat": f"{groups} <b>Gruplardagi xabarlarimni kuzatish</b>\n",
        "pm": f"{pm} <b>Shaxsiy xabarlarimni kuzatish</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> shaxsiy <a href="{message_url}">xabarni</a>'
            " o'chirdi. Xabar:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{}">{}</a> guruhdan <a href="{}">{}</a> <a'
            ' href="{message_url}">xabarni</a> o\'chirdi. Xabar:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> shaxsiy <a href="{message_url}">xabarni</a>'
            " tahrirladi. Eski xabar:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{}">{}</a> guruhdan <a href="{}">{}</a> <a'
            ' href="{message_url}">xabarni</a> tahrirladi. Eski xabar:</b>\n{}'
        ),
        "mode_off": (
            f"{pm} <b>Xabarlarimni kuzatishni to'xtatdim</b><code>{{}}spymode</code>\n"
        ),
        "cfg_enable_pm": "Shaxsiy xabarlarimni kuzatishni yoqish",
        "cfg_enable_groups": "Guruh xabarlarimni kuzatishni yoqish",
        "cfg_whitelist": "Xabarlarni saqlash kerak bo'lgan suhbatlar ro'yxati",
        "cfg_blacklist": "Xabarlarni o'chirish kerak bo'lgan suhbatlar ro'yxati",
        "cfg_always_track": (
            "Nima bo'lishidan qat'i nazar, har doim xabarlarni kuzatib boradigan"
            " suhbatlar ro'yxati"
        ),
        "cfg_log_edits": "Saqlangan tahrirlangan xabarlarni",
        "cfg_ignore_inline": "Inline rejimidan kelgan xabarlarni o'chirish",
        "cfg_fw_protect": "Forwarding floodlardan himoyalash",
        "_cls_doc": (
            "Tanlangan foydalanuvchilardan kelgan va/yoki o'chirilgan yoki tahrirlangan"
            " xabarlarni saqlaydi"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> sizga o'chiriladigan media"
            " yubordi</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>O'z-o'zini yo'q"
            " qiladigan ommaviy axborot vositalarini saqlash</b>\n"
        ),
        "cfg_save_sd": "O'chiriladigan media saqlash",
        "max_cache_size": "Cache direktoriya hajmi",
        "max_cache_age": "Cache yozuvlari maksimal yoshi",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Cache"
            " statistikasi</b>\n\n<emoji document_id=5783078953308655968>📊</emoji>"
            " <b>Jami cache hajmi: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Saqlangan xabarlar soni: {}"
            " dona.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>Eldan"
            " o'tgan xabar: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Cache muvaffaqiyatli"
            " tozalandi</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Noto'g'ri vaqt</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Xabarlar"
            " tiklanmoqda</b>"
        ),
        "restored": (
            f"{rei} <b>Xabarlar muvaffaqiyatli tiklandi. Hikka-nekospy kanaliga tez"
            " orada yetaklanadi.</b>"
        ),
        "recent_maximum": "Vaqtini tiklash uchun maksimal vaqt saniyada",
    }

    strings_tr = {
        "on": "açık",
        "off": "kapalı",
        "state": f"{rei} <b>Şu anda gizli mod {{}}</b>",
        "spybl": f"{rei} <b>Bu sohbet gizli modun siyah listesine eklendi</b>",
        "spybl_removed": (
            f"{rei} <b>Bu sohbet gizli modun siyah listesinden kaldırıldı</b>"
        ),
        "spybl_clear": f"{rei} <b>Gizli modun siyah listesi temizlendi</b>",
        "spywl": f"{rei} <b>Bu sohbet gizli modun beyaz listesine eklendi</b>",
        "spywl_removed": (
            f"{rei} <b>Bu sohbet gizli modun beyaz listesinden kaldırıldı</b>"
        ),
        "spywl_clear": f"{rei} <b>Gizli modun beyaz listesi temizlendi</b>",
        "whitelist": f"\n{rei} <b>Sadece belirtilen gelen mesajları kaydet</b>\n{{}}",
        "always_track": (
            f"\n{rei} <b>Her zaman belirtilen gelen mesajları kaydet</b>\n{{}}"
        ),
        "blacklist": f"\n{rei} <b>Belirtilen gelen mesajları sil</b>\n{{}}",
        "chat": f"{groups} <b>Grup mesajlarımı kaydet</b>\n",
        "pm": f"{pm} <b>Özel mesajlarımı kaydet</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> özel <a href="{message_url}">mesajı</a> sildi.'
            " Mesaj:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{}">{}</a> guruptan <a href="{}">{}</a> <a'
            ' href="{message_url}">mesajı</a> sildi. Mesaj:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> özel <a href="{message_url}">mesajı</a>'
            " düzenledi. Eski mesaj:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{}">{}</a> guruptan <a href="{}">{}</a> <a'
            ' href="{message_url}">mesajı</a> düzenledi. Eski mesaj:</b>\n{}'
        ),
        "mode_off": (
            f"{pm} <b>Mesajlarımı kaydetmeyi kapattım</b><code>{{}}spymode</code>\n"
        ),
        "cfg_enable_pm": "Özel mesajlarımı kaydetmeyi aç",
        "cfg_enable_groups": "Grup mesajlarımı kaydetmeyi aç",
        "cfg_whitelist": "Kaydedilmesi gereken sohbetler listesi",
        "cfg_blacklist": "Silinmesi gereken sohbetler listesi",
        "cfg_always_track": (
            "Ne olursa olsun, iletileri her zaman izlenecek sohbetler listesi"
        ),
        "cfg_log_edits": "Kaydedilen düzenlenmiş mesajları",
        "cfg_ignore_inline": "Inline modundan gelen mesajları sil",
        "cfg_fw_protect": "Forwarding floodlarından korun",
        "_cls_doc": (
            "Belirtilen kullanıcıların/sohbetlerin silinmiş, düzenlenmiş veya"
            " kaydedilen mesajlarını kaydeder"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> sana silinebilir medya gönderdi</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Kendi kendini imha"
            " eden medyayı kaydetme</b>\n"
        ),
        "cfg_save_sd": "Silinebilir medyayı kaydet",
        "max_cache_size": "Önbellek dizininin maksimum boyutu",
        "max_cache_age": "Önbellek kayıtlarının maksimum yaşam süresi",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Önbellek"
            " istatistikleri</b>\n\n<emoji"
            " document_id=5783078953308655968>📊</emoji> <b>Toplam önbellek boyutu:"
            " {}</b>\n<emoji document_id=5974220038956124904>📥</emoji> <b>Kaydedilmiş"
            " mesajlar: {} adet.</b>\n<emoji"
            " document_id=5974081491901091242>🕒</emoji> <b>En eski mesaj:"
            " {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Önbellek başarıyla"
            " temizlendi</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Geçersiz zaman</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Mesajlar geri"
            " yükleniyor</b>"
        ),
        "restored": (
            f"{rei} <b>Mesajlar başarıyla geri yüklendi. Yakında"
            " hikka-nekospy kanalına gönderilecekler.</b>"
        ),
        "recent_maximum": "İlk kaç saniyelik mesajları geri yükleyeceğin",
    }

    strings_es = {
        "on": "activado",
        "off": "desactivado",
        "state": f"{rei} <b>El modo espía está actualmente {{}}</b>",
        "spybl": (
            f"{rei} <b>Este chat ha sido añadido a la lista negra del modo espía</b>"
        ),
        "spybl_removed": (
            f"{rei} <b>Este chat ha sido eliminado de la lista negra del modo espía</b>"
        ),
        "spybl_clear": f"{rei} <b>La lista negra del modo espía ha sido limpiada</b>",
        "spywl": (
            f"{rei} <b>Este chat ha sido añadido a la lista blanca del modo espía</b>"
        ),
        "spywl_removed": (
            f"{rei} <b>Este chat ha sido"
            " eliminado de la lista blanca del modo espía</b>"
        ),
        "spywl_clear": f"{rei} <b>La lista blanca del modo espía ha sido limpiada</b>",
        "whitelist": (
            f"\n{rei} <b>Guardar solo los mensajes de los especificados</b>\n{{}}"
        ),
        "always_track": (
            f"\n{rei} <b>Guardar siempre los mensajes de los especificados</b>\n{{}}"
        ),
        "blacklist": f"\n{rei} <b>Borrar los mensajes de los especificados</b>\n{{}}",
        "chat": (
            "<emoji document_id=603735566736530096   0>👥</emoji> <b>Guardar mis"
            " mensajes de grupo</b>\n"
        ),
        "pm": f"{pm} <b>Guardar mis mensajes privados</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> eliminó un <a href="{message_url}">mensaje</a>'
            " privado. Mensaje:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{}">{}</a> eliminó un <a href="{message_url}">mensaje</a> de'
            ' <a href="{}">{}</a> en el grupo. Mensaje:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> editó un <a href="{message_url}">mensaje</a>'
            " privado. Mensaje anterior:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{}">{}</a> editó un <a href="{message_url}">mensaje</a> de'
            ' <a href="{}">{}</a> en el grupo. Mensaje anterior:</b>\n{}'
        ),
        "mode_off": (
            f"{pm} <b>He desactivado el modo espía</b><code>{{}}spymode</code>\n"
        ),
        "cfg_enable_pm": "Guardar mensajes privados",
        "cfg_enable_groups": "Guardar mensajes de grupo",
        "cfg_whitelist": "Lista de Chats a guardar",
        "cfg_blacklist": "Lista de Сhats a borrar",
        "cfg_always_track": (
            "Lista de Chats para rastrear siempre los mensajes, pase lo que pase"
        ),
        "cfg_log_edits": "Guardar mensajes editados",
        "cfg_ignore_inline": "Ignorar mensajes de inline",
        "cfg_fw_protect": "Protegerse de forwarding floods",
        "_cls_doc": (
            "Guarda los mensajes borrados, editados o enviados por un usuario"
            " especificado"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> te ha enviado un mensaje de"
            " contenido que se puede borrar</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Guardar medios"
            " autodestructivos</b>\n"
        ),
        "cfg_save_sd": "Guardar contenido que se puede borrar",
        "max_cache_size": "Tamaño máximo del directorio de caché",
        "max_cache_age": "Edad máxima de los registros de caché",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Estadísticas de"
            " caché</b>\n\n<emoji document_id=5783078953308655968>📊</emoji> <b>Tamaño"
            " total de la caché: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Mensajes guardados: {}"
            " pcs.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>El más"
            " antiguo mensaje: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>La caché se ha purgado"
            " con éxito</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>tiempo no válido</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Restaurando"
            " mensajes</b>"
        ),
        "restored": (
            f"{rei} <b>Los mensajes se han restaurado con éxito. Se entregarán"
            " al canal hikka-nekospy pronto.</b>"
        ),
        "recent_maximum": "Tiempo máximo para restaurar mensajes de en segundos",
    }

    strings_kk = {
        "on": "қосылған",
        "off": "өшірілген",
        "state": f"{rei} <b>Шпион режимі ағымда {{}}</b>",
        "spybl": (
            f"{rei} <b>Бұл сөйлесу қорытынды шпион режимінің қара тізіміне қосылды</b>"
        ),
        "spybl_removed": (
            f"{rei} <b>Бұл сөйлесу қорытынды шпион режимінің қара тізімінен алынды</b>"
        ),
        "spybl_clear": f"{rei} <b>Шпион режимінің қара тізімін тазалау</b>",
        "spywl": (
            f"{rei} <b>Бұл сөйлесу қорытынды шпион режимінің ақ тізіміне қосылды</b>"
        ),
        "spywl_removed": (
            f"{rei} <b>Бұл сөйлесу қорытынды шпион режимінің ақ тізімінен алынды</b>"
        ),
        "spywl_clear": f"{rei} <b>Шпион режимінің ақ тізімін тазалау</b>",
        "whitelist": f"\n{rei} <b>Тек хабарламаларды қадағалау:</b>\n{{}}",
        "always_track": f"\n{rei} <b>Әрқашан хабарламаларды қадағалау:</b>\n{{}}",
        "blacklist": f"\n{rei} <b>Хабарламаларды елемеу:</b>\n{{}}",
        "chat": f"{groups} <b>Группадағы жазбаларымды сақтау</b>\n",
        "pm": f"{pm} <b>Жеке жазбаларымды сақтау</b>\n",
        "deleted_pm": (
            '🗑 <b><a href="{}">{}</a> жеке <a href="{message_url}">жазбағын</a> жойды.'
            " Жазба:</b>\n{}"
        ),
        "deleted_chat": (
            '🗑 <b><a href="{}">{}</a> <a href="{}">{}</a> топындағы'
            ' <a href="{message_url}">жазбағын</a> жойды. Жазба:</b>\n{}'
        ),
        "edited_pm": (
            '🔏 <b><a href="{}">{}</a> жеке <a href="{message_url}">жазбағын</a>'
            " өзгертті. Алдындағы жазба:</b>\n{}"
        ),
        "edited_chat": (
            '🔏 <b><a href="{}">{}</a> <a href="{}">{}</a> топындағы <a'
            ' href="{message_url}">жазбағын</a> өзгертті. Алдындағы жазба:</b>\n{}'
        ),
        "mode_off": f"{pm} <b>Спай режимін өшірдім</b><code>{{}}spymode</code>\n",
        "cfg_enable_pm": "Жеке хабарламаларды сақтау",
        "cfg_enable_groups": "Топтардың хабарламаларын сақтау",
        "cfg_whitelist": "Сақталатын топтар тізімі",
        "cfg_blacklist": "Жоюға мүмкіндік беретін топтар тізімі",
        "cfg_always_track": (
            "Еш нәрсеге қарамастан, әрқашан хабарламаларды бақылайтын топтар тізімі"
        ),
        "cfg_log_edits": "Өңделген хабарламаларды сақтау",
        "cfg_ignore_inline": "Inline режимінен келген хабарламаларды жою",
        "cfg_fw_protect": "Forwarding flood-тен қорғау",
        "_cls_doc": (
            "Көрсетілген пайдаланушы/топтардың жойылған, өңделген немесе сақталған"
            " хабарламаларын сақтайды"
        ),
        "sd_media": (
            "🔥 <b><a href='tg://user?id={}'>{}</a> сенің жойылған медиа-жазбаңың"
            " болуы мүмкін</b>"
        ),
        "save_sd": (
            "<emoji document_id=5420315771991497307>🔥</emoji> <b>Жойылған"
            " медиа-жазбаларды сақтау</b>\n"
        ),
        "cfg_save_sd": "Жойылған медиа-жазбаларды сақтау",
        "max_cache_size": "Кеш папкасының ең үлкен өлшемі",
        "max_cache_age": "Кеш сақталған запистерінің ең үлкен мерзімі",
        "stats": (
            "<emoji document_id=5431577498364158238>📊</emoji> <b>Кеш"
            " статистикасы</b>\n\n<emoji document_id=5783078953308655968>📊</emoji>"
            " <b>Кеш папкасының үлкен өлшемі: {}</b>\n<emoji"
            " document_id=5974220038956124904>📥</emoji> <b>Сақталған хабарламалар: {}"
            " түрлі.</b>\n<emoji document_id=5974081491901091242>🕒</emoji> <b>Ең ески"
            " хабарлама: {}</b>"
        ),
        "purged_cache": (
            "<emoji document_id=5974057212450967530>🧹</emoji> <b>Кеш тазартылды</b>"
        ),
        "invalid_time": (
            "<emoji document_id=5415918064782811950>😡</emoji> <b>Қате уақыт</b>"
        ),
        "restoring": (
            "<emoji document_id=5325731315004218660>🫥</emoji> <b>Хабарламаларды қалпына"
            " келтіру</b>"
        ),
        "restored": (
            f"{rei} <b>Хабарламалар сәтті қалпына келтірілді. Олар hikka-nekospy"
            " каналына жіберіледі.</b>"
        ),
        "recent_maximum": (
            "Хабарламаларды қалпына келтіру үшін ең үлкен уақыт секундтарда"
        ),
    }

    def __init__(self):
        self._tl_channel = None
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enable_pm",
                True,
                lambda: self.strings("cfg_enable_pm"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "enable_groups",
                False,
                lambda: self.strings("cfg_enable_groups"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                [],
                lambda: self.strings("cfg_whitelist"),
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "blacklist",
                [],
                lambda: self.strings("cfg_blacklist"),
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "always_track",
                [],
                lambda: self.strings("cfg_always_track"),
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "log_edits",
                True,
                lambda: self.strings("cfg_log_edits"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_inline",
                True,
                lambda: self.strings("cfg_ignore_inline"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "fw_protect",
                3.0,
                lambda: self.strings("cfg_fw_protect"),
                validator=loader.validators.Float(minimum=0.0),
            ),
            loader.ConfigValue(
                "save_sd",
                True,
                lambda: self.strings("cfg_save_sd"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "max_cache_size",
                1024 * 1024 * 1024,
                lambda: self.strings("max_cache_size"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "max_cache_age",
                7 * 24 * 60 * 60,
                lambda: self.strings("max_cache_age"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "recent_maximum",
                60 * 60,
                lambda: self.strings("recent_maximum"),
                validator=loader.validators.Integer(minimum=0),
            ),
        )

        self._queue = []
        self._next = 0
        self._threshold = 10
        self._flood_protect_sample = 60

    async def client_ready(self):
        channel, _ = await utils.asset_channel(
            self._client,
            "hikka-nekospy",
            "Deleted and edited messages will appear there",
            silent=True,
            invite_bot=True,
            avatar="https://pm1.narvii.com/6733/0e0380ca5cd7595de53f48c0ce541d3e2f2effc4v2_hq.jpg",
            _folder="hikka",
        )

        self._channel = int(f"-100{channel.id}")
        self._tl_channel = channel.id
        self.METHOD_MAP = {
            "photo": self.inline.bot.send_photo,
            "video": self.inline.bot.send_video,
            "voice": self.inline.bot.send_voice,
            "document": self.inline.bot.send_document,
        }

        self._cacher = CacheManager(self._client, self._db)
        self._gc.start()
        self._recent: PointerList = self.pointer("recents", [])

        if not __name__.startswith("hikka"):
            # License forbids you from removing this if branch btw
            raise loader.LoadError("Module is supported by Hikka only")

    @loader.loop(interval=15)
    async def _gc(self):
        self._cacher.gc(self.config["max_cache_age"], self.config["max_cache_size"])
        for item in self._recent:
            if item[0] + self.config["recent_maximum"] < time.time():
                self._recent.remove(item)

    @loader.loop(interval=0.1, autostart=True)
    async def _sender(self):
        if not self._queue or self._next > time.time():
            return

        item = self._queue.pop(0)
        await item
        self._next = int(time.time()) + self.config["fw_protect"]

    @staticmethod
    def _int(value: typing.Union[str, int], /) -> typing.Union[str, int]:
        return int(value) if str(value).isdigit() else value

    @property
    def blacklist(self):
        return list(
            map(
                self._int,
                self.config["blacklist"]
                + [777000, self._client.tg_id, self._tl_channel, self.inline.bot_id],
            )
        )

    @blacklist.setter
    def blacklist(self, value: list):
        self.config["blacklist"] = list(
            set(value)
            - {777000, self._client.tg_id, self._tl_channel, self.inline.bot_id}
        )

    @property
    def whitelist(self):
        return list(map(self._int, self.config["whitelist"]))

    @whitelist.setter
    def whitelist(self, value: list):
        self.config["whitelist"] = value

    @property
    def always_track(self):
        return list(map(self._int, self.config["always_track"]))

    @loader.command(
        ru_doc="Включить / выключить режим слежения",
        de_doc="Spionagemodus ein / ausschalten",
        uz_doc="Kuzatish rejimini yoqish / o'chirish",
        tr_doc="İzleme modunu aç / kapat",
        es_doc="Activar / desactivar el modo espía",
        kk_doc="Спай режимін қосу / жою",
        it_doc="Attiva / disattiva la modalità spia",
        fr_doc="Activer / désactiver le mode espion",
    )
    async def spymode(self, message: Message):
        """Toggle spymode"""
        await utils.answer(
            message,
            self.strings("state").format(
                self.strings("off" if self.get("state", False) else "on")
            ),
        )
        self.set("state", not self.get("state", False))

    @loader.command(
        ru_doc="Добавить / удалить чат из списка игнора",
        de_doc="Chat zur Ignorierliste hinzufügen / entfernen",
        uz_doc="Chatni qo'shish / olib tashlash",
        tr_doc="Sohbeti engelleme listesine ekle / kaldır",
        es_doc="Agregar / eliminar chat de la lista de ignorados",
        kk_doc="Чатты қосу / жою",
        it_doc="Aggiungi / rimuovi chat dalla lista di ignorati",
        fr_doc="Ajouter / supprimer le chat de la liste des ignorés",
    )
    async def spybl(self, message: Message):
        """Add / remove chat from blacklist"""
        chat = utils.get_chat_id(message)
        if chat in self.blacklist:
            self.blacklist = list(set(self.blacklist) - {chat})
            await utils.answer(message, self.strings("spybl_removed"))
        else:
            self.blacklist = list(set(self.blacklist) | {chat})
            await utils.answer(message, self.strings("spybl"))

    @loader.command(
        ru_doc="Очистить черный список",
        de_doc="Schwarze Liste leeren",
        uz_doc="Qora ro'yxatni tozalash",
        tr_doc="Siyah listeyi temizle",
        es_doc="Limpiar lista negra",
        kk_doc="Қара тізімді тазалау",
        it_doc="Cancella la lista nera",
        fr_doc="Effacer la liste noire",
    )
    async def spyblclear(self, message: Message):
        """Clear blacklist"""
        self.blacklist = []
        await utils.answer(message, self.strings("spybl_clear"))

    @loader.command(
        ru_doc="Добавить / удалить чат из белого списка",
        de_doc="Chat zur Whitelist hinzufügen / entfernen",
        uz_doc="Chatni o'qish ro'yxatiga qo'shish / olib tashlash",
        tr_doc="Sohbeti beyaz listeye ekle / kaldır",
        es_doc="Agregar / eliminar chat de la lista blanca",
        kk_doc="Чатты оқыш тізіміне қосу / жою",
        it_doc="Aggiungi / rimuovi chat dalla whitelist",
        fr_doc="Ajouter / supprimer le chat de la liste blanche",
    )
    async def spywl(self, message: Message):
        """Add / remove chat from whitelist"""
        chat = utils.get_chat_id(message)
        if chat in self.whitelist:
            self.whitelist = list(set(self.whitelist) - {chat})
            await utils.answer(message, self.strings("spywl_removed"))
        else:
            self.whitelist = list(set(self.whitelist) | {chat})
            await utils.answer(message, self.strings("spywl"))

    @loader.command(
        ru_doc="Очистить белый список",
        de_doc="Whitelist leeren",
        uz_doc="O'qish ro'yxatini tozalash",
        tr_doc="Beyaz listeyi temizle",
        es_doc="Limpiar lista blanca",
        kk_doc="Оқыш тізімін тазалау",
        it_doc="Cancella la whitelist",
        fr_doc="Effacer la liste blanche",
    )
    async def spywlclear(self, message: Message):
        """Clear whitelist"""
        self.whitelist = []
        await utils.answer(message, self.strings("spywl_clear"))

    async def _get_entities_list(self, entities: list) -> str:
        return "\n".join(
            [
                "\u0020\u2800\u0020\u2800<emoji"
                ' document_id=4971987363145188045>▫️</emoji> <b><a href="{}">{}</a></b>'
                .format(
                    utils.get_entity_url(await self._client.get_entity(x, exp=0)),
                    utils.escape_html(
                        get_display_name(await self._client.get_entity(x, exp=0))
                    ),
                )
                for x in entities
            ]
        )

    @loader.command(
        ru_doc="Показать текущую конфигурацию спай-мода",
        de_doc="Aktuelle Spy-Modus-Konfiguration anzeigen",
        uz_doc="Spy rejimining hozirgi konfiguratsiyasini ko'rsatish",
        tr_doc="Spy modu geçerli yapılandırmasını göster",
        es_doc="Mostrar la configuración actual del modo espía",
        kk_doc="Спай-режимдің ағымдағы конфигурациясын көрсету",
        it_doc="Mostra la configurazione attuale della modalità spia",
        fr_doc="Afficher la configuration actuelle du mode espion",
    )
    async def spyinfo(self, message: Message):
        """Show current spy mode configuration"""
        if not self.get("state"):
            await utils.answer(
                message, self.strings("mode_off").format(self.get_prefix())
            )
            return

        info = ""

        if self.config["save_sd"]:
            info += self.strings("save_sd")

        if self.config["enable_groups"]:
            info += self.strings("chat")

        if self.config["enable_pm"]:
            info += self.strings("pm")

        if self.whitelist:
            info += self.strings("whitelist").format(
                await self._get_entities_list(self.whitelist)
            )

        if self.config["blacklist"]:
            info += self.strings("blacklist").format(
                await self._get_entities_list(self.config["blacklist"])
            )

        if self.always_track:
            info += self.strings("always_track").format(
                await self._get_entities_list(self.always_track)
            )

        await utils.answer(message, info)

    async def _notify(self, msg_obj: dict, caption: str):
        caption = self.inline.sanitise_text(caption)
        assets = msg_obj["assets"]

        file = next((x for x in assets.values() if x), None)
        if not file:
            self._queue += [
                self.inline.bot.send_message(
                    self._channel,
                    caption,
                    disable_web_page_preview=True,
                )
            ]
            return

        if assets.get("sticker"):
            self._queue += [
                self.inline.bot.send_message(
                    self._channel,
                    caption + "\n\n&lt;sticker&gt;",
                    disable_web_page_preview=True,
                )
            ]
            return

        file["file_reference"] = bytes(bytearray.fromhex(file["file_reference"]))
        file = await self._client.download_file(
            (
                InputPhotoFileLocation
                if assets.get("photo") or assets.get("sticker")
                else InputDocumentFileLocation
            )(**file),
            bytes,
        )

        try:
            if not (
                ext := mimetypes.guess_extension(magic.from_buffer(file, mime=True))
            ):
                ext = ".bin"
        except Exception:
            ext = ".bin"

        file = io.BytesIO(file)
        file.name = f"restored{ext}"

        self._queue += [
            next(func for name, func in self.METHOD_MAP.items() if assets.get(name))(
                self._channel,
                file,
                caption=caption,
            )
        ]

    @loader.raw_handler(UpdateEditChannelMessage)
    async def channel_edit_handler(self, update: UpdateEditChannelMessage):
        self._recent.append(
            [
                int(time.time()),
                utils.get_chat_id(update.message),
                update.message.id,
                "edit",
            ]
        )

        if (
            not self.get("state", False)
            or update.message.out
            or (self.config["ignore_inline"] and update.message.via_bot_id)
        ):
            return

        msg_obj = await self._cacher.fetch_message(
            utils.get_chat_id(update.message),
            update.message.id,
        )
        if (
            msg_obj
            and msg_obj["is_chat"]
            and (
                int(msg_obj["chat_id"]) in self.always_track
                or int(msg_obj["sender_id"]) in self.always_track
                or (
                    self.config["log_edits"]
                    and self.config["enable_groups"]
                    and utils.get_chat_id(update.message) not in self.blacklist
                    and (
                        not self.whitelist
                        or utils.get_chat_id(update.message) in self.whitelist
                    )
                )
            )
            and not msg_obj["sender_bot"]
            and update.message.raw_text != utils.remove_html(msg_obj["text"])
        ):
            await self._notify(
                msg_obj,
                self.strings("edited_chat").format(
                    msg_obj["chat_url"],
                    msg_obj["chat_name"],
                    msg_obj["sender_url"],
                    msg_obj["sender_name"],
                    msg_obj["text"],
                    message_url=msg_obj["url"],
                ),
            )

        await self._cacher.store_message(update.message)

    def _should_capture(self, user_id: int, chat_id: int) -> bool:
        return (
            chat_id not in self.blacklist
            and user_id not in self.blacklist
            and (
                not self.whitelist
                or chat_id in self.whitelist
                or user_id in self.whitelist
            )
        )

    @loader.raw_handler(UpdateEditMessage)
    async def pm_edit_handler(self, update: UpdateEditMessage):
        self._recent.append(
            [
                int(time.time()),
                utils.get_chat_id(update.message),
                update.message.id,
                "edit",
            ]
        )

        if (
            not self.get("state", False)
            or update.message.out
            or (self.config["ignore_inline"] and update.message.via_bot_id)
        ):
            return

        msg_obj = await self._cacher.fetch_message(
            utils.get_chat_id(update.message),
            update.message.id,
        )

        sender_id, chat_id, is_chat = (
            int(msg_obj["sender_id"]),
            int(msg_obj["chat_id"]),
            msg_obj["is_chat"],
        )

        if (
            (
                sender_id in self.always_track
                or chat_id in self.always_track
                or (
                    (
                        self.config["log_edits"]
                        and self._should_capture(sender_id, chat_id)
                    )
                    and (
                        (
                            self.config["enable_pm"]
                            and not is_chat
                            or self.config["enable_groups"]
                            and is_chat
                        )
                    )
                )
            )
            and update.message.raw_text != utils.remove_html(msg_obj["text"])
            and not msg_obj["sender_bot"]
        ):
            await self._notify(
                msg_obj,
                (
                    self.strings("edited_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                    if is_chat
                    else self.strings("edited_pm").format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                ),
            )

        await self._cacher.store_message(update.message)

    @loader.raw_handler(UpdateDeleteMessages)
    async def pm_delete_handler(self, update: UpdateDeleteMessages):
        for message in update.messages:
            self._recent.append([int(time.time()), None, message, "del"])

        if not self.get("state", False):
            return

        for message in update.messages:
            if not (
                msg_obj := await self._cacher.fetch_message(
                    chat_id=None,
                    message_id=message,
                )
            ):
                continue

            sender_id, chat_id, is_chat = (
                int(msg_obj["sender_id"]),
                int(msg_obj["chat_id"]),
                msg_obj["is_chat"],
            )

            if (
                sender_id not in self.always_track
                and chat_id not in self.always_track
                and (
                    not self._should_capture(sender_id, chat_id)
                    or (self.config["ignore_inline"] and msg_obj["via_bot_id"])
                    or (not self.config["enable_groups"] and is_chat)
                    or (not self.config["enable_pm"] and not is_chat)
                )
                or msg_obj["sender_bot"]
            ):
                continue

            await self._notify(
                msg_obj,
                (
                    self.strings("deleted_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                    if is_chat
                    else self.strings("deleted_pm").format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                ),
            )

    def _is_always_track(self, user_id: int, chat_id: int) -> bool:
        return chat_id in self.always_track or user_id in self.always_track

    @loader.raw_handler(UpdateDeleteChannelMessages)
    async def channel_delete_handler(self, update: UpdateDeleteChannelMessages):
        for message in update.messages:
            self._recent.append([int(time.time()), update.channel_id, message, "del"])

        if not self.get("state", False):
            return

        for message in update.messages:
            if not message or not (
                msg_obj := await self._cacher.fetch_message(update.channel_id, message)
            ):
                continue

            sender_id, chat_id = (
                int(msg_obj["sender_id"]),
                int(msg_obj["chat_id"]),
            )

            if (
                self._is_always_track(sender_id, chat_id)
                or self.config["enable_groups"]
                and (
                    self._should_capture(sender_id, chat_id)
                    and (not self.config["ignore_inline"] or not msg_obj["via_bot_id"])
                    and not msg_obj["sender_bot"]
                )
            ):
                await self._notify(
                    msg_obj,
                    self.strings("deleted_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )

    @loader.watcher("in")
    async def watcher(self, message: Message):
        await self._cacher.store_message(message)
        if (
            not self.config["save_sd"]
            or not getattr(message, "media", False)
            or not getattr(message.media, "ttl_seconds", False)
        ):
            return

        media = io.BytesIO(await self.client.download_media(message.media, bytes))
        media.name = "sd.jpg" if message.photo else "sd.mp4"
        sender = await self.client.get_entity(message.sender_id, exp=0)
        await (
            self.inline.bot.send_photo if message.photo else self.inline.bot.send_video
        )(
            self._channel,
            media,
            caption=self.strings("sd_media").format(
                utils.get_entity_url(sender),
                utils.escape_html(get_display_name(sender)),
            ),
        )

    @loader.command()
    async def stat(self, message: Message):
        """Show stats for cached media and messages"""
        dirsize, messages_count, oldest_message = self._cacher.stats()
        await utils.answer(
            message,
            self.strings("stats").format(
                dirsize,
                messages_count,
                oldest_message,
            ),
        )

    @loader.command()
    async def purgecache(self, message: Message):
        """Empty cache storage from messages"""
        self._cacher.purge()
        self._recent.clear()
        await utils.answer(message, self.strings("purged_cache"))

    @loader.command()
    async def rest(self, message: Message):
        """[time] - Restore all deleted and edited messages from last 5 minutes"""
        args = utils.get_args_raw(message) or "5m"

        if args[-1].isdigit():
            args += "s"

        if args[-1] == "m":
            args = int(args[:-1]) * 60
        elif args[-1] == "s":
            args = int(args[:-1])
        elif args[-1] == "h":
            args = int(args[:-1]) * 60 * 60

        if args < 1:
            await utils.answer(message, self.strings("invalid_time"))
            return

        message = await utils.answer(message, self.strings("restoring"))
        for time_, chat_id, message_id, action in self._recent:
            if time.time() - time_ > args:
                continue

            if not (msg_obj := await self._cacher.fetch_message(chat_id, message_id)):
                continue

            if all(arg in msg_obj for arg in ("chat_url", "chat_name")):
                await self._notify(
                    msg_obj,
                    self.strings(
                        "deleted_chat" if action == "del" else "edited_chat"
                    ).format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )
            else:
                await self._notify(
                    msg_obj,
                    self.strings(
                        "deleted_pm" if action == "del" else "edited_pm"
                    ).format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )

        await utils.answer(message, self.strings("restored"))
