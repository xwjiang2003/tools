/* gitignore.js —— .gitignore 生成器。
 *
 * 纯前端：模板是内置静态数据，选择只在内存里合并，没有任何网络请求。
 * 面向用户的文案一律走 window.__TL__（英文页零中文由 check.py 把关）；
 * 本文件里只允许出现模板名与规则行 —— 它们是文件名/代码，不是文案。
 *
 * 与 github/gitignore 官方模板的取舍：官方单个模板动辄 100~200 行，对一个
 * 「勾几下就生成」的页面是纯噪声，而且会让人不看完就提交。这里每个模板只留
 * 日常真的会踩的规则；可提交的东西（go.sum、Cargo.lock、composer.lock、
 * gradle-wrapper.jar）一律不忽略 —— 忽略错了比少忽略更难发现。
 */
var G = (typeof window !== 'undefined') ? window : {};

// ---------------------------------------------------------------- 模板库

var GI_CATALOG = [
  {
    key: 'lang',
    items: [
      { key: 'node', name: 'Node.js', lines: [
        'node_modules/',
        '.npm/',
        '.pnpm-store/',
        '.yarn/cache',
        '.yarn/install-state.gz',
        '.eslintcache',
        '.stylelintcache',
        'npm-debug.log*',
        'yarn-debug.log*',
        'yarn-error.log*',
        'pnpm-debug.log*'
      ]},
      { key: 'python', name: 'Python', lines: [
        '__pycache__/',
        '*.py[cod]',
        '*.so',
        '.Python',
        '.venv/',
        'venv/',
        'build/',
        'dist/',
        '*.egg-info/',
        '.eggs/',
        '.pytest_cache/',
        '.mypy_cache/',
        '.ruff_cache/',
        '.coverage',
        'htmlcov/',
        '.tox/'
      ]},
      { key: 'go', name: 'Go', lines: [
        '*.exe',
        '*.exe~',
        '*.dll',
        '*.so',
        '*.dylib',
        '*.test',
        '*.out',
        '*.prof',
        'coverage.out',
        'go.work.sum'
      ]},
      { key: 'rust', name: 'Rust', lines: [
        '/target/',
        '**/*.rs.bk',
        '*.pdb'
      ]},
      { key: 'java', name: 'Java', lines: [
        '*.class',
        '*.jar',
        '*.war',
        '*.ear',
        'hs_err_pid*',
        'replay_pid*',
        'target/',
        'build/',
        'out/'
      ]},
      { key: 'kotlin', name: 'Kotlin', lines: [
        '*.class',
        '*.jar',
        '.kotlin/',
        'build/',
        'out/'
      ]},
      { key: 'swift', name: 'Swift', lines: [
        '.build/',
        '.swiftpm/',
        'DerivedData/',
        'xcuserdata/',
        '*.xcuserstate',
        '*.ipa',
        '*.dSYM.zip'
      ]},
      { key: 'dart', name: 'Dart / Flutter', lines: [
        '.dart_tool/',
        '.packages',
        '.pub-cache/',
        '.pub/',
        'build/',
        '.flutter-plugins',
        '.flutter-plugins-dependencies',
        '*.iml'
      ]},
      { key: 'cpp', name: 'C / C++', lines: [
        '*.o',
        '*.obj',
        '*.a',
        '*.lib',
        '*.so',
        '*.so.*',
        '*.dylib',
        '*.dll',
        '*.exe',
        '*.out',
        '*.app',
        'build/',
        'cmake-build-*/',
        'CMakeCache.txt',
        'CMakeFiles/'
      ]},
      { key: 'csharp', name: 'C# / .NET', lines: [
        '[Bb]in/',
        '[Oo]bj/',
        '*.user',
        '*.suo',
        '*.userprefs',
        '*.pdb',
        '*.cache',
        'packages/',
        'project.lock.json'
      ]},
      { key: 'php', name: 'PHP', lines: [
        '/vendor/',
        '.phpunit.result.cache',
        '.php-cs-fixer.cache',
        '.php-cs-fixer.php',
        '*.log'
      ]},
      { key: 'ruby', name: 'Ruby', lines: [
        '/.bundle/',
        '/vendor/bundle',
        '*.gem',
        '.rspec_status',
        'coverage/',
        'tmp/'
      ]},
      { key: 'elixir', name: 'Elixir', lines: [
        '/_build/',
        '/cover/',
        '/deps/',
        '*.ez',
        '*.beam',
        'erl_crash.dump',
        '.elixir_ls/'
      ]},
      { key: 'scala', name: 'Scala', lines: [
        'target/',
        '.bsp/',
        '.bloop/',
        '.metals/',
        '.scala-build/'
      ]},
      { key: 'lua', name: 'Lua', lines: [
        '*.o',
        '*.so',
        'luac.out'
      ]}
    ]
  },
  {
    key: 'framework',
    items: [
      { key: 'next', name: 'Next.js', lines: [
        '.next/',
        'out/',
        '.vercel/',
        '.swc/',
        'next-env.d.ts'
      ]},
      { key: 'nuxt', name: 'Nuxt', lines: [
        '.nuxt/',
        '.output/',
        'dist/',
        '.data/'
      ]},
      { key: 'angular', name: 'Angular', lines: [
        '/dist/',
        '/out-tsc/',
        '/tmp/',
        '/.angular/'
      ]},
      { key: 'sveltekit', name: 'SvelteKit', lines: [
        '.svelte-kit/',
        'build/',
        '.vercel/'
      ]},
      { key: 'django', name: 'Django', lines: [
        'db.sqlite3',
        'db.sqlite3-journal',
        '/staticfiles/',
        '/media/',
        'local_settings.py'
      ]},
      { key: 'laravel', name: 'Laravel', lines: [
        '/public/storage',
        '/storage/*.key',
        'Homestead.json',
        'Homestead.yaml'
      ]}
    ]
  },
  {
    key: 'editor',
    items: [
      { key: 'vscode', name: 'VS Code', lines: [
        '.vscode/*',
        '!.vscode/settings.json',
        '!.vscode/extensions.json',
        '!.vscode/launch.json',
        '!.vscode/tasks.json'
      ]},
      { key: 'jetbrains', name: 'JetBrains', lines: [
        '.idea/',
        '*.iml',
        '*.iws',
        '*.ipr'
      ]},
      { key: 'vim', name: 'Vim', lines: [
        '*.swp',
        '*.swo',
        '*~'
      ]},
      { key: 'emacs', name: 'Emacs', lines: [
        '*~',
        '\\#*\\#',
        '.\\#*'
      ]},
      { key: 'visualstudio', name: 'Visual Studio', lines: [
        '.vs/',
        '*.suo',
        '*.user',
        '*.sln.docstates'
      ]}
    ]
  },
  {
    key: 'os',
    items: [
      { key: 'macos', name: 'macOS', lines: [
        '.DS_Store',
        '.AppleDouble',
        '.LSOverride',
        '._*',
        '.Spotlight-V100',
        '.Trashes'
      ]},
      { key: 'windows', name: 'Windows', lines: [
        'Thumbs.db',
        'ehthumbs.db',
        'Desktop.ini',
        '$RECYCLE.BIN/',
        '*.lnk'
      ]},
      { key: 'linux', name: 'Linux', lines: [
        '*~',
        '.directory',
        '.Trash-*'
      ]}
    ]
  },
  {
    key: 'tool',
    items: [
      { key: 'maven', name: 'Maven', lines: [
        'target/',
        'pom.xml.tag',
        'pom.xml.releaseBackup',
        'release.properties',
        '.mvn/timing.properties'
      ]},
      { key: 'gradle', name: 'Gradle', lines: [
        '.gradle/',
        'build/',
        '*.jar',
        '!gradle/wrapper/gradle-wrapper.jar'
      ]},
      { key: 'terraform', name: 'Terraform', lines: [
        '.terraform/',
        '*.tfstate',
        '*.tfstate.*',
        'crash.log',
        '*.tfvars'
      ]},
      { key: 'latex', name: 'LaTeX', lines: [
        '*.aux',
        '*.log',
        '*.out',
        '*.toc',
        '*.fls',
        '*.fdb_latexmk',
        '*.synctex.gz'
      ]},
      { key: 'jupyter', name: 'Jupyter', lines: [
        '.ipynb_checkpoints/',
        '*.nbconvert.ipynb'
      ]},
      { key: 'unity', name: 'Unity', lines: [
        '[Ll]ibrary/',
        '[Tt]emp/',
        '[Oo]bj/',
        '[Bb]uild/',
        '[Ll]ogs/',
        '[Uu]ser[Ss]ettings/',
        '*.csproj',
        '*.sln'
      ]},
      { key: 'godot', name: 'Godot', lines: [
        '.godot/',
        '*.translation',
        'export_presets.cfg'
      ]}
    ]
  },
  {
    key: 'common',
    items: [
      { key: 'env', name: 'Env & secrets', lines: [
        '.env',
        '.env.*',
        '!.env.example',
        '*.pem',
        '*.key',
        '*.p12',
        'secrets.json'
      ]},
      { key: 'logs', name: 'Logs', lines: [
        '*.log',
        'logs/'
      ]},
      { key: 'coverage', name: 'Coverage', lines: [
        'coverage/',
        'lcov.info',
        '.nyc_output/'
      ]},
      { key: 'cache', name: 'Cache & temp', lines: [
        '.cache/',
        '.tmp/',
        'tmp/',
        '*.bak',
        '*.orig'
      ]}
    ]
  }
];

