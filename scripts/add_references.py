# ~/Wind Chimes-bot/scripts/add_references.py
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


def add_missing_references(page_title):
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    page = pywikibot.Page(site, page_title)
    text = page.text

    # 添加<references />标签
    if '<references />' not in text and '<ref>' in text:
        text += '\n<references />'

    # 添加参考资料章节
    if '== 参考资料 ==' not in text and '<ref>' in text:
        text += '\n== 参考资料 ==\n<references />'

    if text != page.text:
        summary = '添加缺失的<references />和参考资料章节'
        page.text = text
        page.save(summary)
        print(f'已添加到页面: {page_title}')
    else:
        print(f'页面 {page_title} 已有<references />和参考资料章节')


# 示例调用
add_missing_references('Talk:茶馆')
