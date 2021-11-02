"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Web2Zip
#<3 pic: https://img.icons8.com/fluency/48/000000/winrar.png
#<3 desc: Скачивает файл из ссылки и отправляет в виде архива


from .. import loader, utils
import io
import requests

@loader.tds
class Web2zipMod(loader.Module):
	"""Пакует файл из ссылки в архив"""
	strings = {'name': 'Web2zip',
	'no_args': '🦊 <b>Укажи ссылку</b>',
	'fetch_error': '🦊 <b>Ошибка скачивания файла</b>',
	'loading': '🦊 <b>Загрузка...</b>'}

	async def web2zipcmd(self, message):
		""".web2zip <ссылка на сайт> - Запаковать файл из сайта в архив"""
		website = utils.get_args_raw(message)
		if not website:
			await utils.answer(message, self.strings('no_args', message))
			return
		try:
			f = io.BytesIO(requests.get(website).content)
		except:
			await utils.answer(message, self.strings('fetch_error', message))
			return

		f.name = website.split('/')[-1]

		await message.respond(file=f)
		await message.delete()
