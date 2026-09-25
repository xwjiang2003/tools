# -*- coding: utf-8 -*-
"""科技热榜：新闻源定义 + 抓取 + 构建期渲染。

这个模块同时被 `fetch_news.py`（抓数据）和 `build.py`（渲染页面）导入，
所以源的清单只在这里维护一份。

设计要点
--------
* **只用标准库**。整个项目的构建至今零第三方依赖，这里保持一致：
  urllib 取数据、xml.etree 解 RSS/Atom、ThreadPoolExecutor 并发抓取。
* **抓不到就沿用上一次的数据**。任何一个源临时抽风时保留 `data/news.json`
  里的旧条目，页面因此永远不会变空——这是能安心交给定时任务的前提。
* **内容在构建期烘焙进 HTML**。不靠前端拉接口，爬虫不执行 JS 也能读到全部条目；
  页面上唯一的一段 JS 只负责切换来源标签，禁用 JS 时全部条目照常显示。
* **英文源过滤掉含中日韩文字的条目**。英文页里出现中文既不合语境，
  也会让 check.py 的「英文页无未翻译中文」检查失败。
"""

import html as html_mod
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'news.json'

# 带上联系方式是礼貌，也让对方在限流时能先联系而不是直接封。
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 '
      '(+https://devtools.help/)')

# 北京时间。中国不实行夏令时，用固定偏移即可——刻意不用 zoneinfo，
# 因为 Windows 不自带 IANA 时区库，会额外引入 tzdata 依赖。
CST = timezone(timedelta(hours=8))
# 展示时区：中文页用北京时间，英文页用 UTC（英文源的读者分布更分散，UTC 更中性）。
DISPLAY_TZ = {'zh': CST, 'en': timezone.utc}

# 每个源在页面上最多展示多少条
PER_SOURCE = {'zh': 15, 'en': 20}

# 摘要截断长度（字符）。
#
# 取的是「够判断要不要点进去」的量，不是「能代替原文」的量：几十字足以构成
# 著作权法意义上的适当引用，再多就开始有替代原文的观感了。English feeds 的
# 摘要本身更长、且英文信息密度低，所以上限给得宽一些。
#
# 渲染时会再按这个值兜一次截断（见 render_body），所以改完不需要等下一次抓取，
# 旧的 data/news.json 快照也会立即收缩到新长度。
SUMMARY_LIMIT = {'zh': 60, 'en': 100}

SOURCE_TIMEOUT = 30
MAX_WORKERS = 8

# 中日韩文字。英文源命中即丢弃。
CJK_RE = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]')

# ---------------------------------------------------------------- 新闻源