// 预设组合：按 key 顺序覆盖「选中的这一套」，不是追加 —— 点第二次不会再叠一层。
var GI_PRESETS = [
  { key: 'node', items: ['node', 'next', 'vscode', 'macos', 'env', 'logs'] },
  { key: 'python', items: ['python', 'django', 'vscode', 'macos', 'env', 'logs', 'coverage'] },
  { key: 'go', items: ['go', 'vscode', 'macos', 'env', 'logs'] },
  { key: 'java', items: ['java', 'maven', 'jetbrains', 'macos', 'env', 'logs', 'coverage'] },
  { key: 'mixed', items: ['node', 'python', 'vscode', 'macos', 'env', 'logs', 'cache'] }
];

// ---------------------------------------------------------------- 纯函数

/** 单行规范化：两端空白一律去掉。
 *  git 里「前导空格」是用来转义真空格文件名的手段，但那属于极少数场景，
 *  而用户从聊天窗口/文档里复制过来的规则十有八九带着缩进 —— 保留缩进只会
 *  生成一条永远匹配不上的规则，且完全静默。所以这里选择 trim。
 */
function giCleanLine(s) {
  return String(s == null ? '' : s).replace(/\r/g, '').replace(/^\s+/, '').replace(/\s+$/, '');
}

/** 取一段文本里的有效规则（去掉注释与空行），保持原顺序。 */
function giRulesOf(text) {
  var lines = String(text == null ? '' : text).replace(/\r\n?/g, '\n').split('\n');
  var out = [];
  for (var i = 0; i < lines.length; i++) {
    var ln = giCleanLine(lines[i]);
    if (!ln || ln.charAt(0) === '#') continue;
    out.push(ln);
  }
  return out;
}

