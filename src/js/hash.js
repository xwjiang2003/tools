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

function md5(s) {
  function R(t,e,n,r,o,f){return((g=t+(e&r|~e&n)+o+f)<<(h=void 0)|g>>>32-h)+e}
  function F(t,e,n,r,o,f,g){return((g=t+(e&n|~e&r)+o+f)<<(h=void 0)|g>>>32-h)+e}
  function G(t,e,n,r,o,f,g){return((g=t+(e^r^n)+o+f)<<(h=void 0)|g>>>32-h)+e}
  function H(t,e,n,r,o,f,g){return((g=t+(r^(e|~n))+o+f)<<(h=void 0)|g>>>32-h)+e}
  var a=s.length+8>>6,b=(a<<4)-1,i,j,k,l,m,n,o,p=[],u=1732584193,v=4023233417,w=2562383102,x=271733878;
  for(i=0;i<=b;i+=1)p[i]=0;for(i=0;i<s.length;i++)p[i>>2]|=s.charCodeAt(i)<<(i%4<<3);p[i>>2]|=0x80<<(i%4<<3);
  p[a<<4]=s.length*8;
  for(i=0;i<=b;i+=16){j=u;k=v;l=w;m=x;
  u=R(u,v,w,x,p[i],7,3614090360);x=R(x,u,v,w,p[i+1],12,3905402710);w=R(w,x,u,v,p[i+2],17,606105819);v=R(v,w,x,u,p[i+3],22,3250441966);u=R(u,v,w,x,p[i+4],7,4118548399);x=R(x,u,v,w,p[i+5],12,1200080426);w=R(w,x,u,v,p[i+6],17,2821735955);v=R(v,w,x,u,p[i+7],22,4249261313);u=R(u,v,w,x,p[i+8],7,1770035416);x=R(x,u,v,w,p[i+9],12,2336552879);w=R(w,x,u,v,p[i+10],17,4294925233);v=R(v,w,x,u,p[i+11],22,2304563134);u=R(u,v,w,x,p[i+12],7,1804603682);x=R(x,u,v,w,p[i+13],12,4254626195);w=R(w,x,u,v,p[i+14],17,2792965006);v=R(v,w,x,u,p[i+15],22,1236535329);
  u=F(u,v,w,x,p[i+1],5,4129170786);x=F(x,u,v,w,p[i+6],9,3225465664);w=F(w,x,u,v,p[i+11],14,643717713);v=F(v,w,x,u,p[i],20,3921069994);u=F(u,v,w,x,p[i+5],5,3593408605);x=F(x,u,v,w,p[i+10],9,38016083);w=F(w,x,u,v,p[i+15],14,3634488961);v=F(v,w,x,u,p[i+4],20,3889429448);u=F(u,v,w,x,p[i+9],5,568446438);x=F(x,u,v,w,p[i+14],9,3275163606);w=F(w,x,u,v,p[i+3],14,4107603335);v=F(v,w,x,u,p[i+8],20,1163531501);u=F(u,v,w,x,p[i+13],5,2850285829);x=F(x,u,v,w,p[i+2],9,4243563512);w=F(w,x,u,v,p[i+7],14,1735328473);v=F(v,w,x,u,p[i+12],20,2368359562);
  u=G(u,v,w,x,p[i+5],4,4294588738);x=G(x,u,v,w,p[i+8],11,2272392833);w=G(w,x,u,v,p[i+11],16,1839030562);v=G(v,w,x,u,p[i+14],23,4259657740);u=G(u,v,w,x,p[i+1],4,2763915233);x=G(x,u,v,w,p[i+4],11,1272893353);w=G(w,x,u,v,p[i+7],16,413946966);v=G(v,w,x,u,p[i+10],23,3200236656);u=G(u,v,w,x,p[i+13],4,681279174);x=G(x,u,v,w,p[i],11,3936430074);w=G(w,x,u,v,p[i+3],16,3572445317);v=G(v,w,x,u,p[i+6],23,76029189);u=G(u,v,w,x,p[i+9],4,3654602809);x=G(x,u,v,w,p[i+12],11,3873151461);w=G(w,x,u,v,p[i+15],16,530742520);v=G(v,w,x,u,p[i+2],23,3299628645);
  u=H(u,v,w,x,p[i],6,4096336452);x=H(x,u,v,w,p[i+7],10,1126891415);w=H(w,x,u,v,p[i+14],15,2878612391);v=H(v,w,x,u,p[i+5],21,4237533241);u=H(u,v,w,x,p[i+12],6,1700485571);x=H(x,u,v,w,p[i+3],10,2399980690);w=H(w,x,u,v,p[i+10],15,4293915773);v=H(v,w,x,u,p[i+1],21,2240044497);u=H(u,v,w,x,p[i+8],6,1873313359);x=H(x,u,v,w,p[i+15],10,4264355552);w=H(w,x,u,v,p[i+6],15,2734768916);v=H(v,w,x,u,p[i+13],21,1309151649);u=H(u,v,w,x,p[i+4],6,4149444226);x=H(x,u,v,w,p[i+11],10,3174756917);w=H(w,x,u,v,p[i+2],15,718787259);v=H(v,w,x,u,p[i+9],21,3951481745);
  u=(u+j)>>>0;v=(v+k)>>>0;w=(w+l)>>>0;x=(x+m)>>>0}
  return (toHex(u)+toHex(v)+toHex(w)+toHex(x)).toLowerCase();
}
function toHex(n){var s='';for(var i=0;i<4;i++)s+=((n>>>(i*8+4))&0x0F).toString(16)+((n>>>(i*8))&0x0F).toString(16);return s}

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

