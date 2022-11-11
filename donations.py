#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/donations_icon.png
# meta banner: https://mods.hikariatama.ru/badges/donations.jpg
# meta desc: [RU] Create donate widgets through Hikari.Donations platform
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class HikariDonationsMod(loader.Module):
    """Создает виджеты для доната"""

    strings = {"name": "HikariDonations", "args": "🚫 <b>Неверные аргументы</b>"}

    async def donatecmd(self, message: Message):
        """<сумма> <описание> - Создать новый донатный виджет в текущем чате"""
        args = utils.get_args_raw(message)
        if not args or len(args.split()) < 2 or not args.split()[0].isdigit():
            await utils.answer(message, self.strings("args"))
            return

        amount = int(args.split()[0])
        target = args.split(maxsplit=1)[1]

        if amount not in range(1, 50001):
            await utils.answer(message, self.strings("args"))
            return

        amount = str(amount)

        async with self._client.conversation("@hikaridonate_bot") as conv:
            for msg in ["/widget", target, amount]:
                m = await conv.send_message(msg)
                r = await conv.get_response()

                await m.delete()
                await r.delete()

        widget_id = r.reply_markup.rows[0].buttons[0].query
        q = await self._client.inline_query("@hikaridonate_bot", widget_id)
        await q[0].click(message.peer_id)
        await message.delete()
