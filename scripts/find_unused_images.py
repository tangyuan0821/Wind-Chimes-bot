# ~/Wind Chimes-bot/scripts/find_unused_images.py
import pywikibot
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

def find_unused_images():
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    unused_images = []
    for image in site.allimages(filterredir='nonredirects'):
        if not list(image.linkedPages()):
            unused_images.append(image.title())
    return unused_images

# 示例调用
unused_images = find_unused_images()
print('未使用的媒体文件：', unused_images)
