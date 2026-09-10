# -*- coding: utf-8 -*-
"""站点级配置：只在构建与提交脚本之间共享的常量。"""

# IndexNow 的 key。
#
# 这是「无账号」把 URL 推给搜索引擎的唯一通道，Bing / Yandex / Seznam / Naver 共享提交结果。
# key 本身不是机密（它就是要公开挂在网站上供对方回抓校验的），但必须保持稳定：
# 一旦改动，之前建立的校验关系失效，需要重新提交。
#
# 校验文件放在 https://xwjiang2003.github.io/tools/<key>.txt，即 IndexNow 的 Option 2：
# key 文件所在目录决定可提交的 URL 范围，正好覆盖 /tools/ 下全部页面。
#
# 注：2026-09 已建立用户站点仓库 xwjiang2003.github.io，主机根目录现在可写，
# 官方「强烈建议」的 Option 1（key 文件放主机根目录、覆盖整站）已经可行。
# 当前仍用 Option 2 是因为它已在 IndexNow/Bing/Yandex/Seznam 四家验证通过，且只有 /tools/ 一个站点；
# 等以后新增第二个项目站点（如 /warden/）时，再把 key 文件移到根仓库即可，改动只有 keyLocation 一行。
INDEXNOW_KEY = '9f4c1d7a2e8b5306ac1f7d9e4b2a8c30'

# 提交端点。IndexNow 约定：提交给任一参与方即自动共享给其他参与方，
# 这里逐个提交一遍，是为了拿到各家独立的返回码、便于排查。
ENDPOINTS = [
    ('IndexNow', 'https://api.indexnow.org/indexnow'),
    ('Bing', 'https://www.bing.com/indexnow'),
    ('Yandex', 'https://yandex.com/indexnow'),
    ('Seznam', 'https://search.seznam.cz/indexnow'),
]
