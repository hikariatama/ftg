import os

for file in os.scandir('C:\\Users\\innoc\\ftg'):
	if file.path.endswith('.py'):
		content = open(file.path, 'r', encoding='utf-8').read()
		if 'hikariatama' in content:
			open(file.path, 'w', encoding='utf-8').write(content.replace('hikariatama', 'hikariatama'))
			print(f"Processed {file.path}")
