import pywikibot
import datetime
import os
from miraheze_family import MirahezeFamily  # 导入自定义的 Family 类



username = os.getenv('WIKI_USERNAME')
password = os.getenv('WIKI_PASSWORD')
print(f"用户名：{username}")  # 确保用户名环境变量传递正确

if not username or not password:
    raise ValueError("缺少用户名或密码，请检查 GitHub Secrets 设置")

# 手动注册自定义的 Family
pywikibot.site._families['miraheze'] = MirahezeFamily()


# 配置站点
site = pywikibot.Site()

# 登录
site.login('Wind Chimes-bot', 'MHM1008BOT')
# 需要存档的页面列表
pages_to_archive = [
    'zhwpwiki_talk:茶馆',
    'zhwpwiki_talk:权限申请',
    'zhwpwiki_talk:管理员告示板'
]

def archive_page(page_name):
    # 获取页面内容
    page = pywikibot.Page(site, page_name)
    content = page.text

    # 获取当前日期，作为存档的标题
    archive_title = f"{page_name}/存档/2025"
    
    # 检查存档页面是否已存在
    archive_page = pywikibot.Page(site, archive_title)
    if not archive_page.exists():
        # 创建存档页面
        archive_page.text = content
        archive_page.save(f"自动存档: {archive_title}")
    else:
        print(f"存档页面 {archive_title} 已存在，跳过存档.")

def main():
    for page_name in pages_to_archive:
        print(f"开始存档 {page_name} ...")
        archive_page(page_name)

if __name__ == '__main__':
    main()
