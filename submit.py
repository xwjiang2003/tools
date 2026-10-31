#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把站点 URL 提交给搜索引擎。

为什么要用 IndexNow：Google 与百度的 sitemap ping 接口已于 2023 年前后下线
（实测 Google 无响应、Bing 返回 410、百度返回 404），IndexNow 是目前唯一
**不需要注册账号**就能提交 URL 的通道，提交结果由 Bing / Yandex / Seznam / Naver 共享。

Bing 的索引又直接供 ChatGPT Search 检索使用，所以这一步同时影响传统搜索与 AI 引用。

换域名后 host 变了，必须带着新 host 重新提交一次。

用法:
  python3 submit.py                  # 提交 sitemap 中的全部 URL（全量，慎用）
  python3 submit.py --changed DIR    # 只提交与 DIR（上一版发布目录）内容不同的 URL
  python3 submit.py --dry-run        # 只打印将要提交的内容

为什么默认全量要慎用（2026-10-31 实测）：Bing 后台 IndexNow 面板显示累计提交
113.3K 次，而站点只有约 948 条 URL —— 相当于每条 URL 被反复推了 120 次。
Bing 官方文档明确「只提交新增或更新的 URL」，高频全量重推会稀释该来源的信任度。
deploy.sh 因此改成发布后跑 `--changed docs.old`：只推本次真正变动的页面，
日常增量通常是个位数到几十条。

注意：IndexNow 会回抓 https://devtools.help/<key>.txt 校验归属，
所以必须先把这个 key 文件部署上线，再运行本脚本。
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from site_config import INDEXNOW_KEY, KEY_LOCATION, ENDPOINTS, ROOT_SITE_URL  # noqa: E402


def _sitemap_children_text():
    """拼接 sitemap 索引引用的全部子文件文本。

    2026-10-22 起 sitemap.xml 是 sitemapindex，只列子 sitemap 文件名；
    页面 URL 全在 sitemap-*.xml 里。只读索引会把子 sitemap 自己的 URL
    当成页面 URL 提交，必须展开。
    """
    docs = ROOT / 'docs'
    index = docs / 'sitemap.xml'
    if not index.exists():
        print(f'❌ 找不到 {index}，先运行 python3 build.py')
        return ''
    texts = []
    for m in re.findall(r'<loc>(.*?)</loc>', index.read_text('utf-8')):
        name = m.rsplit('/', 1)[-1]
        cf = docs / name
        if not cf.exists():
            print(f'❌ 找不到 {cf}，先运行 python3 build.py')
            return ''
        texts.append(cf.read_text('utf-8'))
    return '\n'.join(texts)


def all_urls():
    """站点全部 URL：读构建产物 docs/sitemap.xml 索引及其子文件。

    以前是从 TOOLS 手算一份路径列表，结果是每加一种新页面（速查表、博客文章）
    都要记得回来同步一次，忘了就漏提交——而漏提交的后果恰恰是最难发现的那种。
    sitemap 由 build.py 生成、且与真实页面一一对应（check.py 会校验条数），
    用它当唯一来源，新增页面自动进提交列表。
    """
    text = _sitemap_children_text()
    if not text:
        return []

    # sitemap 里中英是一对：<loc> 是中文页，英文页在 hreflang="en" 的备用链接里。
    # 只看 <loc> 会漏掉整套英文站，所以两个都要取。
    locs = re.findall(r'<loc>(.*?)</loc>', text)
    en_locs = re.findall(r'hreflang="en" href="(.*?)"', text)
    urls = []
    for zh, en in zip(locs, en_locs):
        urls += [zh, en]
    urls += locs[len(en_locs):]

    # 兜底：确保根 URL 一定在最前（迁移到自定义域名后 ROOT_SITE_URL == base_url，
    # 两者相同会去重；保留这段是为了换回子目录部署时首页不被漏掉）。
    seen, out = {ROOT_SITE_URL}, [ROOT_SITE_URL]
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _html_to_url(rel):
    """发布目录内的相对路径 → 站点 URL。

    规则与 build.py 的 out_path 完全对应：`index.html` 表示该目录，其余按文件名。
      index.html            → https://devtools.help/
      regex/index.html      → https://devtools.help/regex/
      en/regex/index.html   → https://devtools.help/en/regex/
      privacy.html          → https://devtools.help/privacy.html
    """
    rel = Path(rel)
    if rel.name == 'index.html':
        parent = rel.parent.as_posix()
        return ROOT_SITE_URL if parent in ('', '.') else f'{ROOT_SITE_URL}{parent}/'
    return f'{ROOT_SITE_URL}{rel.as_posix()}'


