#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把站点 URL 主动推送给百度（普通收录 - API 推送）。

为什么单独有这个脚本：百度不参与 IndexNow，submit.py 覆盖的 Bing/Yandex/Seznam
跟百度是两套体系。而百度对新站点几乎不主动发现深层页，API 推送是唯一能主动
触发抓取的通道，也是这里最值得定期跑的一步。

接口约定（百度官方）：
  POST http://data.zz.baidu.com/urls?site=<站点>&token=<密钥>
  Content-Type: text/plain
  请求体：每行一个 URL，最多 2000 条
  返回：{"remain":剩余配额, "success":成功条数,
         "not_same_site":[], "not_valid":[]}

用法:
  python3 push_baidu.py                # 推送中文页（9 个，默认）
  python3 push_baidu.py --with-en      # 连英文页一起推
  python3 push_baidu.py --dry-run      # 只打印将要推送的内容
  python3 push_baidu.py --file urls.txt  # 推送文件里的 URL（每行一条）

配额说明：每日配额与站点等级相关，返回的 remain 就是当天剩余次数。
配额用尽返回 500 + "over quota"，不是故障，第二天自动恢复。
"""

import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from content import SITE, TOOLS                                   # noqa: E402
from site_config import (BAIDU_PUSH_ENDPOINT, BAIDU_PUSH_SITE,    # noqa: E402
                         BAIDU_PUSH_TOKEN)

EN_DIR = 'en/'
PRIVACY = 'privacy.html'
MAX_URLS = 2000


def zh_urls(with_en=False):
    """中文页（默认）；--with-en 时把英文页也带上。"""
    urls = []
    for p in [t['path'] for t in TOOLS] + [PRIVACY]:
        urls.append(SITE['base_url'] + p)
        if with_en:
            urls.append(SITE['base_url'] + EN_DIR + p)
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main():
    args = sys.argv[1:]
    token = os.environ.get('BAIDU_PUSH_TOKEN') or BAIDU_PUSH_TOKEN
    if not token:
        print('❌ 未配置百度推送 token：填 src/site_config.py 的 BAIDU_PUSH_TOKEN，'
              '或用环境变量 BAIDU_PUSH_TOKEN 传入。')
        return 1

    if '--file' in args:
        path = Path(args[args.index('--file') + 1])
        urls = [ln.strip() for ln in path.read_text('utf-8').splitlines() if ln.strip()]
    else:
        urls = zh_urls(with_en='--with-en' in args)

    urls = [u for u in urls if u.startswith('http')]
    if not urls:
        print('❌ 没有可推送的 URL')
        return 1
    if len(urls) > MAX_URLS:
        print(f'❌ 一次最多 {MAX_URLS} 条，当前 {len(urls)} 条')
        return 1

    if '--dry-run' in args:
        print(f'待推送 {len(urls)} 条：')
        for u in urls:
            print('  ' + u)
        return 0

    endpoint = (f'{BAIDU_PUSH_ENDPOINT}?'
                + urllib.parse.urlencode({'site': BAIDU_PUSH_SITE, 'token': token}))
    data = ('\n'.join(urls) + '\n').encode('utf-8')
    req = urllib.request.Request(endpoint, data=data, method='POST',
                                 headers={'Content-Type': 'text/plain'})

    print(f'→ 推送 {len(urls)} 条到百度（site={BAIDU_PUSH_SITE}）\n')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, text = r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        code, text = e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:                                        # noqa: BLE001
        code, text = 0, str(e)

    import json
    if code == 200:
        try:
            res = json.loads(text)
        except ValueError:
            print(f'⚠️  HTTP 200 但返回不是 JSON：{text[:200]}')
            return 1
        ok = res.get('success', 0)
        print(f'✅ 成功 {ok} 条，当日剩余配额 {res.get("remain", "?")}')
        if res.get('not_same_site'):
            print(f'⚠️  不属于本站：{res["not_same_site"]}')
        if res.get('not_valid'):
            print(f'⚠️  无效 URL：{res["not_valid"]}')
        for u in urls:
            print('   ' + u)
        return 0

    hints = {
        400: '站点未在百度验证过，或 token 错误',
        401: 'token 无效',
        404: '接口地址错误',
        500: '服务器错误（配额用尽也返回 500，看返回体是否含 over quota）',
    }
    print(f'❌ HTTP {code} — {hints.get(code, text.strip()[:200] or "无响应")}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
