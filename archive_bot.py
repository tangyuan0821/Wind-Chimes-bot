import mwclient
from datetime import datetime, timedelta
import dateutil.parser
import pytz
import logging
import time
import os

# 配置信息
USERNAME = os.environ['WIKI_USERNAME']
PASSWORD = os.environ['WIKI_PASSWORD']
WIKI_URL = 'zhwpwiki.miraheze.org'
PAGES_TO_WATCH = [
    'Zhwpwiki talk:管理员告示板',
    'Zhwpwiki talk:权限申请',
    'Zhwpwiki Talk:茶馆'
]
ARCHIVE_DAYS = 7  # 默认存档时间
SPECIAL_RULES = {
    'Zhwpwiki Talk:茶馆': {
        'archive_days': 30,  # 茶馆30天存档
        'archive_path': '历史记录'  # 茶馆使用不同的存档路径
    }
}
LOG_DIR = 'logs'  # 日志文件目录
LOG_FILE = os.path.join(LOG_DIR, 'archive_bot.log')  # 日志文件路径
MAX_RETRIES = 3
RETRY_DELAY = 60  # 秒

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
site = mwclient.Site(WIKI_URL, path='/w/')
site.login(USERNAME, PASSWORD)
logger.info(f"登录成功！当前用户：{site.username}")


def get_timestamp():
    """获取当前时间戳"""
    return datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')


def add_signature(text):
    """添加自动签名"""
    timestamp = get_timestamp()
    signature = f"\n\n<!-- 由{USERNAME}于{timestamp}自动存档 -->"
    return text + signature


def parse_sections(text):
    """解析页面章节"""
    sections = []
    current_section = []
    section_title = None
    for line in text.split('\n'):
        if line.startswith('=='):
            if section_title is not None:
                sections.append(('\n'.join(current_section), section_title))
                current_section = []
            section_title = line.strip('= ').strip()
        else:
            current_section.append(line)
    if section_title:
        sections.append(('\n'.join(current_section), section_title))
    return sections


def get_last_active(section_text):
    """获取章节最后活跃时间"""
    timestamps = []
    for line in section_text.split('\n'):
        if line.startswith('<!--'):
            try:
                ts_str = line.split('Timestamp:')[1].split('-->')[0].strip()
                timestamps.append(dateutil.parser.parse(ts_str))
            except:
                continue
    return max(timestamps) if timestamps else datetime.now(pytz.utc)


def get_archive_settings(page_title):
    """获取页面特定的存档设置"""
    if page_title in SPECIAL_RULES:
        return SPECIAL_RULES[page_title]
    return {
        'archive_days': ARCHIVE_DAYS,
        'archive_path': '存档'
    }


def safe_edit(page, text, summary, max_retries=MAX_RETRIES):
    """带重试机制的编辑函数"""
    for attempt in range(max_retries):
        try:
            # 获取当前页面时间戳用于防冲突
            base_timestamp = page.revision['timestamp']
            page.edit(text=text, summary=summary, basetimestamp=base_timestamp)
            return True
        except mwclient.errors.APIError as e:
            if 'editconflict' in str(e).lower():
                logger.warning(f"编辑冲突，尝试重新加载页面 (尝试 {attempt + 1}/{max_retries})")
                time.sleep(RETRY_DELAY)
                page = site.pages[page.name]  # 重新加载页面
                continue
            logger.error(f"编辑失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return False
    logger.error(f"达到最大重试次数 {max_retries}，放弃编辑")
    return False


def archive_page(page_title):
    """处理单个页面存档"""
    try:
        page = site.pages[page_title]
        if not page.exists:
            logger.warning(f"页面 {page_title} 不存在，跳过处理")
            return

        settings = get_archive_settings(page_title)
        current_year = datetime.now().year
        archive_page_title = f"{page_title}/{settings['archive_path']}/{current_year}"

        text = page.text()
        sections = parse_sections(text)

        archive_page = site.pages[archive_page_title]
        new_content = []
        archived_content = []

        cutoff_time = datetime.now(pytz.utc) - timedelta(days=settings['archive_days'])

        for content, title in sections:
            last_active = get_last_active(content)

            if last_active < cutoff_time:
                archived_content.append(f"== {title} ==\n{content}\n")
            else:
                new_content.append(f"== {title} ==\n{content}\n")

        if archived_content:
            # 更新存档页面
            archive_text = archive_page.text() or ''
            new_archive_text = add_signature('\n'.join(archived_content) + '\n' + archive_text)
            if safe_edit(archive_page, new_archive_text, f'Bot: 存档{len(archived_content)}个旧讨论'):
                logger.info(f"成功存档 {len(archived_content)} 个讨论到 {archive_page_title}")

            # 更新原页面
            new_page_text = add_signature('\n'.join(new_content))
            if safe_edit(page, new_page_text, f'Bot: 移除{len(archived_content)}个已存档讨论'):
                logger.info(f"成功更新 {page_title}，移除 {len(archived_content)} 个讨论")
        else:
            logger.info(f"{page_title} 没有需要存档的内容")

    except Exception as e:
        logger.error(f"处理 {page_title} 时出错：{str(e)}", exc_info=True)


# 执行存档任务
if __name__ == '__main__':
    logger.info("开始存档任务...")
    for page_title in PAGES_TO_WATCH:
        archive_page(page_title)
    logger.info("存档任务完成")