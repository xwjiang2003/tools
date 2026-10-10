"""一次性脚本：把 docs/ 里引用的第三方 CDN 资源下载到本地 src/cdn/。

下载后由 build.py 输出到 docs/assets/cdn/，页面引用改写为同源路径，
解决 cdnjs.cloudflare.com 对 Baiduspider 返回 403 的问题。

用法：python fetch_cdn.py
"""
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
SRC = ROOT / 'src'
CDN = SRC / 'cdn'

CDN_ORIGIN = 'https://cdnjs.cloudflare.com/ajax/libs/'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


def find_node():
    """找一个能用的 node.exe —— JS 语法校验要用它。"""
    for cand in ('node', 'node.exe'):
        p = shutil.which(cand)
        if p:
            return p
    for base in (Path.home() / '.workbuddy' / 'binaries' / 'node' / 'versions'):
        if base.is_dir():
            found = sorted(base.glob('*/node.exe'), reverse=True)
            if found:
                return str(found[0])
    return ''


def verify(dest):
    """下载下来的文件必须完整，否则退回重试。

    踩过坑：cdnjs 在这条链路上会返回 HTTP 200 但内容被截断的响应
    （brace-fold.min.js 只给了 379 字节，node 解析直接报错）。
    这种半截文件一旦发布，浏览器加载时会是语法错误，整个页面的 JS
    跟着崩 —— 比外链 403 还糟。所以必须校验，不能只看状态码。
    """
    if dest.suffix == '.js':
        node = find_node()
        if node:
            r = subprocess.run([node, '--check', str(dest)],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                return 'JS 语法不完整'
    elif dest.suffix == '.css':
        css = dest.read_bytes().decode('utf-8', 'ignore')
        if css.count('{') != css.count('}'):
            return 'CSS 大括号不配对'
    return ''


def collect_urls():
    """提取去重后的 cdnjs 链接。

    刻意从 src/ 而不是 docs/ 里扫：docs/ 是构建产物，改造之后里面的链接已经被
    换成了 /assets/cdn/ —— 从它扫只能得到「一声唤 unexpected 的空结果」。
    src/index.html 才是这些标签真正的来源；隐私政策正文里提到的
    cdnjs.cloudflare.com 是裸域名（后面没有 /ajax/libs/），不会被下面这条正则匹配。
    """
    pat = re.compile(re.escape(CDN_ORIGIN) + r'[^\s"\'<>)]+')
    urls = set()
    for base in (SRC, DOCS):
        for fp in base.rglob('*.html'):
            urls.update(pat.findall(fp.read_text('utf-8', 'ignore')))
        if urls:
            return sorted(urls)
    return []


def fetch(args):
    url, dest = args
    last = ''
    for attempt in range(1, 5):
        req = urllib.request.Request(url, headers={
            'User-Agent': UA,
            'Accept-Encoding': 'identity',
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                declared = int(r.headers.get('Content-Length') or 0)
            if declared and len(data) != declared:
                last = f'长度不符 {len(data)}/{declared}'
                time.sleep(2 * attempt)
                continue
            if len(data) < 200:
                last = f'响应过小 {len(data)}B'
                time.sleep(1)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            bad = verify(dest)
            if bad:
                dest.unlink(missing_ok=True)
                last = bad
                time.sleep(2 * attempt)
                continue
            return dest, len(data), ''
        except Exception as e:
            last = str(e)[:70]
            time.sleep(2 * attempt)
    return dest, 0, last


def main():
    urls = collect_urls()
    if not urls:
        print('docs/ 里没有 cdnjs 引用，无需下载。')
        return 1
    if not find_node():
        print('⚠ 没找到 node，无法做 JS 语法校验；半截文件可能混入，请人工抽查。')
    print(f'共 {len(urls)} 个去重资源\n')
    jobs = []
    for u in urls:
        rel = u[len(CDN_ORIGIN):]
        jobs.append((u, CDN / Path(*rel.split('/'))))
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for dest, size, err in ex.map(fetch, jobs):
            rel = dest.relative_to(CDN).as_posix()
            if size:
                ok += 1
                print(f'  ✓ {rel:58s} {size / 1024:7.1f} KB')
            else:
                fail += 1
                print(f'  ✗ {rel:58s} {err}')
    print(f'\n成功 {ok} / 失败 {fail}')
    return 0 if fail == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
