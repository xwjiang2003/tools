# DevTools — 在线开发工具集

纯前端在线开发工具集，所有数据仅在浏览器本地处理，无后端、无追踪。

线上地址：<https://xwjiang2003.github.io/tools/>

## 页面结构

每个工具都是**独立 URL、独立 HTML**，只包含自己的工具界面与正文，互不重复：

| URL | 工具 |
|-----|------|
| `/tools/` | JSON 格式化 / 压缩 / 校验 / 排序 / 转义 / 树视图 / 比对 / 转换 / JSONPath |
| `/tools/diff/` | 文本差异比对 |
| `/tools/encode/` | Base64 / URL / Unicode / HTML 实体 / Hex 编解码 |
| `/tools/regex/` | 正则表达式测试与替换预览 |
| `/tools/timestamp/` | Unix 时间戳与日期互转、多时区 |
| `/tools/hash/` | MD5 / SHA / HMAC / AES 与文件哈希 |
| `/tools/formatter/` | HTML / CSS / JS / SQL / XML 格式化与压缩 |
| `/tools/string/` | 字符串大小写 / 排序 / 去重 / 替换 / 统计 |
| `/tools/generator/` | UUID / 随机密码 / 二维码 / Lorem Ipsum / 随机数据 |
| `/tools/privacy.html` | 隐私政策 |

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
- 生成 `sitemap.xml`、`robots.txt`、`.nojekyll`。

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
src/content.py      各工具页的标题/描述/正文/FAQ 文案
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

- 9 个工具各自有唯一标题、描述与正文（构建时烘焙进 HTML，不依赖 JS 渲染）。
- `sitemap.xml` + `robots.txt`；提交到 [Google Search Console](https://search.google.com/search-console)
  与 [Bing 网站管理员工具](https://www.bing.com/webmasters) 可加速收录。
- 每页带 JSON-LD 结构化数据（WebApplication + FAQPage），有机会在搜索结果中展示 FAQ 富摘要。
- 顶部导航与页脚都是真实 `<a>` 内链，便于爬虫发现 9 个工具页。

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
