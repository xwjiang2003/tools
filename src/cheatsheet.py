# -*- coding: utf-8 -*-
"""Go 工具链速查表（/go-cheatsheet/）：数据 + 构建期渲染。

内容直接写在本文件里而不是 data/*.json：条目中的示例代码含大量引号、反斜杠、
$ 与 => 符号，JSON 转义极易写错；Python 三引号字符串几乎没有转义负担，
也可以用注释组织条目。渲染模式与 news.py 一致：构建期把全部内容烘焙进 HTML，
内联 JS 只做「搜索过滤 + 分类跳转」这一件锦上添花的事——禁用 JS 时所有条目
照样完整可见，爬虫不执行 JS 也能读到全部内容。

条目维护约定：
  - cmd      命令或指令本身（速查表里被复制的对象）
  - desc     一句话说明它干什么
  - example  可直接照抄的用法（代码块，可省）
  - pitfall  真实踩坑点（速查表与普通文档的差异就在这里，尽量写）
  - 所有文本字段都是 {'zh': ..., 'en': ...}，示例代码中英共用一份
  - 版本相关表述以 UPDATED / GO_VERSION 为准，Go 发新版后整体过一遍
"""

UPDATED = '2026-09-24'
GO_VERSION = '1.27'          # 当前稳定版（1.27.1，2026-09-01）

