#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/tidal_icon.png
# meta banner: https://mods.hikariatama.ru/badges/tidal.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10
# requires: tidalapi

import asyncio
from .. import loader, utils
from ..inline.types import InlineCall
from telethon.tl.types import Message
import logging
import tidalapi

logger = logging.getLogger(__name__)


@loader.tds
class TidalMod(loader.Module):
    """API wrapper over TIDAL Hi-Fi music streaming service"""

    strings = {
        "name": "Tidal",
        "args": "🚫 <b>Specify search query</b>",
        "404": "🚫 <b>No results found</b>",
        "oauth": "🔑 <b>Login to TIDAL</b>\n\n<i>This link will expire in 5 minutes</i>",
        "oauth_btn": "🔑 Login",
        "success": "✅ <b>Successfully logged in!</b>",
        "error": "🚫 <b>Error logging in</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Searching...</b>",
        "tidal_like_btn": "🖤 Like",
        "tidal_dislike_btn": "💔 Dislike",
        "auth_first": "🚫 <b>You need to login first</b>",
    }

    strings_ru = {
        "args": "🚫 <b>Укажите поисковый запрос</b>",
        "404": "🚫 <b>Ничего не найдено</b>",
        "oauth": (
            "🔑 <b>Авторизуйтесь в TIDAL</b>\n\n<i>Эта ссылка будет действительна в"
            " течение 5 минут</i>"
        ),
        "oauth_btn": "🔑 Авторизоваться",
        "success": "✅ <b>Успешно авторизованы!</b>",
        "error": "🚫 <b>Ошибка авторизации</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Ищем...</b>",
        "tidal_like_btn": "🖤 Нравится",
        "tidal_dislike_btn": "💔 Не нравится",
        "auth_first": "🚫 <b>Сначала нужно авторизоваться</b>",
    }

    strings_de = {
        "args": "🚫 <b>Gib einen Suchbegriff an</b>",
        "404": "🚫 <b>Nichts gefunden</b>",
        "oauth": (
            "🔑 <b>Logge dich bei TIDAL ein</b>\n\n<i>Dieser Link ist 5 Minuten lang"
            " gültig</i>"
        ),
        "oauth_btn": "🔑 Einloggen",
        "success": "✅ <b>Erfolgreich eingeloggt!</b>",
        "error": "🚫 <b>Fehler beim Einloggen</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Suche...</b>",
        "tidal_like_btn": "🖤 Gefällt mir",
        "tidal_dislike_btn": "💔 Gefällt mir nicht",
        "auth_first": "🚫 <b>Du musst dich zuerst einloggen</b>",
    }

    strings_tr = {
        "args": "🚫 <b>Arama sorgusu belirtin</b>",
        "404": "🚫 <b>Sonuç bulunamadı</b>",
        "oauth": (
            "🔑 <b>TIDAL'e giriş yapın</b>\n\n<i>Bu bağlantı 5 dakika içinde sona"
            " erecek</i>"
        ),
        "oauth_btn": "🔑 Giriş yap",
        "success": "✅ <b>Başarıyla giriş yaptınız!</b>",
        "error": "🚫 <b>Giriş hatası</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Aranıyor...</b>",
        "tidal_like_btn": "🖤 Beğen",
        "tidal_dislike_btn": "💔 Beğenme",
        "auth_first": "🚫 <b>Önce giriş yapmanız gerekir</b>",
    }

    strings_hi = {
        "args": "🚫 <b>खोज प्रश्न निर्दिष्ट करें</b>",
        "404": "🚫 <b>कोई परिणाम नहीं मिला</b>",
        "oauth": (
            "🔑 <b>TIDAL में लॉगिन करें</b>\n\n<i>यह लिंक 5 मिनट के लिए सक्रिय होगा</i>"
        ),
        "oauth_btn": "🔑 लॉगिन करें",
        "success": "✅ <b>सफलतापूर्वक लॉगिन किया गया!</b>",
        "error": "🚫 <b>लॉगिन त्रुटि</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>खोज रहा है...</b>",
        "tidal_like_btn": "🖤 पसंद",
        "tidal_dislike_btn": "💔 पसंद नहीं",
        "auth_first": "🚫 <b>पहले लॉगिन करना आवश्यक है</b>",
    }

    strings_uz = {
        "args": "🚫 <b>Qidiruv so'rovi belgilang</b>",
        "404": "🚫 <b>Natija topilmadi</b>",
        "oauth": (
            "🔑 <b>TIDAL'da kirishingiz kerak</b>\n\n<i>Ushbu havola 5 daqiqaga aktiv"
            " bo'ladi</i>"
        ),
        "oauth_btn": "🔑 Kirish",
        "success": "✅ <b>Muvaffaqiyatli kirildi!</b>",
        "error": "🚫 <b>Kirishda xatolik</b>",
        "search": "🐈‍⬛ <b>{}</b>",
        "tidal_btn": "🐈‍⬛ Tidal",
        "searching": "🔍 <b>Izlanmoqda...</b>",
        "tidal_like_btn": "🖤 Yoqadi",
        "tidal_dislike_btn": "💔 Yo'qadi",
        "auth_first": "🚫 <b>Avval kirish kerak</b>",
    }

    async def client_ready(self):
        self._faved = []

        self.tidal = tidalapi.Session()
        login_credentials = (
            self.get("session_id"),
            self.get("token_type"),
            self.get("access_token"),
            self.get("refresh_token"),
        )

        if all(login_credentials):
            try:
                await utils.run_sync(self.tidal.load_oauth_session, *login_credentials)
                assert await utils.run_sync(self.tidal.check_login)
            except Exception:
                logger.exception("Error loading OAuth session")

        if not self.get("muted"):
            try:
                await utils.dnd(self._client, "@hikka_musicdl_bot", archive=True)
                await utils.dnd(self._client, "@DirectLinkGenerator_Bot", archive=True)
            except Exception:
                pass

            self.set("muted", True)

        self._obtain_faved.start()
        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    @loader.loop(interval=60)
    async def _obtain_faved(self):
        if not await utils.run_sync(self.tidal.check_login):
            return

        self._faved = list(
            map(
                int,
                (
                    await utils.run_sync(
                        self.tidal.request,
                        "GET",
                        f"users/{self.tidal.user.id}/favorites/ids",
                    )
                ).json()["TRACK"],
            )
        )

    def _save_session_info(self):
        self.set("token_type", self.tidal.token_type)
        self.set("session_id", self.tidal.session_id)
        self.set("access_token", self.tidal.access_token)
        self.set("refresh_token", self.tidal.refresh_token)

    @loader.command(
        ru_doc="Авторизация в TIDAL",
        de_doc="Authentifizierung in TIDAL",
        tr_doc="TIDAL'de oturum açma",
        hi_doc="TIDAL में प्रमाणीकरण",
        uz_doc="TIDAL'da avtorizatsiya",
    )
    async def tlogincmd(self, message: Message):
        """Open OAuth window to login into TIDAL"""
        result, future = self.tidal.login_oauth()
        form = await self.inline.form(
            message=message,
            text=self.strings("oauth"),
            reply_markup={
                "text": self.strings("oauth_btn"),
                "url": f"https://{result.verification_uri_complete}",
            },
            gif="https://i.gifer.com/8Z2a.gif",
        )

        outer_loop = asyncio.get_event_loop()

        def callback(*args, **kwargs):
            nonlocal form, outer_loop
            if self.tidal.check_login():
                asyncio.ensure_future(
                    form.edit(
                        self.strings("success"),
                        gif="https://c.tenor.com/IrKex2lXvR8AAAAC/sparkly-eyes-joy.gif",
                    ),
                    loop=outer_loop,
                )
                self._save_session_info()
            else:
                asyncio.ensure_future(form.edit(self.strings("error")), loop=outer_loop)

        future.add_done_callback(callback)

    @loader.command(
        ru_doc="<запрос> - Поиск трека в TIDAL",
        de_doc="<Anfrage> - Suche nach einem Track in TIDAL",
        tr_doc="<sorgu> - TIDAL'de bir parça arama",
        hi_doc="<अनुरोध> - TIDAL में एक ट्रैक खोजें",
        uz_doc="<so'rov> - TIDAL'da parca qidirish",
    )
    async def tidalcmd(self, message: Message):
        """<query> - Search TIDAL"""
        if not await utils.run_sync(self.tidal.check_login):
            await utils.answer(message, self.strings("auth_first"))
            return

        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("searching"))

        result = await utils.run_sync(self.tidal.search, "track", query, limit=1)
        if not result or not result.tracks:
            await utils.answer(message, self.strings("404"))
            return

        track = result.tracks[0]
        full_name = f"{track.artist.name} - {track.name}"

        meta = (
            await utils.run_sync(
                self.tidal.request,
                "GET",
                f"tracks/{track.id}",
            )
        ).json()

        tags = []

        if meta.get("explicit"):
            tags += ["#explicit🤬"]

        if meta.get("audioQuality"):
            tags += [f"#{meta['audioQuality']}🔈"]

        if isinstance(meta.get("audioModes"), list):
            for tag in meta["audioModes"]:
                tags += [f"#{tag}🎧"]

        if track.id in self._faved:
            tags += ["#favorite🖤"]

        if tags:
            tags = "\n\n" + "\n".join(
                ["  ".join(chunk) for chunk in utils.chunks(tags, 2)]
            )

        text = self.strings("search").format(utils.escape_html(full_name)) + tags

        message = await utils.answer(
            message, text + "\n\n<i>Downloading audio file...</i>"
        )
        url = await self.musicdl.dl(full_name)

        await self.inline.form(
            message=message,
            text=text,
            **(
                {
                    "audio": {
                        "url": url,
                        "title": track.name,
                        "performer": track.artist.name,
                    }
                }
                if url
                else {}
            ),
            silent=True,
            reply_markup=[
                [
                    {
                        "text": self.strings("tidal_btn"),
                        "url": f"https://listen.tidal.com/track/{track.id}",
                    },
                    *(
                        [
                            {
                                "text": self.strings("tidal_like_btn"),
                                "callback": self._like,
                                "args": (track, text),
                            }
                        ]
                        if track.id not in self._faved
                        else [
                            {
                                "text": self.strings("tidal_dislike_btn"),
                                "callback": self._dislike,
                                "args": (track, text),
                            }
                        ]
                    ),
                ],
            ],
        )

    async def _like(self, call: InlineCall, track: tidalapi.Track, text: str):
        try:
            await utils.run_sync(self.tidal.user.favorites.add_track, track.id)
        except Exception:
            logger.exception("Error liking track")
            await call.answer("🚫 Error!")
        else:
            await call.answer("💚 Liked!")
            await call.edit(
                text,
                reply_markup=[
                    [
                        {
                            "text": self.strings("tidal_btn"),
                            "url": f"https://listen.tidal.com/track/{track.id}",
                        },
                        {
                            "text": self.strings("tidal_dislike_btn"),
                            "callback": self._dislike,
                            "args": (track, text),
                        },
                    ],
                ],
            )

    async def _dislike(self, call: InlineCall, track: tidalapi.Track, text: str):
        try:
            await utils.run_sync(self.tidal.user.favorites.remove_track, track.id)
        except Exception:
            logger.exception("Error disliking track")
            await call.answer("🚫 Error!")
        else:
            await call.answer("💔 Disliked!")
            await call.edit(
                text,
                reply_markup=[
                    [
                        {
                            "text": self.strings("tidal_btn"),
                            "url": f"https://listen.tidal.com/track/{track.id}",
                        },
                        {
                            "text": self.strings("tidal_like_btn"),
                            "callback": self._like,
                            "args": (track, text),
                        },
                    ],
                ],
            )