# 说明几件事：
#   kind='rss'  RSS 2.0；'atom' Atom；'hn' 走 Hacker News 官方 Firebase 接口
#   desc        分组标题后面的一句话标签
#   note        编辑点评：这家源适合看什么、不适合看什么
#
#   note 存在的理由不只是「好看」。纯标题列表容易被搜索引擎判成没有增量价值的
#   抓取内容；而「什么情况下值得读这家源」是抓不出、也复制不走的判断，正是把
#   聚合变成策展的那一点增量。所以这里每条都要写实际的取舍，不要写成客套介绍。
#   36氪已不再提供 RSS（/feed 返回 HTML），其接口需要签名，故不收录；
#   知乎热榜接口要登录态，同样不收录。
SOURCES = [
    # ---------------- 中文 ----------------
    {
        'id': 'ithome', 'lang': 'zh', 'kind': 'rss',
        'name': 'IT之家', 'desc': '综合科技资讯，更新最快',
        'note': '硬件首发和价格快讯基本都从这里出，更新频次是这一批里最高的；'
                '要闻与软文混排，看标题时得自己筛一遍。',
        'home': 'https://www.ithome.com/', 'url': 'https://www.ithome.com/rss/',
    },
    {
        'id': 'sspai', 'lang': 'zh', 'kind': 'rss',
        'name': '少数派', 'desc': '数字生活与效率工具',
        'note': '偏重实测与长期使用体验，出稿慢但值得细读；不适合追当日热点，'
                '更像工具选型时要翻的参考库。',
        'home': 'https://sspai.com/', 'url': 'https://sspai.com/feed',
    },
    {
        'id': 'infoq', 'lang': 'zh', 'kind': 'rss',
        'name': 'InfoQ 中文', 'desc': '软件开发与架构',
        'note': '聚焦架构实践与技术选型复盘，读者偏资深工程师；'
                '这里没有消费电子新闻，想找技术深度优先翻它。',
        'home': 'https://www.infoq.cn/', 'url': 'https://www.infoq.cn/feed',
    },
    {
        'id': 'oschina', 'lang': 'zh', 'kind': 'rss',
        'name': '开源中国', 'desc': '开源项目与社区动态',
        'note': '开源项目发布、版本更新与社区动态最全，适合盯版本号；'
                '原创分析较少，多为资讯转述。',
        'home': 'https://www.oschina.net/news', 'url': 'https://www.oschina.net/news/rss',
    },
    {
        'id': 'solidot', 'lang': 'zh', 'kind': 'rss',
        'name': 'Solidot', 'desc': '科技、安全与极客文化',
        'note': '偏极客口味，安全漏洞与科研类新闻占比高；'
                '译文体标题有时偏生硬，但信息密度不错。',
        'home': 'https://www.solidot.org/', 'url': 'https://www.solidot.org/index.rss',
    },
    {
        'id': 'ifanr', 'lang': 'zh', 'kind': 'rss',
        'name': '爱范儿', 'desc': '消费电子与新硬件',
        'note': '新硬件与 AI 应用的体验向报道，选题偏年轻化；'
                '深度评测不多，更适合知道最近出了什么。',
        'home': 'https://www.ifanr.com/', 'url': 'https://www.ifanr.com/feed',
    },
    {
        'id': 'tmtpost', 'lang': 'zh', 'kind': 'rss',
        'name': '钛媒体', 'desc': '科技商业与产业观察',
        'note': '偏产业与资本视角，融资、供应链、政策类的解释性文章较多；'
                '想找具体技术细节不适合看这里。',
        'home': 'https://www.tmtpost.com/', 'url': 'https://www.tmtpost.com/rss.xml',
    },
    {
        'id': 'leiphone', 'lang': 'zh', 'kind': 'rss',
        'name': '雷峰网', 'desc': 'AI 与前沿技术',
        'note': 'AI 落地与公司动态更新较勤，也常发产业观察；'
                '部分稿件带明显观点倾向，注意区分事实与评论。',
        'home': 'https://www.leiphone.com/', 'url': 'https://www.leiphone.com/feed',
    },
    # ---------------- English ----------------
    {
        'id': 'hackernews', 'lang': 'en', 'kind': 'hn',
        'name': 'Hacker News', 'desc': 'What developers are reading right now',
        'note': 'Ranked by community vote rather than editors, and the score after each '
                'title is the best proxy for what working developers actually care about today.',
        'home': 'https://news.ycombinator.com/', 'url': '',
    },
    {
        'id': 'techcrunch', 'lang': 'en', 'kind': 'rss',
        'name': 'TechCrunch', 'desc': 'Startups, funding and product news',
        'note': 'Strongest on funding rounds, acquisitions and launch coverage. '
                'Treat its forecasts as commentary, not data.',
        'home': 'https://techcrunch.com/', 'url': 'https://techcrunch.com/feed/',
    },
    {
        'id': 'theverge', 'lang': 'en', 'kind': 'atom',
        'name': 'The Verge', 'desc': 'Consumer tech and culture',
        'note': 'The widest range of the four, from phones to policy to internet culture, '
                'and usually the best writing. Reviews are opinionated, so check a second '
                'source before buying on one.',
        'home': 'https://www.theverge.com/', 'url': 'https://www.theverge.com/rss/index.xml',
    },
    {
        'id': 'arstechnica', 'lang': 'en', 'kind': 'rss',
        'name': 'Ars Technica', 'desc': 'Deep dives into technology',
        'note': 'The most technical of the four, with long explainers on chips, science and '
                'policy. Worth opening when you have time rather than for quick headlines.',
        'home': 'https://arstechnica.com/', 'url':
            'https://feeds.arstechnica.com/arstechnica/technology-lab',
    },
]

