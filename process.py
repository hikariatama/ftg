import os
import re
for mod in os.scandir('.'):
	if not mod.path.endswith('.py'): continue
	# print(mod.path)
	code = open(mod.path, 'r', encoding='utf-8').read()
	code = re.sub(r'([ \t]*async def .*?cmd.*?\n[ \t]*""")[.][^ ]*? (- )?', r'\1', code)
	print(code)
	# if input('? - ') == 'n':
		# break
	open(mod.path, 'w', encoding='utf-8').write(code)
