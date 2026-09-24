# -*- coding: utf-8 -*-
"""博客（/blog/）：文章数据（中文）+ 构建期渲染。

设计取向与全站一致：文章正文以 HTML 片段的形式写在本文件里，构建期烘焙进静态页，
不依赖任何 JS 注入，爬虫不执行 JS 也能读到全文。

每篇文章是一个 dict：
  slug        URL 段（blog/<slug>/），同时是英文版 content 的关联键
  date        首次发布日期（YYYY-MM-DD）
  updated     最后校订日期（驱动 sitemap 的 lastmod 与页面「更新于」）
  tags        标签（索引页卡片与文章页头部展示）
  title       SEO 标题（<title>）
  description SEO 描述
  keywords    SEO 关键词
  h1          文章页大标题
  summary     索引页卡片摘要（也用于 JSON-LD）
  body        正文 HTML 片段（h2/h3/p/pre/ul/blockquote/table）
  related     相关阅读 [(文字, 相对站点根的路径)]，构建时加语言前缀

英文版在 blog_en.py，按 slug 对应；两版都必须存在（build 会强制校验），
保证 hreflang 与 sitemap 永远指向真实存在的页面。
"""

# 博客索引页（相对站点根）
BLOG_INDEX = 'blog/'


def article_path(slug):
    return f'{BLOG_INDEX}{slug}/'


