# -*- coding: utf-8 -*-
"""给缺失 seealso 的存量工具页补「相关工具与阅读」区块（中英双语）。
每个条目在插入时重新计算偏移；已存在 seealso 的跳过。
"""
import io
import re
import sys

ZH = {
    'hotnews': [
        ('常用时间戳速查（今天 / 本周 / 本月）', 'timestamp-list/'),
        ('Unix 时间戳与日期互转', 'timestamp/'),
        ('Go 工具链命令速查表', 'go-cheatsheet/'),
        ('JSON 在线格式化与校验', './'),
    ],
    'diff': [
        ('文本大小写与风格转换', 'string/'),
        ('在线正则测试', 'regex/'),
        ('命名风格互转（camel/snake/kebab）', 'case/'),
        ('JSON 在线格式化与校验', './'),
    ],
    'regex': [
        ('文本大小写与风格转换', 'string/'),
        ('两段文本差异比对', 'diff/'),
        ('命名风格互转（camel/snake/kebab）', 'case/'),
        ('UUID 与随机数据生成', 'generator/'),
    ],
    'hash': [
        ('Base64 / URL / Unicode 编解码', 'encode/'),
        ('JWT 解码与签名校验', 'jwt/'),
        ('UUID 生成与解析', 'uuid/'),
        ('随机密码与数据生成', 'generator/'),
    ],
    'string': [
        ('命名风格互转（camel/snake/kebab）', 'case/'),
        ('两段文本差异比对', 'diff/'),
        ('在线正则测试', 'regex/'),
        ('JSON 在线格式化与校验', './'),
    ],
    'generator': [
        ('UUID 生成与解析', 'uuid/'),
        ('Snowflake ID 生成与解析', 'snowflake/'),
        ('MD5 / SHA / HMAC 哈希计算', 'hash/'),
        ('文本大小写与风格转换', 'string/'),
    ],
    'case': [
        ('文本大小写与风格转换', 'string/'),
        ('在线正则测试', 'regex/'),
        ('Go 代码在线格式化（gofmt）', 'gofmt-online/'),
        ('JSON 在线格式化与校验', './'),
    ],
    'jwt': [
        ('MD5 / SHA / HMAC 哈希计算', 'hash/'),
        ('Base64 / URL / Unicode 编解码', 'encode/'),
        ('Unix 时间戳与日期互转', 'timestamp/'),
        ('JSON 在线格式化与校验', './'),
    ],
    'yaml': [
        ('JSON 与 CSV / XML 双向转换', './'),
        ('JSON 与 TOML 双向转换', 'toml/'),
        ('CSV 查看与转换工具', 'csv/'),
        ('CSV 转 SQL INSERT 生成器', 'csv-to-sql-insert/'),
    ],
    'toml': [
        ('JSON 与 YAML 双向转换', 'yaml/'),
        ('JSON 与 CSV / XML 双向转换', './'),
        ('CSV 查看与转换工具', 'csv/'),
        ('代码格式化工具（HTML / CSS / JS / SQL）', 'formatter/'),
    ],
}
EN = {
    'hotnews': [
        ('Common timestamp lookup (today / this week / this month)', 'timestamp-list/'),
        ('Unix timestamp converter', 'timestamp/'),
        ('Go toolchain cheatsheet', 'go-cheatsheet/'),
        ('JSON formatter & validator', './'),
    ],
    'diff': [
        ('Text case & style converter', 'string/'),
        ('Regex tester', 'regex/'),
        ('Case converter (camel/snake/kebab)', 'case/'),
        ('JSON formatter & validator', './'),
    ],
    'regex': [
        ('Text case & style converter', 'string/'),
        ('Text diff tool', 'diff/'),
        ('Case converter (camel/snake/kebab)', 'case/'),
        ('UUID & random data generator', 'generator/'),
    ],
    'hash': [
        ('Base64 / URL / Unicode codec', 'encode/'),
        ('JWT decoder & verifier', 'jwt/'),
        ('UUID generator & parser', 'uuid/'),
        ('Password & random data generator', 'generator/'),
    ],
    'string': [
        ('Case converter (camel/snake/kebab)', 'case/'),
        ('Text diff tool', 'diff/'),
        ('Regex tester', 'regex/'),
        ('JSON formatter & validator', './'),
    ],
    'generator': [
        ('UUID generator & parser', 'uuid/'),
        ('Snowflake ID decoder & builder', 'snowflake/'),
        ('MD5 / SHA / HMAC hashing', 'hash/'),
        ('Text case & style converter', 'string/'),
    ],
    'case': [
        ('Text case & style converter', 'string/'),
        ('Regex tester', 'regex/'),
        ('Go formatter online (gofmt)', 'gofmt-online/'),
        ('JSON formatter & validator', './'),
    ],
    'jwt': [
        ('MD5 / SHA / HMAC hashing', 'hash/'),
        ('Base64 / URL / Unicode codec', 'encode/'),
        ('Unix timestamp converter', 'timestamp/'),
        ('JSON formatter & validator', './'),
    ],
    'yaml': [
        ('JSON ↔ CSV / XML converter', './'),
        ('JSON ↔ TOML converter', 'toml/'),
        ('CSV viewer & converter', 'csv/'),
        ('CSV to SQL INSERT generator', 'csv-to-sql-insert/'),
    ],
    'toml': [
        ('JSON ↔ YAML converter', 'yaml/'),
        ('JSON ↔ CSV / XML converter', './'),
        ('CSV viewer & converter', 'csv/'),
        ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
    ],
}


def block(links):
    out = ["        'seealso': ["]
    for text, href in links:
        out.append("            ('%s', '%s')," % (text, href))
    out.append("        ],")
    return '\n'.join(out) + '\n'


def find_list_entry(src, slug):
    for m in re.finditer(r"\n    \{\n", src):
        sm = re.match(r"'slug': '([\w-]+)'", src[m.end():].lstrip())
        if not sm or sm.group(1) != slug:
            continue
        start = m.start() + 1
        nxt = re.search(r"\n    \{\n|\n\]\n|\n\}\n", src[start:])
        end = start + (nxt.start() if nxt else len(src) - start)
        return start, end
    return None


def patch_list(path, table):
    for slug, links in table.items():
        src = io.open(path, encoding='utf-8').read()
        pos = find_list_entry(src, slug)
        if not pos:
            print('MISSING:', slug, path)
            sys.exit(1)
        a, b = pos
        seg = src[a:b]
        if "'seealso'" in seg:
            print('skip (has seealso):', slug)
            continue
        tail_m = re.search(r"\n    \},?\s*$", seg)
        if not tail_m:
            print('no tail:', slug)
            sys.exit(1)
        seg2 = seg[:tail_m.start()] + '\n' + block(links) + seg[tail_m.start():]
        src = src[:a] + seg2 + src[b:]
        io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
        print('patched', slug)


patch_list(r'D:\workspace\dev-tools\src\content.py', ZH)
patch_list(r'D:\workspace\dev-tools\src\content_en.py', EN)
