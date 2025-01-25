# ~/Wind Chimes-bot/scripts/remove_protection_templates.py
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


def remove_protection_templates(page_title):
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    page = pywikibot.Page(site, page_title)
    text = page.text

    # 示例：删除未被保护的页面上的保护模板
    # 注意：实际操作时需要根据保护模板的具体名称来调整
    if not page.isProtected():
        text = text.replace('{{保护}}', '')
        text = text.replace('{{受保护}}', '')
        if text != page.text:
            summary = '删除未被保护页面上的保护模板'
            page.text = text
            page.save(summary)
            print(f'已删除页面 {page_title} 上的保护模板')
        else:
            print(f'页面 {page_title} 没有需要删除的保护模板')
    else:
        print(f'页面 {page_title} 已被保护，跳过删除')


# 示例调用
remove_protection_templates('Talk:茶馆')
