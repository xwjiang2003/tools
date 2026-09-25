# devtools.help — 项目记忆文档

## 发布流程

```
python build.py          # 从 src/ 生成 docs/ 静态站点
python check.py          # 验证构建结果
python sync_remote.py    # 同步远程更改（避免覆盖 GitHub Actions）
python build.py          # 重新构建确保最新
python gh_commit.py      # 通过 REST API 提交到 GitHub
# GitHub Actions 触发 Pages 部署
python submit.py         # IndexNow API 提交 URL 到搜索引擎
```

## 内容规范

- **中英双语**: 所有页面在构建时独立生成 `zh-CN` 和 `en` 两个版本
- **SEO**: 使用 IndexNow (`submit.py`) 和百度推送 (`push_baidu.py`) 维护搜索引擎索引
- **部署**: 通过 GitHub REST API 部署（非 `git push`），避免与 GitHub Actions 冲突
- **同步远程**: 推送前必须先同步远程，防止覆盖自动化更新

## 已知问题

- **搜索引擎索引覆盖有限**: 多数搜索引擎仅抓取首页，需手动向 Bing Webmaster Tools 提交 URL
- **Vulkan warmup timeout**: Arc B370 iGPU 上启动本地模型时可能出现错误 3003

## 构建规则

- 源文件位于 `src/` 目录，通过 `build.py` 生成 `docs/` 静态站点
- `src/tools/` 目录包含各个工具的 HTML 模板
- `src/css/` 和 `src/js/` 包含样式和脚本
- 博客内容在 `src/blog.py` / `src/blog_en.py` 中定义
- 动态页面（hotnews、go-cheatsheet）在 `build.py` 中特殊处理

## 部署信息

- **域名**: devtools.help
- **托管**: GitHub Pages
- **GitHub 仓库**: 通过 REST API 部署
- **SEO 验证**: BingSiteAuth.xml、Baidu 验证文件已放置

## 开发周期记录

### 2025-09-25

- 完成静态站点生成器构建，生成中英双语 9 个工具页面
- 部署到 GitHub Pages (https://www.devtools.help)
- 配置 IndexNow API 和百度推送
- 手动向 Bing Webmaster Tools 提交 URL 改善索引覆盖

### 2025-09-24

- 开发 go-cheatsheet 工具页面
- 优化构建流程，确保同步远程策略正确执行
