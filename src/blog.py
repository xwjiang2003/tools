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
        'slug': 'coraza-waf-rules',
        'date': '2026-09-25',
        'updated': '2026-09-25',
        'tags': ['WAF', 'Coraza', '安全', 'ModSecurity', 'OWASP'],
        'title': ('Coraza 规则详解：从 SecRule 语法到写出第一条防护规则 '
                  '| DevTools 博客'),
        'description': (
            'Coraza 是 Go 语言写的开源 WAF、ModSecurity 的官方接任者，规则语法（SecRule）'
            '与 ModSecurity 几乎完全兼容。本文从「一条规则由什么组成」讲起，覆盖变量、'
            '运算符、转换函数、动作、五个处理阶段、OWASP CRS 核心规则集，并手把手写一个 '
            '防 SQL 注入的自定义规则，最后讲清 DetectionOnly 与 On 两种模式的取舍。'
        ),
        'keywords': (
            'Coraza 规则,Coraza WAF,SecRule 语法,ModSecurity 替代,OWASP CRS,'
            'Coraza 自定义规则,SecRuleEngine,@rx 运算符,WAF 规则编写'
        ),
        'h1': 'Coraza 规则详解：从 SecRule 语法到写出第一条防护规则',
        'summary': (
            'Coraza 是 Go 写的开源 WAF、ModSecurity 的接任者，SecRule 语法基本兼容。'
            '讲清一条规则的三要素、五个处理阶段、OWASP CRS 规则集，并手把手写一个 '
            '防 SQL 注入的自定义规则，以及 DetectionOnly 与 On 的取舍。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：Coraza 是 Go 语言实现的开源 WAF、ModSecurity 的官方接任者，
  规则语法（SecRule）与 ModSecurity 几乎完全兼容，老项目迁移基本是「换引擎、规则照抄」。
  核心是<b>一条 SecRule = 变量 + 运算符 + 动作</b>，配合五个处理阶段与 OWASP CRS 规则集，
  既能直接套用社区规则，也能自己写针对性规则。</p>
</blockquote>

<h2>一、Coraza 是什么</h2>
<p>Coraza 是一个用 Go 写的、符合 <b>OWASP 标准</b>的 Web 应用防火墙引擎，也是 ModSecurity v3
停止维护后被社区广泛采用的替代品。它最值得说的三点：</p>
<ul>
  <li><b>语法兼容 ModSecurity</b>：过去写的 <code>SecRule</code>、<code>SecAction</code>、
      <code>SecRuleEngine</code> 等指令，以及 OWASP CRS（Core Rule Set）核心规则集，
      基本可以原样跑在 Coraza 上，迁移成本极低；</li>
  <li><b>纯 Go、无 C 依赖</b>：不依赖 libmodsecurity 那个 C 库，交叉编译、容器化、嵌入到
      自己的 Go 程序里都顺手；</li>
  <li><b>既能当库也能当网关</b>：可以 <code>import</code> 进 Go 服务做内联检测，也能通过
      Caddy / Nginx 连接器或独立网关（如 warden）部署在流量前面。</li>
</ul>
<p>它遵循 Apache-2.0 许可，是 OWASP 基金会下的正式项目。</p>

<h2>二、一条规则由什么组成</h2>
<p>Coraza 的绝大多数防护逻辑都写在一条 <code>SecRule</code> 里。一条最朴素的规则长这样：</p>
<pre><code>SecRule REQUEST_HEADERS:User-Agent "@rx (?i)(sqlmap|nikto|nmap)" \\
    "id:1001,phase:1,deny,status:403,msg:'known scanner UA'"</code></pre>
<p>它由三个部分构成，顺序固定：</p>
<table>
  <tr><th>组成部分</th><th>作用</th><th>上例对应</th></tr>
  <tr><td>变量（Variable）</td><td>指定检测哪份数据：请求头、参数、URI、body、IP……</td><td><code>REQUEST_HEADERS:User-Agent</code></td></tr>
  <tr><td>运算符（Operator）</td><td>指定怎么判定命中，以 @ 开头</td><td><code>@rx (?i)(sqlmap|nikto)</code></td></tr>
  <tr><td>动作（Action）</td><td>指定命中后做什么，逗号分隔的键值对</td><td><code>id:1001,phase:1,deny,...</code></td></tr>
</table>
<p>反斜杠 <code>\\</code> 是续行符，把一条长规则拆成多行更可读。下面分别拆看这三块。</p>

<h2>三、变量：你要检测的是哪份数据</h2>
<p>变量决定了规则盯着请求的哪一部分。常用的一批：</p>
<table>
  <tr><th>变量</th><th>含义</th></tr>
  <tr><td><code>REQUEST_URI</code></td><td>完整请求路径（含查询串），最常用</td></tr>
  <tr><td><code>REQUEST_LINE</code></td><td>完整请求行，如 <code>GET /a?x=1 HTTP/1.1</code></td></tr>
  <tr><td><code>REQUEST_HEADERS</code></td><td>全部请求头；加冒号取单个，如 <code>REQUEST_HEADERS:User-Agent</code></td></tr>
  <tr><td><code>REQUEST_BODY</code></td><td>请求体（POST 表单 / JSON / XML，需开启相应解析）</td></tr>
  <tr><td><code>ARGS</code> / <code>ARGS_GET</code> / <code>ARGS_POST</code></td><td>所有参数 / 仅查询串 / 仅表单</td></tr>
  <tr><td><code>QUERY_STRING</code></td><td>仅查询串部分</td></tr>
  <tr><td><code>REMOTE_ADDR</code></td><td>客户端 IP</td></tr>
  <tr><td><code>RESPONSE_BODY</code></td><td>响应体（出方向检测，如泄露银行卡号）</td></tr>
  <tr><td><code>TX</code></td><td>事务变量，规则之间用 setvar 传递数据</td></tr>
</table>
<p>变量还能带计数 / 集合语义，比如 <code>&amp;ARGS</code> 统计参数个数，
<code>ARGS:username</code> 只取名为 username 的参数。多个变量用 <code>|</code> 并联：
<code>REQUEST_HEADERS|REQUEST_BODY</code> 表示「头或体任一命中即触发」。</p>

<h2>四、运算符：怎么算命中</h2>
<p>运算符决定匹配逻辑，都以 @ 开头。最常用的是正则匹配：</p>
<pre><code>@rx &lt;正则表达式&gt;          # 正则匹配，命中返回 true
@pm word1 word2 ...       # 短语匹配，多关键词「或」关系，性能优于挨个 @rx
@pmFromFile /path/list    # 从文件批量读关键词做短语匹配（如扫描器 UA 清单）</code></pre>
<p>其它常用运算符：</p>
<table>
  <tr><th>运算符</th><th>判定</th></tr>
  <tr><td><code>@eq</code> / <code>@gt</code> / <code>@lt</code> / <code>@ge</code> / <code>@le</code></td><td>等于 / 大于 / 小于 / 大于等于 / 小于等于（数值）</td></tr>
  <tr><td><code>@contains</code> / <code>@beginsWith</code> / <code>@endsWith</code></td><td>包含 / 前缀 / 后缀</td></tr>
  <tr><td><code>@within</code></td><td>目标是否在给定集合内（如 IP 在 CIDR 内）</td></tr>
  <tr><td><code>@ipMatch</code></td><td>客户端 IP 是否匹配某个 CIDR / IP 列表</td></tr>
  <tr><td><code>@validateUrlEncoding</code></td><td>URL 编码是否合法（识别 %u 等畸形编码绕过）</td></tr>
  <tr><td><code>@validateUtf8Encoding</code></td><td>UTF-8 编码是否合法</td></tr>
  <tr><td><code>@detectSQLi</code></td><td>内置的 SQL 注入检测（CRS 在用）</td></tr>
  <tr><td><code>@detectXSS</code></td><td>内置的 XSS 检测</td></tr>
  <tr><td><code>@rx</code> 配合 <code>!</code></td><td>取反：<code>@rx !...</code> 表示不匹配才命中</td></tr>
</table>
<p>小提示：<code>@pm</code> 比一串 <code>@rx (a|b|c)</code> 快得多，它内部是 Aho-Corasick 多模匹配；
要匹配几十个扫描器关键词时优先用 <code>@pmFromFile</code>。</p>

<h2>五、转换函数（transforms）：匹配前先归一化</h2>
<p>攻击者常用大小写混合、URL 双重编码、空白穿插来绕过规则。转换函数会在匹配<b>之前</b>
对变量做变换，把变形归一化。写在动作里、用 <code>t:</code> 前缀，可叠加多个：</p>
<pre><code>"id:1002,phase:2,deny,t:lowercase,t:urlDecode,t:removeWhitespace,t:compressWhitespace,@rx (?i)(union\\s+select|drop\\s+table)"</code></pre>
<table>
  <tr><th>转换函数</th><th>做了什么</th></tr>
  <tr><td><code>t:none</code></td><td>先清空之前累积的转换（常放最前重置）</td></tr>
  <tr><td><code>t:lowercase</code></td><td>转小写，抵消大小写绕过</td></tr>
  <tr><td><code>t:urlDecode</code> / <code>t:urlDecodeUni</code></td><td>URL 解码（含 %u 编码）</td></tr>
  <tr><td><code>t:removeWhitespace</code> / <code>t:compressWhitespace</code></td><td>去空白 / 压缩连续空白</td></tr>
  <tr><td><code>t:htmlEntityDecode</code></td><td>解码 <code>&amp;amp;</code> <code>&amp;#x3c;</code> 这类 HTML 实体</td></tr>
  <tr><td><code>t:base64Decode</code></td><td>Base64 解码</td></tr>
  <tr><td><code>t:normalisePath</code> / <code>t:normalisePathWin</code></td><td>归一化路径（消解 ../ 与多余斜杠）</td></tr>
  <tr><td><code>t:cmdLine</code></td><td>把命令行字符串归一化（抵消失空格、引号、路径变形）</td></tr>
</table>

<h2>六、动作：命中之后做什么</h2>
<p>动作分三类。最常用的是破坏性动作（决定请求的最终命运）：</p>
<table>
  <tr><th>破坏性动作</th><th>效果</th></tr>
  <tr><td><code>deny</code></td><td>立即拦截，可配 <code>status:403</code>（或 406 等）</td></tr>
  <tr><td><code>block</code></td><td>按当前 <code>SecDefaultAction</code> 设定的方式拦截（更灵活）</td></tr>
  <tr><td><code>pass</code></td><td>放行（但记录 / 计数，常用于只告警不拦）</td></tr>
  <tr><td><code>allow</code></td><td>放行并跳过后续阶段检测</td></tr>
  <tr><td><code>redirect</code> + <code>location</code></td><td>302 跳转到指定地址</td></tr>
</table>
<p>非破坏性动作负责记账与上下文：</p>
<pre><code>setvar:tx.sql_hits=+1     # 给事务变量计数（配合 &gt; 阈值再拦）
setvar:tx.block_flag=1    # 打个标记，后面规则读到就拦截
capture                   # 把 @rx 的捕获组存进 TX.0 / TX.1 ...
log / nolog               # 是否写日志
auditlog / noauditlog     # 是否进审计日志</code></pre>
<p>还有些元数据动作必须给每条规则带上，方便排障：</p>
<pre><code>id:1003                  # 规则 ID（必填且全局唯一，CRS 占 900000+ 段，自定义建议 1000-7999）
phase:2                  # 处理阶段
msg:'sql injection'       # 命中时记录的可读信息
severity:'CRITICAL'       # 严重级别（EMERGENCY/ALERT/CRITICAL/ERROR/WARNING/NOTICE/INFO）
tag:'attack-sqli'         # 标签，便于归类统计</code></pre>

<h2>七、规则链（chain）：多条件「且」关系</h2>
<p>单条规则只能表达一个「变量 + 运算符」。要表达「A 且 B」用 <code>chain</code> 把多条规则串起来，
只有整条链全部命中才执行最后一条的破坏性动作：</p>
<pre><code>SecRule ARGS_GET:q "@rx (?i)select" "id:2001,phase:2,chain,t:none,t:lowercase"
    SecRule REQUEST_HEADERS:User-Agent "@rx (?i)(sqlmap|havij)" "deny,status:403,msg:'sql tool'"</code></pre>
<p>上例含义：只有当参数 <code>q</code> 里出现 select <b>并且</b> UA 是扫描器时才拦截——
避免单独一条 select 就把正常带 SQL 关键字的搜索请求误杀。</p>

<h2>八、五个处理阶段（phase）</h2>
<p>规则按 <code>phase</code> 分布在请求 / 响应的不同阶段，越靠前越省资源：</p>
<table>
  <tr><th>阶段</th><th>时机</th><th>适合放什么</th></tr>
  <tr><td>phase:1</td><td>请求头刚收完</td><td>按 IP / UA / Host 做粗筛（最快）</td></tr>
  <tr><td>phase:2</td><td>请求体解析完</td><td>参数、body 的注入 / XSS 检测（最常用）</td></tr>
  <tr><td>phase:3</td><td>响应头生成前</td><td>出方向头改写</td></tr>
  <tr><td>phase:4</td><td>响应体生成后</td><td>出方向数据泄露检测（卡号、身份证）</td></tr>
  <tr><td>phase:5</td><td>日志记录时</td><td>仅做统计 / 记日志，不拦截</td></tr>
</table>
<p>把廉价的粗筛放 phase:1、把贵的正则 / 解码放 phase:2，是减少误杀和开销的关键。</p>

<h2>九、OWASP CRS：开箱即用的规则集</h2>
<p>自己写规则是兜底，真正扛住日常攻击的是 <b>OWASP CRS（Core Rule Set）</b>——
一套社区维护、覆盖 SQLi / XSS / 文件包含 / 协议违规 / 扫描器指纹等场景的通用规则，随 Coraza
一起分发。启用方式就是在配置文件里 Include 它：</p>
<pre><code>Include /path/to/coraza.conf          # 引擎基础配置（SecRuleEngine 等）
Include /path/to/crs-setup.conf       # CRS 总开关与调参
Include /path/to/rules/*.conf          # 具体规则文件</code></pre>
<p>CRS 的几个实用调参（在 <code>crs-setup.conf</code> 里）：</p>
<ul>
  <li><code>tx.paranoia_level</code>：偏执等级 1~4，越高规则越严、误报也越多，默认 1；
      上线初期建议先 1，观察稳定后再上调；</li>
  <li><code>tx.blocking_paranoia_level</code>：实际拦截的偏执等级，可低于 <code>paranoia_level</code>
      做到「高级别只记录、低级别才拦」；</li>
  <li><code>tx.anomaly_score_block</code>：把「累计异常分超阈值才拦」作为拦截策略，比单条命中就拦更稳；
      单条规则命中通常只加分、不直接 deny，由总分决定是否拦截，显著降低误杀。</li>
</ul>

<h2>十、实战：写一个防 SQL 注入的自定义规则</h2>
<p>假设搜索接口 <code>/search?q=</code> 老被注入探测，要在 CRS 之外加一条针对性规则。
思路：先归一化、再正则、命中先计数而非直接拦、超阈值再 deny：</p>
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
<p>这条规则做了三件事：①只在 <code>/search</code> 路径启用，不影响别的接口；
②对 <code>q</code> 参数做大小写无关、解码后的正则匹配，命中先打 <code>sql_score</code> 标记；
③真正拦截的是「分数累计到 5」那条，给正常关键词搜索留了缓冲，避免一次误匹配就 403。</p>
<p>把自定义文件 Include 进主配置即可，无需改动 CRS 本身。</p>

<h2>十一、DetectionOnly 与 On：先观察再拦截</h2>
<p><code>SecRuleEngine</code> 是总开关，只有两个值值得记住：</p>
<table>
  <tr><th>取值</th><th>行为</th><th>何时用</th></tr>
  <tr><td><code>DetectionOnly</code></td><td>只记录、不拦截</td><td>新规则 / 新站点上线前先跑一段时间</td></tr>
  <tr><td><code>On</code></td><td>命中即按动作处理</td><td>确认误报可控之后</td></tr>
</table>
<p>经验之谈：<b>任何新规则、任何新接入的站点，先用 DetectionOnly 跑至少一到两周</b>，
翻审计日志看有没有把正常业务算成攻击（典型误杀：带 <code>select</code> 的搜索、带
<code>&lt;</code> 的富文本编辑、JSON 里的大段文本）。确认误报率可接受，再把对应规则切到
<code>On</code> 或调高 <code>blocking_paranoia_level</code>。<b>直接 On 上线是 WAF 误杀的头号原因。</b></p>

<h2>十二、怎么把它跑起来</h2>
<p>Coraza 不是只能当独立盒子，常见四种落地姿势：</p>
<table>
  <tr><th>方式</th><th>怎么做</th><th>适合</th></tr>
  <tr><td>Go 库内联</td><td><code>import github.com/corazawaf/coraza/v3</code>，在 handler 里 ProcessRequest</td><td>自己写 Go 服务、想内联检测</td></tr>
  <tr><td>Caddy 连接器</td><td>用 coraza-caddy 插件，Caddyfile 里加几行即可</td><td>已在用 Caddy 反代</td></tr>
  <tr><td>Nginx 连接器</td><td>coraza-nginx 动态模块</td><td>已在用 Nginx、想最小改动</td></tr>
  <tr><td>独立网关</td><td>如 warden，一个二进制把 Coraza + CC 防护 + 后台打包</td><td>不想碰配置、要开箱即用的面板</td></tr>
</table>
<p>以 Caddy 为例，最小配置只是：</p>
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

<h2>十三、小结</h2>
<p>Coraza 把 ModSecurity 那套成熟的规则体系搬到了 Go 上，迁移几乎零成本。记住这条主线：</p>
<table>
  <tr><th>概念</th><th>一句话</th></tr>
  <tr><td>一条规则</td><td>变量 + 运算符（@ 开头）+ 动作（id/phase/deny…）</td></tr>
  <tr><td>归一化</td><td>用 t: 转换函数在匹配前消解变形绕过</td></tr>
  <tr><td>多条件</td><td>chain 表达「且」，TX 变量做跨规则计数</td></tr>
  <tr><td>日常防护</td><td>直接上 OWASP CRS，别从零手搓</td></tr>
  <tr><td>上线纪律</td><td>DetectionOnly 观察 → 再 On；异常分阈值拦截比单条 deny 稳</td></tr>
</table>
<p>想看一个把 Coraza 和 CC 防护、IP 归属拦截打包成单文件网关的真实项目，见
<a href="/blog/warden-go-waf/">warden：一个单文件部署的 Go 反向代理 WAF</a>。</p>
''',
        'related': [
            ('warden：一个单文件部署的 Go 反向代理 WAF', 'blog/warden-go-waf/'),
            ('Go 工具链命令速查表', 'go-cheatsheet/'),
        ],
    },
    {
        'slug': 'warden-go-waf',
        'date': '2026-09-25',
        'updated': '2026-09-25',
        'tags': ['Go', 'WAF', '开源项目'],
        'title': ('沃盾 warden：单文件部署的 Go 反向代理 WAF（CC 防护 + 内嵌后台）'
                  ' | DevTools 博客'),
        'description': (
            '沃盾（warden）是一个用 Go 写的轻量级反向代理 WAF：连接限流、频率限制、CC 防护、'
            'IP 归属拦截与 OWASP Coraza 规则检测都在一个可执行文件里，管理后台通过 go:embed '
            '内嵌，无需额外部署前端，SQLite 为纯 Go 实现不需要 cgo。本文讲清它解决什么问题、'
            '几个关键设计取舍、三分钟上手的部署方式，以及上线前必须知道的五件事。'
        ),
        'keywords': (
            'Go WAF,开源 WAF,反向代理 WAF,CC 防护,自托管 WAF,Coraza WAF,go:embed,'
            '单文件部署,IP 归属拦截,沃盾 warden,CC 攻击防护,轻量 WAF'
        ),
        'h1': '沃盾 warden：一个单文件部署的 Go 反向代理 WAF',
        'summary': (
            '把 L4 连接限流、频率限制、CC 挑战、IP 归属拦截和 OWASP Coraza 规则检测做进一个 '
            'Go 可执行文件，管理后台用 go:embed 内嵌。讲清它解决什么问题、为什么这么选型，'
            '以及上线前必须知道的五件事。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：warden 是给「被 CC 和扫描器困扰、但用不起商业 WAF、也不想改 DNS
  上云 WAF」的小站准备的自托管方案——一个二进制丢到服务器上，把 Nginx 的流量指过去就行。
  当前版本 <b>v1.0.1</b>，Apache-2.0 开源，支持 Windows / Linux（amd64 + arm64）。</p>
</blockquote>

<h2>一、它要解决的是什么问题</h2>
<p>企业官网、学校站点、内网业务系统这类小站，常年被两类流量消耗：</p>
<ol>
  <li><b>CC / 爬虫刷量</b>：大量 IP 高频请求热点页面（新闻列表、详情页、搜索接口），
      请求单看每一个都「合法」，合起来把后端打满；</li>
  <li><b>扫描器探测</b>：<code>/wp-admin</code>、<code>/.env</code>、<code>/phpmyadmin</code>
      这类路径扫描，以及 sqlmap、nikto 等工具的特征流量。</li>
</ol>
<p>可选的现成方案各有各的别扭：商业 WAF 贵；云 WAF 要改 DNS 解析、流量要绕一圈；
Nginx 原生的 <code>limit_req</code> 能做限速，但在<b>「怎么区分正常用户和脚本」</b>这件事上手段有限——
限速要么放行要么拒绝，没有中间态。</p>
<p>warden 的定位是：<b>用一个小巧的自托管程序，把 L4~L7 的防护 + CC 挑战 + 可观测性一次性解决</b>。
它的核心设计取向是「宁可多一次验证码，也不要误杀真实用户」——疑似脚本先弹验证码，
验证通过就发可信凭证，之后走快路径。</p>

<h2>二、三个为了「好部署」的选型</h2>
<p>这个项目最值得说的其实不是功能，而是它把部署复杂度压到了什么程度。</p>
<h3>1. 前端用 go:embed 打进二进制</h3>
<p>管理后台是 Vue3 + Element Plus + ECharts 写的单文件应用，但通过
<code>go:embed</code> 直接编进可执行文件，<b>不需要额外部署前端、不需要 Nginx 配静态目录</b>。
第三方库也全部本地化放在 <code>web/vendor/</code>，不走 CDN——内网、离线环境照常打开。</p>
<pre><code>// 改完 web/admin.html 重新 go build 即可，资源自动打进二进制
go build -o warden ./cmd/warden</code></pre>
<h3>2. SQLite 用纯 Go 实现，不需要 cgo</h3>
<p>用的是 <code>modernc.org/sqlite</code> 而不是需要 cgo 的 mattn 版本。带来的直接好处是
<b>交叉编译没有负担</b>：在 Windows 上直接编出 Linux 产物，不需要装交叉工具链。</p>
<pre><code>CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -o warden-linux-arm64 ./cmd/warden</code></pre>
<p>发布包一个 zip 同时含 <code>warden.exe</code>（Windows/amd64）、<code>warden</code>（Linux/amd64）、
<code>warden-linux-arm64</code> 三个产物，平铺在根目录，<code>run.sh</code> 按
<code>uname -m</code> 自动挑对应的二进制。</p>
<h3>3. 所有内存状态都有 TTL 和清扫协程</h3>
<p>令牌桶、可信 IP、行为状态、违规记录全部带过期时间和后台清扫，长时间运行不会无界增长。
这是自托管程序能不能「丢上去就忘了」的前提。</p>

<h2>三、请求是怎么走一遍的</h2>
<pre><code>客户端 ──▶ [Nginx / LB，可选] ──▶ warden :81 ──▶ 业务后端 :8002</code></pre>
<p>warden 内部分两层：</p>
<p><b>TCP 层</b>：<code>ConnLimitListener</code> 在 <code>accept</code> 阶段用令牌桶限流，
超额的<b>直接丢弃，根本不进入 HTTP 处理</b>——这一层挡的是最消耗资源的连接洪水。</p>
<p><b>HTTP 中间件链</b>，由外到内七道：</p>
<pre><code>1. IP 黑名单      ── 命中 → 拦截
2. URL 白/黑名单  ── 命中 → 放行 / 拦截
3. IP 白名单      ── 命中 → 直通（跳过后续所有检测）
4. CC 防护        ── 泛洪 / 行为 / 限速 → 验证码挑战
5. 频率限制       ── 热点 / 整站 / 子网 → 429
6. Coraza WAF     ── OWASP CRS 规则检测
7. 多站点 Router  ── 按 Host 反代到上游</code></pre>
<p>顺序本身就是策略：白名单在最前面直通，<b>代价高的检测（Coraza）放在后面</b>，
能被前面拦掉的流量不会走到规则引擎。</p>

<h2>四、CC 防护怎么判断「这是脚本」</h2>
<p>这是 warden 与「单纯限速」最大的区别。它不靠单一阈值，而是几条线索叠加：</p>
<table>
  <tr><th>手段</th><th>判断依据</th></tr>
  <tr><td>新 IP 泛洪检测</td><td>滑动窗口统计新 / 老 IP 占比，超过阈值判定泛洪，新 IP 一律先过验证码</td></tr>
  <tr><td>行为检测</td><td>请求间隔高度均匀、或长期只访问 1~2 个路径 → 判为脚本</td></tr>
  <tr><td>可信 IP 快路</td><td>累计访问达阈值即晋升可信，走独立高配额通道；可信列表持久化到 SQLite</td></tr>
  <tr><td>可信会话快路</td><td>验证码通过后签发 Cookie，同一 IP 下多用户互不影响</td></tr>
  <tr><td>每 IP 限速</td><td>未可信 IP 独立令牌桶，超限<b>弹验证码而不是直接断连</b></td></tr>
  <tr><td>共享令牌桶</td><td>未可信总量保护，拥堵时用验证码自我恢复</td></tr>
</table>
<p>几个细节能看出它是真在真实攻击里打磨过的：</p>
<ul>
  <li><b>静态资源免检</b>：图片 / JS / CSS / 字体直接放行，避免「一篇文章几十个请求」被误伤；</li>
  <li><b>验证码按 (会话, IP) 复用</b>：不会重复生成把用户正在填的验证码冲掉；</li>
  <li><b>爬虫白名单</b>：识别搜索引擎 UA，不弹验证码（改走限速），不影响收录；</li>
  <li><b>违规升级要双条件</b>：违规次数达标 <b>且</b> 持续违规超过 <code>offender_persist_sec</code>
      才升级为内核层封禁——避免一次性 IP 也建规则，把系统防火墙规则表撑爆。</li>
</ul>
<p>此外还有基于离线 xdb 库的 <b>IP 归属拦截</b>：可分别开关「国外 IP」与「云厂商 / IDC IP」。
真实用户几乎不会来自腾讯云、阿里云机房，这个开关对刷量特别有效，且<b>无外部请求</b>，
不依赖第三方 API。</p>

<h2>五、三分钟上手</h2>
<p>不需要编译的话，直接用 Release 里的 zip：</p>
<pre><code>mkdir -p /opt/warden &amp;&amp; cd /opt/warden
unzip ~/warden-v1.0.1.zip
chmod +x run.sh warden warden-linux-arm64   # zip 不保留可执行位
./run.sh</code></pre>
<p>要自己编译的话（Go 1.23+）：</p>
<pre><code># Windows
$env:GOPROXY = "https://goproxy.cn,https://goproxy.io,direct"
go mod tidy
go build -o warden.exe ./cmd/warden

# Linux
export GOPROXY=https://goproxy.cn,https://goproxy.io,direct
go build -o warden ./cmd/warden
./warden -config config.json</code></pre>
<p>最小配置只要两行，把自己放在业务前面：</p>
<pre><code>{
  "listen": ":81",
  "backend": "http://127.0.0.1:8002"
}</code></pre>
<p>验证：</p>
<pre><code>curl http://127.0.0.1:81/healthz   # 健康检查
curl -I  http://127.0.0.1:81/      # 应转发到后端</code></pre>
<p>管理后台默认 <code>http://127.0.0.1:9090</code>，能看到实时拦截指标、QPS / 拦截率趋势、
拦截分类占比、CPU / 内存、攻击日志分页查询与可信 IP 列表。</p>
<p>三种部署形态按需要选：</p>
<table>
  <tr><th>方案</th><th>链路</th><th>适用</th></tr>
  <tr><td>A. Nginx 前置（推荐）</td><td>:443 → Nginx(TLS 卸载) → warden:81 → 后端</td><td>需要 TLS、已有 Nginx</td></tr>
  <tr><td>B. WAF 直接对外</td><td>:80 → warden → 后端</td><td>想少一跳（Windows 下监听 80 需管理员）</td></tr>
  <tr><td>C. 多站点</td><td>按 Host 路由到不同上游</td><td>一台机器反代多个站点</td></tr>
</table>
<p>长期跑就用 systemd（Linux）或 NSSM（Windows）注册成服务，README 里有现成的 unit 文件。</p>

<h2>六、上线前必须知道的五件事</h2>
<h3>1. 先用 DetectionOnly 观察，再切 On</h3>
<p>把 <code>rules/coraza.conf</code> 里的 <code>SecRuleEngine</code> 设成
<code>DetectionOnly</code>，先观察一段时间有没有误报，确认真实业务不受影响后再改成 <code>On</code>。
CC 防护同理：先只开验证码挑战，看真实用户的通过率，再逐步收紧阈值。
<b>直接开 On 上线是 WAF 误杀的头号原因。</b></p>
<h3>2. 改 config.json 不会生效</h3>
<p>配置读取顺序是 <b>SQLite config 表 → 回退 config.json</b>。首次启动会用 config.json
初始化数据库，之后<b>一律以 DB 为准</b>。请在管理后台修改并重启。</p>
<h3>3. Windows 版 Nginx 有 1024 连接上限</h3>
<p>Windows 版 Nginx 用 <code>select()</code> 事件模型，单 worker 最多约 1024 并发连接，
<code>worker_connections</code> 设再大也不生效。并发较高时，把 Nginx 放到 Linux / WSL2，
或者让 warden 直接对外（Go 在 Windows 上用 IOCP，无此限制）。</p>
<h3>4. 上游 keepalive 超时要对齐</h3>
<p>warden 到后端的空闲连接回收时间要<b>短于</b>后端（如 Tomcat 的 <code>connectionTimeout</code>），
否则会复用已被后端关闭的连接，触发 <code>connection reset</code> → 间歇 502。</p>
<h3>5. 防火墙封禁默认关闭，别急着开</h3>
<p>早期版本会为每个 IP 创建 in/out 两条 <code>netsh</code> 规则，攻击量下能迅速累积到上万条，
而 Windows 防火墙每次增删规则都要重编译整张规则表，操作会越来越慢。
所以现在<b>默认关闭</b>，要开就得配合定期清理。</p>

<h2>七、两个有意思的工程细节</h2>
<p>管理后台和 WAF 跑在<b>同一个进程</b>里，所以轮询开销直接叠加在业务上，这两处做了优化：</p>
<ul>
  <li><b>读内存不用 <code>runtime.ReadMemStats</code></b>：它会触发 STW 停顿，实测单次约
      8.7µs；改用 <code>runtime/metrics</code> 读同样指标仅约 0.3µs（快约 27 倍），
      而取值一致。前端是按 3 秒轮询 <code>/api/stats</code> 的，这个差别会被放大。</li>
  <li><b>CPU 使用率常驻采样</b>：<code>GetSystemTimes</code> / <code>/proc/stat</code> 给的是
      自开机以来的累计值，必须两次采样求差。若只在接口被请求时才采样，离开仪表盘再切回来，
      第一次读数会是整段空档的平均值（可能是几分钟）。所以后台以 1 秒间隔常驻采样并缓存，
      接口只读缓存。</li>
</ul>

<h2>八、适合谁，不适合谁</h2>
<p><b>适合</b>：企业官网、学校 / 政府站点、内网业务系统这类「后端不太健壮、流量模式相对固定、
没人专门做安全运维」的场景；想自建、想完全掌控数据与规则的人。</p>
<p><b>不适合</b>：需要企业级规则运营、DDoS 大流量清洗（那应该在运营商 / CDN 侧做）、
或者指望装完就不管的场景。README 里也写得很清楚：这是<b>应用层防护手段</b>，
不能替代系统补丁、最小权限和后端自身的安全编码。</p>

<h2>九、项目信息</h2>
<ul>
  <li>许可证：<b>Apache-2.0</b>（含明确的专利授权，允许商业使用与闭源集成）</li>
  <li>语言 / 依赖：Go 1.23+、OWASP Coraza v3、纯 Go SQLite、Vue3 + Element Plus + ECharts</li>
  <li>当前版本：v1.0.1（跨平台单包分发）</li>
  <li>Gitee：<a href="https://gitee.com/jxw1111/warden" rel="nofollow noopener" target="_blank">gitee.com/jxw1111/warden</a></li>
  <li>GitHub：<a href="https://github.com/xwjiang2003/warden" rel="nofollow noopener" target="_blank">github.com/xwjiang2003/warden</a></li>
</ul>
<p>欢迎提交 Issue / PR，贡献默认按 Apache-2.0 授权，建议在提交信息里附
<code>Signed-off-by</code>（DCO）。</p>
''',
        'related': [
            ('Coraza 规则详解', 'blog/coraza-waf-rules/'),
            ('Go 工具链命令速查表', 'go-cheatsheet/'),
            ('gofmt 和 goimports 的区别', 'blog/gofmt-vs-goimports/'),
        ],
    },
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
