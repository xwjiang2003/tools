#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把站点 URL 提交给搜索引擎。

为什么要用 IndexNow：Google 与百度的 sitemap ping 接口已于 2023 年前后下线
（实测 Google 无响应、Bing 返回 410、百度返回 404），IndexNow 是目前唯一
**不需要注册账号**就能提交 URL 的通道，提交结果由 Bing / Yandex / Seznam / Naver 共享。

Bing 的索引又直接供 ChatGPT Search 检索使用，所以这一步同时影响传统搜索与 AI 引用。

用法:
  python3 submit.py            # 提交 sitemap 中的全部 URL
  python3 submit.py --dry-run  # 只打印将要提交的内容

注意：IndexNow 会回抓 https://xwjiang2003.github.io/tools/<key>.txt 校验归属，
所以必须先把这个 key 文件部署上线，再运行本脚本。
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from content import SITE, TOOLS                       # noqa: E402
from site_config import INDEXNOW_KEY, KEY_LOCATION, ENDPOINTS, ROOT_SITE_URL  # noqa: E402

EN_DIR = 'en/'
PRIVACY = 'privacy.html'


def all_urls():
    """主机根页面 + tools 站点的 10 个中文页与 10 个英文页。"""
    urls = [ROOT_SITE_URL]
    for p in [t['path'] for t in TOOLS] + [PRIVACY]:
        urls.append(SITE['base_url'] + p)
        urls.append(SITE['base_url'] + EN_DIR + p)
    return urls


def main():
    host = ROOT_SITE_URL.split('//', 1)[1].rstrip('/').split('/')[0]
    key_location = KEY_LOCATION
    urls = all_urls()
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
