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

# 复用 build.py 的配置（语言集、中文源字典），避免两处各写一份导致漂移。
# build() 在 `if __name__ == '__main__'` 内，导入不会触发构建。
try:
    from build import LANGS, EN, MSGS, DEFAULT_LANG, LANG_DIRS  # noqa: F401
    from course import COURSE_LANGS                        # noqa: F401
    _HAS_BUILD = True
except Exception:                                   # noqa: BLE001
    _HAS_BUILD = False
    DEFAULT_LANG = 'zh'
    LANGS = ('zh', 'en')
    LANG_DIRS = {'zh': '', 'en': 'en/'}
    COURSE_LANGS = ('zh', 'en')
    EN, MSGS = {}, {'en': {}}

CJK = re.compile(r'[\u4e00-\u9fff]')
# 连续的汉字段作为一个整体比对白名单，逐字符比会把「中文」拆成「中」「文」
CJK_RUN = re.compile(r'[\u4e00-\u9fff]+')
# 注释整段跳过（源码注释本就是中文，不该被翻译）
COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->|(?<!:)//[^\n]*', re.S)
# 英文页里刻意保留的中文：语言切换按钮 + 字符串工具的 CJK 示例
CJK_WHITELIST = {'中文', '你好', '世界'}
# ja / ko 页天然含 CJK（汉字 / 谚文），不能做零 CJK 断言；改为查「中文源短语泄漏」。
CJK_SCRIPT_LANGS = {'ja', 'ko'}
# 中文源短语（2 字及以上）；单字易与日文/韩文同字误伤，排除。
ZH_SOURCE_KEYS = {k for k in EN if len(k) >= 2}
# 站点根目录下的第三方验证文件（root_files/ 里的那些）。它们是 .html 但不是本站页面，
# 没有反馈弹窗、也不进 sitemap，页面级检查必须跳过，否则每次都会被误报。
VERIFY_PREFIXES = ('baidu_verify_', 'google', 'yandex_', 'msvalidate', 'sogou_verify_',
                   '360verify', 'bing', 'indexnow')


