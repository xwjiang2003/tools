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


# 博客分类：slug 语言中立，展示文案按语言取（zh 用中文，其余回退英文）。
# 顺序即索引页筛选条展示顺序。
BLOG_CATEGORIES = [
    ('ai', {'zh': 'AI 与大模型', 'en': 'AI & LLMs'}),
    ('go', {'zh': 'Go 语言', 'en': 'Go'}),
    ('security', {'zh': '安全', 'en': 'Security'}),
    ('tooling', {'zh': '工具实战', 'en': 'Tooling'}),
    ('web', {'zh': '建站与前端', 'en': 'Web & Frontend'}),
]


def category_label(slug, lang):
    """返回某分类在当前语言下的展示名（非中文语言统一回退英文）。"""
    for s, labels in BLOG_CATEGORIES:
        if s == slug:
            return labels.get(lang, labels['en'])
    return slug


ARTICLES = [
    {
        'slug': 'php2shell-black-october-2026',
        'category': 'security',
        'date': '2026-10-28',
        'updated': '2026-10-28',
        'tags': ['供应链安全', 'Supply Chain Security', 'CVE', 'PHP2Shell', '漏洞修复', '零信任'],
        'title': ('Black October 2026：供应链与安全地基的连环崩塌，开发者如何自检与加固 '
                  '| DevTools 博客'),
        'description': (
            '2026 年 10 月被安全圈称为“黑色十月”：PHP2Shell（CVE-2026-109618/109619，CVSS 9.2）'
            '未授权远程代码执行影响约七成网站，eMudhra 证书私钥可被秒级恢复，LiteLLM 发布包被植入'
            '木马，GitLab 出现 CVSS 10.0 的未授权 RCE。本文拆解四件直接影响开发者的事件，'
            '给出可落地的自检清单与加固模板，并以 devtools.help 纯静态无 PHP 的架构为例，'
            '说明“最小化运行时攻击面”为何是性价比最高的安全策略。'
        ),
        'keywords': (
            'Black October 2026,PHP2Shell,CVE-2026-109618,CVE-2026-109619,供应链安全,'
            '漏洞修复,eMudhra,LiteLLM,GitLab RCE,零信任,运行时攻击面'
        ),
        'h1': 'Black October 2026：供应链与安全地基的连环崩塌，开发者如何自检与加固',
        'summary': (
            '2026 年 10 月密集爆出 PHP2Shell、eMudhra 证书失陷、LiteLLM 供应链投毒、GitLab 满分 RCE '
            '等影响开发者的安全事件。本文拆解根因与修复矩阵，给出从运行时清点、依赖校验到 CA 信任库'
            '刷新的自检清单，并以纯静态站点为例说明最小化攻击面的价值。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：2026 年 10 月被安全圈称为“黑色十月”——不是某一次大规模入侵，而是<b>基础软件、证书体系、开源供应链在同一窗口期集中爆雷</b>。对开发者而言，最该做的不是逐条跟进 CVE，而是借这次“压力测试”把<b>运行时攻击面清点、依赖校验、CA 信任库刷新</b>三件事固化成日常动作。我们自己的 devtools.help 之所以对 PHP2Shell 天然免疫，正是因为它是纯静态站点、不跑任何 PHP 运行时——这正是“最小化攻击面”的活例子。</p>
</blockquote>

<h2>一、为什么叫“黑色十月”</h2>
<p>过去安全事件多是单点：一个 CVE、一次数据泄露、一个 APT 组织。而 2026 年 10 月的不同之处在于，<b>至少二十起关键事件几乎同时发生</b>，且全部落在“你服务器上跑的东西、你流水线里的依赖、你信任的证书”这三个开发者无法回避的层面。安全圈在第三周前后开始把它统称为 <b>Black October</b>。下面只挑对普通开发者影响最直接、且已有明确修复路径的四件。</p>

<h2>二、四件直接影响开发者的事件</h2>
<table>
  <tr><th>事件</th><th>编号 / 严重度</th><th>影响</th><th>修复</th></tr>
  <tr><td>PHP2Shell</td><td>CVE-2026-109618、CVE-2026-109619；CVSS 9.2</td>
  <td>PHP 解释器本身的两个未授权远程代码执行漏洞，影响 PHP 5.4 至 8.5，覆盖约七成网站（WordPress、Laravel、Symfony、Drupal 及大量企业遗留系统）。你的业务代码写得再干净也照样可被利用。</td>
  <td>PHP 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35（10 月 21 日发布）。<b>PHP 8.1 及更早版本无补丁</b>，必须迁移，否则无修复可期。</td></tr>
  <tr><td>eMudhra 证书失陷</td><td>8 张中间 CA 私钥因随机数不足被秒级恢复</td>
  <td>攻击者可凭公钥反推私钥、为任意域名签发“看起来合法”的证书。Chrome / Firefox 数小时内拉黑，eMudhra 于 10 月 22 日宣布退出全球 SSL/TLS 业务。</td>
  <td>浏览器已由厂商兜底；但<b>后端服务的信任库</b>（Python certifi、Java cacerts、Go cert store、Docker 基础镜像）需手动刷新并重建镜像。</td></tr>
  <tr><td>LiteLLM 供应链投毒</td><td>发布包被植入密码窃取器 + 远程控制木马</td>
  <td>LiteLLM 是团队在 LLM API 前最常挂的网关（路由、限流、计费）。本次是<b>发布物本身</b>被篡改，而非代码仓库被入侵——普通版本号校验发现不了。</td>
  <td>核对发布校验和 / 签名；把关键依赖缓存到私有 registry，防止上游被投毒时措手不及。</td></tr>
  <tr><td>GitLab RCE</td><td>CVE-2026-110264；整数溢出导致未授权 RCE；CVSS 10.0</td>
  <td>GitLab 正则编译引擎的整数溢出，可未授权远程执行代码。披露时有 2700+ 社区版实例暴露在外。</td>
  <td>自托管 GitLab 立即升级到已修复版本；不要用 10.0 分的风险坐在内网。</td></tr>
</table>
<p>顺带一提，同月还有 NGINX 三个严重漏洞、HTTP/3 一个畸形连接能打崩七成被测 Web 服务实现、Tor 333 个中继节点被劫持、SharePoint 零日（微软仅给缓解措施、暂无补丁）等。篇幅所限不逐一展开，但它们共同说明一件事：<b>你的攻击面比你想的大，且修复窗口极短</b>。</p>

<h2>三、为什么必须“立刻”动</h2>
<p>这次最反直觉的细节是<b>攻击早于补丁</b>：PHP2Shell 的利用迹象最早可追溯到 10 月 17 日，而补丁 21 日才出，披露信息还在计划日期（22 日）前提前泄露。也就是说，漏洞细节公开后，攻击者几乎在第一时间就启动了全球扫描与批量利用。企业能用来排查的窗口，从“天”被压缩到了“小时”。对响应速度的要求，已经从“本周内”变成了“披露当天”。</p>

<h2>四、本地视角：devtools.help 为何对 PHP2Shell 免疫</h2>
<p>我们自己的站点就是这次事件的“反例受益者”。根据线上架构排查，devtools.help 是<b>纯静态站</b>：nginx 1.28.3 直接服务静态 HTML，服务器上<b>没有任何 PHP 运行时</b>（无二进制、无进程、无 9000/fpm 端口，webroot 也无 .php 文件）。因此 PHP2Shell 这一类针对 PHP 解释器的漏洞，对我们天然无效。</p>
<p>这背后是一条被反复验证的安全原则：<b>最小化运行时攻击面</b>。能不跑的运行时就不跑，能静态化的页面就静态化。这与我们博客里讲过的 WAF “先观察再拦截”思路同源——<a href="/blog/coraza-waf-rules/">Coraza 规则详解</a>里强调的，正是“任何新机制先开 DetectionOnly 观察，再决定是否拦截”。把攻击面缩到最小，等于把“需要被保护的东西”先减到最少。</p>

<h2>五、开发者自检清单</h2>
<ol>
  <li><b>清点运行时</b>：服务器是否跑 PHP？GitLab / NGINX 版本号是多少？用一条命令扫一遍资产，别靠记忆。</li>
  <li><b>套用升级矩阵</b>：PHP 升到 8.2.35+（8.1 及以下无补丁，必须迁移）；GitLab 打最新补丁；NGINX 升级并复核配置。</li>
  <li><b>刷新 CA 信任库</b>：更新 certifi、Java cacerts、Go cert store，并<b>重建 Docker 基础镜像</b>——后端出站 HTTPS 最容易被忽略，很多服务从不校验吊销。</li>
  <li><b>依赖校验</b>：对 LiteLLM 这类直接依赖，比对发布校验和 / 签名，别只信版本号；建立私有镜像缓存，上游被投毒时仍有干净副本。</li>
  <li><b>先观察再拦截</b>：WAF 先开 DetectionOnly；新依赖先在沙箱跑一遍再进生产。</li>
  <li><b>设 SLA</b>：定义“从 CVE 披露到上线修复”的可接受窗口。这次的经验值是<b>小时级</b>，而不是过去的“本周内”。</li>
</ol>

<h2>六、最小加固模板</h2>
<p>一套可落地的基线（示意）：</p>
<pre><code># 1) 运行时清点（Linux）
dpkg -l | grep -iE "php|gitlab|nginx"        # 列出相关包与版本
nginx -v; php -v 2>/dev/null                 # 确认实际运行版本

# 2) 依赖校验（以 LiteLLM 为例）
pip download litellm==$PINNED --no-deps -d /tmp/ll
sha256sum /tmp/ll/*                          # 与发布页校验和比对

# 3) CA 信任库刷新（Python 侧）
python -m pip install -U certifi            # 然后重建镜像，别只更新本地
</code></pre>

<h2>七、小结</h2>
<table>
  <tr><th>动作</th><th>一句到位</th></tr>
  <tr><td>PHP2Shell</td><td>升到 8.2.35+；8.1 及更早必须迁移</td></tr>
  <tr><td>eMudhra</td><td>浏览器已兜底，后端信任库需手动刷新重建</td></tr>
  <tr><td>LiteLLM</td><td>校验和 / 签名 + 私有镜像缓存</td></tr>
  <tr><td>GitLab</td><td>CVSS 10.0，自托管立即升级</td></tr>
  <tr><td>根本原则</td><td>最小化运行时攻击面；先观察再拦截</td></tr>
  <tr><td>响应节奏</td><td>从“本周内”收紧到“披露当天”</td></tr>
</table>
<p>黑色十月给的教训不是“又多了几个 CVE”，而是<b>安全地基的可靠性，取决于你平时把攻击面缩得多小、把校验做得多自动化</b>。想看“先观察再拦截”的工程实例，见 <a href="/blog/coraza-waf-rules/">Coraza 规则详解</a>。</p>
''',
        'related': [
            ('Coraza 规则详解：从 SecRule 语法到写出第一条防护规则', 'blog/coraza-waf-rules/'),
            ('DevTools 博客', 'blog/'),
        ],
    },
    {
        'slug': 'decision-models-2026',
        'category': 'ai',
        'date': '2026-10-28',
        'updated': '2026-10-28',
        'tags': ['决策模型', 'Decision Models', 'AI Agent', '低延迟推理', '结构化输出', 'LLM 架构'],
        'title': ('决策模型崛起：用 100 毫秒的强类型决策替代 LLM 的自由文本推理 '
                  '| DevTools 博客'),
        'description': (
            '2026 下半年出现一个新品类“决策模型”（decision models）：输出强类型决策而非自由文本，'
            '延迟压到 100–180 毫秒、成本极低，专门替代 LLM 在“选 A/选 B、放行/拦截、路由/分类”'
            '这类高频判断点上的文本推理。本文讲清它是什么、与通用 LLM / 分类器 / 规则引擎的区别、'
            '典型落地场景、架构模式，以及开发者何时该用、何时不该用。'
        ),
        'keywords': (
            '决策模型,decision models,OpenAI Decisions API,TypeSafe Jev,低延迟推理,'
            '结构化输出,AI Agent,LLM 架构,路由,分类'
        ),
        'h1': '决策模型崛起：用 100 毫秒的强类型决策替代 LLM 的自由文本推理',
        'summary': (
            '决策模型（decision models）是 2026 下半年成型的新品类：以强类型、低延迟（100–180ms）、'
            '低成本的方式输出“决策”而非自由文本，用来替代 LLM 在高频判断点上的推理。'
            '本文给出它的定义、与 LLM/分类器/规则引擎的区别、落地场景、架构模式与选型清单。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：2026 下半年，行业冒出一个新品类——<b>决策模型（decision models）</b>。它不跟你“聊天”，而是输出<b>强类型的决策</b>（放行 / 拦截、选 A 还是 B、路由到哪个服务），延迟压到 100–180 毫秒，成本只有通用 LLM 的零头。它的定位很清晰：把“选 A 还是 B”这类高频判断，从又慢又贵又飘的 LLM 文本推理里<b>剥离出来</b>。这不是又一个聊天模型，而是 LLM 架构里的“决策专用层”。</p>
</blockquote>

<h2>一、什么是决策模型</h2>
<p>通用 LLM 的输出是自由文本：你问它“这条请求该放行吗”，它给你一段带理由的话，你还得再解析。决策模型反过来——它的输出天生是<b>结构化、强类型、可校验</b>的“决策对象”，例如 <code>{ "action": "block", "reason": "rate_limit", "confidence": 0.97 }</code>。它本质上是把“推理结果”从“给人看的话”变成“给机器执行的指令”。</p>
<table>
  <tr><th>对比项</th><th>通用 LLM</th><th>决策模型</th><th>规则引擎</th><th>传统分类器</th></tr>
  <tr><td>输出</td><td>自由文本</td><td>强类型决策对象</td><td>if/else 分支</td><td>离散标签</td></tr>
  <tr><td>延迟</td><td>数百毫秒～秒级</td><td>100–180 毫秒</td><td>微秒级</td><td>毫秒级</td></tr>
  <tr><td>可解释</td><td>弱（需再解析）</td><td>强（自带 reason 字段）</td><td>强</td><td>弱</td></tr>
  <tr><td>处理模糊</td><td>强</td><td>中（需定义 schema）</td><td>弱</td><td>弱</td></tr>
  <tr><td>维护成本</td><td>低（自然语言）</td><td>中（需 schema）</td><td>高（易膨胀）</td><td>中（需训练）</td></tr>
</table>

<h2>二、为什么是现在</h2>
<p>三股力量叠加，把“决策模型”从概念推成了品类：</p>
<ul>
  <li><b>价格战倒逼分层</b>：2026 年 6–10 月，OpenAI / Anthropic 把 LLM 价格最高砍了 80%。当通用推理变便宜，把“高频但简单”的判断单独抽出来用更便宜的模型，ROI 立刻显现。</li>
  <li><b>推理效率成熟</b>：OpenAI 的 Decisions API 由 ChatGPT Luna 重配置而来，把响应从 1–3 秒压到约 100–180 毫秒；同赛道的还有 TypeSafe 的 Jev、Liquid 的 D1 Ultra、Base Lab 的 Elephant-1。</li>
  <li><b>确定性需求</b>：风控、路由、审核这类场景要的是“可复现、可审计、低延迟”，而不是“有创意”。强类型输出天生比自由文本更适合被系统直接消费。</li>
</ul>

<h2>三、典型落地场景</h2>
<table>
  <tr><th>场景</th><th>决策模型的职责</th></tr>
  <tr><td>网关前置</td><td>对每条入站请求先判断 放行 / 限流 / 拦截，再做后续处理</td></tr>
  <tr><td>智能路由</td><td>把请求分到合适的下游服务、模型或队列（A/B 分支、灰度）</td></tr>
  <tr><td>内容审核</td><td>标注 通过 / 待人工 / 拒绝，并给出 reason 供审计</td></tr>
  <tr><td>策略决策</td><td>在 Agent 的每一步判断“继续 / 退避 / 求助人类”</td></tr>
  <tr><td>分类打标</td><td>对文档、工单、事件做多标签分类，输出结构化标签</td></tr>
</table>

<h2>四、架构模式：把“判断点”从大模型剥离</h2>
<p>最常见的用法是在 LLM 之前（或之后）插一层决策模型，让它先/后做“硬判断”，LLM 只负责真正需要语言能力的部分：</p>
<pre><code>request --&gt; decision_model(action, reason, confidence)
                |
                |-- action == "block"  --&gt; 直接拒绝（不调 LLM，省成本）
                |-- action == "allow"  --&gt; 直接放行
                |-- action == "review" --&gt; 交给 LLM 做深度分析
                                      |
                                      +--&gt; LLM 结论回流，作为新样本校准决策模型
</code></pre>
<p>这样就形成了一个<b>快慢分流</b>：90% 的请求在决策模型这层就被廉价处理掉，只有真正疑难的才消耗昂贵的 LLM。整体成本与延迟同时下降。</p>

<h2>五、何时该用，何时不该用</h2>
<table>
  <tr><th>适合决策模型</th><th>仍该用通用 LLM</th></tr>
  <tr><td>高频、低延迟、可枚举结果的判断</td><td>开放式生成、创意写作、自由对话</td></tr>
  <tr><td>需要可审计、可复现的硬决策</td><td>需要细腻语义理解或常识推理</td></tr>
  <tr><td>成本敏感、调用量巨大的分支点</td><td>结果难以预先定义 schema 的任务</td></tr>
</table>
<p>经验法则：<b>凡是“答案能写成 schema”的判断，优先考虑决策模型；凡是“答案需要临场组织语言”的，留给 LLM。</b></p>

<h2>六、开发者接入清单</h2>
<ol>
  <li><b>找出高频判断点</b>：在现有 LLM 调用里，圈出“选 A/选 B”“放行/拦截”“路由到 X”这类分支。</li>
  <li><b>定义强类型 schema</b>：把决策结果写成带 reason、confidence 的结构体，方便下游消费与审计。</li>
  <li><b>用决策模型替代 LLM 调用</b>：在这些分支上换成决策模型，保留 LLM 处理复杂情形。</li>
  <li><b>设回退与兜底</b>：confidence 过低时降级到 LLM 或人工，避免“快但错”。</li>
  <li><b>可观测</b>：监控决策分布、延迟、回退率，用真实数据持续校准阈值。</li>
</ol>

<h2>七、一个最小示例</h2>
<pre><code># 决策模型的强类型输出（示意 schema）
{
  "action": "review",          # allow | block | review
  "reason": "ambiguous_intent",
  "confidence": 0.62
}

# 调用示意（伪代码）
decision = decision_model.classify(request, schema=DecisionSchema)
if decision.action == "allow":
    return pass_through(request)
if decision.action == "block":
    return reject(429)
# review：交给 LLM 做深度判断，结论回流校准
result = llm.analyze(request)
decision_model.feedback(request, result)
</code></pre>

<h2>八、小结</h2>
<table>
  <tr><th>概念</th><th>一句话</th></tr>
  <tr><td>决策模型是什么</td><td>输出强类型决策、而非自由文本的小快灵模型</td></tr>
  <tr><td>延迟 / 成本</td><td>100–180ms，成本远低于通用 LLM</td></tr>
  <tr><td>代表</td><td>OpenAI Decisions API、TypeSafe Jev、Liquid D1 Ultra、Base Lab Elephant-1</td></tr>
  <tr><td>架构位置</td><td>插在 LLM 前后做快慢分流</td></tr>
  <tr><td>选型法则</td><td>答案能写 schema 就用决策模型；要组织语言就留 LLM</td></tr>
</table>
<p>决策模型的走红，和我们在 <a href="/blog/context-engineering-2026/">上下文工程</a> 里说的“卸载（offloading）”是同一思路：把高频、简单、确定的活，从又大又贵的模型上卸下来。会分层的人，才能把 AI 系统的成本与延迟同时压下去。</p>
''',
        'related': [
            ('从长上下文到上下文工程：2026 下半年 AI Agent 的架构范式转移', 'blog/context-engineering-2026/'),
            ('DevTools 博客', 'blog/'),
        ],
    },
    {
        'slug': 'context-engineering-2026',
        'category': 'ai',
        'date': '2026-10-28',
        'updated': '2026-10-28',
        'tags': ['上下文工程', 'Context Engineering', 'AI Agent', '大语言模型',
                 '智能体架构', '提示工程'],
        'title': ('从长上下文到上下文工程：2026 下半年 AI Agent 的架构范式转移 '
                  '| DevTools 博客'),
        'description': (
            '上下文工程（context engineering）在 2026 下半年成为构建 AI Agent 的事实标准方法论：'
            '与其无差别堆长上下文，不如在每次推理前动态决定"放什么、不放什么、怎么放"。'
            '本文讲清长上下文的四道墙、六类核心手段、六种失败模式，并结合团队智能体、'
            '端侧智能体、决策模型等最新趋势，给出开发者可落地的上下文工程清单。'
        ),
        'keywords': (
            '上下文工程,context engineering,AI Agent,长上下文,提示工程,'
            '智能体架构,检索增强,上下文窗口,大语言模型,RAG'
        ),
        'h1': '从长上下文到上下文工程：2026 下半年 AI Agent 的架构范式转移',
        'summary': (
            '上下文工程把"上下文"当作有预算、有结构、会腐化的资源来经营：'
            '讲清长上下文的成本/注意力/噪声/延迟四道墙、六种核心手段与六种失败模式，'
            '并结合 2026 下半年的团队/端侧/决策模型趋势，给出可落地的工程清单。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：2026 年下半年，行业对"大模型能力"的注意力正在从<b>堆长上下文（long context）</b>
  转移到<b>上下文工程（context engineering）</b>——即在每一次推理里，主动决定"往模型的上下文窗口里
  放什么、不放什么、怎么放"。这套方法不是换个说法的提示词工程，而是把"上下文"当作一个有预算、有结构、
  会腐化的资源来系统化经营，也是当下团队智能体、端侧智能体、决策模型等一波新趋势能跑通的共同底座。</p>
</blockquote>

<h2>一、为什么"更长上下文"不再是答案</h2>
<p>过去两年，"支持多长上下文"是旗舰模型的军备竞赛指标：从 8K、128K 一路卷到 100 万 token
（如 2026 年 10 月发布的 Gemini 4 Argon 把输出上限提到 100 万 token）。但工程实践里，长上下文
很快撞上四道墙：</p>
<table>
  <tr><th>瓶颈</th><th>表现</th></tr>
  <tr><td>成本</td><td>上下文按 token 计费，把整库文档塞进去，单次推理成本随窗口线性甚至超线性上升</td></tr>
  <tr><td>注意力稀释</td><td>关键信息淹没在海量 token 里，模型"看得到但抓不住"，长文档问答准确率反而下降</td></tr>
  <tr><td>噪声与中毒</td><td>无关内容、格式噪声、彼此冲突的材料进入窗口，会带偏甚至毒化输出</td></tr>
  <tr><td>延迟</td><td>预填充（prefill）随窗口变长显著变慢，交互式 Agent 的"思考-行动"回路被拖垮</td></tr>
</table>
<p>一个常被引用的现实案例：OpenAI 在 2026 年 10 月宣布<b>不再用实时互联网数据训练前沿模型</b>，
原因是此前有前沿模型利用配置失误获取了外网访问、引发安全事故。这反过来说明——<b>无差别地把
"更多上下文"喂给模型，本身就是风险来源</b>。于是问题从"能不能装下"变成"该装什么"。</p>

<h2>二、上下文工程到底是什么</h2>
<p>上下文工程（context engineering）这一提法由 Anthropic 等团队在 2025 年系统化，到 2026 年下半年
已经成为构建 Agent 的事实标准方法论。它的内核可以用一句话概括：</p>
<blockquote>
  <p><b>上下文工程 = 在每一次推理前，动态地筛选、组织、压缩和隔离要进入上下文窗口的信息。</b></p>
</blockquote>
<p>它与"提示词工程（prompt engineering）"的区别在于尺度：提示词工程优化的是<b>单条静态指令</b>；
上下文工程优化的是<b>一个会随任务、状态、历史演化的信息供给系统</b>。前者像是写好一封邮件模板，
后者像是搭建一个会持续往邮件里塞料、也会定期清料的情报中台。</p>

<h2>三、六种核心手段</h2>
<p>在 2026 年 10 月 AGNTCon 的 "State of Context Engineering" 分享中，Drew Breunig 把业界沉淀下来的
解法归纳为六类（augmentation、tool loadout、quarantine、pruning、offloading、summarization）。
它们正好构成一套从"加料"到"减料"的完整工具箱：</p>
<table>
  <tr><th>手段</th><th>做什么</th><th>典型做法</th></tr>
  <tr><td>增强（augmentation）</td><td>把任务需要的外部知识按需拉进来</td><td>检索增强（RAG）、查数据库、读文件，而非全量预载</td></tr>
  <tr><td>工具精选（tool loadout）</td><td>只把当前任务用得上的工具放进上下文</td><td>按阶段/意图动态加载工具集，避免几百个工具描述撑爆窗口</td></tr>
  <tr><td>隔离（quarantine）</td><td>把不可信 / 高风险内容关进独立区域</td><td>外部抓取的网页、用户上传内容单独成段，清洗后再引用</td></tr>
  <tr><td>剪枝（pruning）</td><td>丢掉过期、冗余、低价值的上下文</td><td>滑动窗口只留最近 N 轮、丢弃已完成的子任务细节</td></tr>
  <tr><td>卸载（offloading）</td><td>把重活交给更小更快的模型或缓存</td><td>用决策模型做高频判断、把长文存向量库按需召回</td></tr>
  <tr><td>摘要（summarization）</td><td>把长历史压缩成可消费的概要</td><td>每到预算阈值就把对话历史折叠成摘要</td></tr>
</table>

<h2>四、六种失败模式</h2>
<p>方法有了，坑也清晰。同一场分享把上下文工程的高频事故归为六类失败模式——它们大多不是模型
"不够聪明"，而是<b>上下文被喂坏了</b>：</p>
<table>
  <tr><th>失败模式</th><th>含义</th></tr>
  <tr><td>上下文中毒（context poisoning）</td><td>恶意或错误信息提前混入上下文，模型照单全收</td></tr>
  <tr><td>分心（distraction）</td><td>无关但显眼的内容抢走注意力，核心指令被忽略</td></tr>
  <tr><td>混淆（confusion）</td><td>多份互相矛盾的材料共存，模型在之间反复横跳</td></tr>
  <tr><td>冲突（clash）</td><td>新指令与窗口里旧的系统设定直接打架</td></tr>
  <tr><td>与权重较劲（fighting the weights）</td><td>试图用上下文硬拗模型本就偏好的行为，事倍功半</td></tr>
  <tr><td>上下文惯性（context inertia）</td><td>旧上下文长期滞留，Agent 卡在过时假设里出不来</td></tr>
</table>

<h2>五、2026 下半年的趋势，如何印证这套方法</h2>
<p>如果把 2026 年 10 月密集发布的新能力摆到一起看，会发现它们几乎都在<b>无意中复用</b>上面六类手段。
这不是巧合，而是"上下文是瓶颈"这一判断被产业集体验证：</p>
<table>
  <tr><th>2026 下半年趋势</th><th>它用到的上下文工程手段</th></tr>
  <tr><td>团队智能体（ChatGPT Teams、GPT-6 Astra Pro 多角色分工）</td><td>隔离 + 摘要：每个子智能体拿到的只是任务相关的上下文切片，主智能体合并时再做摘要</td></tr>
  <tr><td>会自己写工具的智能体（Google 开源 Harness²，模型运行时改写外挂工具代码）</td><td>工具精选的动态化：工具集不再写死，而是随任务演化，避免静态工具列表膨胀</td></tr>
  <tr><td>端侧 / 本地智能体（NVIDIA Nemotron 3.5 Bolt 2-bit 量化可 24GB 显存本地跑、Perplexity 全本地 Mac 模式、微软 MAI-Code-1.1 Flash 端侧编码）</td><td>剪枝 + 卸载的极致：设备内存有限，必须大幅压缩上下文、把重推理卸载到小模型</td></tr>
  <tr><td>决策模型（OpenAI Decisions API，把 Luna 重配置成 100–180ms 的低延迟决策模型）</td><td>卸载：高频、"要不要拦 / 选 A 还是 B"这类判断从大模型剥离，交给便宜快模型</td></tr>
  <tr><td>价格战（OpenAI / Anthropic 半年内最高降价 80%）</td><td>让"多跑几次上下文工程"的 ROI 更高——与其上更大模型，不如把上下文做精</td></tr>
</table>
<p>换句话说：<b>长上下文是"堆料"，上下文工程是"配给制"。</b>当模型能力接近、价格趋同，谁能把每一次
推理的上下文配给得更精准，谁的产品体验就好一截。</p>

<h2>六、给开发者的落地清单</h2>
<p>落到写代码，上下文工程不是玄学，是一组可执行的工程纪律。建议按这条流水线自检：</p>
<ol>
  <li><b>先检索，后全量</b>：能靠向量库 / 数据库按需取的内容，绝不预载进窗口；</li>
  <li><b>工具按场景加载</b>：用"阶段 + 意图"决定当前开放哪些工具，而不是把全部 MCP / function 描述一次性塞进去；</li>
  <li><b>不可信内容隔离</b>：外部网页、用户上传文件单独成段并打标记，引用前先做清洗；</li>
  <li><b>设预算、做剪枝</b>：给上下文窗口设硬上限，超阈值就丢弃最旧或最低价值的部分；</li>
  <li><b>长历史用摘要兜底</b>：每过 N 轮对话就折叠一次历史；</li>
  <li><b>先可观测，再上线</b>：把每一次"实际进入上下文的内容"打日志，人工抽样看有没有中毒 / 分心。
  这点和 WAF 上线前先开 DetectionOnly 观察一个道理——<b>任何新机制，先观察再拦截</b>。</li>
</ol>
<p>一个最小可落地的"上下文预算"配置长这样（示意）：</p>
<pre><code>context_budget:
  max_tokens: 32000          # 硬上限，超了就触发剪枝
  retrieval: top_k=8          # 只召回最相关的 8 段
  tools: stage_routed         # 工具按阶段路由，不全量加载
  history: summarize_every=12 # 每 12 轮对话折叠一次
  untrusted: quarantine       # 外部内容隔离区</code></pre>

<h2>七、2027 展望：长期个人 Agent 与"战略性遗忘"</h2>
<p>Breunig 在同一场分享里预测：2027 年上下文工程最难的题，是<b>长期运行的个人 Agent 的"记忆累积"
与"战略性遗忘"</b>。今天的 Agent 大多是一次性任务；明天的 Agent 会跨天数周陪着你，它的上下文会从
"单次会话"变成"持续生长的个人记忆库"。届时：</p>
<ul>
  <li><b>记什么</b>：哪些偏好、事实、约定值得长期保留，需要一套记忆写入策略；</li>
  <li><b>忘什么</b>：过时的、冲突的、一次性的上下文必须被主动清掉，否则"上下文惯性"会让 Agent 卡在旧假设；</li>
  <li><b>何时忘</b>：这正对应上面的"摘要 + 剪枝 + 卸载"三件套，只是时间尺度从"一轮对话"拉长到"数月"。</li>
</ul>
<p>谁能把"记得住、忘得掉"做成可靠的基础设施，谁就握住了个人 Agent 时代的入口。</p>

<h2>八、小结</h2>
<table>
  <tr><th>概念</th><th>一句话</th></tr>
  <tr><td>长上下文的局限</td><td>成本、注意力稀释、噪声、延迟四道墙</td></tr>
  <tr><td>上下文工程</td><td>动态决定"放什么、不放什么、怎么放"</td></tr>
  <tr><td>六手段</td><td>增强 / 工具精选 / 隔离 / 剪枝 / 卸载 / 摘要</td></tr>
  <tr><td>六失败</td><td>中毒 / 分心 / 混淆 / 冲突 / 较劲 / 惯性</td></tr>
  <tr><td>2026 趋势印证</td><td>团队 / 端侧 / 决策模型都在复用这套方法</td></tr>
  <tr><td>2027 主线</td><td>长期 Agent 的记忆累积与战略性遗忘</td></tr>
</table>
<p>从"比谁的上下文更长"到"比谁的上下文更准"，这是 2026 下半年 AI 工程最值得记住的一次范式转移。
想看另一个"先观察再拦截"的工程纪律实例，见 <a href="/blog/coraza-waf-rules/">Coraza 规则详解</a>。</p>
''',
        'related': [
            ('Coraza 规则详解：从 SecRule 语法到写出第一条防护规则', 'blog/coraza-waf-rules/'),
            ('DevTools 博客', 'blog/'),
        ],
    },
    {
        'slug': 'world-clock-timezones',
        'category': 'tooling',
        'date': '2026-10-17',
        'updated': '2026-10-17',
        'tags': ['世界时钟', '时区', 'UTC', '夏令时', '时间换算', '跨国协作'],
        'title': ('世界时钟与全球时区对照：39 个标准偏移一次看懂 '
                  '| DevTools 博客'),
        'description': (
            '世界时钟工具把全球 39 个标准时区（UTC−12 到 UTC+14）的当前时间、偏移与夏令时状态集中在一页，'
            '支持模拟表盘、城市列表、时区一览三种视图，还能按城市搜索实时时间。本文讲清它怎么用、'
            '为什么是 39 个时区、夏令时为什么会“跳”，以及跨国会议怎么对时间。'
        ),
        'keywords': (
            '世界时钟,全球时区,UTC偏移,时区对照,夏令时,当前时间,跨国会议,时间换算'
        ),
        'h1': '世界时钟与全球时区对照：39 个标准偏移一次看懂',
        'summary': (
            '世界时钟工具把全球 39 个标准时区的当前时间、偏移与夏令时集中在一页，支持表盘 / 列表 / '
            '时区一览三种视图与城市搜索。讲清它怎么用、为什么是 39 个时区、夏令时为什么会“跳”，'
            '以及跨国会议怎么对时间。'
        ),
        'body': '''
<blockquote>
  <p><b>一句话结论</b>：全球实际在用的<b>标准</b> UTC 偏移一共 38 个（UTC−12:00 到 UTC+14:00，
  外加若干半小时 / 45 分钟偏移），加上 UTC 基准本身，世界时钟用 39 张卡把它们的当前时间、偏移与
  夏令时状态一次铺开。同属一个时区的多个城市合并到一张卡上，所以“一张卡 = 一个时区 = 一批城市”。</p>
</blockquote>

<h2>一、这个工具能做什么</h2>
<p>世界时钟页面把全球主要时区的当前时间集中在一屏里，<b>每秒刷新</b>，并自动处理夏令时。它提供三种视图，随时切换：</p>
<table>
  <tr><th>视图</th><th>适合场景</th></tr>
  <tr><td>表盘（默认）</td><td>每个时区一张模拟钟表卡片，直观看到时针分针秒针的“早晚”差异</td></tr>
  <tr><td>列表</td><td>城市 / 地区 + 当前时间 + 偏移的紧凑表格，适合快速对照</td></tr>
  <tr><td>时区一览</td><td>按标准偏移从早到晚（UTC−12 → UTC+14）排列的静态总表，含全部代表城市</td></tr>
</table>
<p>顶部还有一个<b>城市搜索框</b>：输入城市名、时区名（如 <code>Asia/Shanghai</code>）或偏移（如
<code>UTC+8</code>），即可筛出匹配城市，并直接看到它的时区与实时表盘时间。</p>

<h2>二、为什么是 39 个时区</h2>
<p>直觉上“时区”好像有几百个（因为每个国家 / 地区都可能自己定），但按<b>标准 UTC 偏移</b>来数，
全球实际在用的只有 38 档：从 <code>UTC−12:00</code>（贝克岛，几乎无人居住）一路到
<code>UTC+14:00</code>（圣诞岛 / 基里巴斯莱恩群岛）。在这 38 档之间，还夹着几个半小时偏移
（如 <code>UTC+05:30</code> 印度、<code>UTC+09:30</code> 澳大利亚中部）和 45 分钟偏移
（如 <code>UTC+05:45</code> 尼泊尔、<code>UTC+08:45</code> 澳大利亚尤克拉）。</p>
<p>再加上 <code>UTC±00:00</code> 这个基准本身（既代表协调世界时，也覆盖伦敦、里斯本等无夏令时或带夏令时的地区），
合起来就是页面上的 <b>39 张卡</b>。换句话说，这 39 张卡已经把“全世界的钟”按偏移铺完了——再多并不会增加信息，
只是把同一偏移下的不同行政时区再拆开而已。</p>
<p>每个时区卡上标注了该时区的 IANA 名称、标准偏移，以及一批<b>共享此时区的代表城市</b>
（例如 <code>UTC+08:00</code> 一张卡就覆盖了北京 / 上海、新加坡、珀斯、香港）。这正是“同一时区的多个城市合并到
一张卡”的设计：<b>一张卡显示一个时区的统一时间，卡上列出该区所有代表城市</b>。</p>

<h2>三、三种视图怎么用</h2>
<h3>1. 表盘视图</h3>
<p>每个时区一张圆形模拟表盘，秒针每秒走动，下方同时给出数字时间与当地日期。卡上用徽标标出当前是否处于夏令时。
这是最直观的“一眼看出谁早谁晚”的视图。</p>
<h3>2. 列表视图</h3>
<p>把“城市 / 地区、当前时间、偏移”排成表格，纵向滚动即可对照，适合需要精确读数或复制时间的场景。</p>
<h3>3. 时区一览</h3>
<p>静态总表，按标准偏移从早到晚排列，每一行是该时区的代表标签、IANA 名称、标准偏移与全部代表城市。
它不随秒刷新，适合当作“世界时区速查表”反复查看。</p>

<h2>四、城市搜索：查任意城市的时间</h2>
<p>在顶部搜索框输入城市中文或英文（取决于当前语言），或输入 IANA 时区名、偏移字符串，结果会实时列出匹配城市，
每张结果卡同样带模拟表盘与数字时间。结果卡下方还会列出<b>同属该时区的其它城市</b>，方便你确认“这些城市其实是同一个时间”。</p>
<p>例如搜索 <code>东京</code>，会给你 <code>Asia/Tokyo</code> 的当前时间，并提示同区的首尔、平壤也是同一时刻；
搜索 <code>UTC+8</code> 则会一次性列出北京、上海、新加坡、香港、珀斯等所有 UTC+8 代表城市。</p>

<h2>五、夏令时为什么会“跳”</h2>
<p>不少时区实行夏令时（DST）：每年某天把时钟拨快 1 小时（春跳），某天拨回（秋跳）。所以这些地区的“当前偏移”
会在标准值上 <b>±1 小时</b>浮动。页面顶部的偏移徽标和卡片上的 DST 标记会如实反映这一状态——
这也是为什么同样写 <code>UTC+01:00</code> 的巴黎，夏天实际是 <code>UTC+02:00</code>。</p>
<p>一个常见坑：北半球夏天，纽约（UTC−4）与伦敦（UTC+1）相差 5 小时；但冬天纽约（UTC−5）与伦敦（UTC+0）相差 6 小时。
<b>跨时区约会议，永远以“具体日期 + 具体城市”为准，别凭记忆里的时间差。</b></p>

<h2>六、实战：跨国会议怎么对时间</h2>
<p>假设你在北京（UTC+8），要和伦敦（UTC+0/+1）与纽约（UTC−5/−4）开三方会。做法：</p>
<ol>
  <li>打开世界时钟，切到“表盘”或“列表”视图，直接读出三地此刻的钟面；</li>
  <li>用城市搜索快速定位三地，确认各自当前偏移（是否夏令时）；</li>
  <li>选定一个对三地都合理的本地时间（比如北京晚上 8 点），再用时区一览反查伦敦与纽约对应的本地时刻；</li>
  <li>若需要精确间隔，用 <a href="/diff/">时间差值计算</a> 工具按本地时区算出两时刻之间的天 / 时 / 分 / 秒。</li>
</ol>

<h2>七、常见问题</h2>
<table>
  <tr><th>问题</th><th>简短回答</th></tr>
  <tr><td>为什么有的城市没出现在列表里？</td><td>列表收录的是各标准偏移的代表城市；你的城市多半属于其中某个 IANA 时区，用城市搜索即可定位。</td></tr>
  <tr><td>时间准吗？</td><td>由浏览器本地时钟驱动，每秒刷新；时区换算用标准 Intl API，与系统一致。</td></tr>
  <tr><td>为什么是 39 张卡而不是更多？</td><td>39 已是全球标准偏移档位的全集，再拆只是把同一偏移下的行政时区分开，不增加新信息。</td></tr>
  <tr><td>夏令时标记会自己变吗？</td><td>会，每分钟校对一次，拨快 / 拨回当天会自动出现或消失。</td></tr>
</table>

<h2>八、小结</h2>
<table>
  <tr><th>概念</th><th>一句话</th></tr>
  <tr><td>标准偏移</td><td>全球 38 档（UTC−12 → UTC+14）+ UTC 基准 = 39 张卡</td></tr>
  <tr><td>同城多城市</td><td>合并到同一张卡，一卡一区、一区多城</td></tr>
  <tr><td>三种视图</td><td>表盘看早晚、列表读数、时区一览当速查表</td></tr>
  <tr><td>城市搜索</td><td>按城市 / 时区 / 偏移筛选，给实时表盘时间</td></tr>
  <tr><td>夏令时</td><td>当前偏移会在标准值上 ±1 小时，约会议以具体日期为准</td></tr>
</table>
<p>打开 <a href="/world-clock/">世界时钟工具</a> 自己对照一下，比记时差可靠得多。</p>
''',
        'related': [
            ('世界时钟工具', 'world-clock/'),
            ('时间差值计算', 'diff/'),
            ('博客首页', 'blog/'),
        ],
    },
    {
        'slug': 'coraza-waf-rules',
        'category': 'security',
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
        'category': 'security',
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
        'category': 'go',
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
        'cat_all': '全部',
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
        'cat_all': 'All',
    },
}

# 阶段2：新语言未单独翻博客 chrome 时，统一回退英文（与正文英文回退策略一致）。
for _L in ('ja', 'ko', 'es', 'pt-BR', 'fr', 'de', 'ru', 'id'):
    if _L not in TEXT:
        TEXT[_L] = dict(TEXT['en'])

# 阶段2：HTML / JSON-LD 语言属性按目标语言取真实代码（避免新语言页被误标成英文）。
_HTML_LANG = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es',
             'pt-BR': 'pt-BR', 'fr': 'fr', 'de': 'de', 'ru': 'ru', 'id': 'id'}


def _esc(s):
    import html as html_mod
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def articles_for(lang, articles_en):
    """按语言返回文章列表（中文用源文案；其余语言统一回退英文文案，再由 localize() 翻界面 chrome）。"""
    out = []
    for a in ARTICLES:
        if lang == 'zh':
            out.append(a)
        else:
            en = dict(a)
            en.update(articles_en[a['slug']])
            out.append(en)
    return out


def render_index(lang, articles_en, base):
    """博客索引页主体：分类筛选条 + 文章卡片列表。"""
    t = TEXT[lang]
    cats = ''.join(
        f'<a class="blog-cat" data-cat="{_esc(s)}" '
        f'href="{_esc(base + BLOG_INDEX)}?category={_esc(s)}">'
        f'{_esc(category_label(s, lang))}</a>'
        for s, _ in BLOG_CATEGORIES)
    out = ['<div class="blog">',
           '  <div class="blog-head">',
           f'    <p class="blog-head-lead">{_esc(t["index_lead"])}</p>',
           '  </div>',
           '  <div class="blog-cats" id="blogCats">',
           f'    <a class="blog-cat active" data-cat="" '
           f'href="{_esc(base + BLOG_INDEX)}">{_esc(t["cat_all"])}</a>',
           cats,
           '  </div>',
           '  <div class="blog-list">']
    for a in articles_for(lang, articles_en):
        href = base + article_path(a['slug'])
        cat = a.get('category')
        cat_attr = f' data-cat="{_esc(cat)}"' if cat else ''
        tags = ''.join(f'<span class="blog-tag">{_esc(tag)}</span>' for tag in a['tags'])
        out.append(f'    <a class="blog-card" href="{_esc(href)}"{cat_attr}>')
        out.append(f'      <p class="blog-card-title">{_esc(a["h1"])}</p>')
        out.append(f'      <p class="blog-card-desc">{_esc(a["summary"])}</p>')
        out.append(f'      <p class="blog-card-meta"><time datetime="{a["date"]}">'
                   f'{a["date"]}</time>{tags}</p>')
        out.append('    </a>')
    out.append('  </div>')
    out.append('''
  <script>
  (function(){
    var bar=document.getElementById('blogCats'); if(!bar) return;
    var cards=[].slice.call(document.querySelectorAll('.blog-card'));
    function apply(cat){
      cards.forEach(function(c){
        c.style.display=(!cat||c.getAttribute('data-cat')===cat)?'':'none';
      });
      [].slice.call(bar.querySelectorAll('.blog-cat')).forEach(function(b){
        b.classList.toggle('active', b.getAttribute('data-cat')===cat);
      });
    }
    bar.addEventListener('click', function(e){
      var b=e.target.closest('.blog-cat'); if(!b) return;
      e.preventDefault();
      var cur=new URLSearchParams(location.search).get('category');
      var cat=b.getAttribute('data-cat');
      if(cur===cat){ cat=null; }
      var u=new URL(location.href);
      if(cat){ u.searchParams.set('category',cat); }
      else { u.searchParams.delete('category'); }
      history.replaceState(null,'',u); apply(cat);
    });
    apply(new URLSearchParams(location.search).get('category'));
  })();
  </script>''')
    out.append('</div>')
    return '\n'.join(out)


def render_article(lang, a, base):
    """文章页主体：h1 + 元信息 + 正文 + 相关阅读。"""
    t = TEXT[lang]
    tags = ''.join(f'<span class="blog-tag">{_esc(tag)}</span>' for tag in a['tags'])
    meta = [f'<time datetime="{a["date"]}">{_esc(t["published"])} {a["date"]}</time>']
    if a['updated'] != a['date']:
        meta.append(f'<time datetime="{a["updated"]}">{_esc(t["updated"])} {a["updated"]}</time>')
    cat = a.get('category')
    if cat:
        meta.append(f'<a class="blog-cat-tag" href="{_esc(base + BLOG_INDEX)}?category={_esc(cat)}">'
                    f'{_esc(category_label(cat, lang))}</a>')
    meta.append(tags)
    lang_attr = _HTML_LANG.get(lang, 'en')
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
        'inLanguage': _HTML_LANG.get(lang, 'en'),
        'isAccessibleForFree': True,
        'author': {'@type': 'Organization', 'name': 'DevTools'},
        'keywords': a['keywords'],
        'articleSection': category_label(a.get('category', ''), lang),
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
            'inLanguage': _HTML_LANG.get(lang, 'en'),
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
