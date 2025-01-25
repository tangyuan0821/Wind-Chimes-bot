# ~/Wind Chimes-bot/scripts/suggest_convert_to_lua.py
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

def suggest_convert_to_lua():
    # 示例：查找高消耗模板并建议转换为Lua
    # 注意：这需要更复杂的逻辑来分析模板的使用情况
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    high_consumption_templates = []  # 这里需要添加具体的高消耗模板列表
    for template_title in high_consumption_templates:
        template_page = pywikibot.Page(site, f'Template:{template_title}')
        if template_page.exists():
            print(f'建议将 {template_title} 转换为Lua')
        else:
            print(f'模板 {template_title} 不存在')

# 示例调用
suggest_convert_to_lua()