SOURCE_BY_ID = {s['id']: s for s in SOURCES}

# ---------------------------------------------------------------- 抓取工具

_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE = re.compile(r'\s+')
# URL 里只丢掉明确的跟踪参数。不能一刀切掉整个 query ——
# 很多站点的正文地址就是 /article?id=123 这种形态。
_DROP_PARAM_RE = re.compile(r'^(utm_\w+|spm|share_\w+|from_source|wxshare|ref_src)$', re.I)


def _get(url, timeout=SOURCE_TIMEOUT):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'application/rss+xml, application/atom+xml, application/xml, '
                  'text/xml, application/json, */*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean_url(url):
    """去掉跟踪参数与锚点，既让展示的链接干净，也用于去重。"""
    url = (url or '').strip()
    if not url:
        return ''
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if not parts.query:
        return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))
    keep = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not _DROP_PARAM_RE.match(k)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(keep), ''))


def clean_text(raw, limit=0):
    """把 RSS 里的 description 洗成可直接放进 <p> 的纯文本。"""
    if not raw:
        return ''
    s = html_mod.unescape(raw)
    s = _TAG_RE.sub(' ', s)          # 标签换成空格，避免 "<p>a</p><p>b" 粘成 "ab"
    s = html_mod.unescape(s)         # 有些源是双重转义，再解一次
    s = _WS_RE.sub(' ', s).strip()
    if limit and len(s) > limit:
        s = s[:limit].rstrip(' ,;，。') + '…'
    return s


def parse_ts(raw):
    """把 RSS 的 RFC 822 或 Atom 的 ISO 8601 时间统一成 epoch 秒。"""
    raw = (raw or '').strip()
    if not raw:
        return 0
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
    except Exception:                                          # noqa: BLE001
        pass
    try:
        dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:                                          # noqa: BLE001
        return 0


def _find_text(node, *names):
    for n in names:
        el = node.find(n)
        if el is not None and (el.text or '').strip():
            return el.text.strip()
    return ''


def parse_feed(raw):
    """解析 RSS 2.0 或 Atom，返回 [(title, url, date_raw, summary_raw), ...]。"""
    root = ET.fromstring(raw)
    rows = []
    if root.tag.split('}')[-1] == 'feed':                      # Atom
        ns = root.tag.split('}')[0].lstrip('{')
        for e in root.findall(f'{{{ns}}}entry'):
            url = ''
            for link in e.findall(f'{{{ns}}}link'):
                if link.get('rel', 'alternate') == 'alternate' and link.get('href'):
                    url = link.get('href')
                    break
            rows.append((
                _find_text(e, f'{{{ns}}}title'),
                url,
                _find_text(e, f'{{{ns}}}published', f'{{{ns}}}updated'),
                _find_text(e, f'{{{ns}}}summary', f'{{{ns}}}content'),
            ))
    else:                                                      # RSS 2.0
        channel = root.find('channel')
        if channel is None:
            channel = root
        for it in channel.findall('item'):
            rows.append((
                _find_text(it, 'title'),
                _find_text(it, 'link'),
                _find_text(it, 'pubDate', '{http://purl.org/dc/elements/1.1/}date'),
                _find_text(it, 'description',
                           '{http://purl.org/rss/1.0/modules/content/}encoded'),
            ))
    return rows


def _fetch_hn(src, limit):
    """Hacker News 官方接口：先取榜单 ID，再逐条取详情。

    HN 没有「热榜 RSS」，但 Firebase 接口免费无鉴权，且带 score，
    正好能当作热度显示——这是别的源给不了的信息。
    """
    ids = json.loads(_get('https://hacker-news.firebaseio.com/v0/topstories.json'))
    ids = ids[:min(limit * 2, 48)]

    def one(i):
        try:
            return json.loads(_get(
                f'https://hacker-news.firebaseio.com/v0/item/{i}.json', timeout=15))
        except Exception:                                      # noqa: BLE001
            return None

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        details = list(pool.map(one, ids))

    items = []
    for it in details:
        if not it or it.get('type') != 'story' or it.get('deleted') or it.get('dead'):
            continue
        title = it.get('title') or ''
        if CJK_RE.search(title):        # 英文页不该出现中日韩条目
            continue
        items.append({
            'title': title,
            'url': clean_url(it.get('url')
                             or f'https://news.ycombinator.com/item?id={it.get("id")}'),
            'ts': int(it.get('time') or 0),
            'summary': '',
            'heat': it.get('score') or 0,
        })
        if len(items) >= limit:
            break
    return items


