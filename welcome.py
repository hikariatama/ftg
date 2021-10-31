"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Welcome
#<3 pic: https://img.icons8.com/fluency/48/000000/enter-2.png
#<3 desc: Приветствие новых участников чатов


from .. import loader, utils


@loader.tds
class WelcomeMod(loader.Module):
	"""Приветствие новых пользователей в чате."""
	strings = {'name': 'Welcome',
	'welcome': '🦊 <b>Теперь я буду приветствовать здесь людей</b>', 
	'chat_not_found': '🦊 <b>Я не приветствую людей в этом чате</b>', 
	'unwelcome': '🦊 <b>Теперь я не буду приветствовать здесь людей</b>'}

	async def client_ready(self, client, db):
		self.db = db
		self.client = client
		self.welcome = db.get('Welcome', 'welcome', {})

	async def welcomecmd(self, message):
		"""Включить \\ изменить приветственный текст в текущем чате"""
		cid = utils.get_chat_id(message)
		args = utils.get_args_raw(message)
		
		self.welcome[cid] = args
		self.db.set('Welcome', 'welcome', self.welcome)
		await utils.answer(message, self.strings('welcome', message))

	async def unwelcomecmd(self, message):
		"""Отключить приветственный текст в текущем чате"""
		cid = utils.get_chat_id(message)
		args = utils.get_args_raw(message)
		
		if cid not in self.welcome:
			await utils.answer(message, self.strings('chat_not_found', message))
			return

		del self.welcome[cid]
		self.db.set('Welcome', 'welcome', self.welcome)
		await utils.answer(message, self.strings('unwelcome', message))

	async def watcher(self, message):
		# try:
		cid = utils.get_chat_id(message)
		if cid not in self.welcome:
			return

		if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
			user = await message.get_user()
			chat = await message.get_chat()
			await self.client.send_message(cid, self.welcome[cid].replace('{user}', user.first_name).replace('{chat}', chat.title).replace('{mention}', '<a href="tg://user?id=' + str(user.id) + '">' + user.first_name + '</a>'))
			await message.delete()