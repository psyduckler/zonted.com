const root = document.getElementById('dialog');
const nameEl = document.getElementById('dialog-name');
const textEl = document.getElementById('dialog-text');
const hintEl = document.getElementById('dialog-hint');
const linkEl = document.getElementById('dialog-link');

const TYPE_CPS = 50;

let pages = [];
let pageIdx = 0;
let charIdx = 0;
let lastTick = 0;
let typing = false;
let open = false;
let link = null;

export function isOpen() { return open; }

function isLastPage() {
  return pageIdx === pages.length - 1;
}

function showLinkIfReady() {
  if (!linkEl) return;
  if (link && !typing && isLastPage()) {
    linkEl.textContent = link.label;
    linkEl.setAttribute('href', link.href);
    linkEl.classList.add('show');
  } else {
    linkEl.classList.remove('show');
  }
}

export function openDialog({ name = '', pages: incoming = [], link: incomingLink = null } = {}) {
  pages = Array.isArray(incoming) ? incoming : [String(incoming)];
  if (pages.length === 0) pages = [''];
  pageIdx = 0;
  charIdx = 0;
  typing = true;
  lastTick = performance.now();
  open = true;
  link = incomingLink && incomingLink.href ? incomingLink : null;
  nameEl.textContent = name;
  textEl.textContent = '';
  hintEl.classList.remove('show');
  if (linkEl) linkEl.classList.remove('show');
  root.classList.remove('hidden');
}

export function closeDialog() {
  open = false;
  typing = false;
  link = null;
  if (linkEl) linkEl.classList.remove('show');
  root.classList.add('hidden');
}

export function advance() {
  if (!open) return;
  if (typing) {
    charIdx = pages[pageIdx].length;
    textEl.textContent = pages[pageIdx];
    typing = false;
    hintEl.classList.add('show');
    showLinkIfReady();
    return;
  }
  pageIdx++;
  if (pageIdx >= pages.length) {
    closeDialog();
    return;
  }
  charIdx = 0;
  typing = true;
  lastTick = performance.now();
  textEl.textContent = '';
  hintEl.classList.remove('show');
  if (linkEl) linkEl.classList.remove('show');
}

export function tick(now) {
  if (!open || !typing) return;
  const dt = Math.max(0, (now - lastTick) / 1000);
  lastTick = now;
  charIdx = Math.min(pages[pageIdx].length, charIdx + dt * TYPE_CPS);
  textEl.textContent = pages[pageIdx].slice(0, Math.floor(charIdx));
  if (charIdx >= pages[pageIdx].length) {
    typing = false;
    hintEl.classList.add('show');
    showLinkIfReady();
  }
}
