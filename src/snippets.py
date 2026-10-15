# -*- coding: utf-8 -*-
"""常用代码片段库（/snippets/）：数据 + 构建期渲染。

与 cheatsheet.py / news.py 同一哲学：
  - 内容构建期烘焙进 HTML，禁用 JS 时全部片段完整可见（默认 data-on="1"），
    爬虫不执行 JS 也能读到每一条代码；
  - 内联 JS 只做两件锦上添花的事：语言筛选 + 关键词过滤；复制按钮走 core.js
    的 copyTextById（news_tpl 只内联 core.js，不引编辑器与 CodeMirror）。

条目维护约定：
  - title / desc 必须是 {'zh': ..., 'en': ...}（页面级文案，两种语言都要人工过）
  - code 中英共用一份，**注释统一写英文**：中文注释要么写成双语两份，
    要么在英文页留残；统一英文注释是从源头规避该问题的最简做法
  - 片段按「解决了什么真实问题」选，不追求语法全覆盖；能附坑点就附
"""

UPDATED = '2026-10-15'

TEXT = {
    'zh': {
        'lead': '日常写代码反复会用的片段，按语言分组，每条一键复制。'
                '代码注释统一用英文，可以直接嵌进任何项目。',
        'updated': '更新于',
        'total': '共 ',
        'unit': ' 条',
        'tip': '点语言标签筛选，搜索框按标题、说明与代码全文过滤',
        'search': '搜索标题、说明或代码…',
        'all': '全部',
        'nohit': '没有匹配的代码片段，换个关键词或语言试试',
        'copy': '复制',
    },
    'en': {
        'lead': 'Snippets you reach for again and again, grouped by language, '
                'one click to copy. Comments are in English so they drop into '
                'any project as-is.',
        'updated': 'Updated',
        'total': '',
        'unit': ' snippets',
        'tip': 'Click a language tab to filter; the search box matches titles, '
               'descriptions and code',
        'search': 'Search titles, descriptions or code…',
        'all': 'All',
        'nohit': 'No matching snippets — try another keyword or language',
        'copy': 'Copy',
    },
}

