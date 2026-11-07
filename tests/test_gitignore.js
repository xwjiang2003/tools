// 单测：gitignore 生成器的纯函数与内置模板库自检
// 覆盖：行规范化、规则抽取、通配匹配、"取反规则失效"检测、多模板合并去重、
//       用户自定义优先级，以及模板库本身的完整性（key 唯一、预设引用有效、无中文）。
// 运行：node tests/test_gitignore.js
const assert = require('assert');
const path = require('path');
const Q = require(path.join(__dirname, '..', 'src', 'js', 'gitignore.js'));

let pass = 0;
const fails = [];
function eq(actual, expected, msg) {
    try { assert.deepStrictEqual(actual, expected); pass++; }
    catch (e) {
        fails.push(msg + '\n    期望 ' + JSON.stringify(expected) + '\n    实际 ' + JSON.stringify(actual));
    }
}
function ok(cond, msg) {
    if (cond) pass++;
    else fails.push(msg);
}

// ---------------------------------------------------------------- 行规范化
eq(Q.giCleanLine('  node_modules/  '), 'node_modules/', 'clean: 两端空白去掉');
eq(Q.giCleanLine('\tnode_modules/\r'), 'node_modules/', 'clean: 制表符与回车');
eq(Q.giCleanLine(null), '', 'clean: null 不抛异常');
eq(Q.giCleanLine('   '), '', 'clean: 纯空白 → 空串');

// ---------------------------------------------------------------- 规则抽取
eq(Q.giRulesOf('# 注释\nnode_modules/\n\n*.log\n'), ['node_modules/', '*.log'],
    'rules: 去注释与空行，保序');
eq(Q.giRulesOf(''), [], 'rules: 空串');
eq(Q.giRulesOf('#只有注释'), [], 'rules: 只有注释');
eq(Q.giRulesOf('a\r\nb'), ['a', 'b'], 'rules: CRLF 能正确切行');

// ---------------------------------------------------------------- 自定义块
eq(Q.giCustomLines('a\n\na\nb\n'), ['a', 'b'], 'custom: 块内精确去重');
eq(Q.giCustomLines('# 我的规则\nsecret.txt'), ['# 我的规则', 'secret.txt'],
    'custom: 注释原样保留');
eq(Q.giCustomLines('  dist/  \r\n'), ['dist/'], 'custom: 行规范化');

// ---------------------------------------------------------------- 通配匹配
ok(Q.giPatternHit('*.log', 'app.log'), 'glob: *.log 命中 app.log');
// git 的锚定规则：模式里没有斜杠就不锚定，可以匹配任意深度
ok(Q.giPatternHit('*.log', 'sub/app.log'), 'glob: 非锚定模式匹配任意层级（git 语义）');
ok(!Q.giPatternHit('sub/*.log', 'a/sub/app.log'), 'glob: 含斜杠即锚定到根，不匹配深层同路径');
ok(Q.giPatternHit('sub/*.log', 'sub/app.log'), 'glob: 锚定模式命中根下对应路径');
ok(Q.giPatternHit('*.jar', 'gradle/wrapper/gradle-wrapper.jar'),
    'glob: *.jar 命中深层同名文件（取反规则判定的前提）');
ok(Q.giPatternHit('/dist', 'dist'), 'glob: 前导斜杠锚定到根');
ok(!Q.giPatternHit('/dist', 'app/dist'), 'glob: 锚定模式不匹配子目录里的同名项');
ok(Q.giPatternHit('**/*.log', 'a/b/c.log'), 'glob: ** 跨多级目录');
ok(Q.giPatternHit('node_modules', 'node_modules'), 'glob: 字面量相等');
ok(!Q.giPatternHit('node_modules', 'node_modules_x'), 'glob: 不做前缀匹配');
ok(Q.giPatternHit('file?.txt', 'file1.txt'), 'glob: ? 匹配单字符');
ok(!Q.giPatternHit('file?.txt', 'file10.txt'), 'glob: ? 不匹配多字符');
ok(Q.giPatternHit('build/', 'build'), 'glob: 尾部斜杠不影响匹配');
ok(Q.giPatternHit('build/', 'pkg/build'), 'glob: 目录名同样非锚定');
ok(Q.giPatternHit('[Bb]in', 'bin'), 'glob: 字符类');
ok(Q.giPatternHit('[Bb]in', 'Bin'), 'glob: 字符类大小写变体');
ok(Q.giPatternHit('[Bb]in', 'src/Proj/bin'), 'glob: 字符类也能匹配任意层级');
ok(!Q.giPatternHit('', 'anything'), 'glob: 空模式不匹配');