/** 用户自定义块：去空行、块内精确去重，注释原样保留（那是人写的说明）。 */
function giCustomLines(text) {
  var lines = String(text == null ? '' : text).replace(/\r\n?/g, '\n').split('\n');
  var out = [];
  var seen = {};
  for (var i = 0; i < lines.length; i++) {
    var ln = giCleanLine(lines[i]);
    if (!ln) continue;
    if (ln.charAt(0) !== '#') {
      if (seen[ln]) continue;
      seen[ln] = 1;
    }
    out.push(ln);
  }
  return out;
}

/** gitignore 的简易通配匹配：实现 * / ** / ? / 字符类，以及「非锚定模式」语义。
 *
 *  最容易写错的是锚定规则（git 文档原话）：模式里只要开头或中间出现 `/`，
 *  就被锚定到 .gitignore 所在目录；否则它可以匹配**任意深度**的同名项。
 *  所以 `*.jar` 能命中 gradle/wrapper/gradle-wrapper.jar，而 `/dist` 只命中根下的 dist。
 *  漏掉这一条，判断「取反规则是否生效」时会把大量有效规则误判成失效。
 */
function giPatternHit(pattern, path) {
  var p = String(pattern == null ? '' : pattern).replace(/\/+$/, '');
  if (!p) return false;

  var pathStr = String(path == null ? '' : path).replace(/^\/+/, '');
  if (!pathStr) return false;

  var anchored = p.indexOf('/') >= 0;
  if (p.charAt(0) === '/') {
    p = p.slice(1);
    anchored = true;
  }
  if (!p) return false;

  var re;
  try { re = new RegExp('^' + giGlobBody(p) + '$'); } catch (e) { return false; }

  if (re.test(pathStr)) return true;
  if (anchored) return false;
  var base = pathStr.slice(pathStr.lastIndexOf('/') + 1);
  return base !== pathStr && re.test(base);
}