SECTIONS = [
    # ================================================== Go
    {
        'id': 'go',
        'name': {'zh': 'Go', 'en': 'Go'},
        'desc': {
            'zh': '标准库能搞定的事就不引第三方：超时、并发、解码与文件读取的高频写法。',
            'en': 'High-frequency Go patterns from the standard library: timeouts, '
                  'concurrency, decoding and file reading.',
        },
        'items': [
            {
                'title': {'zh': '读取环境变量（带默认值）', 'en': 'Read env var with a default'},
                'desc': {
                    'zh': '变量未设置或为空白时回退到默认值，避免 os.Getenv 直接返回空串造成的误判。',
                    'en': 'Fall back when the var is unset or blank, so an empty '
                          'string never silently wins.',
                },
                'code': '''func getEnv(key, fallback string) string {
\tif v := strings.TrimSpace(os.Getenv(key)); v != "" {
\t\treturn v
\t}
\treturn fallback
}''',
            },
            {
                'title': {'zh': 'HTTP 请求加超时（context）', 'en': 'HTTP request with timeout (context)'},
                'desc': {
                    'zh': '超时或取消都会以 error 从 Do 返回且 resp 为 nil——拿到 err 先返回，不要解引用 resp。',
                    'en': 'On timeout or cancellation Do returns an error and resp '
                          'is nil — return early, never dereference resp.',
                },
                'code': '''ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
if err != nil {
\treturn err
}
resp, err := http.DefaultClient.Do(req)
if err != nil {
\treturn err // timeout/cancel: context.DeadlineExceeded / Canceled
}
defer resp.Body.Close()''',
            },
            {
                'title': {'zh': '等待并发任务并收集全部错误', 'en': 'Wait for concurrent tasks, collect all errors'},
                'desc': {
                    'zh': 'WaitGroup 等全部协程结束，互斥锁收集每个任务的错误，最后 errors.Join 合成一条（Go 1.20+）。',
                    'en': 'WaitGroup joins every goroutine, a mutex collects each '
                          'error, errors.Join merges them (Go 1.20+).',
                },
                'code': '''var (
\twg   sync.WaitGroup
\tmu   sync.Mutex
\terrs []error
)
for _, u := range urls {
\twg.Add(1)
\tgo func(u string) {
\t\tdefer wg.Done()
\t\tif _, err := fetch(u); err != nil {
\t\t\tmu.Lock()
\t\t\terrs = append(errs, err)
\t\t\tmu.Unlock()
\t\t}
\t}(u)
}
wg.Wait()
return errors.Join(errs...)''',
            },
            {
                'title': {'zh': '按行读文件（兼容超长行）', 'en': 'Read a file line by line (long lines safe)'},
                'desc': {
                    'zh': 'Scanner 默认单行上限 64 KB，超长行会静默停止而非报错——用 Buffer 调大并检查 sc.Err()。',
                    'en': 'Scanner stops silently on lines over 64 KB by default — '
                          'raise the cap with Buffer and always check sc.Err().',
                },
                'code': '''f, err := os.Open(path)
if err != nil {
\treturn err
}
defer f.Close()

sc := bufio.NewScanner(f)
sc.Buffer(make([]byte, 0, 64*1024), 1024*1024) // raise the per-line cap to 1 MB
for sc.Scan() {
\tline := sc.Text()
\t_ = line
}
return sc.Err() // long lines surface here: bufio.Scanner: token too long''',
            },
            {
                'title': {'zh': '严格 JSON 解码（拒绝未知字段）', 'en': 'Strict JSON decoding (reject unknown fields)'},
                'desc': {
                    'zh': '解析配置或 API 响应时打开它，字段名拼错立刻暴露，不会静默丢字段。',
                    'en': 'Decoding configs or API payloads with it makes a '
                          'misspelled field fail loudly instead of vanishing.',
                },
                'code': '''dec := json.NewDecoder(resp.Body)
dec.DisallowUnknownFields() // a misspelled field now fails loudly
var cfg Config
if err := dec.Decode(&cfg); err != nil {
\treturn err
}''',
            },
            {
                'title': {'zh': '正确停止 Ticker', 'en': 'Stop a Ticker properly'},
                'desc': {
                    'zh': 'NewTicker 不配 Stop 会泄漏底层定时器；用 done channel 让循环可退出。',
                    'en': 'NewTicker without Stop leaks the runtime timer; a done '
                          'channel lets the loop exit.',
                },
                'code': '''ticker := time.NewTicker(time.Second)
defer ticker.Stop()
for {
\tselect {
\tcase <-ticker.C:
\t\t// runs every second
\tcase <-done:
\t\treturn
\t}
}''',
            },
            {
                'title': {'zh': '原子计数器（无锁累加）', 'en': 'Atomic counter (lock-free)'},
                'desc': {
                    'zh': 'atomic.Int64（Go 1.19+）比 mutex + int64 轻，也不会忘记加锁。',
                    'en': 'atomic.Int64 (Go 1.19+) is lighter than mutex + int64 '
                          'and impossible to forget to lock.',
                },
                'code': '''var hits atomic.Int64
hits.Add(1)
total := hits.Load()''',
            },
            {
                'title': {'zh': 'defer 捕获 panic 转为错误', 'en': 'Turn panic into error with defer'},
                'desc': {
                    'zh': '在可能 panic 的边界函数用命名返回值 + defer recover，把崩溃变成可处理的 error。',
                    'en': 'At boundaries that may panic, a named return plus '
                          'deferred recover turns a crash into a handleable error.',
                },
                'code': '''defer func() {
\tif r := recover(); r != nil {
\t\terr = fmt.Errorf("panic: %v", r)
\t}
}()''',
            },
        ],
    },
    # ================================================== Python
    {
        'id': 'python',
        'name': {'zh': 'Python', 'en': 'Python'},
        'desc': {
            'zh': '数据处理与网络请求里最常写错的几处：保序去重、超时元组、时区与可变默认值。',
            'en': 'The Python spots that bite most often: order-preserving '
                  'dedupe, timeout tuples, timezones and mutable defaults.',
        },
        'items': [
            {
                'title': {'zh': '列表去重且保持顺序', 'en': 'Deduplicate a list, keep order'},
                'desc': {
                    'zh': 'dict.fromkeys 保序去重；set 会打乱顺序，手写循环更慢。',
                    'en': 'dict.fromkeys dedupes while preserving order; set '
                          'scrambles it and a manual loop is slower.',
                },
                'code': '''def dedupe(items):
\treturn list(dict.fromkeys(items))''',
            },
            {
                'title': {'zh': '字典按值排序取前 N', 'en': 'Sort a dict by value, take top N'},
                'desc': {
                    'zh': 'sorted 配 key lambda 按值排，reverse=True 取高频前 10。',
                    'en': 'Sort items by value with a key lambda; reverse=True '
                          'gives the top 10 most frequent.',
                },
                'code': '''top = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)[:10]''',
            },
            {
                'title': {'zh': 'requests 自动重试（指数退避）', 'en': 'requests with retries (exponential backoff)'},
                'desc': {
                    'zh': 'Session 挂 HTTPAdapter 配置重试；timeout 必须是元组，只写一个数字仅约束读取。',
                    'en': 'Mount a retrying HTTPAdapter on a Session. timeout must '
                          'be a tuple — a bare number only bounds the read.',
                },
                'code': '''from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(
\ttotal=3, backoff_factor=0.5,
\tstatus_forcelist=[429, 500, 502, 503, 504],
)))
resp = session.get(url, timeout=(3, 10))  # (connect timeout, read timeout)''',
            },
            {
                'title': {'zh': '时区安全的当前时间', 'en': 'Timezone-aware now()'},
                'desc': {
                    'zh': '不带时区的 now() 是本地墙上时间，跨时区部署会错；用 zoneinfo 显式指定（3.9+，无需 pytz）。',
                    'en': 'Naive now() is local wall time and drifts across '
                          'deployments; pin the zone with zoneinfo (3.9+).',
                },
                'code': '''from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Shanghai"))''',
            },
            {
                'title': {'zh': '递归查找文件并按时间排序', 'en': 'Recursively find files, newest first'},
                'desc': {
                    'zh': 'pathlib 的 rglob 递归匹配；配 stat().st_mtime 按修改时间排序。',
                    'en': "pathlib's rglob matches recursively; pair with "
                          'stat().st_mtime to sort by modification time.',
                },
                'code': '''from pathlib import Path

logs = sorted(Path("var/log").rglob("*.log"), key=lambda p: p.stat().st_mtime)''',
            },
            {
                'title': {'zh': '批量重命名文件', 'en': 'Batch-rename files'},
                'desc': {
                    'zh': 'enumerate 从 1 编号，:03d 补零保证字典序；先 sorted 保证结果可复现。',
                    'en': 'Number from 1 and zero-pad with :03d so names sort '
                          'correctly; sort first for reproducible runs.',
                },
                'code': '''from pathlib import Path

for i, p in enumerate(sorted(Path("photos").glob("*.jpg")), 1):
\tp.rename(p.with_name(f"photo-{i:03d}.jpg"))''',
            },
            {
                'title': {'zh': 'dataclass 的可变默认值', 'en': 'Mutable defaults in dataclasses'},
                'desc': {
                    'zh': '字段默认值必须不可变，列表/字典用 default_factory，直接写 [] 会 ValueError。',
                    'en': 'Field defaults must be immutable; use default_factory '
                          'for lists/dicts or Python raises ValueError.',
                },
                'code': '''from dataclasses import dataclass, field

@dataclass
class Cart:
\titems: list = field(default_factory=list)  # not items: list = []''',
            },
            {
                'title': {'zh': '计时上下文管理器', 'en': 'Timing context manager'},
                'desc': {
                    'zh': 'perf_counter 是单调时钟，不受系统时间调整影响；finally 保证异常时也输出耗时。',
                    'en': 'perf_counter is monotonic and immune to clock '
                          'adjustments; finally prints even on exceptions.',
                },
                'code': '''from contextlib import contextmanager
from time import perf_counter

@contextmanager
def timer(label):
\tstart = perf_counter()
\ttry:
\t\tyield
\tfinally:
\t\tprint(f"{label}: {perf_counter() - start:.3f}s")

with timer("query"):
\trun_query()''',
            },
        ],
    },
    # ================================================== JavaScript
    {
        'id': 'js',
        'name': {'zh': 'JavaScript', 'en': 'JavaScript'},
        'desc': {
            'zh': '现代浏览器原生能力优先：structuredClone、AbortSignal、URLSearchParams。',
            'en': 'Prefer native browser APIs: structuredClone, AbortSignal, '
                  'URLSearchParams.',
        },
        'items': [
            {
                'title': {'zh': '深拷贝（原生）', 'en': 'Deep clone (native)'},
                'desc': {
                    'zh': 'structuredClone 支持 Date、Map、Set 与循环引用，不需要再引三方库。',
                    'en': 'structuredClone handles Date, Map, Set and circular '
                          'refs — no library needed.',
                },
                'code': '''const copy = structuredClone(obj);''',
            },
            {
                'title': {'zh': '防抖', 'en': 'Debounce'},
                'desc': {
                    'zh': '停止触发 ms 毫后才执行，适合搜索框；要第一次就响应需改 leading 版。',
                    'en': 'Fires after ms of quiet — ideal for search inputs; '
                          'switch to a leading variant if the first keystroke must respond.',
                },
                'code': '''function debounce(fn, ms = 300) {
\tlet t;
\treturn (...args) => {
\t\tclearTimeout(t);
\t\tt = setTimeout(() => fn(...args), ms);
\t};
}''',
            },
            {
                'title': {'zh': 'Promise 失败自动重试', 'en': 'Retry a failing promise'},
                'desc': {
                    'zh': '指数退避（delay × 2^i），最后一次失败才向上抛。',
                    'en': 'Exponential backoff (delay × 2^i); only rethrows on '
                          'the final attempt.',
                },
                'code': '''async function retry(fn, times = 3, delay = 500) {
\tfor (let i = 0; i < times; i++) {
\t\ttry {
\t\t\treturn await fn();
\t\t} catch (e) {
\t\t\tif (i === times - 1) throw e;
\t\t\tawait new Promise((r) => setTimeout(r, delay * 2 ** i));
\t\t}
\t}
}''',
            },
            {
                'title': {'zh': 'fetch 加超时', 'en': 'fetch with a timeout'},
                'desc': {
                    'zh': 'AbortSignal.timeout 一行搞定；Safari 16.4+/Node 17.3+ 才支持，旧环境用 AbortController + setTimeout。',
                    'en': 'AbortSignal.timeout is one line; it needs Safari 16.4+ '
                          '/Node 17.3+ — fall back to AbortController + setTimeout.',
                },
                'code': '''const resp = await fetch(url, { signal: AbortSignal.timeout(5000) });''',
            },
            {
                'title': {'zh': '解析 URL 查询参数', 'en': 'Parse URL query params'},
                'desc': {
                    'zh': 'get 缺失返回 null，用 ?? 给默认值；直接 Number(null) 会得到 0 掩盖错误。',
                    'en': 'get returns null when missing — default it with ??; '
                          'Number(null) is 0 and hides bugs.',
                },
                'code': '''const params = new URLSearchParams(location.search);
const page = Number(params.get("page") ?? 1);''',
            },
            {
                'title': {'zh': '数组分块', 'en': 'Chunk an array'},
                'desc': {
                    'zh': 'Array.from 一次生成全部块，比反复 splice 原数组安全。',
                    'en': 'Build all chunks up front — safer than splicing the '
                          'original array in place.',
                },
                'code': '''const chunk = (arr, size) =>
\tArray.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
\t\tarr.slice(i * size, i * size + size));''',
            },
            {
                'title': {'zh': '可中断的 sleep', 'en': 'Interruptible sleep'},
                'desc': {
                    'zh': '轮询等待比 setInterval 干净；需要响应外部取消信号时改用 AbortSignal 版。',
                    'en': 'Cleaner than setInterval for poll-style waits; use an '
                          'AbortSignal variant when cancellation must interrupt it.',
                },
                'code': '''const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(1000);''',
            },
            {
                'title': {'zh': '数组去重', 'en': 'Deduplicate an array'},
                'desc': {
                    'zh': 'Set 一行去重，NaN 也能正确去重；对象按引用去重。',
                    'en': 'One line with Set; NaN dedupes correctly, objects '
                          'dedupe by reference.',
                },
                'code': '''const uniq = [...new Set(arr)];''',
            },
        ],
    },
    # ================================================== Shell
    {
        'id': 'shell',
        'name': {'zh': 'Shell', 'en': 'Shell'},
        'desc': {
            'zh': '脚本健壮性与跨平台差异：空格文件名、sed -i、退出码与临时目录清理。',
            'en': 'Robustness and portability: filenames with spaces, sed -i, '
                  'exit codes and temp-dir cleanup.',
        },
        'items': [
            {
                'title': {'zh': '严格模式', 'en': 'Strict mode'},
                'desc': {
                    'zh': '-e 遇错即停、-u 未定义变量即停、pipefail 让管道中途失败也报错；改 IFS 防空格拆词。',
                    'en': '-e exits on error, -u on unset vars, pipefail surfaces '
                          'mid-pipeline failures; reset IFS so spaces don\'t split words.',
                },
                'code': '''set -euo pipefail
IFS=$'\\n\\t\'''',
            },
            {
                'title': {'zh': '安全遍历含空格的文件名', 'en': 'Iterate filenames with spaces safely'},
                'desc': {
                    'zh': '-print0 + read -d \'\' 用 NUL 分隔，空格、换行都不会拆开文件名。',
                    'en': '-print0 with read -d \'\' splits on NUL, so spaces and '
                          'newlines in filenames stay intact.',
                },
                'code': '''find . -name '*.log' -print0 | while IFS= read -r -d '' f; do
\tgzip "$f"
done''',
            },
            {
                'title': {'zh': '解析命令行参数', 'en': 'Parse command-line options'},
                'desc': {
                    'zh': 'getopts 是 POSIX 内置，处理 -f value / -v 最稳；最后 shift 吃掉已解析部分。',
                    'en': 'getopts is a POSIX builtin — the safest way to parse '
                          'short options; finish with shift to drop what was consumed.',
                },
                'code': '''while getopts "f:v" opt; do
\tcase "$opt" in
\tf) file="$OPTARG" ;;
\tv) verbose=1 ;;
\t*) echo "usage: $0 [-f file] [-v]" >&2; exit 1 ;;
\tesac
done
shift $((OPTIND - 1))''',
            },
            {
                'title': {'zh': '跨平台原地替换（sed -i）', 'en': 'Portable in-place replace (sed -i)'},
                'desc': {
                    'zh': 'macOS 的 sed -i 要求一个后缀参数，照抄 Linux 写法会报 undefined variable。',
                    'en': 'macOS sed -i requires a suffix argument; copying the '
                          'Linux form verbatim fails with an undefined-variable error.',
                },
                'code': '''# GNU sed (Linux)
sed -i 's/foo/bar/g' file.txt
# BSD sed (macOS): empty suffix = no backup
sed -i '' 's/foo/bar/g' file.txt''',
            },
            {
                'title': {'zh': '并行批处理', 'en': 'Parallel batch processing'},
                'desc': {
                    'zh': '-P 指定并行度（nproc 取核数），-I{} 占位符独立拼命令，适合 CPU 密集任务。',
                    'en': '-P sets parallelism (nproc for cores) and -I{} builds '
                          'one command per item — good for CPU-bound jobs.',
                },
                'code': '''ls *.jpg | xargs -P "$(nproc)" -I{} convert {} -resize 800x {}.webp''',
            },
            {
                'title': {'zh': '临时目录自动清理', 'en': 'Self-cleaning temp directory'},
                'desc': {
                    'zh': 'mktemp -d 建唯一目录，trap 绑 EXIT 保证任何退出路径都清理，避免 /tmp 堆积。',
                    'en': 'mktemp -d creates a unique dir; trap on EXIT cleans it '
                          'on every exit path.',
                },
                'code': '''tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT''',
            },
            {
                'title': {'zh': '查看端口占用', 'en': 'Find what holds a port'},
                'desc': {
                    'zh': 'lsof -i :端口 列出占用进程；精简容器没有 lsof 时用 ss 替代。',
                    'en': 'lsof -i :port lists the owning process; on slim '
                          'containers without lsof, use ss instead.',
                },
                'code': '''lsof -i :8080         # macOS / Linux
ss -tlnp | grep 8080 # Linux fallback when lsof is missing''',
            },
            {
                'title': {'zh': '后台常驻并写日志', 'en': 'Run in background with logs'},
                'desc': {
                    'zh': 'nohup + & 脱离终端，>> 追加日志、2>&1 合并 stderr；务必存 PID，否则事后找不到进程。',
                    'en': 'nohup + & detaches from the terminal; >> appends and '
                          '2>&1 merges stderr — always save the PID.',
                },
                'code': '''nohup ./worker >> worker.log 2>&1 &
echo $! > worker.pid''',
            },
        ],
    },
    # ================================================== SQL
    {
        'id': 'sql',
        'name': {'zh': 'SQL', 'en': 'SQL'},
        'desc': {
            'zh': 'PostgreSQL 方言：深分页、窗口函数、upsert 与递归查询。',
            'en': 'PostgreSQL dialect: deep pagination, window functions, '
                  'upsert and recursive queries.',
        },
        'items': [
            {
                'title': {'zh': 'Keyset 分页（替代 OFFSET）', 'en': 'Keyset pagination (over OFFSET)'},
                'desc': {
                    'zh': 'OFFSET 越翻越慢；以上一页最后一行为游标做行值比较，直接走索引。',
                    'en': 'OFFSET slows with depth; compare the last row of the '
                          'previous page as a cursor so the index is used.',
                },
                'code': '''SELECT id, title FROM posts
WHERE (created_at, id) < (:cursor_at, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;''',
            },
            {
                'title': {'zh': '每组取最新一行', 'en': 'Latest row per group'},
                'desc': {
                    'zh': 'ROW_NUMBER 窗口函数按分组排序取 rn=1，比 GROUP BY 后自连接更直观更快。',
                    'en': 'ROW_NUMBER per partition with rn = 1 beats '
                          'group-by-then-self-join in clarity and speed.',
                },
                'code': '''SELECT * FROM (
\tSELECT *, ROW_NUMBER() OVER (
\t\tPARTITION BY user_id ORDER BY created_at DESC
\t) AS rn
\tFROM orders
) t WHERE rn = 1;''',
            },
            {
                'title': {'zh': '存在则更新（upsert）', 'en': 'Insert or update (upsert)'},
                'desc': {
                    'zh': 'ON CONFLICT 是 PostgreSQL/SQLite 写法；MySQL 用 ON DUPLICATE KEY UPDATE。',
                    'en': 'ON CONFLICT is PostgreSQL/SQLite; MySQL spells it '
                          'ON DUPLICATE KEY UPDATE.',
                },
                'code': '''INSERT INTO stats (day, views) VALUES (DATE '2026-10-15', 1)
ON CONFLICT (day) DO UPDATE SET views = stats.views + 1;''',
            },
            {
                'title': {'zh': '递归查询树形结构', 'en': 'Recursive tree query'},
                'desc': {
                    'zh': '锚点（根节点）+ 递归成员（接上前一层）；忘记终止条件会无限递归。',
                    'en': 'An anchor (roots) plus a recursive term joining the '
                          'previous level; a missing termination condition loops forever.',
                },
                'code': '''WITH RECURSIVE tree AS (
\tSELECT id, parent_id, name, 0 AS depth
\tFROM categories WHERE parent_id IS NULL
\tUNION ALL
\tSELECT c.id, c.parent_id, c.name, t.depth + 1
\tFROM categories c JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, name;''',
            },
            {
                'title': {'zh': '累计求和', 'en': 'Running total'},
                'desc': {
                    'zh': '窗口默认帧就是 UNBOUNDED PRECEDING→CURRENT ROW，显式写出避免读代码的人猜。',
                    'en': 'The default frame is UNBOUNDED PRECEDING → CURRENT ROW; '
                          'write it out so readers don\'t have to guess.',
                },
                'code': '''SELECT day, views,
\tSUM(views) OVER (
\t\tORDER BY day
\t\tROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
\t) AS total
FROM daily_views;''',
            },
            {
                'title': {'zh': '按周/月聚合', 'en': 'Truncate to month/week'},
                'desc': {
                    'zh': 'date_trunc 把时间截到月/周/日；GROUP BY 1 按位置引用第一列。',
                    'en': 'date_trunc snaps timestamps to month/week/day; '
                          'GROUP BY 1 references the first column by position.',
                },
                'code': '''SELECT date_trunc('month', created_at) AS month, COUNT(*)
FROM orders
GROUP BY 1 ORDER BY 1;''',
            },
            {
                'title': {'zh': '计算每行占比', 'en': 'Per-row share of total'},
                'desc': {
                    'zh': 'SUM(...) OVER () 空帧即全表总和；整数相除会截断，先转 numeric。',
                    'en': 'SUM(...) OVER () with an empty frame is the grand total; '
                          'cast to numeric first or integer division truncates.',
                },
                'code': '''SELECT category, amount,
\tamount::numeric / SUM(amount) OVER () AS share
FROM sales;''',
            },
            {
                'title': {'zh': '查找重复记录', 'en': 'Find duplicate rows'},
                'desc': {
                    'zh': '加唯一索引前先跑它确认没有存量重复，否则建索引直接失败。',
                    'en': 'Run it before adding a unique index — existing '
                          'duplicates make the creation fail.',
                },
                'code': '''SELECT email, COUNT(*) FROM users
GROUP BY email
HAVING COUNT(*) > 1;''',
            },
        ],
    },
    # ================================================== Git
    {
        'id': 'git',
        'name': {'zh': 'Git', 'en': 'Git'},
        'desc': {
            'zh': '日常救援与历史整理：撤销、拆分、排查与清理。',
            'en': 'Everyday rescue and history hygiene: undo, split, bisect '
                  'and clean up.',
        },
        'items': [
            {
                'title': {'zh': '撤销提交但保留改动', 'en': 'Undo a commit, keep the changes'},
                'desc': {
                    'zh': 'reset --mixed 只影响本地；提交已推远端且别人可能拉过时必须用 revert。',
                    'en': 'reset --mixed is local-only; once pushed and possibly '
                          'pulled, use revert instead.',
                },
                'code': '''git reset --mixed HEAD~1   # changes back to worktree, commit gone
# if pushed and possibly pulled, revert instead:
git revert HEAD''',
            },
            {
                'title': {'zh': '修改最近一次提交', 'en': 'Amend the latest commit'},
                'desc': {
                    'zh': '--amend 重写最近提交；已推送的提交 amend 后需强推，先确认没人基于它工作。',
                    'en': '--amend rewrites the latest commit; amending a pushed '
                          'one needs a force push — confirm nobody has built on it.',
                },
                'code': '''git commit --amend -m "a more accurate commit message"
# include the file you forgot
git add forgotten.txt && git commit --amend --no-edit''',
            },
            {
                'title': {'zh': '只提交文件的一部分', 'en': 'Stage part of a file'},
                'desc': {
                    'zh': '-p 按 hunk 交互暂存，把一个文件里的两处改动拆成两个提交。',
                    'en': '-p stages hunk by hunk, splitting two changes in one '
                          'file into separate commits.',
                },
                'code': '''git add -p            # interactive hunk-by-hunk staging
git add -p path.txt   # only this file''',
            },
            {
                'title': {'zh': '二分查找引入 bug 的提交', 'en': 'Bisect the commit that broke it'},
                'desc': {
                    'zh': '二分把 N 次排查降到 log₂N；脚本能自动判断时用 git bisect run。',
                    'en': 'Binary search cuts N investigations to log₂N; when a '
                          'script can decide, git bisect run automates it.',
                },
                'code': '''git bisect start
git bisect bad                 # HEAD is bad
git bisect good v1.2.0         # this tag is good
# git checks out candidates; just mark good/bad, then:
git bisect reset''',
            },
            {
                'title': {'zh': '清理已合并分支', 'en': 'Delete merged branches'},
                'desc': {
                    'zh': '--merged 只列已合入的；grep 排除当前分支与主分支自己，-d 保证未合并删不掉。',
                    'en': '--merged lists only merged branches; grep excludes the '
                          'current and main branches, and -d refuses unmerged ones.',
                },
                'code': '''git branch --merged main | grep -v '^\\*\\|main' | xargs -r git branch -d''',
            },
            {
                'title': {'zh': '从历史中删除文件', 'en': 'Purge a file from history'},
                'desc': {
                    'zh': '误提交密钥后必须改历史 + 强推 + 吊销密钥，三步缺一不可；用 filter-repo 而非已废弃的 filter-branch。',
                    'en': 'After committing secrets: rewrite, force push AND '
                          'rotate the key. Use filter-repo, not the deprecated filter-branch.',
                },
                'code': '''git filter-repo --path secrets.env --invert-paths
# then force push; rotate the key - rewriting != un-leaking''',
            },
        ],
    },
]


