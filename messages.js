/* Messenger: AJAX polling, optimistic send, in-place inbox updates.
   Chat bubbles: textContent (safe). Inbox preview: innerHTML (intentional sink). */
(function () {
  'use strict';
  var DB = window.DB;
  if (!DB) return;

  var inboxList = document.getElementById('inbox-list');
  var chatPanel = document.getElementById('chat-panel');
  var inboxSearch = document.getElementById('inbox-search');

  var activeUsername = chatPanel ? (chatPanel.getAttribute('data-active-username') || '') : '';
  var activeConvId = chatPanel ? parseInt(chatPanel.getAttribute('data-conv-id') || '0', 10) : 0;
  var lastMessageId = 0;
  var renderedIds = {};

  function initFromServerRender() {
    var rows = DB.qa('.bubble-row[data-msg-id]', document.getElementById('chat-body') || document);
    rows.forEach(function (r) {
      var id = parseInt(r.getAttribute('data-msg-id'), 10) || 0;
      if (id) { renderedIds[id] = true; lastMessageId = Math.max(lastMessageId, id); }
    });
    var body = document.getElementById('chat-body');
    if (body) body.scrollTop = body.scrollHeight;
  }

  /* ---------- Inbox rendering (in-place, no full wipe) ---------- */
  function buildConvRow(conv) {
    var a = DB.el('a', 'conv');
    a.href = '/messages/' + conv.other.username;
    a.setAttribute('data-conv-id', conv.conversation_id);
    a.setAttribute('data-username', conv.other.username);
    a.setAttribute('data-last-id', conv.last_message_id);

    var wrap = DB.el('span', 'avatar-wrap');
    wrap.appendChild(DB.buildAvatar(conv.other, 'md'));
    wrap.appendChild(DB.el('span', 'dot online'));
    a.appendChild(wrap);

    var main = DB.el('div', 'conv-main');
    main.appendChild(DB.el('div', 'conv-name', conv.other.display_name));
    var preview = DB.el('div', 'conv-preview');
    main.appendChild(preview);
    a.appendChild(main);

    var side = DB.el('div');
    side.style.cssText = 'display:flex;flex-direction:column;align-items:flex-end;gap:4px';
    var time = DB.el('span', 'conv-time time');
    time.setAttribute('data-ts', conv.last_at || '');
    side.appendChild(time);
    side.appendChild(DB.el('span', 'conv-badge'));
    a.appendChild(side);

    updateConvRow(a, conv);
    return a;
  }

  function updateConvRow(row, conv) {
    row.setAttribute('data-last-id', conv.last_message_id);
    var name = row.querySelector('.conv-name');
    if (name) name.textContent = conv.other.display_name;

    // === Inbox preview: intentional innerHTML sink (renders last message as HTML) ===
    var preview = row.querySelector('.conv-preview');
    if (preview) {
      preview.innerHTML = (conv.last_from_me ? 'You: ' : '') + (conv.last_message || '');
    }

    var time = row.querySelector('.conv-time');
    if (time) { time.setAttribute('data-ts', conv.last_at || ''); time.textContent = DB.timeAgo(conv.last_at); }

    var badge = row.querySelector('.conv-badge');
    if (badge) {
      if (conv.unread > 0) { badge.textContent = conv.unread; badge.style.display = ''; }
      else { badge.textContent = ''; badge.style.display = 'none'; }
    }
    row.classList.toggle('unread', conv.unread > 0);
    row.classList.toggle('active', conv.other.username === activeUsername);
  }

  function renderInbox(convs) {
    if (!inboxList) return;
    var existing = {};
    DB.qa('.conv[data-conv-id]', inboxList).forEach(function (r) {
      existing[r.getAttribute('data-conv-id')] = r;
    });
    var seen = {};
    var ordered = [];
    convs.forEach(function (conv) {
      var key = String(conv.conversation_id);
      seen[key] = true;
      var row = existing[key];
      if (row) { updateConvRow(row, conv); }
      else { row = buildConvRow(conv); }
      ordered.push(row);
    });
    // Remove rows no longer present
    Object.keys(existing).forEach(function (k) {
      if (!seen[k]) existing[k].remove();
    });
    // Remove the "empty" placeholder if we now have conversations
    var emptyEl = inboxList.querySelector('.dropdown-empty');
    if (emptyEl && ordered.length) emptyEl.remove();
    // Reorder (appendChild moves existing nodes without destroying them)
    ordered.forEach(function (row) { inboxList.appendChild(row); });
    applySearchFilter();
  }

  async function loadConversations() {
    try {
      var r = await DB.api('/api/messages/conversations');
      if (r.ok && r.data && r.data.ok) renderInbox(r.data.conversations);
    } catch (e) { /* ignore polling errors */ }
  }

  /* ---------- Chat rendering (safe) ---------- */
  function buildBubble(m) {
    var row = DB.el('div', 'bubble-row' + (m.from_me ? ' me' : ''));
    row.setAttribute('data-msg-id', m.id || '');
    if (m.from_me) {
      var del = DB.el('button', 'bubble-del', '✕');
      del.type = 'button'; del.title = 'Remove message';
      row.appendChild(del);
    } else {
      row.appendChild(DB.buildAvatar(m.sender, 'sm'));
    }
    row.appendChild(DB.el('div', 'bubble', m.content)); // textContent -> safe
    return row;
  }

  function nearBottom(body) {
    return body.scrollHeight - body.scrollTop - body.clientHeight < 80;
  }

  function renderChat(data) {
    activeUsername = data.other.username;
    activeConvId = data.conversation_id || 0;
    lastMessageId = 0;
    renderedIds = {};

    chatPanel.innerHTML = '';
    chatPanel.setAttribute('data-active-username', activeUsername);
    chatPanel.setAttribute('data-conv-id', activeConvId || '');

    var head = DB.el('div', 'chat-head');
    head.id = 'chat-head';
    var alink = DB.el('a'); alink.href = '/profile/' + data.other.username;
    alink.appendChild(DB.buildAvatar(data.other, 'md'));
    head.appendChild(alink);
    var hb = DB.el('div');
    hb.appendChild(DB.el('div', 'ch-name', data.other.display_name));
    hb.appendChild(DB.el('div', 'ch-sub', '● Active now'));
    head.appendChild(hb);
    chatPanel.appendChild(head);

    var body = DB.el('div', 'chat-body'); body.id = 'chat-body';
    (data.messages || []).forEach(function (m) {
      body.appendChild(buildBubble(m));
      if (m.id) { renderedIds[m.id] = true; lastMessageId = Math.max(lastMessageId, m.id); }
    });
    chatPanel.appendChild(body);

    var form = DB.el('form', 'chat-form'); form.id = 'chat-form';
    var input = DB.el('input'); input.id = 'chat-input'; input.type = 'text'; input.placeholder = 'Aa'; input.autocomplete = 'off'; input.maxLength = 2000;
    var btn = DB.el('button', 'btn primary', 'Send'); btn.type = 'submit';
    form.appendChild(input); form.appendChild(btn);
    chatPanel.appendChild(form);

    body.scrollTop = body.scrollHeight;
    input.focus();
    bindChatForm();
  }

  async function loadConversation(username, push) {
    try {
      var r = await DB.api('/api/messages/conversation/' + encodeURIComponent(username));
      if (r.ok && r.data && r.data.ok) {
        renderChat(r.data);
        if (push) history.pushState({ username: username }, '', '/messages/' + username);
        // clear unread on the clicked row immediately
        var row = inboxList && inboxList.querySelector('.conv[data-username="' + cssEscape(username) + '"]');
        if (row) {
          row.classList.remove('unread');
          var b = row.querySelector('.conv-badge'); if (b) { b.textContent = ''; b.style.display = 'none'; }
          DB.qa('.conv', inboxList).forEach(function (c) { c.classList.remove('active'); });
          row.classList.add('active');
        }
      }
    } catch (e) { /* ignore */ }
  }

  function cssEscape(s) { return String(s).replace(/"/g, '\\"'); }

  /* ---------- Sending (optimistic) ---------- */
  function bindChatForm() {
    var form = document.getElementById('chat-form');
    if (!form) return;
    form.addEventListener('submit', async function (ev) {
      ev.preventDefault();
      var input = document.getElementById('chat-input');
      var body = document.getElementById('chat-body');
      var text = (input.value || '').trim();
      if (!text || !activeUsername) return;

      // optimistic bubble
      var temp = buildBubble({ id: '', from_me: true, content: text, sender: DB.ME });
      temp.classList.add('pending');
      body.appendChild(temp);
      body.scrollTop = body.scrollHeight;
      input.value = '';

      var r = await DB.api('/api/messages/send', { method: 'POST', body: { to: activeUsername, content: text } });
      if (r.ok && r.data && r.data.ok) {
        temp.classList.remove('pending');
        var mid = r.data.message.id;
        temp.setAttribute('data-msg-id', mid);
        renderedIds[mid] = true;
        lastMessageId = Math.max(lastMessageId, mid);
        activeConvId = r.data.conversation_id;
        chatPanel.setAttribute('data-conv-id', activeConvId);
        loadConversations();
      } else {
        temp.classList.add('failed');
        temp.style.opacity = '0.4';
        var bub = temp.querySelector('.bubble');
        if (bub) bub.title = 'Failed to send';
      }
    });
  }

  /* ---------- Poll active conversation ---------- */
  async function pollActive() {
    if (!activeUsername) return;
    try {
      var r = await DB.api('/api/messages/conversation/' + encodeURIComponent(activeUsername) + '?after=' + lastMessageId);
      if (!(r.ok && r.data && r.data.ok)) return;
      var body = document.getElementById('chat-body');
      if (!body) return;
      var msgs = r.data.messages || [];
      if (!msgs.length) return;
      var wasBottom = nearBottom(body);
      msgs.forEach(function (m) {
        if (m.id && renderedIds[m.id]) return;
        body.appendChild(buildBubble(m));
        if (m.id) { renderedIds[m.id] = true; lastMessageId = Math.max(lastMessageId, m.id); }
      });
      if (wasBottom) body.scrollTop = body.scrollHeight;
    } catch (e) { /* ignore */ }
  }

  /* ---------- Inbox click (AJAX switch) ---------- */
  if (inboxList) {
    inboxList.addEventListener('click', function (ev) {
      var conv = ev.target.closest && ev.target.closest('.conv');
      if (!conv) return;
      ev.preventDefault();
      var username = conv.getAttribute('data-username');
      if (username) loadConversation(username, true);
    });
  }

  // Delete own message (delegated; the chat panel is rebuilt on conversation switch)
  document.addEventListener('click', async function (ev) {
    var del = ev.target.closest && ev.target.closest('.bubble-del');
    if (!del) return;
    var row = del.closest('.bubble-row');
    if (!row) return;
    var mid = row.getAttribute('data-msg-id');
    if (!mid) { row.remove(); return; } // optimistic bubble not yet saved
    if (!window.confirm('Remove this message?')) return;
    del.disabled = true;
    var r = await DB.api('/api/messages/message/' + mid + '/delete', { method: 'POST' });
    if (r.ok && r.data && r.data.ok) {
      delete renderedIds[mid];
      row.remove();
      loadConversations();
    } else {
      del.disabled = false;
    }
  });

  window.addEventListener('popstate', function () {
    var m = /^\/messages\/([^/]+)/.exec(location.pathname);
    if (m) loadConversation(decodeURIComponent(m[1]), false);
  });

  /* ---------- Inbox search ---------- */
  function applySearchFilter() {
    if (!inboxSearch) return;
    var term = (inboxSearch.value || '').trim().toLowerCase();
    DB.qa('.conv', inboxList).forEach(function (row) {
      var name = (row.querySelector('.conv-name') || {}).textContent || '';
      row.style.display = (!term || name.toLowerCase().indexOf(term) !== -1) ? '' : 'none';
    });
  }
  if (inboxSearch) inboxSearch.addEventListener('input', applySearchFilter);

  /* ---------- Boot ---------- */
  initFromServerRender();
  if (activeUsername) bindChatForm();
  loadConversations();
  setInterval(loadConversations, 2000);
  setInterval(pollActive, 2000);
})();
