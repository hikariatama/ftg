import os

for file in os.scandir('C:\\Users\\innoc\\ftg'):
	if file.path.endswith('.py'):
		content = open(file.path, 'r', encoding='utf-8').read()
		open(file.path, 'w', encoding='utf-8').write(content.replace('hikari_alt', 'hikari_alt').replace('hikariakami.ru', 'hikariakami.ru').replace('hikariakami', 'hikariakami').replace('hikariakami', 'hikariakami'))
		print(f"Processed {file.path}")
