// string-tools.js — String case, sort, dedup, replace, split/join tools
// ============================================================
// 7. STRING TOOLS PAGE
// ============================================================
let strCurrentOp = 'case';

function initStringPage() {
  document.querySelectorAll('#strOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#strOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      strCurrentOp = btn.dataset.op;
      updateStrOptions();
    };
  });
  updateStrOptions();
}

function updateStrOptions() {
  const o = document.getElementById('strOpOptions');
  const titles = {case:'大小写转换', sort:'排序结果', dedup:'去重结果', replace:'替换结果', splitjoin:'分割/合并', liner:'行操作'};
  document.getElementById('strResultTitle').textContent = titles[strCurrentOp] || '结果';
  switch (strCurrentOp) {
    case 'case':
      o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="runStrOp(\'upper\')">大写</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'lower\')">小写</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'title\')">首字母大写</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'camel\')">驼峰命名</button>';
      break;
    case 'sort':
      o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="runStrOp(\'sort-asc\')">按行升序</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'sort-desc\')">按行降序</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'sort-len\')">按长度</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'shuffle\')">随机打乱</button>';
      break;
    case 'dedup':
      o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="runStrOp(\'dedup\')">行去重</button><label class="checkbox-label"><input type="checkbox" id="strKeepEmpty">保留空行</label>';
      break;
    case 'replace':
      o.innerHTML = '<span style="font-size:12px">查找:</span><input type="text" class="format-select" id="strFind" placeholder="文本或正则" style="width:150px"><span style="font-size:12px">替换:</span><input type="text" class="format-select" id="strReplace" placeholder="替换为" style="width:150px"><button class="btn btn-sm btn-primary" onclick="runStrOp(\'replace\')">替换</button>';
      break;
    case 'splitjoin':
      o.innerHTML = '<span style="font-size:12px">分隔符:</span><input type="text" class="format-select" id="strSep" value="," style="width:80px"><button class="btn btn-sm btn-primary" onclick="runStrOp(\'split\')">分割</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'join\')">合并</button>';
      break;
    case 'liner':
      o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="runStrOp(\'addnum\')">添加行号</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'prefix\')">添加前缀</button><span style="font-size:12px"><input type="text" class="format-select" id="strLinerVal" placeholder="前缀/起始号" style="width:80px"></span><button class="btn btn-sm btn-primary" onclick="runStrOp(\'suffix\')">添加后缀</button><button class="btn btn-sm btn-primary" onclick="runStrOp(\'trim\')">去除首尾空格</button>';
      break;
  }
}

function autoStrCount() {
  const t = document.getElementById('strInput').value;
  document.getElementById('strStats').innerHTML = '字符: ' + t.length + ' | 单词: ' + t.split(/\s+/).filter(w => w.length).length + ' | 行: ' + t.split(NL).length + ' | 字节: ' + new TextEncoder().encode(t).length;
}

function runStrOp(op) {
  const input = document.getElementById('strInput').value;
  if (!input.trim()) { toast('请先输入文本','error'); return; }
  const el = document.getElementById('strResult');
  let result = '';
  switch (op) {
    case 'upper': result = input.toUpperCase(); break;
    case 'lower': result = input.toLowerCase(); break;
    case 'title': result = input.replace(/\b\w/g, c => c.toUpperCase()); break;
    case 'camel': result = input.replace(/[-_\s]+(.)/g, (_, c) => c.toUpperCase()).replace(/^./, c => c.toLowerCase()); break;
    case 'sort-asc': result = input.split(NL).sort().join(NL); break;
    case 'sort-desc': result = input.split(NL).sort().reverse().join(NL); break;
    case 'sort-len': result = input.split(NL).sort((a, b) => a.length - b.length).join(NL); break;
    case 'shuffle':
      const arr = input.split(NL);
      for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; }
      result = arr.join(NL); break;
    case 'dedup':
      const keep = document.getElementById('strKeepEmpty')?.checked;
      const lines = input.split(NL);
      const seen = new Set();
      result = lines.filter(l => { if (!keep && !l.trim()) return true; if (seen.has(l)) return false; seen.add(l); return true; }).join(NL);
      break;
    case 'replace':
      const find = document.getElementById('strFind')?.value || '';
      if (!find) { toast('请输入查找内容','error'); return; }
      const repl = document.getElementById('strReplace')?.value || '';
      try { result = input.replace(new RegExp(find, 'g'), repl); } catch (e) { result = input.split(find).join(repl); }
      break;
    case 'split':
      const sep = document.getElementById('strSep')?.value || ',';
      result = input.split(sep).map(s => s.trim()).join(NL); break;
    case 'join':
      const sep2 = document.getElementById('strSep')?.value || ',';
      result = input.split(NL).filter(l => l.trim()).join(sep2); break;
    case 'addnum':
      const start = parseInt(document.getElementById('strLinerVal')?.value) || 1;
      result = input.split(NL).map((l, i) => (start + i) + '. ' + l).join(NL); break;
    case 'prefix':
      const p = document.getElementById('strLinerVal')?.value || '';
      result = input.split(NL).map(l => p + l).join(NL); break;
    case 'suffix':
      const s = document.getElementById('strLinerVal')?.value || '';
      result = input.split(NL).map(l => l + s).join(NL); break;
    case 'trim': result = input.split(NL).map(l => l.trim()).join(NL); break;
  }
  el.textContent = result;
  toast('操作完成');
}

