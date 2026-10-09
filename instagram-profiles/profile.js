/* 문영스냅 프로필 페이지 공용 동작.
   <body data-account="e_euno_official"> 처럼 계정을 정하면 그 계정의 프로필을 그린다.
   데이터·그림은 snap-shared.js(문영스냅에서 옮겨 온 것)에서 온다. */
(function () {
  'use strict';
  var D = window.SNAP_DATA, A = window.SNAP_ART, ART = A.ART, IMG = A.IMG;
  var ME = document.body.dataset.account;
  var PAGE = { e_euno_official: 'lee-eunho.html', seojin_official: 'kim-seojin.html' };

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* 이 브라우저에만 남는 편의 설정. 막혀 있어도 화면은 그대로 동작한다 */
  var NS = 'munyoung-profile:';
  function load(k, f) { try { var v = localStorage.getItem(NS + k); return v == null ? f : JSON.parse(v); } catch (e) { return f; } }
  function save(k, v) { try { localStorage.setItem(NS + k, JSON.stringify(v)); } catch (e) {} }

  /* ---------- 시간 ---------- */
  function toTs(s) { var m = String(s || '').match(/(\d{4})\D(\d{1,2})\D(\d{1,2})(?:\D+(\d{1,2}):(\d{2}))?/); return m ? new Date(+m[1], m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0)).getTime() : 0; }
  var TURNS = D.turns.map(function (t) { return { name: t.name, time: t.time, desc: t.desc, ts: toTs(t.time) }; });
  var state = { turn: Math.min(TURNS.length - 1, Math.max(0, load('turn', 0) | 0)), tab: 'posts', dated: !!load('dated', false), teacher: !!load('teacher', false) };
  function now() { return TURNS[state.turn].ts; }
  var WD = '일월화수목금토';
  function absDate(ts) {
    var d = new Date(ts), h = d.getHours();
    return d.getFullYear() + '년 ' + (d.getMonth() + 1) + '월 ' + d.getDate() + '일 (' + WD[d.getDay()] + ') ' + (h < 12 ? '오전 ' : '오후 ') + ((h % 12) || 12) + ':' + ('0' + d.getMinutes()).slice(-2);
  }
  function shortDate(ts) { var d = new Date(ts); return d.getFullYear() + '.' + ('0' + (d.getMonth() + 1)).slice(-2) + '.' + ('0' + d.getDate()).slice(-2) + ' ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  function ledDate(ts) { var d = new Date(ts); return d.getFullYear() + ' ' + (d.getMonth() + 1) + ' ' + d.getDate(); }
  function fmtN(n) { n = Math.max(0, Math.round(n)); if (n >= 10000) return (Math.round(n / 1000) / 10).toString().replace(/\.0$/, '') + '만'; return n.toLocaleString('ko-KR'); }

  /* ---------- 게시물 ---------- */
  var POSTS = D.posts.map(function (p) { p.ts = toTs(p.t); return p; });
  var BY_ID = {}; POSTS.forEach(function (p) { BY_ID[p.id] = p; });
  function visiblePosts() { return POSTS.filter(function (p) { return p.ts <= now(); }).sort(function (a, b) { return b.ts - a.ts; }); }
  /* 좋아요: 시점별 값이 있으면 그 값, 없으면 올린 뒤 사흘에 걸쳐 최종값까지 오른다(문영스냅과 같은 규칙) */
  function grow(n, ts) { var h = (now() - ts) / 3600e3; if (h <= 0) return 0; if (h >= 72) return n; return n * (1 - Math.exp(-h / 9)); }
  function stepVal(arr) { var v = 0; arr.forEach(function (s) { if (toTs(s[0]) <= now()) v = s[1]; }); return v; }
  var liked = {};
  function likeCount(p) { return Math.round(Array.isArray(p.likes) ? stepVal(p.likes) : grow(p.likes || 0, p.ts)) + (liked[p.id] ? 1 : 0); }
  function comments(p) {
    return (p.comments || []).map(function (c) {
      return { by: c[0], ts: toTs(c[1]), text: c[2], likes: c[3] || 0,
        replies: (c[4] || []).map(function (r) { return { by: r[0], ts: toTs(r[1]), text: r[2], likes: r[3] || 0 }; }).filter(function (r) { return r.ts <= now(); }) };
    }).filter(function (c) { return c.ts <= now(); }).sort(function (a, b) { return a.ts - b.ts; });
  }
  function commentCount(p) { var n = comments(p).reduce(function (s, c) { return s + 1 + c.replies.length; }, 0); return Math.max(n, Math.round(grow(p.cmt || 0, p.ts))); }
  /* 캡션 수정 이력: 지금 시점까지 일어난 수정만 */
  function captionNow(p) {
    var hist = [{ ts: p.ts, text: p.cap || '' }];
    (p.edits || []).forEach(function (e) { var ts = toTs(e[0]); if (ts <= now()) hist.push({ ts: ts, text: e[1] }); });
    return { text: hist[hist.length - 1].text, hist: hist };
  }

  /* ---------- 그림 ---------- */
  var IC = {
    heart: '<path d="M12 20.5s-7.5-4.6-7.5-10.3A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.6c0 5.7-7.5 10.3-7.5 10.3z"/>',
    comment: '<path d="M20.5 11.5a8.5 8.5 0 0 1-12.6 7.4L3.5 20.5l1.6-4.3A8.5 8.5 0 1 1 20.5 11.5z"/>',
    share: '<path d="M21 3 10 14M21 3l-7 18-4-7-7-4z"/>',
    save: '<path d="M19 21l-7-5-7 5V4.5A1.5 1.5 0 0 1 6.5 3h11A1.5 1.5 0 0 1 19 4.5z"/>',
    grid: '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/>',
    tag: '<path d="M20 20c-1.3-3.4-4.5-5.5-8-5.5S5.3 16.6 4 20"/><circle cx="12" cy="8.5" r="3.8"/><rect x="2.5" y="2.5" width="19" height="19" rx="3"/>',
    multi: '<rect x="7" y="3" width="14" height="14" rx="2"/><path d="M17 21H5a2 2 0 0 1-2-2V7"/>',
    play: '<path d="M7 4.5v15l12-7.5z"/>',
    pin: '<path d="M9 3h6l-1 6 4 4H6l4-4z"/><path d="M12 13v8"/>',
    link: '<path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/>',
    left: '<path d="M15 5l-7 7 7 7"/>', right: '<path d="M9 5l7 7-7 7"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>', more: '<circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/>'
  };
  function ic(n, cls) { return '<svg class="i ' + (cls || '') + '" viewBox="0 0 24 24" aria-hidden="true">' + IC[n] + '</svg>'; }
  var VF = '<svg class="vf" viewBox="0 0 24 24" role="img" aria-label="인증된 계정"><path fill="currentColor" d="M12 1.6l2.6 2 3.3-.3.9 3.2 2.9 1.6-1 3.2 1 3.2-2.9 1.6-.9 3.2-3.3-.3L12 22.4l-2.6-2-3.3.3-.9-3.2-2.9-1.6 1-3.2-1-3.2 2.9-1.6.9-3.2 3.3.3z"/><path d="M7.6 12.2l3 3 5.8-6" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#ffc21a"/><stop offset=".55" stop-color="#ff5a1f"/><stop offset="1" stop-color="#e3326c"/></linearGradient></defs><rect x="2" y="2" width="28" height="28" rx="8.5" fill="url(#lg)"/><circle cx="16" cy="16.5" r="7.2" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M16 9.3v4.4M22.2 13l-3.8 2.2M22.2 20l-3.8-2.2M16 23.7v-4.4M9.8 20l3.8-2.2M9.8 13l3.8 2.2" stroke="#fff" stroke-width="1.6"/><circle cx="24.2" cy="7.8" r="1.6" fill="#fff"/></svg>';

  function artOf(m) {
    if (m.img && IMG[m.img]) return '<img src="' + IMG[m.img] + '" alt="">';
    if (m.art && ART[m.art]) return ART[m.art](m);
    return '';
  }
  function avHTML(h, cls) {
    var a = D.accounts[h], inner = '';
    /* 프로필 사진 칸은 작아서 표지 그림 속 글자는 빼고 쓴다 */
    if (a) inner = a.av.img && IMG[a.av.img] ? '<img src="' + IMG[a.av.img] + '" alt="">' : ART[a.av.art] ? ART[a.av.art]({}).replace(/<text[\s\S]*?<\/text>/g, '') : '';
    else { var pal = ['#e8a04a', '#4d8a8a', '#c9553d', '#5b6fb5', '#7a9a52', '#a2569b', '#3f7fbf', '#b5835b'], n = 0; for (var i = 0; i < h.length; i++) n = (n * 31 + h.charCodeAt(i)) | 0;
      return '<span class="av ' + (cls || '') + '" style="background:' + pal[Math.abs(n) % pal.length] + ';color:#fff;font-weight:900;font-size:12px" aria-hidden="true">' + esc(h.replace(/[^a-z0-9]/gi, '').charAt(0).toUpperCase()) + '</span>'; }
    return '<span class="av ' + (cls || '') + '" aria-hidden="true">' + inner + '</span>';
  }
  function slideHTML(m) {
    var body;
    if (m.letter) body = '<div class="k k-letter"><div class="k-body">' + esc(m.letter) + '</div><div class="k-sign">' + esc(m.sign || '') + '</div></div>';
    else body = artOf(m);
    if (m.video) body += '<span class="vbadge">' + ic('play', 'fill') + esc(m.video) + '</span>';
    return '<div class="slide" role="img" aria-label="' + esc(m.alt || '게시물 이미지') + '">' + body + '</div>';
  }
  /* 글 안의 @계정: 두 공식 계정이면 그 프로필로 간다 */
  function rich(s) {
    return esc(s).replace(/@([a-z0-9._]*[a-z0-9_])/gi, function (all, h) {
      return PAGE[h] ? '<a class="mention" href="' + PAGE[h] + '">@' + h + '</a>' : '<span class="mention">@' + h + '</span>';
    }).replace(/\n/g, '<br>');
  }
  function uname(h) { return '<b>' + esc(h) + '</b>' + (D.accounts[h] && D.accounts[h].verified ? VF : ''); }
  function ulink(h) { return PAGE[h] && h !== ME ? '<a href="' + PAGE[h] + '">' + uname(h) + '</a>' : uname(h); }

  /* ---------- 스토리 ---------- */
  var LIFE = (D.storyHours || 24) * 3600e3;
  function activeStory(h) { var t = now(); return D.stories.filter(function (s) { var ts = toTs(s.t); return s.by === h && ts <= t && t < ts + LIFE; })[0]; }

  /* ---------- 그리기 ---------- */
  var acct = D.accounts[ME];
  var OTHER = ME === 'e_euno_official' ? 'seojin_official' : 'e_euno_official';
  var followed = false;

  function render() {
    var t = TURNS[state.turn];
    $('#when').innerHTML = '<div class="when-in"><span class="when-k">현재 시점</span><span class="when-t">' + esc(t.name) + ' · ' + absDate(t.ts) + '</span><span class="when-d">' + esc(t.desc) + '</span>' +
      '<div class="seg" role="group" aria-label="시점 고르기">' + TURNS.map(function (x, i) { return '<button data-turn="' + i + '" aria-pressed="' + (i === state.turn) + '">' + esc(x.name) + '</button>'; }).join('') + '</div></div>';

    var mine = visiblePosts().filter(function (p) { return p.by === ME; });
    var pinned = mine.filter(function (p) { return p.pin; }).concat(mine.filter(function (p) { return !p.pin; }));
    var story = activeStory(ME);
    var av = story ? '<button class="ring" data-story aria-label="스토리 보기">' + avHTML(ME) + '</button>' : avHTML(ME);
    $('#prof').innerHTML =
      '<div class="prof-av">' + av + '</div>' +
      '<div class="prof-info"><div class="prof-top"><h1>' + esc(ME) + (acct.verified ? VF : '') + '</h1>' +
        '<button class="btn ' + (followed ? '' : 'pri') + '" id="follow" aria-pressed="' + followed + '">' + (followed ? '팔로잉' : '팔로우') + '</button>' +
        '<button class="btn" data-msg>메시지 보내기</button></div>' +
        '<ul class="cnt"><li>게시물 <b>' + (mine.length + (acct.olderPosts || 0)).toLocaleString('ko-KR') + '</b></li><li>팔로워 <b>' + esc(acct.followers) + '</b></li><li>팔로우 <b>' + esc(acct.following) + '</b></li></ul></div>' +
      '<div class="bio"><div class="nm">' + esc(acct.name) + '</div><div class="cat">' + esc(acct.category) + '</div>' + acct.bio.map(rich).join('<br>') +
        (acct.link ? '<div><span class="lk">' + ic('link') + esc(acct.link) + '</span></div>' : '') +
        (state.teacher && acct.note ? '<div class="note">교사 메모 · ' + esc(acct.note) + '</div>' : '') + '</div>';

    $('#hls').innerHTML = (acct.highlights || []).map(function (x, i) {
      return '<li class="hl"><button data-hl="' + i + '" aria-label="하이라이트 ' + esc(x.title) + ' 보기"><span class="av" aria-hidden="true">' + artOf(x.frames[0] || {}) + '</span><span>' + esc(x.title) + '</span></button></li>';
    }).join('');

    $$('.tab').forEach(function (b) { b.setAttribute('aria-selected', b.dataset.tab === state.tab); });
    $('#datesw').setAttribute('aria-pressed', state.dated);

    var list = state.tab === 'tagged' ? visiblePosts().filter(function (p) { return (p.tags || []).indexOf(ME) > -1; }) : pinned;
    var grid = $('#grid');
    grid.classList.toggle('dated', state.dated);
    if (!list.length) {
      grid.innerHTML = state.tab === 'tagged' ? '<div class="empty"><b>사진 없음</b>' + esc(acct.name) + ' 님이 태그된 사진이 아직 없어요.</div>' : '<div class="empty"><b>게시물 없음</b>이 시점까지 올린 게시물이 없어요.</div>';
    } else {
      grid.innerHTML = list.map(function (p, i) {
        var n = p.media.length, m0 = p.media[0] || {};
        var icon = p.pin && state.tab !== 'tagged' ? ic('pin', 'fill') : n > 1 ? ic('multi') : m0.video ? ic('play', 'fill') : '';
        return '<button class="gi" data-open="' + esc(p.id) + '" aria-label="' + esc(absDate(p.ts)) + ' 게시물 열기">' + slideHTML(m0) +
          (icon ? '<span class="ic">' + icon + '</span>' : '') +
          '<span class="led" style="--n:' + i + '" aria-hidden="true">' + ledDate(p.ts) + '</span>' +
          '<span class="hov" aria-hidden="true"><span>' + ic('heart', 'fill') + fmtN(likeCount(p)) + '</span><span>' + ic('comment', 'fill') + fmtN(commentCount(p)) + '</span></span></button>';
      }).join('');
    }
    var older = $('#older');
    older.hidden = state.tab === 'tagged' || !acct.olderPosts;
    older.textContent = '이전 게시물 ' + (acct.olderPosts || 0).toLocaleString('ko-KR') + '개는 이 화면에서 볼 수 없어요.';
    $('#teacher').setAttribute('aria-pressed', state.teacher);
  }

  /* ---------- 게시물 창 ---------- */
  var dlg = $('#post'), cur = null;
  function cmHTML(c) {
    return '<div class="cm">' + avHTML(c.by) + '<div class="body">' + ulink(c.by) + rich(c.text) +
      '<div class="meta"><time>' + shortDate(c.ts) + '</time>' + (c.likes ? '<span>좋아요 ' + c.likes.toLocaleString('ko-KR') + '개</span>' : '') + '</div></div></div>';
  }
  function openPost(id) {
    var p = BY_ID[id]; if (!p) return; cur = p;
    var n = p.media.length, cap = captionNow(p);
    var capHTML = cap.text || cap.hist.length > 1 ? '<div class="cm">' + avHTML(p.by) + '<div class="body">' + uname(p.by) + rich(cap.text) +
      '<div class="meta"><time>' + shortDate(p.ts) + '</time>' + (cap.hist.length > 1 ? '<button class="edited" data-hist aria-expanded="false">수정됨 · 이력 ' + cap.hist.length + '개</button>' : '') + '</div>' +
      (cap.hist.length > 1 ? '<ol class="hist" hidden>' + cap.hist.map(function (h) { return '<li><time>' + shortDate(h.ts) + '</time>' + esc(h.text) + '</li>'; }).join('') + '</ol>' : '') +
      (state.teacher && p.data ? '<span class="datab">' + esc(p.data) + '</span>' : '') + '</div></div>' : '';
    var cms = comments(p).map(function (c) { return cmHTML(c) + (c.replies.length ? '<div class="reps">' + c.replies.map(cmHTML).join('') + '</div>' : ''); }).join('');
    dlg.innerHTML = '<div class="pm" role="document">' +
      '<div class="pm-media"><div class="car" data-i="0" data-n="' + n + '"><div class="track">' + p.media.map(slideHTML).join('') + '</div>' +
        (n > 1 ? '<button class="c-nav p" data-car="-1" aria-label="이전 사진" hidden>' + ic('left') + '</button><button class="c-nav n" data-car="1" aria-label="다음 사진">' + ic('right') + '</button><div class="c-dots">' + p.media.map(function (x, i) { return '<i class="' + (i ? '' : 'on') + '"></i>'; }).join('') + '</div>' : '') + '</div></div>' +
      '<div class="pm-side"><div class="pm-head">' + avHTML(p.by) + '<div class="who">' + uname(p.by) + (p.ad ? '<small>유료 광고</small>' : '') + '</div><button class="x" data-close aria-label="닫기">' + ic('x') + '</button></div>' +
        '<div class="pm-list">' + capHTML + (cms || (capHTML ? '' : '<p class="muted">아직 댓글이 없어요.</p>')) + '</div>' +
        '<div class="pm-foot"><div class="acts"><button data-like aria-pressed="' + !!liked[p.id] + '" aria-label="좋아요" class="' + (liked[p.id] ? 'liked' : '') + '">' + ic('heart') + '</button>' + ic('comment') + ic('share') + '<span class="sp"></span>' + ic('save') + '</div>' +
        '<div class="likes" id="likes">좋아요 ' + likeCount(p).toLocaleString('ko-KR') + '개</div>' +
        '<span class="stamp-abs">올린 시각 <b>' + absDate(p.ts) + '</b></span></div></div></div>';
    dlg.setAttribute('aria-label', p.by + ' 게시물, ' + absDate(p.ts));
    if (!dlg.open) dlg.showModal();
  }
  function carGo(car, d) {
    var n = +car.dataset.n, i = Math.max(0, Math.min(n - 1, +car.dataset.i + d)); car.dataset.i = i;
    $('.track', car).style.transform = 'translateX(' + (-100 * i) + '%)';
    $('.c-nav.p', car).hidden = i === 0; $('.c-nav.n', car).hidden = i === n - 1;
    $$('.c-dots i', car).forEach(function (x, k) { x.classList.toggle('on', k === i); });
  }

  /* ---------- 스토리·하이라이트 창 ---------- */
  var sv = { frames: [], i: 0, head: '' };
  function openFrames(frames, head) { sv = { frames: frames, i: 0, head: head }; drawFrame(); if (!dlg.open) dlg.showModal(); }
  function drawFrame() {
    var f = sv.frames[sv.i];
    var art = artOf(f);
    dlg.setAttribute('aria-label', '스토리 ' + (sv.i + 1) + '/' + sv.frames.length);
    dlg.innerHTML = '<div class="sv"><div class="slide">' + art + '</div>' +
      (f.text ? '<div class="sv-txt"><span>' + esc(f.text) + '</span></div>' : '') +
      '<div class="sv-bars">' + sv.frames.map(function (x, k) { return '<i class="' + (k <= sv.i ? 'on' : '') + '"></i>'; }).join('') + '</div>' +
      '<div class="sv-head">' + avHTML(ME) + '<b>' + esc(ME) + '</b><small>' + sv.head + '</small><span class="sp"></span><button class="x" data-close aria-label="닫기">' + ic('x') + '</button></div>' +
      '<button class="sv-zone l" data-frame="-1" aria-label="이전 장면"></button><button class="sv-zone r" data-frame="1" aria-label="다음 장면"></button></div>';
  }

  /* ---------- 이벤트 ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.dataset.turn != null) { state.turn = +b.dataset.turn; save('turn', state.turn); render(); }
    else if (b.dataset.tab) { state.tab = b.dataset.tab; render(); }
    else if (b.id === 'datesw') { state.dated = !state.dated; save('dated', state.dated); $('#grid').classList.toggle('dated', state.dated); b.setAttribute('aria-pressed', state.dated); }
    else if (b.id === 'teacher') { state.teacher = !state.teacher; save('teacher', state.teacher); render(); }
    else if (b.id === 'follow') { followed = !followed; render(); }
    else if (b.dataset.open) openPost(b.dataset.open);
    else if (b.hasAttribute('data-story')) { var st = activeStory(ME); if (st) openFrames(st.frames, absDate(toTs(st.t))); }
    else if (b.dataset.hl != null) { var h = acct.highlights[+b.dataset.hl]; openFrames(h.frames, esc(h.title)); }
    else if (b.dataset.frame) { var j = sv.i + (+b.dataset.frame); if (j < 0 || j >= sv.frames.length) dlg.close(); else { sv.i = j; drawFrame(); } }
    else if (b.dataset.car) carGo(b.closest('.car'), +b.dataset.car);
    else if (b.hasAttribute('data-close')) dlg.close();
    else if (b.hasAttribute('data-hist')) { var ol = b.closest('.body').querySelector('.hist'); ol.hidden = !ol.hidden; b.setAttribute('aria-expanded', !ol.hidden); }
    else if (b.hasAttribute('data-like') && cur) { liked[cur.id] = !liked[cur.id]; b.classList.toggle('liked', liked[cur.id]); b.setAttribute('aria-pressed', liked[cur.id]); $('#likes').textContent = '좋아요 ' + likeCount(cur).toLocaleString('ko-KR') + '개'; render(); }
  });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { cur = null; dlg.innerHTML = ''; });
  document.addEventListener('keydown', function (e) {
    if (!dlg.open) return;
    var car = $('.car', dlg);
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      var d = e.key === 'ArrowRight' ? 1 : -1;
      if (car && +car.dataset.n > 1) carGo(car, d);
      else if ($('.sv', dlg)) { var j = sv.i + d; if (j >= 0 && j < sv.frames.length) { sv.i = j; drawFrame(); } }
    }
  });

  $('#logo').innerHTML = LOGO + '<span>문영스냅</span>';
  $('#other').innerHTML = avHTML(OTHER) + '<span>' + esc(OTHER) + '</span>';
  $('#other').href = PAGE[OTHER];
  render();
})();
