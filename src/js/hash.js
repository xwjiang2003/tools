// hash.js — MD5, SHA, HMAC, AES encryption/hashing
// ============================================================
// 5. HASH/CRYPTO PAGE
// ============================================================
let hashCurrentOp = 'md5';

function initHashPage() {
  document.querySelectorAll('#hashOpBtns .op-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#hashOpBtns .op-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      hashCurrentOp = btn.dataset.op;
      updateHashOptions();
      doHash();
    };
  });
  updateHashOptions();
}

function updateHashOptions() {
  const o = document.getElementById('hashOpOptions');
  const titles = {md5:'MD5 哈希', sha1:'SHA-1 哈希', sha256:'SHA-256 哈希', sha512:'SHA-512 哈希', hmac:'HMAC 哈希', aes:'AES 加解密'};
  document.getElementById('hashResultTitle').textContent = titles[hashCurrentOp] || '哈希结果';
  if (hashCurrentOp === 'hmac') {
    o.innerHTML = '<span style="font-size:12px">密钥:</span><input type="text" class="format-select" id="hmacKey" placeholder="输入HMAC密钥" style="width:180px" onchange="doHash()"><select class="format-select" id="hmacAlgo" onchange="doHash()"><option value="SHA-256">HMAC-SHA256</option><option value="SHA-1">HMAC-SHA1</option><option value="SHA-512">HMAC-SHA512</option></select>';
  } else if (hashCurrentOp === 'aes') {
    o.innerHTML = '<span style="font-size:12px">密钥:</span><input type="text" class="format-select" id="aesKey" placeholder="AES密钥" style="width:180px"><select class="format-select" id="aesMode"><option value="encrypt">加密</option><option value="decrypt">解密</option></select><button class="btn btn-sm btn-primary" onclick="doHash()">执行</button>';
  } else {
    o.innerHTML = '<button class="btn btn-sm btn-primary" onclick="doHash()">计算哈希</button>';
  }
}

async function doHash() {
  const input = document.getElementById('hashInput').value;
  const resEl = document.getElementById('hashResult');
  if (!input.trim() && hashCurrentOp !== 'aes') { resEl.textContent = '请输入文本'; return; }
  try {
    let result;
    switch (hashCurrentOp) {
      case 'md5': result = md5(input); break;
      case 'sha1': result = await shaHash('SHA-1', input); break;
      case 'sha256': result = await shaHash('SHA-256', input); break;
      case 'sha512': result = await shaHash('SHA-512', input); break;
      case 'hmac':
        const key = document.getElementById('hmacKey').value;
        const algo = document.getElementById('hmacAlgo').value;
        if (!key) { resEl.textContent = '请输入 HMAC 密钥'; return; }
        result = await hmacHash(algo, key, input);
        break;
      case 'aes':
        const aesKey = document.getElementById('aesKey').value;
        const mode = document.getElementById('aesMode').value;
        if (!aesKey) { resEl.textContent = '请输入 AES 密钥'; return; }
        result = await aesCrypt(aesKey, input, mode);
        break;
    }
    resEl.textContent = result;
    toast('计算完成');
  } catch (e) {
    resEl.textContent = '错误: ' + e.message;
    toast('计算失败','error');
  }
}

// MD5（RFC 1321）。
//
// 这里原本是一段被压缩坏掉的实现，有三处缺陷，导致「无论输入什么都返回同一个值」：
//   1. 块数算成 `s.length+8>>6`，少了 +1 —— 56 字符以下的输入一次主循环都不跑，
//      直接返回初始状态，输出恒为 0123456789abcdeffedcba9876543210；
//   2. 循环左移写成 `<<(h=void 0)`，位移量恒为 0，轮函数完全失效；
//   3. 长度字段写在 `p[a<<4]`（越过最后一个块），而不是末块的第 14 个字。
// 另外它用 charCodeAt 取 UTF-16 码元，中文会算出与标准 MD5 不一致的结果。
// 现改为干净可读、按 UTF-8 字节运算的标准实现。
const MD5_S = [
  7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
];
const MD5_K = [
  0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
  0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
  0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
  0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
  0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
  0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
  0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
  0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
];

