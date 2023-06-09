# scope: hikka_min 1.2.10
#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/terminal_icon.png
# meta banner: https://mods.hikariatama.ru/badges/terminal.jpg
# meta developer: @bsolute
# rework: @hikariatama
# scope: hikka_only

import asyncio
import contextlib
import logging
import os
import re
import typing

import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


def hash_msg(message):
    return f"{str(utils.get_chat_id(message))}/{str(message.id)}"


async def read_stream(func: callable, stream, delay: float):
    last_task = None
    data = b""
    while True:
        dat = await stream.read(1)

        if not dat:
            # EOF
            if last_task:
                # Send all pending data
                last_task.cancel()
                await func(data.decode("utf-8"))
                # If there is no last task there is inherently no data, so theres no point sending a blank string
            break

        data += dat

        if last_task:
            last_task.cancel()

        last_task = asyncio.ensure_future(sleep_for_task(func, data, delay))


async def sleep_for_task(func: callable, data: bytes, delay: float):
    await asyncio.sleep(delay)
    await func(data.decode("utf-8"))


class MessageEditor:
    def __init__(
        self,
        message: telethon.tl.types.Message,
        command: str,
        config,
        strings,
        request_message,
    ):
        self.message = message
        self.command = command
        self.stdout = ""
        self.stderr = ""
        self.rc = None
        self.redraws = 0
        self.config = config
        self.strings = strings
        self.request_message = request_message

    async def update_stdout(self, stdout):
        self.stdout = stdout
        await self.redraw()

    async def update_stderr(self, stderr):
        self.stderr = stderr
        await self.redraw()

    async def redraw(self):
        text = self.strings("running").format(utils.escape_html(self.command))  # fmt: skip

        if self.rc is not None:
            text += self.strings("finished").format(utils.escape_html(str(self.rc)))

        text += self.strings("stdout")
        text += utils.escape_html(self.stdout[max(len(self.stdout) - 2048, 0) :])
        stderr = utils.escape_html(self.stderr[max(len(self.stderr) - 1024, 0) :])
        text += (self.strings("stderr") + stderr) if stderr else ""
        text += self.strings("end")

        with contextlib.suppress(telethon.errors.rpcerrorlist.MessageNotModifiedError):
            try:
                self.message = await utils.answer(self.message, text)
            except telethon.errors.rpcerrorlist.MessageTooLongError as e:
                logger.error(e)
                logger.error(text)
        # The message is never empty due to the template header

    async def cmd_ended(self, rc):
        self.rc = rc
        self.state = 4
        await self.redraw()

    def update_process(self, process):
        pass


class SudoMessageEditor(MessageEditor):
    # Let's just hope these are safe to parse
    PASS_REQ = "[sudo] password for"
    WRONG_PASS = r"\[sudo\] password for (.*): Sorry, try again\."
    TOO_MANY_TRIES = (r"\[sudo\] password for (.*): sudo: [0-9]+ incorrect password attempts")  # fmt: skip

    def __init__(self, message, command, config, strings, request_message):
        super().__init__(message, command, config, strings, request_message)
        self.process = None
        self.state = 0
        self.authmsg = None

    def update_process(self, process):
        logger.debug("got sproc obj %s", process)
        self.process = process

    async def update_stderr(self, stderr):
        logger.debug("stderr update " + stderr)
        self.stderr = stderr
        lines = stderr.strip().split("\n")
        lastline = lines[-1]
        lastlines = lastline.rsplit(" ", 1)
        handled = False

        if (
            len(lines) > 1
            and re.fullmatch(self.WRONG_PASS, lines[-2])
            and lastlines[0] == self.PASS_REQ
            and self.state == 1
        ):
            logger.debug("switching state to 0")
            await self.authmsg.edit(self.strings("auth_failed"))
            self.state = 0
            handled = True
            await asyncio.sleep(2)
            await self.authmsg.delete()

        if lastlines[0] == self.PASS_REQ and self.state == 0:
            logger.debug("Success to find sudo log!")
            text = self.strings("auth_needed").format(self._tg_id)

            try:
                await utils.answer(self.message, text)
            except telethon.errors.rpcerrorlist.MessageNotModifiedError as e:
                logger.debug(e)

            logger.debug("edited message with link to self")
            command = "<code>" + utils.escape_html(self.command) + "</code>"
            user = utils.escape_html(lastlines[1][:-1])

            self.authmsg = await self.message[0].client.send_message(
                "me",
                self.strings("auth_msg").format(command, user),
            )
            logger.debug("sent message to self")

            self.message[0].client.remove_event_handler(self.on_message_edited)
            self.message[0].client.add_event_handler(
                self.on_message_edited,
                telethon.events.messageedited.MessageEdited(chats=["me"]),
            )

            logger.debug("registered handler")
            handled = True

        if len(lines) > 1 and (
            re.fullmatch(self.TOO_MANY_TRIES, lastline)
            and (self.state == 1 or self.state == 3 or self.state == 4)
        ):
            logger.debug("password wrong lots of times")
            await utils.answer(self.message, self.strings("auth_locked"))
            await self.authmsg.delete()
            self.state = 2
            handled = True

        if not handled:
            logger.debug("Didn't find sudo log.")
            if self.authmsg is not None:
                await self.authmsg[0].delete()
                self.authmsg = None
            self.state = 2
            await self.redraw()

        logger.debug(self.state)

    async def update_stdout(self, stdout):
        self.stdout = stdout

        if self.state != 2:
            self.state = 3  # Means that we got stdout only

        if self.authmsg is not None:
            await self.authmsg.delete()
            self.authmsg = None

        await self.redraw()

    async def on_message_edited(self, message):
        # Message contains sensitive information.
        if self.authmsg is None:
            return

        logger.debug(f"got message edit update in self {str(message.id)}")

        if hash_msg(message) == hash_msg(self.authmsg):
            # The user has provided interactive authentication. Send password to stdin for sudo.
            try:
                self.authmsg = await utils.answer(message, self.strings("auth_ongoing"))
            except telethon.errors.rpcerrorlist.MessageNotModifiedError:
                # Try to clear personal info if the edit fails
                await message.delete()

            self.state = 1
            self.process.stdin.write(
                message.message.message.split("\n", 1)[0].encode("utf-8") + b"\n"
            )


