# -*- coding: utf-8 -*-
"""博客文章的英文文案，按 slug 与 blog.py 的 ARTICLES 一一对应。

硬性约束（check.py 会强制）：英文页面除白名单外不允许出现任何中文字符，
所以本文件的内容必须是完整英文，代码示例里也不要带中文注释。
"""

ARTICLES_EN = {
    'warden-go-waf': {
        'tags': ['Go', 'WAF', 'Open Source'],
        'title': ('warden: A Single-Binary Go Reverse-Proxy WAF with CC Protection '
                  '| DevTools Blog'),
        'description': (
            'warden is a lightweight reverse-proxy WAF written in Go: connection limiting, '
            'rate limiting, CC protection, IP origin blocking and OWASP Coraza rule detection '
            'all live in one executable, with the admin dashboard embedded via go:embed and a '
            'pure-Go SQLite that needs no cgo. This post covers the problem it solves, the key '
            'design trade-offs, a three-minute deployment, and five things to know before '
            'putting it in front of production traffic.'
        ),
        'keywords': (
            'go waf,open source waf,reverse proxy waf,cc attack protection,self hosted waf,'
            'coraza waf,go embed,single binary,ip geolocation blocking,warden waf'
        ),
        'h1': 'warden: A Single-Binary Go Reverse-Proxy WAF',
        'summary': (
            'L4 connection limiting, rate limiting, CC challenges, IP origin blocking and '
            'OWASP Coraza rules packed into one Go executable, with the admin dashboard '
            'embedded via go:embed. What problem it solves, why it is built this way, and five '
            'things to check before going live.'
        ),
        'body': '''
<blockquote>
  <p><b>TL;DR</b>: warden is a self-hosted WAF for small sites that are bothered by CC floods
  and scanners, but cannot justify a commercial WAF and do not want to change DNS for a cloud
  one. Drop a single binary on the server and point your Nginx traffic at it. Current release
  is <b>v1.0.1</b>, licensed Apache-2.0, shipping for Windows and Linux (amd64 + arm64).</p>
</blockquote>

<h2>1. The problem it targets</h2>
<p>Small sites - company homepages, school portals, internal business systems - are drained by
two kinds of traffic:</p>
<ol>
  <li><b>CC floods and scraping</b>: many IPs hammering hot pages (news listings, detail pages,
      search endpoints). Every single request looks legitimate; together they saturate the
      backend.</li>
  <li><b>Scanner probing</b>: path scans for <code>/wp-admin</code>, <code>/.env</code>,
      <code>/phpmyadmin</code>, plus the fingerprints of tools like sqlmap and nikto.</li>
</ol>
<p>Every off-the-shelf option has a catch: commercial WAFs cost money; cloud WAFs require a DNS
change and route traffic through someone else; Nginx's native <code>limit_req</code> can rate
limit but is limited at <b>telling real users from scripts</b> - rate limiting is allow or deny,
with nothing in between.</p>
<p>warden's position: <b>one small self-hosted program covering L4-L7 protection, CC challenges
and observability</b>. Its guiding principle is "better one extra CAPTCHA than blocking a real
user" - suspected scripts get a challenge first, and passing it issues a trust credential that
puts them on the fast path.</p>

<h2>2. Three choices made for deployability</h2>
<p>The most interesting part of this project is not the feature list but how far it pushes down
deployment complexity.</p>
<h3>a. The frontend is embedded with go:embed</h3>
<p>The admin dashboard is a single-file Vue3 + Element Plus + ECharts app, embedded directly
into the executable with <code>go:embed</code>: <b>no separate frontend deployment, no static
location in Nginx</b>. Third-party libraries are vendored locally in <code>web/vendor/</code>
rather than loaded from a CDN, so it works on isolated networks.</p>
<pre><code>// edit web/admin.html, rebuild, and the assets are baked in
go build -o warden ./cmd/warden</code></pre>
<h3>b. Pure-Go SQLite, no cgo</h3>
<p>It uses <code>modernc.org/sqlite</code> instead of the cgo-based mattn driver. The direct
benefit: <b>cross-compilation is painless</b>, so you can produce Linux binaries from Windows
with no cross toolchain.</p>
<pre><code>CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -o warden-linux-arm64 ./cmd/warden</code></pre>
<p>One release zip contains <code>warden.exe</code> (Windows/amd64), <code>warden</code>
(Linux/amd64) and <code>warden-linux-arm64</code>, all flat in the root, and
<code>run.sh</code> picks the right one via <code>uname -m</code>.</p>
<h3>c. Every in-memory state has a TTL and a sweeper</h3>
<p>Token buckets, trusted IPs, behavior state and offense records all expire and are cleaned up
by background goroutines, so memory does not grow without bound. That is what makes a
self-hosted daemon safe to deploy and forget.</p>

<h2>3. How a request travels</h2>
<pre><code>client --&gt; [Nginx / LB, optional] --&gt; warden :81 --&gt; backend :8002</code></pre>
<p>Internally, two layers:</p>
<p><b>TCP layer</b>: <code>ConnLimitListener</code> applies a token bucket at the
<code>accept</code> stage and <b>drops excess connections outright, before any HTTP work</b>.
That is where the most resource-hungry connection floods get stopped.</p>
<p><b>HTTP middleware chain</b>, outside in:</p>
<pre><code>1. IP blocklist     -- hit -&gt; block
2. URL allow/deny   -- hit -&gt; allow / block
3. IP allowlist     -- hit -&gt; pass through (skips every check below)
4. CC protection    -- flood / behavior / rate -&gt; CAPTCHA challenge
5. Rate limiting    -- hot path / site-wide / subnet -&gt; 429
6. Coraza WAF       -- OWASP CRS rule detection
7. Multi-site router-- reverse proxy by Host</code></pre>
<p>The order is the strategy: allowlisted IPs bypass everything, and <b>the expensive check
(Coraza) sits near the end</b>, so traffic already blocked upstream never reaches the rule
engine.</p>

<h2>4. How CC protection decides "this is a script"</h2>
<p>This is where warden differs most from plain rate limiting. It does not rely on a single
threshold; it stacks several signals:</p>
<table>
  <tr><th>Mechanism</th><th>Signal</th></tr>
  <tr><td>New-IP flood detection</td><td>Sliding-window ratio of new vs. known IPs; above the threshold it is a flood and every new IP must pass a CAPTCHA</td></tr>
  <tr><td>Behavior detection</td><td>Suspiciously uniform request intervals, or hitting only one or two paths forever -&gt; script</td></tr>
  <tr><td>Trusted-IP fast path</td><td>Cumulative visits above a threshold promote the IP to trusted, with its own high-quota bucket; persisted to SQLite</td></tr>
  <tr><td>Trusted-session fast path</td><td>Passing a CAPTCHA issues a cookie, so multiple users behind one IP do not interfere</td></tr>
  <tr><td>Per-IP rate limit</td><td>Separate token bucket for untrusted IPs; exceeding it <b>raises a CAPTCHA instead of dropping the connection</b></td></tr>
  <tr><td>Shared token bucket</td><td>Total untrusted capacity guard; under congestion it self-recovers via CAPTCHAs</td></tr>
</table>
<p>A few details show it was honed against real traffic:</p>
<ul>
  <li><b>Static assets are exempt</b>: images, JS, CSS and fonts pass straight through, so one
      article loading dozens of resources is not mistaken for an attack.</li>
  <li><b>CAPTCHAs are reused per (session, IP)</b>: regenerating does not clobber the code the
      user is currently typing.</li>
  <li><b>Search-engine allowlist</b>: crawler user agents get rate limiting instead of
      CAPTCHAs, so indexing is unaffected.</li>
  <li><b>Escalation needs two conditions</b>: an offense count <i>and</i> sustained offending
      beyond <code>offender_persist_sec</code> before kernel-level blocking kicks in - a
      one-off IP should not create a firewall rule and bloat the rule table.</li>
</ul>
<p>There is also <b>IP origin blocking</b> backed by an offline xdb database: foreign IPs and
cloud/IDC ranges can be blocked independently. Real users rarely come from a Tencent Cloud or
Alibaba Cloud data center, so this is effective against bot traffic - and it makes
<b>no external requests</b>, so there is no third-party API dependency.</p>

<h2>5. Up and running in three minutes</h2>
<p>With a release zip, no compilation needed:</p>
<pre><code>mkdir -p /opt/warden &amp;&amp; cd /opt/warden
unzip ~/warden-v1.0.1.zip
chmod +x run.sh warden warden-linux-arm64   # zip does not preserve executable bits
./run.sh</code></pre>
<p>Building it yourself (Go 1.23+):</p>
<pre><code># Windows
$env:GOPROXY = "https://goproxy.cn,https://goproxy.io,direct"
go mod tidy
go build -o warden.exe ./cmd/warden

# Linux
export GOPROXY=https://goproxy.cn,https://goproxy.io,direct
go build -o warden ./cmd/warden
./warden -config config.json</code></pre>
<p>The minimal config is two lines - it sits in front of your backend:</p>
<pre><code>{
  "listen": ":81",
  "backend": "http://127.0.0.1:8002"
}</code></pre>
<p>Verify:</p>
<pre><code>curl http://127.0.0.1:81/healthz   # health check
curl -I  http://127.0.0.1:81/      # should be proxied to the backend</code></pre>
<p>The dashboard defaults to <code>http://127.0.0.1:9090</code> and shows live blocking
counters, QPS/block-rate trends, a breakdown of block categories, CPU and memory, paginated
attack logs and the trusted IP list.</p>
<p>Three deployment shapes to choose from:</p>
<table>
  <tr><th>Option</th><th>Path</th><th>When</th></tr>
  <tr><td>A. Nginx in front (recommended)</td><td>:443 -&gt; Nginx (TLS) -&gt; warden:81 -&gt; backend</td><td>You need TLS and already run Nginx</td></tr>
  <tr><td>B. warden exposed directly</td><td>:80 -&gt; warden -&gt; backend</td><td>You want one hop less (on Windows, port 80 needs admin)</td></tr>
  <tr><td>C. Multi-site</td><td>Route by Host to different upstreams</td><td>One machine proxying several sites</td></tr>
</table>
<p>For long-term operation, register it as a service with systemd (Linux) or NSSM (Windows);
the README has a ready-made unit file.</p>

<h2>6. Five things to know before going live</h2>
<h3>a. Observe with DetectionOnly, then switch to On</h3>
<p>Set <code>SecRuleEngine DetectionOnly</code> in <code>rules/coraza.conf</code>, watch for
false positives for a while, and only then switch to <code>On</code>. Do the same with CC
protection: start with CAPTCHA challenges only, check the real-user pass rate, then tighten
thresholds gradually. <b>Going straight to On is the number one cause of a WAF blocking
legitimate traffic.</b></p>
<h3>b. Editing config.json has no effect</h3>
<p>Config resolution is <b>SQLite config table first, config.json as fallback</b>. The first
start seeds the database from config.json; after that <b>the database wins</b>. Change settings
in the dashboard and restart.</p>
<h3>c. Nginx on Windows caps out at 1024 connections</h3>
<p>The Windows build of Nginx uses the <code>select()</code> event model, so a single worker
handles roughly 1024 concurrent connections no matter how large
<code>worker_connections</code> is. For higher concurrency, run Nginx on Linux or WSL2, or let
warden listen directly (Go uses IOCP on Windows and has no such limit).</p>
<h3>d. Align upstream keepalive timeouts</h3>
<p>The idle-connection reclaim time from warden to the backend must be <b>shorter</b> than the
backend's own (for example Tomcat's <code>connectionTimeout</code>), otherwise warden reuses
connections the backend already closed, causing <code>connection reset</code> and intermittent
502s.</p>
<h3>e. Firewall blocking is off by default - keep it that way at first</h3>
<p>An early version created two <code>netsh</code> rules per IP, which under attack volume
quickly accumulated into tens of thousands; Windows Firewall recompiles the entire rule table
on every add or remove, so operations got slower and slower. It is therefore <b>disabled by
default</b> now, and enabling it means committing to periodic rule cleanup.</p>

<h2>7. Two engineering details worth stealing</h2>
<p>The dashboard runs in the <b>same process</b> as the WAF, so polling overhead lands directly
on the serving path. Two optimizations address that:</p>
<ul>
  <li><b>Memory stats avoid <code>runtime.ReadMemStats</code></b>: it triggers a stop-the-world
      pause, measured at about 8.7 microseconds per call; reading the same metric through
      <code>runtime/metrics</code> takes about 0.3 microseconds (roughly 27x faster) with
      identical values. The dashboard polls <code>/api/stats</code> every 3 seconds, which
      amplifies the difference.</li>
  <li><b>CPU usage is sampled continuously</b>: <code>GetSystemTimes</code> and
      <code>/proc/stat</code> return cumulative values since boot, so a rate needs two samples.
      Sampling only when the endpoint is called means that after leaving the dashboard for a
      while, the first reading covers the whole gap - possibly an average over several minutes.
      A background loop samples every second and caches; the endpoint only reads the cache.</li>
</ul>

<h2>8. Who it is for, and who it is not</h2>
<p><b>For</b>: company homepages, school and government sites, internal business systems -
cases where the backend is not very robust, traffic patterns are fairly stable, and nobody is
doing security ops full time. Also for anyone who wants to self-host and fully control their
data and rules.</p>
<p><b>Not for</b>: teams needing enterprise-grade rule operations, volumetric DDoS scrubbing
(that belongs at the ISP or CDN layer), or anyone expecting install-and-forget. The README says
it plainly: this is <b>application-layer protection</b> and does not replace system patching,
least privilege, or secure coding in the backend.</p>

<h2>9. Project facts</h2>
<ul>
  <li>License: <b>Apache-2.0</b> (includes an explicit patent grant; commercial use and
      closed-source integration allowed)</li>
  <li>Stack: Go 1.23+, OWASP Coraza v3, pure-Go SQLite, Vue3 + Element Plus + ECharts</li>
  <li>Current version: v1.0.1 (single cross-platform package)</li>
  <li>Gitee: <a href="https://gitee.com/jxw1111/warden" rel="nofollow noopener" target="_blank">gitee.com/jxw1111/warden</a></li>
  <li>GitHub: <a href="https://github.com/xwjiang2003/warden" rel="nofollow noopener" target="_blank">github.com/xwjiang2003/warden</a></li>
</ul>
<p>Issues and PRs are welcome. Contributions are licensed under Apache-2.0 by default; please
include a <code>Signed-off-by</code> line (DCO) in your commit message.</p>
''',
        'related': [
            ('Go toolchain command cheat sheet', 'go-cheatsheet/'),
            ('gofmt vs goimports', 'blog/gofmt-vs-goimports/'),
        ],
    },
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
