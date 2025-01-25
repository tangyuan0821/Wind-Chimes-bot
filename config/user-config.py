# ~/mybot/config/user-config.py
# 这个文件用于配置Pywikibot的各种参数

# 设置站点的信息
family = 'miraheze'
mylang = 'zhwpwiki'

# 设置站点的URL
site = {
    'miraheze': {
        'url': 'https://zhwpwiki.miraheze.org',
        'path': '/w/api.php',
    }
}

# 设置日志文件路径
log = {
    'filename': '~/Wind Chimes-bot/logs/pywikibot.log',
}

# 设置日志级别
loglevel = 'INFO'

# 设置是否自动登录
autopatrol = True

# 设置是否自动确认编辑
autocreate = True

# 设置使用哪个编辑器（例如：vim, nano, 或者默认编辑器）
editor = 'default'

# 设置是否允许机器人在页面上进行编辑
use_tracking = True

# 设置是否允许机器人创建页面
allow_serve = True

# 设置是否使用缓存
use_cache = True

# 设置是否允许使用2FA（如果需要）
use_2fa = True

# 其他自定义配置可以在这里添加