SECTIONS = [
    # ================================================== 构建 / 运行 / 测试
    {
        'id': 'build',
        'name': {'zh': '构建、运行与测试', 'en': 'Build, Run & Test'},
        'desc': {
            'zh': '日常写得最多的一组命令，全部支持 ./... 匹配当前模块下的所有包。',
            'en': 'The commands you type most often. All of them accept ./... '
                  'to match every package in the current module.',
        },
        'items': [
            {
                'cmd': 'go build ./...',
                'desc': {
                    'zh': '编译当前模块的所有包。不带 -o 时只检查能否编译，不会留下二进制文件。',
                    'en': 'Compiles every package in the module. Without -o it only '
                          'type-checks and links — no binary is left behind.',
                },
                'example': 'go build -o bin/app ./cmd/app',
                'pitfall': {
                    'zh': './... 不会包含 vendor 目录和子模块（各有自己 go.mod 的目录）。',
                    'en': './... skips the vendor directory and nested modules '
                          '(directories with their own go.mod).',
                },
            },
            {
                'cmd': 'go run .',
                'desc': {
                    'zh': '编译到临时目录并立即运行，开发调试最常用。',
                    'en': 'Compiles into a temp directory and runs immediately — '
                          'the daily driver for local development.',
                },
                'example': 'go run ./cmd/app --config dev.yaml',
                'pitfall': {
                    'zh': 'kill 掉 go run 进程不一定能杀掉它启动的子进程（程序本体），'
                          '生产环境请用 go build 的产物。',
                    'en': 'Killing the go run process may leave the actual child '
                          'binary running — always ship go build artifacts in production.',
                },
            },
            {
                'cmd': 'go test ./...',
                'desc': {
                    'zh': '运行全部测试。常用旗标：-v 详细输出、-run 按正则筛选、-race 竞态检测、-cover 覆盖率。',
                    'en': 'Runs all tests. Handy flags: -v verbose, -run to filter by '
                          'regex, -race for the race detector, -cover for coverage.',
                },
                'example': 'go test -race -run TestParse ./pkg/parser/...\ngo test -coverprofile=cover.out ./... && go tool cover -html=cover.out',
                'pitfall': {
                    'zh': '测试结果会被缓存，改了环境变量或外部文件不会使缓存失效——'
                          '需要强制重跑时加 -count=1。',
                    'en': 'Test results are cached; changing env vars or external files '
                          'does NOT invalidate the cache — force a rerun with -count=1.',
                },
            },
            {
                'cmd': 'go vet ./...',
                'desc': {
                    'zh': '官方静态检查：printf 参数错位、不可达代码、错误的 struct tag 等。',
                    'en': 'The official static analyzer: printf mismatches, unreachable '
                          'code, malformed struct tags, and more.',
                },
                'example': 'go vet ./... && staticcheck ./...',
                'pitfall': {
                    'zh': 'vet 只覆盖一小类高置信问题，CI 里建议再挂 staticcheck（honest 地说：两者误报都很低）。',
                    'en': 'vet only covers a small set of high-confidence checks; '
                          'add staticcheck in CI for much broader coverage.',
                },
            },
            {
                'cmd': 'go install pkg@version',
                'desc': {
                    'zh': '把命令行工具安装到 GOBIN（默认 ~/go/bin），管理全局工具的标准方式。',
                    'en': 'Installs a command into GOBIN (default ~/go/bin) — the standard '
                          'way to manage global Go tools.',
                },
                'example': 'go install golang.org/x/tools/cmd/goimports@latest\ngo install honnef.co/go/tools/cmd/staticcheck@2025.1',
                'pitfall': {
                    'zh': '带 @版本号 时 go install 会忽略当前目录的 go.mod，在独立上下文中构建；'
                          '想给项目加依赖请用 go get，不是 go install。',
                    'en': 'With @version, go install ignores the go.mod in the current '
                          'directory and builds in isolation; to add a project dependency '
                          'use go get, not go install.',
                },
            },
            {
                'cmd': 'go clean -cache -modcache',
                'desc': {
                    'zh': '清空构建缓存与模块下载缓存，排查「改了依赖却像没改」类怪问题的最后手段。',
                    'en': 'Wipes the build cache and module download cache — the last '
                          'resort when dependency changes seem to have no effect.',
                },
                'example': {
                    'zh': 'go clean -cache\ngo clean -modcache   # 更狠：删掉全部已下载模块',
                    'en': 'go clean -cache\ngo clean -modcache   # harsher: deletes every downloaded module',
                },
                'pitfall': {
                    'zh': '-modcache 会删掉 GOMODCACHE 下所有模块，下次构建全量重新下载，CI 镜像里慎用。',
                    'en': '-modcache deletes every downloaded module; the next build '
                          're-downloads everything, so use it carefully on CI images.',
                },
            },
        ],
    },
    # ================================================== 模块与依赖
    {
        'id': 'mod',
        'name': {'zh': '模块与依赖管理', 'en': 'Modules & Dependencies'},
        'desc': {
            'zh': 'go.mod / go.sum 的日常操作。排查依赖问题时先看 go mod graph 和 go mod why。',
            'en': 'Day-to-day go.mod / go.sum operations. When debugging dependency '
                  'issues, reach for go mod graph and go mod why first.',
        },
        'items': [
            {
                'cmd': 'go mod init <path>',
                'desc': {
                    'zh': '初始化模块，生成 go.mod。模块路径就是别人 import 你时用的路径。',
                    'en': 'Initializes a module and writes go.mod. The module path is '
                          'exactly what others will use to import you.',
                },
                'example': 'go mod init github.com/yourname/project',
                'pitfall': {
                    'zh': '私有仓库也要用完整域名路径（如 git.company.com/team/proj），'
                          '随便起个短名会让 go get 无法定位仓库。',
                    'en': 'Private repos still need a full host-based path '
                          '(e.g. git.company.com/team/proj); a short made-up name '
                          'makes the module unresolvable.',
                },
            },
            {
                'cmd': 'go mod tidy',
                'desc': {
                    'zh': '按代码里真实的 import 增删 go.mod 条目并补全 go.sum，提交前必跑。',
                    'en': 'Adds/removes go.mod entries to match real imports and completes '
                          'go.sum — run it before every commit.',
                },
                'example': {
                    'zh': 'go mod tidy\ngo mod tidy -compat=1.26   # 兼容到指定旧版本',
                    'en': 'go mod tidy\ngo mod tidy -compat=1.26   # stay compatible with an older version',
                },
                'pitfall': {
                    'zh': '报 missing go.sum entry 时，先 go mod download <模块> 再 tidy；'
                          'tidy 只扫描当前 GOOS/GOARCH 下的构建标签，跨平台代码注意 -compat。',
                    'en': 'On "missing go.sum entry", run go mod download <module> first, '
                          'then tidy again; tidy scans build tags for the current '
                          'GOOS/GOARCH only — mind -compat for older toolchains.',
                },
            },
            {
                'cmd': 'go get pkg@version',
                'desc': {
                    'zh': '添加、升级或降级依赖（只改 go.mod，不安装任何二进制）。',
                    'en': 'Adds, upgrades or downgrades a dependency (edits go.mod only — '
                          'installs no binaries).',
                },
                'example': {
                    'zh': 'go get github.com/gin-gonic/gin@latest\ngo get github.com/sirupsen/logrus@v1.9.3   # 降级同理',
                    'en': 'go get github.com/gin-gonic/gin@latest\ngo get github.com/sirupsen/logrus@v1.9.3   # same for downgrades',
                },
                'pitfall': {
                    'zh': '不带版本等价于 @upgrade，可能顺手升级一堆间接依赖；'
                          '想最小改动就钉死版本号。',
                    'en': 'Omitting the version means @upgrade and may pull a cascade of '
                          'indirect upgrades; pin an exact version for minimal diffs.',
                },
            },
            {
                'cmd': 'go list -m -u all',
                'desc': {
                    'zh': '列出全部依赖及可升级版本（[v1.2.3] 后缀表示有新版本）。',
                    'en': 'Lists all dependencies with available upgrades '
                          '(a [v1.2.3] suffix means a newer version exists).',
                },
                'example': {
                    'zh': 'go list -m -u all\ngo list -m -versions github.com/spf13/cobra   # 看某个模块的全部版本',
                    'en': 'go list -m -u all\ngo list -m -versions github.com/spf13/cobra   # every version of one module',
                },
                'pitfall': {
                    'zh': 'all 包含间接依赖，输出会很长；只看直接依赖用 go list -m -u $(go list -m -f \'{{if not .Indirect}}{{.Path}}{{end}}\' all)。',
                    'en': '"all" includes indirect deps and gets long; filter to direct '
                          'deps with go list -m -f \'{{if not .Indirect}}{{.Path}}{{end}}\' all.',
                },
            },
            {
                'cmd': 'go mod why <pkg>',
                'desc': {
                    'zh': '回答「这个包到底是谁引进来的」：给出从 main 包到它的导入链。',
                    'en': 'Answers "who pulled this package in?" by showing the import '
                          'chain from your main packages to it.',
                },
                'example': {
                    'zh': 'go mod why golang.org/x/sys\ngo mod graph | grep jwt   # 看完整的依赖图',
                    'en': 'go mod why golang.org/x/sys\ngo mod graph | grep jwt   # the full dependency graph',
                },
                'pitfall': {
                    'zh': 'why 显示的是「主模块视角」的链；要对比两个模块互相的版本要求，用 go mod graph。',
                    'en': 'why shows the chain from the main module\'s perspective; '
                          'for raw version requirements between modules use go mod graph.',
                },
            },
            {
                'cmd': 'go mod download',
                'desc': {
                    'zh': '只下载依赖到本地缓存，不编译。CI 里用它预热缓存、加速后续构建。',
                    'en': 'Downloads dependencies into the local cache without compiling — '
                          'use it to warm up CI caches.',
                },
                'example': {
                    'zh': 'go mod download\ngo mod download github.com/gin-gonic/gin   # 只下载指定模块',
                    'en': 'go mod download\ngo mod download github.com/gin-gonic/gin   # download just this module',
                },
                'pitfall': {
                    'zh': 'go.sum 缺条目导致的构建失败，多半 download 一下对应模块就能修。',
                    'en': 'Most "missing go.sum entry" build failures are fixed by '
                          'downloading the offending module explicitly.',
                },
            },
            {
                'cmd': 'go mod verify',
                'desc': {
                    'zh': '校验本地缓存里的模块与 go.sum 记录的哈希一致，防缓存被篡改。',
                    'en': 'Verifies that cached modules match the hashes recorded in '
                          'go.sum — guards against a tampered cache.',
                },
                'example': 'go mod verify',
                'pitfall': {
                    'zh': '输出 all modules verified 才是通过；任何一行不匹配都说明缓存不可信，应 go clean -modcache。',
                    'en': 'Only "all modules verified" is a pass; any mismatch means the '
                          'cache is untrustworthy — run go clean -modcache.',
                },
            },
        ],
    },
    # ================================================== 格式化与代码工具
    {
        'id': 'fmt',
        'name': {'zh': '格式化与代码工具', 'en': 'Formatting & Code Tools'},
        'desc': {
            'zh': 'gofmt 管格式，goimports 在此基础上管 import，两者区别详见本站博客专题。',
            'en': 'gofmt handles layout; goimports additionally manages imports — '
                  'see our blog post for the full comparison.',
        },
        'items': [
            {
                'cmd': 'gofmt -l -w .',
                'desc': {
                    'zh': '格式化代码：-l 列出不符合规范的文件，-w 直接改写，-d 只看差异不改文件。',
                    'en': 'Formats source code: -l lists non-conforming files, -w rewrites '
                          'in place, -d shows the diff without writing.',
                },
                'example': {
                    'zh': 'gofmt -l .          # CI 检查：有输出即失败\ngofmt -d main.go    # 看会改成什么样\ngofmt -s -w .       # 同时做代码简化',
                    'en': 'gofmt -l .          # CI check: any output means failure\ngofmt -d main.go    # preview what would change\ngofmt -s -w .       # also simplify the code',
                },
                'pitfall': {
                    'zh': 'gofmt 不会增删 import，也不会调整 import 分组——那是 goimports 的活，两者结果可以不一样。',
                    'en': 'gofmt never adds/removes imports and does not reorder import '
                          'groups — that is goimports territory, and their output can differ.',
                },
            },
            {
                'cmd': 'goimports -l -w .',
                'desc': {
                    'zh': '= gofmt + 自动补全/删除 import + 按标准库/第三方分组排序。',
                    'en': '= gofmt + automatic import addition/removal + grouping '
                          '(stdlib first, then third-party).',
                },
                'example': {
                    'zh': 'go install golang.org/x/tools/cmd/goimports@latest\ngoimports -local github.com/myorg -w .   # 本地包单独一组',
                    'en': 'go install golang.org/x/tools/cmd/goimports@latest\ngoimports -local github.com/myorg -w .   # own packages in their own group',
                },
                'pitfall': {
                    'zh': '不加 -local 时，你自己公司的包会被归进「第三方」一组；'
                          '首次在大仓库上运行会建索引，比较慢属正常。',
                    'en': 'Without -local, your own organization\'s packages land in the '
                          'third-party group; the first run on a large repo builds an '
                          'index and is expectedly slow.',
                },
            },
            {
                'cmd': 'go doc <pkg>.<symbol>',
                'desc': {
                    'zh': '终端里查文档：包、函数、类型都可以，不用开浏览器。',
                    'en': 'Reads documentation in the terminal — packages, functions and '
                          'types, no browser needed.',
                },
                'example': {
                    'zh': 'go doc net/http.Server\ngo doc json.Marshal\ngo doc github.com/gin-gonic/gin@latest   # 1.27 起支持 pkg@version',
                    'en': 'go doc net/http.Server\ngo doc json.Marshal\ngo doc github.com/gin-gonic/gin@latest   # pkg@version since Go 1.27',
                },
                'pitfall': {
                    'zh': '查未下载的第三方包会失败，先 go mod download 或加 @version 后缀。',
                    'en': 'Querying a third-party package that is not downloaded yet '
                          'fails — run go mod download first or append @version.',
                },
            },
            {
                'cmd': 'go generate ./...',
                'desc': {
                    'zh': '扫描源码里的 //go:generate 注释并执行对应命令（生成 mock、stringer 等）。',
                    'en': 'Scans for //go:generate directives and runs them (mocks, '
                          'stringer, and other codegen).',
                },
                'example': '//go:generate stringer -type=Status\ngo generate ./...',
                'pitfall': {
                    'zh': 'go generate 不是构建的一部分，go build 不会触发它——生成物要提交进仓库或写进 CI。',
                    'en': 'go generate is NOT part of the build — go build never triggers '
                          'it. Commit generated files or run it in CI.',
                },
            },
            {
                'cmd': 'gofumpt -l -w .',
                'desc': {
                    'zh': '第三方更严格的格式化器（gofmt 的超集），团队统一风格时常用。',
                    'en': 'A stricter third-party formatter (a superset of gofmt), popular '
                          'for enforcing team-wide style.',
                },
                'example': 'go install mvdan.cc/gofumpt@latest\ngofumpt -extra -w .',
                'pitfall': {
                    'zh': 'gofumpt 的输出是 gofmt 兼容的更严格版本，混用两个工具格式化同一仓库会产生反复横跳的 diff。',
                    'en': 'gofumpt output is a stricter gofmt-compatible style; mixing '
                          'both tools on one repo creates flip-flopping diffs.',
                },
            },
            {
                'cmd': 'staticcheck ./...',
                'desc': {
                    'zh': '事实标准的深度静态检查，覆盖 bug、性能、弃用 API、代码简化建议。',
                    'en': 'The de-facto deep static analyzer: bugs, performance, '
                          'deprecated APIs and simplifications.',
                },
                'example': 'go install honnef.co/go/tools/cmd/staticcheck@latest\nstaticcheck ./...',
                'pitfall': {
                    'zh': '和 go vet 是互补关系不是替代关系：vet 管编译级高置信问题，staticcheck 管更宽的最佳实践。',
                    'en': 'Complements go vet rather than replacing it: vet covers '
                          'compiler-grade certainties, staticcheck covers broader practice.',
                },
            },
        ],
    },
    # ================================================== 环境变量
    {
        'id': 'env',
        'name': {'zh': '关键环境变量', 'en': 'Key Environment Variables'},
        'desc': {
            'zh': '用 go env -w 写入的配置持久保存在 go env 文件里，对所有终端会话生效。',
            'en': 'Values set via go env -w persist in the go env file and apply to '
                  'every shell session.',
        },
        'items': [
            {
                'cmd': 'GOPROXY',
                'desc': {
                    'zh': '模块下载代理。国内网络必配，否则拉github上的依赖经常超时。',
                    'en': 'The module download proxy. A regional mirror is essential where '
                          'proxy.golang.org is unreachable or slow.',
                },
                'example': {
                    'zh': 'go env -w GOPROXY=https://goproxy.cn,direct\ngo env -w GOPROXY=https://goproxy.io,direct   # 另一个常用镜像',
                    'en': 'go env -w GOPROXY=https://goproxy.cn,direct\ngo env -w GOPROXY=https://goproxy.io,direct   # another popular mirror',
                },
                'pitfall': {
                    'zh': 'direct 要放在最后：意思是「所有代理都失败后才直连源仓库」；'
                          '只写 direct 等于完全不用代理。',
                    'en': 'Put direct last: it means "fall back to the origin only after '
                          'all proxies fail"; writing only direct disables proxies entirely.',
                },
            },
            {
                'cmd': 'GOPRIVATE',
                'desc': {
                    'zh': '声明私有模块路径前缀（glob），匹配的模块跳过代理和 sum 校验，直连仓库。',
                    'en': 'Glob patterns for private module prefixes; matching modules '
                          'bypass the proxy and checksum database and fetch directly.',
                },
                'example': {
                    'zh': 'go env -w GOPRIVATE=git.company.com/*,github.com/myorg/*\ngo env -w GONOPROXY=git.company.com/*   # 只想绕过代理时',
                    'en': 'go env -w GOPRIVATE=git.company.com/*,github.com/myorg/*\ngo env -w GONOPROXY=git.company.com/*   # bypass the proxy only',
                },
                'pitfall': {
                    'zh': 'GOPRIVATE 同时是 GONOPROXY 和 GONOSUMDB 的默认值；'
                          '只想跳过其中一项就单独设置那两个变量。',
                    'en': 'GOPRIVATE is the default for both GONOPROXY and GONOSUMDB; '
                          'set those two individually when you only want one behavior.',
                },
            },
            {
                'cmd': 'GOFLAGS',
                'desc': {
                    'zh': '给所有 go 命令追加默认旗标，比如全局启用 -mod=mod 或 -race。',
                    'en': 'Default flags appended to every go command, e.g. a global '
                          '-mod=mod or -race.',
                },
                'example': {
                    'zh': 'go env -w GOFLAGS=-mod=mod\ngo env -u GOFLAGS   # 删除设置',
                    'en': 'go env -w GOFLAGS=-mod=mod\ngo env -u GOFLAGS   # unset the setting',
                },
                'pitfall': {
                    'zh': '项目根目录有 vendor/ 且 go >= 1.14 时默认自动 -mod=vendor，'
                          '此时 go get 的改动看起来「不生效」多半是这个原因。',
                    'en': 'With a vendor/ directory and go >= 1.14, -mod=vendor is '
                          'automatic — that is usually why go get edits seem to have '
                          'no effect.',
                },
            },
            {
                'cmd': 'GOPATH / GOMODCACHE / GOBIN',
                'desc': {
                    'zh': 'GOPATH 是工作区根；模块缓存在 $GOPATH/pkg/mod（即 GOMODCACHE）；安装的二进制去 GOBIN。',
                    'en': 'GOPATH is the workspace root; modules cache at '
                          '$GOPATH/pkg/mod (GOMODCACHE); installed binaries land in GOBIN.',
                },
                'example': {
                    'zh': 'go env GOPATH GOMODCACHE GOBIN\ngo env -w GOBIN=$HOME/bin   # 自定义安装位置',
                    'en': 'go env GOPATH GOMODCACHE GOBIN\ngo env -w GOBIN=$HOME/bin   # custom install location',
                },
                'pitfall': {
                    'zh': 'go install 装了工具却提示 command not found，基本都是 GOBIN 不在 PATH 里。',
                    'en': '"command not found" right after go install almost always means '
                          'GOBIN is not on your PATH.',
                },
            },
            {
                'cmd': 'CGO_ENABLED',
                'desc': {
                    'zh': '是否启用 CGO。交叉编译和纯静态二进制时设为 0。',
                    'en': 'Toggles CGO. Set it to 0 for cross-compilation and fully '
                          'static binaries.',
                },
                'example': 'CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app ./cmd/app',
                'pitfall': {
                    'zh': '关掉 CGO 后 net 的域名解析和 os/user 的用户查询会走纯 Go 实现，'
                          '行为与 glibc 略有差异（ Alpine 容器里反而更稳）。',
                    'en': 'With CGO off, net DNS resolution and os/user lookups fall back '
                          'to pure-Go implementations that behave slightly differently '
                          'from glibc (and are usually more reliable in Alpine containers).',
                },
            },
            {
                'cmd': {'zh': 'GO111MODULE（历史变量）', 'en': 'GO111MODULE (legacy)'},
                'desc': {
                    'zh': 'Go 1.11–1.22 时代的模块模式开关，Go 1.23 起已被 go 命令彻底移除，无需再设置。',
                    'en': 'The Go 1.11–1.22 module-mode switch; removed from the go '
                          'command entirely in Go 1.23 — no need to set it anymore.',
                },
                'example': {
                    'zh': 'go env GO111MODULE   # 当前版本会报：unknown go environment variable',
                    'en': 'go env GO111MODULE   # on current versions: unknown go environment variable',
                },
                'pitfall': {
                    'zh': '老 CI 脚本里的 GO111MODULE=on 可以直接删掉；如果升级后脚本报错，就是它。',
                    'en': 'Delete GO111MODULE=on from legacy CI scripts; if a script '
                          'starts failing after a toolchain upgrade, this is why.',
                },
            },
        ],
    },
    # ================================================== go.mod 指令
    {
        'id': 'modfile',
        'name': {'zh': 'go.mod 指令速查', 'en': 'go.mod Directives'},
        'desc': {
            'zh': 'go.mod 一共就这几个指令，搞懂 replace 和 retract 能解决 80% 的依赖纠纷。',
            'en': 'go.mod has only a handful of directives; mastering replace and '
                  'retract resolves 80% of dependency disputes.',
        },
        'items': [
            {
                'cmd': 'module / go / toolchain',
                'desc': {
                    'zh': '模块路径、语言版本下限、期望的工具链版本，go.mod 的头部三行。',
                    'en': 'Module path, minimum language version, and the expected '
                          'toolchain — the three header lines of go.mod.',
                },
                'example': 'module github.com/you/proj\n\ngo 1.26\n\ntoolchain go1.27.1',
                'pitfall': {
                    'zh': 'Go 1.21 起 go 指令是硬下限：工具链比它老会直接拒绝构建，而不是「试试看」。',
                    'en': 'Since Go 1.21 the go directive is a hard floor: an older '
                          'toolchain refuses to build instead of "giving it a try".',
                },
            },
            {
                'cmd': 'require',
                'desc': {
                    'zh': '声明依赖及最低版本。// indirect 注释表示间接依赖（不直接被你的代码 import）。',
                    'en': 'Declares a dependency with its minimum version. The // indirect '
                          'comment marks deps your code does not import directly.',
                },
                'example': 'require (\n\tgithub.com/gin-gonic/gin v1.10.0\n\tgolang.org/x/sys v0.24.0 // indirect\n)',
                'pitfall': {
                    'zh': 'Go 1.27 起 go mod tidy 会自动把多个 require 块合并成'
                          '「直接 + 间接」两块的标准结构，手工拆块没有意义。',
                    'en': 'Since Go 1.27, go mod tidy consolidates scattered require '
                          'blocks into the standard direct/indirect two-block layout — '
                          'hand-splitting blocks is pointless.',
                },
            },
            {
                'cmd': 'replace',
                'desc': {
                    'zh': '把某个模块替换成本地目录或 fork，调试依赖和临时打补丁的标配。',
                    'en': 'Substitutes a module with a local directory or fork — the '
                          'standard way to debug deps or apply temporary patches.',
                },
                'example': 'replace github.com/foo/bar => ../bar\n\nreplace github.com/foo/bar v1.2.3 => github.com/you/bar v1.2.4-fix',
                'pitfall': {
                    'zh': 'replace 只在主模块生效：你发布的库被别人 import 时，你库里的 replace 会被完全忽略。',
                    'en': 'replace only applies to the main module: when someone imports '
                          'your library, the replace directives inside it are ignored.',
                },
            },
            {
                'cmd': 'exclude',
                'desc': {
                    'zh': '明确排除某个有问题的版本，go 命令会当它不存在。',
                    'en': 'Explicitly excludes a broken version; the go command treats '
                          'it as non-existent.',
                },
                'example': 'exclude github.com/foo/bar v1.2.3',
                'pitfall': {
                    'zh': 'exclude 同样只在主模块生效；已发布的库撤回版本应该用 retract 而不是 exclude。',
                    'en': 'exclude is main-module-only too; to withdraw versions of a '
                          'published library use retract, not exclude.',
                },
            },
            {
                'cmd': 'retract',
                'desc': {
                    'zh': '库作者撤回自己已发布的版本（发错版本号的后悔药），go get 会自动避开。',
                    'en': 'Lets a library author withdraw published versions (the antidote '
                          'to a bad release); go get automatically avoids them.',
                },
                'example': {
                    'zh': 'retract (\n\tv1.2.0   // 误发了未完成的功能\n\tv1.1.9   // 安全问题，请升级到 v1.1.10\n)',
                    'en': 'retract (\n\tv1.2.0   // shipped an unfinished feature by mistake\n\tv1.1.9   // security issue, please upgrade to v1.1.10\n)',
                },
                'pitfall': {
                    'zh': 'retract 不删版本（代理上仍在，仍可被显式指定），只是不再被 @latest 等查询选中。',
                    'en': 'retract does not delete versions (they stay on the proxy and '
                          'can still be requested explicitly); it only removes them from '
                          'queries like @latest.',
                },
            },
        ],
    },
    # ================================================== 交叉编译与版本管理
    {
        'id': 'x',
        'name': {'zh': '交叉编译与版本管理', 'en': 'Cross-Compilation & Toolchains'},
        'desc': {
            'zh': 'Go 的交叉编译不需要目标平台的工具链，一对环境变量就够了。',
            'en': 'Go cross-compiles without any target-platform toolchain — two '
                  'environment variables are enough.',
        },
        'items': [
            {
                'cmd': 'GOOS / GOARCH',
                'desc': {
                    'zh': '指定目标操作系统与架构，直接加在 go build 前面即可交叉编译。',
                    'en': 'Target OS and architecture — prefix go build with them to '
                          'cross-compile.',
                },
                'example': 'GOOS=linux   GOARCH=amd64 go build -o app-linux-amd64   ./cmd/app\nGOOS=linux   GOARCH=arm64 go build -o app-linux-arm64   ./cmd/app\nGOOS=windows GOARCH=amd64 go build -o app.exe           ./cmd/app\nGOOS=darwin  GOARCH=arm64 go build -o app-darwin-arm64  ./cmd/app',
                'pitfall': {
                    'zh': '用到 CGO 的依赖（sqlite3 驱动等）交叉编译会失败，需要目标平台的 C 工具链，'
                          '或换纯 Go 实现（如 modernc.org/sqlite）。',
                    'en': 'Dependencies that use CGO (e.g. sqlite3 drivers) fail to '
                          'cross-compile without a target C toolchain — switch to pure-Go '
                          'alternatives like modernc.org/sqlite.',
                },
            },
            {
                'cmd': 'go tool dist list',
                'desc': {
                    'zh': '列出当前工具链支持的全部 GOOS/GOARCH 组合。',
                    'en': 'Lists every GOOS/GOARCH pair supported by your toolchain.',
                },
                'example': 'go tool dist list\ngo tool dist list | grep linux',
                'pitfall': {
                    'zh': '小众组合（如 linux/riscv64）不需要额外安装任何东西，能列出来就能编。',
                    'en': 'Exotic pairs (e.g. linux/riscv64) need no extra installation — '
                          'if it is listed, it compiles.',
                },
            },
            {
                'cmd': 'GOTOOLCHAIN',
                'desc': {
                    'zh': '工具链选择策略：auto 按 go.mod 自动下载切换（默认），local 只用本机版本。',
                    'en': 'Toolchain selection policy: auto downloads and switches per '
                          'go.mod (default); local uses only the installed version.',
                },
                'example': {
                    'zh': 'go env GOTOOLCHAIN\ngo env -w GOTOOLCHAIN=local   # 禁止自动下载工具链',
                    'en': 'go env GOTOOLCHAIN\ngo env -w GOTOOLCHAIN=local   # never download a toolchain automatically',
                },
                'pitfall': {
                    'zh': 'CI 镜像里建议显式设为 local 并预装正确版本，否则构建会现场下载工具链，慢且可能失败。',
                    'en': 'On CI images prefer local with the right version preinstalled — '
                          'otherwise builds download a toolchain on the spot, which is '
                          'slow and can fail.',
                },
            },
            {
                'cmd': '-trimpath -ldflags "-s -w"',
                'desc': {
                    'zh': '发布构建三件套：去掉本机路径、符号表与调试信息，体积能小 20–30%。',
                    'en': 'The release-build trio: strips local paths, symbol table and '
                          'DWARF info — typically 20–30% smaller binaries.',
                },
                'example': 'go build -trimpath -ldflags="-s -w" -o bin/app ./cmd/app',
                'pitfall': {
                    'zh': '-s -w 之后 panic 堆栈里的行号仍在，但无法用 delve 做源码级调试；发布件才用，日常构建别加。',
                    'en': 'After -s -w, panics still carry line numbers but source-level '
                          'debugging with delve is gone — use it for release artifacts only.',
                },
            },
            {
                'cmd': 'go version / go env',
                'desc': {
                    'zh': '确认当前工具链版本与全部环境配置，排查环境问题第一步。',
                    'en': 'Shows the active toolchain version and full environment — '
                          'the first step of any environment debugging.',
                },
                'example': {
                    'zh': 'go version\ngo env GOVERSION GOOS GOARCH GOPROXY\ngo env -json   # 机器可读的全量配置',
                    'en': 'go version\ngo env GOVERSION GOOS GOARCH GOPROXY\ngo env -json   # machine-readable dump of every setting',
                },
                'pitfall': {
                    'zh': 'go env 显示的是「生效值」，它可能来自系统环境变量、go env -w 文件或默认值三处之一。',
                    'en': 'go env shows the effective value, which can come from the OS '
                          'environment, the go env -w file, or built-in defaults.',
                },
            },
        ],
    },
]