def fetch_source(src, limit):
    """抓单个源。返回值：正常时是条目列表，出错时抛异常由调用方兜住。"""
    if src['kind'] == 'hn':
        return _fetch_hn(src, limit)

    rows = parse_feed(_get(src['url']))
    slimit = SUMMARY_LIMIT[src['lang']]
    items, seen = [], set()
    for title, url, date_raw, summary_raw in rows:
        title = clean_text(title, 0)
        url = clean_url(url)
        if not title or not url.startswith('http'):
            continue
        if src['lang'] == 'en' and CJK_RE.search(title):
            continue
        key = url.rstrip('/').lower()
        if key in seen:
            continue
        seen.add(key)
        items.append({
            'title': title,
            'url': url,
            'ts': parse_ts(date_raw),
            'summary': clean_text(summary_raw, slimit),
        })
        if len(items) >= limit:
            break
    return items


# ---------------------------------------------------------------- 聚合

def fetch_all(previous=None, only=None, on_result=None):
    """并发抓全部源，返回新的数据集。

    previous 用于兜底：某个源这一轮没抓到（或抓到 0 条）时，沿用它的旧条目，
    并在该源上标 `stale`，页面会显示「上次成功抓取」的时间。
    """
    prev_sources = (previous or {}).get('sources') or {}
    now = int(time.time())
    targets = [s for s in SOURCES if not only or s['id'] in only]

    def job(src):
        t0 = time.time()
        try:
            return src, fetch_source(src, PER_SOURCE[src['lang']]), None, time.time() - t0
        except Exception as e:                                 # noqa: BLE001
            return src, [], f'{type(e).__name__}: {e}', time.time() - t0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(job, targets))

    sources = {}
    for src, items, err, secs in results:
        old = prev_sources.get(src['id']) or {}
        elapsed = {'fetch_secs': round(secs, 1)}
        if items:
            entry = {'ok': True, 'fetched_at': now, 'items': items, **elapsed}
        elif old.get('items'):
            entry = {'ok': False, 'fetched_at': old.get('fetched_at', 0),
                     'items': old['items'], 'stale': True, 'error': err, **elapsed}
        else:
            entry = {'ok': False, 'fetched_at': 0, 'items': [], 'error': err, **elapsed}
        if err:
            entry['error'] = err
        sources[src['id']] = entry
        if on_result:
            on_result(src, entry, err)
    # 本轮没参与抓取的源（--only）原样保留
    for sid, entry in prev_sources.items():
        sources.setdefault(sid, entry)

    # 本轮一条都没抓到（比如 runner 网络整体不通）时，不要把 generated_at 推进到现在
    # ——否则页面会顶着「更新于今天 08:00」显示昨天的内容。保持上一次的时间，头部说的就是实话。
    any_ok = any(e.get('ok') for e in sources.values())
    generated = now if any_ok else ((previous or {}).get('generated_at') or 0)

    return {'generated_at': generated,
            'sources': {sid: sources[sid] for sid in SOURCE_BY_ID if sid in sources}}


def load_news(path=None):
    """读 data/news.json；文件不存在时返回一个空壳，让 build 仍能跑通。"""
    p = Path(path) if path else DATA_FILE
    try:
        return json.loads(p.read_text('utf-8'))
    except Exception:                                          # noqa: BLE001
        return {'generated_at': 0, 'sources': {}}


def save_news(data, path=None):
    p = Path(path) if path else DATA_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', 'utf-8')


def sources_for(lang):
    return [s for s in SOURCES if s['lang'] == lang]


def visible_items(data, src):
    """取某个源要展示的条目，取前 PER_SOURCE 条。

    刻意**保持源给出的顺序**，不按时间重排：各源的列表本身就是编辑/算法排过的榜
    —— Hacker News 的 topstories 尤其明显，按时间重排会把它的排名彻底打乱。
    """
    entry = (data.get('sources') or {}).get(src['id']) or {}
    return list(entry.get('items') or [])[:PER_SOURCE[src['lang']]]