class RawMessageEditor(SudoMessageEditor):
    def __init__(
        self,
        message,
        command,
        config,
        strings,
        request_message,
        show_done=False,
    ):
        super().__init__(message, command, config, strings, request_message)
        self.show_done = show_done

    async def redraw(self):
        logger.debug(self.rc)

        if self.rc is None:
            text = (
                "<code>"
                + utils.escape_html(self.stdout[max(len(self.stdout) - 4095, 0) :])
                + "</code>"
            )
        elif self.rc == 0:
            text = (
                "<code>"
                + utils.escape_html(self.stdout[max(len(self.stdout) - 4090, 0) :])
                + "</code>"
            )
        else:
            text = (
                "<code>"
                + utils.escape_html(self.stderr[max(len(self.stderr) - 4095, 0) :])
                + "</code>"
            )

        if self.rc is not None and self.show_done:
            text += "\n" + self.strings("done")

        logger.debug(text)

        with contextlib.suppress(
            telethon.errors.rpcerrorlist.MessageNotModifiedError,
            telethon.errors.rpcerrorlist.MessageEmptyError,
            ValueError,
        ):
            try:
                await utils.answer(self.message, text)
            except telethon.errors.rpcerrorlist.MessageTooLongError as e:
                logger.error(e)
                logger.error(text)


