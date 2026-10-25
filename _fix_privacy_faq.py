# -*- coding: utf-8 -*-
"""幂等修复隐私 FAQ 补丁造成的内容文件损坏。

动作：
  1. 从 hotnews 的 seealso 列表中删除误插的 FAQ 元组（zh + en）；
  2. 给缺失隐私 FAQ 的页面在 faq 列表末尾统一插入一条（zh 10 页 / en 29 页）。
重复运行不会产生重复条目。
"""
import re
import sys

ZH_Q = '使用这个页面会收集我的数据吗？'
ZH_A = (
    '不会。页面内容要么在构建时就写进 HTML，要么全部在你的浏览器本地完成计算，'
    '输入内容不会发送到任何服务器；除了页脚访问量统计（百度统计与不蒜子，见隐私政策），'
    '本站不收集你的任何行为数据。'
)
EN_Q = 'Does this page collect my data?'
EN_A = (
    'No. The content is either baked into the HTML at build time or every calculation runs '
    'locally in your browser, so your input is never sent to any server. Apart from the footer '
    'traffic counters (Baidu Analytics and busuanzi, see the privacy policy), this site '
    'collects nothing about your visit.'
)

# 需要删除的垃圾元组（问题文本 -> 用于定位）
GARBAGE_ZH_Q = '浏览热榜会收集我的数据吗？'
GARBAGE_EN_Q = 'Does browsing the feed collect my data?'


def drop_garbage(src, q):
    """删除 seealso 列表体内以 q 为问题文本的元组。

    只在 seealso 段内操作（不碰 faq 段）；正则不吃前置换行，保证前一条
    目的行尾与 seealso 的 ], 缩进结构完整。覆盖单行答案与跨行拼接答案。
    """
    pat = re.compile(
        r"            \('" + re.escape(q) + r"',\n"
        r"(?:             [^\n]*\n)*?"          # 若干整行答案（行尾无 ),）
        r"             [^\n]*\),\n"              # 最后一个答案行，自带 ),
    )
    out = []
    pos = 0
    n = 0
    for m in re.finditer(r"'seealso': \[", src):
        seg_start = m.end()
        end = re.search(r"\n        \],", src[seg_start:])
        if not end:
            continue
        seg_end = seg_start + end.start() + 1  # 含段尾换行
        seg = src[seg_start:seg_end]
        new_seg, k = pat.subn('', seg)
        if k:
            out.append(src[pos:seg_start])
            out.append(new_seg)
            pos = seg_end
            n += k
    out.append(src[pos:])
    return ''.join(out), n


def split_entries(src, is_dict):
    if is_dict:
        parts = re.split(r"(\n    '[a-z0-9-]+': \{)", src)
    else:
        parts = re.split(r"(        'slug': '[a-z0-9-]+',)", src)
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i], parts[i + 1]))
    return out


def faq_has_privacy(body):
    m = re.search(r"'faq': \[", body)
    if not m:
        return True  # 无 faq 段的页面不动
    tail = body[m.end():]
    end = re.search(r"\n        \],", tail)
    seg = tail[:end.start()] if end else tail
    return ('隐私政策' in seg) or ('上传' in seg) or \
           ('privacy policy' in seg.lower()) or ('uploaded' in seg.lower())


def insert_faq(src, is_dict, q, a):
    """循环：每轮重新切分，给首个缺隐私 FAQ 的条目插入一条，直到没有缺口。"""
    hits = []
    while True:
        target = None
        for head, body in split_entries(src, is_dict):
            if not faq_has_privacy(body):
                target = (head, body)
                break
        if target is None:
            break
        head, body = target
        if is_dict:
            slug = re.match(r"\n    '([a-z0-9-]+)': \{", head).group(1)
        else:
            slug = re.match(r"        'slug': '([a-z0-9-]+)',", head).group(1)
        fm = re.search(r"'faq': \[", body)
        if not fm:
            print('  !! %s 无 faq 段，跳过' % slug)
            break
        tail = body[fm.end():]
        end = re.search(r"\n        \],", tail)
        if not end:
            print('  !! %s faq 段无结尾，跳过' % slug)
            break
        ins = "\n            ('%s',\n             '%s')," % (q, a)
        new_body = body[:fm.end()] + tail[:end.start()] + ins + tail[end.start():]
        src = src.replace(head + body, head + new_body, 1)
        hits.append(slug)
    return src, hits


def process(path, is_dict, garbage_q, q, a):
    src = open(path, encoding='utf-8').read()
    src, n = drop_garbage(src, garbage_q)
    print('%s: 删除 seealso 垃圾元组 %d 处' % (path, n))
    src, hits = insert_faq(src, is_dict, q, a)
    print('%s: 插入隐私 FAQ %d 页 -> %s' % (path, len(hits), hits))
    open(path, 'w', encoding='utf-8', newline='\n').write(src)


if __name__ == '__main__':
    process('src/content.py', False, GARBAGE_ZH_Q, ZH_Q, ZH_A)
    process('src/content_en.py', True, GARBAGE_EN_Q, EN_Q, EN_A)
    print('done')
