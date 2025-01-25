# ~/mybot/families/miraheze_family.py
# 自定义的Family文件用于Miraheze上的Wiki

from pywikibot import family

class Family(family.Family):

    name = 'miraheze'
    domain = 'miraheze.org'

    def langcodes(self):
        return {
            'zhwpwiki': 'zhwpwiki.miraheze.org',
        }

    def scriptpath(self, code):
        return '/w'