@loader.tds
class TerminalMod(loader.Module):
    """Runs commands"""

    strings = {
        "name": "Terminal",
        "fw_protect": "How long to wait in seconds between edits in commands",
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Reply to a terminal"
            " command to terminate it</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Could not kill"
            " process</b>"
        ),
        "killed": "<emoji document_id=5312526098750252863>🚫</emoji> <b>Killed</b>",
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>No command is running"
            " in that message</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> System call</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>Exit code</b> <code>{}</code>",
        "stdout": "\n<b>📼 Stdout:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Stderr:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Authentication"
            " failed,"
            " please try again</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " Interactive authentication required</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>Please edit this"
            " message to the password for</b> <code>{}</code> <b>to run</b>"
            " <code>{}</code>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Authentication"
            " failed,"
            " please try again later</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Authenticating...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>Done</b>",
    }

    strings_ru = {
        "fw_protect": "Задержка между редактированиями",
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Ответь на выполняемую"
            " команду для ее завершения</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Не могу убить"
            " процесс</b>"
        ),
        "killed": "<b>Убит</b>",
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>В этом сообщении не"
            " выполняется команда</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> Системная команда</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>Код выхода </b> <code>{}</code>",
        "stdout": "\n<b>📼 Вывод:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Ошибки:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аутентификация"
            " неуспешна, попробуй еще раз</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " Необходима аутентификация</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>Пожалуйста,"
            " отредактируй это сообщение с паролем от рута для</b> <code>{}</code> <b>,"
            " чтобы выполнить</b> <code>{}</code>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Аутентификация не"
            " удалась. Попробуй позже</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Аутентификация...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>Ура</b>",
    }

    strings_de = {
        "fw_protect": (
            "Wie lange soll zwischen den Editierungen in Befehlen gewartet werden"
        ),
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Antworte auf einen"
            " Terminal-Befehl um ihn zu stoppen</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Konnte den Prozess"
            " nicht stoppen</b>"
        ),
        "killed": "<emoji document_id=5312526098750252863>🚫</emoji> <b>Gestoppt</b>",
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Kein Befehl wird in"
            " dieser Nachricht ausgeführt</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> Systemaufruf</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>Exit-Code</b> <code>{}</code>",
        "stdout": "\n<b>📼 Stdout:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Stderr:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Authentifizierung"
            " fehlgeschlagen, bitte versuche es erneut</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " Interaktive Authentifizierung benötigt</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>Bitte bearbeite diese"
            " Nachricht mit dem Passwort für</b> <code>{}</code> <b>um</b>"
            " <code>{}</code> <b>auszuführen</b>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Authentifizierung"
            " fehlgeschlagen, bitte versuche es später erneut</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Authentifizierung"
            " läuft...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>Fertig</b>",
    }

    strings_tr = {
        "fw_protect": "Bir komut arasındaki düzenleme süresi",
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Çalışan bir komutu"
            " durdurmak için yanıtlayın</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>İşlemi"
            " durduramadım</b>"
        ),
        "killed": "<b>Durduruldu</b>",
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Bu mesajda"
            " çalışan bir"
            " komut yok</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> Sistem komutu</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>Çıkış kodu</b> <code>{}</code>",
        "stdout": "\n<b>📼 Stdout:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Stderr:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Kimlik doğrulama"
            " başarısız, lütfen tekrar deneyin</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " Etkileşimli kimlik doğrulaması gerekli</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>Lütfen bu mesajı</b>"
            " <code>{}</code> <b>için</b> <code>{}</code> <b>çalıştırmak için parola"
            " olarak düzenleyin</b>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Kimlik doğrulama"
            " başarısız, lütfen daha sonra tekrar deneyin</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Kimlik doğrulaması"
            " sürüyor...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>Bitti</b>",
    }

    strings_uz = {
        "fw_protect": "Buyruqlar orasidagi tahrirlash vaqti",
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Ishga tushgan"
            " buyruqni"
            " to'xtatish uchun uni javob qilib yuboring</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Protsessni to'xtatib"
            " bo'lmadi</b>"
        ),
        "killed": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>To'xtatildi</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Ushbu xabarda ishga"
            " tushgan buyruq yo'q</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> Tizim buyrug'i</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>Chiqish kodi</b> <code>{}</code>",
        "stdout": "\n<b>📼 Stdout:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Stderr:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Autentifikatsiya"
            " muvaffaqiyatsiz, iltimos qayta urinib ko'ring</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " Ishlanadigan autentifikatsiya talab qilinadi</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>Iltimos, ushbu"
            " xabarni</b> <code>{}</code> <b>uchun</b> <code>{}</code> <b>ishga"
            " tushurish uchun parolasi sifatida tahrirlang</b>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Autentifikatsiya"
            " muvaffaqiyatsiz, iltimos keyinroq qayta urinib ko'ring</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Autentifikatsiya"
            " davom"
            " etmoqda...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>Tugadi</b>",
    }

    strings_hi = {
        "fw_protect": "कमांड के बीच संपादन समय",
        "what_to_kill": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>कमांड चलाने के लिए"
            " उत्तर दें</b>"
        ),
        "kill_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>प्रक्रिया बंद नहीं की"
            " जा सकती</b>"
        ),
        "killed": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>बंद किया गया</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>इस संदेश में कोई कमांड"
            " नहीं चल रहा है</b>"
        ),
        "running": (
            "<emoji document_id=5472111548572900003>⌨️</emoji><b> सिस्टम कमांड</b>"
            " <code>{}</code>"
        ),
        "finished": "\n<b>बाहरी कोड</b> <code>{}</code>",
        "stdout": "\n<b>📼 Stdout:</b>\n<code>",
        "stderr": (
            "</code>\n\n<b><emoji document_id=5312526098750252863>🚫</emoji>"
            " Stderr:</b>\n<code>"
        ),
        "end": "</code>",
        "auth_fail": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>प्रमाणीकरण विफल, कृपया"
            " पुन: प्रयास करें</b>"
        ),
        "auth_needed": (
            "<emoji document_id=5472308992514464048>🔐</emoji><a"
            ' href="tg://user?id={}">'
            " इंटरैक्टिव प्रमाणीकरण की आवश्यकता है</a>"
        ),
        "auth_msg": (
            "<emoji document_id=5472308992514464048>🔐</emoji> <b>कृपया इस संदेश को</b>"
            " <code>{}</code> <b>के लिए</b> <code>{}</code> <b>कमांड चलाने के लिए"
            " पासवर्ड के रूप में संपादित करें</b>"
        ),
        "auth_locked": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>प्रमाणीकरण विफल, कृपया"
            " बाद में पुन: प्रयास करें</b>"
        ),
        "auth_ongoing": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>प्रमाणीकरण चल रहा"
            " है...</b>"
        ),
        "done": "<emoji document_id=5314250708508220914>✅</emoji> <b>हो गया</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "FLOOD_WAIT_PROTECT",
                2,
                lambda: self.strings("fw_protect"),
                validator=loader.validators.Integer(minimum=0),
            ),
        )
        self.activecmds = {}

    @loader.owner
    @loader.command(
        ru_doc="<команда> - Запустить команду в системе",
        de_doc="<Befehl> - Führt einen Befehl im System aus",
        tr_doc="<komut> - Sistemde komutu çalıştırır",
        hi_doc="<कमांड> - सिस्टम में कमांड चलाएं",
        uz_doc="<buyruq> - Tizimda buyruqni ishga tushiradi",
    )
    async def terminalcmd(self, message):
        """<command> - Execute bash command"""
        await self.run_command(message, utils.get_args_raw(message))

    @loader.owner
    @loader.command(
        ru_doc="Сокращение для '.terminal apt'",
        de_doc="Abkürzung für '.terminal apt'",
        tr_doc="'terminal apt' kısaltması",
        hi_doc="'.terminal apt' के लिए शब्द का छोटा रूप",
        uz_doc="'terminal apt' qisqartmasi",
    )
    async def aptcmd(self, message):
        """Shorthand for '.terminal apt'"""
        await self.run_command(
            message,
            ("apt " if os.geteuid() == 0 else "sudo -S apt ")
            + utils.get_args_raw(message)
            + " -y",
            RawMessageEditor(
                message,
                f"apt {utils.get_args_raw(message)}",
                self.config,
                self.strings,
                message,
                True,
            ),
        )

    async def run_command(
        self,
        message: telethon.tl.types.Message,
        cmd: str,
        editor: typing.Optional[MessageEditor] = None,
    ):
        if len(cmd.split(" ")) > 1 and cmd.split(" ")[0] == "sudo":
            needsswitch = True

            for word in cmd.split(" ", 1)[1].split(" "):
                if word[0] != "-":
                    break

                if word == "-S":
                    needsswitch = False

            if needsswitch:
                cmd = " ".join([cmd.split(" ", 1)[0], "-S", cmd.split(" ", 1)[1]])

        sproc = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=utils.get_base_dir(),
        )

        if editor is None:
            editor = SudoMessageEditor(message, cmd, self.config, self.strings, message)

        editor.update_process(sproc)

        self.activecmds[hash_msg(message)] = sproc

        await editor.redraw()

        await asyncio.gather(
            read_stream(
                editor.update_stdout,
                sproc.stdout,
                self.config["FLOOD_WAIT_PROTECT"],
            ),
            read_stream(
                editor.update_stderr,
                sproc.stderr,
                self.config["FLOOD_WAIT_PROTECT"],
            ),
        )

        await editor.cmd_ended(await sproc.wait())
        del self.activecmds[hash_msg(message)]

    @loader.owner
    async def terminatecmd(self, message):
        """[-f to force kill] - Use in reply to send SIGTERM to a process"""
        if not message.is_reply:
            await utils.answer(message, self.strings("what_to_kill"))
            return

        if hash_msg(await message.get_reply_message()) in self.activecmds:
            try:
                if "-f" not in utils.get_args_raw(message):
                    self.activecmds[
                        hash_msg(await message.get_reply_message())
                    ].terminate()
                else:
                    self.activecmds[hash_msg(await message.get_reply_message())].kill()
            except Exception:
                logger.exception("Killing process failed")
                await utils.answer(message, self.strings("kill_fail"))
            else:
                await utils.answer(message, self.strings("killed"))
        else:
            await utils.answer(message, self.strings("no_cmd"))
