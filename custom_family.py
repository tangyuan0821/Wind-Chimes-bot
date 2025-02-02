from pywikibot import family

class Family(family.Family):
    name = 'miraheze'
    langs = {
        'zhwpwiki': 'zhwpwiki.miraheze.org',
    }

    def protocol(self, code):
        return 'https'

    def scriptpath(self, code):
        return '/w'