function md5(input) {
  const bytes = new TextEncoder().encode(input);
  const bitLen = bytes.length * 8;
  // 补齐到 64 字节整数倍；末 8 字节存比特长度（小端）
  const buf = new Uint8Array((((bytes.length + 8) >> 6) + 1) << 6);
  buf.set(bytes);
  buf[bytes.length] = 0x80;
  const dv = new DataView(buf.buffer);
  dv.setUint32(buf.length - 8, bitLen >>> 0, true);
  dv.setUint32(buf.length - 4, Math.floor(bitLen / 4294967296), true);

  let h0 = 0x67452301, h1 = 0xefcdab89, h2 = 0x98badcfe, h3 = 0x10325476;
  const rotl = (x, c) => ((x << c) | (x >>> (32 - c))) >>> 0;
  const w = new Uint32Array(16);

  for (let off = 0; off < buf.length; off += 64) {
    for (let i = 0; i < 16; i++) w[i] = dv.getUint32(off + i * 4, true);
    let a = h0, b = h1, c = h2, d = h3;
    for (let i = 0; i < 64; i++) {
      let f, g;
      if (i < 16) { f = (b & c) | (~b & d); g = i; }
      else if (i < 32) { f = (d & b) | (~d & c); g = (5 * i + 1) & 15; }
      else if (i < 48) { f = b ^ c ^ d; g = (3 * i + 5) & 15; }
      else { f = c ^ (b | ~d); g = (7 * i) & 15; }
      const tmp = d;
      d = c; c = b;
      b = (b + rotl((a + f + MD5_K[i] + w[g]) >>> 0, MD5_S[i])) >>> 0;
      a = tmp;
    }
    h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0;
    h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0;
  }
  // MD5 输出按小端序拼接四个状态字
  const word = n => {
    let s = '';
    for (let i = 0; i < 4; i++) s += ((n >>> (i * 8)) & 0xff).toString(16).padStart(2, '0');
    return s;
  };
  return word(h0) + word(h1) + word(h2) + word(h3);
}

async function shaHash(algo, input) {
  const enc = new TextEncoder().encode(input);
  const buf = await crypto.subtle.digest(algo, enc);
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function hmacHash(algo, key, input) {
  const enc = new TextEncoder();
  const k = await crypto.subtle.importKey('raw', enc.encode(key), { name: 'HMAC', hash: algo }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', k, enc.encode(input));
  return Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function aesCrypt(keyStr, input, mode) {
  const enc = new TextEncoder();
  const keyBytes = enc.encode(keyStr.padEnd(16).slice(0, 16));
  const key = await crypto.subtle.importKey('raw', keyBytes, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
  if (mode === 'encrypt') {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(input));
    const ct = new Uint8Array(encrypted);
    return 'IV:' + Array.from(iv).map(b => b.toString(16).padStart(2, '0')).join('') + NL + '密文:' + Array.from(ct).map(b => b.toString(16).padStart(2, '0')).join('');
  } else {
    const lines = input.trim().split(NL);
    if (lines.length < 2 || !lines[0].startsWith('IV:') || !lines[1].startsWith('密文:')) return '请输入完整的加密输出（含IV行和密文行）';
    const iv = new Uint8Array(lines[0].replace('IV:', '').match(/.{1,2}/g).map(b => parseInt(b, 16)));
    const ct = new Uint8Array(lines[1].replace('密文:', '').match(/.{1,2}/g).map(b => parseInt(b, 16)));
    const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ct);
    return new TextDecoder().decode(decrypted);
  }
}

async function hashFile() {
  const file = document.getElementById('hashFileInput').files[0];
  const el = document.getElementById('hashFileResult');
  if (!file) { el.innerHTML = '请选择文件'; return; }
  try {
    const buf = await file.arrayBuffer();
    const hash = await crypto.subtle.digest('SHA-256', buf);
    const hex = Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
    el.innerHTML = '<b>文件名:</b> ' + escHtml(file.name) + ' (' + formatBytes(file.size) + ')<br><b>SHA-256:</b> ' + hex;
  } catch (e) { el.innerHTML = '文件哈希计算失败: ' + e.message; }
}