def is_page_file(f, target):
    """排除站点根目录下的第三方验证文件。"""
    if f.parent != target:
        return True
    return not f.name.lower().startswith(VERIFY_PREFIXES)


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

    pages = [f for f in sorted(target.rglob('*.html')) if is_page_file(f, target)]
    errors = []

    # 1) 内联脚本语法
    # 单进程复用：当页面数很大（N 语言全量 ~755 页、上万段内联脚本）时，逐段 spawn
    # `node --check` 子进程会被沙箱 / 内存限额 SIGTERM。改用 check_js_inline.mjs
    # （单进程 vm.Script 校验）一次性跑完；找不到 mjs 时回退到逐段子进程（小站够用）。
    mjs = ROOT / 'check_js_inline.mjs'
    js_ok = True
    if mjs.exists():
        try:
            r = subprocess.run(['node', str(mjs), str(target)], capture_output=True, text=True)
            print(r.stdout.strip())
            if r.returncode != 0:
                for line in r.stderr.strip().split('\n'):
                    if line.strip():
                        errors.append(line.strip())
                js_ok = False
        except OSError:
            js_ok = False
            errors.append('node 不可用，无法校验内联脚本')
    else:
        try:
            has_node = subprocess.run(
                ['node', '--version'], capture_output=True).returncode == 0
        except OSError:
            has_node = False
        if not has_node:
            print('⚠️  找不到 node，跳过 JS 语法校验（强烈建议装上，这是本脚本的主要价值）')
            js_ok = None
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
    if js_ok is False:
        print('  ❌ 内联脚本语法校验失败（见上）')

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
            # 中英各自独立成条（满足 ahrefs「每个可索引页都要在 sitemap 里有独立 <loc>」），
            # 所以条数应等于「全部内容页面数」（含 /en/）。早期中英共用一条、英文页只当
            # xhtml:link alternate，导致 ahrefs 报「22 个可索引页不在 sitemap」。
            loc_set = {u.getElementsByTagName('loc')[0].firstChild.data for u in urls}
            # 逐页校验：每个页面的 canonical 都必须能在 sitemap 找到同名 <loc>。
            # 这正是 ahrefs「Indexable page not in sitemap」的对症检查。
            canon_re = re.compile(
                r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.I)
            missing = []
            for f in pages:
                m = canon_re.search(f.read_text('utf-8'))
                if not m:
                    missing.append(f'{f.relative_to(target)}(无canonical)')
                elif m.group(1) not in loc_set:
                    missing.append(f'{f.relative_to(target)}({m.group(1)})')
            ok = (n == len(pages)) and not missing
            print(f'  {"✅" if ok else "❌"} sitemap.xml 合法，含 {n} 条 url'
                  f'（内容页面 {len(pages)} 个，中英各自成条）')
            if n != len(pages):
                errors.append(f'sitemap url 数 {n} != 页面数 {len(pages)}')
            if missing:
                shown = '、'.join(missing[:5])
                more = f' …等 {len(missing)} 个' if len(missing) > 5 else ''
                errors.append(f'{len(missing)} 个页面 canonical 不在 sitemap: {shown}{more}')
            # Go 课程板块只发布 zh/en，hreflang 备用链接按 COURSE_LANGS 数校验；
            # 其余页面全站 8 语言 + x-default。
            def _expected_alts(loc):
                return len(COURSE_LANGS) + 1 if '/go-course/' in loc else len(LANGS) + 1

            no_alt = [u.getElementsByTagName('loc')[0].firstChild.data
                      for u in urls
                      if len(u.getElementsByTagName('xhtml:link')) != _expected_alts(
                          u.getElementsByTagName('loc')[0].firstChild.data)]
            if no_alt:
                shown = '、'.join(no_alt[:3])
                more = f' …等 {len(no_alt)} 个' if len(no_alt) > 3 else ''
                errors.append(f'{len(no_alt)} 条 url 的 hreflang 备用链接数不符预期 '
                              f'（课程页应 {len(COURSE_LANGS) + 1}，其余页应 {len(LANGS) + 1}）: {shown}{more}')
        except Exception as e:                                   # noqa: BLE001
            print(f'  ❌ sitemap.xml 解析失败: {e}')
            errors.append('sitemap.xml 非法')
    else:
        print('  ❌ 缺少 sitemap.xml')
        errors.append('缺少 sitemap.xml')

    # 5) 非中文页中文残留（泄漏）
    #   - en / 拉丁·西里尔语（es pt-BR fr de ru id）：零 CJK（仅白名单例外）。
    #     语言切换下拉框会列出各语言母语名（日本語 / 한국어 / 中文），属正常展示，
    #     扫描前先剔除该 <select>，避免把「日本語」误判为泄漏。
    #   - ja / ko：天然含 CJK，不能做零断言；改用「整段 CJK 串 == 中文源键」判定——
    #     仅当某连续 CJK 串恰好等于某个「译文与原文不同」的中文键时才算泄漏，
    #     既抓未翻译的中文，又避免日语同形汉字（如 北京時間 含 北京）误伤。
    leftovers_cjk = set()
    leaked_keys = {}
    strict_langs = [L for L in LANGS if L != DEFAULT_LANG and L not in CJK_SCRIPT_LANGS]
    cjk_langs = [L for L in LANGS if L in CJK_SCRIPT_LANGS]
    _SELECT = re.compile(r'<select class="lang-select"[^>]*>.*?</select>', re.S)

    for L in strict_langs:
        d = target / (LANG_DIRS.get(L, L + '/') or '.')
        if not d.exists():
            continue
        for f in sorted(d.rglob('*.html')):
            s = _SELECT.sub('', COMMENT.sub('', f.read_text('utf-8')))
            leftovers_cjk |= {run for run in CJK_RUN.findall(s) if run not in CJK_WHITELIST}
    for L in cjk_langs:
        table = MSGS.get(L, {})
        # 仅查「译文与原文不同」的键；译文==原文（同形汉字）跳过以免误伤。
        keys_to_check = {k for k in ZH_SOURCE_KEYS
                         if table.get(k, EN.get(k, k)) != k}
        if not keys_to_check:
            continue
        d = target / (LANG_DIRS.get(L, L + '/') or '.')
        if not d.exists():
            continue
        for f in sorted(d.rglob('*.html')):
            s = COMMENT.sub('', f.read_text('utf-8'))
            # 整段连续 CJK 串，逐个比对是否为未翻译的中文源键（整串匹配，非子串）
            for run in CJK_RUN.findall(s):
                if run in keys_to_check:
                    leaked_keys.setdefault(L, set()).add(run)

    cjk_msg = (f' — {sorted(leftovers_cjk)}' if leftovers_cjk else '')
    print(f'  {"✅" if not leftovers_cjk else "❌"} 非 CJK 语种页（{",".join(strict_langs)}）零中文'
          + cjk_msg)
    if leftovers_cjk:
        errors.append(f'非 CJK 语种页残留中文: {sorted(leftovers_cjk)}')

    if leaked_keys:
        parts = []
        for L in cjk_langs:
            if L in leaked_keys:
                parts.append(f'{L}: {sorted(leaked_keys[L])[:10]}')
        print(f'  ❌ CJK 语种页（{",".join(cjk_langs)}）查到中文源短语泄漏 — '
              + '；'.join(parts))
        errors.append('CJK 语种页中文源短语泄漏: ' + '；'.join(parts))
    else:
        print(f'  ✅ CJK 语种页（{",".join(cjk_langs)}）无中文源短语泄漏')

    print()
    if errors:
        print(f'❌ {len(errors)} 项检查未通过')
        for e in errors:
            print(f'   - {e}')
        return 1
    print('✅ 全部检查通过')
    print('   （这里只做静态检查；行为正确性请再跑 python3 test.py）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
