"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Dyslexia
#<3 pic: https://img.icons8.com/fluency/48/000000/filled-like.png
#<3 desc: Показывает, как бы текст увидел человек с дислексией


from .. import loader, utils
from random import shuffle
import re


@loader.tds
class DyslexiaMod(loader.Module):
	"""Show, how people with dyslexia see the world"""
	strings = {
		"name": "Dyslexia",
		"no_text": "🎈 <b>You need to provide text</b>"
	}
	@loader.unrestricted
	async def dyslexcmd(self, message):
		"""<text | reply> - Show, how people with dyslexia would have seen this text"""
		args = utils.get_args_raw(message)
		if not args:
			try:
				args = (await message.get_reply_message()).text
			except:
				return await utils.answer(message, self.strings('no_text'))

		res = ""
		for word in args.split():
			newline = False
			if '\n' in word:
				word = word.replace('\n', '')
				newline = True

			to_shuffle = re.sub(r'[^a-zA-Zа-яА-Я]', '', word)[1:-1]
			shuffled = list(to_shuffle)
			shuffle(shuffled)

			res += word.replace(to_shuffle, ''.join(shuffled)) + " "
			if newline: res += "\n"

		return await utils.answer(message, res)


