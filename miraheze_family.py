# miraheze_family.py
from pywikibot import family

class MirahezeFamily(family.Family):
    def __init__(self):
        self.name = 'miraheze'  # Family 名称
        self.langs = {
            'zhwpwiki': 'https://zhwpwiki.miraheze.org/w/api.php',  # 站点的 API URL
        }
    @classmethod
    def __post_init__(cls):
        # 在这里设置 family 的语言和 API 端点
        cls.languages = cls.langs

# 将该 family 注册到 pywikibot 中
pywikibot.site._families['miraheze'] = MirahezeFamily()
