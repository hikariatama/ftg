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

# meta title: PM->BL
# meta pic: https://img.icons8.com/external-dreamcreateicons-flat-dreamcreateicons/512/000000/external-death-halloween-dreamcreateicons-flat-dreamcreateicons.png
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.1.14

import asyncio
import logging
import time
import contextlib
from typing import Union

from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
from telethon.tl.types import Message, PeerUser, User
from telethon.utils import get_display_name, get_peer_id

from .. import loader, utils

logger = logging.getLogger(__name__)


def format_(state: Union[bool, None]) -> str:
    if state is None:
        return "❔"

    return "✅" if state else "🚫 Not"


@loader.tds
class PMBLMod(loader.Module):
    """Bans and reports incoming messages from unknown users"""

    strings = {
        "name": "PMBL",
        "state": "⚔️ <b>PM->BL is now {}</b>\n<i>Report spam? - {}\nDelete dialog? - {}</i>",
        "args": "ℹ️ <b>Example usage: </b><code>.pmblsett 0 0</code>",
        "args_pmban": "ℹ️ <b>Example usage: </b><code>.pmbanlast 5</code>",
        "config": "😶‍🌫️ <b>Yeiks! Config saved</b>\n<i>Report spam? - {}\nDelete dialog? - {}</i>",
        "banned": "😊 <b>Hewwo •ᴗ•</b>\nI'm Kirito, the <b>guardian</b> of this account and you are <b>not approved</b>! You can contact my owner <b>in chat</b>, if you need help.\n<b>Sorry, but I need to ban you in terms of security</b> 😥",
        "removing": "😶‍🌫️ <b>Removing {} last dialogs...</b>",
        "removed": "😶‍🌫️ <b>Removed {} last dialogs!</b>",
        "user_not_specified": "🚫 <b>You haven't specified user</b>",
        "approved": '😶‍🌫️ <b><a href="tg://user?id={}">{}</a> approved in pm</b>',
        "banned_log": '👮 <b>I banned <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Contact</b>\n<b>{} Started by you</b>\n<b>{} Active conversation</b>\n\n<b>✊ Actions</b>\n\n<b>{} Reported spam</b>\n<b>{} Deleted dialog</b>\n<b>{} Banned</b>\n\n<b>ℹ️ Message</b>\n<code>{}</code>',
        "hello": "😊 <b>Hewwo!</b>\n<b>I'm Kirito</b> - your personal personal messages guardian. I will block everyone, who's trying to intrude you.\n\nUse <code>.pmbl</code> to enable protection, <code>.pmblsett</code> to configure it and <code>.pmbanlast</code> if you've already been pm-raided.\n\n<i>Glad to be your safeguard!</i>",
    }

    strings_ru = {
        "hello": "😊 <b>Приветики!</b>\n<b>Я Кирито</b> - охранник твоих личных сообщений. Я буду блокировать всех захватчиков.\n\nИспользуй<code>.pmbl</code> для включения защиты, <code>.pmblsett</code> для ее настройки и <code>.pmbanlast</code> если уже слишком поздно, и твои лс атаковали.\n\n<i>Рад быть твоим телохранителем!</i>",
        "state": "⚔️ <b>Текущее состояние PM->BL: {}</b>\n<i>Сообщать о спаме? - {}\nУдалять диалог? - {}</i>",
        "args": "ℹ️ <b>Пример: </b><code>.pmblsett 0 0</code>",
        "args_pmban": "ℹ️ <b>Пример: </b><code>.pmbanlast 5</code>",
        "config": "😶‍🌫️ <b>Йей! Конфиг сохранен</b>\n<i>Сообщать о спаме? - {}\nУдалять диалог? - {}</i>",
        "banned": "🤵 <b>Пожалуйста, подождите •ᴗ•</b>\nЯ <b>защитник</b> этого аккаунта, и вы <b>не подтверждены</b>! Вы можете связаться с моим владельцем <b>в чате</b>, если вам нужна помощь.\n<b>Сожалею, но я должен забанить вас с целью соблюдения безопасности</b> 😥",
        "removing": "😶‍🌫️ <b>Удаляю {} последних диалогов...</b>",
        "removed": "😶‍🌫️ <b>Удалил {} последних диалогов!</b>",
        "user_not_specified": "🚫 <b>Укажи пользователя</b>",
        "_cmd_doc_pmbl": "Выключить\\Включить защиту",
        "_cmd_doc_pmblsett": "<сообщать о спаме?> <удалять диалог?> - Настроить защиту - все параметры в формате 1/0",
        "_cmd_doc_pmbanlast": "<количество> - Забанить и удалить n последних диалогов с пользователями",
        "_cmd_doc_allowpm": "<пользователь> - Разрешить пользователю писать тебе в ЛС",
        "_cls_doc": "Блокирует и репортит входящие сообщения от незнакомцев",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ignore_contacts",
                True,
                lambda: "Ignore contacts?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_active",
                True,
                lambda: "Ignore peers, where you participated?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "active_threshold",
                5,
                lambda: "What number of your messages is required to trust peer",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "custom_message",
                doc=lambda: "Custom message to notify untrusted peers. Leave empty for default one",
            ),
            loader.ConfigValue(
                "photo_url",
                "https://kartinkin.net/uploads/posts/2021-07/1625528600_10-kartinkin-com-p-anime-kirito-anime-krasivo-11.jpg",
                lambda: "Photo, which is sent along with banned notification",
                validator=loader.validators.Link(),
            ),
            loader.ConfigValue(
                "use_maid",
                False,
                lambda: "Whether to replace normal Kirito with maid-Kirito",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._whitelist = self.get("whitelist", [])
        self._ratelimit = []
        self._ratelimit_timeout = 5 * 60
        self._ratelimit_threshold = 10
        if not self.get("ignore_qs", False):
            await self.inline.bot.send_photo(
                self._tg_id,
                photo=r"https://static.zerochan.net/Kirito.%28GGO%29.full.2814614.jpg",
                caption=self.strings("hello"),
                parse_mode="HTML",
            )

            self.set("ignore_qs", True)

    async def pmblcmd(self, message: Message):
        """Toggle PMBL"""
        current = self.get("state", False)
        new = not current
        self.set("state", new)
        await utils.answer(
            message,
            self.strings("state").format(
                "on" if new else "off",
                "yes" if self.get("spam", False) else "no",
                "yes" if self.get("delete", False) else "no",
            ),
        )

    async def pmblsettcmd(self, message: Message):
        """<report spam?> <delete dialog?> - Configure PMBL - all params are 1/0"""
        args = utils.get_args(message)
        if not args or len(args) != 2 or any(not _.isdigit() for _ in args):
            await utils.answer(message, self.strings("args"))
            return

        spam, delete = list(map(int, args))
        self.set("spam", spam)
        self.set("delete", delete)
        await utils.answer(
            message,
            self.strings("config").format(
                "yes" if spam else "no",
                "yes" if delete else "no",
            ),
        )

    async def pmbanlastcmd(self, message: Message):
        """<number> - Ban and delete dialogs with n most new users"""
        n = utils.get_args_raw(message)
        if not n or not n.isdigit():
            await utils.answer(message, self.strings("args_pmban"))
            return

        n = int(n)

        await utils.answer(message, self.strings("removing").format(n))

        dialogs = []
        async for dialog in self._client.iter_dialogs(ignore_pinned=True):
            try:
                if not isinstance(dialog.message.peer_id, PeerUser):
                    continue
            except AttributeError:
                continue

            m = (
                await self._client.get_messages(
                    dialog.message.peer_id,
                    limit=1,
                    reverse=True,
                )
            )[0]

            dialogs += [
                (
                    get_peer_id(dialog.message.peer_id),
                    int(time.mktime(m.date.timetuple())),
                )
            ]

        dialogs.sort(key=lambda x: x[1])
        to_ban = [d for d, _ in dialogs[::-1][:n]]

        for d in to_ban:
            await self._client(BlockRequest(id=d))

            await self._client(DeleteHistoryRequest(peer=d, just_clear=True, max_id=0))

        await utils.answer(message, self.strings("removed").format(n))

    def _approve(self, user: int, reason: str = "unknown"):
        self._whitelist += [user]
        self._whitelist = list(set(self._whitelist))
        self.set("whitelist", self._whitelist)
        logger.info(f"User approved in pm {user}, filter: {reason}")
        return

    async def allowpmcmd(self, message: Message):
        """<reply or user> - Allow user to pm you"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        user = None

        try:
            user = await self._client.get_entity(args)
        except Exception:
            with contextlib.suppress(Exception):
                user = await self._client.get_entity(reply.sender_id) if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(message, self.strings("user_not_specified"))
                return

            user = chat

        self._approve(user.id, "manual_approve")
        await utils.answer(
            message, self.strings("approved").format(user.id, get_display_name(user))
        )

    async def watcher(self, message: Message):
        if (
            getattr(message, "out", False)
            or not isinstance(message, Message)
            or not isinstance(message.peer_id, PeerUser)
            or not self.get("state", False)
            or utils.get_chat_id(message)
            in {
                1271266957,  # @replies
                777000,  # Telegram Notifications
                self._tg_id,  # Self
            }
        ):
            return

        cid = utils.get_chat_id(message)
        if cid in self._whitelist:
            return

        contact, started_by_you, active_peer = None, None, None

        with contextlib.suppress(ValueError):
            entity = await self._client.get_entity(message.peer_id)

            if entity.bot:
                return self._approve(cid, "bot")

            if self.config["ignore_contacts"]:
                if entity.contact:
                    return self._approve(cid, "ignore_contacts")
                else:
                    contact = False

        first_message = (
            await self._client.get_messages(
                message.peer_id,
                limit=1,
                reverse=True,
            )
        )[0]

        if (
            getattr(message, "raw_text", False)
            and first_message.sender_id == self._tg_id
        ):
            return self._approve(cid, "started_by_you")
        else:
            started_by_you = False

        if self.config["ignore_active"]:
            q = 0

            async for msg in self._client.iter_messages(message.peer_id, limit=200):
                if msg.sender_id == self._tg_id:
                    q += 1

                if q >= self.config["active_threshold"]:
                    return self._approve(cid, "active_threshold")

            active_peer = False

        self._ratelimit = list(
            filter(
                lambda x: x + self._ratelimit_timeout < time.time(),
                self._ratelimit,
            )
        )

        if len(self._ratelimit) < self._ratelimit_threshold:
            try:
                await self._client.send_file(
                    message.peer_id,
                    self.config["photo_url"]
                    if not int(self.config["use_maid"])
                    else "http://img0.reactor.cc/pics/post/full/Kirito-Sword-Art-Online-Anime-Maid-2200117.jpeg",
                    caption=self.config["custom_message"] or self.strings("banned"),
                )
            except Exception:
                await utils.answer(
                    message,
                    self.config["custom_message"] or self.strings("banned"),
                )

            self._ratelimit += [round(time.time())]

            try:
                peer = await self._client.get_entity(message.peer_id)
            except ValueError:
                await asyncio.sleep(1)
                peer = await self._client.get_entity(message.peer_id)

            await self.inline.bot.send_message(
                (await self._client.get_me()).id,
                self.strings("banned_log").format(
                    peer.id,
                    utils.escape_html(peer.first_name),
                    format_(contact),
                    format_(started_by_you),
                    format_(active_peer),
                    format_(self.get("spam", False)),
                    format_(self.get("delete", False)),
                    format_(True),
                    utils.escape_html(message.raw_text[:3000]),
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

        await self._client(BlockRequest(id=cid))

        if self.get("spam", False):
            await self._client(ReportSpamRequest(peer=cid))

        if self.get("delete", False):
            await self._client(
                DeleteHistoryRequest(peer=cid, just_clear=True, max_id=0)
            )

        self._approve(cid, "banned")

        logger.warning(f"Intruder punished: {cid}")
