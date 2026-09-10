#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 src/ 构建成可部署的静态站点。

产物（同时写入 dist/ 供本地预览、docs/ 供 GitHub Pages 发布）：
  index.html              JSON 工具（站点首页）
  <slug>/index.html       其余 8 个工具，各自独立 URL、独立标题与正文
  privacy.html            隐私政策
  sitemap.xml / robots.txt / .nojekyll

每个工具页只包含自己的工具 UI 与自己的正文，因此 9 个页面之间没有重复内容；
标题、描述、canonical、结构化数据都在构建时烘焙进 HTML，爬虫不执行 JS 也能读到。

用法:
  python3 build.py            # 构建一次
  python3 build.py --watch    # 监听并重建（需要: pip install watchdog）
"""

import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from content import SITE, TOOLS  # noqa: E402

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
DOCS = ROOT / 'docs'

JS_MODULES = [
    'core.js', 'json-tools.js', 'text-diff.js', 'encode.js', 'regex.js',
    'timestamp.js', 'hash.js', 'formatter.js',
    'string-tools.js', 'generator.js',
]

PRIVACY_PATH = 'privacy.html'


# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(s, quote=True)


def inline_assets(tpl, with_js=True):
    """把 CSS 与 JS 内联进 HTML，保持单文件分发。"""
    css = (SRC / 'css' / 'style.css').read_text('utf-8')
    tpl = tpl.replace(
        '<link rel="stylesheet" href="css/style.css">',
        '<style>\n' + css + '\n</style>'
    )
    if not with_js:           # 隐私政策页不需要编辑器与工具脚本
        return tpl
    for mod in JS_MODULES:
        js = (SRC / 'js' / mod).read_text('utf-8')
        tag = f'<script src="js/{mod}"></script>'
        if tag not in tpl:
            raise SystemExit(f'❌ 模板中找不到脚本标签: {tag}')
        tpl = tpl.replace(tag, '<script>\n// ' + mod + '\n' + js + '\n</script>')
    return tpl


def nav_html(active_slug, base):
    """顶部导航：真实 <a> 链接，让 9 个工具页互相可发现、可抓取。"""
    out = []
    for t in TOOLS:
        href = base + t['path'] if t['path'] else (base or './')
        cls = 'top-nav-item active' if t['slug'] == active_slug else 'top-nav-item'
        out.append(f'    <a class="{cls}" href="{href}">{esc(t["nav"])}</a>')
    return '\n'.join(out)


def footer_links_html(base):
    home = base or './'
    parts = [f'<a href="{home}">首页</a>']
    for t in TOOLS:
        if not t['path']:
            continue
        parts.append(f'<a href="{base}{t["path"]}">{esc(t["nav"])}</a>')
    return ''.join(parts)


def seo_section(t):
    """工具页正文：h1 + 简介 + 功能 + 步骤 + FAQ。构建期写死，不依赖 JS。"""
    p = ['<section class="seo-content">']
    p.append(f'  <h1>{esc(t["h1"])}</h1>')
    for para in t['intro']:
        p.append(f'  <p>{esc(para)}</p>')
    p.append('  <h2>主要功能</h2>')
    p.append('  <ul class="seo-features">')
    for name, desc in t['features']:
        p.append(f'    <li><b>{esc(name)}</b>：{esc(desc)}</li>')
    p.append('  </ul>')
    p.append('  <h2>使用步骤</h2>')
    p.append('  <ol class="seo-steps">')
    for step in t['steps']:
        p.append(f'    <li>{esc(step)}</li>')
    p.append('  </ol>')
    p.append('  <h2>常见问题</h2>')
    p.append('  <div class="faq">')
    for q, a in t['faq']:
        p.append(f'    <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>')
    p.append('  </div>')
    p.append('</section>')
    return '\n'.join(p)


def jsonld(t, url):
    """WebApplication + FAQPage 结构化数据，帮助搜索引擎展示富摘要。"""
    graph = [{
        '@type': 'WebApplication',
        'name': t['h1'],
        'url': url,
        'description': t['description'],
        'applicationCategory': 'DeveloperApplication',
        'operatingSystem': 'Any',
        'browserRequirements': '需要启用 JavaScript 的现代浏览器',
        'isAccessibleForFree': True,
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'CNY'},
    }]
    if t['faq']:
        graph.append({
            '@type': 'FAQPage',
            'mainEntity': [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                for q, a in t['faq']
            ],
        })
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False)
    return '<script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>'


def render_tool_page(tpl, t, tool_body):
    base = '' if not t['path'] else '../'
    home = base or './'
    url = SITE['base_url'] + t['path']
    page = tpl
    page = page.replace('{{PAGE}}', t['slug'])
    page = page.replace('{{TITLE}}', esc(t['title']))
    page = page.replace('{{DESCRIPTION}}', esc(t['description']))
    page = page.replace('{{KEYWORDS}}', esc(t['keywords']))
    page = page.replace('{{CANONICAL}}', url)
    page = page.replace('{{JSONLD}}', jsonld(t, url))
    page = page.replace('{{NAV}}', nav_html(t['slug'], base))
    page = page.replace('{{FOOTER_LINKS}}', footer_links_html(base))
    page = page.replace('{{TOOL}}', tool_body)
    page = page.replace('{{SEO}}', seo_section(t))
    page = page.replace('{{HOME}}', home)
    page = page.replace('{{BASE}}', base)
    return page


def render_privacy(tpl):
    url = SITE['base_url'] + PRIVACY_PATH
    page = tpl
    page = page.replace('{{CANONICAL}}', url)
    page = page.replace('{{NAV}}', nav_html('privacy', ''))
    page = page.replace('{{FOOTER_LINKS}}', footer_links_html(''))
    page = page.replace('{{HOME}}', './')
    page = page.replace('{{BASE}}', '')
    return page


def sitemap_xml():
    rows = [f'  <url><loc>{SITE["base_url"]}</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>']
    for t in TOOLS:
        if not t['path']:
            continue
        rows.append(
            f'  <url><loc>{SITE["base_url"] + t["path"]}</loc>'
            f'<changefreq>monthly</changefreq><priority>0.8</priority></url>'
        )
    rows.append(
        f'  <url><loc>{SITE["base_url"] + PRIVACY_PATH}</loc>'
        f'<changefreq>yearly</changefreq><priority>0.3</priority></url>'
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


def robots_txt():
    return (f'User-agent: *\nAllow: /\n\nSitemap: {SITE["base_url"]}sitemap.xml\n')


# ---------------------------------------------------------------- build

def build():
    tpl = inline_assets((SRC / 'index.html').read_text('utf-8'))
    privacy_tpl = inline_assets((SRC / 'privacy.html').read_text('utf-8'), with_js=False)

    pages = {}
    total_body = 0

    for t in TOOLS:
        body = (SRC / 'tools' / f'{t["slug"]}.html').read_text('utf-8').strip()
        total_body += len(body)
        pages[Path(t['path']) / 'index.html' if t['path'] else Path('index.html')] = \
            render_tool_page(tpl, t, body)
    pages[Path(PRIVACY_PATH)] = render_privacy(privacy_tpl)

    pages[Path('sitemap.xml')] = sitemap_xml()
    pages[Path('robots.txt')] = robots_txt()
    pages[Path('.nojekyll')] = ''

    for outdir in (DIST, DOCS):
        if outdir.exists():
            shutil.rmtree(outdir)
        for rel, content in pages.items():
            fp = outdir / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, 'utf-8')

    print(f'  ✓ 内联 CSS + {len(JS_MODULES)} 个 JS 模块')
    for rel in sorted(pages, key=str):
        size = len(pages[rel])
        print(f'  ✓ {str(rel):24s} {size / 1024:7.1f} KB')
    print(f'\n✅ {len(pages)} 个文件 → dist/ (本地预览) + docs/ (GitHub Pages 发布)')
    return True


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
                except Exception as ex:  # 构建失败不要让监听退出
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