// ---------------------------------------------------------------- 覆盖判定
ok(Q.giCoveredBy(['node_modules/'], 'node_modules/foo/bar.js'), 'cover: 目录规则覆盖子文件');
ok(Q.giCoveredBy(['*.log'], 'app.log'), 'cover: 通配覆盖同名文件');
ok(!Q.giCoveredBy(['*.log'], 'keep.txt'), 'cover: 不相关规则不误判');
ok(Q.giCoveredBy(['.vscode/*'], '.vscode/settings.json'), 'cover: 目录/* 覆盖直接子项');
// 孙级同样算「已被覆盖」——这不是过度判定，而是 git 的真实行为：
// .vscode/* 会把 nested/ 整个目录忽略掉，而被忽略的目录 git 不会进去读，
// 所以 !.vscode/nested/x.json 一定失效。这正是要提醒用户的那类静默失败。
ok(Q.giCoveredBy(['.vscode/*'], '.vscode/nested/x.json'), 'cover: 父目录被忽略时孙级取反必然失效');
ok(!Q.giCoveredBy(['.vscode/*.json'], '.vscode/nested/x.json'), 'cover: 模式不匹配时不算覆盖');
ok(Q.giCoveredBy(['.vscode/**'], '.vscode/nested/x.json'), 'cover: ** 覆盖孙级');

// ---------------------------------------------------------------- 取反失效检测
// 这是本站最想帮人抓的坑：!foo 写在忽略规则之前，或者根本没有对应规则
eq(Q.giDeadNegations('*.log\n!keep.log'), [], 'neg: 先忽略后取反 → 有效');
eq(Q.giDeadNegations('!keep.log'), ['!keep.log'], 'neg: 孤立的取反 → 失效');
eq(Q.giDeadNegations('!keep.log\n*.log'), ['!keep.log'], 'neg: 顺序反了 → 失效');
eq(Q.giDeadNegations('.vscode/*\n!.vscode/settings.json'), [], 'neg: 目录/* + 取反子文件 → 有效');
eq(Q.giDeadNegations('# 说明\n*.log\n\n!keep.log'), [], 'neg: 注释与空行不干扰');
eq(Q.giDeadNegations(''), [], 'neg: 空文本');
eq(Q.giDeadNegations('.env.*\n!.env.example'), [], 'neg: 组内 env 取反有效');

// ---------------------------------------------------------------- 合并
const A = { name: 'A', lines: ['a1/', 'dup/', '# 内部注释', 'a2'] };
const B = { name: 'B', lines: ['b1', 'dup/', 'b2'] };
const r1 = Q.giBuild([A, B], {});
eq(r1.rules, 5, 'build: 跨块去重后规则数');
eq(r1.groups, 2, 'build: 两组都保留');
eq(r1.text.indexOf('# A') >= 0, true, 'build: 组标题用 # 模板名');
eq(r1.text.indexOf('a1/\ndup/') >= 0, true, 'build: 组内规则保序');
ok(r1.dupes.length === 1 && r1.dupes[0].rule === 'dup/', 'build: 记录被去掉的重复规则');
eq(r1.text.split('\n\n').length, 2, 'build: 组之间恰好一个空行');

// 整块被去重干净时，不该留下一个孤立标题
const r2 = Q.giBuild([{ name: 'A', lines: ['x'] }, { name: 'B', lines: ['x'] }], {});
eq(r2.groups, 1, 'build: 全重复的块整块丢弃');
eq(r2.text, '# A\nx', 'build: 丢弃后正文干净');

// 用户自定义优先：模板里的同一条规则要被丢掉
const r3 = Q.giBuild([{ name: 'A', lines: ['dist/', 'a'] }], { custom: 'dist/' });
eq(r3.text, 'dist/\n\n# A\na', 'build: 自定义规则排在末尾且模板里的重复项被去掉');
eq(r3.rules, 2, 'build: 规则总数含自定义');
eq(r3.customRules, 1, 'build: 自定义规则单独计数');

const r4 = Q.giBuild([{ name: 'A', lines: ['a'] }], { custom: '# mine\nsecret', customPos: 'start' });
eq(r4.text, '# mine\nsecret\n\n# A\na', 'build: customPos=start 排在开头');

const r5 = Q.giBuild([], {});
eq(r5.text, '', 'build: 无输入 → 空文本');
eq(r5.groups, 0, 'build: 无输入 → 0 组');
eq(r5.rules, 0, 'build: 无输入 → 0 规则');

