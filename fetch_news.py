#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取科技资讯，写入 data/news.json。

由 GitHub Actions 每天 08:00（北京时间）自动执行，也可以手动跑：

    python3 fetch_news.py                 # 抓全部源
    python3 fetch_news.py --only ithome   # 只抓某个源（逗号分隔可多个）
    python3 fetch_news.py --dry-run       # 只报告，不写文件

抓到的数据由 build.py 渲染成 /hotnews/ 静态页，所以本步骤不产出 HTML，
页面是构建期从 JSON 烘焙出来的 —— 这样爬虫不执行 JS 也能读到全部条目。

任何一个源失败都不会让页面变空：失败的源沿用 data/news.json 里的上一次结果，
并在页面上标注「上次成功抓取」的时间。所以这个脚本「部分成功」是可接受的。
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))

from news import (DATA_FILE, SOURCES, fetch_all, load_news,  # noqa: E402
                  save_news)


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    only = None
    if '--only' in args:
        only = set(args[args.index('--only') + 1].split(','))
        unknown = only - {s['id'] for s in SOURCES}
        if unknown:
            print(f'❌ 未知的源: {", ".join(sorted(unknown))}')
            print(f'   可用: {", ".join(s["id"] for s in SOURCES)}')
            return 1
    stale_all = '--no-keep' in args

    previous = {} if stale_all else load_news()
    prev_count = sum(len((v or {}).get('items') or [])
                     for v in (previous.get('sources') or {}).values())
    print(f'→ 抓取 {len(only) if only else len(SOURCES)} 个源'
          f'（上一次快照 {prev_count} 条）\n')

    report = []

    def on_result(src, entry, err):
        n = len(entry['items'])
        if entry.get('ok'):
            mark, note = '✅', ''
        elif entry.get('stale'):
            mark, note = '⚠️ ', '（沿用上次结果）'
        else:
            mark, note = '❌', ''
        report.append((src, n, mark, note, err, entry.get('fetch_secs', 0)))

    started = time.time()
    data = fetch_all(previous, only=only, on_result=on_result)
    elapsed = time.time() - started

    for row in sorted(report, key=lambda r: -r[5]):
        src, n, mark, note, err, secs = row
        tag = '中文' if src['lang'] == 'zh' else 'EN '
        line = (f'  {mark} {tag} {src["id"]:<11} {src["name"]:<14} '
                f'{n:>3} 条 {secs:>5.1f}s {note}')
        if err:
            line += f'  ← {err[:80]}'
        print(line)

    total = sum(len((v or {}).get('items') or []) for v in data['sources'].values())
    ok = sum(1 for v in data['sources'].values() if v.get('ok'))
    print(f'\n  共 {total} 条，{ok}/{len(data["sources"])} 个源抓取成功，'
          f'耗时 {elapsed:.1f}s')

    if dry:
        print('\n（--dry-run：未写入文件）')
        return 0

    if not ok:
        # 一条都没抓到说明是整体网络问题，不是某个源抽风。此时不写文件、返回非零，
        # 让定时任务在这一步就失败——GitHub 会发邮件通知，也不会把停更的页面当成新版本发布。
        print('\n❌ 所有源都抓取失败，未写入文件（保留上一次的快照）。'
              '请检查网络或各源可用性。')
        return 2

    save_news(data)
    print(f'\n✅ 已写入 {DATA_FILE.relative_to(ROOT)}')
    print('   下一步：python3 build.py  然后  python3 check.py docs')
    return 0


if __name__ == '__main__':
    sys.exit(main())
