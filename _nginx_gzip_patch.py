# -*- coding: utf-8 -*-
"""把 nginx.conf 里整段被注释的 gzip 指令启用，并加 gzip_static。

背景：gzip on 一直开着，但 gzip_types 等在默认块里全被注释，实际只压缩
text/html。百度 Spider 中澳链路最差 ~10KB/s，858KB sitemap 裸传 90s，
必触其 60s socket 超时（百度抓取诊断实报 socket 读写错误）。
"""
import io

PATH = '/etc/nginx/nginx.conf'
BACKUP = '/etc/nginx/nginx.conf.bak-20261022'

NEW_TAIL = """\t# 2026-10-22：以下指令此前整段被注释，gzip 实际只压 text/html，
\t# XML/CSS/JS 全部裸传。百度 Spider 中澳链路最差 ~10KB/s，858KB 的
\t# sitemap 裸传需 90s，必触其 60s socket 超时（抓取诊断实报 socket
\t# 读写错误）。开启全类型压缩，并为构建产物里的 sitemap .gz 开直发。
\tgzip_vary on;
\tgzip_proxied any;
\tgzip_comp_level 6;
\tgzip_buffers 16 8k;
\tgzip_http_version 1.1;
\tgzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
\tgzip_static on;
"""

src = io.open(PATH, encoding='utf-8').read()
if 'gzip_static on;' in src:
    print('ALREADY_PATCHED')
    raise SystemExit(0)

lines = src.split('\n')
out = []
i = 0
patched = False
while i < len(lines):
    out.append(lines[i])
    if lines[i].strip() == 'gzip on;' and not patched:
        # 吞掉后续连续的 "# gzip_*" 注释行，换成真正启用的指令
        j = i + 1
        while j < len(lines) and lines[j].strip().startswith('# gzip_'):
            j += 1
        out.extend(NEW_TAIL.rstrip('\n').split('\n'))
        i = j
        patched = True
        continue
    i += 1

if not patched:
    raise SystemExit('ANCHOR_NOT_FOUND: no bare "gzip on;" line')

io.open(BACKUP, 'w', encoding='utf-8').write(src)
io.open(PATH, 'w', encoding='utf-8').write('\n'.join(out))
print('PATCHED, backup at ' + BACKUP)
