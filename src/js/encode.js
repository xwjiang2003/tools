// encode.js — Base64, URL, Unicode, HTML entity, Hex encode/decode
// ============================================================
// 2. ENCODE/DECODE PAGE
// ============================================================
let encodeCurrentOp = 'base64', encodeMode = 'encode';

function initEncodePage() {
  document.querySelectorAll('#encodeOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#encodeOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      encodeCurrentOp = btn.dataset.op;
      updateEncodeTitle();
      runEncodeOp(encodeMode);
    };
  });
  updateEncodeTitle();
}

function updateEncodeTitle() {
  const names = {base64:'Base64', url:'URL', unicode:'Unicode', htmlentity:'HTML实体', hex:'Hex'};
  document.getElementById('encodeResultTitle').textContent = names[encodeCurrentOp] + (encodeMode === 'encode' ? ' 编码' : ' 解码') + ' 结果';
}

function runEncodeOp(mode) {
  encodeMode = mode;
  updateEncodeTitle();
  const input = document.getElementById('encodeInput').value;
  if (!input.trim()) { toast('请先输入文本','error'); return; }
  let result = '';
  try {
    switch (encodeCurrentOp) {
      case 'base64':
        if (mode === 'encode') result = btoa(String.fromCharCode(...new TextEncoder().encode(input)));
        else result = new TextDecoder().decode(Uint8Array.from(atob(input), c => c.charCodeAt(0)));
        break;
      case 'url':
        result = mode === 'encode' ? encodeURIComponent(input) : decodeURIComponent(input);
        break;
      case 'unicode':
        if (mode === 'encode') { for (let i = 0; i < input.length; i++) { const c = input.charCodeAt(i); result += c > 127 ? '\\u' + c.toString(16).padStart(4, '0') : input[i]; } }
        else result = input.replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
        break;
      case 'htmlentity':
        if (mode === 'encode') result = input.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
        else { const ta = document.createElement('textarea'); ta.innerHTML = input; result = ta.value; }
        break;
      case 'hex':
        // 必须按 UTF-8 字节走：原实现用 charCodeAt 输出 UTF-16 码元，
        // 「中」会编成 4e2d（4 个十六进制位），而解码端每次只读 2 位，
        // 于是解出 'N-' 这种乱码——编码与解码不对称，中文无法往返。
        if (mode === 'encode') {
          result = Array.from(new TextEncoder().encode(input))
            .map(b => b.toString(16).padStart(2, '0')).join(' ');
        } else {
          const pairs = input.replace(/[^0-9a-fA-F]/g, '').match(/[0-9a-fA-F]{1,2}/g) || [];
          result = new TextDecoder().decode(Uint8Array.from(pairs.map(h => parseInt(h, 16))));
        }
        break;
    }
    document.getElementById('encodeResult').textContent = result;
    toast(mode === 'encode' ? '编码完成' : '解码完成');
  } catch (e) {
    document.getElementById('encodeResult').textContent = '❌ 错误: ' + e.message;
    toast('操作失败，请检查输入','error');
  }
}

