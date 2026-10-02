/* TransLog frontend */
const $ = (id) => document.getElementById(id);

const I = {
  doc: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M13.1719 2.09961C13.9408 2.09969 14.6789 2.40555 15.2227 2.94922L19.0508 6.77734C19.5946 7.32113 19.9003 8.05911 19.9004 8.82812V18C19.9004 20.1539 18.1539 21.9004 16 21.9004H8C5.84626 21.9002 4.09961 20.1538 4.09961 18V6C4.09961 3.84621 5.84626 2.09981 8 2.09961H13.1719ZM8 3.90039C6.84037 3.90059 5.90039 4.84032 5.90039 6V18C5.90039 19.1597 6.84037 20.0994 8 20.0996H16C17.1598 20.0996 18.0996 19.1598 18.0996 18V9.90039H15C13.3985 9.90019 12.0996 8.6015 12.0996 7V3.90039H8ZM13.9004 7C13.9004 7.60739 14.3927 8.09941 15 8.09961H17.8213C17.8068 8.08333 17.7928 8.06626 17.7773 8.05078L13.9492 4.22266C13.9335 4.20696 13.9169 4.19237 13.9004 4.17773V7Z" fill="currentColor"/></svg>',
  docok: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M13.1719 2.09961C13.9408 2.09969 14.6789 2.40555 15.2227 2.94922L19.0508 6.77734C19.5946 7.32113 19.9003 8.05911 19.9004 8.82812V18C19.9004 20.1539 18.1539 21.9004 16 21.9004H8C5.84626 21.9002 4.09961 20.1538 4.09961 18V6C4.09961 3.84621 5.84626 2.09981 8 2.09961H13.1719ZM8 3.90039C6.84037 3.90059 5.90039 4.84032 5.90039 6V18C5.90039 19.1597 6.84037 20.0994 8 20.0996H16C17.1598 20.0996 18.0996 19.1598 18.0996 18V9.90039H15C13.3985 9.90019 12.0996 8.6015 12.0996 7V3.90039H8ZM13.9004 7C13.9004 7.60739 14.3927 8.09941 15 8.09961H17.8213C17.8068 8.08333 17.7928 8.06626 17.7773 8.05078L13.9492 4.22266C13.9335 4.20696 13.9169 4.19237 13.9004 4.17773V7Z" fill="currentColor"/><path fill-rule="evenodd" clip-rule="evenodd" d="M16.1368 12.2636C16.4882 12.6151 16.4882 13.1849 16.1368 13.5364L12.6974 16.9757C11.7602 17.913 10.2406 17.913 9.30332 16.9757L7.86398 15.5364C7.5125 15.1849 7.5125 14.6151 7.86398 14.2636C8.21545 13.9121 8.7853 13.9121 9.13677 14.2636L10.5761 15.7029C10.8104 15.9373 11.1903 15.9373 11.4246 15.7029L14.864 12.2636C15.2154 11.9121 15.7853 11.9121 16.1368 12.2636Z" fill="currentColor"/></svg>',
  up: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M11.3636 3.36358C11.7151 3.01211 12.2849 3.01211 12.6364 3.36358L17.0808 7.80802C17.4323 8.1595 17.4323 8.72934 17.0808 9.08082C16.7293 9.43229 16.1595 9.43229 15.808 9.08082L12.9 6.17277V14.6666C12.9 15.1637 12.497 15.5666 12 15.5666C11.5029 15.5666 11.1 15.1637 11.1 14.6666V6.17277L8.19193 9.08082C7.84046 9.43229 7.27061 9.43229 6.91914 9.08082C6.56766 8.72934 6.56766 8.1595 6.91914 7.80802L11.3636 3.36358ZM3.99998 13.7666C4.49703 13.7666 4.89998 14.1696 4.89998 14.6666V18.2222C4.89998 18.455 4.99246 18.6783 5.15707 18.8429C5.32169 19.0075 5.54495 19.1 5.77775 19.1H18.2222C18.455 19.1 18.6783 19.0075 18.8429 18.8429C19.0075 18.6783 19.1 18.455 19.1 18.2222V14.6666C19.1 14.1696 19.5029 13.7666 20 13.7666C20.497 13.7666 20.9 14.1696 20.9 14.6666V18.2222C20.9 18.9324 20.6179 19.6135 20.1157 20.1157C19.6135 20.6179 18.9324 20.9 18.2222 20.9H5.77775C5.06756 20.9 4.38646 20.6179 3.88428 20.1157C3.3821 19.6135 3.09998 18.9324 3.09998 18.2222V14.6666C3.09998 14.1696 3.50292 13.7666 3.99998 13.7666Z" fill="currentColor"/></svg>',
  dl: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2.90002C12.4971 2.90002 12.9 3.30297 12.9 3.80002V12.2939L15.8081 9.38585C16.1595 9.03438 16.7294 9.03438 17.0808 9.38585C17.4323 9.73732 17.4323 10.3072 17.0808 10.6586L12.6364 15.1031C12.4676 15.2719 12.2387 15.3667 12 15.3667C11.7613 15.3667 11.5324 15.2719 11.3636 15.1031L6.91917 10.6586C6.5677 10.3072 6.5677 9.73732 6.91917 9.38585C7.27064 9.03438 7.84049 9.03438 8.19196 9.38585L11.1 12.2939V3.80002C11.1 3.30297 11.503 2.90002 12 2.90002ZM4.00001 13.5874C4.49706 13.5874 4.90001 13.9903 4.90001 14.4874V18.043C4.90001 18.2758 4.99249 18.499 5.1571 18.6636C5.32172 18.8282 5.54498 18.9207 5.77778 18.9207H18.2222C18.455 18.9207 18.6783 18.8283 18.8429 18.6636C19.0075 18.499 19.1 18.2758 19.1 18.043V14.4874C19.1 13.9903 19.5029 13.5874 20 13.5874C20.4971 13.5874 20.9 13.9903 20.9 14.4874V18.043C20.9 18.7531 20.6179 19.4342 20.1157 19.9364C19.6135 20.4386 18.9324 20.7207 18.2222 20.7207H5.77778C5.06759 20.7207 4.38649 20.4386 3.88431 19.9364C3.38213 19.4342 3.10001 18.7531 3.10001 18.043V14.4874C3.10001 13.9903 3.50295 13.5874 4.00001 13.5874Z" fill="currentColor"/></svg>',
  send: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" style="transform:rotate(90deg)"><path d="M16.5364 10.1636C16.8879 10.5151 16.8879 11.0849 16.5364 11.4364C16.1849 11.7879 15.6151 11.7879 15.2636 11.4364L12.9 9.07281V17.1C12.9 17.597 12.4971 18 12 18C11.503 18 11.1 17.597 11.1 17.1V9.07281L8.73641 11.4364C8.38494 11.7879 7.81509 11.7879 7.46362 11.4364C7.11214 11.0849 7.11214 10.5151 7.46362 10.1636L11.3636 6.2636C11.7151 5.91211 12.2849 5.91211 12.6364 6.2636L16.5364 10.1636Z" fill="currentColor"/></svg>',
  clip: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path fill-rule="evenodd" clip-rule="evenodd" d="M5.33687 6.99039C5.3578 5.78589 5.85099 4.6378 6.7102 3.79339C7.56941 2.94899 8.7259 2.47583 9.93058 2.47583C11.1353 2.47583 12.2918 2.94899 13.151 3.79339C14.0102 4.6378 14.5034 5.78589 14.5243 6.9904L14.5244 6.99413L14.6366 15.4805L14.6367 15.4826C14.6427 15.8466 14.5763 16.2082 14.4414 16.5464C14.3062 16.8852 14.1049 17.1937 13.8492 17.4539C13.5935 17.714 13.2886 17.9207 12.9522 18.0617C12.6158 18.2028 12.2546 18.2754 11.8898 18.2754C11.5251 18.2754 11.1639 18.2028 10.8275 18.0617C10.4911 17.9207 10.1862 17.714 9.93046 17.4539C9.67477 17.1937 9.47346 16.8852 9.33826 16.5464C9.20413 16.2102 9.13775 15.8509 9.14291 15.4891L9.14291 6.8937C9.14291 6.39665 9.54585 5.9937 10.0429 5.9937C10.54 5.9937 10.9429 6.39665 10.9429 6.8937L10.9429 15.4961L10.9428 15.5118C10.9406 15.6375 10.9635 15.7625 11.0101 15.8793C11.0567 15.9961 11.1261 16.1025 11.2143 16.1922C11.3024 16.2819 11.4076 16.3531 11.5236 16.4018C11.6395 16.4504 11.7641 16.4754 11.8898 16.4754C12.0156 16.4754 12.1401 16.4504 12.2561 16.4018C12.3721 16.3531 12.4772 16.2819 12.5654 16.1922C12.6536 16.1025 12.723 15.9961 12.7696 15.8793C12.8162 15.7625 12.8391 15.6375 12.8369 15.5118L12.8368 15.508L12.7246 7.02168L12.7245 7.0199C12.7113 6.28795 12.4114 5.59037 11.8893 5.0772C11.3667 4.56361 10.6633 4.27583 9.93058 4.27583C9.19787 4.27583 8.49447 4.56361 7.97188 5.0772C7.45232 5.5878 7.15282 6.28097 7.13685 7.00892L7.24783 15.4961C7.24783 16.7273 7.73683 17.908 8.60739 18.7786C9.47795 19.6491 10.6587 20.1382 11.8898 20.1382C13.121 20.1382 14.3017 19.6491 15.1723 18.7786C16.0428 17.908 16.5319 16.7273 16.5319 15.4961L16.5411 7.33157C16.5416 6.83451 16.945 6.43202 17.4421 6.43258C17.9391 6.43313 18.3416 6.83653 18.3411 7.33359L18.3319 15.4961C18.3318 17.2045 17.6531 18.8434 16.4451 20.0514C15.2369 21.2595 13.5984 21.9382 11.8898 21.9382C10.1813 21.9382 8.54272 21.2595 7.3346 20.0514C6.12791 18.8447 5.44937 17.2086 5.44776 15.5022L5.33681 7.0178C5.33669 7.00867 5.33671 6.99953 5.33687 6.99039Z" fill="currentColor"/></svg>',
  pin: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M18.9003 10.7998C18.9002 7.08572 16.2547 3.90039 11.9999 3.90039C7.74237 3.90047 5.10056 7.05052 5.10046 10.7998C5.10046 13.0829 6.29178 15.183 7.80359 16.916C9.30556 18.6377 11.0351 19.8955 11.91 20.4775C11.9433 20.4997 11.9743 20.5068 11.9999 20.5068C12.0255 20.5068 12.0564 20.4997 12.0897 20.4775C12.9646 19.8955 14.6942 18.6377 16.1962 16.916C17.708 15.183 18.8993 13.083 18.9003 10.7998ZM11.9999 6.00039C14.0894 6.00039 15.7994 7.80835 15.7994 10.0311C15.7994 12.2538 14.0894 14.0618 11.9999 14.0618C9.91034 14.0618 8.20037 12.2538 8.20037 10.0311C8.20037 7.80835 9.91034 6.00039 11.9999 6.00039Z" fill="currentColor"/></svg>',
  check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M19.3027 5.9053C19.6542 5.55397 20.2247 5.55388 20.5761 5.9053C20.9273 6.25675 20.9273 6.82734 20.5761 7.17874L9.65911 18.0948C9.30773 18.4461 8.73814 18.446 8.38665 18.0948L3.42376 13.1328C3.0726 12.7814 3.07263 12.2118 3.42376 11.8604C3.77524 11.509 4.34575 11.5089 4.6972 11.8604L9.02239 16.1856L19.3027 5.9053Z" fill="currentColor"/></svg>',
  close: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M17.9542 4.77253C18.3056 4.42106 18.8761 4.42106 19.2276 4.77253C19.579 5.12401 19.579 5.69452 19.2276 6.04597L13.2735 12.0001L19.2276 17.9542C19.5791 18.3056 19.5791 18.8761 19.2276 19.2276C18.8761 19.5791 18.3056 19.5791 17.9542 19.2276L12.0001 13.2735L6.04595 19.2276C5.69451 19.5791 5.12399 19.5791 4.77255 19.2276C4.42111 18.8761 4.42111 18.3056 4.77255 17.9542L10.7267 12.0001L4.77253 6.04595C4.42106 5.69451 4.42106 5.12399 4.77253 4.77255C5.12401 4.42111 5.69452 4.42111 6.04597 4.77255L12.0001 10.7267L17.9542 4.77253Z" fill="currentColor"/></svg>',
  search: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M11.5 3C16.1944 3 20 6.80558 20 11.5C20 13.523 19.2933 15.381 18.1132 16.8404L21.1364 19.8636C21.4879 20.2151 21.4879 20.7849 21.1364 21.1364C20.7849 21.4879 20.2151 21.4879 19.8636 21.1364L16.8404 18.1132C15.381 19.2933 13.523 20 11.5 20C6.80558 20 3 16.1944 3 11.5C3 6.80558 6.80558 3 11.5 3ZM11.5 4.8C7.79908 4.8 4.8 7.79908 4.8 11.5C4.8 15.2009 7.79908 18.2 11.5 18.2C15.2009 18.2 18.2 15.2009 18.2 11.5C18.2 7.79908 15.2009 4.8 11.5 4.8Z" fill="currentColor"/></svg>',
  warn: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M12 3C12.42 3 12.81 3.23 13.01 3.6L21.35 18.6C21.55 18.96 21.55 19.4 21.35 19.76C21.15 20.12 20.76 20.35 20.34 20.35H3.66C3.24 20.35 2.85 20.12 2.65 19.76C2.45 19.4 2.45 18.96 2.65 18.6L10.99 3.6C11.19 3.23 11.58 3 12 3ZM12 8C11.5 8 11.1 8.4 11.1 8.9V13.1C11.1 13.6 11.5 14 12 14C12.5 14 12.9 13.6 12.9 13.1V8.9C12.9 8.4 12.5 8 12 8ZM12.9 15.9C12.9 15.4 12.5 15 12 15C11.5 15 11.1 15.4 11.1 15.9V16.1C11.1 16.6 11.5 17 12 17C12.5 17 12.9 16.6 12.9 16.1V15.9Z" fill="currentColor"/></svg>'
};

