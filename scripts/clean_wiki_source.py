# ~/Wind Chimes-bot/scripts/clean_wiki_source.py
import pywikibot
import re
import os

# 设置自定义配置文件的路径
config_path = os.path.expanduser('~/Wind Chimes-bot/config/user-config.py')
password_path = os.path.expanduser('~/Wind Chimes-bot/config/user-password.py')
family_path = os.path.expanduser('~/Wind Chimes-bot/families')

# 加载自定义配置文件
pywikibot.config.execute(config_path)

# 加载用户名和密码
pywikibot.config.usernames.update(pywikibot.UserPasswordManager(password_path).load())

# 加载自定义 family 文件夹
pywikibot.config.family_files.append(family_path)

# 初始化站点
site = pywikibot.Site('zhwpwiki', 'miraheze')
page = pywikibot.Page(site, '页面标题')
text = page.text

# 删除多余的空格
text = re.sub(r'\s+', ' ', text)

# 格式化表格（假设表格使用{| ... |}格式）
text = re.sub(r'\{\|', '{|\n', text)
text = re.sub(r'\|\}', '\n|}', text)
text = re.sub(r'\|([^\n])', r'|\n\1', text)

page.text = text
page.save(summary='使wiki源代码更美观整洁')
