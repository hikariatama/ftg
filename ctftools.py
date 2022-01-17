"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""


#<3 title: CTF Toolkit
#<3 pic: https://img.icons8.com/fluency/48/000000/user-credentials.png
#<3 desc: Базовые инструменты, которые могут пригодиться на низкосортных CTF соревах


from .. import loader, utils
import os
import time
import io

@loader.tds
class CTFToolsMod(loader.Module):
    """CTF Toolkit."""
    strings = {"name": "CTF Toolkit", 
    'processing': "<b>📤 Обработка...</b>",
    'file_not_specified': "<b>Мне какой файл читать, не подскажешь?... 🗿</b>",
    'read_error': '<b>🗿 Ошибка чтения файла</b>'}
    async def filetypecmd(self, message):
        """Linux File command wrapper"""
        reply = await message.get_reply_message()
        message = await utils.answer(message, self.strings('processing', message))
        if not reply and type(message.media) is None:
            await utils.answer(message, self.strings('file_not_specified', message))
            return
        if not reply:
            media = message.media
            print(media)
        else:
            media = reply.media

        filename = '/tmp/' + str(round(time.time())) + '.scan'

        file = await message.client.download_file(media)
        try:
            open(filename, 'wb').write(file)

            res = str(os.popen('file ' + filename).read()).replace(filename + ': ', '')
            os.system('rm -rf ' + filename)

            await utils.answer(message, '<code>' + res + '</code>')
        except:
            await utils.answer(message, self.strings('read_error', message))

    async def stringscmd(self, message):
        """Linux Strings | grep . command wrapper"""
        await utils.answer(message, self.strings('processing', message))
        args = utils.get_args_raw(message)
        grep = '' if args == '' else ' | grep ' + args
        reply = await message.get_reply_message()
        if not reply and type(message.media) is None:
            await utils.answer(message, self.strings('file_not_specified', message))
            return
        if not reply:
            media = message.media
            print(media)
        else:
            media = reply.media

        filename = '/tmp/' + str(round(time.time()))

        file = await message.client.download_file(media)
        try:
            open(filename, 'wb').write(file)

            res = str(os.popen('strings ' + filename + grep).read())
            os.system('rm -rf ' + filename)
            try:
                await utils.answer(message, '<code>' + res + '</code>')
            except:
                txt = io.BytesIO(res.encode('utf-8'))
                txt.name = "strings_result.txt"
                await message.delete()
                await message.client.send_file(message.to_id, txt)
        except:
            await utils.answer(message, self.strings('read_error', message))
