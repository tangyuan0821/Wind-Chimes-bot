# ~/Wind Chimes-bot/scripts/fix_spelling_errors.py
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


def fix_spelling_errors(page_title):
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    page = pywikibot.Page(site, page_title)
    text = page.text

    # 示例：修正常见拼写错误
    # 注意：实际操作时需要根据错误的具体情况进行调整
    text = text.replace('受保護', '受保护')

    if text != page.text:
        summary = '修正常见拼写错误'
        page.text = text
        page.save(summary)
        print(f'已修正页面: {page_title}')
    else:
        print(f'页面 {page_title} 没有需要修正的常见拼写错误')


# 示例调用
fix_spelling_errors('Talk:茶馆')