/** 把 glob 主体翻成正则源码（不含首尾锚点）。 */
function giGlobBody(p) {
  var re = '';
  for (var i = 0; i < p.length; i++) {
    var ch = p.charAt(i);
    if (ch === '*') {
      if (p.charAt(i + 1) === '*') {
        i++;
        if (p.charAt(i + 1) === '/') i++;
        re += '.*';
      } else {
        re += '[^/]*';
      }
    } else if (ch === '?') {
      re += '[^/]';
    } else if (ch === '[') {
      var end = p.indexOf(']', i + 1);
      if (end > i) { re += p.slice(i, end + 1); i = end; }
      else { re += '\\['; }
    } else {
      re += ch.replace(/[.+^${}()|\\]/g, '\\$&');
    }
  }
  return re;
}

/** target 是否被 rules 里某条规则覆盖到（含祖先目录）。 */
function giCoveredBy(rules, target) {
  var t = String(target == null ? '' : target).replace(/^\/+/, '');
  if (!t) return false;
  var segs = t.split('/');
  var cands = [];
  var acc = '';
  for (var i = 0; i < segs.length; i++) {
    acc += (i ? '/' : '') + segs[i];
    cands.push(acc);
  }
  for (var r = 0; r < rules.length; r++) {
    for (var c = 0; c < cands.length; c++) {
      if (giPatternHit(rules[r], cands[c])) return true;
    }
  }
  return false;
}

/** 找出「写了却没生效」的取反规则。
 *  这是 .gitignore 最经典的坑：!foo 只有在它前面已经有一条忽略 foo 的规则时才有意义，
 *  顺序反了或被祖先目录挡住（父目录整体被忽略时，git 不会去读子目录里的内容）就完全不生效。
 */
function giDeadNegations(text) {
  var lines = String(text == null ? '' : text).replace(/\r\n?/g, '\n').split('\n');
  var ignored = [];
  var dead = [];
  for (var i = 0; i < lines.length; i++) {
    var ln = giCleanLine(lines[i]);
    if (!ln || ln.charAt(0) === '#') continue;
    if (ln.charAt(0) === '!') {
      if (!giCoveredBy(ignored, ln.slice(1))) dead.push(ln);
    } else {
      ignored.push(ln);
    }
  }
  return dead;
}

/**
 * 合并生成 .gitignore 正文。
 * entries: [{name, lines}] —— 调用方已按期望顺序排好
 * opts: {custom, customPos:'start'|'end'}
 *
 * 两条刻意的规则：
 *  1. 规则行跨模板精确去重，注释不参与去重（组标题必须保留，否则输出没有章法）。
 *  2. 用户自定义的规则优先级最高：生成块里与它重复的行会被丢掉，
 *     这样「我自己写的写法」永远不会被模板的写法顶掉。
 */
function giBuild(entries, opts) {
  opts = opts || {};
  var custom = giCustomLines(opts.custom);
  var customSet = {};
  var customRules = 0;
  for (var c = 0; c < custom.length; c++) {
    if (custom[c].charAt(0) === '#') continue;
    customSet[custom[c]] = 1;
    customRules++;
  }

  var seen = {};
  var dupes = [];
  var blocks = [];
  var rules = 0;
  var list = entries || [];

  for (var i = 0; i < list.length; i++) {
    var e = list[i];
    if (!e || !e.name) continue;
    var src = e.lines || [];
    var out = [];
    for (var j = 0; j < src.length; j++) {
      var ln = giCleanLine(src[j]);
      if (!ln) continue;
      if (ln.charAt(0) === '#') { out.push(ln); continue; }
      if (customSet[ln] || seen[ln]) {
        dupes.push({ rule: ln, at: e.name });
        continue;
      }
      seen[ln] = 1;
      out.push(ln);
      rules++;
    }
    // 只由注释构成的块（规则全被去重掉）不该留下一个空标题
    while (out.length && out[out.length - 1].charAt(0) === '#') out.pop();
    if (!out.length) continue;
    blocks.push('# ' + e.name + '\n' + out.join('\n'));
  }

  var parts = [];
  var customBlock = custom.join('\n');
  if (custom.length && opts.customPos !== 'end') parts.push(customBlock);
  for (var k = 0; k < blocks.length; k++) parts.push(blocks[k]);
  if (custom.length && opts.customPos === 'end') parts.push(customBlock);

  return {
    text: parts.join('\n\n'),
    groups: blocks.length,
    // rules 是用户看到的总条数（模板贡献 + 自定义），templateRules 只数模板那部分。
    // 分开给是因为界面要显示总数，而单测需要区分「模板真的产出了多少」。
    rules: rules + customRules,
    templateRules: rules,
    customRules: customRules,
    dupes: dupes
  };
}

