# -*- coding: utf-8 -*-
"""博客文章的英文文案，按 slug 与 blog.py 的 ARTICLES 一一对应。

硬性约束（check.py 会强制）：英文页面除白名单外不允许出现任何中文字符，
所以本文件的内容必须是完整英文，代码示例里也不要带中文注释。
"""

ARTICLES_EN = {
    'coraza-waf-rules': {
        'tags': ['WAF', 'Coraza', 'Security', 'ModSecurity', 'OWASP'],
        'title': ('Coraza Rules Explained: From SecRule Syntax to Your First '
                  'Custom Rule | DevTools Blog'),
        'description': (
            'Coraza is a Go-based open-source WAF and the community successor to '
            'ModSecurity, with SecRule syntax that is almost fully compatible. This '
            'post starts from "what a rule is made of" and covers variables, operators, '
            'transforms, actions, the five processing phases, the OWASP CRS set, a '
            'hands-on custom anti-SQLi rule, and the DetectionOnly-vs-On trade-off.'
        ),
        'keywords': (
            'coraza rules,coraza waf,secrule syntax,modsecurity alternative,owasp crs,'
            'coraza custom rule,secruleengine,@rx operator,waf rule writing'
        ),
        'h1': 'Coraza Rules Explained: From SecRule Syntax to Your First Custom Rule',
        'summary': (
            'Coraza is a Go-based open-source WAF and the successor to ModSecurity, with '
            'largely compatible SecRule syntax. This post covers the three parts of a rule, '
            'the five processing phases, the OWASP CRS set, a hands-on custom anti-SQLi '
            'rule, and the DetectionOnly-vs-On trade-off.'
        ),
        'body': '''
<blockquote>
  <p><b>TL;DR</b>: Coraza is an open-source WAF written in Go and the community successor to
  ModSecurity. Its rule syntax (<code>SecRule</code>) is almost fully compatible, so migrating an
  old setup is mostly "swap the engine, keep the rules". The core idea is <b>one SecRule = variable
  + operator + action</b>, combined with five processing phases and the OWASP CRS rule set: you can
  adopt the community rules as-is or write your own targeted rules.</p>
</blockquote>

<h2>1. What Coraza is</h2>
<p>Coraza is a Go-based, OWASP-compliant web application firewall engine, and the widely adopted
replacement since ModSecurity v3 stopped being maintained. Three points worth calling out:</p>
<ul>
  <li><b>ModSecurity-compatible syntax</b>: directives you already wrote - <code>SecRule</code>,
      <code>SecAction</code>, <code>SecRuleEngine</code> - and the OWASP CRS (Core Rule Set) run
      on Coraza with almost no changes, so migration cost is minimal;</li>
  <li><b>Pure Go, no C dependency</b>: it does not depend on the libmodsecurity C library, which
      makes cross-compilation, containerization and embedding into your own Go program painless;</li>
  <li><b>Library or gateway</b>: you can <code>import</code> it into a Go service for inline
      inspection, or deploy it in front of traffic via a Caddy / Nginx connector or a standalone
      gateway such as warden.</li>
</ul>
<p>It is Apache-2.0 licensed and a formal OWASP project.</p>

<h2>2. What a rule is made of</h2>
<p>Most of Coraza's protection logic lives in a single <code>SecRule</code>. The simplest rule
looks like this:</p>
<pre><code>SecRule REQUEST_HEADERS:User-Agent "@rx (?i)(sqlmap|nikto|nmap)" \\
    "id:1001,phase:1,deny,status:403,msg:'known scanner UA'"</code></pre>
<p>It has three parts, in fixed order:</p>
<table>
  <tr><th>Part</th><th>Role</th><th>Example above</th></tr>
  <tr><td>Variable</td><td>What data to inspect: headers, args, URI, body, IP...</td><td><code>REQUEST_HEADERS:User-Agent</code></td></tr>
  <tr><td>Operator</td><td>How to decide a match; starts with @</td><td><code>@rx (?i)(sqlmap|nikto)</code></td></tr>
  <tr><td>Action</td><td>What to do on match; comma-separated key/value pairs</td><td><code>id:1001,phase:1,deny,...</code></td></tr>
</table>
<p>The backslash <code>\\</code> is a line continuation, so a long rule can be split across lines for
readability. Let's take the three parts apart.</p>

<h2>3. Variables: which piece of data you inspect</h2>
<p>Variables decide which part of the request a rule watches. The common ones:</p>
<table>
  <tr><th>Variable</th><th>Meaning</th></tr>
  <tr><td><code>REQUEST_URI</code></td><td>Full request path (including query string); most used</td></tr>
  <tr><td><code>REQUEST_LINE</code></td><td>Full request line, e.g. <code>GET /a?x=1 HTTP/1.1</code></td></tr>
  <tr><td><code>REQUEST_HEADERS</code></td><td>All request headers; add a colon for one, e.g. <code>REQUEST_HEADERS:User-Agent</code></td></tr>
  <tr><td><code>REQUEST_BODY</code></td><td>Request body (POST form / JSON / XML; requires the relevant parser on)</td></tr>
  <tr><td><code>ARGS</code> / <code>ARGS_GET</code> / <code>ARGS_POST</code></td><td>All args / query string only / form only</td></tr>
  <tr><td><code>QUERY_STRING</code></td><td>Query string only</td></tr>
  <tr><td><code>REMOTE_ADDR</code></td><td>Client IP</td></tr>
  <tr><td><code>RESPONSE_BODY</code></td><td>Response body (egress inspection, e.g. leaking card numbers)</td></tr>
  <tr><td><code>TX</code></td><td>Transaction variable; rules pass data between each other with setvar</td></tr>
</table>
<p>Variables also carry count / collection semantics: <code>&amp;ARGS</code> counts the number of
parameters, and <code>ARGS:username</code> selects only the parameter named username. Multiple
variables are OR-ed with <code>|</code>: <code>REQUEST_HEADERS|REQUEST_BODY</code> means "match if
either header or body hits".</p>

<h2>4. Operators: how a match is decided</h2>
<p>Operators decide the matching logic and all start with @. The most common is regex matching:</p>
<pre><code>@rx &lt;regular expression&gt;   # regex match, returns true on hit
@pm word1 word2 ...        # phrase match, multiple keywords OR-ed, faster than many @rx
@pmFromFile /path/list     # read keywords from a file for phrase match (e.g. scanner UA list)</code></pre>
<p>Other common operators:</p>
<table>
  <tr><th>Operator</th><th>Test</th></tr>
  <tr><td><code>@eq</code> / <code>@gt</code> / <code>@lt</code> / <code>@ge</code> / <code>@le</code></td><td>equal / greater / less / greater-or-equal / less-or-equal (numeric)</td></tr>
  <tr><td><code>@contains</code> / <code>@beginsWith</code> / <code>@endsWith</code></td><td>contains / prefix / suffix</td></tr>
  <tr><td><code>@within</code></td><td>whether the target is within a given set (e.g. IP within a CIDR)</td></tr>
  <tr><td><code>@ipMatch</code></td><td>whether the client IP matches a CIDR / IP list</td></tr>
  <tr><td><code>@validateUrlEncoding</code></td><td>whether URL encoding is valid (catches %u and other malformed-encoding bypasses)</td></tr>
  <tr><td><code>@validateUtf8Encoding</code></td><td>whether UTF-8 encoding is valid</td></tr>
  <tr><td><code>@detectSQLi</code></td><td>built-in SQL injection detection (used by CRS)</td></tr>
  <tr><td><code>@detectXSS</code></td><td>built-in XSS detection</td></tr>
  <tr><td><code>@rx</code> with <code>!</code></td><td>negation: <code>@rx !...</code> matches when it does NOT match</td></tr>
</table>
<p>Tip: <code>@pm</code> is much faster than a chain of <code>@rx (a|b|c)</code> because it uses an
internal Aho-Corasick multi-pattern matcher; when matching dozens of scanner keywords, prefer
<code>@pmFromFile</code>.</p>

<h2>5. Transforms: normalize before matching</h2>
<p>Attackers mix case, double-URL-encode, and pad with whitespace to evade rules. A transform runs
<b>before</b> matching to normalize those variations. It is written in the action list with a
<code>t:</code> prefix and several can be stacked:</p>
<pre><code>"id:1002,phase:2,deny,t:lowercase,t:urlDecode,t:removeWhitespace,t:compressWhitespace,@rx (?i)(union\\s+select|drop\\s+table)"</code></pre>
<table>
  <tr><th>Transform</th><th>What it does</th></tr>
  <tr><td><code>t:none</code></td><td>Clears any previously accumulated transforms (usually placed first to reset)</td></tr>
  <tr><td><code>t:lowercase</code></td><td>Lowercases, defeating case evasion</td></tr>
  <tr><td><code>t:urlDecode</code> / <code>t:urlDecodeUni</code></td><td>URL-decode (including %u encoding)</td></tr>
  <tr><td><code>t:removeWhitespace</code> / <code>t:compressWhitespace</code></td><td>Remove / compress runs of whitespace</td></tr>
  <tr><td><code>t:htmlEntityDecode</code></td><td>Decode entities like <code>&amp;amp;</code> <code>&amp;#x3c;</code></td></tr>
  <tr><td><code>t:base64Decode</code></td><td>Base64-decode</td></tr>
  <tr><td><code>t:normalisePath</code> / <code>t:normalisePathWin</code></td><td>Normalize path (resolve ../ and extra slashes)</td></tr>
  <tr><td><code>t:cmdLine</code></td><td>Normalize a command-line string (defeats spacing, quotes, path tricks)</td></tr>
</table>

<h2>6. Actions: what happens after a match</h2>
<p>Actions fall into three groups. The disruptive actions decide the request's fate:</p>
<table>
  <tr><th>Disruptive</th><th>Effect</th></tr>
  <tr><td><code>deny</code></td><td>Block immediately; pair with <code>status:403</code> (or 406, etc.)</td></tr>
  <tr><td><code>block</code></td><td>Block per the current <code>SecDefaultAction</code> (more flexible)</td></tr>
  <tr><td><code>pass</code></td><td>Allow but log / count (common for alert-only rules)</td></tr>
  <tr><td><code>allow</code></td><td>Allow and skip remaining phase checks</td></tr>
  <tr><td><code>redirect</code> + <code>location</code></td><td>302 redirect to a given URL</td></tr>
</table>
<p>Non-disruptive actions keep bookkeeping and context:</p>
<pre><code>setvar:tx.sql_hits=+1     # increment a tx variable (block later when &gt; threshold)
setvar:tx.block_flag=1    # set a flag later rules read to block
capture                   # store @rx capture groups into TX.0 / TX.1 ...
log / nolog               # whether to write to the log
auditlog / noauditlog     # whether to enter the audit log</code></pre>
<p>Some metadata actions must be on every rule for troubleshooting:</p>
<pre><code>id:1003                  # rule ID (required, globally unique; CRS uses 900000+, custom 1000-7999)
phase:2                  # processing phase
msg:'sql injection'       # human-readable note recorded on match
severity:'CRITICAL'       # level (EMERGENCY/ALERT/CRITICAL/ERROR/WARNING/NOTICE/INFO)
tag:'attack-sqli'         # tag, handy for grouping stats</code></pre>

<h2>7. Chains: multi-condition "AND"</h2>
<p>A single rule expresses one "variable + operator". To express "A AND B", chain rules with
<code>chain</code>; only when the whole chain matches does the last rule's disruptive action run:</p>
<pre><code>SecRule ARGS_GET:q "@rx (?i)select" "id:2001,phase:2,chain,t:none,t:lowercase"
    SecRule REQUEST_HEADERS:User-Agent "@rx (?i)(sqlmap|havij)" "deny,status:403,msg:'sql tool'"</code></pre>
<p>This means: block only when parameter <code>q</code> contains select <b>and</b> the UA is a
scanner - avoiding a bare "select" blocking a legitimate search that happens to contain SQL
keywords.</p>

<h2>8. The five phases</h2>
<p>Rules are distributed across request / response phases by <code>phase</code>; earlier is cheaper:</p>
<table>
  <tr><th>Phase</th><th>When</th><th>Good for</th></tr>
  <tr><td>phase:1</td><td>Request headers just received</td><td>Coarse filter by IP / UA / Host (fastest)</td></tr>
  <tr><td>phase:2</td><td>Request body parsed</td><td>Injection / XSS on args and body (most used)</td></tr>
  <tr><td>phase:3</td><td>Before response headers</td><td>Egress header rewriting</td></tr>
  <tr><td>phase:4</td><td>After response body</td><td>Egress data-leak inspection (card / ID numbers)</td></tr>
  <tr><td>phase:5</td><td>At logging</td><td>Stats / logging only, never blocks</td></tr>
</table>
<p>Putting cheap coarse filters in phase:1 and expensive regex / decoding in phase:2 is the key to
fewer false positives and lower overhead.</p>

<h2>9. OWASP CRS: rules that work out of the box</h2>
<p>Writing your own rules is the backstop; what actually stops day-to-day attacks is the <b>OWASP
CRS (Core Rule Set)</b> - a community-maintained, general-purpose rule set covering SQLi, XSS,
file inclusion, protocol violations and scanner fingerprints, shipped with Coraza. You enable it by
Including it in your config:</p>
<pre><code>Include /path/to/coraza.conf          # engine base config (SecRuleEngine, etc.)
Include /path/to/crs-setup.conf       # CRS master switch and tuning
Include /path/to/rules/*.conf          # the actual rule files</code></pre>
<p>Handy CRS knobs (in <code>crs-setup.conf</code>):</p>
<ul>
  <li><code>tx.paranoia_level</code>: paranoia level 1-4; higher is stricter and noisier, default 1.
      Start at 1 and raise it once things are stable;</li>
  <li><code>tx.blocking_paranoia_level</code>: the level that actually blocks; can be lower than
      <code>paranoia_level</code> so higher levels only log while lower levels block;</li>
  <li><code>tx.anomaly_score_block</code>: block when the accumulated anomaly score passes a
      threshold instead of on a single hit - far more stable than per-rule deny; each rule usually
      only adds score, and the total decides, which sharply cuts false positives.</li>
</ul>

<h2>10. Hands-on: a custom anti-SQLi rule</h2>
<p>Suppose your search endpoint <code>/search?q=</code> keeps getting injection probes and you want a
targeted rule on top of CRS. Idea: normalize first, regex next, count rather than block on hit, and
deny only past a threshold:</p>
<pre><code># /etc/coraza/custom/search-sqli.conf
SecRule REQUEST_URI "@rx (?i)/search" "id:900100,phase:1,pass,nolog,setvar:tx.on_search=1"

SecRule ARGS_GET:q \\
    "@rx (?i)(union\\s+select|select\\s+.*\\s+from|or\\s+1=1|'\\s+or\\s+'|drop\\s+table|insert\\s+into)" \\
    "id:900101,phase:2,chain,t:none,t:lowercase,t:urlDecode,t:compressWhitespace"
    SecRule TX:on_search "@eq 1" \\
        "deny,status:403,msg:'SQLi in search q',severity:'CRITICAL',tag:'attack-sqli',\\
         setvar:tx.sql_score=+5"

SecAction "id:900102,phase:2,pass,setvar:tx.sql_score=0"
SecRule TX:sql_score "@ge 5" "id:900103,phase:2,deny,status:403,msg:'SQLi score exceeded'"</code></pre>
<p>This rule does three things: 1) it only applies on <code>/search</code>, leaving other endpoints
alone; 2) it matches <code>q</code> case-insensitively and after decoding, and on a hit just stamps
a <code>sql_score</code> flag; 3) the real block is the "score reached 5" rule, leaving a buffer for
legitimate keyword searches so one bad match does not 403. Include the custom file in the main
config; CRS itself stays untouched.</p>

<h2>11. DetectionOnly vs On: observe before you block</h2>
<p><code>SecRuleEngine</code> is the master switch; only two values matter:</p>
<table>
  <tr><th>Value</th><th>Behavior</th><th>When</th></tr>
  <tr><td><code>DetectionOnly</code></td><td>Log only, never block</td><td>Run new rules / new sites for a while first</td></tr>
  <tr><td><code>On</code></td><td>Act on matches per the actions</td><td>Once false positives are under control</td></tr>
</table>
<p>Rule of thumb: <b>any new rule, any newly onboarded site, runs in DetectionOnly for at least one
to two weeks</b> first. Read the audit log to see whether legitimate traffic was flagged (typical
false positives: searches containing "select", rich-text editing containing <code>&lt;</code>, or
large JSON blobs of text). Once the false-positive rate is acceptable, switch the relevant rules to
<code>On</code> or raise <code>blocking_paranoia_level</code>. <b>Going straight to On is the number
one cause of a WAF blocking legitimate traffic.</b></p>

<h2>12. How to actually run it</h2>
<p>Coraza is not only a standalone box; four common ways to deploy:</p>
<table>
  <tr><th>Way</th><th>How</th><th>When</th></tr>
  <tr><td>Go library inline</td><td><code>import github.com/corazawaf/coraza/v3</code> and call ProcessRequest in your handler</td><td>You write the Go service and want inline inspection</td></tr>
  <tr><td>Caddy connector</td><td>Use the coraza-caddy plugin; a few lines in the Caddyfile</td><td>You already reverse-proxy with Caddy</td></tr>
  <tr><td>Nginx connector</td><td>coraza-nginx dynamic module</td><td>You already use Nginx and want minimal change</td></tr>
  <tr><td>Standalone gateway</td><td>E.g. warden, one binary packing Coraza + CC protection + dashboard</td><td>You want a panel and zero config fiddling</td></tr>
</table>
<p>For Caddy, the minimal config is just:</p>
<pre><code>{
    order coraza before reverse_proxy
}
example.com {
    coraza {
        directives `
            Include /etc/coraza/coraza.conf
            Include /etc/coraza/crs/crs-setup.conf
            Include /etc/coraza/rules/*.conf
        `
    }
    reverse_proxy 127.0.0.1:8000
}</code></pre>

<h2>13. Recap</h2>
<p>Coraza brings ModSecurity's mature rule system to Go, at near-zero migration cost. Keep this
spine in mind:</p>
<table>
  <tr><th>Concept</th><th>One line</th></tr>
  <tr><td>One rule</td><td>variable + operator (starts with @) + action (id/phase/deny...)</td></tr>
  <tr><td>Normalize</td><td>Use t: transforms to defeat evasion before matching</td></tr>
  <tr><td>Multi-condition</td><td>chain for "AND", TX variable for cross-rule counting</td></tr>
  <tr><td>Daily protection</td><td>Adopt OWASP CRS; do not hand-roll from scratch</td></tr>
  <tr><td>Go-live discipline</td><td>DetectionOnly observe -&gt; then On; score-threshold blocking beats per-rule deny</td></tr>
</table>
<p>To see a real project that packs Coraza with CC protection and IP-origin blocking into a
single-file gateway, read <a href="/en/blog/warden-go-waf/">warden: A Single-Binary Go
Reverse-Proxy WAF</a>.</p>
''',
        'related': [
            ('warden: A Single-Binary Go Reverse-Proxy WAF', 'blog/warden-go-waf/'),
            ('Go toolchain command cheat sheet', 'go-cheatsheet/'),
        ],
    },
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
            ('Coraza Rules Explained', 'blog/coraza-waf-rules/'),
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
