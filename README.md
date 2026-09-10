# DevTools — 在线开发工具集

纯前端在线开发工具集，所有数据仅在浏览器本地处理，无后端、无追踪。

线上地址：<https://xwjiang2003.github.io/tools/>

## 页面结构

每个工具都是**独立 URL、独立 HTML**，只包含自己的工具界面与正文，互不重复。
每种语言各有一套完整页面：中文在根目录，英文在 `/en/` 下。

| URL | English | 工具 |
|-----|---------|------|
| `/tools/` | `/tools/en/` | JSON 格式化 / 压缩 / 校验 / 排序 / 转义 / 树视图 / 比对 / 转换 / JSONPath |
| `/tools/diff/` | `/tools/en/diff/` | 文本差异比对 |
| `/tools/encode/` | `/tools/en/encode/` | Base64 / URL / Unicode / HTML 实体 / Hex 编解码 |
| `/tools/regex/` | `/tools/en/regex/` | 正则表达式测试与替换预览 |
| `/tools/timestamp/` | `/tools/en/timestamp/` | Unix 时间戳与日期互转、多时区 |
| `/tools/hash/` | `/tools/en/hash/` | MD5 / SHA / HMAC / AES 与文件哈希 |
| `/tools/formatter/` | `/tools/en/formatter/` | HTML / CSS / JS / SQL / XML 格式化与压缩 |
| `/tools/string/` | `/tools/en/string/` | 字符串大小写 / 排序 / 去重 / 替换 / 统计 |
| `/tools/generator/` | `/tools/en/generator/` | UUID / 随机密码 / 二维码 / Lorem Ipsum / 随机数据 |
| `/tools/privacy.html` | `/tools/en/privacy.html` | 隐私政策 |

## 多语言

- **自动选择**：首次访问时按浏览器语言判断，中文浏览器留在中文版，其余跳到 `/en/`。
  已手动选择过（写入 localStorage）或疑似搜索引擎爬虫时不跳转，避免干扰收录。
- **手动切换**：页眉右上角的 `中文 / English` 分段控件，选择会被记住。
- **URL 覆盖**：`?lang=zh` / `?lang=en` 可强制指定并记住，适合分享链接。
- 两种语言各有独立的标题、描述、正文与 `hreflang` 备用链接，爬虫不执行 JS 也能读到完整内容——
  英文页面在**构建时**就完成了全部文案替换，不存在运行时翻译闪烁。

## 构建

源码在 `src/`，构建产物在 `docs/`（GitHub Pages 发布目录）和 `dist/`（本地预览）。

```bash
python3 build.py            # 构建一次
python3 build.py --watch    # 监听 src/ 变化并重建（需 pip install watchdog）
```

构建做的事：

- 把 `src/css/style.css` 与 `src/js/*.js` 内联进每个页面，单页自包含、无本地依赖请求。
- 把 `src/tools/<slug>.html` 的界面与 `src/content.py` 里的说明/步骤/FAQ 组装成完整的工具页。
- 生成每页独立的 `<title>`、`<meta description>`、`<link canonical>`、Open Graph 与 JSON-LD（WebApplication + FAQPage）。
- 生成 `sitemap.xml`（含 `hreflang` 备用链接）、`robots.txt`、`.nojekyll`。
- 英文版把内联 JS 与 HTML 里的界面文案整体替换为英文（`src/i18n.py` 字典），
  源码注释保持原样不动。

### 本地预览

```bash
python3 build.py
python3 -m http.server 8080 --directory dist
# 打开 http://localhost:8080
```

### 目录说明

```
src/index.html      工具页模板（内含 {{占位符}}）
src/privacy.html    隐私政策模板
src/content.py      中文：各工具页的标题/描述/正文/FAQ 文案
src/content_en.py   英文：同上
src/i18n.py         中文界面字符串 → 英文（含少量需整行改写的补丁）
src/tools/*.html    各工具的界面片段（构建时嵌入模板）
src/css/style.css   全站样式
src/js/*.js         各工具逻辑
build.py            静态站点生成器
docs/               构建产物 = GitHub Pages 发布目录
dist/               构建产物 = 本地预览（已 gitignore）
```

> GitHub Pages 的发布源是仓库的 **`docs/` 目录**（仓库根目录的文件不会被发布）。
> 因此只需提交 `docs/`，`dist/` 仅为本地预览。

## 技术栈

- **CodeMirror 5** — 代码编辑器（CDN 引入）
- **原生 JavaScript** — 无框架，纯前端实现
- **CSS Variables** — 支持亮色/暗色主题切换
- **Python 构建脚本** — 零第三方依赖的静态站点生成

## SEO

