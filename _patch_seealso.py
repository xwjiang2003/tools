# -*- coding: utf-8 -*-
"""交叉链接补全（每步重新计算条目偏移，避免前次插入让后续偏移失效）：
1. formatter（已有 seealso）：头部插入 gofmt-online 链接；
2. csv / timestamp（无 seealso）：在条目末尾新建 seealso 块。
中英双语同步。
"""
import io
import re
import sys

ZH_SEEALSO = {
    'csv': """        'seealso': [
            ('CSV 转 SQL INSERT 生成器', 'csv-to-sql-insert/'),
            ('JSON 与 CSV / XML / YAML 双向转换（JSON 工具箱）', './'),
            ('JSON 与 YAML 双向转换', 'yaml/'),
            ('JSON 与 TOML 双向转换', 'toml/'),
        ],
""",
    'timestamp': """        'seealso': [
            ('Cron 表达式生成器', 'cron-generator/'),
            ('批量时间戳与日期互转', 'batch/'),
            ('常用时间戳速查（今天 / 本周 / 本月）', 'timestamp-list/'),
            ('世界时区与当前时间', 'timezones/'),
        ],
""",
}
EN_SEEALSO = {
    'csv': """        'seealso': [
            ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
            ('JSON ↔ CSV / XML / YAML converter (JSON toolbox)', './'),
            ('JSON ↔ YAML converter', 'yaml/'),
            ('JSON ↔ TOML converter', 'toml/'),
        ],
""",
    'timestamp': """        'seealso': [
            ('Cron expression generator', 'cron-generator/'),
            ('Batch timestamp converter', 'batch/'),
            ('Common timestamp lookup (today / this week / this month)', 'timestamp-list/'),
            ('World time zones & current time', 'timezones/'),
        ],
""",
}


def find_entry(src, slug):
    """每次重新查找，返回 (start, end)。"""
    for m in re.finditer(r"\n    \{\n", src):
        sm = re.match(r"'slug': '([\w-]+)'", src[m.end():].lstrip())
        if not sm or sm.group(1) != slug:
            continue
        start = m.start() + 1
        nxt = re.search(r"\n    \{\n|\n\]\n|\n\}\n", src[start:])
        end = start + (nxt.start() if nxt else len(src) - start)
        return start, end
    return None


def patch(path, table, formatter_link):
    for slug, block in list(table.items()) + [('formatter', None)]:
        src = io.open(path, encoding='utf-8').read()
        pos = find_entry(src, slug)
        if not pos:
            print('MISSING entry:', slug, 'in', path)
            sys.exit(1)
        a, b = pos
        seg = src[a:b]
        if slug == 'formatter':
            m = re.search(r"'seealso': \[\n", seg)
            if not m:
                print('formatter has no seealso?!')
                sys.exit(1)
            if 'gofmt-online/' in seg:
                print('formatter already linked')
                continue
            seg2 = seg[:m.end()] + formatter_link + seg[m.end():]
        else:
            if "'seealso'" in seg:
                print('already has seealso:', slug)
                continue
            tail_m = re.search(r"\n    \},?\s*$", seg)
            if not tail_m:
                print('no tail found for', slug)
                sys.exit(1)
            seg2 = seg[:tail_m.start()] + '\n' + block.rstrip('\n') + seg[tail_m.start():]
        src = src[:a] + seg2 + src[b:]
        io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
        print('patched', slug, 'in', path)


patch(r'D:\workspace\dev-tools\src\content.py', ZH_SEEALSO,
      "            ('Go 代码在线格式化（gofmt）', 'gofmt-online/'),\n")
patch(r'D:\workspace\dev-tools\src\content_en.py', EN_SEEALSO,
      "            ('Go formatter online (gofmt)', 'gofmt-online/'),\n")
