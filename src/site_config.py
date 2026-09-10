# -*- coding: utf-8 -*-
"""站点级配置：只在构建与提交脚本之间共享的常量。"""

# IndexNow 的 key。
#
# 这是「无账号」把 URL 推给搜索引擎的唯一通道，Bing / Yandex / Seznam / Naver 共享提交结果。
# key 本身不是机密（它就是要公开挂在网站上供对方回抓校验的），但必须保持稳定：
# 一旦改动，之前建立的校验关系失效，需要重新提交。
#
# 校验文件固定放在 https://xwjiang2003.github.io/tools/<key>.txt。
# 因为本仓库是 /tools/ 项目站点（https://xwjiang2003.github.io/ 根路径 404），
# 无法把 key 文件放到主机根目录，所以走 IndexNow 的 Option 2：
# key 文件所在目录决定了可提交的 URL 范围 —— 正好覆盖 /tools/ 下的全部页面。
INDEXNOW_KEY = '9f4c1d7a2e8b5306ac1f7d9e4b2a8c30'

# 提交端点。IndexNow 约定：提交给任一参与方即自动共享给其他参与方，
# 这里逐个提交一遍，是为了拿到各家独立的返回码、便于排查。
ENDPOINTS = [
    ('IndexNow', 'https://api.indexnow.org/indexnow'),
    ('Bing', 'https://www.bing.com/indexnow'),
    ('Yandex', 'https://yandex.com/indexnow'),
    ('Seznam', 'https://search.seznam.cz/indexnow'),
]
