#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta title: WCOStream β
# meta pic: https://0x0.st/oUyf.webp
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/wcostream.jpg
# scope: hikka_only
# scope: hikka_min 1.6.0
# requires: cloudscraper js2py user-agent

import asyncio
import base64
import dataclasses
import difflib
import io
import logging
import re
import threading
import typing
from collections import namedtuple
from queue import Queue

import cloudscraper
import js2py
import requests
from telethon.tl.types import Message
from user_agent import generate_user_agent

from .. import loader, utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Anime:
    title: str
    description: str
    image: str
    url: str


Link = namedtuple("Link", ["name", "url"])


class Downloader(threading.Thread):
    def __init__(self, base: "ThreadedDownloader"):  # type: ignore
        super().__init__()
        self.queue = base.queue
        self.result = base.result

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()

            self.result[url] = url.download()
            self.queue.task_done()


class URLTarget:
    def __init__(self, url: Link, scraper: cloudscraper.CloudScraper):
        self.name = url.name
        self.url = url.url
        self.scraper = scraper

    def download(self):
        try:
            file = io.BytesIO()
            file.name = "video.mp4"
            with self.scraper.get(
                self.url,
                stream=True,
                headers={
                    **self._common_headers,
                    "Accept": "*/*",
                    "Accept-Encoding": "identity;q=1, *;q=0",
                    "Connection": "keep-alive",
                    "Referer": f"https://{self.config['wco_mirror']}/",
                    "Sec-Fetch-Dest": "video",
                    "Sec-Fetch-Mode": "no-cors",
                },
            ) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    file.write(chunk)

            file.seek(0)
        except Exception:
            return None

        return (self.name, file)

    def __str__(self) -> str:
        return f"URLTarget({self.url})"


class ThreadedDownload:
    def __init__(
        self,
        scraper: cloudscraper.CloudScraper,
        urls: typing.Optional[typing.List[Link]] = None,
        thread_count: int = 5,
    ):
        self.scraper = scraper
        self.queue = Queue(0)  # Infinite sized queue
        self.threads = []
        self.result = {}

        self.thread_count = thread_count

        for url in urls:
            self.queue.put(URLTarget(url, self.scraper))

    def run(self):
        for _ in range(self.thread_count):
            thread = Downloader(self)
            thread.start()
            self.threads.append(thread)

        if self.queue.qsize() > 0:
            self.queue.join()