const ORD = {enroute:['в пути','c-blue'], loading:['погрузка','c-gray'], problem:['проблема','c-red'], done:['доставлен','c-green']};
const DST = {review:['На проверке','c-amber'], approved:['Одобрен','c-green'], rejected:['Отклонён','c-red']};
const AVC = ['#2563eb','#dc2626','#16a34a','#7c3aed'];

let ME = null;
let orders = [];
let docs = [];
let exports_ = [];
let settingsOpen = false;
let active = null;
let filter = 'all';
let q = '';
let lastMsgId = 0;
let chatTimer = null;
let ordersTimer = null;

async function api(url, opts) {
  const r = await fetch(url, opts);
  if (r.status === 401) { showLogin(); throw new Error('unauthorized'); }
  if (!r.ok) {
    const e = await r.json().catch(() => ({error: 'Ошибка сервера'}));
    throw new Error(e.error || 'Ошибка сервера');
  }
  return r.json();
}

const esc = (s) => String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

/* ---------- auth ---------- */
async function boot() {
  try {
    ME = await api('/api/me');
    showApp();
  } catch (e) { showLogin(); }
}
function showLogin() {
  stopTimers();
  $('app-view').classList.add('hidden');
  $('login-view').classList.remove('hidden');
}
function showApp() {
  $('login-view').classList.add('hidden');
  $('app-view').classList.remove('hidden');
  if (ME.role === 'dispatcher') $('settings-btn').style.display = '';
  active = ME.role === 'driver' ? ME.order_id : (orders[0] && orders[0].id);
  refreshAll();
  startTimers();
}
async function doLogin() {
  $('li-error').textContent = '';
  try {
    ME = await api('/api/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({login: $('li-login').value.trim(), password: $('li-pass').value})
    });
    showApp();
  } catch (e) {
    $('li-error').textContent = e.message === 'unauthorized' ? 'Неверный логин или пароль' : e.message;
  }
}
async function doLogout() {
  await api('/api/logout', {method: 'POST'}).catch(() => {});
  ME = null; showLogin();
}
$('li-pass').addEventListener('keydown', (e) => { if (e.key === 'Enter') doLogin(); });
$('li-login').addEventListener('keydown', (e) => { if (e.key === 'Enter') doLogin(); });

