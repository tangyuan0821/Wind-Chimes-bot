# miraheze_family.py
from pywikibot import family

class MirahezeFamily(family.Family):
    def __init__(self):
        self.name = 'miraheze'  # Family 名称
        self.langs = {
            'zhwpwiki': 'https://zhwpwiki.miraheze.org/w/api.php',  # 站点的 API URL
        }

# 将该 family 注册到 pywikibot 中
pywikibot.site._families['miraheze'] = MirahezeFamily()
