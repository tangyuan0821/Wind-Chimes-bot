# ~/Wind Chimes-bot/families/__init__.py
# 这个文件确保 families 文件夹被视为一个包

# 您可以在这里添加一些包级别的初始化代码
# 例如，确保所有必要的模块都被导入
from .miraheze_family import Family

# 加载自定义配置文件
import pywikibot
import os




# 设置自定义配置文件的路径
config_path = os.path.expanduser('~/Wind Chimes-bot/config/user-config.py')
password_path = os.path.expanduser('~/Wind Chimes-bot/config/user-password.py')
family_path = os.path.expanduser('~/Wind Chimes-bot/families')

# 加载自定义配置文件
pywikibot.config.execute(config_path)

# 加载用户名和密码
pywikibot.config.usernames.update(pywikibot.NoUserConfigManager(password_path).load())

# 加载自定义 family 文件夹
pywikibot.config.family_files.append(family_path)



