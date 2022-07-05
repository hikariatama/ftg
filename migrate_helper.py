# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @hikarimods

import asyncio
import io
from .. import loader, utils
import logging
import requests
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import UpdateNewChannelMessage
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


@loader.tds
class HikkaMigratorMod(loader.Module):
    """Delivers minor updates, which can be installed within restart"""

    strings = {
        "name": "HikkaMigrator",
        "avatar": "☺️ <b>Do you want to apply new bot avatar?</b>",
    }

    strings_ru = {
        "avatar": "☺️ <b>Давай сменим аватарку бота?</b>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._fuck = False
        if self.get("hash") == "ad3e522b2173c85c344a07259500a687":
            raise loader.SelfUnload

        self.set("hash", "ad3e522b2173c85c344a07259500a687")
        asyncio.ensure_future(self._process())
        await self.inline.bot.send_photo(
            client._tg_id,
            "https://github.com/hikariatama/assets/raw/master/bot_pfp.png",
            caption=self.strings("avatar"),
            reply_markup=self.inline.generate_markup(
                {
                    "text": "🎉 Apply",
                    "callback": self._call,
                }
            ),
        )
        raise loader.SelfUnload

    async def _call(self, call: InlineCall):
        if self._fuck:
            return

        async with self._client.conversation("@BotFather") as conv:
            m = await conv.send_message("/cancel")
            r = await conv.get_response()
            await m.delete()
            await r.delete()
            m = await conv.send_message("/setuserpic")
            r = await conv.get_response()
            await m.delete()
            await r.delete()
            m = await conv.send_message(f"@{self.inline.bot_username}")
            r = await conv.get_response()
            await m.delete()
            await r.delete()
            photo = io.BytesIO(
                requests.get(
                    "https://github.com/hikariatama/assets/raw/master/bot_pfp.png"
                ).content
            )
            photo.name = "avatar.png"
            f = await conv.send_file(photo)
            r = await conv.get_response()
            await f.delete()
            await r.delete()

        await call.answer("🎉 Applied new cool avatar!")
        self._fuck = True

    async def _process(self):
        if (
            self.lookup("HikkaInfo").config["banner_url"]
            == "https://i.imgur.com/XYNawuK.jpeg"
        ):
            logger.info("🔁 Applied new cool banner!")
            self.lookup("HikkaInfo").config[
                "banner_url"
            ] = "https://github.com/hikariatama/assets/raw/master/hikka_banner.png"

        icons = [
            "hikka-assets",
            "hikka-acc-switcher",
            "hikka-backups",
            "hikka-logs",
            "hikka-onload",
            "silent-tags",
        ]

        async for dialog in self._client.iter_dialogs(None, ignore_migrated=True):
            if (
                dialog.name in icons
                and dialog.is_channel
                and (
                    dialog.entity.participants_count == 1
                    or dialog.entity.participants_count == 2
                    and dialog.name in {"hikka-logs", "silent-tags"}
                )
            ):
                res = await self._client(
                    EditPhotoRequest(
                        channel=dialog.entity,
                        photo=await self._client.upload_file(
                            (
                                await utils.run_sync(
                                    requests.get,
                                    "https://github.com/hikariatama/assets/raw/master/"
                                    + dialog.name
                                    + ".png",
                                )
                            ).content,
                            file_name="photo.png",
                        ),
                    )
                )
                await self._client.delete_messages(
                    dialog.entity,
                    message_ids=[
                        next(
                            update
                            for update in res.updates
                            if isinstance(update, UpdateNewChannelMessage)
                        ).message.id
                    ],
                )

                await asyncio.sleep(5)
