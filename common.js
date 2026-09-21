/* DevilBook — shared client helpers.
   NOTE: All user-controlled text in feed/comments/messages is rendered with
   textContent (never innerHTML). The ONLY innerHTML sink for user data is the
   Messenger inbox preview in messages.js (intentional). */
(function () {
  'use strict';

  var ME = { id: 0, username: '', display_name: '', avatar_url: 'devil-red' };
  try {
    var meEl = document.getElementById('me-data');
    if (meEl) ME = JSON.parse(meEl.textContent);
  } catch (e) { /* ignore */ }

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function initials(name) {
    var parts = String(name || '?').trim().split(/\s+/).slice(0, 2);
    var s = parts.map(function (p) { return p.charAt(0); }).join('').toUpperCase();
    return s || '?';
  }

  // Build an avatar element safely (initials via textContent).
  function buildAvatar(user, size) {
    var span = document.createElement('span');
    span.className = 'avatar ' + (size || 'sm') + ' av-' + ((user && user.avatar_url) || 'devil-red');
    span.textContent = initials(user && (user.display_name || user.username));
    span.title = (user && (user.display_name || user.username)) || '';
    return span;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }

  function timeAgo(iso) {
    if (!iso) return '';
    var t = new Date(iso).getTime();
    if (isNaN(t)) return '';
    var s = Math.floor((Date.now() - t) / 1000);
    if (s < 5) return 'just now';
    if (s < 60) return s + 's';
    var m = Math.floor(s / 60);
    if (m < 60) return m + 'm';
    var h = Math.floor(m / 60);
    if (h < 24) return h + 'h';
    var d = Math.floor(h / 24);
    if (d < 7) return d + 'd';
    return new Date(t).toLocaleDateString();
  }

  function refreshTimes(root) {
    qa('.time[data-ts]', root).forEach(function (n) {
      var ts = n.getAttribute('data-ts');
      if (ts) n.textContent = timeAgo(ts);
    });
  }

  async function api(url, opts) {
    opts = opts || {};
    var init = { method: opts.method || 'GET', headers: {}, credentials: 'same-origin' };
    if (opts.body !== undefined) {
      init.headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(opts.body);
    }
    var res = await fetch(url, init);
    var data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    return { ok: res.ok, status: res.status, data: data };
  }

  /* ---------- Dropdowns ---------- */
  function closeAllDropdowns(except) {
    qa('.dropdown.open').forEach(function (d) { if (d !== except) d.classList.remove('open'); });
  }
  function bindDropdown(toggleId, dropdownId, onOpen) {
    var toggle = document.getElementById(toggleId);
    var dd = document.getElementById(dropdownId);
    if (!toggle || !dd) return;
    toggle.addEventListener('click', function (ev) {
      ev.stopPropagation();
      var willOpen = !dd.classList.contains('open');
      closeAllDropdowns(dd);
      dd.classList.toggle('open', willOpen);
      if (willOpen && typeof onOpen === 'function') onOpen();
    });
    dd.addEventListener('click', function (ev) { ev.stopPropagation(); });
  }
  document.addEventListener('click', function () { closeAllDropdowns(null); });

  bindDropdown('profile-toggle', 'profile-dropdown');

  /* ---------- Post card renderer (safe) ---------- */
  function buildPostCard(post) {
    var card = el('article', 'card post-card');
    card.setAttribute('data-post-id', post.id);
    card.setAttribute('data-liked', post.liked_by_me ? 1 : 0);
    card.setAttribute('data-mine', post.is_mine ? 1 : 0);

    var head = el('div', 'post-head');
    var alink = el('a');
    alink.href = '/profile/' + post.author.username;
    alink.appendChild(buildAvatar(post.author, 'md'));
    head.appendChild(alink);

    var phMain = el('div', 'ph-main');
    var author = el('div', 'post-author');
    var authorA = el('a', null, post.author.display_name);
    authorA.href = '/profile/' + post.author.username;
    author.appendChild(authorA);
    var meta = el('div', 'post-meta');
    var timeS = el('span', 'time'); timeS.setAttribute('data-ts', post.created_at); timeS.textContent = timeAgo(post.created_at);
    meta.appendChild(timeS);
    meta.appendChild(el('span', null, '·'));
    meta.appendChild(el('span', 'vis-pill', post.visibility === 'friends' ? '👥 Friends' : '🌐 Public'));
    phMain.appendChild(author); phMain.appendChild(meta);
    head.appendChild(phMain);

    if (post.can_delete) {
      var anchor = el('div', 'menu-anchor');
      var mbtn = el('button', 'post-menu-btn post-menu-toggle', '⋯');
      var menu = el('div', 'dropdown post-menu'); menu.style.width = '180px';
      if (post.is_mine) {
        var editBtn = el('button', 'menu-item post-edit'); editBtn.style.cssText = 'width:100%;border:none;background:transparent;text-align:left';
        editBtn.appendChild(el('span', 'side-ico', '✏️'));
        var em = el('div', 'mi-main'); em.appendChild(el('div', 'mi-title', 'Edit post')); editBtn.appendChild(em);
        menu.appendChild(editBtn);
      }
      var delBtn = el('button', 'menu-item post-delete'); delBtn.style.cssText = 'width:100%;border:none;background:transparent;text-align:left';
      delBtn.appendChild(el('span', 'side-ico', '🗑️'));
      var dm = el('div', 'mi-main'); dm.appendChild(el('div', 'mi-title', 'Delete post')); delBtn.appendChild(dm);
      menu.appendChild(delBtn);
      anchor.appendChild(mbtn); anchor.appendChild(menu);
      head.appendChild(anchor);
    }
    card.appendChild(head);

    if (post.content) {
      card.appendChild(el('div', 'post-content', post.content)); // textContent -> safe
    }
    if (post.image_url) {
      var imgWrap = el('div', 'post-image');
      var img = document.createElement('img');
      img.src = post.image_url; // server-generated path; set via .src (no HTML parsing)
      img.alt = ''; img.loading = 'lazy';
      imgWrap.appendChild(img);
      card.appendChild(imgWrap);
    }

    var stats = el('div', 'post-stats');
    var likesMini = el('span', 'likes-mini');
    likesMini.appendChild(el('span', 'mini-like', '👍'));
    likesMini.appendChild(document.createTextNode(' '));
    likesMini.appendChild(el('span', 'like-count', post.like_count));
    stats.appendChild(likesMini);
    stats.appendChild(el('span', 'comment-count-label', post.comment_count + ' comment' + (post.comment_count === 1 ? '' : 's')));
    card.appendChild(stats);

    var actions = el('div', 'post-actions');
    var likeBtn = el('button', 'pa-btn like-btn' + (post.liked_by_me ? ' active' : ''));
    likeBtn.appendChild(document.createTextNode('👍 '));
    likeBtn.appendChild(el('span', null, 'Like'));
    var comBtn = el('button', 'pa-btn comment-toggle');
    comBtn.appendChild(document.createTextNode('💬 '));
    comBtn.appendChild(el('span', null, 'Comment'));
    var shBtn = el('button', 'pa-btn share-btn');
    shBtn.appendChild(document.createTextNode('↪️ '));
    shBtn.appendChild(el('span', null, 'Share'));
    actions.appendChild(likeBtn); actions.appendChild(comBtn); actions.appendChild(shBtn);
    card.appendChild(actions);

    var comments = el('div', 'comments');
    var list = el('div', 'comment-list');
    (post.comments || []).forEach(function (c) { list.appendChild(buildComment(c)); });
    comments.appendChild(list);
    var form = el('form', 'comment-form');
    form.appendChild(buildAvatar(ME, 'sm'));
    var input = el('input'); input.type = 'text'; input.name = 'content'; input.placeholder = 'Write a comment...'; input.maxLength = 2000; input.autocomplete = 'off';
    form.appendChild(input);
    var pbtn = el('button', 'btn sm primary', 'Post'); pbtn.type = 'submit';
    form.appendChild(pbtn);
    comments.appendChild(form);
    card.appendChild(comments);

    return card;
  }

  function buildComment(c) {
    var wrap = el('div', 'comment');
    wrap.setAttribute('data-comment-id', c.id);
    var a = el('a'); a.href = '/profile/' + c.author.username; a.appendChild(buildAvatar(c.author, 'sm'));
    wrap.appendChild(a);
    var body = el('div', 'c-body');
    var au = el('div', 'c-author');
    var aa = el('a', null, c.author.display_name); aa.href = '/profile/' + c.author.username;
    au.appendChild(aa);
    body.appendChild(au);
    body.appendChild(el('div', 'c-text', c.content)); // textContent -> safe
    wrap.appendChild(body);
    return wrap;
  }

  /* ---------- Delegated interactions ---------- */
  document.addEventListener('click', async function (ev) {
    var t = ev.target;

    // post menu toggle
    var menuToggle = t.closest && t.closest('.post-menu-toggle');
    if (menuToggle) {
      ev.stopPropagation();
      var dd = menuToggle.parentNode.querySelector('.post-menu');
      var willOpen = !dd.classList.contains('open');
      closeAllDropdowns(dd);
      dd.classList.toggle('open', willOpen);
      return;
    }

    // like
    var likeBtn = t.closest && t.closest('.like-btn');
    if (likeBtn) {
      var card = likeBtn.closest('.post-card');
      if (!card) return;
      var pid = card.getAttribute('data-post-id');
      likeBtn.disabled = true;
      var r = await api('/posts/' + pid + '/like', { method: 'POST' });
      likeBtn.disabled = false;
      if (r.ok && r.data && r.data.ok) {
        likeBtn.classList.toggle('active', r.data.liked);
        card.setAttribute('data-liked', r.data.liked ? 1 : 0);
        var lc = card.querySelector('.like-count');
        if (lc) lc.textContent = r.data.like_count;
      }
      return;
    }

    // comment toggle -> focus input
    var ctoggle = t.closest && t.closest('.comment-toggle');
    if (ctoggle) {
      var card2 = ctoggle.closest('.post-card');
      var inp = card2 && card2.querySelector('.comment-form input');
      if (inp) inp.focus();
      return;
    }

    // share (fake)
    var share = t.closest && t.closest('.share-btn');
    if (share) {
      share.classList.add('active');
      var span = share.querySelector('span');
      if (span) { span.textContent = 'Shared'; setTimeout(function () { span.textContent = 'Share'; share.classList.remove('active'); }, 1200); }
      return;
    }

    // delete post
    var del = t.closest && t.closest('.post-delete');
    if (del) {
      var card3 = del.closest('.post-card');
      var pid3 = card3.getAttribute('data-post-id');
      if (!window.confirm('Delete this post?')) return;
      var rd = await api('/posts/' + pid3 + '/delete', { method: 'POST' });
      if (rd.ok && rd.data && rd.data.ok) { card3.parentNode.removeChild(card3); }
      return;
    }

    // edit post
    var edit = t.closest && t.closest('.post-edit');
    if (edit) {
      var card4 = edit.closest('.post-card');
      closeAllDropdowns(null);
      startInlineEdit(card4);
      return;
    }

    // friend actions
    var fa = t.closest && t.closest('[data-action]');
    if (fa) {
      var action = fa.getAttribute('data-action');
      if (action && action.indexOf('friend-') === 0) {
        await handleFriendAction(action, fa);
        return;
      }
    }
  });

  // comment submit (delegated)
  document.addEventListener('submit', async function (ev) {
    var form = ev.target;
    if (!form.classList || !form.classList.contains('comment-form')) return;
    ev.preventDefault();
    var card = form.closest('.post-card');
    if (!card) return;
    var pid = card.getAttribute('data-post-id');
    var input = form.querySelector('input');
    var text = (input.value || '').trim();
    if (!text) return;
    input.disabled = true;
    var r = await api('/posts/' + pid + '/comment', { method: 'POST', body: { content: text } });
    input.disabled = false;
    if (r.ok && r.data && r.data.ok) {
      var list = card.querySelector('.comment-list');
      list.appendChild(buildComment(r.data.comment));
      input.value = '';
      var lbl = card.querySelector('.comment-count-label');
      if (lbl) lbl.textContent = r.data.comment_count + ' comment' + (r.data.comment_count === 1 ? '' : 's');
      input.focus();
    }
  });

  function startInlineEdit(card) {
    if (card.querySelector('.edit-area')) return;
    var contentEl = card.querySelector('.post-content');
    if (!contentEl) {
      // image-only post: create an editable content slot
      contentEl = el('div', 'post-content', '');
      var headEl = card.querySelector('.post-head');
      if (headEl && headEl.nextSibling) card.insertBefore(contentEl, headEl.nextSibling);
      else card.appendChild(contentEl);
    }
    var pid = card.getAttribute('data-post-id');
    var original = contentEl.textContent;
    var ta = el('textarea', 'edit-area');
    ta.value = original;
    ta.style.cssText = 'width:100%;min-height:70px;border:1px solid var(--line);border-radius:8px;padding:10px;font-size:15px';
    var bar = el('div'); bar.style.cssText = 'display:flex;gap:8px;margin-top:8px';
    var save = el('button', 'btn sm primary', 'Save');
    var cancel = el('button', 'btn sm', 'Cancel');
    bar.appendChild(save); bar.appendChild(cancel);
    contentEl.style.display = 'none';
    contentEl.parentNode.insertBefore(ta, contentEl.nextSibling);
    ta.parentNode.insertBefore(bar, ta.nextSibling);
    ta.focus();
    cancel.addEventListener('click', function () { ta.remove(); bar.remove(); contentEl.style.display = ''; });
    save.addEventListener('click', async function () {
      var val = (ta.value || '').trim();
      if (!val) return;
      save.disabled = true;
      var r = await api('/posts/' + pid + '/edit', { method: 'POST', body: { content: val } });
      save.disabled = false;
      if (r.ok && r.data && r.data.ok) {
        contentEl.textContent = r.data.post.content; // safe
        ta.remove(); bar.remove(); contentEl.style.display = '';
      }
    });
  }

  async function handleFriendAction(action, btn) {
    btn.disabled = true;
    var url = null, method = 'POST';
    var userId = btn.getAttribute('data-user-id');
    var reqId = btn.getAttribute('data-request-id');
    if (action === 'friend-request') url = '/friends/request/' + userId;
    else if (action === 'friend-accept') url = '/friends/accept/' + reqId;
    else if (action === 'friend-reject') url = '/friends/reject/' + reqId;
    else if (action === 'friend-remove') url = '/friends/remove/' + userId;
    if (!url) { btn.disabled = false; return; }

    var r = await api(url, { method: method });
    btn.disabled = false;
    if (!(r.ok && r.data && r.data.ok)) {
      // soft-fail; keep UI intact
      return;
    }

    // Friends list page: remove request row / person card
    var reqRow = btn.closest('[data-request-row]');
    var personCard = btn.closest('[data-person-card]');
    if (action === 'friend-accept' && reqRow) { reqRow.remove(); decrementCount('#req-count'); toggleRequestsCard(); return; }
    if (action === 'friend-reject' && reqRow) { reqRow.remove(); decrementCount('#req-count'); toggleRequestsCard(); return; }
    if (action === 'friend-remove' && personCard) { personCard.remove(); decrementCount('#friend-count'); return; }

    // Profile page: swap the actions area
    var actionsWrap = document.getElementById('profile-actions');
    if (actionsWrap && btn.closest('#profile-actions')) {
      updateProfileActions(actionsWrap, action);
    }
  }

  function updateProfileActions(wrap, action) {
    var username = null;
    var msgLink = wrap.querySelector('a[href^="/messages/"]');
    if (msgLink) username = msgLink.getAttribute('href').split('/messages/')[1];
    var uid = wrap.getAttribute('data-user-id');
    var first = null;
    if (action === 'friend-request') {
      first = el('button', 'btn', '⏳ Request sent'); first.disabled = true;
    } else if (action === 'friend-accept') {
      first = el('button', 'btn', '✔️ Friends');
      first.setAttribute('data-action', 'friend-remove'); first.setAttribute('data-user-id', uid);
    } else if (action === 'friend-reject') {
      first = el('button', 'btn primary', '➕ Add friend');
      first.setAttribute('data-action', 'friend-request'); first.setAttribute('data-user-id', uid);
    } else if (action === 'friend-remove') {
      first = el('button', 'btn primary', '➕ Add friend');
      first.setAttribute('data-action', 'friend-request'); first.setAttribute('data-user-id', uid);
    }
    wrap.innerHTML = '';
    if (first) wrap.appendChild(first);
    if (username) {
      var m = el('a', 'btn primary', '💬 Message'); m.href = '/messages/' + username;
      wrap.appendChild(m);
    }
  }

  function decrementCount(sel) {
    var n = q(sel);
    if (!n) return;
    var m = /\((\d+)\)/.exec(n.textContent);
    var val = m ? Math.max(0, parseInt(m[1], 10) - 1) : 0;
    n.textContent = '(' + val + ')';
  }
  function toggleRequestsCard() {
    var rows = qa('#friend-requests [data-request-row]');
    var card = q('#requests-card');
    if (card && rows.length === 0) card.style.display = 'none';
  }

  // composer submit (feed page) handled in feed.js; expose helpers
  window.DB = {
    ME: ME,
    q: q, qa: qa, el: el, api: api,
    buildAvatar: buildAvatar, buildPostCard: buildPostCard, buildComment: buildComment,
    timeAgo: timeAgo, refreshTimes: refreshTimes, initials: initials,
    closeAllDropdowns: closeAllDropdowns
  };

  // initial + periodic time refresh
  refreshTimes(document);
  setInterval(function () { refreshTimes(document); }, 30000);
})();