/* ---------- data ---------- */
async function refreshAll() {
  orders = await api('/api/orders');
  if (ME.role === 'driver') active = ME.order_id;
  else if (!orders.find(o => o.id === active)) active = orders[0] && orders[0].id;
  renderStats(); renderSide();
  await refreshDocs(); await refreshChat(true); await refreshExports();
}
async function refreshExports() {
  exports_ = await api('/api/exports').catch(() => []);
  renderExports();
}
async function refreshDocs() {
  const p = new URLSearchParams();
  if (filter !== 'all') p.set('status', filter);
  if (q) p.set('q', q);
  docs = await api('/api/docs?' + p.toString());
  renderCenter();
  if (ME) renderStats();
}
async function refreshChat(full) {
  if (!active) return;
  const after = full ? 0 : lastMsgId;
  const msgs = await api('/api/msgs?order_id=' + encodeURIComponent(active) + '&after_id=' + after);
  if (full) {
    CHAT_CACHE[active] = msgs;
    lastMsgId = msgs.length ? msgs[msgs.length - 1].id : 0;
    renderChat();
    const o = orders.find(x => x.id === active);
    if (o) o.unread = 0;
    renderStats(); renderSide();
  } else if (msgs.length) {
    lastMsgId = msgs[msgs.length - 1].id;
    appendMsgs(msgs);
  }
}
function startTimers() {
  stopTimers();
  chatTimer = setInterval(() => refreshChat(false).catch(() => {}), 2500);
  ordersTimer = setInterval(async () => {
    try {
      const fresh = await api('/api/orders');
      if (JSON.stringify(fresh) !== JSON.stringify(orders)) { orders = fresh; renderStats(); renderSide(); }
    } catch (e) {}
  }, 5000);
}
function stopTimers() {
  if (chatTimer) clearInterval(chatTimer);
  if (ordersTimer) clearInterval(ordersTimer);
  chatTimer = ordersTimer = null;
}

