# scope: hikka_min 1.2.10
__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://i.imgur.com/MTkqvXX.jpeg
# scope: inline
# scope: hikka_only
# meta developer: @hikarimods

import logging
import time
from urllib.parse import quote_plus

import requests
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery

logger = logging.getLogger(__name__)


@loader.tds
class ShikimoriMod(loader.Module):
    """Shikimori API Wrapper"""

    strings = {
        "name": "Shikimori",
        "authorize": "🔓 Authorize",
        "code": "✍️ Code",
        "code_input": "✍️ Redirect url after auth",
        "auth": (
            '🔓 <b>Shikimori authorization:</b>\n\n1. Click "🔓 Authorize"\n2. Click'
            ' "Allow"\n3. Copy redirect url, and enter it in "✍️ Code"'
        ),
        "my_animes": (
            "🐙 <b>My humble anime <a"
            ' href="https://shikimori.one/{}/list/anime/order-by/name">list</a>:</b>\n\n{}'
        ),
        "no_args": "🚫 <b>No arguments specified</b>",
        "added": "❤️ <b>Anime {} added to planned</b>",
        "auth_successful": "👍 <b>Authorized! Check module help for new commands</b>",
        "planned": "🕐 Planned",
        "watching": "🎬 Watching",
        "rewatching": "🔄 Re-watching",
        "completed": "✅ Completed",
        "on_hold": "🗓 Holded",
        "dropped": "🚫 Dropped",
        "interact": (
            '📼 <b>Interacting with <a href="https://shikimori.one{}">{}</a></b>'
        ),
        "state_changed": "Anime state changed to {}",
        "delete": "🗑 Delete",
        "no_status": "🔘 Change status",
        "error": "🚫 Error",
        "success": "✅ Success",
    }

    strings_ru = {
        "authorize": "🔓 Авторизоваться",
        "code": "✍️ Код",
        "code_input": "✍️ Ссылка, на которую тебя перебросило после авторизации",
        "auth": (
            '🔓 <b>Авторизация на Shikimori:</b>\n\n1. Нажми "🔓 Авторизоваться"\n2.'
            ' Нажми "Разрешить"\n3. Скопируй ссылку, на которую тебя перекинет, и введи'
            ' ее в "✍️ Код"'
        ),
        "my_animes": (
            "🐙 <b>Мой скромный <a"
            ' href="https://shikimori.one/{}/list/anime/order-by/name">список</a>'
            " аниме:</b>\n\n{}"
        ),
        "no_args": "🚫 <b>Аргументы не указаны</b>",
        "added": "❤️ <b>Аниме {} добавлено в отложенные</b>",
        "auth_successful": (
            "👍 <b>Авторизован! Смотри помощь модуля, там новые команды</b>"
        ),
        "planned": "🕐 Запланировано",
        "watching": "🎬 Смотрю",
        "rewatching": "🔄 Пересматриваю",
        "completed": "✅ Просмотрено",
        "on_hold": "🗓 Отложено",
        "dropped": "🚫 Заброшено",
        "interact": (
            '📼 <b>Взаимодействие с <a href="https://shikimori.one{}">{}</a></b>'
        ),
        "state_changed": "Состояние аниме изменено на {}",
        "delete": "🗑 Удалить",
        "no_status": "🔘 Изменить статус",
        "error": "🚫 Ошибка",
        "success": "✅ Успешно",
    }

    async def client_ready(self, client, db):
        self._shiki_me = None  # will be set later
        self._rates_cache = {}

    async def _search(
        self,
        query: str,
        limit: int = 10,
        no_retry: bool = False,
    ) -> dict:
        result = await utils.run_sync(
            requests.get,
            f"https://shikimori.one/api/animes?search={quote_plus(query)}&limit={limit}",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._search(query, limit, no_retry=True)

        result = result.json()
        rates = {
            i["anime"]["id"]: i
            for i in await self._get_rates()
            if "anime" in i and "id" in i["anime"]
        }

        for i, item in enumerate(result):
            if item["id"] in rates:
                result[i]["status"] = rates[item["id"]]["status"]
                result[i]["episodes_seen"] = rates[item["id"]]["episodes"]
            else:
                if "status" in result[i]:
                    del result[i]["status"]

        return result

    def _get_anime_message(self, anime: dict) -> str:
        return (
            f'🐱 <b>{utils.escape_html(anime["russian"])}</b>\n'
            f'🌍 <b>URL:</b> https://shikimori.one{anime["url"]}\n'
            f'🧮 <b>Type:</b> {anime["kind"]}\n'
            f'📺 <b>Episodes: </b>{anime.get("episodes_seen", 0)}/{anime["episodes"]}\n'
            f'📅 <b>Released: </b>{anime["released_on"]}'
        )

    def _get_anime_markup(self, anime: dict) -> str:
        return [
            [
                {
                    "text": self.strings(anime.get("status", "no_status")),
                    "callback": self._anime_interact,
                    "args": (anime,),
                }
            ],
        ] + (
            [
                [
                    {
                        "text": "➖ Episode",
                        "callback": self._change_episodes_quantity,
                        "args": (anime, -1),
                    },
                    {
                        "text": "➕ Episode",
                        "callback": self._change_episodes_quantity,
                        "args": (anime, 1),
                    },
                ]
            ]
            if anime.get("status", "no_status") not in {"completed", "no_status"}
            else []
        )

    async def anime_inline_handler(self, query: InlineQuery):
        """<query> - Search Shikimori"""
        if not query.args:
            return await query.e400()

        result = []
        for anime in await self._search(query.args):
            result += [
                {
                    "title": anime["name"],
                    "thumb": f'https://shikimori.one/{anime["image"]["preview"]}',
                    "message": self._get_anime_message(anime),
                    "reply_markup": self._get_anime_markup(anime),
                }
            ]

        return result

    async def shikicmd(self, message: Message):
        """<anime> - Search anime and return best match as form"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        anime = (await self._search(args, limit=1))[0]

        await self.inline.form(
            message=message,
            text=self._get_anime_message(anime),
            reply_markup=self._get_anime_markup(anime),
            photo=f'https://shikimori.one/{anime["image"]["original"]}',
        )

    async def _change_episodes_quantity(
        self,
        call: InlineCall,
        anime: dict,
        diff: int,
        no_retry: bool = False,
    ):
        if not self._shiki_me:
            self._shiki_me = await self._get_me()

        self._rates_cache = {}
        await self._get_rates()

        rate = None

        for i, local_rate in enumerate(self._rates_cache["rates"]):
            if local_rate["anime"]["id"] == anime["id"]:
                rate = local_rate
                self._rates_cache["rates"][i]["episodes"] += diff

        if not rate:
            logger.error("Can't find rate by anime id")
            return False

        payload = {
            "user_rate[chapters]": rate.get("chapters", 0),
            "user_rate[episodes]": rate.get("episodes", 0) + diff,
            "user_rate[rewatches]": rate.get("rewatches", 0),
            "user_rate[volumes]": rate.get("volumes", 0),
            "user_rate[score]": rate.get("score", 0),
            "user_rate[status]": rate.get("status", None),
            "user_rate[text]": rate.get("text", None),
        }

        result = await utils.run_sync(
            requests.put,
            f"https://shikimori.one/api/v2/user_rates/{rate['id']}",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
            data=payload,
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._change_episodes_quantity(
                call, anime, diff, no_retry=True
            )

        if not str(result.status_code).startswith("2"):
            logger.error(result.text)
            await call.answer(self.strings("error"))
            return

        if "episodes_seen" in anime:
            anime["episodes_seen"] += diff
        else:
            anime["episodes_seen"] = 0 if diff < 0 else 1

        await call.answer(self.strings("success"))
        await call.edit(self._get_anime_message(anime), self._get_anime_markup(anime))

    async def _anime_interact(
        self,
        call: InlineCall,
        anime: dict,
    ):
        await call.edit(
            self.strings("interact").format(
                anime["url"],
                utils.escape_html(anime["russian"]),
            ),
            reply_markup=utils.chunks(
                [
                    {
                        "text": self.strings(status),
                        "callback": self._change_anime_state,
                        "args": (anime, status),
                    }
                    for status in {
                        "planned",
                        "watching",
                        "rewatching",
                        "completed",
                        "on_hold",
                        "dropped",
                    }
                ],
                2,
            )
            + [
                [
                    {
                        "text": self.strings("delete"),
                        "callback": self._delete_anime_rate,
                        "args": (anime,),
                    }
                ]
            ],
        )

    async def _change_anime_state(self, call: InlineCall, anime: dict, state: str):
        await self._change_anime_state_api(anime["id"], state)

        # We can do this locally to prevent API Flood
        for i, item in enumerate(self._rates_cache["rates"]):
            if item["anime"]["id"] == anime["id"]:
                self._rates_cache["rates"][i]["status"] = state

        anime["status"] = state

        await call.answer(self.strings("state_changed").format(self.strings(state)))
        await call.edit(self._get_anime_message(anime), self._get_anime_markup(anime))

    async def _delete_anime_rate(self, call: InlineCall, anime: dict):
        await self._delete_anime_rate_api(anime["id"])

        # We can do this locally to prevent API Flood
        for i, item in enumerate(self._rates_cache["rates"]):
            if item["anime"]["id"] == anime["id"]:
                del self._rates_cache["rates"][i]

        del anime["status"]

        await call.answer(self.strings("state_changed").format(self.strings("delete")))
        await call.edit(self._get_anime_message(anime), self._get_anime_markup(anime))

    async def shikiauthcmd(self, message: Message):
        """Authorize on Shikimori.one"""
        await self.inline.form(
            message=message,
            text=self.strings("auth"),
            reply_markup=[
                {
                    "text": self.strings("authorize"),
                    "url": r"https://shikimori.one/oauth/authorize?client_id=-wQ_BBnF3GOvhRi6Z6pS60sYzY5ge7Y92aBtCEYSbgc&redirect_uri=https%3A%2F%2Fmods.hikariatama.ru&response_type=code&scope=user_rates",
                },
                {
                    "text": self.strings("code"),
                    "input": self.strings("code_input"),
                    "handler": self._proceed_auth,
                },
            ],
        )

    async def _request_token(self, code: str):
        result = (
            await utils.run_sync(
                requests.post,
                "https://shikimori.one/oauth/token",
                headers={"User-Agent": "Hikka"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "-wQ_BBnF3GOvhRi6Z6pS60sYzY5ge7Y92aBtCEYSbgc",
                    "client_secret": "mRESsAiJxzuOPMCkrgRvbdnMfLycZAAt_YDgD4hMDyA",
                    "code": code,
                    "redirect_uri": "https://mods.hikariatama.ru",
                },
            )
        ).json()

        self.set("token", result["access_token"])
        self.set("refresh_token", result["refresh_token"])

    async def _refresh_token(self):
        result = (
            await utils.run_sync(
                requests.post,
                "https://shikimori.one/oauth/token",
                headers={"User-Agent": "Hikka"},
                data={
                    "grant_type": "refresh_token",
                    "client_id": "-wQ_BBnF3GOvhRi6Z6pS60sYzY5ge7Y92aBtCEYSbgc",
                    "client_secret": "mRESsAiJxzuOPMCkrgRvbdnMfLycZAAt_YDgD4hMDyA",
                    "refresh_token": self.get("refresh_token"),
                },
            )
        ).json()
        self.set("token", result["access_token"])
        self.set("refresh_token", result["refresh_token"])

    async def _change_anime_state_api(
        self,
        uid: int,
        state: str,
        kind: str = "Anime",
        no_retry: bool = False,
    ) -> bool:
        if not self._shiki_me:
            self._shiki_me = await self._get_me()

        payload = {
            "user_rate[status]": state,
            "user_rate[target_id]": uid,
            "user_rate[target_type]": kind,
            "user_rate[user_id]": self._shiki_me["id"],
            "user_rate[score]": 0,
        }

        result = await utils.run_sync(
            requests.post,
            "https://shikimori.one/api/v2/user_rates",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
            data=payload,
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._change_anime_state_api(uid, state, kind, no_retry=True)

        if not str(result.status_code).startswith("2"):
            logger.error(result.text)

        return str(result.status_code).startswith("2")

    async def _delete_anime_rate_api(
        self,
        uid: int,
        no_retry: bool = False,
    ) -> bool:
        if not self._shiki_me:
            self._shiki_me = await self._get_me()

        self._rates_cache = {}
        await self._get_rates()

        rate_id = None

        for rate in self._rates_cache["rates"]:
            if rate["anime"]["id"] == uid:
                rate_id = rate["id"]

        if not rate_id:
            logger.error("Can't find rate by anime id")
            return False

        result = await utils.run_sync(
            requests.delete,
            f"https://shikimori.one/api/v2/user_rates/{rate_id}",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._delete_anime_rate_api(uid, no_retry=True)

        if not str(result.status_code).startswith("2"):
            logger.error(result.text)
            logger.error(result.status_code)

        return str(result.status_code).startswith("2")

    async def _get_me(self, no_retry: bool = False) -> dict:
        result = await utils.run_sync(
            requests.get,
            "https://shikimori.one/api/users/whoami",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._get_me(no_retry=True)

        return result.json()

    async def myshikicmd(self, message: Message):
        """Show watched animes from Shikimori.one"""
        rates = await self._get_rates()  # do this early so the self._shiki_me is set
        await utils.answer(
            message,
            self.strings("my_animes").format(
                self._shiki_me["nickname"],
                "\n".join(
                    [
                        f"<a href=\"https://shikimori.one{rate['anime']['url']}\">▫️</a>"
                        f" <i>{utils.escape_html(rate['anime'].get('russian', rate['anime']['name']))}</i>"
                        for rate in rates
                        if rate["status"] == "completed"
                    ]
                ),
            ),
        )

    async def aniaddcmd(self, message: Message):
        """<name> - Add best search match to the list of planned animes"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        anime = (await self._search(args, 1))[0]
        await self._change_anime_state_api(anime["id"], "planned")
        await utils.answer(
            message,
            self.strings("added").format(utils.escape_html(anime["russian"])),
        )

    async def _get_rates(self, no_retry: bool = False) -> list:
        if self._rates_cache and self._rates_cache["timeout"] > time.time():
            return self._rates_cache["rates"]

        if not self._shiki_me:
            self._shiki_me = await self._get_me()

        result = await utils.run_sync(
            requests.get,
            f"https://shikimori.one/api/users/{self._shiki_me['id']}/anime_rates?limit=5000",
            headers={
                "User-Agent": "Hikka",
                "Authorization": f"Bearer {self.get('token')}",
            },
        )

        if result.status_code == 401:
            if no_retry:
                logger.error("Can't refresh token")
                return {}

            await self._refresh_token()
            return await self._get_rates(no_retry=True)

        self._rates_cache = {"timeout": time.time() + 5 * 60, "rates": result.json()}

        return result.json()

    async def _proceed_auth(self, call: InlineCall, query: str):
        try:
            code = query.split("?code=")[1]
        except Exception:
            return

        await self._request_token(code)
        await call.edit(self.strings("auth_successful"))