def _esc(s):
    import html as html_mod
    return html_mod.escape(str(s if s is not None else ''), quote=True)


def _lv(v, lang):
    """str 表示中英共用，dict 表示分语言。"""
    if isinstance(v, dict):
        return v[lang]
    return v or ''


def total_snippets():
    return sum(len(s['items']) for s in SECTIONS)


def render_body(lang):
    """渲染片段库主体：说明 + 语言标签 + 搜索框 + 分节卡片（带复制按钮）。

    与 cheatsheet.py 同型：没有 JS 时全部片段可见（data-on="1"），
    JS 只做筛选；复制按钮依赖 core.js 的 copyTextById（news_tpl 已内联）。
    """
    t = TEXT[lang]
    total = total_snippets()
    out = ['<div class="snp" id="snp">']

    # ---- 顶部：说明 + meta + 语言标签 + 搜索框 ----
    out.append('  <div class="snp-head">')
    out.append(f'    <p class="snp-lead">{_esc(t["lead"])}</p>')
    out.append(f'    <p class="snp-meta"><b>{_esc(t["updated"])} {UPDATED}</b>'
               f'<span class="snp-dot">·</span>{_esc(t["total"])}{total}{_esc(t["unit"])}'
               f'<span class="snp-dot">·</span>{_esc(t["tip"])}</p>')
    out.append('    <div class="snp-tabs" role="tablist">')
    out.append(f'      <button type="button" class="snp-tab active" data-snp-lang="all">'
               f'{_esc(t["all"])}<span class="snp-tab-n">{total}</span></button>')
    for s in SECTIONS:
        out.append(f'      <button type="button" class="snp-tab" data-snp-lang="{s["id"]}">'
                   f'{_esc(s["name"][lang])}<span class="snp-tab-n">{len(s["items"])}</span></button>')
    out.append('    </div>')
    out.append(f'    <input class="snp-search" id="snpSearch" type="search" '
               f'placeholder="{_esc(t["search"])}" aria-label="{_esc(t["search"])}">')
    out.append('  </div>')

    # ---- 分节片段卡片 ----
    idx = 0
    out.append('  <div class="snp-groups">')
    for s in SECTIONS:
        out.append(f'    <section class="snp-group" id="snp-{s["id"]}" data-lang="{s["id"]}" data-on="1">')
        out.append(f'      <h3 class="snp-group-head">{_esc(s["name"][lang])}'
                   f'<span class="snp-group-desc">{_esc(s["desc"][lang])}</span></h3>')
        out.append('      <div class="snp-items">')
        for it in s['items']:
            title = it['title'][lang]
            desc = it['desc'][lang]
            code = it['code']
            # 搜索索引只放当前语言（混两种语言会让英文页带中文残留，
            # 且对读者而言用另一种语言搜索没有意义）
            hay = ' '.join([title, desc, code, s['name'][lang]]).lower()
            out.append(f'        <article class="snp-item" data-on="1" data-lang="{s["id"]}" '
                       f'data-hay="{_esc(hay)}">')
            out.append(f'          <div class="snp-item-head">')
            out.append(f'            <h4 class="snp-title">{_esc(title)}</h4>')
            out.append(f'            <span class="snp-lang">{_esc(s["name"][lang])}</span>')
            out.append(f'          </div>')
            out.append(f'          <p class="snp-desc">{_esc(desc)}</p>')
            out.append(f'          <div class="snp-code-wrap">')
            out.append(f'            <pre class="snp-code" id="snp-code-{idx}"><code>{_esc(code)}</code></pre>')
            out.append(f'            <button type="button" class="btn btn-sm snp-copy" '
                       f'onclick="copyTextById(\'snp-code-{idx}\')">{_esc(t["copy"])}</button>')
            out.append(f'          </div>')
            out.append(f'        </article>')
            idx += 1
        out.append('      </div>')
        out.append('    </section>')
    out.append('  </div>')
    out.append(f'  <p class="snp-nohit" id="snpNohit" hidden>{_esc(t["nohit"])}</p>')

    # 唯一的交互脚本：语言标签 + 搜索框组合过滤；无脚本时全部可见。
    # 复制走 core.js 的 copyTextById，不在这里重复实现。
    out.append('''  <script>
(function () {
  var box = document.getElementById('snpSearch');
  var tabs = document.querySelectorAll('.snp-tab[data-snp-lang]');
  var items = document.querySelectorAll('.snp-item');
  var groups = document.querySelectorAll('.snp-group');
  var nohit = document.getElementById('snpNohit');
  var lang = 'all';
  function apply() {
    var q = box ? box.value.trim().toLowerCase() : '';
    var any = false;
    Array.prototype.forEach.call(items, function (it) {
      var on = (lang === 'all' || it.getAttribute('data-lang') === lang) &&
               (!q || it.getAttribute('data-hay').indexOf(q) !== -1);
      it.setAttribute('data-on', on ? '1' : '0');
      if (on) any = true;
    });
    Array.prototype.forEach.call(groups, function (g) {
      var vis = g.querySelector('.snp-item[data-on="1"]');
      g.setAttribute('data-on', vis ? '1' : '0');
    });
    if (nohit) nohit.hidden = any;
  }
  Array.prototype.forEach.call(tabs, function (tab) {
    tab.addEventListener('click', function () {
      lang = tab.getAttribute('data-snp-lang');
      Array.prototype.forEach.call(tabs, function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      apply();
    });
  });
  if (box) box.addEventListener('input', apply);
  apply();
})();
</script>''')
    out.append('</div>')
    return '\n'.join(out)