class WCODownloader:
    def __init__(self, message: Message, max_retries: int):
        logger.debug("Initializing new WCODownloader instance...")
        self.scraper = cloudscraper.create_scraper()
        self.message = message
        self.args = None  # Must be passed later using feed()
        self.max_retries = max_retries

        self._useragent = generate_user_agent(device_type="desktop")
        self._common_headers = {
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": self._useragent,
        }
        self._anime_cache = {}

    async def feed(self, args: str):
        logger.debug("Feeding WCODownloader with %s", args)

        anime = await self._search(args)

        if anime is None:
            logger.debug("No anime found for %s", args)
            return None

        self.args = anime
        return await self._fetch_metadata()

    @staticmethod
    def _guess_season(name: str) -> int:
        try:
            return int(re.findall(r"season (\d+)", name.lower())[0])
        except IndexError:
            return 1

    @staticmethod
    def _guess_episode(name: str) -> int:
        try:
            return int(re.findall(r"episode (\d+)", name.lower())[0])
        except IndexError:
            return 1

    async def _fetch_page_urls(self) -> typing.List[Link]:
        logger.debug("Fetching page URLs...")

        result = (
            await utils.run_sync(
                self.scraper.get,
                f"https://{self.config['wco_mirror']}/anime/{self.args}",
            )
        ).text

        if "The requested URL was not found on this server" in result:
            logger.debug("Anime %s not found", self.args)
            await utils.answer(self.message, self.strings("404").format(self.args))
            return

        urls = list(
            sorted(
                [
                    Link(name, url)
                    for url, name in re.findall(
                        r'<a href="([^"]*?)" rel="bookmark" title="[^"]*?"'
                        r' class="sonra">([^<]*?)</a>',
                        result,
                        flags=re.DOTALL,
                    )
                ],
                key=lambda x: (self._guess_season(x.name), self._guess_episode(x.name)),
            )
        )

        logger.debug("Found %d page URLs for %s", len(urls), self.args)

        return urls

    async def _fetch_download_urls(self, links: typing.List[Link]) -> typing.List[Link]:
        logger.debug("Fetching download URLs...")

        urls = []

        for name, link in links:
            logger.debug("Fetching download URL for %s", name)

            result = (await utils.run_sync(self.scraper.get, link)).text
            result = re.search(
                r"<script>var [^ ]*? = \"\";.*?</script>", result, re.DOTALL
            )[0]

            def atob(s):
                return base64.b64decode("{}".format(s)).decode("utf-8")

            js2py.disable_pyimport()
            ctx = js2py.EvalJs({"atob": atob})

            result = (
                result.replace("document.write", "return ")
                .replace("<script>", "")
                .replace("</script>", "")
                .replace("var for", "var For")
                .replace("escape(for)", "escape(For)")
                .replace("for +=", "For +=")
            )

            logger.debug("Solving WCO challenge for %s: %s", name, result)

            ctx.execute(f"function f(){{{result}}};")

            link = re.search(r'src="(.*?)"', ctx.f())[1]

            if not link.startswith("http"):
                link = f"https://{self.config['wco_mirror']}/{link}"

            logger.debug("Found interim URL #1 for %s: %s", name, link)

            result = (
                await utils.run_sync(
                    self.scraper.get,
                    link,
                    headers={
                        **self._common_headers,
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "referer": f"https://{self.config['wco_mirror']}/",
                    },
                )
            ).text

            link = (
                f"https://{self.config['wco_mirror']}"
                + re.search(r'\(".*?(\/inc\/embed\/getvidlink.php.*?)"', result)[1]
            )

            logger.debug("Found interim URL #2 for %s: %s", name, link)

            result = (
                await utils.run_sync(
                    self.scraper.get,
                    link,
                    headers={
                        **self._common_headers,
                        "Accept": "*/*",
                        "Cookie": "countrytabs=0",
                        "Referer": link,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )
            ).json()

            url = f"{result['server']}/getvid?evid={result['enc']}"

            logger.debug("Found download URL for %s: %s", name, url)

            urls += [Link(name, url)]

        return urls

    async def download(
        self,
        retries: int = 0,
    ) -> typing.List[typing.Tuple[str, io.BytesIO]]:
        logger.debug("Starting download...")
        if retries >= self.max_retries:
            logger.debug("Max retries reached, abort")
            return []

        if not (links := await self._fetch_page_urls()):
            logger.debug("No links found, restarting...")
            return await self.download(retries + 1)

        urls = (
            urls
            if (urls := await self._fetch_download_urls(links))
            else await self.download(retries + 1)
        )

        logger.debug("Downloading %d files...", len(urls))

        downloader = ThreadedDownload(self.scraper, urls, 5)
        await utils.run_sync(downloader.run)

        logger.debug("Download complete")

        return [result for result in downloader.result.values() if result]

    def download_file(self, url: str) -> io.BytesIO:
        logger.debug("Downloading file %s", url)

        file = io.BytesIO()
        file.name = "video.mp4"

        with self.scraper.get(
            url,
            stream=True,
            headers={
                **self._common_headers,
                "Accept-Encoding": "identity;q=1, *;q=0",
                "Connection": "keep-alive",
                "Referer": f"https://{self.config['wco_mirror']}/",
                "Sec-Fetch-Dest": "video",
                "Sec-Fetch-Mode": "no-cors",
            },
        ) as r:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)

        file.seek(0)

        logger.debug("Download complete for %s", url)

        return file

    async def _fetch_metadata(self, retries: int = 0) -> Anime:
        logger.debug("Fetching metadata for %s...", self.args)

        if retries >= self.max_retries:
            return None

        try:
            url = f"https://{self.config['wco_mirror']}/anime/{self.args}"
            result = (await utils.run_sync(self.scraper.get, url)).text

            if "The requested URL was not found on this server" in result:
                raise Exception

            title = re.search(r'<h2 title="[^"]*?">(.*?)</h2>', result)[1]
            description = re.search(r"<p>(.*?)</p>", result)[1]
            image = (
                "https:"
                + re.search(
                    r'cat-img-desc.*?<img src="(.*?)" alt=',
                    result,
                    flags=re.DOTALL,
                )[1]
            )

            anime = Anime(title, description, image, url)
            logger.debug("Found metadata for %s: %s", self.args, anime)

            return anime
        except Exception as e:
            logger.debug("Failed to fetch metadata due to %s, retrying...", e)

            await asyncio.sleep(1)
            return await self._fetch_metadata(retries + 1)

    async def _cache_anime_list(self):
        logger.debug("Caching anime list...")
        self._anime_cache = {
            anime.lower(): link
            for anime, link in (
                await utils.run_sync(requests.get, "https://0x0.st/oUtA.json")
            )
            .json()
            .items()
        }

    async def _search(self, query: str) -> typing.Optional[str]:
        if not self._anime_cache:
            await self._cache_anime_list()

        match = difflib.get_close_matches(
            query.lower(), self._anime_cache.keys(), cutoff=0.5
        )
        return self._anime_cache[match[0]] if match else None


