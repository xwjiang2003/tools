# JSON Tools — 在线 JSON 工具集

在线 JSON 工具网站，纯前端实现，所有数据仅在浏览器本地处理。

## 功能

| 工具 | 说明 |
|------|------|
| **格式化** | JSON 美化，支持自定义缩进（2空格/4空格/Tab） |
| **压缩** | JSON 压缩为一行，显示压缩前后大小对比 |
| **校验** | JSON 合法性校验，显示错误位置和结构概览 |
| **比对** | 两个 JSON 差异对比，支持语义比对（忽略 key 顺序） |
| **转换** | JSON ↔ CSV / XML / YAML 相互转换 |
| **JSONPath** | 使用 JSONPath 表达式查询 JSON 数据 |
| **转义** | JSON 字符串转义与去转义 |
| **排序** | 递归按 key 字母排序（升序/降序） |
| **树视图** | 可折叠/展开的 JSON 树形结构浏览 |

## 使用方式

直接在浏览器中打开 `index.html` 即可使用，无需安装任何依赖。

### 本地预览

```bash
# Python 3
python3 -m http.server 8080

# 然后访问 http://localhost:8080
```

## 技术栈

- **CodeMirror 5** — 代码编辑器（CDN 引入）
- **原生 JavaScript** — 无框架，纯前端实现
- **CSS Variables** — 支持亮色/暗色主题切换

## 快捷键

| 快捷键 | 说明 |
|--------|------|
| `Ctrl + Enter` | 执行当前面板操作（格式化/压缩/校验等） |

## 浏览器兼容

支持所有现代浏览器（Chrome / Firefox / Safari / Edge）。