/* ---------- render ---------- */
function renderStats() {
  const rc = docs.filter(d => d.status === 'review').length;
  const un = orders.reduce((s, o) => s + o.unread, 0);
  $('stats').innerHTML =
    '<span class="chip c-amber">' + I.warn + ' На проверке: ' + rc + '</span>' +
    '<span class="chip c-blue"><svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M18 4H6C4.9 4 4 4.9 4 6V15L2 18H22L20 15V6C20 4.9 19.1 4 18 4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg> Непрочитанных: ' + un + '</span>';
  $('me-box').textContent = ME.name + (ME.role === 'dispatcher' ? ' · диспетчер' : ' · водитель');
}

function orderCard(o, clickable) {
  const st = ORD[o.status] || ['', 'c-gray'];
  const av = AVC[orders.indexOf(o) % AVC.length];
  const badge = (o.review_count ? '<span class="chip c-amber">' + I.warn + ' ' + o.review_count + '</span>' : '') +
                (o.unread ? '<span class="chip c-blue">' + o.unread + ' новых</span>' : '');
  return '<button class="ord ' + (active === o.id ? 'on' : '') + '" ' + (clickable ? 'onclick="selectOrder(\'' + o.id + '\')"' : '') + ' style="cursor:' + (clickable ? 'pointer' : 'default') + '">' +
    '<div class="o-top"><span class="oid">' + o.id + '</span><span class="chip c-gray">' + esc(o.request_no || '') + '</span><span class="chip ' + st[1] + '">' + st[0] + '</span></div>' +
    '<div class="oname">' + esc(o.driver) + '</div>' +
    '<div class="oroute">' + I.pin + esc(o.route) + '</div>' +
    '<div class="ometa">' + esc(o.cargo) + ' · ' + esc(o.plate) + '</div>' +
    (badge ? '<div class="obadges">' + badge + '</div>' : '') + '</button>';
}