// ---------------------------------------------------------------- 页面

function initGitignore() {
  var host = document.getElementById('giGroups');
  if (!host) return;
  var L = G.__TL__ || {};
  var pre = document.getElementById('giPre');
  var meta = document.getElementById('giMeta');
  var warnEl = document.getElementById('giWarn');
  var search = document.getElementById('giSearch');
  var custom = document.getElementById('giCustom');
  var presetHost = document.getElementById('giPresets');
  var toast = document.getElementById('giToast');

  var state = { sel: {}, q: '', custom: '', pos: 'end' };
  var idx = {};

  function t(key, fallback) {
    var v = L[key];
    return (v == null || v === '') ? (fallback == null ? '' : fallback) : v;
  }

  // ---- 分类与 chip
  for (var gi = 0; gi < GI_CATALOG.length; gi++) {
    (function (group) {
      var sec = document.createElement('section');
      sec.className = 'gi-group';

      var head = document.createElement('div');
      head.className = 'gi-group-head';
      var nameEl = document.createElement('span');
      nameEl.className = 'gi-group-name';
      nameEl.textContent = t('cat_' + group.key, group.key);
      var countEl = document.createElement('span');
      countEl.className = 'gi-group-n';
      head.appendChild(nameEl);
      head.appendChild(countEl);

      var box = document.createElement('div');
      box.className = 'gi-chips';

      for (var ii = 0; ii < group.items.length; ii++) {
        (function (item) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'tl-chip gi-chip';
          b.textContent = item.name;
          b.setAttribute('aria-pressed', 'false');
          b.addEventListener('click', function () { toggle(item.key); });
          box.appendChild(b);
          idx[item.key] = { btn: b, item: item, group: group, count: countEl, sec: sec };
        })(group.items[ii]);
      }

      sec.appendChild(head);
      sec.appendChild(box);
      host.appendChild(sec);
    })(GI_CATALOG[gi]);
  }

  // ---- 预设
  if (presetHost) {
    for (var pi = 0; pi < GI_PRESETS.length; pi++) {
      (function (p) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'btn btn-sm gi-preset';
        b.textContent = t('preset_' + p.key, p.key);
        b.addEventListener('click', function () {
          state.sel = {};
          for (var i = 0; i < p.items.length; i++) state.sel[p.items[i]] = 1;
          paint();
        });
        presetHost.appendChild(b);
      })(GI_PRESETS[pi]);
    }
  }

  function toggle(key) {
    if (state.sel[key]) delete state.sel[key];
    else state.sel[key] = 1;
    paint();
  }

  function selectedEntries() {
    var out = [];
    for (var g = 0; g < GI_CATALOG.length; g++) {
      var items = GI_CATALOG[g].items;
      for (var i = 0; i < items.length; i++) {
        if (state.sel[items[i].key]) out.push(items[i]);
      }
    }
    return out;
  }

  function paintChips() {
    var q = state.q.replace(/^\s+|\s+$/g, '').toLowerCase();
    for (var g = 0; g < GI_CATALOG.length; g++) {
      var group = GI_CATALOG[g];
      var shown = 0;
      var on = 0;
      var countEl = null;
      for (var i = 0; i < group.items.length; i++) {
        var it = group.items[i];
        var rec = idx[it.key];
        if (!rec) continue;
        countEl = rec.count;
        var hit = !q || it.name.toLowerCase().indexOf(q) >= 0;
        rec.btn.hidden = !hit;
        var active = !!state.sel[it.key];
        rec.btn.className = 'tl-chip gi-chip' + (active ? ' active' : '');
        rec.btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        if (hit) shown++;
        if (active) on++;
      }
      if (countEl) countEl.textContent = on + '/' + shown;
      var sec = idx[group.items[0].key] && idx[group.items[0].key].sec;
      if (sec) sec.hidden = shown === 0;
    }
    var total = 0;
    for (var k in state.sel) if (state.sel.hasOwnProperty(k)) total++;
    var setCount = document.getElementById('giSetCount');
    if (setCount) setCount.textContent = t('set_count').replace('{n}', total);
  }

  function paintOut() {
    var r = giBuild(selectedEntries(), { custom: state.custom, customPos: state.pos });
    if (pre) pre.textContent = r.text || t('out_empty');
    if (meta) {
      var bits = [];
      bits.push(t('n_groups').replace('{n}', r.groups));
      bits.push(t('n_rules').replace('{n}', r.rules));
      if (r.dupes.length) bits.push(t('n_dupes').replace('{n}', r.dupes.length));
      meta.textContent = bits.join(' · ');
    }
    if (warnEl) {
      var dead = giDeadNegations(r.text);
      if (dead.length) {
        warnEl.hidden = false;
        // 规则另起一行（CSS 用 pre-line），否则一长串挤在冒号后面看不清
        warnEl.textContent = t('warn_dead') + '\n' + dead.join('\n');
      } else {
        warnEl.hidden = true;
        warnEl.textContent = '';
      }
    }
    return r;
  }

  function paint() {
    paintChips();
    paintOut();
  }

  // ---- 事件
  if (search) {
    search.addEventListener('input', function () {
      state.q = search.value || '';
      paintChips();
    });
  }
  if (custom) {
    custom.addEventListener('input', function () {
      state.custom = custom.value || '';
      paintOut();
    });
  }
  var posEls = document.querySelectorAll('input[name="giPos"]');
  for (var pe = 0; pe < posEls.length; pe++) {
    posEls[pe].addEventListener('change', function (e) {
      state.pos = e.target.value === 'start' ? 'start' : 'end';
      paintOut();
    });
  }

  function flash(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.hidden = false;
    clearTimeout(flash._t);
    flash._t = setTimeout(function () { toast.hidden = true; }, 1800);
  }

  var copyBtn = document.getElementById('giCopy');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var r = giBuild(selectedEntries(), { custom: state.custom, customPos: state.pos });
      if (!r.text) { flash(t('copy_empty')); return; }
      var done = function () { flash(t('copied')); };
      var fail = function () { flash(t('copy_fail')); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(r.text).then(done, fail);
      } else {
        try {
          var ta = document.createElement('textarea');
          ta.value = r.text;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          done();
        } catch (e) { fail(); }
      }
    });
  }

  var dlBtn = document.getElementById('giDownload');
  if (dlBtn) {
    dlBtn.addEventListener('click', function () {
      var r = giBuild(selectedEntries(), { custom: state.custom, customPos: state.pos });
      if (!r.text) { flash(t('copy_empty')); return; }
      var blob = new Blob([r.text + '\n'], { type: 'text/plain;charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'gitignore.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      flash(t('downloaded'));
    });
  }

  var clearBtn = document.getElementById('giClear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      state.sel = {};
      state.custom = '';
      if (custom) custom.value = '';
      paint();
    });
  }

  paint();
}

// ---------------------------------------------------------------- 导出

G.giCleanLine = giCleanLine;
G.giRulesOf = giRulesOf;
G.giCustomLines = giCustomLines;
G.giPatternHit = giPatternHit;
G.giCoveredBy = giCoveredBy;
G.giDeadNegations = giDeadNegations;
G.giBuild = giBuild;
G.GI_CATALOG = GI_CATALOG;
G.GI_PRESETS = GI_PRESETS;
G.initGitignore = initGitignore;

if (typeof G.addEventListener === 'function' && typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    G.addEventListener('DOMContentLoaded', initGitignore);
  } else {
    initGitignore();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    giCleanLine: giCleanLine,
    giRulesOf: giRulesOf,
    giCustomLines: giCustomLines,
    giPatternHit: giPatternHit,
    giCoveredBy: giCoveredBy,
    giDeadNegations: giDeadNegations,
    giBuild: giBuild,
    GI_CATALOG: GI_CATALOG,
    GI_PRESETS: GI_PRESETS
  };
}