# ---------------------------------------------------------------- 渲染

TEXT = {
    'zh': {
        'updated': '更新于',
        'lead': '聚合 8 家中文科技媒体与 4 家英文科技媒体的最新条目，只做索引与直达，不转载正文',
        'total': '本期共 ',
        'unit': ' 条',
        'all': '全部',
        'visits': '前往',
        'home': '首页',
        'empty': '暂无数据，请稍后再来。',
        'stale': '该源本轮抓取失败，显示的是上次成功抓取的内容',
        'partial': '个来源本轮抓取失败，已沿用上次成功的内容',
        'latest': '最新',
        'lpar': '（',
        'rpar': '）',
    },
    'en': {
        'updated': 'Updated',
        'lead': 'Four English tech publications, newest first — headlines link straight to the '
                'publisher and nothing is republished here',
        'total': 'Total ',
        'unit': ' items',
        'all': 'All',
        'visits': 'Open',
        'home': 'homepage',
        'empty': 'No data yet — please check back later.',
        'stale': 'Fetch failed this round; showing the last successful snapshot',
        'partial': 'sources failed this round; their last successful snapshot is shown',
        'latest': 'latest',
        'lpar': ' (',
        'rpar': ')',
    },
}

_LANG_ATTR = {'zh': 'zh-CN', 'en': 'en'}


def _trunc(s, limit):
    """渲染期的二次截断。

    fetch 已经截过一次，但 data/news.json 里可能存着上一次以更宽上限抓到的摘要；
    兜这一刀能确保收紧 SUMMARY_LIMIT 之后不必等到明天的定时任务才生效。
    """
    if not s or not limit or len(s) <= limit:
        return s
    return s[:limit].rstrip(' ,;，。·') + '…'


def _esc(s):
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def format_ts(ts, lang):
    """条目时间一律用 MM-dd HH:mm。

    不再对「今天/昨天」做特殊显示（HH:mm、昨天 HH:mm）：同一屏里混着三种格式
    反而要靠读者自己换算，统一成 MM-dd HH:mm 一眼就能比大小。
    """
    if not ts:
        return ''
    dt = datetime.fromtimestamp(ts, DISPLAY_TZ[lang])
    return dt.strftime('%m-%d %H:%M')


def _iso(ts, lang):
    if not ts:
        return ''
    return datetime.fromtimestamp(ts, DISPLAY_TZ[lang]).isoformat()


