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
    sitemap.xml（带 hreflang 备用链接） / robots.txt / .nojekyll

两种语言各自拥有独立的 URL、标题、描述、canonical、hreflang 与正文，
英文页面在构建时就把界面文案整体替换掉，因此不依赖运行时 JS 翻译。

用法:
  python3 build.py            # 构建一次
  python3 build.py --watch    # 监听并重建（需要: pip install watchdog）
"""

import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from content import SITE, TOOLS, PRIVACY_BODY_ZH          # noqa: E402
from content_en import TOOLS_EN, PRIVACY_BODY_EN          # noqa: E402
from i18n import EN, JS_PATCHES, HTML_PATCHES             # noqa: E402
from site_config import INDEXNOW_KEY, CUSTOM_DOMAIN       # noqa: E402

SRC = ROOT / 'src'
DIST = ROOT / 'dist'
DOCS = ROOT / 'docs'

# 需要原样发布到站点根目录的第三方文件（搜索引擎的域名验证文件等）。
#
# 不能直接放进 docs/：下面 build() 会 rmtree(outdir)，手放进去的文件必然被删
# （CNAME 早就因为这个原因改成由构建生成了）。所以统一放在仓库根的 root_files/，
# 由构建复制到 dist/ 与 docs/ 根目录。以后新增验证文件只要丢进这个目录，
# 不用再改代码；换域名/换平台要删除时，也只要从这里删掉即可。
ROOT_FILES = ROOT / 'root_files'

JS_MODULES = [
    'core.js', 'json-tools.js', 'text-diff.js', 'encode.js', 'regex.js',
    'timestamp.js', 'hash.js', 'formatter.js',
    'string-tools.js', 'generator.js',
]

EN_DIR = 'en/'
PRIVACY_FILE = 'privacy.html'
REPO_URL = 'https://github.com/xwjiang2003/tools'
BAIDU_ANALYTICS_ID = 'd052ce9e23ea8d3ec643b0d49eb5b96a'
ISSUES_URL = REPO_URL + '/issues'
DISCUSSIONS_URL = REPO_URL + '/discussions'
FEEDBACK_EMAIL = '278975598@qq.com'
LANGS = ('zh', 'en')
HTML_LANG = {'zh': 'zh-CN', 'en': 'en'}


# ---------------------------------------------------------------- 本地化

# 按长度降序拼成一条正则：正则的备选分支从左到右尝试，因此长词优先命中，
# 不会出现「格式化完成」先被「格式化」切开的情况。
_PATTERN = re.compile('|'.join(re.escape(k) for k in sorted(EN, key=len, reverse=True)))
_LOOKUP = EN

# 注释整段跳过：源码注释保持中文原样，比被逐词替换成半中半英更好读。
# `(?<!:)//` 用来避开 https:// 里的双斜杠。
_COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->|(?<!:)//[^\n]*', re.S)


def _sub_terms(text):
    for old, new in JS_PATCHES:      # 语序/数组等需要整行改写的地方
        text = text.replace(old, new)
    for old, new in HTML_PATCHES:
        text = text.replace(old, new)
    return _PATTERN.sub(lambda m: _LOOKUP[m.group(0)], text)


def localize(text):
    """把整页（HTML + 内联 JS）里的中文界面文案替换成英文，注释保持原样。"""
    out, last = [], 0
    for m in _COMMENT.finditer(text):
        out.append(_sub_terms(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_sub_terms(text[last:]))
    return ''.join(out)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- 路径计算

def out_path(lang, path):
    """path 为工具相对路径（'' 或 'diff/'）或带扩展名的页面（privacy.html）。"""
    prefix = EN_DIR if lang == 'en' else ''
    if path.endswith('.html'):          # 独立文件，不再套目录
        return Path(prefix + path)
    return Path(prefix + path + 'index.html')


def rel_root(lang, path):
    """从输出文件所在目录回到站点根目录的相对前缀。"""
    depth = (0 if path == '' else 1) + (1 if lang == 'en' else 0)
    return '../' * depth


def lang_prefix(lang, root):
    """当前语言内部的链接前缀。"""
    return root + (EN_DIR if lang == 'en' else '')


def other_lang_url(lang, root, path):
    """同一页在另一种语言下的相对 URL。"""
    if lang == 'en':
        return (root + path) or './'
    return root + EN_DIR + path


def canonical_url(lang, path):
    return SITE['base_url'] + (EN_DIR if lang == 'en' else '') + path


# ---------------------------------------------------------------- 页面片段

def hreflang_html(path):
    zh = SITE['base_url'] + path
    en = SITE['base_url'] + EN_DIR + path
    return ('<link rel="alternate" hreflang="zh-CN" href="' + zh + '">\n'
            '<link rel="alternate" hreflang="en" href="' + en + '">\n'
            '<link rel="alternate" hreflang="x-default" href="' + zh + '">')


def lang_switch_html(lang, other_url):
    zh_href = './' if lang == 'zh' else other_url
    en_href = './' if lang == 'en' else other_url
    zh_cls = 'lang-link active' if lang == 'zh' else 'lang-link'
    en_cls = 'lang-link active' if lang == 'en' else 'lang-link'
    return (
        '<div class="lang-switch">'
        f'<a class="{zh_cls}" href="{zh_href}" data-lang-set="zh">中文</a>'
        f'<a class="{en_cls}" href="{en_href}" data-lang-set="en">English</a>'
        '</div>\n'
        '<script>\n'
        '// 记住手动选择：下次访问不再自动跳转\n'
        'document.addEventListener("click", function (e) {\n'
        '  var a = e.target.closest && e.target.closest("[data-lang-set]");\n'
        '  if (!a) return;\n'
        '  try { localStorage.setItem("devtools-lang", a.getAttribute("data-lang-set")); } catch (err) {}\n'
        '}, true);\n'
        '</script>'
    )


def analytics_html():
    """百度统计代码，按官方要求放在全部页面的 </head> 之前。

    刻意保持与百度后台给出的片段一字不差（含 document.getElementsByTagName 的插入方式），
    因为「代码安装检查」是按页面 HTML 里是否出现 hm.js?<id> 来判断的，
    改动片段有被误判为未安装的风险。
    """
    return '''<!-- 百度统计（Baidu Analytics）：按官方要求置于 head 结束标签之前，全站所有页面 -->
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?__BAIDU_ID__";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>'''.replace('__BAIDU_ID__', BAIDU_ANALYTICS_ID)


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


def autodetect_html(lang, other_url):
    """首次访问按浏览器语言跳到对应语言版本；已手动选择过或疑似爬虫则不跳。"""
    targets = json.dumps({'zh': './' if lang == 'zh' else other_url,
                          'en': './' if lang == 'en' else other_url})
    return f'''<script>
// 语言自动选择：仅在用户没手动选过、且不是搜索引擎爬虫时执行。
// 爬虫跳过是为了不影响两个语言版本的收录（配合 hreflang 使用）。
(function () {{
  try {{
    var KEY = 'devtools-lang';
    var q = location.search.match(/[?&]lang=(zh|en)(?:&|$)/);
    if (q) {{ try {{ localStorage.setItem(KEY, q[1]); }} catch (e) {{}} return; }}
    if (localStorage.getItem(KEY)) return;
    if (/(bot|crawler|spider|crawling|slurp|bingpreview)/i.test(navigator.userAgent)) return;
    var langs = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || ''];
    var preferZh = false;
    for (var i = 0; i < langs.length; i++) {{
      if (/^zh\\b/i.test(langs[i])) {{ preferZh = true; break; }}
    }}
    var want = preferZh ? 'zh' : 'en';
    var target = {targets}[want];
    if (target && want !== '{lang}') location.replace(target);
  }} catch (e) {{}}
}})();
</script>'''


def nav_html(active_slug, base, labels):
    out = []
    for t in TOOLS:
        href = base + t['path'] if t['path'] else (base or './')
        cls = 'top-nav-item active' if t['slug'] == active_slug else 'top-nav-item'
        out.append(f'    <a class="{cls}" href="{href}">{esc(labels[t["slug"]])}</a>')
    return '\n'.join(out)


def footer_links_html(base, labels):
    home = base or './'
    parts = [f'<a href="{home}">{esc(labels["_home"])}</a>']
    for t in TOOLS:
        if not t['path']:
            continue
        parts.append(f'<a href="{base}{t["path"]}">{esc(labels[t["slug"]])}</a>')
    return ''.join(parts)


def seo_section(c):
    """工具页正文：h1 + 简介 + 功能 + 步骤 + FAQ，构建期写死，不依赖 JS。"""
    sep = '：' if c.get('_lang') == 'zh' else ' — '
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
    p.append('</section>')
    return '\n'.join(p)


def jsonld(c, url, lang):
    graph = [{
        '@type': 'WebApplication',
        'name': c['h1'],
        'url': url,
        'description': c['description'],
        'applicationCategory': 'DeveloperApplication',
        'operatingSystem': 'Any',
        'browserRequirements': '需要启用 JavaScript 的现代浏览器' if lang == 'zh'
                               else 'Requires a modern browser with JavaScript enabled',
        'inLanguage': HTML_LANG[lang],
        'isAccessibleForFree': True,
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'CNY'},
    }]
    if c['faq']:
        graph.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                for q, a in c['faq']
            ],
        })
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False)
    return '<script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>'


# ---------------------------------------------------------------- 资源内联

def inline_assets(tpl, with_js=True):
    css = (SRC / 'css' / 'style.css').read_text('utf-8')
    tpl = tpl.replace('<link rel="stylesheet" href="css/style.css">',
                      '<style>\n' + css + '\n</style>')
    if not with_js:
        return tpl
    for mod in JS_MODULES:
        js = (SRC / 'js' / mod).read_text('utf-8')
        tag = f'<script src="js/{mod}"></script>'
        if tag not in tpl:
            raise SystemExit(f'❌ 模板中找不到脚本标签: {tag}')
        tpl = tpl.replace(tag, '<script>\n// ' + mod + '\n' + js + '\n</script>')
    return tpl


# ---------------------------------------------------------------- 组装

HEADINGS = {
    'zh': {'_features_heading': '主要功能', '_steps_heading': '使用步骤',
           '_faq_heading': '常见问题', '_home': '首页'},
    'en': {'_features_heading': 'Features', '_steps_heading': 'How to use',
           '_faq_heading': 'FAQ', '_home': 'Home'},
}

# 英文界面文案直接复用 i18n 字典，保证与内联 JS 的翻译一致
NAV_LABELS = {
    'zh': {t['slug']: t['nav'] for t in TOOLS},
    'en': {t['slug']: TOOLS_EN[t['slug']]['nav'] for t in TOOLS},
}
for _lang in LANGS:
    NAV_LABELS[_lang].update(HEADINGS[_lang])


def content_for(tool, lang):
    c = dict(tool) if lang == 'zh' else dict(TOOLS_EN[tool['slug']])
    c['_lang'] = lang
    c.update(HEADINGS[lang])
    return c


def apply_common(page, lang, slug, path, title, description, keywords, body, seo, ld, base, home):
    other = other_lang_url(lang, rel_root(lang, path), path)
    page = page.replace('{{PAGE}}', slug)
    page = page.replace('{{LANG}}', HTML_LANG[lang])
    page = page.replace('{{TITLE}}', esc(title))
    page = page.replace('{{DESCRIPTION}}', esc(description))
    page = page.replace('{{KEYWORDS}}', esc(keywords))
    page = page.replace('{{CANONICAL}}', canonical_url(lang, path))
    page = page.replace('{{HREFLANG}}', hreflang_html(path))
    page = page.replace('{{AUTODETECT}}', autodetect_html(lang, other))
    page = page.replace('{{LANGSWITCH}}', lang_switch_html(lang, other))
    page = page.replace('{{ANALYTICS}}', analytics_html())
    page = page.replace('{{FEEDBACK_BTN}}', feedback_btn_html())
    page = page.replace('{{FEEDBACK_MODAL}}', feedback_modal_html())
    page = page.replace('{{NAV}}', nav_html(None if path == PRIVACY_FILE else _slug_of(path),
                                            base, NAV_LABELS[lang]))
    page = page.replace('{{FOOTER_LINKS}}', footer_links_html(base, NAV_LABELS[lang]))
    page = page.replace('{{JSONLD}}', ld)
    page = page.replace('{{TOOL}}', body)
    page = page.replace('{{SEO}}', seo)
    page = page.replace('{{PRIVACY_BODY}}', seo)
    page = page.replace('{{HOME}}', home)
    page = page.replace('{{BASE}}', base)
    return page


_SLUG_BY_PATH = {t['path']: t['slug'] for t in TOOLS}


def _slug_of(path):
    return _SLUG_BY_PATH.get(path)


def build():
    tpl = inline_assets((SRC / 'index.html').read_text('utf-8'))
    privacy_tpl = inline_assets((SRC / 'privacy.html').read_text('utf-8'), with_js=False)

    pages = {}
    for lang in LANGS:
        for t in TOOLS:
            c = content_for(t, lang)
            body = (SRC / 'tools' / f'{t["slug"]}.html').read_text('utf-8').strip()
            base = lang_prefix(lang, rel_root(lang, t['path']))
            home = base or './'
            page = apply_common(tpl, lang, t['slug'], t['path'], c['title'], c['description'],
                                c['keywords'], body, seo_section(c),
                                jsonld(c, canonical_url(lang, t['path']), lang),
                                base, home)
            if lang == 'en':
                page = localize(page)
            pages[out_path(lang, t['path'])] = page

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
                            '', body, '', base, home)
        if lang == 'en':
            page = localize(page)
        pages[out_path(lang, PRIVACY_FILE)] = page

    pages[Path('sitemap.xml')] = sitemap_xml()
    pages[Path('robots.txt')] = robots_txt()
    pages[Path('llms.txt')] = llms_txt()
    pages[Path('.nojekyll')] = ''
    # GitHub Pages 自定义域名。必须由构建生成：下面会 rmtree(docs)，
    # 手动放进去的 CNAME 每次构建都会被删掉，域名随之失效。
    pages[Path('CNAME')] = CUSTOM_DOMAIN + '\n'
    # IndexNow 归属校验文件。域名根 == 本站发布目录根，所以放这里。
    pages[Path(f'{INDEXNOW_KEY}.txt')] = INDEXNOW_KEY

    # 站点根目录的附加文件（搜索引擎验证文件等），见上方 ROOT_FILES 的说明
    if ROOT_FILES.is_dir():
        for extra in sorted(ROOT_FILES.iterdir()):
            if extra.is_file():
                pages[Path(extra.name)] = extra.read_text('utf-8')

    for outdir in (DIST, DOCS):
        if outdir.exists():
            shutil.rmtree(outdir)
        for rel, content in pages.items():
            fp = outdir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, 'utf-8')

    print(f'  ✓ 内联 CSS + {len(JS_MODULES)} 个 JS 模块 × 2 语言')
    for rel in sorted(pages, key=str):
        print(f'  ✓ {str(rel):28s} {len(pages[rel]) / 1024:7.1f} KB')
    print(f'\n✅ {len(pages)} 个文件 → dist/ (本地预览) + docs/ (GitHub Pages 发布)')
    return True


def sitemap_xml():
    paths = [t['path'] for t in TOOLS] + [PRIVACY_FILE]
    rows = []
    for p in paths:
        zh = SITE['base_url'] + p
        en = SITE['base_url'] + EN_DIR + p
        pri = '1.0' if p == '' else ('0.3' if p == PRIVACY_FILE else '0.8')
        rows.append(
            '  <url>\n'
            f'    <loc>{zh}</loc>\n'
            f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{zh}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{zh}"/>\n'
            f'    <changefreq>monthly</changefreq><priority>{pri}</priority>\n'
            '  </url>'
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


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
    lines = [
        '# DevTools — 在线开发工具集',
        '#',
        '# ⚠️ 爬虫只会读取主机根目录的 /robots.txt，本文件（/tools/robots.txt）不影响抓取，',
        f'#    权威版本在 {SITE["base_url"].rsplit("/", 2)[0]}/robots.txt，两份放行清单保持同步。',
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
    out = [
        f'# {SITE["name"]} — 在线开发工具集 / Online Developer Tools',
        '',
        '> 免注册、免安装的纯浏览器端开发者工具集合，覆盖 JSON、文本比对、编解码、正则、',
        '> 时间戳、哈希、代码格式化、字符串处理与生成器共 9 个工具。所有解析与计算都在用户',
        '> 浏览器内完成，输入内容不会上传到任何服务器。中英双语，免费无广告。',
        '',
        'Key facts:',
        '- 9 tools, each on its own URL; every page runs entirely client-side '
        '(no upload, no signup, no ads).',
        '- Bilingual: Chinese at the root, English under /en/. Same tools, independent copy.',
        '- Verification hooks: /sitemap.xml (with hreflang alternates), /robots.txt, '
        'JSON-LD on every tool page.',
        '',
        '## Tools / 工具',
        '',
    ]
    for t in TOOLS:
        en = TOOLS_EN[t['slug']]
        zh_url = SITE['base_url'] + t['path']
        en_url = SITE['base_url'] + EN_DIR + t['path']
        out.append(f'- [{t["h1"]}]({zh_url}): {t["description"]}')
        out.append(f'  - English: [{en["h1"]}]({en_url}) — {en["description"]}')
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
    if '--watch' in sys.argv or '-w' in sys.argv:
        build()
        watch()
    else:
        build()
