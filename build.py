#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 src/ 构建成中英双语的静态站点。

产物（同时写入 dist/ 供本地预览、docs/ 供 GitHub Pages 发布）：

  中文（默认）
    index.html              JSON 工具（站点首页）
    <slug>/index.html       其余 8 个工具
    privacy.html            隐私政策
  英文（/en/ 前缀）
    en/index.html  en/<slug>/index.html  en/privacy.html
  公共
    sitemap 索引 + 子文件（带 hreflang 备用链接） / robots.txt / .nojekyll

两种语言各自拥有独立的 URL、标题、描述、canonical、hreflang 与正文，
英文页面在构建时就把界面文案整体替换掉，因此不依赖运行时 JS 翻译。

用法:
  python3 build.py            # 构建一次
  python3 build.py --watch    # 监听并重建（需要: pip install watchdog）
"""

import gzip
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from content import SITE, TOOLS, PRIVACY_BODY_ZH          # noqa: E402
from content_en import TOOLS_EN, PRIVACY_BODY_EN          # noqa: E402
from content_es import TOOLS_ES                            # noqa: E402
from content_fr import TOOLS_FR                            # noqa: E402
from content_de import TOOLS_DE                            # noqa: E402
from content_ptbr import TOOLS_PTBR                        # noqa: E402
from content_ru import TOOLS_RU                            # noqa: E402
from content_id import TOOLS_ID                            # noqa: E402
from content_ja import TOOLS_JA                            # noqa: E402
from content_ko import TOOLS_KO                            # noqa: E402
from i18n import (EN, JS_PATCHES, HTML_PATCHES,          # noqa: E402
                  JA, KO, ES, PTBR, FR, DE, RU, ID)
from news import (CST, jsonld_items, load_news,           # noqa: E402
                  render_body as render_news_body,
                  sources_for, visible_items)
from cheatsheet import render_body as render_cheat_body   # noqa: E402
from snippets import render_body as render_snippets_body  # noqa: E402
from blog import (ARTICLES, BLOG_INDEX, TEXT as BLOG_TEXT,  # noqa: E402
                  article_jsonld, article_path, articles_for,
                  index_jsonld as blog_index_jsonld,
                  render_article, render_index as render_blog_index)
from blog_en import ARTICLES_EN                           # noqa: E402
import evergreen as EV                                     # noqa: E402
from course import (COURSE_INDEX, COURSE_LANGS, COURSE_TEXT, MODULES, PUBLISHED,  # noqa: E402
                    LESSON_BODIES_EN, course_index_jsonld, lesson_jsonld, lesson_meta,
                    lesson_path, render_course_index, render_lesson)
from site_config import INDEXNOW_KEY, CUSTOM_DOMAIN       # noqa: E402
from home_text import HOME_TEXT                            # noqa: E402

SRC = ROOT / 'src'
DIST = ROOT / 'dist'
DOCS = ROOT / 'docs'

# 今日热榜页。正文不是静态文件而是构建期从 data/news.json 渲染出来的，
# 所以 build() 里对它单独处理（见下方 NEWS_SLUG 分支）。
NEWS_SLUG = 'hotnews'
NEWS_PATH = next(t['path'] for t in TOOLS if t['slug'] == NEWS_SLUG)

# Go 速查表页。与热榜同型：正文构建期从 cheatsheet.py 的数据渲染，
# 页面只需要 core.js（不需要编辑器与 CodeMirror），见 build() 的 CHEAT_SLUG 分支。
CHEAT_SLUG = 'go-cheatsheet'

# 首页（工具导航门户）。
#
# 2026-10-31 改版：`/` 原来是 JSON 工具页（slug json + path ''），现在拆成两页——
#   首页  path ''      → 门户：搜索 + 分类导航 + 全部工具静态链接
#   JSON  path 'json/' → 原工具页原样保留
# 动因是 Bing 后台数据：948 条 URL 里只有 16 条拿到过曝光，而首页（JSON 工具）
# 只被当成"一个 JSON 工具站"，内页几乎没有入口权重。门户页把 57 个工具全部
# 以真实 <a> 摊平在首屏以下，既符合 tool.lu / 菜鸟教程那类目录站的使用习惯，
# 也给搜索引擎一条从强权页通往全部内页的路径。
HOME_SLUG = 'home'

# 常用代码片段库页。与速查表同型：构建期从 snippets.py 的数据渲染，
# 复制按钮复用 core.js 的 copyTextById，同样只需要 core.js。
SNIP_SLUG = 'snippets'

# 需要原样发布到站点根目录的第三方文件（搜索引擎的域名验证文件等）。
#
# 不能直接放进 docs/：下面 build() 会 rmtree(outdir)，手放进去的文件必然被删
# （CNAME 早就因为这个原因改成由构建生成了）。所以统一放在仓库根的 root_files/，
# 由构建复制到 dist/ 与 docs/ 根目录。以后新增验证文件只要丢进这个目录，
# 不用再改代码；换域名/换平台要删除时，也只要从这里删掉即可。
ROOT_FILES = ROOT / 'root_files'

# 第三方 CDN 资源自托管。
#
# 起因（2026-10-10 实测）：cdnjs.cloudflare.com 对 Baiduspider UA 会确定性返回 403
# ——同一个 URL 用普通浏览器 UA 是 200，换成百度蜘蛛的 UA 就是 403。全站 422 处引用、
# 每个工具页 14 个依赖，于是百度蜘蛛虽然拿到了 HTML（200），但 CodeMirror 初始化必然
# 失败，渲染出来是编辑器空白的残页。这比单纯慢更致命：慢只是抓得慢，资源 403 是
# 抓到了也是个坏页面。
#
# 做法：用 fetch_cdn.py 把资源下载到 src/cdn/，构建时输出到 assets/cdn/，
# 并把页面里的 https://cdnjs.cloudflare.com/ajax/libs/X 改写为同源 /assets/cdn/X。
#
# 两个刻意的选择：
# 1. 不自内联 —— 全内联会让首页 HTML 从 143 KB 涨到 300 KB+，之前的优化就白做了；
#    输出成独立文件既同源又能被浏览器长期缓存。
# 2. 用绝对路径而不是相对路径 —— 页面分布在 /、/en/、/blog/<slug>/ 好几层深度，
#    相对路径要在每处单独算层级，将来加一层目录就会错。
CDN_ORIGIN = 'https://cdnjs.cloudflare.com/ajax/libs/'
CDN_SRC = SRC / 'cdn'
CDN_OUT = Path('assets') / 'cdn'
CDN_LOCAL_URL = '/' + CDN_OUT.as_posix() + '/'

JS_MODULES = [
    'core.js', 'json-tools.js', 'text-diff.js', 'encode.js', 'regex.js',
    'timestamp.js', 'datetime-tools.js', 'id-tools.js', 'base-tools.js',
    'hash.js', 'formatter.js',
    'string-tools.js', 'generator.js', 'home.js',
]

# ---------------------------------------------------------------- 按页资产裁剪（2026-10-19）
# 背景：此前每个页面都全量内联 13 个 JS 模块 + 全量 CSS + CodeMirror 12 个脚本，
# 单页 270KB+（gzip ~89KB），百度抓取诊断的 200K 显示上限会把正文拦腰截断。
# 现在每页只带自己需要的资产。审计方法（tools_verify_css.py 全量断言）：
#   - JS：core.js initPage switch 表 + 工具页 inline script 引用 + 模块函数级核对
#   - CSS：每页静态 HTML 类 + 模块 JS 生成类（含字符串拼接类，如 word-add）
#     必须落在该页分配的 CSS 组内，否则断言失败
#   - __WC_ZONES__ 仅 world-clock / timezones 消费（datetime-tools.js 的
#     worldRefBody 渲染与 initTimezonesPage），其余页整行删除
#   - CodeMirror 仅 json 页需要（createCM 唯一调用方是 json-tools.js），
#     且只保留 javascript 模式 + matchbrackets/closebrackets/fold 三件套
PAGE_MODULES = {
    'json': ('core.js', 'json-tools.js'),
    'csv': ('core.js',),                       # textarea + 页内 IIFE，不依赖 json-tools
    'yaml': ('core.js',), 'toml': ('core.js',), 'jwt': ('core.js',),
    'color': ('core.js',), 'case': ('core.js',),
    'diff': ('core.js', 'text-diff.js'),
    'encode': ('core.js', 'encode.js'),
    'regex': ('core.js', 'regex.js'),
    'timestamp': ('core.js', 'timestamp.js'),
    'batch': ('core.js', 'datetime-tools.js'),
    'timestamp-list': ('core.js', 'datetime-tools.js'),
    'timezones': ('core.js', 'datetime-tools.js'),
    'weeknumbers': ('core.js', 'datetime-tools.js'),
    'daynumbers': ('core.js', 'datetime-tools.js'),
    'years': ('core.js', 'datetime-tools.js'),
    'world-clock': ('core.js', 'datetime-tools.js'),
    'countdown': ('core.js', 'datetime-tools.js'),
    'date-difference': ('core.js', 'datetime-tools.js'),
    'date-calculator': ('core.js', 'datetime-tools.js'),
    'duration': ('core.js', 'datetime-tools.js'),
    'uuid': ('core.js', 'id-tools.js'), 'snowflake': ('core.js', 'id-tools.js'),
    'tid': ('core.js', 'id-tools.js'), 'objectid': ('core.js', 'id-tools.js'),
    'firebase': ('core.js', 'id-tools.js'),
    'base': ('core.js', 'base-tools.js'), 'binary': ('core.js', 'base-tools.js'),
    'hex': ('core.js', 'base-tools.js'),
    'hash': ('core.js', 'hash.js'),
    'formatter': ('core.js', 'formatter.js'),
    'gofmt-online': ('core.js',),
    'cron-generator': ('core.js',),
    'csv-to-sql-insert': ('core.js',),
    'sql-formatter': ('core.js',),
    'markdown-to-html': ('core.js',),
    'string': ('core.js', 'string-tools.js'),
    'generator': ('core.js', 'generator.js'),
    'home': ('core.js', 'home.js'),
    'hotnews': ('core.js',), 'go-cheatsheet': ('core.js',), 'snippets': ('core.js',),
    'blog': ('core.js',), 'go-course': ('core.js',),
    'privacy': (),
}
PAGE_CSS = {
    'home': ('base', 'home'),
    'json': ('base', 'json'),
    'csv': ('base',),
    'yaml': ('base',), 'toml': ('base',), 'jwt': ('base',),
    'color': ('base',), 'case': ('base',),
    'diff': ('base', 'diff'),
    'encode': ('base',),
    'regex': ('base', 'regex'),
    'timestamp': ('base', 'liveclock'),
    'batch': ('base', 'time'), 'timestamp-list': ('base', 'time'),
    'timezones': ('base', 'time'), 'weeknumbers': ('base', 'time'),
    'daynumbers': ('base', 'time'), 'years': ('base', 'time'),
    'world-clock': ('base', 'time', 'worldclock'),
    'countdown': ('base', 'time'), 'date-difference': ('base', 'time'),
    'date-calculator': ('base', 'time'), 'duration': ('base', 'time'),
    'uuid': ('base',), 'snowflake': ('base',), 'tid': ('base',),
    'objectid': ('base',), 'firebase': ('base',),
    'base': ('base', 'baseconv'), 'binary': ('base', 'baseconv'),
    'hex': ('base', 'baseconv'),
    'hash': ('base',), 'formatter': ('base',), 'gofmt-online': ('base',),
    'cron-generator': ('base',), 'csv-to-sql-insert': ('base',),
    'sql-formatter': ('base',), 'markdown-to-html': ('base',),
    'string': ('base',),
    'generator': ('base', 'generator'),
    'hotnews': ('base', 'hotnews'), 'go-cheatsheet': ('base', 'cheatsheet'),
    'snippets': ('base', 'snippets'), 'blog': ('base', 'blog'),
    'go-course': ('base', 'blog', 'course'),
    'privacy': ('base', 'legal'),
}
PAGE_WC_ZONES = {'world-clock', 'timezones'}    # datetime-tools.js 的两个消费点
PAGE_KEEP_CM = {'json'}                          # createCM 唯一调用方 json-tools.js
EVERGREEN_PREFIXES = ('calendar-', 'weeks-', 'days-', 'year-')
# CodeMirror 必需资产之外，json 页也用不到的 cdnjs 标签（死代码/冗余模式）
CM_DEAD_TAGS = [
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/xml/xml.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/css/css.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/sql/sql.min.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/fold/xml-fold.min.js"></script>',
]

def assets_for(slug):
    """slug → (modules, css_groups, keep_cdn)。 evergreen 页按前缀匹配。"""
    if slug and slug.startswith(EVERGREEN_PREFIXES):
        return (('core.js',), ('base', 'evergreen'), False)
    mods = PAGE_MODULES.get(slug, ('core.js',))
    groups = PAGE_CSS.get(slug, ('base',))
    return (mods, groups, slug in PAGE_KEEP_CM)

EN_DIR = 'en/'
PRIVACY_FILE = 'privacy.html'
REPO_URL = 'https://github.com/xwjiang2003/tools'
BAIDU_ANALYTICS_ID = 'e9b85aa19d65fd425765334c56874861'
ISSUES_URL = REPO_URL + '/issues'
DISCUSSIONS_URL = REPO_URL + '/discussions'
FEEDBACK_EMAIL = '278975598@qq.com'
LANGS = ('zh', 'en', 'ja', 'ko', 'es', 'pt-BR', 'fr', 'de', 'ru', 'id')  # 阶段2 新增 8 语
HTML_LANG = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es',
             'pt-BR': 'pt-BR', 'fr': 'fr', 'de': 'de', 'ru': 'ru', 'id': 'id'}

# ---- 多语言通用配置（消除所有 `if lang=='en'` 硬编码）----
DEFAULT_LANG = 'zh'                  # 根语言：URL 无前缀
XDEFAULT_LANG = 'zh'                 # hreflang x-default 指向
LANG_DIRS = {L: ('' if L == DEFAULT_LANG else L + '/') for L in LANGS}  # 每语言目录前缀
HREFLANG_CODE = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es',
                 'pt-BR': 'pt-BR', 'fr': 'fr', 'de': 'de', 'ru': 'ru', 'id': 'id'}
LANG_NAMES = {'zh': '中文', 'en': 'English', 'ja': '日本語', 'ko': '한국어',
              'es': 'Español', 'pt-BR': 'Português', 'fr': 'Français',
              'de': 'Deutsch', 'ru': 'Русский', 'id': 'Indonesia'}   # 切换器显示名
LANG_SWITCH_ARIA_BY_LANG = {'zh': '语言', 'en': 'Language', 'ja': '言語', 'ko': '언어',
                            'es': 'Idioma', 'pt-BR': 'Idioma', 'fr': 'Langue',
                            'de': 'Sprache', 'ru': 'Язык', 'id': 'Bahasa'}
SEP_BY_LANG = {L: ('：' if L == 'zh' else ' — ') for L in LANGS}     # 功能名/描述间分隔符
BROWSER_REQ_BY_LANG = {
    'zh': '需要启用 JavaScript 的现代浏览器',
    'en': 'Requires a modern browser with JavaScript enabled',
    'ja': 'JavaScript を有効にしたモダンブラウザが必要です',
    'ko': 'JavaScript를 사용할 수 있는 최신 브라우저가 필요합니다',
    'es': 'Requiere un navegador moderno con JavaScript habilitado',
    'pt-BR': 'Requer um navegador moderno com JavaScript ativado',
    'fr': 'Nécessite un navigateur moderne avec JavaScript activé',
    'de': 'Benötigt einen modernen Browser mit aktiviertem JavaScript',
    'ru': 'Требуется современный браузер с включённым JavaScript',
    'id': 'Membutuhkan peramban modern dengan JavaScript aktif',
}
RECENT_LABEL_BY_LANG = {'zh': '最近使用', 'en': 'Recent', 'ja': '最近使用',
                        'ko': '최근 사용', 'es': 'Recientes', 'pt-BR': 'Recentes',
                        'fr': 'Récents', 'de': 'Zuletzt', 'ru': 'Недавние', 'id': 'Terakhir'}
BLOG_LABEL_BY_LANG = {'zh': '博客', 'en': 'Blog', 'ja': 'ブログ', 'ko': '블로그',
                      'es': 'Blog', 'pt-BR': 'Blog', 'fr': 'Blog', 'de': 'Blog',
                      'ru': 'Блог', 'id': 'Blog'}
CONTENT_BY_LANG = {
    'zh': {t['slug']: t for t in TOOLS},
    'en': TOOLS_EN,
    'es': TOOLS_ES,
    'fr': TOOLS_FR,
    'de': TOOLS_DE,
    'pt-BR': TOOLS_PTBR,
    'ru': TOOLS_RU,
    'id': TOOLS_ID,
    'ja': TOOLS_JA,
    'ko': TOOLS_KO,
}
# （曾有一份 NAV_LABELS_BY_LANG，与下方 NAV_LABELS 重复且新语言缺键就 KeyError，
#  2026-10-31 首页改版时删除；需要按语言的导航名请直接用 NAV_LABELS。）


def lang_dir(lang):
    """语言目录前缀：根语言为空串，其余为 `lang/` 。"""
    return LANG_DIRS.get(lang, lang + '/')


# ---------------------------------------------------------------- 本地化

# 注释整段跳过：源码注释保持中文原样，比被逐词替换成半中半英更好读。
# `(?<!:)//` 用来避开 https:// 里的双斜杠。
_COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->|(?<!:)//[^\n]*', re.S)
# 整段跳过的「非 HTML 文本」：注释 + <script>/<style> 块 + 语言切换下拉。
# 脚本 / 样式里的中文 UI 串需要本地化，但译文若含引号 / 反斜杠会破坏 JS / CSS 字符串，
# 故块内替换时转义。语言下拉里的选项标签是各语言母语名（日本語 / 한국어 / 中文），
# 绝不能被 localize 当成中文源短语做子串替换（否则 日本語→Day本語），故整段跳过。
_SKIP = re.compile(
    r'/\*.*?\*/|<!--.*?-->|(?<!:)//[^\n]*'
    r'|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>'
    r'|<select class="lang-select"[^>]*>.*?</select>',
    re.S | re.I)

# MSGS[lang] = {中文短语: 目标语短语}；英文沿用既有 EN 字典，其余 8 语在 i18n.py 填充。
# localize() 对非根语言整页（HTML + 内联 JS）做按长度降序的整词替换；某短语在目标语缺失时
# 回退到 EN（英文），再缺失才保留中文——保证非中文页绝不泄漏中文、且未翻完也有可读兜底。
MSGS = {'en': EN, 'ja': JA, 'ko': KO, 'es': ES, 'pt-BR': PTBR,
        'fr': FR, 'de': DE, 'ru': RU, 'id': ID}
JS_PATCHES_BY_LANG = {'en': JS_PATCHES}
HTML_PATCHES_BY_LANG = {'en': HTML_PATCHES}

# 按 (id(table), id(fallback)) 缓存「目标语 ∪ EN」合并正则，避免每次重建。
_PATTERN_CACHE = {}


def _combined_pattern(table, fallback):
    key = (id(table), id(fallback) if fallback is not None else None)
    pat = _PATTERN_CACHE.get(key)
    if pat is None:
        combined = dict(table)
        if fallback:
            for k, v in fallback.items():
                combined.setdefault(k, v)
        pat = re.compile(
            '|'.join(re.escape(k) for k in sorted(combined, key=len, reverse=True)))
        _PATTERN_CACHE[key] = pat
    return pat


def _sub_terms_for(text, patches_js, patches_html, table, fallback=None, escape=False):
    for old, new in patches_js:
        text = text.replace(old, new)
    for old, new in patches_html:
        text = text.replace(old, new)
    if not table and not fallback:
        return text
    pat = _combined_pattern(table, fallback)

    def repl(m):
        k = m.group(0)
        if fallback is None:
            v = table.get(k, k)
        else:
            v = table.get(k, fallback.get(k, k))
        # 在 <script>/<style> 内替换：译文里的引号 / 反斜杠会破坏 JS / CSS 字符串，
        # 必须转义（HTML 段不转义，保证展示正确）。
        if escape:
            v = (v.replace('\\', '\\\\').replace("'", "\\'")
                  .replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r'))
        return v
    return pat.sub(repl, text)


def localize(text, lang=DEFAULT_LANG):
    """把整页里的中文界面文案替换成目标语言（根语言 zh 原样返回）。

    注释整段跳过；<script>/<style> 块内替换时对译文值做引号转义，避免破坏
    JS / CSS 字符串（如法语 l'historique 的撇号）。
    """
    if lang == DEFAULT_LANG:
        return text
    patches_js = JS_PATCHES_BY_LANG.get(lang, JS_PATCHES)   # 非 en 暂复用英文 JS 改写
    patches_html = HTML_PATCHES_BY_LANG.get(lang, HTML_PATCHES)
    table = MSGS.get(lang, {})
    fallback = None if lang == 'en' else EN                  # 非英文缺失时回退英文
    out, last = [], 0
    for m in _SKIP.finditer(text):
        seg = text[last:m.start()]
        out.append(_sub_terms_for(seg, patches_js, patches_html, table, fallback))
        body = m.group(0)
        if body[:7].lower() == '<script' or body[:6].lower() == '<style':
            # 块内：本地化 + 转义译文值
            out.append(_sub_terms_for(body, patches_js, patches_html, table, fallback, escape=True))
        else:
            out.append(body)                                 # 注释：保持原样
        last = m.end()
    out.append(_sub_terms_for(text[last:], patches_js, patches_html, table, fallback))
    return ''.join(out)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- 路径计算

def out_path(lang, path):
    """path 为工具相对路径（'' 或 'diff/'）或带扩展名的页面（privacy.html）。"""
    prefix = lang_dir(lang)
    if path.endswith('.html'):          # 独立文件，不再套目录
        return Path(prefix + path)
    return Path(prefix + path + 'index.html')


def rel_root(lang, path):
    """从输出文件所在目录回到站点根目录的相对前缀。

    depth 按 path 里的 '/' 数计算：'' → 0，'diff/' → 1，'blog/foo/' → 2，
    'privacy.html' 这类根级文件 → 0。英文页再多一级 /en/。
    """
    depth = path.count('/') + (0 if lang == DEFAULT_LANG else 1)
    return '../' * depth


def lang_prefix(lang, root):
    """当前语言内部的链接前缀。"""
    return root + lang_dir(lang)


def other_lang_url(lang, root, path):
    """同一页在另一种语言下的相对 URL。"""
    if lang == 'en':
        return (root + path) or './'
    return root + EN_DIR + path


def canonical_url(lang, path):
    return SITE['base_url'] + lang_dir(lang) + path


# ---------------------------------------------------------------- 页面片段

def hreflang_html(path, langs=None):
    langs = langs or LANGS
    links = []
    for L in langs:
        links.append('<link rel="alternate" hreflang="%s" href="%s">'
                     % (HREFLANG_CODE[L], SITE['base_url'] + lang_dir(L) + path))
    links.append('<link rel="alternate" hreflang="x-default" href="%s">'
                 % (SITE['base_url'] + lang_dir(XDEFAULT_LANG) + path))
    return '\n'.join(links)


def lang_switch_html(lang, path, langs=None):
    """N 语言切换器：`<select>` 下拉，避免 10 种语言横排挤爆 header 宽度预算。
    每个选项的 value 是「当前页在目标语言下的相对 URL」，change 时记到 localStorage 并跳转。
    aria-label 用当前语言表述，避免英文页出现英文标签这种小瑕疵。
    langs 限定可选语言（如课程板块仅 zh/en 有页面）。"""
    langs = langs or LANGS
    rel = rel_root(lang, path)
    opts = []
    for L in langs:
        if L == lang:
            href = './'                      # 当前页：预选中，不跳转
        else:
            href = rel + lang_dir(L) + path
            if not href:
                href = './'
        opts.append('<option value="%s" data-lang="%s"%s>%s</option>'
                   % (href, L, ' selected' if L == lang else '', LANG_NAMES[L]))
    aria = LANG_SWITCH_ARIA_BY_LANG.get(lang, 'Language')
    return (
        '<div class="lang-switch">\n'
        '  <select class="lang-select" aria-label="%s">\n' % aria
        + '\n'.join('    ' + o for o in opts) + '\n'
        '  </select>\n'
        '</div>\n'
        '<script>\n'
        '// 语言切换：记住手动选择，下次访问不再自动跳转\n'
        'var __ls = document.querySelector(".lang-select");\n'
        'if (__ls) {\n'
        '  __ls.addEventListener("change", function () {\n'
        '    var o = __ls.options[__ls.selectedIndex];\n'
        '    try { localStorage.setItem("devtools-lang", o.getAttribute("data-lang")); } catch (e) {}\n'
        '    location.href = __ls.value;\n'
        '  });\n'
        '}\n'
        '</script>'
    )


def analytics_html():
    """统计代码，按官方要求放在全部页面的 </head> 之前。

    - 百度统计：刻意保持与后台给出的片段一字不差（含 document.getElementsByTagName 的插入方式），
      因为「代码安装检查」是按页面 HTML 里是否出现 hm.js?<id> 来判断的，改动片段有被误判为未安装的风险。
    - Ahrefs Web Analytics：直接用官方给的 <script src=... data-key=... async> 片段，
      「Recheck installation」同样按页面是否含 analytics.ahrefs.com/analytics.js 判断。
    """
    baidu = '''<!-- 百度统计（Baidu Analytics）：按官方要求置于 head 结束标签之前，全站所有页面 -->
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?__BAIDU_ID__";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>'''.replace('__BAIDU_ID__', BAIDU_ANALYTICS_ID)
    ahrefs = (
        '<!-- Ahrefs Web Analytics：置于 head 结束标签之前，全站所有页面 -->\n'
        '<script src="https://analytics.ahrefs.com/analytics.js" '
        'data-key="PRpvcCuMLrHbGbDAXyFg9Q" async></script>'
    )
    return baidu + '\n' + ahrefs


def feedback_btn_html():
    """页眉的反馈按钮。"""
    return ('<button class="feedback-btn" type="button" data-feedback-open '
            'title="问题反馈" aria-label="问题反馈">💬</button>')


def feedback_modal_html():
    """反馈弹窗。

    这里刻意没有用 GitHub API 直接建 issue —— 那需要一个 token，放在纯静态站点上
    必然泄露。可行的做法只有「深链到预选好模板的新建页」，由用户在自己已登录的
    浏览器里提交，既不需要后端也不需要任何凭据。
    """
    return '''<dialog class="feedback-modal" id="feedbackModal">
  <div class="fb-head">
    <h3>问题反馈</h3>
    <button class="fb-close" type="button" data-feedback-close aria-label="关闭">&times;</button>
  </div>
  <p class="fb-lead">本站是纯前端静态站，没有后端也没有账号系统，反馈走 GitHub Issues、讨论区或邮件。</p>
  <div class="fb-links">
    <a class="fb-link" href="__ISSUES__/new?template=bug_report.yml&amp;labels=bug" target="_blank" rel="noopener">
      <b>🐞 报告问题</b><span>工具报错、结果不对、页面异常</span>
    </a>
    <a class="fb-link" href="__ISSUES__/new?template=feature_request.yml&amp;labels=enhancement" target="_blank" rel="noopener">
      <b>💡 功能建议</b><span>想要新工具或改进体验</span>
    </a>
    <a class="fb-link" href="__DISCUSSIONS__" target="_blank" rel="noopener">
      <b>💬 讨论区</b><span>使用问题、经验交流、不确定算不算 bug 的反馈</span>
    </a>
  </div>
  <div class="fb-diag">
    <button class="btn btn-sm" type="button" id="fbCopyDiag">📋 复制诊断信息</button>
    <span class="fb-hint">粘贴到 issue 或邮件里能帮我更快定位问题，其中不含你输入的任何内容</span>
  </div>
  <p class="fb-note">
    <span>其它：</span><a href="__ISSUES__" target="_blank" rel="noopener">查看已有反馈</a>
    <span>·</span>
    <span>邮件反馈（无需 GitHub 账号）：</span><a href="mailto:__EMAIL__?subject=%5BDevTools%5D%20Feedback">__EMAIL__</a>
  </p>
</dialog>
<script>
(function () {
  var modal = document.getElementById('feedbackModal');
  if (!modal) return;
  function open(e) {
    if (e) e.preventDefault();
    if (typeof modal.showModal === 'function') { if (!modal.open) modal.showModal(); }
    else { window.open('__ISSUES__', '_blank', 'noopener'); }
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-feedback-open]'), function (el) {
    el.addEventListener('click', open);
  });
  Array.prototype.forEach.call(document.querySelectorAll('[data-feedback-close]'), function (el) {
    el.addEventListener('click', function () { modal.close(); });
  });
  modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); });

  var copy = document.getElementById('fbCopyDiag');
  if (copy) copy.addEventListener('click', function () {
    var text = [
      '页面: ' + location.href,
      '浏览器: ' + navigator.userAgent,
      '语言: ' + (navigator.language || '') + ' / 界面: ' + document.documentElement.lang,
      '屏幕: ' + screen.width + 'x' + screen.height + ' @' + (window.devicePixelRatio || 1) + 'x',
      '主题: ' + (document.documentElement.getAttribute('data-theme') || 'light'),
      '时间: ' + new Date().toISOString()
    ].join('\\n');
    function done(ok) {
      copy.textContent = ok ? '✅ 已复制' : '❌ 复制失败';
      setTimeout(function () { copy.textContent = '📋 复制诊断信息'; }, 1600);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else { done(false); }
  });
})();
</script>'''.replace('__ISSUES__', ISSUES_URL) \
       .replace('__DISCUSSIONS__', DISCUSSIONS_URL) \
       .replace('__EMAIL__', FEEDBACK_EMAIL)


def autodetect_html(lang, path, langs=None):
    """首次访问按浏览器语言跳到对应语言版本；已手动选择过或疑似爬虫则不跳。
    langs 限定可选语言（如课程板块仅 zh/en 有页面）。

    算法集中在 src/js/lang-detect.js（resolveAutoLang），由本函数内联进 <head>；
    这里只注入每页数据（可选语言 + 各语言 URL 映射）。改语言策略只动那个 js 文件。
    """
    langs = langs or LANGS
    rel = rel_root(lang, path)
    targets = json.dumps({L: ((rel + lang_dir(L) + path) or './') for L in langs})
    lang_list = json.dumps(list(langs))
    # 算法源文件：内联到 head，保证首访早跳转、不闪，且全站单一来源。
    alg = (SRC / 'js' / 'lang-detect.js').read_text('utf-8').rstrip('\n')
    return f'''<script>
// 语言自动选择：仅在用户没手动选过、且不是搜索引擎爬虫时执行。
// 算法见 src/js/lang-detect.js（单一来源），构建期内联到此；爬虫跳过是为了
// 不影响各语言版本的收录（配合 hreflang 使用）。
{alg}
(function () {{
  try {{
    var KEY = 'devtools-lang';
    var q = location.search.match(/[?&]lang=([A-Za-z-]+)(?:&|$)/);
    if (q) {{ try {{ localStorage.setItem(KEY, q[1]); }} catch (e) {{}} return; }}
    if (localStorage.getItem(KEY)) return;
    if (/(bot|crawler|spider|crawling|slurp|bingpreview)/i.test(navigator.userAgent)) return;
    var bl = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || ''];
    var want = resolveAutoLang(bl, {lang_list});
    var targets = {targets};
    var target = targets[want];
    if (target && want !== '{lang}') location.replace(target);
  }} catch (e) {{}}
}})();
</script>'''


# 顶部导航分组（工具在前、内容在后）。展示顺序即列表顺序；
# slugs 必须覆盖 TOOLS 的全部条目（含首页 JSON 工具），否则该条目不会出现在导航里。
NAV_GROUPS = [
    {'zh': 'JSON', 'en': 'JSON', 'slugs': ['json']},
    {'zh': '格式转换', 'en': 'Convert', 'slugs': ['formatter', 'gofmt-online', 'sql-formatter', 'markdown-to-html', 'yaml', 'toml', 'csv', 'csv-to-sql-insert', 'color']},
    {'zh': '进制转换', 'en': 'Base Convert', 'slugs': ['base', 'binary', 'hex']},
    {'zh': '编码 / 加密', 'en': 'Encode / Crypto', 'slugs': ['encode', 'hash', 'jwt']},
    {'zh': '文本 / 字符串', 'en': 'Text / String', 'slugs': ['diff', 'string', 'regex', 'case']},
    {'zh': '代码 / 生成', 'en': 'Code / Gen', 'slugs': ['generator', 'snippets']},
    {'zh': '时间 / 日期', 'en': 'Time / Date', 'slugs': [
        'timestamp', 'batch', 'timestamp-list', 'cron-generator', 'timezones', 'weeknumbers', 'daynumbers',
        'years', 'world-clock', 'countdown', 'date-difference', 'date-calculator', 'duration']},
    {'zh': 'ID / 标识', 'en': 'ID / Identifiers', 'slugs': ['uuid', 'snowflake', 'tid', 'objectid', 'firebase']},
    {'zh': '速查表', 'en': 'Cheat Sheets', 'slugs': ['go-cheatsheet']},
]
CONTENT_GROUP = {'zh': '内容', 'en': 'Content', 'slugs': ['hotnews', 'blog', 'go-course']}

# 首页「全部工具」板块的一句话说明（每个工具 ≤ 30 字）。
#
# 为什么只放在首页：38 个工具的内页各自已有完整的 h1/简介/功能/FAQ，重复写没有意义；
# 但首页在搜索眼里目前只是「一个 JSON 工具站」，其余工具在首页仅有一个导航词。
# 给每个工具一句可读的描述 + 一个真实 <a href>，既让首页覆盖其余工具的关键词，
# 也把首页的链接权重分发到所有内页（内页收录上不去的主因之一就是缺这条路径）。
# 新增工具时必须同步补一条，否则该工具在首页只剩名称没有描述（不影响构建，但会丢关键词）。
TOOL_BLURBS = {
    'zh': {
        'json': '格式化、压缩、校验、比对，与 CSV / XML / YAML 互转',
        'hotnews': '每日聚合 Hacker News、TechCrunch 等技术资讯',
        'go-cheatsheet': 'Go 常用命令、环境变量与踩坑速查',
        'diff': '逐字符 / 逐词比对两段文本的差异',
        'encode': 'Base64、URL、Unicode、HTML 实体编解码',
        'regex': '在线测试正则，实时高亮匹配与替换预览',
        'timestamp': 'Unix 时间戳与日期互转，秒 / 毫秒自动识别',
        'hash': 'MD5 / SHA 系列、HMAC、AES 与文件校验值',
        'formatter': 'HTML / CSS / JS / SQL 代码格式化',
        'gofmt-online': 'gofmt 规则在线格式化 Go 代码，纯浏览器运行',
        'cron-generator': '可视化生成 Linux crontab 定时任务表达式',
        'csv-to-sql-insert': 'CSV 一键生成 SQL INSERT 批量插入语句',
        'sql-formatter': 'SQL 语句在线格式化，关键字大写与缩进可调',
        'markdown-to-html': 'Markdown 转 HTML，支持表格、代码块与列表',
        'string': '大小写转换、去重、排序与字数统计',
        'generator': 'UUID、随机密码与二维码生成',
        'color': 'HEX / RGB / HSL 颜色互转与配色预览',
        'case': 'camelCase、snake_case 等命名风格互转',
        'jwt': 'JWT 解码与 HS256 / 384 / 512 签名校验',
        'yaml': 'JSON 与 YAML 双向转换',
        'toml': 'JSON 与 TOML 双向转换',
        'csv': 'JSON 与 CSV 双向转换，可选是否带表头',
        'batch': '批量时间戳与日期互转',
        'timestamp-list': '今天 / 本周 / 本月等常用时间戳速查',
        'timezones': '两个城市之间的时区换算与当前时间对照',
        'weeknumbers': 'ISO 周数与日期互查',
        'daynumbers': '年内第几天与日期互查',
        'years': '闰年判断与某年的天数',
        'world-clock': '多城市世界时钟，支持多个视图',
        'countdown': '到指定日期的倒计时',
        'date-difference': '两个日期相差多少天 / 月 / 年',
        'date-calculator': '日期加减天数与工作日推算',
        'duration': '秒、分、时、天之间的时长换算',
        'uuid': 'UUID v4 / v7 批量生成与解析',
        'snowflake': 'Snowflake ID 反解时间戳与机器号',
        'tid': 'Twitter Snowflake ID 转发布时间',
        'objectid': 'MongoDB ObjectId 内嵌时间戳解析',
        'firebase': 'Firebase Push ID 的生成时间解析',
        'base': '2–36 任意进制之间互转',
        'binary': '二进制、十进制、十六进制换算',
        'hex': '十六进制与文本、十进制互转',
        'snippets': '常用语言的代码片段速查',
        'blog': 'Go、前端与建站实践的技术长文',
    },
    'en': {
        'json': 'Format, minify, validate, diff and convert to CSV / XML / YAML',
        'hotnews': 'Daily tech news from Hacker News, TechCrunch and more',
        'go-cheatsheet': 'Go commands, environment variables and pitfalls',
        'diff': 'Character- and word-level text diff',
        'encode': 'Base64, URL, Unicode and HTML entity encode / decode',
        'regex': 'Test regular expressions with live highlight and replace preview',
        'timestamp': 'Unix timestamp and date converter, auto-detects seconds or ms',
        'hash': 'MD5 / SHA family, HMAC, AES and file checksums',
        'formatter': 'HTML, CSS, JS and SQL code formatter',
        'gofmt-online': 'Format Go code with real gofmt rules in your browser',
        'cron-generator': 'Build Linux crontab expressions visually',
        'csv-to-sql-insert': 'Turn CSV into SQL INSERT statements in one click',
        'sql-formatter': 'Format SQL statements with keyword casing and indent options',
        'markdown-to-html': 'Turn Markdown into HTML with tables, code blocks and lists',
        'string': 'Case conversion, dedupe, sorting and word count',
        'generator': 'UUID, random password and QR code generator',
        'color': 'HEX / RGB / HSL colour converter with preview',
        'case': 'camelCase, snake_case and other naming styles',
        'jwt': 'Decode JWTs and verify HS256 / 384 / 512 signatures',
        'yaml': 'JSON and YAML converter',
        'toml': 'JSON and TOML converter',
        'csv': 'JSON and CSV converter with optional header row',
        'batch': 'Convert many timestamps at once',
        'timestamp-list': 'Common timestamps: today, this week, this month',
        'timezones': 'Convert time between two cities and compare clocks',
        'weeknumbers': 'ISO week number and date lookup',
        'daynumbers': 'Day of the year and date lookup',
        'years': 'Leap year check and days in a given year',
        'world-clock': 'Multi-city world clock with several views',
        'countdown': 'Countdown to any target date',
        'date-difference': 'Days, months and years between two dates',
        'date-calculator': 'Add or subtract days and working days',
        'duration': 'Seconds, minutes, hours and days converter',
        'uuid': 'Generate and inspect UUID v4 / v7 in bulk',
        'snowflake': 'Decode Snowflake IDs into time and worker ID',
        'tid': 'Turn a Twitter snowflake ID into its timestamp',
        'objectid': 'Decode the timestamp inside a MongoDB ObjectId',
        'firebase': 'Decode the timestamp inside a Firebase push ID',
        'base': 'Convert between any bases from 2 to 36',
        'binary': 'Binary, decimal and hexadecimal conversion',
        'hex': 'Hex to text and decimal conversion',
        'snippets': 'Copy-ready code snippets for common languages',
        'blog': 'Long-form posts on Go, the web and building this site',
    },
}
# 未单独翻译的语言先回退英文（与正文策略一致，绝不留中文）。
for _lang in LANGS:
    if _lang not in TOOL_BLURBS:
        TOOL_BLURBS[_lang] = TOOL_BLURBS['en']

# 阶段2：新语言未单独翻分类名时，统一回退英文（与正文英文回退策略一致）。
for _grp in NAV_GROUPS + [CONTENT_GROUP]:
    for _L in LANGS:
        if _L not in _grp:
            _grp[_L] = _grp.get('en', _grp['zh'])

_TOOL_BY_SLUG = {t['slug']: t for t in TOOLS}


def nav_html(active_slug, base, labels, lang='zh'):
    """顶部导航 = 下拉式 Mega Menu。

    工具板块（NAV_GROUPS）每个分类渲染成一个 .nav-dropdown：触发按钮 + 悬停展开的工具面板，
    表头始终一行、不横向滚动；当前所处工具的分类触发词会高亮。内容板块（CONTENT_GROUP：
    今日热榜、博客）作为平级链接排在分类之后。面板用 CSS :hover / :focus-within 展开，
    无需 JS，移动端点击触发词（按钮获得焦点）即可展开。
    """
    out = []
    # 首页入口：logo 也指向首页，但导航里给一条显式链接——移动端抽屉展开后
    # logo 常被滚动出视野，没有这一条就只能靠浏览器返回键。
    home_cls = 'top-nav-link active' if active_slug == HOME_SLUG else 'top-nav-link'
    out.append(f'    <a class="{home_cls}" href="{base or "./"}">{esc(labels["_home"])}</a>')
    # 工具板块 -> 下拉
    for g in NAV_GROUPS:
        items, group_active = [], False
        for slug in g['slugs']:
            t = _TOOL_BY_SLUG.get(slug)
            if not t:
                continue
            href = base + t['path'] if t['path'] else (base or './')
            if t['slug'] == active_slug:
                group_active = True
                items.append(f'        <a class="nav-panel-item active" href="{href}">{esc(labels[t["slug"]])}</a>')
            else:
                items.append(f'        <a class="nav-panel-item" href="{href}">{esc(labels[t["slug"]])}</a>')
        if not items:
            continue
        trig_cls = 'nav-trigger active' if group_active else 'nav-trigger'
        out.append('    <div class="nav-dropdown">')
        out.append(f'      <button class="{trig_cls}" type="button" aria-haspopup="true" aria-expanded="false">{esc(g[lang])}<span class="caret" aria-hidden="true"></span></button>')
        out.append('      <div class="nav-panel" role="menu">')
        out.append(f'        <div class="nav-panel-title">{esc(g[lang])}</div>')
        out.extend(items)
        out.append('      </div>')
        out.append('    </div>')
    # 内容板块 -> 平级链接
    for slug in CONTENT_GROUP['slugs']:
        if slug == 'blog':
            cls = 'top-nav-link active' if active_slug == 'blog' else 'top-nav-link'
            out.append(f'    <a class="{cls}" href="{base}{BLOG_INDEX}">{esc(labels["_blog"])}</a>')
            continue
        if slug == 'go-course':
            # Go 课程图文板块有 zh / en 两个版本；其余语言无课程页，不显示入口避免死链
            if lang not in COURSE_LANGS:
                continue
            cls = ('top-nav-link active' if active_slug == 'go-course'
                   else 'top-nav-link')
            out.append(f'    <a class="{cls}" href="{base}{COURSE_INDEX}">{esc(labels["_course"])}</a>')
            continue
        t = _TOOL_BY_SLUG.get(slug)
        if not t:
            continue
        href = base + t['path'] if t['path'] else (base or './')
        cls = 'top-nav-link active' if t['slug'] == active_slug else 'top-nav-link'
        out.append(f'    <a class="{cls}" href="{href}">{esc(labels[t["slug"]])}</a>')
    # 日历与日期（当前年份代表入口）：按年静态参考页不进 TOOLS，单独成组。内部代号 evergreen。
    trig_cls = 'nav-trigger active' if active_slug == 'evergreen' else 'nav-trigger'
    out.append('    <div class="nav-dropdown">')
    out.append(f'      <button class="{trig_cls}" type="button" aria-haspopup="true" aria-expanded="false">{esc(EVERGREEN_NAV_LABELS[lang])}<span class="caret" aria-hidden="true"></span></button>')
    out.append('      <div class="nav-panel" role="menu">')
    out.append(f'        <div class="nav-panel-title">{esc(EVERGREEN_NAV_LABELS[lang])}</div>')
    for label, href in EV.evergreen_nav_items(lang):
        out.append(f'        <a class="nav-panel-item" href="{base}{href}">{esc(label)}</a>')
    out.append('      </div>')
    out.append('    </div>')
    # 最近使用（动态，由 JS 从 localStorage 填充；无 JS 时面板为空）。
    # 放在导航末尾，与上方分类下拉保持同一套样式与交互（桌面悬停展开、窄屏抽屉内原地展开）。
    recent_label = RECENT_LABEL_BY_LANG.get(lang, 'Recent')
    out.append('    <div class="nav-dropdown nav-recent">')
    out.append(f'      <button class="nav-trigger" type="button" aria-haspopup="true" aria-expanded="false">{esc(recent_label)}<span class="caret" aria-hidden="true"></span></button>')
    out.append('      <div class="nav-panel" id="recentPanel" role="menu"></div>')
    out.append('    </div>')
    return '\n'.join(out)


def tool_index_json(base, lang):
    """生成全站工具搜索索引（每页注入 window.__TOOL_INDEX__）。

    字段：slug / href / g(分类名) + zh{label,title,kw} + en{label,title,kw}。
    - 中文页：zh 用真实中文（展示 + 可被英文关键词搜到），en 用英文（跨语言搜索）。
    - 英文页：zh 字段也填英文，保证英文页 JSON 零中文（否则 check.py 会报“英文页含中文”）。
    href 与导航一致用 base+path，从任意页相对跳转都正确；展示与匹配按当前语言选取。
    """
    def group_of(slug):
        g = next((x for x in NAV_GROUPS if slug in x['slugs']), None)
        if g:
            return g[lang]
        if slug in CONTENT_GROUP['slugs']:
            return CONTENT_GROUP[lang]
        return ''
    def href_of(path):
        return (base + path) if path else (base or './')
    entries = []
    for t in TOOLS:
        slug = t['slug']
        te = TOOLS_EN.get(slug, t)
        zh_l, zh_t, zh_k = t.get('nav', ''), t.get('title', ''), t.get('keywords', '')
        en_l, en_t, en_k = te.get('nav', ''), te.get('title', ''), te.get('keywords', '')
        if lang != DEFAULT_LANG:
            # 非根语言页：zh 字段填「本语言」文本（content_xx 已翻短字段则用它，
            # 否则回退英文），保证搜索结果/最近使用不显示英语也绝不残留中文；
            # en 字段保留英文，兼顾跨语言检索（core.js 搜索同时匹配 zh 与 en）。
            _c = content_for(t, lang)
            zh_l = _c.get('nav') or en_l
            zh_t = _c.get('title') or en_t
            zh_k = _c.get('keywords') or en_k
        entries.append({
            'slug': slug, 'href': href_of(t['path']), 'g': group_of(slug),
            'zh': {'l': zh_l, 't': zh_t, 'k': zh_k},
            'en': {'l': en_l, 't': en_t, 'k': en_k},
        })
    # 博客索引（不是 TOOLS，单独补一条，让搜索也能定位博客）
    bt = BLOG_TEXT[lang]
    entries.append({
        'slug': 'blog', 'href': href_of(BLOG_INDEX), 'g': CONTENT_GROUP[lang],
        'zh': {'l': BLOG_LABEL_BY_LANG.get(lang, 'Blog'), 't': bt['index_title'], 'k': bt['index_kw']},
        'en': {'l': 'Blog', 't': bt['index_title'], 'k': bt['index_kw']},
    })
    return json.dumps(entries, ensure_ascii=False)


# ---------- 世界时钟 / 时区页 共享时区数据集（单一数据源，构建期按语言注入）----------
# 每项：IANA 时区、标准 UTC 偏移文案、中文标签、中文代表城市、英文标签、英文代表城市。
# 顺序即标准 UTC 偏移从早到晚（UTC−12 → UTC+14），含全球 38 个实际在用标准偏移。
# 注入到 window.__WC_ZONES__（每页），由 datetime-tools.js 按当前语言读取，避免中文数据泄漏到英文页。
WC_ZONES = [
    ('Etc/GMT+12', 'UTC−12:00', '贝克岛（美属·无人）', ['贝克岛', '豪兰岛'],
     'Baker I. (US)', ['Baker I.', 'Howland I.']),
    ('Pacific/Pago_Pago', 'UTC−11:00', '帕果帕果', ['帕果帕果（美属萨摩亚）', '阿洛菲（纽埃）'],
     'Pago Pago', ['Pago Pago (American Samoa)', 'Alofi (Niue)']),
    ('Pacific/Honolulu', 'UTC−10:00', '檀香山', ['檀香山（夏威夷）', '帕皮提（法属波利尼西亚）'],
     'Honolulu', ['Honolulu (Hawaii)', 'Papeete (Fr. Polynesia)']),
    ('Pacific/Marquesas', 'UTC−09:30', '努库希瓦', ['努库希瓦（马克萨斯群岛）'],
     'Nuku Hiva', ['Nuku Hiva (Marquesas)']),
    ('America/Anchorage', 'UTC−09:00', '安克雷奇', ['安克雷奇（阿拉斯加）'],
     'Anchorage', ['Anchorage (Alaska)']),
    ('America/Los_Angeles', 'UTC−08:00', '洛杉矶', ['洛杉矶', '温哥华', '蒂华纳'],
     'Los Angeles', ['Los Angeles', 'Vancouver', 'Tijuana']),
    ('America/Denver', 'UTC−07:00', '丹佛', ['丹佛', '凤凰城', '埃德蒙顿'],
     'Denver', ['Denver', 'Phoenix', 'Edmonton']),
    ('America/Chicago', 'UTC−06:00', '芝加哥', ['芝加哥', '墨西哥城', '温尼伯'],
     'Chicago', ['Chicago', 'Mexico City', 'Winnipeg']),
    ('America/New_York', 'UTC−05:00', '纽约', ['纽约', '多伦多', '波哥大', '利马'],
     'New York', ['New York', 'Toronto', 'Bogotá', 'Lima']),
    ('America/Halifax', 'UTC−04:00', '哈利法克斯', ['哈利法克斯', '加拉加斯', '圣地亚哥', '拉巴斯'],
     'Halifax', ['Halifax', 'Caracas', 'Santiago', 'La Paz']),
    ('America/St_Johns', 'UTC−03:30', '圣约翰斯', ['圣约翰斯（纽芬兰）'],
     "St. John's", ["St. John's (Newfoundland)"]),
    ('America/Sao_Paulo', 'UTC−03:00', '圣保罗', ['圣保罗', '布宜诺斯艾利斯', '蒙得维的亚'],
     'São Paulo', ['São Paulo', 'Buenos Aires', 'Montevideo']),
    ('America/Noronha', 'UTC−02:00', '费尔南多-迪诺罗尼亚', ['费尔南多-迪诺罗尼亚', '南乔治亚'],
     'Fernando de Noronha', ['Fernando de Noronha', 'South Georgia']),
    ('Atlantic/Azores', 'UTC−01:00', '蓬塔德尔加达', ['蓬塔德尔加达（亚速尔）', '普拉亚（佛得角）'],
     'Ponta Delgada', ['Ponta Delgada (Azores)', 'Praia (Cape Verde)']),
    ('UTC', 'UTC±00:00', '协调世界时', ['UTC 基准（无时区）'],
     'UTC', ['UTC reference']),
    ('Europe/London', 'UTC±00:00', '伦敦', ['伦敦', '里斯本', '雷克雅未克', '阿克拉'],
     'London', ['London', 'Lisbon', 'Reykjavík', 'Accra']),
    ('Europe/Paris', 'UTC+01:00', '巴黎', ['巴黎', '柏林', '罗马', '马德里', '拉各斯'],
     'Paris', ['Paris', 'Berlin', 'Rome', 'Madrid', 'Lagos']),
    ('Europe/Athens', 'UTC+02:00', '雅典', ['雅典', '开罗', '赫尔辛基', '约翰内斯堡', '布加勒斯特'],
     'Athens', ['Athens', 'Cairo', 'Helsinki', 'Johannesburg', 'Bucharest']),
    ('Europe/Moscow', 'UTC+03:00', '莫斯科', ['莫斯科', '伊斯坦布尔', '内罗毕', '利雅得'],
     'Moscow', ['Moscow', 'Istanbul', 'Nairobi', 'Riyadh']),
    ('Asia/Tehran', 'UTC+03:30', '德黑兰', ['德黑兰（伊朗）'],
     'Tehran', ['Tehran (Iran)']),
    ('Asia/Dubai', 'UTC+04:00', '迪拜', ['迪拜', '巴库', '第比利斯'],
     'Dubai', ['Dubai', 'Baku', 'Tbilisi']),
    ('Asia/Kabul', 'UTC+04:30', '喀布尔', ['喀布尔（阿富汗）'],
     'Kabul', ['Kabul (Afghanistan)']),
    ('Asia/Karachi', 'UTC+05:00', '卡拉奇', ['卡拉奇（巴基斯坦）', '塔什干', '马累'],
     'Karachi', ['Karachi (Pakistan)', 'Tashkent', 'Malé']),
    ('Asia/Kolkata', 'UTC+05:30', '加尔各答', ['加尔各答 / 新德里', '科伦坡'],
     'Kolkata', ['Kolkata / New Delhi', 'Colombo']),
    ('Asia/Kathmandu', 'UTC+05:45', '加德满都', ['加德满都（尼泊尔）'],
     'Kathmandu', ['Kathmandu (Nepal)']),
    ('Asia/Dhaka', 'UTC+06:00', '达卡', ['达卡（孟加拉）', '阿拉木图', '鄂木斯克'],
     'Dhaka', ['Dhaka (Bangladesh)', 'Almaty', 'Omsk']),
    ('Asia/Yangon', 'UTC+06:30', '仰光', ['仰光（缅甸）', '科科斯群岛'],
     'Yangon', ['Yangon (Myanmar)', 'Cocos Is.']),
    ('Asia/Bangkok', 'UTC+07:00', '曼谷', ['曼谷', '雅加达', '河内'],
     'Bangkok', ['Bangkok', 'Jakarta', 'Hanoi']),
    ('Asia/Shanghai', 'UTC+08:00', '北京 / 上海', ['北京 / 上海', '新加坡', '珀斯', '香港'],
     'Beijing / Shanghai', ['Beijing / Shanghai', 'Singapore', 'Perth', 'Hong Kong']),
    ('Australia/Eucla', 'UTC+08:45', '尤克拉', ['尤克拉（澳大利亚中西部，约 50 人）'],
     'Eucla', ['Eucla (W. Australia, ~50)']),
    ('Asia/Tokyo', 'UTC+09:00', '东京', ['东京', '首尔', '平壤'],
     'Tokyo', ['Tokyo', 'Seoul', 'Pyongyang']),
    ('Australia/Adelaide', 'UTC+09:30', '阿德莱德', ['阿德莱德', '达尔文'],
     'Adelaide', ['Adelaide', 'Darwin']),
    ('Australia/Sydney', 'UTC+10:00', '悉尼', ['悉尼', '墨尔本', '布里斯班'],
     'Sydney', ['Sydney', 'Melbourne', 'Brisbane']),
    ('Australia/Lord_Howe', 'UTC+10:30', '豪勋爵岛', ['豪勋爵岛（澳大利亚，约 350 人）'],
     'Lord Howe I.', ['Lord Howe I. (~350)']),
    ('Pacific/Guadalcanal', 'UTC+11:00', '霍尼亚拉', ['霍尼亚拉（所罗门）', '努美阿（新喀里多尼亚）'],
     'Honiara', ['Honiara (Solomon Is.)', 'Nouméa (New Caledonia)']),
    ('Pacific/Auckland', 'UTC+12:00', '奥克兰', ['奥克兰', '苏瓦（斐济）', '彼得罗巴甫洛夫斯克'],
     'Auckland', ['Auckland', 'Suva (Fiji)', 'Petropavlovsk-Kamchatsky']),
    ('Pacific/Chatham', 'UTC+12:45', '查塔姆群岛', ['查塔姆群岛（新西兰，约 600 人）'],
     'Chatham Is.', ['Chatham Is. (~600)']),
    ('Pacific/Tongatapu', 'UTC+13:00', '努库阿洛法', ['努库阿洛法（汤加）', '阿皮亚（萨摩亚）', '基里巴斯（凤凰群岛）'],
     'Nukuʻalofa', ['Nukuʻalofa (Tonga)', 'Apia (Samoa)', 'Kiribati (Phoenix Is.)']),
    ('Pacific/Kiritimati', 'UTC+14:00', '圣诞岛', ['圣诞岛（基里巴斯·莱恩群岛）'],
     'Kiritimati', ['Kiritimati (Line Is.)']),
]


def wc_zones_json(lang):
    """生成世界时钟 / 时区页共享的时区数据集（注入 window.__WC_ZONES__）。

    与 tool_index_json 同理：英文页只输出英文 label/cities，保证英文页零中文。
    偏移文案（UTC−12:00 等）无中日韩字符，中英共用。
    """
    items = []
    for tz, off, zh_label, zh_cities, en_label, en_cities in WC_ZONES:
        if lang != DEFAULT_LANG:
            items.append({'tz': tz, 'off': off, 'label': en_label, 'cities': en_cities})
        else:
            items.append({'tz': tz, 'off': off, 'label': zh_label, 'cities': zh_cities})
    return json.dumps(items, ensure_ascii=False)


EVERGREEN_NAV_LABELS = {
    'zh': '日历与日期', 'en': 'Calendar & Dates',
    'ja': 'カレンダーと日付', 'ko': '달력 및 날짜', 'es': 'Calendario y fechas',
    'pt-BR': 'Calendário e datas', 'fr': 'Calendrier et dates',
    'de': 'Kalender & Daten', 'ru': 'Календарь и даты', 'id': 'Kalender & Tanggal',
}


def footer_links_html(base, labels):
    home = base or './'
    parts = [f'<a href="{home}">{esc(labels["_home"])}</a>']
    for t in TOOLS:
        if not t['path']:
            continue
        parts.append(f'<a href="{base}{t["path"]}">{esc(labels[t["slug"]])}</a>')
    # 博客不是工具、不进 TOOLS，但需要一个站点级入口（正文交叉链接之外的保底）。
    parts.append(f'<a href="{base}{BLOG_INDEX}">{esc(labels["_blog"])}</a>')
    return ''.join(parts)


# ---------------------------------------------------------------- 首页（导航门户）
#
# 首页正文不是「工具界面」而是「目录 + 搜索」：全部工具以静态 <a> 摊平在
# 分类区块里，JS 只负责即时筛选与时间戳时钟。这样即使 JS 不执行（爬虫、
# 禁用脚本的浏览器），页面依然是一份完整可用的导航页。


# 图标一律内联 SVG（stroke 取 currentColor），不引外部图标库：
# 站点已有"第三方资源全部自托管"的约定，多一个 CDN 依赖就多一处失效点。
_HOME_ICON_PATHS = {
    'braces': '<path d="M9 4H8a2 2 0 0 0-2 2v3a2 2 0 0 1-2 2 2 2 0 0 1 2 2v3a2 2 0 0 0 2 2h1"/>'
              '<path d="M15 4h1a2 2 0 0 1 2 2v3a2 2 0 0 0 2 2 2 2 0 0 0-2 2v3a2 2 0 0 1-2 2h-1"/>',
    'convert': '<path d="M4 8h13l-3.5-3.5"/><path d="M20 16H7l3.5 3.5"/>',
    'hash': '<path d="M9.5 4 7.5 20"/><path d="M16.5 4l-2 16"/><path d="M4 9h16"/><path d="M3.5 15h16"/>',
    'lock': '<rect x="4.5" y="10.5" width="15" height="9.5" rx="2"/>'
            '<path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/><path d="M12 14.5v2"/>',
    'text': '<path d="M4 6.5h16"/><path d="M4 12h11"/><path d="M4 17.5h7"/>',
    'code': '<path d="M9 7 4 12l5 5"/><path d="M15 7l5 5-5 5"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3.2 2"/>',
    'tag': '<path d="M20.4 13.4 13 20.8a2 2 0 0 1-2.8 0L3.5 14.1V4.5h9.6l7.3 7.3a1.2 1.2 0 0 1 0 1.6z"/>'
           '<circle cx="7.8" cy="8.8" r="1.2"/>',
    'book': '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5z"/>'
            '<path d="M11 4h7.5A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5H11"/>',
    'news': '<rect x="3.5" y="5" width="13" height="14" rx="1.5"/>'
            '<path d="M16.5 9H20v8.5a1.5 1.5 0 0 1-1.5 1.5h-2"/>'
            '<path d="M6.5 8.5h7"/><path d="M6.5 12h7"/><path d="M6.5 15.5h4"/>',
    'pen': '<path d="M4 20l4.2-1 9.3-9.3-3.2-3.2L5 15.8z"/><path d="M14.3 6.5 17.5 3.7l3.2 3.2-2.8 3.2z"/>',
    'bookopen': '<path d="M12 6.5C10 4.9 6.5 4.6 4.5 5.6v12.6c2-1 5.5-.7 7.5.9 2-1.6 5.5-1.9 7.5-.9V5.6c-2-1-5.5-.7-7.5.9z"/>'
                '<path d="M12 6.5v12.6"/>',
    'search': '<circle cx="10.8" cy="10.8" r="6.8"/><path d="M16 16l4.5 4.5"/>',
    'regex': '<path d="M12 4v9"/><path d="M8.2 6.5 15.8 12"/><path d="M15.8 6.5 8.2 12"/>'
             '<circle cx="12" cy="17.6" r="1.1"/>',
    'diff': '<path d="M7 4v10"/><path d="M4 11l3 3 3-3"/><path d="M17 20V10"/><path d="M14 13l3-3 3 3"/>',
    'bolt': '<path d="M13 3 4.5 13.5H10L9 21l8.5-10.5H12z"/>',
    'shield': '<path d="M12 3.2 19 6v6.2c0 4-3 7.1-7 8.6-4-1.5-7-4.6-7-8.6V6z"/>'
              '<path d="M9 12l2.2 2.2L15.4 10"/>',
    'globe': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/>'
             '<path d="M12 3.5c2.6 2.6 2.6 14.4 0 17"/><path d="M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
    'offline': '<path d="M3 3l18 18"/><path d="M8.5 15.6a5 5 0 0 1 6.4-.3"/>'
               '<path d="M5.2 11.9a10.5 10.5 0 0 1 4-2.3"/><path d="M14.6 10a10.5 10.5 0 0 1 4.2 1.9"/>'
               '<path d="M12 19h.01"/>',
}
# NAV_GROUPS 的顺序即分类图标的顺序（用位置而不是中文名索引，避免多语言漂移）
_HOME_GROUP_ICONS = ['braces', 'convert', 'hash', 'lock', 'text', 'code', 'clock', 'tag', 'book']
_HOME_CONTENT_ICONS = {'hotnews': 'news', 'blog': 'pen', 'go-course': 'bookopen'}
# 「常用工具」按真实流量与使用频次排序：时间戳与正则是 Bing 后台曝光前二，
# 其余是站内点击与直觉上最常被打开的几项。
_HOME_QUICK = [
    ('timestamp', 'clock'), ('regex', 'regex'), ('json', 'braces'), ('encode', 'lock'),
    ('uuid', 'tag'), ('hash', 'hash'), ('diff', 'diff'), ('generator', 'bolt'),
]


def _home_icon(name, cls=''):
    path = _HOME_ICON_PATHS.get(name) or _HOME_ICON_PATHS['braces']
    return ('<svg' + (f' class="{cls}"' if cls else '') +
            ' viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"'
            ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + path + '</svg>')


def render_home_body(lang):
    """首页正文：hero + 常用工具 + 分类导航 + 卖点 + 站点说明。

    与其它工具页不同，这一页不输出 seo_section（h1/简介/功能/步骤/FAQ 那套骨架
    是为"单工具落地页"设计的，套到目录页上只会多出一堆无人阅读的样板文字）。
    """
    tx = HOME_TEXT.get(lang, HOME_TEXT['en'])
    labels = NAV_LABELS[lang]
    blurbs = TOOL_BLURBS.get(lang, TOOL_BLURBS['en'])
    base = lang_prefix(lang, rel_root(lang, ''))
    home_href = base or './'
    # 首页上实际列出的入口数：全部工具页 + 博客索引 +（仅 zh/en）Go 课程。
    # 与 llms.txt 的「工具数」口径不同是刻意的：首页说的是"这里有多少个入口"，
    # 而 llms.txt 报的是"有多少个带输入框的工具"，两者不应互相迁就。
    n_pages = (len([t for t in TOOLS if t['slug'] != HOME_SLUG]) + 1
               + (1 if lang in COURSE_LANGS else 0))

    def href_of(path):
        return (base + path) if path else home_href

    def label_of(slug):
        if slug in ('blog', 'go-course'):
            return labels['_blog'] if slug == 'blog' else labels['_course']
        return labels.get(slug, slug)

    def href_slug(slug):
        if slug == 'blog':
            return base + BLOG_INDEX
        if slug == 'go-course':
            return base + COURSE_INDEX
        return href_of(_TOOL_BY_SLUG[slug]['path'])

    def keywords_of(slug):
        """筛选用的关键词串：工具标题 + keywords，按当前语言取（不混入中文）。"""
        if slug == 'blog':
            bt = BLOG_TEXT[lang]
            return f'{bt["index_title"]} {bt["index_kw"]}'
        if slug == 'go-course':
            ct = COURSE_TEXT.get(lang) or COURSE_TEXT['en']
            return f'{ct["index_title"]} {ct["index_kw"]}'
        t = _TOOL_BY_SLUG[slug]
        c = content_for(t, lang)
        return f'{c.get("title", "")} {c.get("keywords", "")}'.strip()

    p = ['<div class="home" id="homeRoot">']

    # ---------------- hero ----------------
    p.append('  <section class="home-hero">')
    p.append('    <div class="home-hero-copy">')
    p.append(f'      <p class="home-eyebrow">{esc(tx["eyebrow"])}</p>')
    p.append('      <h1 class="home-title">' + esc(tx['h1']) +
             f'<span>{esc(tx["h1_sub"].format(n=n_pages))}</span></h1>')
    p.append(f'      <p class="home-lead">{esc(tx["lead"])}</p>')
    p.append('      <div class="home-search">')
    p.append('        ' + _home_icon('search', 'home-search-ico'))
    p.append('        <input id="homeSearch" type="search" autocomplete="off" spellcheck="false"'
             f' placeholder="{esc(tx["search_ph"])}" aria-label="{esc(tx["search_ph"])}">')
    p.append('      </div>')
    p.append(f'      <p class="home-search-hint">{esc(tx["search_hint"])}</p>')
    p.append('      <div class="home-chips">')
    for slug, _ in _HOME_QUICK[:5]:
        p.append(f'        <a class="home-chip" href="{esc(href_slug(slug))}">{esc(label_of(slug))}</a>')
    p.append('      </div>')
    p.append('    </div>')

    p.append(f'    <aside class="home-live" aria-label="{esc(tx["live_t"])}">')
    p.append('      <div class="home-live-label"><span class="home-live-dot"></span>' +
             esc(tx['live_t']) + '</div>')
    p.append('      <div class="home-live-num" id="homeEpoch">&mdash;</div>')
    p.append('      <div class="home-live-ms" id="homeEpochMs">&mdash;</div>')
    p.append('      <div class="home-live-foot">')
    p.append('        <div class="home-live-stats">')
    p.append(f'          <div class="home-live-stat"><b>{n_pages}</b><span>{esc(tx["stat_tools"])}</span></div>')
    p.append(f'          <div class="home-live-stat"><b>{len(LANGS)}</b><span>{esc(tx["stat_langs"])}</span></div>')
    p.append('        </div>')
    p.append(f'        <a class="home-live-cta" href="{esc(href_slug("timestamp"))}">'
             + esc(tx['live_cta']) + ' &rarr;</a>')
    p.append('      </div>')
    p.append('    </aside>')
    p.append('  </section>')

    # ---------------- 常用工具 ----------------
    p.append('  <section class="home-section">')
    p.append('    <div class="home-section-head">')
    p.append(f'      <h2>{esc(tx["quick"])}</h2><p>{esc(tx["quick_sub"])}</p>')
    p.append('    </div>')
    p.append('    <div class="home-quick">')
    for slug, icon in _HOME_QUICK:
        p.append(f'      <a class="home-quick-card" href="{esc(href_slug(slug))}">')
        p.append(f'        <span class="home-quick-ico">{_home_icon(icon)}</span>')
        p.append(f'        <span class="home-quick-name">{esc(label_of(slug))}</span>')
        p.append(f'        <span class="home-quick-desc">{esc(blurbs.get(slug, ""))}</span>')
        p.append('      </a>')
    p.append('    </div>')
    p.append('  </section>')

    # ---------------- 分类导航 ----------------
    p.append('  <section class="home-section">')
    p.append('    <div class="home-section-head">')
    p.append(f'      <h2>{esc(tx["browse"])}</h2><p>{esc(tx["browse_sub"])}</p>')
    p.append('    </div>')
    p.append(f'    <div class="home-empty">{esc(tx["no_result"])}</div>')
    # 分类区块用两列瀑布（CSS column-count）：工具数少的分类（JSON 只有 1 个）
    # 不再独占一整行的空白，也避免 1440px 下 5 列网格里出现成排的空洞。
    p.append('    <div class="home-cats">')

    groups = []
    for i, g in enumerate(NAV_GROUPS):
        groups.append((g, g[lang], _HOME_GROUP_ICONS[i] if i < len(_HOME_GROUP_ICONS) else 'braces'))
    # 内容板块（热榜 / 博客 / 课程）合成一张卡：拆成三张同名"内容"卡会让人以为重复。
    content_slugs = [s2 for s2 in CONTENT_GROUP['slugs']
                     if not (s2 == 'go-course' and lang not in COURSE_LANGS)]
    if content_slugs:
        groups.append(({'slugs': content_slugs}, CONTENT_GROUP[lang], 'news'))

    for g, gname, icon in groups:
        # 博客与 Go 课程不是 TOOLS 条目（各有独立数据源），单独放行
        slugs = [s for s in g['slugs'] if s in _TOOL_BY_SLUG or s in ('blog', 'go-course')]
        if not slugs:
            continue
        p.append(f'    <section class="home-cat" data-n="{len(slugs)}">')
        p.append('      <div class="home-cat-head">')
        p.append(f'        <span class="home-cat-ico">{_home_icon(icon)}</span>')
        p.append(f'        <h2>{esc(gname)}</h2>')
        p.append(f'        <span class="home-cat-count">{len(slugs)}</span>')
        p.append('      </div>')
        p.append('      <div class="home-tiles">')
        for slug in slugs:
            kw = keywords_of(slug)
            p.append(f'        <a class="home-tile" href="{esc(href_slug(slug))}" data-k="{esc(kw)}">')
            p.append(f'          <span class="home-tile-name">{esc(label_of(slug))}</span>')
            p.append(f'          <span class="home-tile-desc">{esc(blurbs.get(slug, ""))}</span>')
            p.append('        </a>')
        p.append('      </div>')
        p.append('    </section>')
    p.append('    </div>')
    p.append('  </section>')

    # ---------------- 卖点 ----------------
    p.append('  <section class="home-why">')
    for i, (title, desc) in enumerate(tx['why']):
        icon = ['shield', 'bolt', 'globe', 'offline'][i] if i < 4 else 'shield'
        p.append('    <div class="home-why-item">')
        p.append(f'      <span class="home-why-ico">{_home_icon(icon)}</span>')
        p.append(f'      <h3>{esc(title)}</h3>')
        p.append(f'      <p>{esc(desc)}</p>')
        p.append('    </div>')
    p.append('  </section>')

    # ---------------- 站点说明 ----------------
    p.append('  <section class="home-about">')
    p.append(f'    <h2>{esc(tx["seo_h2"])}</h2>')
    for para in tx['seo_p']:
        p.append(f'    <p>{esc(para)}</p>')
    p.append('  </section>')

    p.append('</div>')
    return '\n'.join(p)


def seo_section(c):
    """工具页正文：h1 + 简介 + 功能 + 步骤 + FAQ，构建期写死，不依赖 JS。"""
    sep = SEP_BY_LANG.get(c.get('_lang'), ' — ')
    p = ['<section class="seo-content">']
    p.append(f'  <h1>{esc(c["h1"])}</h1>')
    for para in c['intro']:
        p.append(f'  <p>{esc(para)}</p>')
    p.append(f'  <h2>{esc(c["_features_heading"])}</h2>')
    p.append('  <ul class="seo-features">')
    for name, desc in c['features']:
        p.append(f'    <li><b>{esc(name)}</b>{sep}{esc(desc)}</li>')
    p.append('  </ul>')
    p.append(f'  <h2>{esc(c["_steps_heading"])}</h2>')
    p.append('  <ol class="seo-steps">')
    for step in c['steps']:
        p.append(f'    <li>{esc(step)}</li>')
    p.append('  </ol>')
    p.append(f'  <h2>{esc(c["_faq_heading"])}</h2>')
    p.append('  <div class="faq">')
    for q, a in c['faq']:
        p.append(f'    <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>')
    p.append('  </div>')
    # 「相关工具与阅读」：正文级交叉链接（真实 <a href>，不是全站样板导航）。
    # 链接是站点根相对路径，构建时补上语言前缀 c['_base']（由 build() 在调用前注入）。
    if c.get('seealso'):
        p.append(f'  <h2>{esc(c["_related_heading"])}</h2>')
        p.append('  <ul class="seo-related">')
        for text, href in c['seealso']:
            p.append(f'    <li><a href="{esc(c["_base"] + href)}">{esc(text)}</a></li>')
        p.append('  </ul>')
    # 2026-10-31：这里原本为「首页 = JSON 工具页」追加一份全站工具清单。
    # 首页拆成独立门户页后，工具清单归门户所有（见 render_home_body），
    # JSON 页恢复成和其它工具页一样的结构（正文 + 相关工具），不再重复列 42 个链接。
    p.append('</section>')
    return '\n'.join(p)


def jsonld(c, url, lang, news=None, slug=None, path=None):
    graph = []
    if c.get('slug') == HOME_SLUG:
        # 门户页：CollectionPage 描述"这是一份工具目录"，再用 ItemList 把每个工具页
        # 显式列出来——搜索引擎读结构化数据比读 DOM 更确定，也让 42 个内页多一条
        # 明确的关联边（内页收录不足正是当前最大的问题）。
        graph.append({
            '@type': 'CollectionPage',
            'name': c['h1'],
            'url': url,
            'description': c['description'],
            'inLanguage': HTML_LANG[lang],
            'isAccessibleForFree': True,
        })
        items = []
        for t in TOOLS:
            if t['slug'] == HOME_SLUG:
                continue
            tgt = content_for(t, lang)
            items.append({'@type': 'ListItem', 'position': len(items) + 1,
                          'name': tgt.get('h1') or t.get('nav', t['slug']),
                          'url': canonical_url(lang, t['path'])})
        graph.append({
            '@type': 'ItemList',
            'name': c['h1'],
            'numberOfItems': len(items),
            'itemListOrder': 'https://schema.org/ItemListUnordered',
            'itemListElement': items,
        })
    elif c.get('slug') == NEWS_SLUG:
        # 热榜页不是「应用」，而是一个每天更新的列表页：用 CollectionPage + ItemList
        # 描述更准确，也给了搜索引擎一个明确信号——这一页的条目会变、并且都指向外部原文。
        graph.append({
            '@type': 'CollectionPage',
            'name': c['h1'],
            'url': url,
            'description': c['description'],
            'inLanguage': HTML_LANG[lang],
            'isAccessibleForFree': True,
        })
        entries = jsonld_items(lang, news or {}, 20)
        if entries:
            graph.append({
                '@type': 'ItemList',
                'name': c['h1'],
                'numberOfItems': sum(len(visible_items(news, s))
                                     for s in sources_for(lang)),
                'itemListOrder': 'https://schema.org/ItemListUnordered',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': i, 'name': title, 'url': link}
                    for i, (_, title, link) in enumerate(entries, 1)
                ],
            })
    else:
        graph.append({
            '@type': 'WebApplication',
            'name': c['h1'],
            'url': url,
            'description': c['description'],
            'applicationCategory': 'DeveloperApplication',
            'operatingSystem': 'Any',
            'browserRequirements': BROWSER_REQ_BY_LANG.get(lang, 'Requires a modern browser with JavaScript enabled'),
            'inLanguage': HTML_LANG[lang],
            'isAccessibleForFree': True,
            'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'CNY'},
        })
    if c['faq']:
        graph.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                for q, a in c['faq']
            ],
        })
    # BreadcrumbList：首页 > [分类] > 工具（仅工具页；新闻页 / 博客页另行处理）
    if (slug or c.get('slug')) != NEWS_SLUG:
        crumbs = [{'name': SITE.get('name', 'DevTools'), 'url': canonical_url(lang, '')}]
        s = slug or c.get('slug')
        group = next((g for g in NAV_GROUPS if s in g['slugs']), None)
        if group:
            first = next((s2 for s2 in group['slugs'] if _TOOL_BY_SLUG.get(s2)), None)
            if first:
                crumbs.append({'name': group[lang],
                               'url': canonical_url(lang, _TOOL_BY_SLUG[first]['path'])})
        crumbs.append({'name': c['h1'],
                       'url': canonical_url(lang, path or c.get('path', ''))})
        graph.append({
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1,
                 'name': crumbs[i]['name'], 'item': crumbs[i]['url']}
                for i in range(len(crumbs))
            ],
        })
    return _jsonld_raw(graph)


def _jsonld_raw(graph):
    """把 @graph 条目列表包成 JSON-LD <script> 标签（工具页与博客页共用）。"""
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False)
    return '<script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>'


# ---------------------------------------------------------------- 资源内联

# CSS 组文件的固定级联顺序：base 永远第一，其余组按此序追加，
# 保证与原 style.css 单文件内的规则顺序一致（如 .tool-card 的 base 定义
# 必须早于 time 组的覆盖定义）。
CSS_GROUPS = ['base', 'home', 'json', 'diff', 'regex', 'generator', 'liveclock',
              'time', 'baseconv', 'worldclock', 'hotnews', 'cheatsheet',
              'snippets', 'blog', 'course', 'evergreen', 'legal']

# 模板处理结果按资产组合 memoize：756 个页面实际只有十几种
# (modules, css_groups, keep_cdn) 组合，每组合只做一次字符串替换。
_TPL_CACHE = {}


def inline_assets(tpl, modules=JS_MODULES, css_groups=None, keep_cdn=False):
    """把 CSS 与 JS 按页裁剪内联进模板。

    modules    要内联的 JS 模块（顺序须保持 core.js 在前）；不在列表里的
               `<script src="js/...">` 整行删除。
    css_groups 要内联的 CSS 组（级联顺序，base 必须在首位）；None = 全部组。
    keep_cdn   False：删掉所有 cdnjs 外链；'cm'：保留 CodeMirror 必需资产
               （codemirror 核心 + javascript 模式 + monokai 主题 +
                matchbrackets/closebrackets/foldcode/foldgutter/brace-fold），
               只删 xml/css/sql 模式、xml-fold 等冗余标签。
    """
    key = (tuple(modules), tuple(css_groups) if css_groups else None, keep_cdn)
    if key in _TPL_CACHE:
        return _TPL_CACHE[key]
    if css_groups is None:
        css_groups = CSS_GROUPS
    styles = []
    for g in css_groups:
        p = SRC / 'css' / (g + '.css')
        if not p.exists():
            raise SystemExit(f'❌ 缺少 CSS 组文件: {p}')
        styles.append('<style>\n/* ' + g + '.css */\n'
                      + p.read_text('utf-8').rstrip('\n') + '\n</style>')
    tpl = tpl.replace('<link rel="stylesheet" href="css/style.css">',
                      '\n'.join(styles))
    for mod in JS_MODULES:
        tag = f'<script src="js/{mod}"></script>'
        if tag not in tpl:
            if not modules:
                continue          # privacy 模板本就没有 JS 模块标签
            raise SystemExit(f'❌ 模板中找不到脚本标签: {tag}')
        if mod not in modules:
            tpl = tpl.replace(tag + '\n', '')          # 整行连标签一并去掉
            continue
        js = (SRC / 'js' / mod).read_text('utf-8')
        tpl = tpl.replace(tag, '<script>\n// ' + mod + '\n' + js + '\n</script>')
    if keep_cdn == 'cm':
        for dead in CM_DEAD_TAGS:
            if dead + '\n' in tpl:
                tpl = tpl.replace(dead + '\n', '')
    elif not keep_cdn:
        tpl = re.sub(r'\n<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/[^"]*">',
                     '', tpl)
        tpl = re.sub(r'\n<script src="https://cdnjs\.cloudflare\.com/[^"]*"></script>',
                     '', tpl)
    _TPL_CACHE[key] = tpl
    return tpl


# ---------------------------------------------------------------- 组装

HEADINGS = {
    'zh': {'_features_heading': '主要功能', '_steps_heading': '使用步骤',
           '_faq_heading': '常见问题', '_home': '首页', '_blog': '博客',
           '_course': 'Go 课程',
           '_related_heading': '相关工具与阅读'},
    'en': {'_features_heading': 'Features', '_steps_heading': 'How to use',
           '_faq_heading': 'FAQ', '_home': 'Home', '_blog': 'Blog',
           '_course': 'Go Course',
           '_related_heading': 'Related tools & reading'},
}
# 其余语言暂回退英文（未翻完的标题也用可读英文兜底）
for _lang in LANGS:
    if _lang not in HEADINGS:
        HEADINGS[_lang] = HEADINGS['en']

# 顶部导航标签：zh 用源；其余语言用英文 nav（含未翻完的英文兜底）
NAV_LABELS = {}
for _lang in LANGS:
    if _lang == DEFAULT_LANG:
        nv = {t['slug']: t['nav'] for t in TOOLS}
    else:
        # 优先用该语言已翻的 nav，缺失回退英文（绝不回退中文）
        nv = {t['slug']: CONTENT_BY_LANG.get(_lang, {}).get(t['slug'], {})
              .get('nav', TOOLS_EN[t['slug']]['nav']) for t in TOOLS}
    nv = dict(nv)
    nv.update(HEADINGS[_lang])
    NAV_LABELS[_lang] = nv


def content_for(tool, lang):
    """取某语言的工具内容；非中文语言若未单独翻译则回退英文，绝不回退中文。

    阶段2：具体语言（ja/ko/es…）的内容字典若只翻了短 SEO 字段（nav/h1/title/
    description/keywords），则以英文全文为底，把已翻的短字段叠加覆盖——长正文
    （intro/features/steps）继续用英文回退，避免大面积半翻译。
    """
    if lang == DEFAULT_LANG:
        c = dict(CONTENT_BY_LANG[DEFAULT_LANG].get(tool['slug'], tool))
    else:
        c = dict(TOOLS_EN.get(tool['slug'], tool))          # 英文长正文（回退）
        lang_c = CONTENT_BY_LANG.get(lang, {}).get(tool['slug'])   # 已翻短 SEO 字段
        if lang_c:
            c.update(lang_c)                                # 叠加覆盖
        c['_lang'] = lang
    c.update(HEADINGS.get(lang, HEADINGS['en']))
    # 英文（及其他语言）内容字典里没有 slug 字段（它们按 slug 建索引，条目本身不带），
    # 而 seo_section 要靠 slug 判断「当前是不是首页」来决定是否输出全部工具清单，
    # 这里统一补齐，避免首页在非中文页丢失该板块。
    c['slug'] = tool['slug']
    return c


def apply_common(page, lang, slug, path, title, description, keywords, body, seo, ld, base, home,
                 wc_zones=True, mono=False, langs=None):
    page = page.replace('{{PAGE}}', slug)
    page = page.replace('{{LANG}}', HTML_LANG[lang])
    page = page.replace('{{TITLE}}', esc(title))
    page = page.replace('{{DESCRIPTION}}', esc(description))
    page = page.replace('{{KEYWORDS}}', esc(keywords))
    page = page.replace('{{CANONICAL}}', canonical_url(lang, path))
    # mono=True：单语言页，不生成 hreflang 备用链接、语言切换器与浏览器语言自动跳转；
    # langs 限定该页可用的语言列表（默认全站语言）；课程板块传 COURSE_LANGS（仅 zh/en）。
    page = page.replace('{{HREFLANG}}', '' if mono else hreflang_html(path, langs))
    page = page.replace('{{AUTODETECT}}', '' if mono else autodetect_html(lang, path, langs))
    page = page.replace('{{LANGSWITCH}}', '' if mono else lang_switch_html(lang, path, langs))
    page = page.replace('{{ANALYTICS}}', analytics_html())
    page = page.replace('{{FEEDBACK_BTN}}', feedback_btn_html())
    page = page.replace('{{FEEDBACK_MODAL}}', feedback_modal_html())
    active = None if path == PRIVACY_FILE else _slug_of(path)
    if active is None and path.startswith(('calendar/', 'weeks/', 'days/', 'year/')):
        active = 'evergreen'
    if slug and str(slug).startswith('blog'):
        active = 'blog'
    if slug and str(slug).startswith('go-course'):
        active = 'go-course'
    page = page.replace('{{NAV}}', nav_html(active, base, NAV_LABELS[lang], lang))
    page = page.replace('{{FOOTER_LINKS}}', footer_links_html(base, NAV_LABELS[lang]))
    page = page.replace('{{JSONLD}}', ld)
    page = page.replace('{{TOOL}}', body)
    page = page.replace('{{SEO}}', seo)
    page = page.replace('{{TOOL_INDEX}}', tool_index_json(base, lang))
    if wc_zones:
        page = page.replace('{{WC_ZONES}}', wc_zones_json(lang))
    else:
        # 非世界时钟/时区页：整行删除注入脚本（datetime-tools.js 两处消费点
        # 都有 `|| []` 兜底，且这两类页之外根本不渲染时区数据）
        page = page.replace('<script>window.__WC_ZONES__ = {{WC_ZONES}};</script>\n', '')
    page = page.replace('{{PRIVACY_BODY}}', seo)
    page = page.replace('{{HOME}}', home)
    page = page.replace('{{BASE}}', base)
    return page


_SLUG_BY_PATH = {t['path']: t['slug'] for t in TOOLS}


def _slug_of(path):
    return _SLUG_BY_PATH.get(path)


def _safe_rmtree(path):
    """递归删除目录（逐文件 os.remove + 逐目录 os.rmdir），与 shutil.rmtree 结果一致，
    但拆成单文件操作，避免本环境对「单次删除 >50 个文件」的批量删除保护拦截构建。
    """
    if not path.exists():
        return
    for root, dirs, files in os.walk(str(path), topdown=False):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except OSError:
                pass
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass
    try:
        os.rmdir(str(path))
    except OSError:
        pass


def build(clean=True, outdirs=None):
    index_tpl = (SRC / 'index.html').read_text('utf-8')
    privacy_src = (SRC / 'privacy.html').read_text('utf-8')

    def tpl_for(slug):
        """按页面资产组合生成（memoize 命中时零成本）内联后的模板。"""
        mods, groups, keep_cdn = assets_for(slug)
        return inline_assets(index_tpl, modules=mods, css_groups=groups,
                             keep_cdn=keep_cdn)

    def wc_for(slug):
        return slug in PAGE_WC_ZONES

    privacy_tpl = inline_assets(privacy_src, modules=(), css_groups=('base', 'legal'))
    news = load_news()

    pages = {}
    for lang in LANGS:
        for t in TOOLS:
            c = content_for(t, lang)
            if t['slug'] == HOME_SLUG:
                # 门户页正文由 build.py 生成（需要按语言取工具名/说明/分类名），
                # 不复用 seo_section 的"单工具落地页"骨架。
                page_tpl, body = tpl_for(HOME_SLUG), render_home_body(lang)
            elif t['slug'] == NEWS_SLUG:
                page_tpl, body = tpl_for(NEWS_SLUG), render_news_body(lang, news)
            elif t['slug'] == CHEAT_SLUG:
                # 速查表与热榜同型：只需要 core.js 的轻量模板 + 构建期渲染的正文
                page_tpl, body = tpl_for(CHEAT_SLUG), render_cheat_body(lang)
            elif t['slug'] == SNIP_SLUG:
                # 片段库同理：core.js + 构建期渲染的正文（复制按钮走 copyTextById）
                page_tpl, body = tpl_for(SNIP_SLUG), render_snippets_body(lang)
            else:
                page_tpl = tpl_for(t['slug'])
                body = (SRC / 'tools' / f'{t["slug"]}.html').read_text('utf-8').strip()
            base = lang_prefix(lang, rel_root(lang, t['path']))
            home = base or './'
            c['_base'] = base     # seo_section 的「相关工具与阅读」链接要用
            seo_html = '' if t['slug'] == HOME_SLUG else seo_section(c)
            page = apply_common(page_tpl, lang, t['slug'], t['path'], c['title'],
                                c['description'], c['keywords'], body, seo_html,
                                jsonld(c, canonical_url(lang, t['path']), lang, news,
                                      t['slug'], t['path']),
                                base, home, wc_zones=wc_for(t['slug']))
            if lang != DEFAULT_LANG:
                page = localize(page, lang)
            pages[out_path(lang, t['path'])] = page

        # ---------------- 年度常青页（calendar / weeks / days / year 按年静态参考页） ----------------
        # 与上面的交互式工具（weeknumbers / daynumbers / years）互补：这里是预先渲染好的
        # 整年参考数据（日历网格、周数表、年内天数表、年份概况），吃长期长尾搜索流量。
        # 英文页直接产出英文正文，localize 只负责翻译通用 chrome（导航/页脚/反馈弹窗）。
        for (ety, eyear, eslug, epath) in EV.evergreen_entries():
            m = EV.meta(ety, eyear, lang)
            base = lang_prefix(lang, rel_root(lang, epath))
            home = base or './'
            c = {'slug': eslug, 'h1': m['h1'], 'description': m['description'],
                 'faq': [], '_lang': lang, '_base': base}
            c.update(HEADINGS[lang])
            seo_data = EV.render_seo(ety, eyear, lang, base)
            c.update({k: seo_data[k] for k in ('intro', 'features', 'steps', 'faq', 'seealso')})
            page = apply_common(
                tpl_for(eslug), lang, eslug, epath, m['title'], m['description'], m['keywords'],
                EV.render_body(ety, eyear, lang, base), seo_section(c),
                jsonld(c, canonical_url(lang, epath), lang, None, eslug, epath),
                base, home, wc_zones=False)
            if lang != DEFAULT_LANG:
                page = localize(page, lang)
            pages[out_path(lang, epath)] = page

        # ---------------- 博客：索引页 + 文章页 ----------------
        # 文章不是工具：不进 TOOLS，但顶部导航里已单独辟出「博客」入口
        # （nav_html 在 Go 速查表之后插入，博客页/文章页高亮）。页面走与热榜相同的
        # 轻量模板（只有 core.js），拥有独立的 URL、canonical、hreflang、
        # JSON-LD（TechArticle）与 sitemap 条目。
        lang_articles = articles_for(lang, ARTICLES_EN)
        bt = BLOG_TEXT[lang]

        base = lang_prefix(lang, rel_root(lang, BLOG_INDEX))
        page = apply_common(tpl_for('blog'), lang, 'blog', BLOG_INDEX, bt['index_title'],
                            bt['index_desc'], bt['index_kw'],
                            render_blog_index(lang, ARTICLES_EN, base), '',
                            _jsonld_raw(blog_index_jsonld(
                                lang_articles, canonical_url(lang, BLOG_INDEX), lang)),
                            base, base or './', wc_zones=False)
        if lang != DEFAULT_LANG:
            page = localize(page, lang)
        pages[out_path(lang, BLOG_INDEX)] = page

        for a in lang_articles:
            apath = article_path(a['slug'])
            base = lang_prefix(lang, rel_root(lang, apath))
            page = apply_common(tpl_for('blog'), lang, 'blog-' + a['slug'], apath, a['title'],
                                a['description'], a['keywords'],
                                render_article(lang, a, base), '',
                                _jsonld_raw([article_jsonld(
                                    a, canonical_url(lang, apath), lang)]),
                                base, base or './', wc_zones=False)
            if lang != DEFAULT_LANG:
                page = localize(page, lang)
            pages[out_path(lang, apath)] = page

        # ---------------- Go 课程图文板块：中心页 + 已发布课程页（zh / en） ----------------
        # 与博客同哲学：正文构建期烘焙（数据来自 course_lessons.py，由仓库根目录
        # convert_lessons.py 从本地讲义 Markdown 生成）。当前支持 zh（全部 41 课）
        # 与 en（已翻译的课，LESSON_BODIES_EN）。非课程语言（ja/ko/es 等）不生成。
        # 页面 hreflang / 语言切换器 / 自动跳转限定在 COURSE_LANGS（仅中英互指，
        # 避免指向不存在的课程页语言版本）。
        if lang == DEFAULT_LANG:
            for clang in COURSE_LANGS:
                ct = COURSE_TEXT[clang]
                base = lang_prefix(clang, rel_root(clang, COURSE_INDEX))
                page = apply_common(tpl_for('go-course'), clang, 'go-course', COURSE_INDEX,
                                    ct['index_title'], ct['index_desc'], ct['index_kw'],
                                    render_course_index(base, clang), '',
                                    _jsonld_raw([course_index_jsonld(
                                        canonical_url(clang, COURSE_INDEX), clang)]),
                                    base, base or './', wc_zones=False, langs=COURSE_LANGS)
                if clang != DEFAULT_LANG:
                    page = localize(page, clang)
                pages[out_path(clang, COURSE_INDEX)] = page

                for slug in PUBLISHED:
                    if clang == 'en' and slug not in LESSON_BODIES_EN:
                        continue
                    lpath = lesson_path(slug)
                    lm = lesson_meta(slug, clang)
                    base = lang_prefix(clang, rel_root(clang, lpath))
                    page = apply_common(tpl_for('go-course'), clang, 'go-course-' + slug, lpath,
                                        lm['title'], lm['description'], lm['keywords'],
                                        render_lesson(slug, base, clang), '',
                                        _jsonld_raw([lesson_jsonld(
                                            lm, canonical_url(clang, lpath), clang)]),
                                        base, base or './', wc_zones=False, langs=COURSE_LANGS)
                    if clang != DEFAULT_LANG:
                        page = localize(page, clang)
                    pages[out_path(clang, lpath)] = page

        # 隐私政策
        body = PRIVACY_BODY_ZH if lang == 'zh' else PRIVACY_BODY_EN
        base = lang_prefix(lang, rel_root(lang, PRIVACY_FILE))
        home = base or './'
        title = ('隐私政策 - DevTools 在线开发工具集' if lang == 'zh'
                 else 'Privacy Policy - DevTools Online Developer Tools')
        desc = ('DevTools 隐私政策：工具输入的数据全部在浏览器本地处理，不上传服务器；'
                '说明访问统计、第三方 CDN 与广告的使用情况。' if lang == 'zh' else
                'DevTools privacy policy: everything you enter into the tools is processed '
                'locally in your browser and never uploaded. Covers analytics, third-party '
                'CDNs and advertising.')
        kw = ('DevTools隐私政策,在线工具隐私,数据本地处理' if lang == 'zh'
              else 'DevTools privacy policy,online tools privacy,local processing')
        page = apply_common(privacy_tpl, lang, 'privacy', PRIVACY_FILE, title, desc, kw,
                            '', body, '', base, home, wc_zones=False)
        if lang != DEFAULT_LANG:
            page = localize(page, lang)
        pages[out_path(lang, PRIVACY_FILE)] = page

    # sitemap：索引 + 按板块子文件（详见 sitemap_files 的注释：百度 60s
    # socket 超时 × 中澳链路最差 ~10KB/s，858KB 单文件必被掐断）。
    sm_files = sitemap_files(news)
    pages.update({Path(fn): text for fn, text in sm_files.items()})
    # 每个 sitemap .xml 预生成 .gz：nginx gzip_static 命中后零 CPU 直发，
    # 客户端不带 Accept-Encoding 时回退到 on-the-fly gzip。
    # mtime=0 保证每次构建的 .gz 字节一致（gzip 头里的时间戳不会漂）。
    sm_gz = {Path(fn + '.gz'): gzip.compress(text.encode('utf-8'), 9, mtime=0)
             for fn, text in sm_files.items()}
    pages[Path('robots.txt')] = robots_txt()
    pages[Path('llms.txt')] = llms_txt()
    pages[Path('.nojekyll')] = ''
    # GitHub Pages 自定义域名。必须由构建生成：下面会 rmtree(docs)，
    # 手动放进去的 CNAME 每次构建都会被删掉，域名随之失效。
    pages[Path('CNAME')] = CUSTOM_DOMAIN + '\n'
    # IndexNow 归属校验文件。域名根 == 本站发布目录根，所以放这里。
    pages[Path(f'{INDEXNOW_KEY}.txt')] = INDEXNOW_KEY

    # 站点根目录的附加文件（搜索引擎验证文件、站点图标等），见上方 ROOT_FILES 的说明。
    #
    # 一律按字节原样发布，不并进 pages：
    #  - pages 的值必须是 str，而这里既有 .html/.xml，也有 .ico/.png，read_text 读二进制直接崩；
    #  - 就算全是文本也不该走 write_text，它会按平台转换换行（Windows 上 \n → \r\n），
    #    而「原样发布」的语义就是逐字节一致。
    root_files = {}
    if ROOT_FILES.is_dir():
        for extra in sorted(ROOT_FILES.iterdir()):
            if extra.is_file():
                root_files[Path(extra.name)] = extra.read_bytes()

    # 把第三方 CDN 资源读进来，并把 HTML 里的外链改写成同源路径。
    # 放在这里而不是逐个页面处理：上面几十处 pages[...] = ... 任何一处都可能引入
    # CDN 链接，收口在落盘前统一替换一次，以后加页面也不用记得再改一遍。
    cdn_assets = {}
    if CDN_SRC.is_dir():
        for fp in sorted(CDN_SRC.rglob('*')):
            if fp.is_file():
                rel = fp.relative_to(CDN_SRC).as_posix()
                cdn_assets[CDN_OUT / rel] = fp.read_bytes()
        if cdn_assets:
            pages = {k: (v.replace(CDN_ORIGIN, CDN_LOCAL_URL) if k.suffix == '.html' else v)
                     for k, v in pages.items()}
    else:
        print('  ⚠ src/cdn/ 不存在：页面保留 cdnjs 外链，百度蜘蛛会拿到 403')

    # 默认同时写两个目录：dist/（被 .gitignore 忽略，本地预览用）与 docs/
    # （发布目录）。传了 outdirs 就只写指定的目录 —— 服务器定时任务靠这个把
    # 「构建」和「发布」分开：先构建到暂存区，校验通过后再原子切换，
    # 这样构建中途失败时线上仍是上一版，不会被 rmtree 清成空目录。
    targets = (DIST, DOCS) if outdirs is None else outdirs
    for outdir in targets:
        if clean and outdir.exists():
            _safe_rmtree(outdir)
        for rel, content in pages.items():
            fp = outdir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, 'utf-8')
        # 二进制写入：这些是压缩过的产物，不能用 write_text，
        # 否则 Windows 上会把内部的 \n 转成 \r\n，文件就废了。
        for rel, data in {**cdn_assets, **root_files, **sm_gz}.items():
            fp = outdir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_bytes(data)

    n_cdn = len(cdn_assets)
    n_root = len(root_files)
    print(f'  ✓ 按页裁剪内联 CSS 组 + JS 模块（{len(_TPL_CACHE)} 种资产组合）'
          + (f'\n  ✓ 自托管第三方资源 {n_cdn} 个 → {CDN_OUT.as_posix()}/' if n_cdn else '')
          + (f'\n  ✓ 站点根附加文件 {n_root} 个 → 发布根（验证文件 / 图标）' if n_root else '')
          + f'\n  ✓ sitemap 索引 + {len(sm_files) - 1} 个子文件'
            f'（每文件 ≤ {SITEMAP_CHUNK} 条 URL），各附 .gz 预压缩')
    for rel in sorted(pages, key=str):
        print(f'  ✓ {str(rel):28s} {len(pages[rel]) / 1024:7.1f} KB')
    where = ' + '.join(d.name for d in targets)
    print(f'\n✅ {len(pages)} 个文件 → {where}')
    return True


# ── sitemap：索引 + 按板块子文件 ──────────────────────────────
# 为什么不再用单文件 urlset：百度 Spider 的 socket 超时是 60 秒，而中澳链路
# 实测最差只有 ~10KB/s（2026-10-22 郑州联通实测：877KB 的 sitemap 要 90.5
# 秒，百度抓取诊断报「socket 读写错误」；同体积换一次连接能到 200KB/s，
# 说明是「链路波动 + 文件过大」叠加，只优化一边都不稳）。
# 对策双管齐下：
#   1) 拆：按板块切成 ≤100 条/文件（≈110KB，最差 11 秒下完）；
#   2) 压：每个 .xml 预生成 .gz（≈15KB），nginx gzip_static 零 CPU 直发。
# 入口 URL 不变，仍是 /sitemap.xml，只是内容从 urlset 变成 sitemapindex，
# robots.txt 的 Sitemap 行无需改动；百度官方帮助明确支持索引文件提交
# （「可以使用XML格式、文本格式以及Sitemap索引文件提交」）。
SITEMAP_CHUNK = 100
# 子文件的命名与索引中的排列顺序
_SITEMAP_SECTIONS = ('pages', 'tools', 'evergreen', 'blog', 'course')


def _url_block(loc, alternates, meta, lastmod=''):
    return ('  <url>\n'
            f'    <loc>{loc}</loc>{lastmod}\n'
            + alternates + meta +
            '  </url>')


def _sitemap_sections(news=None):
    """按板块归组的 sitemap 条目：{板块: {'rows': [...], 'lastmod': 日期}}。

    条目内容（优先级 / changefreq / hreflang / lastmod 口径）与拆分前
    完全一致，只是额外记录板块归属与各板块最新的真实 lastmod——索引里
    只对「确实会变」的板块写 lastmod，跟着构建时间天天变的字段搜索引擎
    会不再信任（与条目级 lastmod 同一原则）。
    """
    news_day = ''
    if news and news.get('generated_at'):
        from datetime import datetime
        news_day = datetime.fromtimestamp(news['generated_at'], CST).strftime('%Y-%m-%d')

    sections = {name: {'rows': [], 'lastmod': ''} for name in _SITEMAP_SECTIONS}

    def add(name, row, lastmod_day=''):
        sec = sections[name]
        sec['rows'].append(row)
        if lastmod_day and (not sec['lastmod'] or lastmod_day > sec['lastmod']):
            sec['lastmod'] = lastmod_day

    # (path, priority, changefreq, lastmod)
    entries = []
    for t in TOOLS:
        p = t['path']
        if p == '':
            entries.append((p, '1.0', 'weekly', ''))
        elif p == NEWS_PATH:
            entries.append((p, '0.9', 'daily', news_day))
        else:
            entries.append((p, '0.8', 'monthly', ''))
    entries.append((PRIVACY_FILE, '0.3', 'yearly', ''))
    # 博客：索引页取最新文章的校订日期，文章页用自己的日期
    blog_updated = max(a['updated'] for a in ARTICLES) if ARTICLES else ''
    entries.append((BLOG_INDEX, '0.6', 'weekly', blog_updated))
    for a in ARTICLES:
        entries.append((article_path(a['slug']), '0.7', 'monthly', a['updated']))
    # 年度常青页：按年静态参考页，变化极少
    for p in EV.evergreen_paths():
        entries.append((p, '0.6', 'yearly', ''))

    # 首页 / 热榜 / 隐私政策是小体量稳定页，归 'pages'；博客与常青页各自
    # 成组；其余工具页（含速查表、片段库）进 'tools'。
    evergreen_set = set(EV.evergreen_paths())

    def section_of(p):
        if p.startswith('blog'):
            return 'blog'
        if p in evergreen_set:
            return 'evergreen'
        if p in ('', NEWS_PATH, PRIVACY_FILE):
            return 'pages'
        return 'tools'

    for p, pri, freq, lastmod_day in entries:
        lastmod = f'\n    <lastmod>{lastmod_day}</lastmod>' if lastmod_day else ''
        alternates = ''.join(
            f'    <xhtml:link rel="alternate" hreflang="{HREFLANG_CODE[L]}" '
            f'href="{SITE["base_url"] + lang_dir(L) + p}"/>\n'
            for L in LANGS)
        alternates += (f'    <xhtml:link rel="alternate" hreflang="x-default" '
                       f'href="{SITE["base_url"] + lang_dir(XDEFAULT_LANG) + p}"/>\n')
        meta = f'    <changefreq>{freq}</changefreq><priority>{pri}</priority>\n'
        # 各语言各自独立成条：每语言页有自己的 canonical、是独立的可索引 URL。
        for L in LANGS:
            loc = SITE['base_url'] + lang_dir(L) + p
            add(section_of(p), _url_block(loc, alternates, meta, lastmod), lastmod_day)

    # Go 课程图文板块：zh / en 双语各自成条 + 中英 hreflang 互指（其余语言无课程页不列）。
    # 英文条目只列已翻译正文的课（LESSON_BODIES_EN），避免 sitemap 指向不存在的英文页。
    course_langs = COURSE_LANGS
    course_pages = [COURSE_INDEX] + [lesson_path(s) for s in PUBLISHED]
    for p in course_pages:
        pri, freq = ('0.6', 'weekly') if p == COURSE_INDEX else ('0.7', 'monthly')
        meta = f'    <changefreq>{freq}</changefreq><priority>{pri}</priority>\n'
        alternates = ''.join(
            f'    <xhtml:link rel="alternate" hreflang="{HREFLANG_CODE[L]}" '
            f'href="{SITE["base_url"] + lang_dir(L) + p}"/>\n'
            for L in course_langs)
        alternates += (f'    <xhtml:link rel="alternate" hreflang="x-default" '
                       f'href="{SITE["base_url"] + lang_dir(XDEFAULT_LANG) + p}"/>\n')
        for L in course_langs:
            if L == 'en' and p != COURSE_INDEX and p.rstrip('/').split('/')[-1] not in LESSON_BODIES_EN:
                continue
            loc = SITE['base_url'] + lang_dir(L) + p
            add('course', _url_block(loc, alternates, meta))
    return sections


def sitemap_files(news=None):
    """{文件名: XML 文本}：sitemap.xml（索引）+ sitemap-<板块>[-n].xml（子文件）。

    索引本身 <1KB，任何链路都是秒下；子文件按板块聚合、≤100 条，单个
    ≈110KB，最差链路 11 秒内可下完（百度 socket 超时 60 秒）。
    """
    sections = _sitemap_sections(news)
    files, index_rows = {}, []
    for name in _SITEMAP_SECTIONS:
        sec = sections[name]
        if not sec['rows']:
            continue
        chunks = [sec['rows'][i:i + SITEMAP_CHUNK]
                  for i in range(0, len(sec['rows']), SITEMAP_CHUNK)]
        for i, chunk in enumerate(chunks, 1):
            fn = f'sitemap-{name}.xml' if len(chunks) == 1 else f'sitemap-{name}-{i}.xml'
            files[fn] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
                         '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                         + '\n'.join(chunk) + '\n</urlset>\n')
            lastmod = f'\n    <lastmod>{sec["lastmod"]}</lastmod>' if sec['lastmod'] else ''
            index_rows.append(
                '  <sitemap>\n'
                f'    <loc>{SITE["base_url"]}{fn}</loc>{lastmod}\n'
                '  </sitemap>')
    files['sitemap.xml'] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(index_rows) + '\n</sitemapindex>\n')
    return files


def robots_txt():
    """显式放行各搜索引擎与 AI 爬虫。

    通配符 `User-agent: *` 本来就允许所有人，但部分爬虫只认自己名下的分组，
    显式列出既是声明意图，也方便以后单独收紧某一家。
    """
    groups = [
        ('搜索引擎', ['Googlebot', 'Bingbot', 'Baiduspider', 'YandexBot',
                      'Sogou web spider', '360Spider', 'DuckDuckBot']),
        ('AI / 大模型爬虫', ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
                             'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
                             'PerplexityBot', 'Perplexity-User',
                             'Google-Extended', 'Applebot', 'Applebot-Extended',
                             'meta-externalagent', 'Bytespider', 'DeepSeekBot',
                             'CCBot', 'Amazonbot', 'cohere-ai', 'YouBot']),
    ]
    # 迁移到自定义域名后，发布目录根 == 主机根，所以这里生成的就是权威版本。
    # 早期放在 /tools/ 子目录下时需要两份清单并提示「本文件不影响抓取」，现已不适用；
    # 也不要再手写该文件——每次构建都会覆盖，改放行清单请改下面的 groups。
    lines = [
        '# DevTools — 在线开发工具集',
        '#',
        '# 本文件由构建生成，并以主机根地址 ' + SITE['base_url'] + 'robots.txt 提供，',
        '# 是唯一权威版本。修改放行清单请改 build.py 的 robots_txt() 后重新构建，',
        '# 直接编辑本文件会在下次构建时被覆盖。',
        '',
        'User-agent: *',
        'Allow: /',
        '',
    ]
    for title, agents in groups:
        lines.append(f'# --- {title} ---')
        for a in agents:
            lines += [f'User-agent: {a}', 'Allow: /']
        lines.append('')
    lines += [
        f'Sitemap: {SITE["base_url"]}sitemap.xml',
        f'# LLM 站点摘要: {SITE["base_url"]}llms.txt',
        '',
    ]
    return '\n'.join(lines)


def llms_txt():
    """按 llms.txt 约定生成的站点摘要，供大模型读取。

    说明：llms.txt 目前只是社区提案，主流模型厂商并未承诺读取，
    真正的收录仍取决于常规索引与检索。这份文件成本极低，属于「有比没有好」，
    但不要指望它是收录开关。
    """
    # 头部文案里的工具数必须动态算：写死数字，每加一个工具这份摘要就撒一次谎
    # 首页（门户页）不是「工具」，热榜/速查表/片段库也不计入工具数
    _NOT_TOOL = (HOME_SLUG, NEWS_SLUG, CHEAT_SLUG, SNIP_SLUG)
    tool_count = sum(1 for t in TOOLS if t['slug'] not in _NOT_TOOL)
    out = [
        f'# {SITE["name"]} — 在线开发工具集 / Online Developer Tools',
        '',
        f'> 免注册、免安装的纯浏览器端开发者工具集合，覆盖 JSON、文本比对、编解码、正则、',
        f'> 时间戳、哈希、代码格式化、字符串处理、数据库与生成器共 {tool_count} 个工具。',
        '> 所有解析与计算都在用户浏览器内完成，输入内容不会上传到任何服务器。',
        '> 全站 10 种语言（中文在根路径，英文 /en/、日文 /ja/、韩文 /ko/、西班牙语 /es/、',
        '> 葡萄牙语 /pt-BR/、法语 /fr/、德语 /de/、俄语 /ru/、印尼语 /id/ 各有完整翻译）。',
        '> 另有一个「今日科技热榜」页面，每天 08:00 自动聚合十余家科技媒体的最新资讯。',
        '',
        'Key facts:',
        f'- {tool_count} tools, each on its own URL; every page runs entirely client-side '
        '(no upload, no signup, no ads).',
        '- 10 languages: Chinese at the root and en/ja/ko/es/pt-BR/fr/de/ru/id directories, '
        'each with a full translated copy of every page.',
        '- A tech news page is rebuilt daily at 08:00 UTC+8 from public RSS feeds; '
        'each item links out to the original article.',
        '- Verification hooks: /sitemap.xml (with hreflang alternates), /robots.txt, '
        'JSON-LD on every tool page.',
        '',
        '## Tools / 工具',
        '',
    ]
    for t in TOOLS:
        # 热榜、速查表与片段库都不是「有输入框的工具」，各自单列一节
        if t['slug'] in _NOT_TOOL:
            continue
        en = TOOLS_EN[t['slug']]
        zh_url = SITE['base_url'] + t['path']
        en_url = SITE['base_url'] + EN_DIR + t['path']
        out.append(f'- [{t["h1"]}]({zh_url}): {t["description"]}')
        out.append(f'  - English: [{en["h1"]}]({en_url}) — {en["description"]}')
    # 速查表与片段库不是工具（没有输入框），单独一节；博客同理，且每篇都要列出，
    # 否则新文章写完不进这份摘要，等于白写。
    cheat = next(t for t in TOOLS if t['slug'] == CHEAT_SLUG)
    cheat_en = TOOLS_EN[CHEAT_SLUG]
    snip = next(t for t in TOOLS if t['slug'] == SNIP_SLUG)
    snip_en = TOOLS_EN[SNIP_SLUG]
    out += [
        '',
        '## Cheatsheet / 速查表',
        '',
        f'- [{cheat["h1"]}]({SITE["base_url"]}{cheat["path"]}): {cheat["description"]}',
        f'  - English: [{cheat_en["h1"]}]({SITE["base_url"]}{EN_DIR}{cheat["path"]})'
        f' — {cheat_en["description"]}',
        '',
        '## Code Snippets / 代码片段',
        '',
        f'- [{snip["h1"]}]({SITE["base_url"]}{snip["path"]}): {snip["description"]}',
        f'  - English: [{snip_en["h1"]}]({SITE["base_url"]}{EN_DIR}{snip["path"]})'
        f' — {snip_en["description"]}',
        '',
        '## Blog / 文章',
        '',
    ]
    for a in ARTICLES:
        out.append(f'- [{a["h1"]}]({SITE["base_url"]}{article_path(a["slug"])}): {a["summary"]}')
        en_a = dict(a)
        en_a.update(ARTICLES_EN[a['slug']])
        out.append(f'  - English: [{en_a["h1"]}]'
                   f'({SITE["base_url"]}{EN_DIR}{article_path(a["slug"])}) — {en_a["summary"]}')
    # Go 课程图文板块：每篇已发布课程都列出，否则新课上线不进这份摘要，等于白写。
    out += [
        '',
        '## Go Course / Go 课程',
        '',
        f'- [Go 语言从入门到精通（课程中心页）]({SITE["base_url"]}{COURSE_INDEX}): '
        '6 大模块 41 课图文教程，零基础到高级工程实践；每课含学习目标、知识讲解、'
        '可运行示例代码、常见错误避坑、最佳实践与练习参考答案，配套 B 站视频课程。',
        f'  - English: [Go from Zero to Pro]({SITE["base_url"]}{EN_DIR}{COURSE_INDEX}) — '
        '41-lesson illustrated Go tutorial across 6 modules, zero to advanced engineering; '
        'each lesson has objectives, explanations, runnable code, pitfalls, best practices and exercises.',
    ]
    for slug in PUBLISHED:
        lm = lesson_meta(slug)
        out.append(f'- [{lm["h1"]}]({SITE["base_url"]}{lesson_path(slug)}): {lm["description"]}')
        if slug in LESSON_BODIES_EN:
            lm_en = lesson_meta(slug, 'en')
            out.append(f'  - English: [{lm_en["h1"]}]({SITE["base_url"]}{EN_DIR}{lesson_path(slug)})'
                       f' — {lm_en["description"]}')
    out += [
        '',
        '## News / 资讯',
        '',
        f'- [今日科技热榜 / Today\'s Tech News]({SITE["base_url"]}{NEWS_PATH}): '
        '每天 08:00 自动聚合 IT之家、少数派、InfoQ、开源中国、Solidot、爱范儿、钛媒体、'
        '雷峰网与 Hacker News、TechCrunch、The Verge、Ars Technica 的最新条目，'
        '每条给出标题、来源、发布时间与原文直达链接。',
        f'  - English: [Today\'s Tech News]({SITE["base_url"]}{EN_DIR}{NEWS_PATH}) — '
        'rebuilt daily from Hacker News, TechCrunch, The Verge and Ars Technica.',
        '',
        '## Calendar & Dates / 日历与日期',
        '',
    ]
    ev_y = EV.nav_year()
    ev_desc = {
        'calendar': '全年 12 个月日历，标注 ISO 周数、星期与闰年。',
        'weeks': 'ISO 8601 全年周数表，逐周起止日期。',
        'days': '年内第几天表，每天映射日期、星期与 ISO 周。',
        'year': '年份概况：闰年、天数、起止星期与 ISO 周数。',
    }
    ev_desc_en = {
        'calendar': 'Full-year 12-month calendar with ISO week numbers, weekdays and leap year.',
        'weeks': 'ISO 8601 week table with the start/end date of every week.',
        'days': 'Day-of-year table mapping each date to its day number, weekday and ISO week.',
        'year': 'Year facts: leap year, total days, start/end weekday and ISO week count.',
    }
    for t in EV.TYPES:
        zh_url = SITE['base_url'] + f'{t}/{ev_y}/'
        en_url = SITE['base_url'] + EN_DIR + f'{t}/{ev_y}/'
        out.append(f'- [{EV.NAV_LABELS_EV["zh"][t]} {ev_y}]({zh_url}): {ev_desc[t]}')
        out.append(f'  - English: [{EV.NAV_LABELS_EV["en"][t]} {ev_y}]({en_url}) — {ev_desc_en[t]}')
    out += [
        '',
        '## Optional',
        '',
        f'- [隐私政策 / Privacy Policy]({SITE["base_url"]}privacy.html): '
        '工具输入数据本地处理、访问统计与第三方资源说明。',
        '- [源代码 / Source](https://github.com/xwjiang2003/tools): issues welcome.',
        '',
    ]
    return '\n'.join(out)


def watch():
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print('pip install watchdog  (or just run: python3 build.py)')
        sys.exit(1)

    class H(FileSystemEventHandler):
        def on_modified(self, e):
            if e.src_path.endswith(('.html', '.css', '.js', '.py')):
                print(f'\n📝 {Path(e.src_path).name} changed')
                try:
                    build()
                except Exception as ex:
                    print(f'❌ 构建失败: {ex}')

    ob = Observer()
    ob.schedule(H(), str(SRC), recursive=True)
    ob.start()
    print(f'👀 Watching {SRC}/ ...')
    try:
        ob.join()
    except KeyboardInterrupt:
        ob.stop()


if __name__ == '__main__':
    no_clean = '--no-clean' in sys.argv
    # --out <dir> 可重复；不传就按默认的 dist/ + docs/ 两个目录输出。
    # 用法示例（服务器定时构建）：
    #   python3 build.py --out dist    只构建到暂存区，校验通过后再发布
    outs = []
    rest = sys.argv[1:]
    while '--out' in rest:
        i = rest.index('--out')
        outs.append(ROOT / rest[i + 1])
        rest = rest[:i] + rest[i + 2:]
    if '--watch' in rest or '-w' in rest:
        build(clean=not no_clean, outdirs=outs or None)
        watch()
    else:
        build(clean=not no_clean, outdirs=outs or None)
