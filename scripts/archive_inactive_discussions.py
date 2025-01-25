# ~/Wind Chimes-bot/scripts/archive_inactive_discussions.py
import pywikibot
from datetime import datetime
import os

# 设置自定义配置文件的路径
config_path = os.path.expanduser('~/Wind Chimes-bot/config/user-config.py')
password_path = os.path.expanduser('~/Wind Chimes-bot/config/user-password.py')
family_path = os.path.expanduser('~/Wind Chimes-bot/families')

# 加载自定义配置文件
with open(config_path, encoding='utf-8') as config_file:
    exec(config_file.read())

# 加载用户名和密码
with open(password_path, encoding='utf-8') as password_file:
    exec(password_file.read())

# 加载自定义 family 文件夹
pywikibot.config.family_files.append(family_path)


def archive_inactive_discussions(page_title, timeout_days=30, archive_base_title='存档'):
    site = pywikibot.Site('zhwpwiki', 'miraheze')
    main_page = pywikibot.Page(site, page_title)
    main_text = main_page.text

    # 获取当前日期
    current_date = datetime.now()
    archive_date_str = current_date.strftime('%Y-%m-%d')
    archive_base_title = f'{main_page.title()}/{archive_base_title}'

    # 创建或获取存档页面
    archive_page_title = f'{archive_base_title}/{current_date.strftime("%Y")}'
    archive_page = pywikibot.Page(site, archive_page_title)

    # 获取或创建存档页面的文本
    if not archive_page.exists():
        archive_text = ''
    else:
        archive_text = archive_page.text

    # 提取超过timeout_days天未活跃的讨论
    sections = main_page.getSections()
    archived_sections = []

    for section in sections:
        section_title = section['title']
        section_text = section['text']

        # 获取每个段落的最后编辑时间
        section_edit_time = main_page.lastNodeTimestamp(section_title)

        if section_edit_time and (current_date - section_edit_time).days > timeout_days:
            archived_section = f'\n== {section_title} (存档于 {archive_date_str}) ==\n{section_text}\n'
            archived_sections.append(archived_section)
            # 从主页面文本中删除已存档的段落
            main_text = main_text.replace(section_text, '')

    # 将存档的段落添加到存档页面
    if archived_sections:
        new_archive_text = f'{{{{存档}}}}\n' + ''.join(archived_sections)
        archive_page.text = new_archive_text
        archive_page.save(f'自动存档超过{timeout_days}天未活跃的讨论')
        print(f'已存档到页面: {archive_page_title}')

        # 更新主页面文本
        main_page.text = main_text
        main_page.save(f'删除超过{timeout_days}天未活跃的讨论')
        print(f'已清理主页面: {page_title}')
    else:
        print(f'页面 {page_title} 没有超过{timeout_days}天未活跃的讨论')


# 示例调用
archive_inactive_discussions('Zhwpwiki talk:茶馆')