def changed_urls(prev_dir):
    """对比上一版发布目录，返回「新增或内容变化」的页面 URL（增量提交用）。

    为什么按内容哈希而不是按 mtime：deploy.sh 每次都是全新构建目录，
    mtime 全部相同，只有内容哈希能反映真实变化。

    只比 .html：sitemap / robots / 静态资源变了不需要单独推 URL
    （它们不是可被搜索的落地页），而页面自身的改动必然带动 HTML 变化。
    """
    prev_dir = Path(prev_dir)
    if not prev_dir.is_dir():
        print(f'⚠ 上一版目录不存在（{prev_dir}），回退为全量提交')
        return all_urls()

    import hashlib

    cur = ROOT / 'docs'
    urls = []
    for f in sorted(cur.rglob('*.html')):
        rel = f.relative_to(cur)
        old = prev_dir / rel
        if old.is_file():
            if hashlib.sha256(old.read_bytes()).digest() == hashlib.sha256(f.read_bytes()).digest():
                continue
        urls.append(_html_to_url(rel))
    print(f'   增量对比：当前 {len(list(cur.rglob("*.html")))} 个页面，'
          f'变动 {len(urls)} 个')
    return urls


def main():
    host = ROOT_SITE_URL.split('//', 1)[1].rstrip('/').split('/')[0]
    key_location = KEY_LOCATION
    prev = None
    for i, a in enumerate(sys.argv):
        if a == '--changed' and i + 1 < len(sys.argv):
            prev = sys.argv[i + 1]
        elif a.startswith('--changed='):
            prev = a.split('=', 1)[1]
    urls = changed_urls(prev) if prev else all_urls()
    if not urls:
        print('✓ 没有页面变动，跳过 IndexNow 提交')
        return 0
    payload = {
        'host': host,
        'key': INDEXNOW_KEY,
        'keyLocation': key_location,
        'urlList': urls,
    }

    if '--dry-run' in sys.argv:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # 先确认 key 文件已上线，否则提交必然 403
    try:
        with urllib.request.urlopen(key_location, timeout=20) as r:
            body = r.read().decode('utf-8').strip()
    except urllib.error.HTTPError as e:
        print(f'❌ key 文件还没上线 ({key_location} → HTTP {e.code})')
        print('   先把 docs/ 提交并推送，等 GitHub Pages 重建完成再运行本脚本。')
        return 1
    except Exception as e:                                     # noqa: BLE001
        print(f'❌ 无法访问 key 文件: {e}')
        return 1
    if body != INDEXNOW_KEY:
        print(f'❌ key 文件内容不匹配：期望 {INDEXNOW_KEY}，实际 {body!r}')
        return 1
    print(f'✓ key 文件已上线: {key_location}')

    req_headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = json.dumps(payload).encode('utf-8')
    print(f'→ 提交 {len(urls)} 个 URL\n')

    meanings = {
        200: '成功，key 已通过校验',
        202: '已接受，key 校验中',
        400: '请求格式错误',
        403: 'key 无效（文件不存在或内容不匹配）',
        422: 'URL 不属于该 host，或 key 与协议不匹配',
        429: '提交过于频繁',
    }
    results = []
    for name, ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=data, headers=req_headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                code, text = r.status, r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            code, text = e.code, e.read().decode('utf-8', 'replace')
        except Exception as e:                                 # noqa: BLE001
            code, text = 0, str(e)
        ok = code in (200, 202)
        results.append(ok)
        detail = meanings.get(code, text.strip()[:80] or '无响应')
        print(f'  {"✅" if ok else "❌"} HTTP {code:<4} {name:<12} {detail}')

    good = sum(results)
    print(f'\n{good}/{len(ENDPOINTS)} 个端点接受提交。'
          'IndexNow 约定：提交给任一参与方，结果会自动共享给其他参与方。')
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