const r6 = Q.giBuild([{ name: 'A', lines: ['a', '', '  ', 'b'] }], {});
eq(r6.rules, 2, 'build: 空行不计入规则数');
ok(r6.text.indexOf('\n\n\n') < 0, 'build: 不产生连续空行');

// 空行/空白模板名不得产生 `# ` 这种半截标题
const r7 = Q.giBuild([{ name: '', lines: ['a'] }, null, { name: 'B', lines: [] }], {});
eq(r7.text, '', 'build: 空名或空规则的条目被跳过');

// ---------------------------------------------------------------- 模板库自检
const cat = Q.GI_CATALOG;
ok(Array.isArray(cat) && cat.length >= 5, 'lib: 至少 5 个分类（' + cat.length + '）');

const allKeys = [];
const allNames = [];
let totalRules = 0;
const seenLine = {};
let dupInLib = [];
for (const g of cat) {
    ok(!!g.key, 'lib: 分类必须有 key');
    ok(Array.isArray(g.items) && g.items.length > 0, 'lib: 分类 ' + g.key + ' 不能为空');
    for (const it of g.items) {
        allKeys.push(it.key);
        allNames.push(it.name);
        ok(Array.isArray(it.lines) && it.lines.length >= 1, 'lib: ' + it.key + ' 至少有 1 条规则');
        for (const ln of it.lines) {
            totalRules++;
            ok(ln === Q.giCleanLine(ln), 'lib: ' + it.key + ' 的规则行不带多余空白');
            ok(ln.length > 0, 'lib: ' + it.key + ' 不含空行');
            // 英文页零汉字是 check.py 的硬门禁，模板里混进中文会整站构建失败
            ok(!/[\u4e00-\u9fff]/.test(ln), 'lib: ' + it.key + ' 的规则行不得含中文（' + ln + '）');
            ok(!/[\u4e00-\u9fff]/.test(it.name), 'lib: 模板名不得含中文（' + it.name + '）');
            if (seenLine[ln]) dupInLib.push(ln + ' (' + it.key + ' ← ' + seenLine[ln] + ')');
            else seenLine[ln] = it.key;
        }
    }
}
ok(allKeys.length === new Set(allKeys).size, 'lib: 模板 key 全局唯一');
ok(allNames.length === new Set(allNames).size, 'lib: 模板名不重复');
ok(totalRules >= 150, 'lib: 规则总量足够（' + totalRules + ' 条）');

// 模板之间的重复是允许的（正是去重要解决的），但同一模板内部不该重复
for (const g of cat) {
    for (const it of g.items) {
        const set = new Set(it.lines);
        ok(set.size === it.lines.length, 'lib: ' + it.key + ' 内部无重复规则');
    }
}

// 预设引用的 key 必须真实存在，否则点了没反应且没有任何提示
for (const p of Q.GI_PRESETS) {
    ok(!!p.key, 'preset: 必须有 key');
    ok(Array.isArray(p.items) && p.items.length > 0, 'preset: ' + p.key + ' 不能为空');
    for (const k of p.items) {
        ok(allKeys.indexOf(k) >= 0, 'preset: ' + p.key + ' 引用了不存在的模板 ' + k);
    }
}

// 每个模板单独生成时都必须能产出有效结果
for (const g of cat) {
    for (const it of g.items) {
        const r = Q.giBuild([it], {});
        ok(r.rules === it.lines.length, 'lib: ' + it.key + ' 单独生成时规则数应等于模板行数');
        ok(r.text.indexOf('# ' + it.name) === 0, 'lib: ' + it.key + ' 首行是组标题');
    }
}

// 全选（含预设叠加）不得崩溃，且结果里无连续空行
const everything = [];
for (const g of cat) for (const it of g.items) everything.push(it);
const rAll = Q.giBuild(everything, { custom: '# tail\nmy.tmp' });
ok(rAll.groups > 30, 'lib: 全选时输出 30+ 组（' + rAll.groups + '）');
ok(rAll.text.indexOf('\n\n\n') < 0, 'lib: 全选也不产生连续空行');
ok(rAll.dupes.length > 0, 'lib: 全选时应能去重出跨模板重复项（' + rAll.dupes.length + '）');
eq(Q.giDeadNegations(rAll.text), [], 'lib: 全选结果里没有失效的取反规则');

// ---------------------------------------------------------------- 汇总
console.log('\n' + (fails.length ? '❌ 失败 ' + fails.length + ' 项 / 共 ' + (pass + fails.length) : '✅ 全部通过 ' + pass + ' 项'));
if (fails.length) {
    fails.forEach((f) => console.log('  - ' + f));
    process.exit(1);
}
