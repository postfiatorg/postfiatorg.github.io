// Opens the password-protected exchange integration page. The page ships as AES-256-GCM ciphertext
// (locked.json); the key is derived from the password with PBKDF2-SHA256 and never leaves the browser.
const $ = (s, r = document) => r.querySelector(s);
const enc = new TextEncoder();
const bytes = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const b64 = buf => btoa(String.fromCharCode(...new Uint8Array(buf)));
const SAVED = 'xi-key';

const box = fetch('/exchange-integration/locked.json', { cache: 'no-cache' })
  .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); });

async function derive(password, b) {
  const base = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']);
  return crypto.subtle.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt: bytes(b.salt), iterations: b.iterations },
    base, { name: 'AES-GCM', length: 256 }, true, ['decrypt']);
}

async function decrypt(key, b) {
  const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: bytes(b.iv) }, key, bytes(b.ct));
  const text = await new Response(new Blob([plain]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  return JSON.parse(text);
}

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch {}
  const area = document.createElement('textarea');
  area.value = text; area.setAttribute('readonly', ''); area.style.cssText = 'position:fixed;top:0;left:-9999px';
  document.body.appendChild(area); area.select();
  const ok = document.execCommand('copy'); area.remove();
  return ok;
}

async function render(p) {
  $('#xi-root').innerHTML = p.html;
  const urls = {};
  for (const [name, text] of Object.entries(p.files)) {
    urls[name] = URL.createObjectURL(new Blob([text], { type: name.endsWith('.json') ? 'application/json' : 'text/plain' }));
  }
  document.querySelectorAll('#xi-root a[href^="/exchange-integration/"]').forEach(a => {
    const name = a.getAttribute('href').split('/').pop();
    if (urls[name]) { a.href = urls[name]; a.download = name; }
  });
  const words = p.md.split(/\s+/).length.toLocaleString('en-US');
  document.querySelectorAll('[data-xi-llm]').forEach(btn => btn.addEventListener('click', async () => {
    const status = $('[data-xi-llm-status]');
    const ok = await copyText(p.md);
    if (status) status.textContent = ok ? `Copied as Markdown, about ${words} words. Paste it into any LLM.` : 'Copy failed. Please try again.';
  }));
  const addr = new URL('/exchange-integration/address.js', location.href).href;
  const js = URL.createObjectURL(new Blob([p.js.replace("from './address.js'", `from '${addr}'`)], { type: 'text/javascript' }));
  await import(js);
  if (location.hash) document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();
}

async function trySaved() {
  const saved = sessionStorage.getItem(SAVED);
  if (!saved || !crypto.subtle) return false;
  try {
    const b = await box;
    const [salt, raw] = saved.split(':');
    if (salt !== b.salt) throw new Error('stale');
    const key = await crypto.subtle.importKey('raw', bytes(raw), 'AES-GCM', false, ['decrypt']);
    await render(await decrypt(key, b));
    return true;
  } catch {
    sessionStorage.removeItem(SAVED);
    return false;
  }
}

const form = $('#xi-lockform');
const msg = $('#xi-lockmsg');
form.addEventListener('submit', async e => {
  e.preventDefault();
  const btn = form.querySelector('button');
  btn.disabled = true; msg.className = 'xi-lockmsg'; msg.textContent = 'Opening…';
  if (!crypto.subtle) {
    btn.disabled = false; msg.className = 'xi-lockmsg bad';
    msg.textContent = 'This page decrypts in the browser and needs a secure (https) connection.';
    return;
  }
  let p;
  try {
    const b = await box;
    const key = await derive($('#xi-pw').value, b);
    p = await decrypt(key, b);
    sessionStorage.setItem(SAVED, `${b.salt}:${b64(await crypto.subtle.exportKey('raw', key))}`);
  } catch (err) {
    btn.disabled = false; msg.className = 'xi-lockmsg bad';
    msg.textContent = err instanceof DOMException && err.name === 'OperationError'
      ? 'That password did not open the page.' : 'The page could not be loaded. Please reload and try again.';
    $('#xi-pw').select();
    return;
  }
  await render(p);
});

trySaved();
