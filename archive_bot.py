import mwclient
import datetime
import os
import dateutil.parser
import pytz
import logging
import time

# 引入自定义家族
import custom_family


username = os.getenv('WIKI_USERNAME')
password = os.getenv('WIKI_PASSWORD')
wiki_url = 'zhwpwiki.miraheze.org'

print(f"用户名：{username}")  # 确保用户名环境变量传递正确

if not username or not password:
    raise ValueError("缺少用户名或密码，请检查 GitHub Secrets 设置")

# 手动注册自定义的 Family
#pywikibot.site._families['miraheze'] = MirahezeFamily()



#site = custom_family.Family().site('zhwpwiki')
#site.login(username, password)
#logger.info(f"登录成功！当前用户：{site.username}")
# 需要存档的页面列表
pages_to_archive = [
    'zhwpwiki_talk:茶馆',
    'zhwpwiki_talk:权限申请',
    'zhwpwiki_talk:管理员告示板'
]

def archive_page(page_name):
    global site
    # 获取页面内容
    page = site.pages[page_name]
    content = page.text

    # 获取当前日期，作为存档的标题
    archive_title = f"{page_name}/存档/2025"
    
    # 检查存档页面是否已存在
   # archive_page = pywikibot.Page(site, archive_title)
    archive_page = site.pages[archive_title]  # 替换为 mwclient 的方式
    if not archive_page.exists():
        # 创建存档页面
        archive_page.text = content
        archive_page.save(f"自动存档: {archive_title}")
    else:
        print(f"存档页面 {archive_title} 已存在，跳过存档.")

# 主函数部分，确保调用正常
def main():
    global logger
    logger.info("开始存档任务...")
    for page_name in pages_to_archive:
        archive_page(page_name)
    logger.info("存档任务完成")


if __name__ == '__main__':
    main()

# 创建日志目录（如果不存在）
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化Wiki连接
site = mwclient.Site(wiki_url, path='/w/')  # 修改这里
site.login(username, password)
logger.info(f"登录成功！当前用户：{site.username}")

