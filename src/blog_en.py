# -*- coding: utf-8 -*-
"""博客文章的英文文案，按 slug 与 blog.py 的 ARTICLES 一一对应。

硬性约束（check.py 会强制）：英文页面除白名单外不允许出现任何中文字符，
所以本文件的内容必须是完整英文，代码示例里也不要带中文注释。
"""

ARTICLES_EN = {
    'gofmt-vs-goimports': {
        'tags': ['Go', 'Toolchain', 'CI'],
        'title': 'gofmt vs goimports: Why Your CI Formatting Check Fails | DevTools Blog',
        'description': (
            'gofmt only handles code layout; goimports additionally adds/removes imports and '
            'sorts them into groups, so the two tools can produce different output for the same '
            'file. This post covers what each tool does, the three situations where their output '
            'diverges, and how to wire a consistent formatting check into CI (GitHub Actions '
            'example included).'
        ),
        'keywords': (
            'gofmt vs goimports,gofmt flags,goimports install,goimports -local,'
            'go format check ci,gofmt -l,gofumpt,go formatting check fails'
        ),
        'h1': 'gofmt vs goimports: Why Your CI Formatting Check Fails',
        'summary': (
            'gofmt handles layout, goimports handles layout plus imports — and their output '
            'can differ on the same file. Here are the three diverging scenarios and the one '
            'CI setup that ends the confusion.'
        ),
        'body': '''
<blockquote>
  <p><b>TL;DR</b>: gofmt only adjusts layout (indentation, alignment, spacing) and never
  touches imports; goimports = gofmt + automatic import addition/removal + import grouping.
  Running goimports in your editor but gofmt -l in CI (or the reverse) is the most common
  reason for "works on my machine, fails in CI". Standardize on goimports everywhere.</p>
</blockquote>

<h2>1. What gofmt does</h2>
<p>gofmt is the official Go layout tool, installed with the toolchain, with a single job:
<b>make whitespace layout conform to one standard</b>. It handles indentation (tabs),
alignment, spacing around operators and brace placement. It never changes program semantics.</p>
<p>The flags that matter:</p>
<pre><code>gofmt -l .        # list non-conforming files without writing (this is your CI check)
gofmt -d main.go  # show the diff it would apply, without writing
gofmt -w .        # rewrite files in place
gofmt -s -w .     # also simplify code (e.g. x[a:len(x)] -&gt; x[a:])
gofmt -r 'rule' -w .  # rewrite by pattern (rarely needed)</code></pre>
<p>The boundary to remember: <b>gofmt never adds or removes imports, and never reorders
import groups</b>. An imported-but-unused package is left in place by gofmt (the compiler
will complain, but that is not gofmt's job).</p>

<h2>2. The two extra things goimports does</h2>
<p>goimports is not part of the standard toolchain; install it separately:</p>
<pre><code>go install golang.org/x/tools/cmd/goimports@latest</code></pre>
<p>It does everything gofmt does, then two things more:</p>
<ol>
  <li><b>Adds and removes imports</b>: use <code>fmt.Println</code> without importing
      <code>fmt</code> and it adds the line; import something unused and it deletes it.</li>
  <li><b>Groups and sorts imports</b>: standard library in one group, third-party in
      another, alphabetical within each group.</li>
</ol>
<p>A typical example. This file imports <code>os</code> without using it, and the groups
are a mess:</p>
<pre><code>package main

import (
	"github.com/gin-gonic/gin"
	"fmt"
	"os"
)

func main() {
	fmt.Println(gin.Version)
}</code></pre>
<p><b>gofmt output</b>: only sorts <code>"fmt"</code> alphabetically inside the same group;
<code>os</code> stays:</p>
<pre><code>import (
	"fmt"
	"github.com/gin-gonic/gin"
	"os"
)</code></pre>
<p><b>goimports output</b>: drops the unused <code>os</code> and splits stdlib from
third-party:</p>
<pre><code>import (
	"fmt"

	"github.com/gin-gonic/gin"
)</code></pre>
<p>Same input, different output — that is the root cause of "the format check passes
locally but fails in CI".</p>

<h2>3. Three scenarios where the output diverges</h2>
<h3>a. An unused import exists</h3>
<p>gofmt keeps it, goimports removes it. If your editor runs goimports on save but CI
checks with gofmt -l, everything passes; the reverse combination — gofmt locally,
goimports -l in CI — breaks the build.</p>
<h3>b. A missing import</h3>
<p>goimports tries to add it automatically. When several candidates exist (is
<code>rand</code> <code>math/rand</code> or <code>math/rand/v2</code>?), it picks one from
its index — and a wrong guess is a compile error. <b>Always eyeball what goimports added
before committing.</b></p>
<h3>c. Your own organization's packages land in the wrong group</h3>
<p>By default goimports lumps every non-stdlib path into the third-party group, so
<code>git.company.com/team/utils</code> ends up mixed with GitHub dependencies. Use
<code>-local</code> to give your own prefix its own group:</p>
<pre><code>goimports -local git.company.com -w .</code></pre>
<p>Mirror the setting in your editor (VS Code's <code>go.formatTool</code> and the
<code>local</code> setting of gopls), or editor formatting will disagree with the CLI.</p>

<h2>4. The correct CI setup</h2>
<p>One principle: <b>the editor, the command line and CI must use the same tool with the
same flags</b>. Standardizing on goimports is recommended (it is a superset of gofmt and
strictly stronger):</p>
<pre><code># any output means some file is non-conforming; exit 1
files=$(goimports -local git.company.com -l .)
if [ -n "$files" ]; then
  echo "files failing goimports:"
  echo "$files"
  exit 1
fi</code></pre>
<p>A complete GitHub Actions example:</p>
<pre><code>name: check
on: [push, pull_request]
jobs:
  fmt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod   # stay in sync with the repo, kills version skew
      - run: go install golang.org/x/tools/cmd/goimports@latest
      - run: |
          files=$(goimports -l .)
          test -z "$files" || { echo "need goimports: $files"; exit 1; }
      - run: go vet ./...
      - run: go test ./...</code></pre>
<div class="post-note">
<p><b>Version pitfall</b>: gofmt shipped with different Go versions can differ on edge-case
syntax, and goimports grouping behavior has changed across releases. Pinning CI with
<code>go-version-file: go.mod</code> eliminates the whole class of "I formatted it locally,
why does CI still fail".</p>
</div>

<h2>5. Going stricter: gofumpt and staticcheck</h2>
<ul>
  <li><b>gofumpt</b>: a stricter superset of gofmt (e.g. enforcing multi-line import
      blocks). Pick exactly one per repo — mixing gofmt and gofumpt produces flip-flopping
      diffs.</li>
  <li><b>staticcheck</b>: not a formatter but a deep static analyzer, usually run alongside
      the formatting check in CI:</li>
</ul>
<pre><code>go install mvdan.cc/gofumpt@latest
gofumpt -l .
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...</code></pre>

<h2>6. Summary</h2>
<table>
  <tr><th></th><th>gofmt</th><th>goimports</th></tr>
  <tr><td>Installation</td><td>Ships with Go</td><td>go install golang.org/x/tools/cmd/goimports@latest</td></tr>
  <tr><td>Code layout</td><td>Yes</td><td>Yes (identical)</td></tr>
  <tr><td>Add/remove imports</td><td>No</td><td>Yes</td></tr>
  <tr><td>Import grouping</td><td>No</td><td>Yes (-local for your own prefix)</td></tr>
  <tr><td>CI check</td><td>gofmt -l .</td><td>goimports -l . (recommended)</td></tr>
</table>
<p>For more commands and pitfalls (gofmt's -s/-r, the goimports indexing mechanism), see the
<a href="/go-cheatsheet/">Go toolchain command cheat sheet</a>, section
&quot;Formatting &amp; Code Tools&quot;.</p>
''',
        'related': [
            ('Go toolchain command cheat sheet', 'go-cheatsheet/'),
            ('Code formatter (HTML / CSS / JS / SQL)', 'formatter/'),
        ],
    },
}