function renderSide() {
  if (ME.role === 'driver') {
    const o = orders.find(x => x.id === ME.order_id);
    $('side').innerHTML = '<p class="side-t">Мой рейс</p>' + (o ? orderCard(o, false) : '') +
      '<p class="side-t" style="margin-top:14px">Отправляйте документы формой ниже — диспетчер проверит их и ответит в чате.</p>';
  } else {
    $('side').innerHTML = '<p class="side-t">Рейсы и водители</p>' + orders.map(o => orderCard(o, true)).join('');
  }
}

function docRow(d) {
  const o = orders.find(x => x.id === d.order_id);
  const st = DST[d.status];
  let act = '';
  if (ME.role === 'dispatcher' && d.status === 'review') {
    act = '<div class="dact"><button class="ibtn ok" onclick="approveDoc(' + d.id + ')">' + I.check + ' Одобрить</button>' +
          '<button class="ibtn no" onclick="rejectDoc(' + d.id + ')">' + I.close + ' Отклонить</button></div>';
  }
  if (d.status === 'rejected' && (ME.role === 'driver' || d.uploader === ME.name)) {
    act = '<div class="dact"><button class="ibtn" onclick="resendDoc(' + d.id + ')">' + I.up + ' Отправить повторно</button></div>';
  }
  return '<div class="doc"><div class="dic">' + (d.status === 'approved' ? I.docok : I.doc) + '</div>' +
    '<div class="dmain"><div class="dname">' + esc(d.name) + '<span class="chip c-gray">' + esc(d.type) + '</span></div>' +
    '<div class="dmeta">' + d.order_id + ' · ' + esc(o ? o.driver : d.uploader) + ' · ' + d.size + ' · ' + d.time + (d.comment ? ' · ' + esc(d.comment) : '') + megaLink(d.mega_url) + '</div>' + act + '</div>' +
    '<div class="dright"><span class="chip ' + st[1] + '">' + st[0] + '</span>' +
    '<a class="ibtn" href="/api/docs/' + d.id + '/download">' + I.dl + ' Скачать</a></div></div>';
}

