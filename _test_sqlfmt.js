// Node smoke test for src/tools/sql-formatter.html core logic.
// Extracts the inline script, stubs the DOM, exports internals, runs asserts.
'use strict';
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('D:/workspace/dev-tools/src/tools/sql-formatter.html', 'utf8');
const m = html.match(/<script>([\s\S]*)<\/script>/);
if (!m) { console.error('FAIL: no script block'); process.exit(1); }
let code = m[1];
// expose internals for testing
code = code.replace(/\}\)\(\);\s*$/, 'globalThis.__t = { format: format, tokenize: tokenize, mergeMulti: mergeMulti }; })();');
if (code === m[1]) { console.error('FAIL: IIFE tail not found'); process.exit(1); }

const sandbox = {
  globalThis: {},
  document: { getElementById: function(){ return null; }, readyState: 'complete', addEventListener: function(){} },
  console: console,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const T = sandbox.globalThis.__t;
if (!T || typeof T.format !== 'function') { console.error('FAIL: internals not exported'); process.exit(1); }

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log('  ok - ' + name); }
  else { fail++; console.log('  FAIL - ' + name + (extra ? '\n' + extra : '')); }
}

const sample = "select u.id, u.name, count(o.id) as order_count from users u left join orders o on o.user_id=u.id where u.status='active' and o.created_at>'2024-01-01' group by u.id,u.name having count(o.id)>1 order by order_count desc limit 10;";

const out2 = T.format(sample, true, '  ');
console.log('--- sample (indent 2) ---');
console.log(out2);
check('SELECT leads first column', /^SELECT u\.id,\n/.test(out2));
check('select list indented', out2.indexOf('\n  u.name,') >= 0);
check('FROM top level', out2.indexOf('\nFROM users u\n') >= 0);
check('LEFT JOIN top level', out2.indexOf('\nLEFT JOIN orders o\n') >= 0);
check('ON indented', out2.indexOf('\n  ON o.user_id = u.id') >= 0);
check('WHERE top level', out2.indexOf("\nWHERE u.status = 'active'\n") >= 0);
check('AND indented once', out2.indexOf('\n  AND o.created_at') >= 0);
check('GROUP BY merged', out2.indexOf('\nGROUP BY u.id,\n') >= 0);
check('HAVING top level', out2.indexOf('\nHAVING count(o.id) > 1\n') >= 0);
check('ORDER BY merged', out2.indexOf('\nORDER BY order_count DESC\n') >= 0);
check('LIMIT top level', out2.indexOf('\nLIMIT 10;') >= 0);
check('keywords uppercased', out2.indexOf('select ') < 0 && out2.indexOf('from ') < 0);
check('count() call kept tight', out2.indexOf('count(o.id) AS order_count') >= 0, out2);
check('qualified name kept', out2.indexOf('u.id') >= 0);
check('idempotent', T.format(out2, true, '  ') === out2, 'second pass differs');

const out4 = T.format(sample, true, '    ');
check('indent unit 4', out4.indexOf('\n    u.name,') >= 0);

const lower = T.format(sample, false, '  ');
check('lowercase kept', /^select u\.id,\n/.test(lower) && lower.indexOf('left join orders o') >= 0);

const ins = T.format("insert into users (id,name) values (1,'a'),(2,'b');", true, '  ');
console.log('--- insert ---');
console.log(ins);
check('INSERT INTO line', /^INSERT INTO users \(/.test(ins));
check('VALUES inline in parens', ins.indexOf("VALUES (1, 'a'), (2, 'b');") >= 0, ins);

const ddl = T.format("create table t (id int primary key, name text not null);", true, '  ');
console.log('--- ddl ---');
console.log(ddl);
check('CREATE TABLE', /^CREATE TABLE t \(\n/.test(ddl));
check('ddl column breaks', ddl.indexOf('CREATE TABLE t (\n  id int PRIMARY KEY,\n  name text NOT NULL\n);') >= 0, ddl);

const nested = T.format("select * from (select id from t where x=1) sub where id in (1,2,3);", true, '  ');
console.log('--- nested ---');
console.log(nested);
check('subquery indented', nested.indexOf('FROM (\n  SELECT id\n  FROM t\n  WHERE x = 1\n) sub') >= 0, nested);
check('IN takes space', nested.indexOf('WHERE id IN (1, 2, 3);') >= 0, nested);

const cmt = T.format("select 1 -- trailing comment\nfrom t;", true, '  ');
console.log('--- comment ---');
console.log(cmt);
check('line comment kept', cmt.indexOf('-- trailing comment') >= 0);

const semi = T.format("select 1; select 2;", true, '  ');
check('multi statement reset', semi.indexOf('\nSELECT 2;') >= 0, semi);

const empty = T.format('   ', true, '  ');
check('empty input -> empty output', empty === '');

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
