import mwclient
from datetime import datetime, timedelta
import dateutil.parser
import pytz
import logging
import time
import os
from collections import OrderedDict
from textwrap import fill

# 配置信息
USERNAME = os.environ['WIKI_USERNAME']
PASSWORD = os.environ['WIKI_PASSWORD']
WIKI_URL = 'zhwpwiki.miraheze.org'
PAGES_TO_WATCH = [
    'Zhwpwiki talk:管理员告示板',
    'Zhwpwiki talk:权限申请',
    'Zhwpwiki talk:茶馆'
]
ARCHIVE_DAYS = 7  # 默认存档时间
SPECIAL_RULES = {
    'Zhwpwiki talk:茶馆': {
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


class DiscussionThread:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.timestamp = self._get_timestamp()

    def _get_timestamp(self):
        timestamps = []
        for line in self.content.split('\n'):
            if line.startswith('<!--'):
                try:
                    ts_str = line.split('Timestamp:')[1].split('-->')[0].strip()
                    timestamps.append(dateutil.parser.parse(ts_str))
                except:
                    continue
        return max(timestamps) if timestamps else datetime.now(pytz.utc)

    def size(self):
        return len(self.title.encode('utf-8')) + len(self.content.encode('utf-8')) + 12

    def to_text(self):
        return f'== {self.title} ==\n\n{self.content}'


class DiscussionPage:
    def __init__(self, page, settings):
        self.page = page
        self.settings = settings
        self.threads = []
        self.header = ''
        self.load_page()

    def load_page(self):
        if not self.page.exists:
            logger.warning(f"页面 {self.page.name} 不存在，跳过处理")
            return
        text = self.page.text()
        sections = self.parse_sections(text)
        for content, title in sections:
            thread = DiscussionThread(title, content)
            self.threads.append(thread)

    def parse_sections(self, text):
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


class PageArchiver:
    def __init__(self, page, settings):
        self.page = DiscussionPage(page, settings)
        self.settings = settings
        self.now = datetime.now(pytz.utc)
        self.archived_threads = 0
        self.archive_page_title = self._get_archive_page_title()
        self.archive_page = site.pages[self.archive_page_title]

    def _get_archive_page_title(self):
        current_year = datetime.now().year
        return f"{self.page.page.name}/{self.settings['archive_path']}/{current_year}"

    def analyze_page(self):
        cutoff_time = self.now - timedelta(days=self.settings['archive_days'])
        keep_threads = []
        archived_threads = []
        for thread in self.page.threads:
            if thread.timestamp < cutoff_time:
                archived_threads.append(thread)
            else:
                keep_threads.append(thread)
        self.archived_threads = len(archived_threads)
        return keep_threads, archived_threads

    def get_timestamp(self):
        return datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

    def add_signature(self, text):
        timestamp = self.get_timestamp()
        signature = f"\n\n<!-- 由{USERNAME}于{timestamp}自动存档 -->"
        return text + signature

    def safe_edit(self, page, text, summary, max_retries=MAX_RETRIES):
        for attempt in range(max_retries):
            try:
                base_timestamp = page.revision['timestamp']
                page.edit(text=text, summary=summary, basetimestamp=base_timestamp)
                return True
            except mwclient.errors.APIError as e:
                if 'editconflict' in str(e).lower():
                    logger.warning(f"编辑冲突，尝试重新加载页面 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(RETRY_DELAY)
                    page = site.pages[page.name]
                    continue
                logger.error(f"编辑失败: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"未知错误: {str(e)}")
                return False
        logger.error(f"达到最大重试次数 {max_retries}，放弃编辑")
        return False

    def run(self):
        keep_threads, archived_threads = self.analyze_page()
        if archived_threads:
            # 更新存档页面
            archive_text = self.archive_page.text() or ''
            new_archive_text = self.add_signature('\n'.join([t.to_text() for t in archived_threads]) + '\n' + archive_text)
            if self.safe_edit(self.archive_page, new_archive_text, f'Bot: 存档{len(archived_threads)}个旧讨论'):
                logger.info(f"成功存档 {len(archived_threads)} 个讨论到 {self.archive_page_title}")

            # 更新原页面
            new_page_text = self.add_signature('\n'.join([t.to_text() for t in keep_threads]))
            if self.safe_edit(self.page.page, new_page_text, f'Bot: 移除{len(archived_threads)}个已存档讨论'):
                logger.info(f"成功更新 {self.page.page.name}，移除 {len(archived_threads)} 个讨论")
        else:
            logger.info(f"{self.page.page.name} 没有需要存档的内容")


def get_archive_settings(page_title):
    if page_title in SPECIAL_RULES:
        return SPECIAL_RULES[page_title]
    return {
        'archive_days': ARCHIVE_DAYS,
        'archive_path': '存档'
    }


# 执行存档任务
if __name__ == '__main__':
    logger.info("开始存档任务...")
    for page_title in PAGES_TO_WATCH:
        page = site.pages[page_title]
        settings = get_archive_settings(page_title)
        archiver = PageArchiver(page, settings)
        archiver.run()
    logger.info("存档任务完成")