function renderCenter() {
  let html = '';
  if (settingsOpen && ME.role === 'dispatcher') {
    html += '<div class="panel" id="settings-panel"><div class="panel-t">Интеграция TransTrade API</div>' +
      '<p class="sett-hint">Документация: <a href="https://tt-ok.ru/data/api_doc/" target="_blank" rel="noopener">tt-ok.ru/data/api_doc</a>. ' +
      'API KEY и api_user_id высылаются почтой после подключения модуля.</p>' +
      '<div class="sett-grid">' +
      '<label>API URL</label><input id="tt-url" placeholder="https://tt-ok.ru/data/api">' +
      '<label>API KEY</label><input id="tt-key" placeholder="••••••••" autocomplete="off">' +
      '<label>api_user_id</label><input id="tt-uid" placeholder="1">' +
      '</div>' +
      '<div class="uprow"><button class="btn-p" onclick="saveTTSettings()">Сохранить</button>' +
      '<button class="ibtn" onclick="testTT()">Проверить подключение</button></div>' +
      '<div id="tt-status"></div></div>';
    html += '<div class="panel"><div class="panel-t">Облачное хранилище MEGA</div>' +
      '<p class="sett-hint">Документы и ZIP-архивы дублируются в MEGA и получают публичные ссылки. ' +
      'Двухфакторная аутентификация MEGA должна быть выключена.</p>' +
      '<div class="sett-grid">' +
      '<label>MEGA email</label><input id="mega-email" placeholder="you@example.com">' +
      '<label>MEGA пароль</label><input id="mega-pass" type="password" placeholder="••••••••" autocomplete="off">' +
      '</div>' +
      '<div class="uprow"><button class="btn-p" onclick="saveMega()">Сохранить</button>' +
      '<button class="ibtn" onclick="testMega()">Проверить вход</button></div>' +
      '<div id="mega-status"></div></div>';
  }
  if (ME.role === 'driver') {
    html += '<div class="panel"><div class="panel-t">' + I.up + ' Отправить документ</div>' +
      '<div class="uprow"><select id="upType"><option>CMR</option><option>ТТН</option><option>Путевой лист</option><option>Доверенность</option><option>Счёт-фактура</option><option>Другое</option></select></div>' +
      '<label class="filelab">' + I.clip + '<span id="fname">Выбрать файл…</span><input type="file" id="upFile" hidden onchange="filePick(this)"></label>' +
      '<div class="uprow"><input id="upCmt" placeholder="Комментарий для диспетчера (необязательно)"></div>' +
      '<button class="btn-p" onclick="uploadDoc()">' + I.up + ' Отправить на проверку</button></div>';
  }
  html += '<div class="panel"><div class="panel-t">' + I.doc + ' ' + (ME.role === 'driver' ? 'Мои документы' : 'Входящие документы') + '</div>';
  if (ME.role === 'dispatcher') {
    const chips = [['all','Все'],['review','На проверке'],['approved','Одобрены'],['rejected','Отклонённые']];
    html += '<div class="fchips">' + chips.map(c => '<button class="' + (filter === c[0] ? 'on' : '') + '" onclick="setFilter(\'' + c[0] + '\')">' + c[1] + '</button>').join('') + '</div>' +
      '<div class="search">' + I.search + '<input placeholder="Поиск по названию или типу…" value="' + esc(q) + '" oninput="setQ(this.value)"></div>';
  }
  html += docs.length ? docs.map(docRow).join('') : '<div class="empty">Документов не найдено</div>';
  html += '</div>';
  html += '<div class="panel"><div class="panel-t">' + I.doc + ' Архивы документов (ZIP)</div><div id="exp-box"></div></div>';
  $('center').innerHTML = html;
  renderExports();
  if (settingsOpen && ME.role === 'dispatcher') { loadTTSettings(); loadMegaSettings(); }
}

function renderExports() {
  const box = $('exp-box');
  if (!box) return;
  const o = orders.find(x => x.id === active);
  let html = '';
  if (o) {
    const n = docs.filter(d => d.order_id === o.id).length;
    html += '<div class="uprow" style="margin-bottom:8px"><button class="ibtn" onclick="doExport()">' + I.dl +
      ' Сформировать ZIP по рейсу ' + esc(o.id) + ' (заявка ' + esc(o.request_no || '—') + ', документов: ' + n + ')</button></div>';
  }
  const list = ME.role === 'driver' ? exports_ : (active ? exports_.filter(e => e.order_id === active) : exports_);
  html += list.length ? list.map(e =>
    '<div class="doc"><div class="dic">' + I.doc + '</div>' +
    '<div class="dmain"><div class="dname">' + esc(e.filename) + '</div>' +
    '<div class="dmeta">' + e.order_id + ' · заявка ' + esc(e.request_no || '—') + ' · файлов: ' + e.doc_count + ' · ' + e.size + ' · ' + e.time + ' · ' + esc(e.created_by) + megaLink(e.mega_url) + '</div></div>' +
    '<div class="dright"><a class="ibtn" href="/api/exports/' + e.id + '/download">' + I.dl + ' Скачать</a></div></div>'
  ).join('') : '<div class="empty">Архивов пока нет</div>';
  box.innerHTML = html;
}

function msgHtml(m) {
  if (m.who === 'sys') return '<div class="msys">' + esc(m.text) + ' · ' + m.time + '</div>';
  const mine = m.who === ME.role;
  let body;
  if (m.doc) {
    body = '<div class="bdoc" onclick="openDocView(' + m.doc.id + ',' + JSON.stringify(m.doc.name) + ')">' + (m.doc.status === 'approved' ? I.docok : I.doc) +
      '<div><div class="bdname">' + esc(m.doc.name) + '</div><div class="bdmeta">' + esc(m.doc.type) + ' · ' + m.doc.size +
      ' · <a href="/api/docs/' + m.doc.id + '/download" onclick="event.stopPropagation()">скачать</a></div></div></div>';
  } else {
    body = esc(m.text);
  }
  return '<div class="mrow ' + (mine ? 'me' : '') + '"><div class="b ' + (mine ? 'me' : 'them') + '">' + body +
    '<span class="bt">' + m.time + '</span></div></div>';
}

