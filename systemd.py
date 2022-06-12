# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/plasticine/344/apple-settings--v2.png
# scope: inline
# scope: hikka_only
# meta developer: @hikarimods

# ⚠️ Please, ensure that userbot has enough rights to control units
# Put these lines in /etc/sudoers:
# 
# user ALL=(ALL) NOPASSWD: /bin/systemctl
# user ALL=(ALL) NOPASSWD: /bin/journalctl
# 
# Where `user` is user on behalf of which the userbot is running

from dataclasses import replace
from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall
import logging
import subprocess
import asyncio
import io
from typing import Union

logger = logging.getLogger(__name__)


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "K", "M", "G", "T", "P"]:
        if size < 1024.0 or unit == "P":
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit}"


@loader.tds
class SystemdMod(loader.Module):
    """Control systemd units easily"""

    strings = {
        "name": "Systemd",
        "panel": ("🎛 <b>Here you can control your systemd units</b>\n\n{}"),
        "unit_doesnt_exist": "🚫 <b>Unit</b> <code>{}</code> <b>doesn't exist!</b>",
        "args": "🚫 <b>No arguments specified</b>",
        "unit_added": "✅ <b>Unit </b><code>{}</code><b> with name </b><code>{}</code><b> added",
        "unit_removed": "✅ <b>Unit </b><code>{}</code><b> removed</b>",
        "unit_action_done": "✅ <b>Action </b><code>{}</code><b> performed on unit </b><code>{}</code>",
        "unit_control": (
            "🎛 <b>Interacting with unit </b><code>{}</code><b> (</b><code>{}</code><b>)</b>\n"
            "{} <b>Unit status: </b><code>{}</code>"
        ),
        "action_not_found": "🚫 <b>Action </b><code>{}</code><b> not found</b>",
        "unit_renamed": "✅ <b>Unit </b><code>{}</code><b> renamed to </b><code>{}</code>",
        "stop_btn": "🍎 Stop",
        "start_btn": "🍏 Start",
        "restart_btn": "🔄 Restart",
        "logs_btn": "📄 Logs",
        "tail_btn": "🚅 Tail",
        "back_btn": "🔙 Back",
        "close_btn": "✖️ Close",
        "refresh_btn": "🔄 Refresh",
    }

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client

    async def inline__close(self, call: InlineCall):
        await call.delete()

    def _get_unit_status_text(self, unit: str) -> str:
        return (
            subprocess.run(
                [
                    "sudo",
                    "-S",
                    "systemctl",
                    "is-active",
                    unit,
                ],
                check=False,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )

    def _is_running(self, unit: str) -> bool:
        return self._get_unit_status_text(unit) == "active"

    def _unit_exists(self, unit: str) -> bool:
        return (
            subprocess.run(
                [
                    "sudo",
                    "-S",
                    "systemctl",
                    "cat",
                    unit,
                ],
                check=False,
                stdout=subprocess.PIPE,
            ).returncode
            == 0
        )

    async def _manage_unit(self, call: Union[InlineCall, int], unit: dict, action: str):
        if action == "start":
            subprocess.run(
                ["sudo", "-S", "systemctl", "start", unit["formal"]], check=True
            )
        elif action == "stop":
            subprocess.run(
                ["sudo", "-S", "systemctl", "stop", unit["formal"]], check=True
            )
        elif action == "restart":
            subprocess.run(
                ["sudo", "-S", "systemctl", "restart", unit["formal"]], check=True
            )
        elif action in {"logs", "tail"}:
            logs = (
                subprocess.run(
                    [
                        "sudo",
                        "-S",
                        "journalctl",
                        "-u",
                        unit["formal"],
                        "-n",
                        "1000",
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                )
                .stdout.decode()
                .strip()
            )

            hostname = (
                subprocess.run(["hostname"], check=True, stdout=subprocess.PIPE)
                .stdout.decode()
                .strip()
            )
            logs = logs.replace(f"{hostname} ", "")
            logs = logs.replace("[" + str(self._get_unit_pid(unit["formal"])) + "]", "")

            if action == "logs":
                logs = io.BytesIO(logs.encode())
                logs.name = f"{unit['formal']}-logs.txt"

                await self._client.send_file(
                    call.form["chat"] if not isinstance(call, int) else call, logs
                )
            else:
                actual_logs = ""
                logs = list(reversed(logs.splitlines()))
                while logs:
                    chunk = f"{logs.pop()}\n"
                    if len(actual_logs + chunk) >= 4096:
                        break

                    actual_logs += chunk

                if isinstance(call, int):
                    await self.inline.form(
                        f"<code>{utils.escape_html(actual_logs)}</code>",
                        call,
                        reply_markup=self._get_unit_markup(unit),
                    )
                    return

                await call.edit(
                    f"<code>{utils.escape_html(actual_logs)}</code>",
                    reply_markup=self._get_unit_markup(unit),
                )
                await call.answer("Action complete")
                return

        if isinstance(call, int):
            return

        await call.answer("Action complete")
        await asyncio.sleep(2)
        await self._control_service(call, unit)

    def _get_unit_markup(self, unit: dict) -> list:
        return [
            [
                {
                    "text": self.strings("start_btn"),
                    "callback": self._manage_unit,
                    "args": (unit, "start"),
                },
                {
                    "text": self.strings("stop_btn"),
                    "callback": self._manage_unit,
                    "args": (unit, "stop"),
                },
                {
                    "text": self.strings("restart_btn"),
                    "callback": self._manage_unit,
                    "args": (unit, "restart"),
                },
            ],
            [
                {
                    "text": self.strings("logs_btn"),
                    "callback": self._manage_unit,
                    "args": (unit, "logs"),
                },
                {
                    "text": self.strings("tail_btn"),
                    "callback": self._manage_unit,
                    "args": (unit, "tail"),
                },
            ],
            [
                {
                    "text": self.strings("refresh_btn"),
                    "callback": self._control_service,
                    "args": (unit,),
                },
                {
                    "text": self.strings("back_btn"),
                    "callback": self._control_services,
                },
            ],
        ]

    async def _control_service(self, call: InlineCall, unit: dict):
        await call.edit(
            self.strings("unit_control").format(
                unit["name"],
                unit["formal"],
                self._get_unit_status_emoji(unit["formal"]),
                self._get_unit_status_text(unit["formal"]),
            ),
            reply_markup=self._get_unit_markup(unit),
        )

    def _get_unit_pid(self, unit: str) -> str:
        return (
            subprocess.run(
                [
                    "sudo",
                    "-S",
                    "systemctl",
                    "show",
                    unit,
                    "--property=MainPID",
                    "--value",
                ],
                check=False,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )

    def _get_unit_resources_consumption(self, unit: str) -> str:
        if not self._is_running(unit):
            return ""

        pid = self._get_unit_pid(unit)
        ram = human_readable_size(
            int(
                subprocess.run(
                    [
                        "ps",
                        "-p",
                        pid,
                        "-o",
                        "rss",
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                )
                .stdout.decode()
                .strip()
                .split("\n")[1]
            )
            * 1024
        )

        cpu = (
            subprocess.run(
                [
                    "ps",
                    "-p",
                    pid,
                    "-o",
                    r"%cpu",
                ],
                check=False,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
            .split("\n")[1]
            + "%"
        )

        return f"📟 <code>{ram}</code> | 🗃 <code>{cpu}</code>"

    def _get_panel(self):
        return self.strings("panel").format(
            "\n".join(
                [
                    f"{self._get_unit_status_emoji(unit['formal'])} <b>{unit['name']}</b> (<code>{unit['formal']}</code>): {self._get_unit_status_text(unit['formal'])} {self._get_unit_resources_consumption(unit['formal'])}"
                    for unit in self.get("services", [])
                ]
            )
        )

    async def _control_services(self, call: InlineCall, refresh: bool = False):
        await call.edit(
            self._get_panel(),
            reply_markup=self._get_services_markup(),
        )

        if refresh:
            await call.answer("Information updated!")

    def _get_unit_status_emoji(self, unit: str) -> str:
        status = self._get_unit_status_text(unit)
        if status == "active":
            return "🍏"
        elif status == "inactive":
            return "🍎"
        elif status == "failed":
            return "🚫"
        elif status == "activating":
            return "🔄"
        else:
            return "❓"

    def _get_services_markup(self) -> list:
        return utils.chunks(
            [
                {
                    "text": self._get_unit_status_emoji(service["formal"])
                    + " "
                    + service["name"],
                    "callback": self._control_service,
                    "args": (service,),
                }
                for service in self.get("services", [])
            ],
            2,
        ) + [
            [
                {
                    "text": self.strings("refresh_btn"),
                    "callback": self._control_services,
                    "args": (True,),
                },
                {"text": self.strings("close_btn"), "callback": self.inline__close},
            ]
        ]

    async def unitscmd(self, message: Message):
        """Open control panel"""
        form = await self.inline.form(
            self._get_panel(),
            message,
            reply_markup=self._get_services_markup(),
        )

    async def addunitcmd(self, message: Message):
        """<unit> <name> - Add new unit"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        try:
            unit, name = args.split(maxsplit=1)
        except ValueError:
            unit = args
            name = args

        if not self._unit_exists(unit):
            await utils.answer(message, self.strings("unit_doesnt_exist").format(unit))
            return

        self.set(
            "services",
            self.get("services", []) + [{"name": name, "formal": unit}],
        )
        await utils.answer(message, self.strings("unit_added").format(unit, name))

    async def delunitcmd(self, message: Message):
        """<unit> - Delete unit"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        if not any(unit["formal"] == args for unit in self.get("services", [])):
            await utils.answer(message, self.strings("unit_doesnt_exist").format(args))
            return

        self.set(
            "services",
            [
                service
                for service in self.get("services", [])
                if service["formal"] != args
            ],
        )
        await utils.answer(message, self.strings("unit_removed").format(args))

    async def unitcmd(self, message: Message):
        """<unit> <start|stop|restart|logs|tail> - Perform specific action on unit bypassing main menu"""
        args = utils.get_args_raw(message)
        if not args or len(args.split()) < 2:
            await utils.answer(message, self.strings("args"))
            return

        unit, action = args.split(maxsplit=1)
        if not self._unit_exists(unit):
            await utils.answer(message, self.strings("unit_doesnt_exist").format(unit))
            return

        if action in {"start", "stop", "restart", "logs"}:
            await self._manage_unit(
                utils.get_chat_id(message),
                {"formal": unit, "name": unit},
                action,
            )
        elif action == "tail":
            await self._manage_unit(
                utils.get_chat_id(message),
                {"formal": unit, "name": unit},
                "tail",
            )
        else:
            await utils.answer(message, self.strings("action_not_found").format(action))
            return

        await utils.answer(
            message,
            self.strings("unit_action_done").format(action, unit),
        )

    async def nameunitcmd(self, message: Message):
        """<unit> <new_name> - Rename unit"""
        args = utils.get_args_raw(message)
        if not args or len(args.split()) < 2:
            await utils.answer(message, self.strings("args"))
            return

        unit, name = args.split(maxsplit=1)
        if not any(unit_["formal"] == unit for unit_ in self.get("services", [])):
            await utils.answer(message, self.strings("unit_doesnt_exist").format(unit))
            return

        self.set(
            "services",
            [
                service
                for service in self.get("services", [])
                if service["formal"] != unit
            ]
            + [{"name": name, "formal": unit}],
        )
        await utils.answer(message, self.strings("unit_renamed").format(unit, name))
