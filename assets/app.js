(function () {
  'use strict';

  var DATA = window.GROK_BOT_TEMPLATES;
  if (!DATA) return;

  var templates = DATA.templates;
  var UNCATEGORIZED = '其他';

  var shelf = document.getElementById('shelf');
  var chipsBox = document.getElementById('cat-chips');
  var search = document.getElementById('search');
  var clearBtn = document.getElementById('clear-search');
  var resultLine = document.getElementById('result-line');
  var emptyMsg = document.getElementById('empty');

  var activeCat = '';

  function zhCats(t) {
    return t.catsZh && t.catsZh.length ? t.catsZh : [UNCATEGORIZED];
  }

  function initial(name) {
    var ch = (name || '?').trim().charAt(0);
    return /[a-z]/.test(ch) ? ch.toUpperCase() : ch;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // ---- 头部统计 ----

  var creators = {};
  var catCounts = {};
  templates.forEach(function (t) {
    if (t.creator) creators[t.creator] = 1;
    zhCats(t).forEach(function (c) { catCounts[c] = (catCounts[c] || 0) + 1; });
  });

  document.getElementById('stat-count').textContent = templates.length;
  document.getElementById('stat-creators').textContent = Object.keys(creators).length;
  document.getElementById('stat-cats').textContent = Object.keys(DATA.categories).length;

  // ---- 分类筛选条 ----

  // 官方精选放最前，其余按数量降序，「其他」垫底。
  var catOrder = Object.keys(catCounts).sort(function (a, b) {
    if (a === '官方精选') return -1;
    if (b === '官方精选') return 1;
    if (a === UNCATEGORIZED) return 1;
    if (b === UNCATEGORIZED) return -1;
    return catCounts[b] - catCounts[a] || a.localeCompare(b, 'zh');
  });

  function makeChip(label, count, value) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chip';
    btn.dataset.cat = value;
    btn.setAttribute('aria-pressed', String(value === activeCat));
    btn.innerHTML = escapeHtml(label) + '<span class="n">' + count + '</span>';
    btn.addEventListener('click', function () {
      activeCat = value;
      Array.prototype.forEach.call(chipsBox.children, function (c) {
        c.setAttribute('aria-pressed', String(c.dataset.cat === activeCat));
      });
      render();
    });
    return btn;
  }

  chipsBox.appendChild(makeChip('全部', templates.length, ''));
  catOrder.forEach(function (c) {
    chipsBox.appendChild(makeChip(c, catCounts[c], c));
  });

  // ---- 卡片 ----

  function cardHtml(t) {
    var cats = zhCats(t);
    var tags = cats.map(function (c) {
      return '<span class="tag' + (c === '官方精选' ? ' official' : '') + '">' + escapeHtml(c) + '</span>';
    }).join('');

    var creator = t.handle
      ? escapeHtml(t.creator) + ' · @' + escapeHtml(t.handle)
      : escapeHtml(t.creator);

    return '' +
      '<article class="card">' +
        '<div class="card-top">' +
          '<div class="avatar" aria-hidden="true">' + escapeHtml(initial(t.name)) + '</div>' +
          '<div>' +
            '<h3>' + escapeHtml(t.nameZh) + '<span class="en">' + escapeHtml(t.name) + '</span></h3>' +
          '</div>' +
        '</div>' +
        '<p class="desc">' + escapeHtml(t.descZh || t.desc) + '</p>' +
        '<div class="tags">' + tags + '</div>' +
        '<p class="meta">创作者：' + creator + '</p>' +
        '<div class="actions">' +
          '<a class="btn btn-primary" href="' + escapeHtml(t.install) + '" target="_blank" rel="noopener noreferrer">安装 / 使用（官方页）</a>' +
          '<a class="btn btn-ghost" href="' + escapeHtml(t.detail) + '" target="_blank" rel="noopener noreferrer">官方详情</a>' +
        '</div>' +
      '</article>';
  }

  // ---- 筛选与渲染 ----

  function matches(t, q) {
    if (activeCat && zhCats(t).indexOf(activeCat) === -1) return false;
    if (!q) return true;
    var hay = [t.nameZh, t.name, t.descZh, t.desc, t.creator, t.handle, t.slug]
      .concat(zhCats(t)).join(' ').toLowerCase();
    return q.split(/\s+/).every(function (word) { return hay.indexOf(word) !== -1; });
  }

  function render() {
    var q = search.value.trim().toLowerCase();
    clearBtn.hidden = !q;

    var hits = templates.filter(function (t) { return matches(t, q); });

    shelf.innerHTML = hits.map(cardHtml).join('');
    emptyMsg.hidden = hits.length > 0;

    var scope = activeCat ? '「' + activeCat + '」' : '全部分类';
    resultLine.textContent = q
      ? scope + '中匹配「' + search.value.trim() + '」的模板 ' + hits.length + ' 个'
      : scope + '共 ' + hits.length + ' 个模板';
  }

  search.addEventListener('input', render);
  clearBtn.addEventListener('click', function () {
    search.value = '';
    search.focus();
    render();
  });

  render();
})();
