#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建产物冒烟测试。

起因：反馈弹窗的内联脚本里 `\\n` 被写成 `\n`，Python 把它变成了真正的换行，
导致 JS 字符串断行、整段脚本语法错误——按钮点了没反应，而页面其它功能完全正常，
肉眼和「文件是否 200」都看不出来。这个脚本专门用来兜住这一类问题。

检查项：
  1. 每段内联 <script> 用 node --check 做语法校验（需要 node）
  2. 不残留 {{占位符}}
  3. 每个页面都有且只有一个 <dialog id="feedbackModal">
  4. sitemap.xml 是合法 XML，且 URL 数与页面数一致
  5. 英文页面除白名单外无残留中文

用法:
  python3 check.py            # 检查 dist/
  python3 check.py docs       # 检查 docs/
"""

import re
import subprocess
import sys
import tempfile
import xml.dom.minidom
from pathlib import Path

ROOT = Path(__file__).parent
CJK = re.compile(r'[\u4e00-\u9fff]')
# 连续的汉字段作为一个整体比对白名单，逐字符比会把「中文」拆成「中」「文」
CJK_RUN = re.compile(r'[\u4e00-\u9fff]+')
# 注释整段跳过（源码注释本就是中文，不该被翻译）
COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->|(?<!:)//[^\n]*', re.S)
# 英文页里刻意保留的中文：语言切换按钮 + 字符串工具的 CJK 示例
CJK_WHITELIST = {'中文', '你好', '世界'}


# 只挑可执行的 JS：type 为空、text/javascript 或 module。
# JSON-LD（application/ld+json）是数据块，拿 node --check 去校验必然报错。
SCRIPT_TAG = re.compile(r'<script([^>]*)>(.*?)</script>', re.S)
JS_TYPES = ('', 'text/javascript', 'application/javascript', 'module')


def inline_scripts(html):
    out = []
    for attrs, body in SCRIPT_TAG.findall(html):
        if re.search(r'\bsrc=', attrs):
            continue
        m = re.search(r'\btype=["\']([^"\']*)["\']', attrs)
        if m and m.group(1).lower() not in JS_TYPES:
            continue
        if body.strip():
            out.append(body)
    return out


def main():
    target = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'dist')
    if not target.exists():
        print(f'❌ 目录不存在: {target}（先运行 python3 build.py）')
        return 1

    pages = sorted(target.rglob('*.html'))
    errors = []

    # 1) 内联脚本语法
    has_node = subprocess.run(['which', 'node'], capture_output=True).returncode == 0
    if not has_node:
        print('⚠️  找不到 node，跳过 JS 语法校验（强烈建议装上，这是本脚本的主要价值）')
    checked = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / 'chunk.js'
        for f in pages:
            for i, js in enumerate(inline_scripts(f.read_text('utf-8'))):
                checked += 1
                if not has_node:
                    continue
                tmp.write_text(js, 'utf-8')
                r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
                if r.returncode != 0:
                    detail = [l for l in r.stderr.split('\n') if l.strip()]
                    errors.append(f'{f.relative_to(target)} 第 {i + 1} 段内联脚本语法错误: '
                                  f'{detail[1] if len(detail) > 1 else r.stderr[:80]}')
    print(f'  {"✅" if not errors else "❌"} 内联脚本语法: 检查 {checked} 段'
          + ('' if has_node else '（已跳过）'))

    # 2) 占位符残留
    leftovers = [str(f.relative_to(target)) for f in pages
                 if re.search(r'\{\{[A-Z_]+\}\}', f.read_text('utf-8'))]
    print(f'  {"✅" if not leftovers else "❌"} 无残留占位符' + (f' — {leftovers}' if leftovers else ''))
    errors += [f'{p} 残留占位符' for p in leftovers]

    # 3) 反馈弹窗存在且唯一
    fb_bad = []
    for f in pages:
        n = f.read_text('utf-8').count('id="feedbackModal"')
        if n != 1:
            fb_bad.append(f'{f.relative_to(target)} 出现 {n} 次')
    print(f'  {"✅" if not fb_bad else "❌"} 反馈弹窗唯一性' + (f' — {fb_bad}' if fb_bad else ''))
    errors += fb_bad

    # 4) sitemap
    sm = target / 'sitemap.xml'
    if sm.exists():
        try:
            d = xml.dom.minidom.parse(str(sm))
            urls = d.getElementsByTagName('url')
            n = len(urls)
            # 中英两个版本共用一条 <url>，靠 xhtml:link 声明 hreflang，
            # 所以条数应等于「非 /en/ 页面数」。
            zh_pages = [f for f in pages
                        if not str(f.relative_to(target)).startswith('en/')]
            ok = n == len(zh_pages)
            print(f'  {"✅" if ok else "❌"} sitemap.xml 合法，含 {n} 条 url'
                  f'（中文页面 {len(zh_pages)} 个，中英共用条目）')
            if not ok:
                errors.append(f'sitemap url 数 {n} != 中文页面数 {len(zh_pages)}')
            no_alt = [u.getElementsByTagName('loc')[0].firstChild.data
                      for u in urls if len(u.getElementsByTagName('xhtml:link')) != 3]
            if no_alt:
                errors.append(f'{len(no_alt)} 条 url 缺少 hreflang 备用链接')
        except Exception as e:                                   # noqa: BLE001
            print(f'  ❌ sitemap.xml 解析失败: {e}')
            errors.append('sitemap.xml 非法')
    else:
        print('  ❌ 缺少 sitemap.xml')
        errors.append('缺少 sitemap.xml')

    # 5) 英文页中文残留
    leftovers_cjk = set()
    for f in sorted((target / 'en').rglob('*.html')):
        s = COMMENT.sub('', f.read_text('utf-8'))
        leftovers_cjk |= {run for run in CJK_RUN.findall(s) if run not in CJK_WHITELIST}
    print(f'  {"✅" if not leftovers_cjk else "❌"} 英文页无未翻译中文'
          + (f' — {sorted(leftovers_cjk)}' if leftovers_cjk else ''))
    if leftovers_cjk:
        errors.append(f'英文页残留中文: {sorted(leftovers_cjk)}')

    print()
    if errors:
        print(f'❌ {len(errors)} 项检查未通过')
        for e in errors:
            print(f'   - {e}')
        return 1
    print('✅ 全部检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