ARTICLES = [
    {
        'slug': 'gofmt-vs-goimports',
        'date': '2026-09-24',
        'updated': '2026-09-24',
        'tags': ['Go', '工具链', 'CI'],
        'title': 'gofmt 和 goimports 的区别：为什么 CI 里的格式化检查会失败 | DevTools 博客',
        'description': (
            'gofmt 只管代码排版，goimports 在此基础上自动增删 import 并分组排序，'
            '两者对同一份代码的输出可以不一样。本文讲清三件事：两个工具各自做什么、'
            '结果在什么情况下会不同、CI 里应该怎么配格式化检查（含 GitHub Actions 示例）。'
        ),
        'keywords': (
            'gofmt goimports区别,gofmt 用法,goimports 安装,goimports -local,'
            'go 代码格式化 ci,gofmt -l,gofumpt,go 格式化检查失败'
        ),
        'h1': 'gofmt 和 goimports 的区别：为什么 CI 里的格式化检查会失败',
        'summary': (
            'gofmt 管排版、goimports 管排版 + import，对同一份代码两者的输出可以不同。'
            '讲清差异产生的三种场景，以及 CI 里统一的检查姿势。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：gofmt 只调整代码排版（缩进、对齐、空格），从不触碰 import；
  goimports = gofmt + 自动增删 import + import 分组排序。本地编辑器用 goimports、
  CI 里却用 gofmt -l 检查（或反过来），是「本地好好的、CI 挂了」的最常见原因。统一用 goimports。</p>
</blockquote>

<h2>一、gofmt 做什么</h2>
<p>gofmt 是 Go 官方的代码排版工具，随工具链一起安装，职责只有一个：<b>让代码的空白布局符合统一规范</b>。
它处理缩进（tab）、对齐、运算符两侧的空格、括号位置这类问题，不会改动任何代码语义。</p>
<p>常用旗标：</p>
<pre><code>gofmt -l .        # 只列出「不符合规范」的文件，不改文件（CI 检查就用它）
gofmt -d main.go  # 显示会改成什么样的 diff，不写回
gofmt -w .        # 直接改写文件
gofmt -s -w .     # 在排版之外再做代码简化（如 x[a:len(x)] → x[a:]）
gofmt -r 'a[i], a[j] = a[j], a[i] -> a[i], a[j] = a[j], a[i]' -w .  # 按规则重写（极少用）</code></pre>
<p>需要记住的边界：<b>gofmt 不会增删 import，也不会调整 import 的分组顺序</b>。
一个引入了却没使用的包，gofmt 会原样保留（编译器会报错，但那不是 gofmt 的职责）。</p>

<h2>二、goimports 多做的两件事</h2>
<p>goimports 不属于 Go 标准工具链，需要单独安装：</p>
<pre><code>go install golang.org/x/tools/cmd/goimports@latest</code></pre>
<p>它先做 gofmt 的全部工作，然后多做两件事：</p>
<ol>
  <li><b>自动补全和删除 import</b>：代码里用了 <code>fmt.Println</code> 但没 import "fmt"，
      它会补上；import 了没用的包，它会删掉。</li>
  <li><b>import 分组排序</b>：按「标准库一组、第三方一组」分组，组内按路径字母序排列。</li>
</ol>
<p>看个典型例子。下面这份代码 import 了没用的 <code>os</code>，分组也是乱的：</p>
<pre><code>package main

import (
	"github.com/gin-gonic/gin"
	"fmt"
	"os"
)

func main() {
	fmt.Println(gin.Version)
}</code></pre>
<p><b>gofmt 的输出</b>：只把 <code>"fmt"</code> 按字母序排进同一组，<code>os</code> 原样保留：</p>
<pre><code>import (
	"fmt"
	"github.com/gin-gonic/gin"
	"os"
)</code></pre>
<p><b>goimports 的输出</b>：删掉未使用的 <code>os</code>，并把标准库和第三方分成两组：</p>
<pre><code>import (
	"fmt"

	"github.com/gin-gonic/gin"
)</code></pre>
<p>同一份输入，两个工具的输出不一样——这就是「格式化检查为什么有时过有时不过」的根源。</p>

<h2>三、结果会不同的三种典型场景</h2>
<h3>1. 存在未使用的 import</h3>
<p>gofmt 保留，goimports 删除。本地编辑器配的是 goimports（保存时自动删），
提交后 CI 用 gofmt -l 检查能通过；但反过来——本地用 gofmt、CI 用 goimports -l——就会挂。</p>
<h3>2. 缺少 import</h3>
<p>goimports 会尝试自动补全。存在多个候选包时（比如 <code>rand</code> 可能是
<code>math/rand</code> 也可能是 <code>math/rand/v2</code>），它会按索引猜一个，
猜错了就是编译错误。<b>所以 goimports 的补全结果必须过一眼，别盲目提交。</b></p>
<h3>3. 你自己公司的包被归错组</h3>
<p>goimports 默认把「非标准库」全归进第三方组，于是 <code>git.company.com/team/utils</code>
会和 github 依赖混在一起。用 <code>-local</code> 参数把自家前缀单独成组：</p>
<pre><code>goimports -local git.company.com -w .</code></pre>
<p>编辑器里也要同步配置（VS Code 的 <code>go.formatTool</code> 与
<code>gopls</code> 的 <code>local</code> 设置），否则编辑器格式化结果和命令行不一致。</p>

<h2>四、CI 里的正确姿势</h2>
<p>原则只有一条：<b>本地编辑器、命令行、CI 三处用同一个工具、同一组参数</b>。
推荐统一为 goimports（它是 gofmt 的超集，检查更严）：</p>
<pre><code># 有输出即代表有文件不符合规范，退出码置 1
files=$(goimports -local git.company.com -l .)
if [ -n "$files" ]; then
  echo "以下文件未通过 goimports 检查："
  echo "$files"
  exit 1
fi</code></pre>
<p>GitHub Actions 完整示例：</p>
<pre><code>name: check
on: [push, pull_request]
jobs:
  fmt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod   # 与仓库 go.mod 保持一致，避免版本差
      - run: go install golang.org/x/tools/cmd/goimports@latest
      - run: |
          files=$(goimports -l .)
          test -z "$files" || { echo "need goimports: $files"; exit 1; }
      - run: go vet ./...
      - run: go test ./...</code></pre>
<div class="post-note">
<p><b>版本坑</b>：不同 Go 版本自带的 gofmt 在极少数边缘语法上的排版会有差异，
goimports 不同版本的分组行为也调整过。CI 用 <code>go-version-file: go.mod</code>
锁定与仓库一致的 Go 版本，可以消掉「我本地格式化过了为什么 CI 还挂」的整类问题。</p>
</div>

<h2>五、想要更严格：gofumpt 与 staticcheck</h2>
<ul>
  <li><b>gofumpt</b>：gofmt 的更严格超集（如强制多行 import 块的写法）。
      注意全仓库只能选一个——混用 gofmt 和 gofumpt 会产生反复横跳的 diff。</li>
  <li><b>staticcheck</b>：不是格式化工具，是深度静态检查，CI 里常与格式化检查并列挂：</li>
</ul>
<pre><code>go install mvdan.cc/gofumpt@latest
gofumpt -l .
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...</code></pre>

<h2>六、小结</h2>
<table>
  <tr><th></th><th>gofmt</th><th>goimports</th></tr>
  <tr><td>安装</td><td>随 Go 工具链自带</td><td>go install golang.org/x/tools/cmd/goimports@latest</td></tr>
  <tr><td>代码排版</td><td>✔</td><td>✔（完全一致）</td></tr>
  <tr><td>增删 import</td><td>✘</td><td>✔</td></tr>
  <tr><td>import 分组排序</td><td>✘</td><td>✔（-local 指定自家前缀）</td></tr>
  <tr><td>CI 检查命令</td><td>gofmt -l .</td><td>goimports -l .（推荐）</td></tr>
</table>
<p>更多命令的用法与坑点（gofmt 的 -s/-r、goimports 的索引机制）见
<a href="/go-cheatsheet/">Go 工具链命令速查表</a>的「格式化与代码工具」一节。</p>
''',
        'related': [
            ('Go 工具链命令速查表', 'go-cheatsheet/'),
            ('代码格式化工具（HTML / CSS / JS / SQL）', 'formatter/'),
        ],
    },
]

# ---------------------------------------------------------------- 渲染

TEXT = {
    'zh': {
        'index_title': '博客 - Go 工具链与开发实战文章 | DevTools',
        'index_desc': ('Go 工具链实战文章：错误排查、版本迁移、CI 实践，'
                       '每篇都经过真实验证。当前连载 Go 专题，后续会有 Rust 等更多专题。'),
        'index_kw': 'Go 教程,gofmt,go mod,Go 工具链,开发工具,CI 实践',
        'index_h1': 'DevTools 博客',
        'index_lead': ('开发工具与工具链的实战文章：错误排查、版本迁移、CI 实践，'
                       '每篇都经过真实验证。当前连载 Go 工具链专题，后续会有 Rust 等更多专题。'),
        'published': '发布于',
        'updated': '更新于',
        'related': '相关阅读',
        'back': '全部文章',
    },
    'en': {
        'index_title': 'Blog - Go Toolchain & Developer How-Tos | DevTools',
        'index_desc': ('Hands-on Go toolchain articles: troubleshooting, version migrations '
                       'and CI practice, all verified against real setups. '
                       'More series (Rust and beyond) are on the way.'),
        'index_kw': 'go tutorial,gofmt,go mod,go toolchain,developer tools,ci practice',
        'index_h1': 'DevTools Blog',
        'index_lead': ('Hands-on articles about developer tools and toolchains: troubleshooting, '
                       'version migrations and CI practice, all verified against real setups. '
                       'The Go series is running now; Rust and more are on the way.'),
        'published': 'Published',
        'updated': 'Updated',
        'related': 'Further reading',
        'back': 'All articles',
    },
}


def _esc(s):
    import html as html_mod
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def articles_for(lang, articles_en):
    """按语言返回文章列表（英文版从 ARTICLES_EN 取文案，元数据回落到中文版）。"""
    out = []
    for a in ARTICLES:
        if lang == 'en':
            en = dict(a)
            en.update(articles_en[a['slug']])
            out.append(en)
        else:
            out.append(a)
    return out


def render_index(lang, articles_en, base):
    """博客索引页主体：简介 + 文章卡片列表。"""
    t = TEXT[lang]
    out = ['<div class="blog">',
           '  <div class="blog-head">',
           f'    <p class="blog-head-lead">{_esc(t["index_lead"])}</p>',
           '  </div>',
           '  <div class="blog-list">']
    for a in articles_for(lang, articles_en):
        href = base + article_path(a['slug'])
        tags = ''.join(f'<span class="blog-tag">{_esc(tag)}</span>' for tag in a['tags'])
        out.append(f'    <a class="blog-card" href="{_esc(href)}">')
        out.append(f'      <p class="blog-card-title">{_esc(a["h1"])}</p>')
        out.append(f'      <p class="blog-card-desc">{_esc(a["summary"])}</p>')
        out.append(f'      <p class="blog-card-meta"><time datetime="{a["date"]}">'
                   f'{a["date"]}</time>{tags}</p>')
        out.append('    </a>')
    out.append('  </div>')
    out.append('</div>')
    return '\n'.join(out)


def render_article(lang, a, base):
    """文章页主体：h1 + 元信息 + 正文 + 相关阅读。"""
    t = TEXT[lang]
    tags = ''.join(f'<span class="blog-tag">{_esc(tag)}</span>' for tag in a['tags'])
    meta = [f'<time datetime="{a["date"]}">{_esc(t["published"])} {a["date"]}</time>']
    if a['updated'] != a['date']:
        meta.append(f'<time datetime="{a["updated"]}">{_esc(t["updated"])} {a["updated"]}</time>')
    meta.append(tags)
    lang_attr = 'zh-CN' if lang == 'zh' else 'en'
    out = [f'<article class="post" lang="{lang_attr}">']
    out.append(f'  <h1>{_esc(a["h1"])}</h1>')
    out.append(f'  <div class="post-meta">{"".join(meta)}</div>')
    out.append(a['body'].strip())
    out.append('  <div class="post-related">')
    out.append(f'    <h2>{_esc(t["related"])}</h2>')
    out.append('    <ul>')
    for text, href in a.get('related', []):
        out.append(f'      <li><a href="{_esc(base + href)}">{_esc(text)}</a></li>')
    out.append(f'      <li><a href="{_esc(base + BLOG_INDEX)}">{_esc(t["back"])}</a></li>')
    out.append('    </ul>')
    out.append('  </div>')
    out.append('</article>')
    return '\n'.join(out)


def article_jsonld(a, url, lang):
    """文章页的 TechArticle 结构化数据。"""
    return {
        '@type': 'TechArticle',
        'headline': a['h1'],
        'description': a['summary'],
        'url': url,
        'datePublished': a['date'],
        'dateModified': a['updated'],
        'inLanguage': 'zh-CN' if lang == 'zh' else 'en',
        'isAccessibleForFree': True,
        'author': {'@type': 'Organization', 'name': 'DevTools'},
        'keywords': a['keywords'],
    }


def index_jsonld(articles, url, lang):
    """博客索引页的 CollectionPage + ItemList 结构化数据。"""
    t = TEXT[lang]
    return [
        {
            '@type': 'CollectionPage',
            'name': t['index_h1'],
            'url': url,
            'description': t['index_desc'],
            'inLanguage': 'zh-CN' if lang == 'zh' else 'en',
            'isAccessibleForFree': True,
        },
        {
            '@type': 'ItemList',
            'numberOfItems': len(articles),
            'itemListOrder': 'https://schema.org/ItemListUnordered',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i, 'name': a['h1'], 'url': url + a['slug'] + '/'}
                for i, a in enumerate(articles, 1)
            ],
        },
    ]