function renderChat() {
  if (!active) { $('chatbox').innerHTML = ''; return; }
  const o = orders.find(x => x.id === active);
  if (!o) { $('chatbox').innerHTML = ''; return; }
  const name = ME.role === 'driver' ? 'Диспетчер Алексей' : o.driver;
  const init = ME.role === 'driver' ? 'Д' : o.driver.split(' ').map(w => w[0]).join('');
  const col = ME.role === 'driver' ? 'var(--text2)' : AVC[orders.indexOf(o) % AVC.length];
  $('chatbox').innerHTML = '<div class="chat"><div class="ch-head">' +
    '<div class="av" style="background:color-mix(in srgb,' + col + ' 15%,transparent);color:' + col + '">' + init + '</div>' +
    '<div><div class="ch-name">' + esc(name) + '</div><div class="ch-sub">' + o.id + ' · заявка ' + esc(o.request_no || '—') + ' · ' + esc(o.route) + '</div></div>' +
    '<span class="chip ' + (ORD[o.status] ? ORD[o.status][1] : 'c-gray') + '" style="margin-left:auto">' + (ORD[o.status] ? ORD[o.status][0] : o.status) + '</span></div>' +
    (ME.role === 'dispatcher' ? '<div class="ch-tt"><button class="ibtn" onclick="pushTT()">' + I.up + ' Отправить заказ в TransTrade' +
      (o.tt_order_id ? ' (ID ' + esc(o.tt_order_id) + ' — обновит)' : '') + '</button></div>' : '') +
    '<div class="ch-msgs" id="msgs"></div>' +
    '<div class="ch-in"><button class="iconbtn" title="Прикрепить последний документ рейса" onclick="attachDoc()">' + I.clip + '</button>' +
    '<input id="chatIn" placeholder="Сообщение…" onkeydown="if(event.key===\'Enter\')sendMsg()">' +
    '<button class="send" onclick="sendMsg()">' + I.send + '</button></div></div>';
  renderMsgList();
}
function renderMsgList() {
  const box = $('msgs');
  if (!box) return;
  box.innerHTML = (CHAT_CACHE[active] || []).map(msgHtml).join('') || '<div class="empty">Сообщений пока нет — напишите первым</div>';
  box.scrollTop = box.scrollHeight;
}
let CHAT_CACHE = {};
function appendMsgs(msgs) {
  (CHAT_CACHE[active] = CHAT_CACHE[active] || []).push(...msgs);
  const box = $('msgs');
  if (box && box.closest('#chatbox')) {
    const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 60;
    box.insertAdjacentHTML('beforeend', msgs.map(msgHtml).join(''));
    if (nearBottom) box.scrollTop = box.scrollHeight;
  }
  const o = orders.find(x => x.id === active);
  if (o) { o.unread = 0; renderStats(); renderSide(); }
}

/* ---------- просмотр документа из чата ---------- */
function openDocView(id, name) {
  const url = '/api/docs/' + id + '/download';
  const ext = (name.split('.').pop() || '').toLowerCase();
  if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
    $('docview-body').innerHTML = '<img src="' + url + '" alt="">';
  } else if (ext === 'pdf') {
    $('docview-body').innerHTML = '<embed src="' + url + '" type="application/pdf">';
  } else {
    window.location.href = url; // неизвестный тип — просто скачиваем
    return;
  }
  $('docview-name').textContent = name;
  $('docview-dl').href = url;
  $('docview').classList.remove('hidden');
}
function closeDocView() {
  $('docview').classList.add('hidden');
  $('docview-body').innerHTML = '';
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !$('docview').classList.contains('hidden')) closeDocView();
});

/* ---------- actions ---------- */
function selectOrder(id) { active = id; lastMsgId = 0; refreshDocs(); refreshChat(true).then(renderSide); }
function setFilter(f) { filter = f; refreshDocs(); }
let qTimer = null;
function setQ(v) { q = v; clearTimeout(qTimer); qTimer = setTimeout(refreshDocs, 300); }
function filePick(inp) {
  const f = inp.files[0];
  $('fname').textContent = f ? f.name + ' · ' + (f.size / 1048576).toFixed(1).replace('.', ',') + ' МБ' : 'Выбрать файл…';
}
async function uploadDoc() {
  const fd = new FormData();
  fd.append('order_id', active);
  fd.append('type', $('upType').value);
  fd.append('comment', $('upCmt').value.trim());
  const f = $('upFile').files[0];
  if (f) fd.append('file', f);
  try {
    await api('/api/docs', {method: 'POST', body: fd});
    await refreshDocs(); await refreshChat(true); await refreshOrders();
  } catch (e) { alert(e.message); }
}
async function refreshOrders() {
  orders = await api('/api/orders');
  renderStats(); renderSide();
}
async function approveDoc(id) { await api('/api/docs/' + id + '/approve', {method: 'POST'}).catch(e => alert(e.message)); await refreshDocs(); await refreshChat(true); await refreshOrders(); }
async function rejectDoc(id) { await api('/api/docs/' + id + '/reject', {method: 'POST'}).catch(e => alert(e.message)); await refreshDocs(); await refreshChat(true); await refreshOrders(); }
async function resendDoc(id) { await api('/api/docs/' + id + '/resend', {method: 'POST'}).catch(e => alert(e.message)); await refreshDocs(); await refreshChat(true); await refreshOrders(); }
async function doExport() {
  if (!active) return;
  try {
    await api('/api/orders/' + encodeURIComponent(active) + '/export', {method: 'POST'});
    await refreshExports(); await refreshChat(true);
  } catch (e) { alert(e.message); }
}

