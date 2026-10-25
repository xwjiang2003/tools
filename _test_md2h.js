// Node smoke test for src/tools/markdown-to-html.html renderer.
'use strict';
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('D:/workspace/dev-tools/src/tools/markdown-to-html.html', 'utf8');
let code = html.match(/<script>([\s\S]*)<\/script>/)[1];
code = code.replace(/\}\)\(\);\s*$/, 'globalThis.__t = { renderBlocks: renderBlocks, inline: inline }; })();');
if (code === html.match(/<script>([\s\S]*)<\/script>/)[1]) { console.error('FAIL: IIFE tail not found'); process.exit(1); }

const sandbox = {
  globalThis: {},
  document: { getElementById: function(){ return null; }, readyState: 'complete', addEventListener: function(){}, createElement: function(){ return {}; } },
  console: console,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const T = sandbox.globalThis.__t;
if (!T || typeof T.renderBlocks !== 'function') { console.error('FAIL: internals not exported'); process.exit(1); }

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log('  ok - ' + name); }
  else { fail++; console.log('  FAIL - ' + name + (extra ? '\n' + extra : '')); }
}

// headings
check('h1', T.renderBlocks('# Hello') === '<h1>Hello</h1>');
check('h3', T.renderBlocks('### Deep') === '<h3>Deep</h3>');
check('h6 closing tags', T.renderBlocks('###### x').indexOf('</h6>') >= 0);

// paragraph
check('paragraph', T.renderBlocks('one two\nthree') === '<p>one two three</p>');

// inline
check('bold **', T.inline('a **b** c').indexOf('<strong>b</strong>') >= 0);
check('bold __', T.inline('a __b__ c').indexOf('<strong>b</strong>') >= 0);
check('italic *', T.inline('a *b* c').indexOf('<em>b</em>') >= 0);
check('italic _', T.inline('a _b_ c').indexOf('<em>b</em>') >= 0);
check('snake_case untouched', T.inline('foo_bar_baz').indexOf('<em>') < 0);
check('inline code', T.inline('run `ls -la` now').indexOf('<code>ls -la</code>') >= 0);
check('del', T.inline('a ~~b~~ c').indexOf('<del>b</del>') >= 0);
check('link', T.inline('[t](https://x.com)').indexOf('<a href="https://x.com"') >= 0);
check('image', T.inline('![alt](https://x.com/a.png)').indexOf('<img src="https://x.com/a.png" alt="alt"') >= 0);
check('link title', T.inline('[t](https://x.com "T")').indexOf('title="T"') >= 0);
check('code not styled inside', T.inline('`**not bold**`').indexOf('<strong>') < 0);
check('link not nested in code', T.inline('`[a](b)`').indexOf('<a href') < 0);

// escaping / XSS
check('raw html escaped', T.renderBlocks('<script>alert(1)</script>').indexOf('<script>') < 0);
check('javascript url blocked', T.inline('[x](javascript:alert(1))').indexOf('javascript:') < 0);
check('data url blocked', T.inline('![x](data:text/html,<b>)').indexOf('data:') < 0);
check('escape amp', T.inline('a & b').indexOf('&amp;') >= 0);

// hr
check('hr ---', T.renderBlocks('---') === '<hr>');
check('hr ***', T.renderBlocks('***') === '<hr>');
check('hr ___', T.renderBlocks('___') === '<hr>');
check('not hr (2 chars)', T.renderBlocks('--') !== '<hr>');

// blockquote
check('blockquote', T.renderBlocks('> quoted').indexOf('<blockquote>') >= 0 && T.renderBlocks('> quoted').indexOf('quoted') >= 0);
check('blockquote multi', T.renderBlocks('> a\n> b').indexOf('a b') >= 0);

// lists
check('ul', T.renderBlocks('- a\n- b').indexOf('<ul>\n<li>a</li>\n<li>b</li>\n</ul>') >= 0, T.renderBlocks('- a\n- b'));
check('ol', T.renderBlocks('1. a\n2. b').indexOf('<ol>') >= 0);
check('nested ul', T.renderBlocks('- a\n  - a1\n- b').indexOf('<ul>\n<li>a1</li>\n</ul>') >= 0, T.renderBlocks('- a\n  - a1\n- b'));
check('star bullets', T.renderBlocks('* a').indexOf('<ul>') >= 0);

// code fence
const fenced = T.renderBlocks('```js\nvar x = 1 < 2;\n```');
check('fence pre/code', fenced.indexOf('<pre><code class="lang-js">') >= 0 && fenced.indexOf('</code></pre>') >= 0, fenced);
check('fence escapes', fenced.indexOf('&lt;') >= 0);
check('fence no inline', fenced.indexOf('<strong>') < 0);

// table
const tbl = T.renderBlocks('| a | b |\n| --- | ---: |\n| 1 | 2 |');
check('table head', tbl.indexOf('<th>a</th><th style="text-align:right">b</th>') >= 0, tbl);
check('table body', tbl.indexOf('<td>1</td><td style="text-align:right">2</td>') >= 0, tbl);
check('table center align', T.renderBlocks('| a |\n| :-: |\n| 1 |').indexOf('text-align:center') >= 0);

// full document
const doc = [
  '# Title', '', 'Para with **bold**.', '', '- item 1', '- item 2', '',
  '## Table', '', '| x | y |', '| --- | --- |', '| 1 | 2 |', '',
  '```', 'plain code', '```', '', '> quote', '', '---', '',
].join('\n');
const out = T.renderBlocks(doc);
console.log('--- full doc ---');
console.log(out);
check('full doc structure', out.indexOf('<h1>Title</h1>') >= 0 && out.indexOf('<h2>Table</h2>') >= 0 &&
  out.indexOf('<ul>') >= 0 && out.indexOf('<table>') >= 0 && out.indexOf('<pre><code>') >= 0 &&
  out.indexOf('<blockquote>') >= 0 && out.indexOf('<hr>') >= 0 && out.indexOf('<p>Para with <strong>bold</strong>.</p>') >= 0, out);
check('no unescaped angle from input', out.indexOf('<script') < 0);

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