# ---------------------------------------------------------------- 渲染

TEXT = {
    'zh': {
        'lead': '覆盖 go build/test、go mod 依赖管理、gofmt/goimports、环境变量、'
                'go.mod 指令与交叉编译，每条附可直接照抄的示例和真实踩坑点',
        'updated': '更新于',
        'ver': '适用版本：Go',
        'total': '共 ',
        'unit': ' 条',
        'search': '搜索命令、环境变量或关键词…',
        'all': '全部',
        'nohit': '没有匹配的条目，换个关键词试试。',
        'code': '示例',
        'pit': '注意',
    },
    'en': {
        'lead': 'Covers go build/test, go mod dependency management, gofmt/goimports, '
                'environment variables, go.mod directives and cross-compilation — '
                'every entry ships a copy-paste example and a real-world pitfall',
        'updated': 'Updated',
        'ver': 'Applies to Go',
        'total': '',
        'unit': ' entries',
        'search': 'Search commands, env vars or keywords…',
        'all': 'All',
        'nohit': 'No matching entry — try another keyword.',
        'code': 'Example',
        'pit': 'Watch out',
    },
}


def _esc(s):
    import html as html_mod
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def _lv(v, lang):
    """取字段值：str 表示中英共用（命令、代码），dict 表示分语言。

    示例代码里的行尾注释大多是中文，如果只写一份共用，英文页会残留中文，
    而且会被 localize() 半翻译成「兼容到指定旧 Version」这种怪句子。
    所以凡示例带注释的，一律写成 {'zh': ..., 'en': ...}。
    """
    if isinstance(v, dict):
        return v[lang]
    return v or ''