def render_body(lang, data):
    """渲染页面主体：来源标签 + 分组列表。

    没有 JS 时全部条目都可见（每组默认 data-on="1"，只有 JS 会把非当前组置 0），
    所以爬虫和禁用 JS 的读者都能拿到完整内容。
    """
    t = TEXT[lang]
    groups = []
    for src in sources_for(lang):
        items = visible_items(data, src)
        entry = (data.get('sources') or {}).get(src['id']) or {}
        if items:
            groups.append((src, items, entry))

    out = ['<div class="news" id="news">']
    if not groups:
        out.append(f'  <p class="news-empty">{_esc(t["empty"])}</p>')
        out.append('</div>')
        return '\n'.join(out)

    total = sum(len(items) for _, items, _ in groups)
    generated = data.get('generated_at') or 0
    updated = (datetime.fromtimestamp(generated, DISPLAY_TZ[lang]).strftime('%Y-%m-%d %H:%M')
               if generated else '—')

    # ---- 顶部：更新时间 + 来源标签 ----
    out.append('  <div class="news-head">')
    out.append('    <div class="news-head-row">')
    out.append(f'      <p class="news-lead">{_esc(t["lead"])}</p>')
    out.append(f'      <p class="news-updated"><b>{_esc(t["updated"])} { _esc(updated) }</b>'
               f'<span class="news-dot">·</span>'
               f'{_esc(t["total"])}{total}{_esc(t["unit"])}</p>')
    out.append('    </div>')
    out.append('    <div class="news-tabs" role="tablist">')
    out.append(f'      <button type="button" class="news-tab active" data-news-src="all" '
               f'role="tab" aria-selected="true">{_esc(t["all"])}</button>')
    for src, items, _ in groups:
        out.append(f'      <button type="button" class="news-tab" data-news-src="{src["id"]}" '
                   f'role="tab" aria-selected="false">{_esc(src["name"])}'
                   f'<span class="news-tab-n">{len(items)}</span></button>')
    out.append('    </div>')
    stale_n = sum(1 for _, _, entry in groups if entry.get('stale'))
    if stale_n:
        out.append(f'    <p class="news-warn">{stale_n} {_esc(t["partial"])}</p>')
    out.append('  </div>')

    # ---- 分组列表 ----
    out.append('  <div class="news-groups">')
    for src, items, entry in groups:
        out.append(f'    <section class="news-group" data-src="{src["id"]}" data-on="1">')
        out.append('      <h3 class="news-group-head">')
        out.append(f'        <a class="news-group-name" href="{_esc(src["home"])}" '
                   f'target="_blank" rel="noopener nofollow">{_esc(src["name"])}</a>')
        out.append(f'        <span class="news-group-desc">{_esc(src["desc"])}</span>')
        out.append('      </h3>')
        if src.get('note'):
            out.append(f'      <p class="news-group-note">{_esc(src["note"])}</p>')
        if entry.get('stale'):
            out.append(f'      <p class="news-warn">{_esc(t["stale"])}{t["lpar"]}'
                       f'{_esc(format_ts(entry.get("fetched_at"), lang))}{t["rpar"]}</p>')
        out.append('      <ol class="news-list">')
        for i, it in enumerate(items, 1):
            title = _esc(it['title'])
            url = _esc(it['url'])
            row = ['        <li class="news-item">',
                   f'          <span class="news-rank">{i}</span>',
                   '          <div class="news-main">',
                   f'            <a class="news-title" href="{url}" target="_blank" '
                   f'rel="noopener nofollow">{title}'
                   f'<span class="news-ext" aria-hidden="true">↗</span></a>']
            if it.get('summary'):
                row.append(f'            <p class="news-summary">'
                           f'{_esc(_trunc(it["summary"], SUMMARY_LIMIT[lang]))}</p>')
            meta = []
            if it.get('ts'):
                meta.append(f'<time datetime="{_esc(_iso(it["ts"], lang))}">'
                            f'{_esc(format_ts(it["ts"], lang))}</time>')
            if it.get('heat'):
                meta.append(f'<span class="news-heat">🔥 {int(it["heat"])}</span>')
            if meta:
                row.append('            <p class="news-meta">' + ''.join(meta) + '</p>')
            row.append('          </div>')
            row.append('        </li>')
            out.append('\n'.join(row))
        out.append('      </ol>')
        out.append('    </section>')
    out.append('  </div>')

    # 唯一的交互脚本：来源标签过滤。禁用 JS 时所有分组本来就是展开的。
    out.append('''  <script>
// 来源标签过滤：只切换 data-on，不做重排。没有这段脚本时全部分组都显示，
// 因为服务端给每组写的就是 data-on="1"。
(function () {
  var tabs = document.querySelectorAll('[data-news-src]');
  var groups = document.querySelectorAll('.news-group');
  if (!tabs.length || !groups.length) return;
  function pick(id) {
    Array.prototype.forEach.call(tabs, function (tab) {
      var on = tab.getAttribute('data-news-src') === id;
      tab.classList.toggle('active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    Array.prototype.forEach.call(groups, function (g) {
      g.setAttribute('data-on',
        (id === 'all' || g.getAttribute('data-src') === id) ? '1' : '0');
    });
  }
  Array.prototype.forEach.call(tabs, function (tab) {
    tab.addEventListener('click', function () {
      pick(tab.getAttribute('data-news-src'));
    });
  });
})();
</script>''')
    out.append('</div>')
    return '\n'.join(out)


def jsonld_items(lang, data, limit=20):
    """给 JSON-LD 的 ItemList 用：跨源按时间取最新的若干条。"""
    rows = []
    for src in sources_for(lang):
        for it in visible_items(data, src):
            if it.get('ts'):
                rows.append((it['ts'], it['title'], it['url']))
    rows.sort(reverse=True)
    return rows[:limit]
