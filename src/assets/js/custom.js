// Filters on /writing/. Every article is already in the DOM; this narrows what
// is visible and keeps the URL in step so a filtered view can be shared.
// Without JS the chips stay plain links to the page showing the same subset.
(function () {
  var root = document.querySelector('[data-filters]');
  if (!root) return;

  var list = document.querySelector('[data-filter-list]');
  var status = document.querySelector('[data-filter-status]');
  var items = Array.prototype.slice.call(list.children);
  var chips = Array.prototype.slice.call(root.querySelectorAll('[data-filter]'));
  var active = {};

  function matches(item) {
    if (active.type && item.dataset.type !== active.type) return false;
    if (active.category && item.dataset.category !== active.category) return false;
    if (active.tag) {
      var tags = (item.dataset.tags || '').split(' ');
      if (tags.indexOf(active.tag) === -1) return false;
    }
    return true;
  }

  function apply(push) {
    var shown = 0;
    items.forEach(function (item) {
      var ok = matches(item);
      item.hidden = !ok;
      if (ok) shown++;
    });

    chips.forEach(function (chip) {
      var on = active[chip.dataset.filter] === chip.dataset.value;
      chip.classList.toggle('is-active', on);
      chip.setAttribute('aria-pressed', on ? 'true' : 'false');
    });

    var keys = Object.keys(active).filter(function (k) { return active[k]; });
    if (keys.length) {
      status.hidden = false;
      status.textContent = shown + (shown === 1 ? ' article' : ' articles') + ' shown.';
      var clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'filter-clear';
      clear.textContent = 'Clear filters';
      clear.addEventListener('click', function () { active = {}; apply(true); });
      status.appendChild(document.createTextNode(' '));
      status.appendChild(clear);
    } else {
      status.hidden = true;
      status.textContent = '';
    }

    if (push && window.history.replaceState) {
      var q = new URLSearchParams();
      keys.forEach(function (k) { q.set(k, active[k]); });
      var qs = q.toString();
      window.history.replaceState(null, '', qs ? '?' + qs : window.location.pathname);
    }
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function (e) {
      e.preventDefault();
      var key = chip.dataset.filter;
      active[key] = active[key] === chip.dataset.value ? null : chip.dataset.value;
      apply(true);
    });
  });

  // Honour ?type=, ?category= and ?tag= on load, so a shared link opens filtered.
  var params = new URLSearchParams(window.location.search);
  ['type', 'category', 'tag'].forEach(function (k) {
    if (params.get(k)) active[k] = params.get(k);
  });
  apply(false);
})();
