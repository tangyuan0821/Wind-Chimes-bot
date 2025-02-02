# miraheze_family.py
from pywikibot import family

class MirahezeFamily(family.Family):
    def __init__(self):
        self.name = 'miraheze'  # Family 名称
        self.langs = {
            'zhwpwiki': 'https://zhwpwiki.miraheze.org/w/api.php',  # 站点的 API URL
        }
    def __init__(self):
        """不要直接实例化，使用 pywikibot 的内部机制来初始化"""
        self.languages = self.langs

    @classmethod
    def getSite(cls, code, **kwargs):
        """返回一个站点实例，避免直接实例化 MirahezeFamily"""
        return super().getSite(code, **kwargs)

# 将该 family 注册到 pywikibot 中
#pywikibot.site._families['miraheze'] = MirahezeFamily()