- 9 个工具 × 2 种语言共 20 个页面，各自有唯一标题、描述与正文（构建时烘焙进 HTML，不依赖 JS 渲染）。
- 中英页面互为 `hreflang` 备用链接（`zh-CN` / `en` / `x-default`），避免被判为重复内容。
- `sitemap.xml`（带 `xhtml:link` 多语言标注）+ `robots.txt`；提交到 [Google Search Console](https://search.google.com/search-console)
  与 [Bing 网站管理员工具](https://www.bing.com/webmasters) 可加速收录。
- 每页带 JSON-LD 结构化数据（WebApplication + FAQPage），有机会在搜索结果中展示 FAQ 富摘要。
- 顶部导航、页脚与语言切换都是真实 `<a>` 内链，便于爬虫发现全部页面。

## 收录与 GEO（让搜索引擎与 AI 能找到本站）

### 已自动化：IndexNow

```bash
python3 submit.py           # 提交全部 20 个 URL
python3 submit.py --dry-run # 只看提交内容
```

Google 与百度的 sitemap ping 接口已下线（实测 Google 无响应、Bing 返回 `410`、百度返回 `404`），
IndexNow 是目前**唯一不需要账号**的提交通道，结果由 Bing / Yandex / Seznam / Naver 共享。
Bing 索引同时供 ChatGPT Search 检索，所以这一步对传统搜索和 AI 引用都有用。

归属校验文件是 `docs/<key>.txt`（key 见 `src/site_config.py`）。
因为本仓库是 GitHub Pages 项目站点、`https://xwjiang2003.github.io/` 根路径返回 404，
key 文件只能放在 `/tools/` 下，走 IndexNow 的 Option 2 —— 恰好覆盖本站全部 URL。

> 改动 key 会让已有校验失效，需要重新提交，所以不要随意更换。

### 用户站点已建立，根目录可用

`xwjiang2003.github.io` 用户站点仓库已创建并发布（<https://xwjiang2003.github.io/>），
+它拿回了**域名根目录的控制权**，因此：

- **文件验证**和 **HTML 标记验证**现在都能用（此前根路径 404，只能标记验证）。
  文件验证：把 `baidu_verify_xxx.html` / `googleXXXX.html` 放进 `xwjiang2003.github.io` 仓库根目录即可。
- **主机级文件已移交根仓库**（`robots.txt` / `sitemap.xml` / IndexNow key）。
  这一点很关键：**`robots.txt` 只有放在主机根目录才会被爬虫读取**，
  此前生成的 `/tools/robots.txt` 实际上从未被任何爬虫读到。权威版本现在在
  <https://xwjiang2003.github.io/robots.txt>。
- IndexNow 已切到官方推荐的 **Option 1**：key 文件在主机根目录，一份 key 覆盖整站，
  可提交的 URL 不再受目录限制。

### 需要你自己登录账号操作

| 平台 | 入口 | 说明 |
|------|------|------|
| Google Search Console | <https://search.google.com/search-console> | 用「网址前缀」添加 `https://xwjiang2003.github.io/tools/`，验证码填进 `src/index.html` 预留的 `google-site-verification` 注释行 |
| Bing 网站管理员工具 | <https://www.bing.com/webmasters> | 同上，用 `msvalidate.01`；也可直接导入 Search Console |
| 百度搜索资源平台 | <https://ziyuan.baidu.com> | 用 `baidu-site-verification`，或直接把验证文件放进根仓库 |

验证码拿到后，把 `src/index.html` 里对应那行注释取消并填入即可，重新 `python3 build.py` 后推送。
百度对 `github.io` 收录一向很差，不要期待太高。

### 关于「提交给大模型厂商」

**不存在这样的提交入口。** OpenAI、Anthropic、Google、DeepSeek 等都没有面向站长的收录申请通道，
任何声称能「提交给大模型」的服务都不可信。实际起作用的是这几件事：

- `robots.txt` 已显式放行 `GPTBot` / `OAI-SearchBot` / `ClaudeBot` / `PerplexityBot` /
  `Google-Extended` / `Bytespider` / `DeepSeekBot` 等（默认 `User-agent: *` 本就允许，显式列出是声明意图）。
- `llms.txt` 已生成（<https://xwjiang2003.github.io/tools/llms.txt>）。
  这是社区提案，主流厂商并未承诺读取，属于成本极低、**不要指望它是收录开关**。
- 真正的杠杆是：进入 Bing / Google 索引（AI 检索大多基于这两家的索引）+ 每页的
  JSON-LD（`WebApplication` + `FAQPage`，FAQ 结构最容易被直接引用）+ 站外引用。

## 访问统计

页脚使用 [不蒜子 busuanzi](https://busuanzi.ibruce.info/) 显示本站总访问量（PV）与访客数（UV）：

- 统计脚本只在线上环境加载，`file://` 本地预览和 `localhost` 调试不会上报，避免污染线上数据。
- 统计服务不可用时，页脚计数器自动移除，不影响页面其它功能。
- 不蒜子按**域名**聚合：`xwjiang2003.github.io` 下所有项目共用同一份 PV/UV，且没有明细报表。
  需要分路径 / 来源 / 地区等详细数据时，可另接百度统计或 Google Analytics。

## 快捷键

| 快捷键 | 说明 |
|--------|------|
| `Ctrl + Enter` | 执行当前面板操作（格式化/压缩/校验等） |

## 浏览器兼容

支持所有现代浏览器（Chrome / Firefox / Safari / Edge）。