@loader.tds
class WCOStream(loader.Module):
    """Downloads anime from WCOstream"""

    strings = {
        "name": "WCOStream",
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Arguments not"
            " specified</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> not found</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Fetching"
            " metadata...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Downloading anime to"
            ' <a href="{}">channel</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Fetching download"
            " urls...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>Anime {} has been"
            ' successfully downloaded to <a href="{}">channel</a></b>'
        ),
    }

    strings_ru = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аргументы не"
            " указаны</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аниме"
            " </b><code>{}</code><b> не найдено</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Получение"
            " метаданных...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Загрузка аниме в"
            ' <a href="{}">канал</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Получение ссылок на"
            " загрузку...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>Аниме {} было"
            ' успешно загружено в <a href="{}">канал</a></b>'
        ),
    }

    strings_kk = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аргументтер"
            " көрсетілмеген</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аниме"
            " </b><code>{}</code><b> табылмады</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Метадеректер"
            " алынуда...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Аниме"
            ' <a href="{}">каналына</a> жүктелуде</b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Жүктеу сілтемелері"
            " алынуда...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>Аниме {} сәтті"
            ' <a href="{}">каналына</a> жүктелді</b>'
        ),
    }

    strings_it = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argomenti non"
            " specificati</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> non trovato</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Recupero dei"
            " metadati...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Download dell'anime"
            ' nel <a href="{}">canale</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Recupero degli URL di"
            " download...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>L'anime {} è stato"
            ' scaricato con successo nel <a href="{}">canale</a></b>'
        ),
    }

    strings_de = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argumente nicht"
            " angegeben</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> nicht gefunden</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Metadaten"
            " abrufen...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Anime wird"
            ' heruntergeladen <a href="{}">channel</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Download-URLs"
            " abrufen...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>Anime {} wurde"
            ' erfolgreich heruntergeladen <a href="{}">channel</a></b>'
        ),
    }

    strings_es = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argumentos no"
            " especificados</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> no encontrado</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Obteniendo"
            " metadatos...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Descargando anime a"
            ' <a href="{}">channel</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Obteniendo URL de"
            " descarga...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>El anime {} se"
            ' descargó correctamente a <a href="{}">channel</a></b>'
        ),
    }

    strings_tr = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argümanlar"
            " belirtilmedi</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> bulunamadı</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Meta veriler"
            " alınıyor...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Anime indiriliyor"
            ' <a href="{}">channel</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>İndirme bağlantıları"
            " alınıyor...<b>\n\n<emoji document_id=5391230176153575100>🚂</emoji>"
            " <b>{}</b>\n\n<emoji document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>{} anime başarıyla"
            ' indirildi <a href="{}">channel</a></b>'
        ),
    }

    strings_uz = {
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argumentlar"
            " ko'rsatilmadi</b>"
        ),
        "404": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Anime"
            " </b><code>{}</code><b> topilmadi</b>"
        ),
        "loading": (
            "<emoji document_id=5332601351417372910>💧</emoji> <b>Meta ma'lumotlar"
            " olinmoqda...</b>"
        ),
        "downloading": (
            "<emoji document_id=4985658201098682958>⬇️</emoji> <b>Anime yuklanmoqda"
            ' <a href="{}">channel</a></b>'
        ),
        "loading_anime": (
            "<emoji document_id=5309799327093236710>🫥</emoji> <b>Yuklab olish"
            " manzillari olinmoqda...<b>\n\n<emoji"
            " document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "anime": (
            "<emoji document_id=5391230176153575100>🚂</emoji> <b>{}</b>\n\n<emoji"
            " document_id=5787544344906959608>ℹ️</emoji> <i>{}</i>"
        ),
        "downloaded": (
            "<emoji document_id=5332533929020761310>✅</emoji> <b>{} anime"
            ' muvaffaqiyatli yuklandi <a href="{}">channel</a></b>'
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "max_retries",
                3,
                lambda: "Maximum amount of retries",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "wco_mirror",
                "www.wcostream.net",
                lambda: "WCO mirror to use",
                validator=loader.validators.Link(),
            ),
        )

    @loader.command()
    async def wco(self, message: Message):
        """<anime> - Download anime"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("loading"))

        downloader = WCODownloader(message, self.config["max_retries"])
        anime = await downloader.feed(args)

        message = await utils.answer(
            message,
            self.strings("loading_anime").format(
                utils.escape_html(anime.title),
                utils.escape_html(anime.description),
            ),
        )

        channel, _ = await utils.asset_channel(
            self._client,
            anime.title[:255],
            anime.description[:255],
            avatar=anime.image,
            channel=True,
        )

        await self._client.send_file(
            channel,
            anime.image,
            caption=self.strings("anime").format(
                utils.escape_html(anime.title),
                utils.escape_html(anime.description),
            ),
        )

        message = await utils.answer(
            message,
            self.strings("downloading").format(f"https://t.me/c/{channel.id}/1"),
        )

        files = await downloader.download()
        files.sort(
            key=lambda x: (
                tuple(map(int, re.findall(r"(\d+)", x[0])))
                if x[0] and re.findall(r"(\d+)", x[0])
                else 0
            )
        )

        for i, (name, file) in enumerate(files):
            await self._client.send_file(
                channel,
                file,
                caption=(
                    "<emoji document_id=5373330964372004748>📺</emoji> <b>{}</b>".format(
                        utils.escape_html(
                            re.sub(
                                r"english|dubbed|subbed",
                                "",
                                (name or ""),
                                flags=re.IGNORECASE,
                            )
                        )
                        or f"{utils.escape_html(anime.title)}: Episode {i + 1} / {len(files)}"
                    )
                ),
            )

        await utils.answer(
            message,
            self.strings("downloaded").format(
                utils.escape_html(anime.title),
                f"https://t.me/c/{channel.id}/1",
            ),
        )
