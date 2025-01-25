# ~/Wind Chimes-bot/scripts/find_broken_links.py
import pywikibot
import os
import requests
from requests.exceptions import RequestException

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


def find_broken_links(page_title):
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    page = pywikibot.Page(site, page_title)
    text = page.text

    # 提取所有外部链接
    external_links = [link for link in page.externallinks()]

    broken_links = []
    for url in external_links:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                broken_links.append(url)
        except RequestException as e:
            broken_links.append(url)
            print(f'请求 {url} 时出错: {e}')

    return broken_links


# 示例调用
broken_links = find_broken_links('Talk:茶馆')
print('发现的断链：', broken_links)

