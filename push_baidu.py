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

🚫 2026-10-19 起已停用（用户要求）
--------------------------------
本脚本不再向百度发送任何 URL。做了两层保险：

  第一层：本文件顶部 BAIDU_PUSH_ENABLED = False —— 脚本直接退出，不建连接。
  第二层：src/site_config.py 的 BAIDU_PUSH_TOKEN 已置空 —— 即使有人越过本开关，
          也拿不到有效 token，脚本同样拒绝运行。

停用背景：对 nginx 日志的核对显示，近 30 天百度蜘蛛只抓了 39 个不重复 URL
（Googlebot 613 / bingbot 61），且从未抓取 sitemap.xml；而推送接口本身配额
极低（日均约 10 条）。投入产出比不成立，故停止主动推送。

若将来要恢复：把 BAIDU_PUSH_ENABLED 改回 True，并填回 site_config.py 的 token。
届时请注意：--dry-run 不受影响，仍可用于查看将要推送的清单。
"""

import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Windows 控制台默认 GBK，print 中文会抛 UnicodeEncodeError 或输出乱码，
# 重定向到文件时也一样。统一强制 UTF-8。
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ───────────────────────────────────────────────────────────────────────
# 推送总开关。False = 完全不联网，任何调用都一样安全退出。
# 2026-10-19 按用户要求置为 False。
# ───────────────────────────────────────────────────────────────────────
BAIDU_PUSH_ENABLED = False
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from content import SITE                                          # noqa: E402
from site_config import (BAIDU_PUSH_ENDPOINT, BAIDU_PUSH_SITE,    # noqa: E402
                         BAIDU_PUSH_TOKEN)

EN_DIR = 'en/'
MAX_URLS = 2000


def zh_urls(with_en=False):
    """中文页（默认）；--with-en 时把英文页也带上。

    URL 列表来自构建产物 docs/sitemap.xml 索引及其子文件，而不是在这里手算一份
    路径清单：速查表、博客文章这类新页面是后加的，手算清单每加一种就要回来同步
    一次，忘了就静默漏推。sitemap 与真实页面一一对应（check.py 校验条数），用它最稳。

    2026-10-22 起 sitemap.xml 是 sitemapindex，只列子 sitemap 文件名，
    页面 URL 在 sitemap-*.xml 里，必须先展开再取 <loc>。
    """
    docs = ROOT / 'docs'
    index = docs / 'sitemap.xml'
    if not index.exists():
        print(f'❌ 找不到 {index}，先运行 python3 build.py')
        return []
    texts = []
    for m in re.findall(r'<loc>(.*?)</loc>', index.read_text('utf-8')):
        name = m.rsplit('/', 1)[-1]
        cf = docs / name
        if not cf.exists():
            print(f'❌ 找不到 {cf}，先运行 python3 build.py')
            return []
        texts.append(cf.read_text('utf-8'))
    text = '\n'.join(texts)
    en_prefix = SITE['base_url'] + EN_DIR
    locs = re.findall(r'<loc>(.*?)</loc>', text)
    en_locs = re.findall(r'hreflang="en" href="(.*?)"', text)
    out, seen = [], set()
    for u in locs + (en_locs if with_en else []):
        if not with_en and u.startswith(en_prefix):
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main():
    # ── 停用拦截（2026-10-19）：任何调用路径都在此止步，不建网络连接 ──
    if not BAIDU_PUSH_ENABLED:
        print('🚫 百度主动推送已停用（2026-10-19）。本次未向百度发送任何请求。')
        print('   原因：百度侧配额极低且抓取深度长期停滞（近 30 天仅 39 个不重复 URL，'
              '从未抓 sitemap.xml），主动推送投入产出比不成立。')
        print('   恢复方法：push_baidu.py → BAIDU_PUSH_ENABLED = True '
              '且 src/site_config.py → BAIDU_PUSH_TOKEN 填回。')
        return 0

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

    # 注意：site 参数不能 urlencode。百度不认识 https%3A%2F%2F 这种编码形式，
    # 会直接返回 400 "site init fail"，看起来跟「站点没验证」一模一样，很容易误判。
    endpoint = f'{BAIDU_PUSH_ENDPOINT}?site={BAIDU_PUSH_SITE}&token={token}'
    data = ('\n'.join(urls) + '\n').encode('utf-8')
    req = urllib.request.Request(
        endpoint, data=data, method='POST',
        headers={'Content-Type': 'text/plain',
                 'User-Agent': 'Mozilla/5.0 devtools.help-push/1.0'})

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

    # 百度把多种失败都塞进 400，光看状态码分不清是没验证、token 错还是配额不够，
    # 所以按返回体里的 message 判断，并始终打印原始返回。
    msg = ''
    try:
        msg = json.loads(text).get('message', '')
    except ValueError:
        pass
    body = text.strip()[:200]

    hints = {
        'over quota': '当日配额不足（本次条数 > 剩余配额）。明天再推，或本次减少条数',
        'site init fail': '站点未在百度验证过，或 site 参数写法不对（不要 urlencode）',
        'token is invalid': 'token 无效',
        'empty content': '请求体为空',
    }
    why = hints.get(msg, f'HTTP {code}')
    print(f'❌ {why}')
    print(f'   原始返回：{body or "无响应"}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