def total_items():
    return sum(len(s['items']) for s in SECTIONS)


def render_body(lang):
    """渲染速查表主体：搜索框 + 分类标签 + 分节条目卡片。

    与 news.py 同一哲学：没有 JS 时全部条目可见（默认 data-on="1"），
    JS 只做过滤，不做内容注入。
    """
    t = TEXT[lang]
    total = total_items()
    out = ['<div class="gocs" id="gocs">']

    # ---- 顶部：说明 + 搜索框 + 分类标签 ----
    out.append('  <div class="gocs-head">')
    out.append(f'    <p class="gocs-lead">{_esc(t["lead"])}</p>')
    out.append(f'    <p class="gocs-meta"><b>{_esc(t["updated"])} {UPDATED}</b>'
               f'<span class="gocs-dot">·</span>{_esc(t["ver"])} {GO_VERSION}.x'
               f'<span class="gocs-dot">·</span>{_esc(t["total"])}{total}{_esc(t["unit"])}</p>')
    out.append(f'    <input class="gocs-search" id="gocsSearch" type="search" '
               f'placeholder="{_esc(t["search"])}" aria-label="{_esc(t["search"])}">')
    out.append('    <div class="gocs-tabs" role="tablist">')
    out.append(f'      <a class="gocs-tab active" href="#gocs" data-gocs-jump="top">{_esc(t["all"])}</a>')
    for s in SECTIONS:
        out.append(f'      <a class="gocs-tab" href="#gocs-{s["id"]}" '
                   f'data-gocs-jump="{s["id"]}">{_esc(s["name"][lang])}'
                   f'<span class="gocs-tab-n">{len(s["items"])}</span></a>')
    out.append('    </div>')
    out.append('  </div>')

    # ---- 分节条目 ----
    out.append('  <div class="gocs-groups">')
    for s in SECTIONS:
        out.append(f'    <section class="gocs-group" id="gocs-{s["id"]}" data-on="1">')
        out.append(f'      <h3 class="gocs-group-head">{_esc(s["name"][lang])}'
                   f'<span class="gocs-group-desc">{_esc(s["desc"][lang])}</span></h3>')
        out.append('      <div class="gocs-items">')
        for it in s['items']:
            cmd = _lv(it['cmd'], lang)
            example = _lv(it.get('example'), lang)
            # 搜索索引：命令 + 当前语言的说明与坑点（小写，一次拼好）。
            # 只索引当前语言——把两种语言都塞进来会让英文页带上中文残留，
            # 而且对英文读者而言用中文词去搜也没有意义。
            hay = ' '.join([cmd, it['desc'][lang],
                            it.get('pitfall', {}).get(lang, ''),
                            example]).lower()
            out.append(f'        <article class="gocs-item" data-on="1" '
                       f'data-hay="{_esc(hay)}">')
            out.append(f'          <code class="gocs-cmd">{_esc(cmd)}</code>')
            out.append(f'          <p class="gocs-desc">{_esc(it["desc"][lang])}</p>')
            if example:
                out.append(f'          <div class="gocs-eg-label">{_esc(t["code"])}</div>')
                out.append(f'          <pre class="gocs-eg"><code>{_esc(example)}</code></pre>')
            if it.get('pitfall'):
                out.append(f'          <p class="gocs-pit"><b>{_esc(t["pit"])}</b>'
                           f'{_esc(it["pitfall"][lang])}</p>')
            out.append('        </article>')
        out.append('      </div>')
        out.append('    </section>')
    out.append('  </div>')
    out.append(f'  <p class="gocs-nohit" id="gocsNohit" hidden>{_esc(t["nohit"])}</p>')

    # 唯一的交互脚本：按 data-hay 过滤条目、隐藏空分组。
    # 没有这段脚本时所有条目都可见（服务端写的就是 data-on="1"）。
    out.append('''  <script>
(function () {
  var box = document.getElementById('gocsSearch');
  if (!box) return;
  var items = document.querySelectorAll('.gocs-item');
  var groups = document.querySelectorAll('.gocs-group');
  var nohit = document.getElementById('gocsNohit');
  function apply() {
    var q = box.value.trim().toLowerCase();
    var any = false;
    Array.prototype.forEach.call(items, function (it) {
      var on = !q || it.getAttribute('data-hay').indexOf(q) !== -1;
      it.setAttribute('data-on', on ? '1' : '0');
      if (on) any = true;
    });
    Array.prototype.forEach.call(groups, function (g) {
      var vis = g.querySelector('.gocs-item[data-on="1"]');
      g.setAttribute('data-on', vis ? '1' : '0');
    });
    if (nohit) nohit.hidden = any || !q;
  }
  box.addEventListener('input', apply);
})();
</script>''')
    out.append('</div>')
    return '\n'.join(out)
