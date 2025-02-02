import mwclient
from datetime import datetime, timedelta
import dateutil.parser
import pytz
import logging
import time
import os

# 配置信息类
class Config:
    def __init__(self):
        self.USERNAME = os.environ.get('WIKI_USERNAME')
        self.PASSWORD = os.environ.get('WIKI_PASSWORD')
        self.WIKI_URL = 'zhwpwiki.miraheze.org'
        self.PAGES_TO_WATCH = [
            'Zhwpwiki talk:管理员告示板',
            'Zhwpwiki talk:权限申请',
            'Zhwpwiki talk:茶馆'
        ]
        self.ARCHIVE_DAYS = 7  # 默认存档时间
        self.SPECIAL_RULES = {
            'Zhwpwiki talk:茶馆': {
                'archive_days': 30,  # 茶馆30天存档
                'archive_path': '历史记录'  # 茶馆使用不同的存档路径
            }
        }
        self.LOG_DIR = 'logs'  # 日志文件目录
        self.LOG_FILE = os.path.join(self.LOG_DIR, 'archive_bot.log')  # 日志文件路径
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 60  # 秒

# 工具类，包含一些辅助函数
class Utils:
    @staticmethod
    def get_timestamp():
        """获取当前时间戳"""
        return datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

    @staticmethod
    def add_signature(text, username):
        """添加自动签名"""
        timestamp = Utils.get_timestamp()
        signature = f"\n\n<!-- 由{username}于{timestamp}自动存档 -->"
        return text + signature

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_archive_settings(page_title, default_days, special_rules):
        """获取页面特定的存档设置"""
        if page_title in special_rules:
            return special_rules[page_title]
        return {
            'archive_days': default_days,
            'archive_path': '存档'
        }

# 主程序类，负责处理存档任务
class ArchiveBot:
    def __init__(self, config):
        self.config = config
        # 创建日志目录（如果不存在）
        if not os.path.exists(self.config.LOG_DIR):
            os.makedirs(self.config.LOG_DIR)
        # 配置日志系统
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        # 初始化Wiki连接
        self.site = mwclient.Site(self.config.WIKI_URL, path='/w/')
        self.site.login(self.config.USERNAME, self.config.PASSWORD)
        self.logger.info(f"登录成功！当前用户：{self.site.username}")

    def safe_edit(self, page, text, summary, max_retries=None):
        """带重试机制的编辑函数"""
        if max_retries is None:
            max_retries = self.config.MAX_RETRIES
        for attempt in range(max_retries):
            try:
                # 获取当前页面时间戳用于防冲突
                base_timestamp = page.revision['timestamp']
                page.edit(text=text, summary=summary, basetimestamp=base_timestamp)
                return True
            except mwclient.errors.APIError as e:
                if 'editconflict' in str(e).lower():
                    self.logger.warning(f"编辑冲突，尝试重新加载页面 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(self.config.RETRY_DELAY)
                    page = self.site.pages[page.name]  # 重新加载页面
                    continue
                self.logger.error(f"编辑失败: {str(e)}")
                return False
            except Exception as e:
                self.logger.error(f"未知错误: {str(e)}")
                return False
        self.logger.error(f"达到最大重试次数 {max_retries}，放弃编辑")
        return False

    def archive_page(self, page_title):
        """处理单个页面存档"""
        try:
            page = self.site.pages[page_title]
            if not page.exists:
                self.logger.warning(f"页面 {page_title} 不存在，跳过处理")
                return

            settings = Utils.get_archive_settings(page_title, self.config.ARCHIVE_DAYS, self.config.SPECIAL_RULES)
            current_year = datetime.now().year
            archive_page_title = f"{page_title}/{settings['archive_path']}/{current_year}"

            text = page.text()
            sections = Utils.parse_sections(text)

            archive_page = self.site.pages[archive_page_title]
            new_content = []
            archived_content = []

            cutoff_time = datetime.now(pytz.utc) - timedelta(days=settings['archive_days'])

            for content, title in sections:
                last_active = Utils.get_last_active(content)

                if last_active < cutoff_time:
                    archived_content.append(f"== {title} ==\n{content}\n")
                else:
                    new_content.append(f"== {title} ==\n{content}\n")

            if archived_content:
                # 更新存档页面
                archive_text = archive_page.text() or ''
                new_archive_text = Utils.add_signature('\n'.join(archived_content) + '\n' + archive_text, self.config.USERNAME)
                if self.safe_edit(archive_page, new_archive_text, f'Bot: 存档{len(archived_content)}个旧讨论'):
                    self.logger.info(f"成功存档 {len(archived_content)} 个讨论到 {archive_page_title}")

                # 更新原页面
                new_page_text = Utils.add_signature('\n'.join(new_content), self.config.USERNAME)
                if self.safe_edit(page, new_page_text, f'Bot: 移除{len(archived_content)}个已存档讨论'):
                    self.logger.info(f"成功更新 {page_title}，移除 {len(archived_content)} 个讨论")
            else:
                self.logger.info(f"{page_title} 没有需要存档的内容")

        except Exception as e:
            self.logger.error(f"处理 {page_title} 时出错：{str(e)}", exc_info=True)

    def run(self):
        """执行存档任务"""
        self.logger.info("开始存档任务...")
        for page_title in self.config.PAGES_TO_WATCH:
            self.archive_page(page_title)
        self.logger.info("存档任务完成")

if __name__ == '__main__':
    config = Config()
    bot = ArchiveBot(config)
    bot.run()