/* ---------- TransTrade API ---------- */
function toggleSettings() {
  settingsOpen = !settingsOpen;
  renderCenter();
}
async function loadTTSettings() {
  try {
    const s = await api('/api/settings/tt');
    $('tt-url').value = s.url || 'https://tt-ok.ru/data/api';
    $('tt-uid').value = s.api_user_id || '';
    $('tt-key').placeholder = s.has_key ? ('сохранён: ' + s.api_key_masked) : '••••••••';
  } catch (e) { /* ignore */ }
}
async function saveTTSettings() {
  const box = $('tt-status');
  try {
    const r = await api('/api/settings/tt', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        url: $('tt-url').value.trim(),
        api_key: $('tt-key').value.trim(),
        api_user_id: $('tt-uid').value.trim()
      })});
    box.innerHTML = '<div class="sett-ok">Сохранено. API ' + (r.configured ? 'настроен полностью' : 'заполнен не полностью') + '.</div>';
    $('tt-key').value = '';
    loadTTSettings();
  } catch (e) {
    box.innerHTML = '<div class="sett-err">' + esc(e.message) + '</div>';
  }
}
async function testTT() {
  const box = $('tt-status');
  box.innerHTML = '<div class="sett-hint">Проверяю соединение…</div>';
  try {
    const r = await api('/api/tt/test', {method: 'POST'});
    box.innerHTML = '<div class="sett-ok">' + esc(r.detail) + '</div>';
  } catch (e) {
    box.innerHTML = '<div class="sett-err">' + esc(e.message) + '</div>';
  }
}

/* ---------- MEGA ---------- */
async function loadMegaSettings() {
  try {
    const s = await api('/api/settings/mega');
    $('mega-email').value = s.email || '';
    $('mega-pass').placeholder = s.has_password ? 'сохранён (введите новый для замены)' : '••••••••';
  } catch (e) { /* ignore */ }
}
async function saveMega() {
  const box = $('mega-status');
  try {
    const r = await api('/api/settings/mega', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email: $('mega-email').value.trim(), password: $('mega-pass').value})});
    box.innerHTML = '<div class="sett-ok">Сохранено. MEGA ' + (r.configured ? 'настроено' : 'заполнено не полностью') + '.</div>';
    $('mega-pass').value = '';
    loadMegaSettings();
  } catch (e) {
    box.innerHTML = '<div class="sett-err">' + esc(e.message) + '</div>';
  }
}
async function testMega() {
  const box = $('mega-status');
  box.innerHTML = '<div class="sett-hint">Вхожу в MEGA…</div>';
  try {
    const r = await api('/api/mega/test', {method: 'POST'});
    box.innerHTML = '<div class="sett-ok">' + esc(r.detail || 'Вход выполнен') + '</div>';
  } catch (e) {
    box.innerHTML = '<div class="sett-err">' + esc(e.message) + '</div>';
  }
}
const megaLink = (url) => url ? ' · <a href="' + esc(url) + '" target="_blank" rel="noopener">MEGA</a>' : '';
async function pushTT() {
  if (!active) return;
  const o = orders.find(x => x.id === active);
  if (!o) return;
  if (!confirm('Отправить заказ ' + o.id + ' (заявка ' + (o.request_no || '—') + ') в TransTrade?' +
      (o.tt_order_id ? '\nЗаказ уже привязан (ID ' + o.tt_order_id + ') — будет выполнено EditOrder.' : ''))) return;
  try {
    const r = await api('/api/orders/' + encodeURIComponent(active) + '/push_tt', {method: 'POST'});
    alert(r.method === 'EditOrder' ? 'Заказ обновлён в TransTrade' : 'Заказ создан в TransTrade' +
      (r.tt_order_id ? ' (ID ' + r.tt_order_id + ')' : ''));
    await refreshOrders(); await refreshChat(true);
  } catch (e) { alert(e.message); }
}
async function sendMsg() {
  const inp = $('chatIn');
  const v = inp.value.trim();
  if (!v) return;
  inp.value = '';
  try {
    const m = await api('/api/msgs', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({order_id: active, text: v})});
    lastMsgId = Math.max(lastMsgId, m.id);
    appendMsgs([m]);
  } catch (e) { alert(e.message); }
}
async function attachDoc() {
  const list = docs.filter(d => d.order_id === active);
  if (!list.length) { alert('По этому рейсу пока нет документов'); return; }
  try {
    const m = await api('/api/msgs', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({order_id: active, text: '', doc_id: list[0].id})});
    lastMsgId = Math.max(lastMsgId, m.id);
    appendMsgs([m]);
  } catch (e) { alert(e.message); }
}

boot();
