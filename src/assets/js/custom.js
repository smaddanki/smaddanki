// Filters on /writing/. Every article is already in the DOM; this narrows what
// is visible and keeps the URL in step so a filtered view can be shared.
// The dropdowns are <details>, so without JS they still open and every item is
// a real link to the page showing the same subset.
(function () {
  // Doks loads app.js with `async`, so this can run before the body is parsed.
  // Without this guard the query below finds nothing, the script bails, and the
  // filter links fall through to plain navigation — intermittently, depending on
  // how the bundle download races the parser.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
  var root = document.querySelector('[data-filters]');
  if (!root) return;

  var list = document.querySelector('[data-filter-list]');
  var status = document.querySelector('[data-filter-status]');
  var items = Array.prototype.slice.call(list.children);
  var links = Array.prototype.slice.call(root.querySelectorAll('[data-filter]'));
  var dropdowns = Array.prototype.slice.call(root.querySelectorAll('[data-dropdown]'));
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

  function render(push) {
    var shown = 0;
    items.forEach(function (item) {
      var ok = matches(item);
      item.hidden = !ok;
      if (ok) shown++;
    });

    links.forEach(function (link) {
      var chosen = active[link.dataset.filter] || '';
      // Leave "All" unhighlighted when nothing is filtered — a solid bar on
      // the default state reads as a selection the reader did not make.
      link.classList.toggle('is-active', !!chosen && chosen === link.dataset.value);
    });

    // Each dropdown's summary shows what it is currently filtered to.
    dropdowns.forEach(function (d) {
      var key = d.dataset.dropdown;
      var current = d.querySelector('[data-current]');
      var chosen = links.filter(function (l) {
        return l.dataset.filter === key && l.dataset.value === active[key];
      })[0];
      current.textContent = chosen ? (chosen.dataset.label || chosen.dataset.value) : 'All';
      d.classList.toggle('is-set', !!chosen);
    });

    var keys = Object.keys(active).filter(function (k) { return active[k]; });
    status.textContent = '';
    if (keys.length) {
      status.hidden = false;
      status.appendChild(document.createTextNode(
        shown + (shown === 1 ? ' article' : ' articles') + ' shown. '));
      var clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'filter-clear';
      clear.textContent = 'Clear filters';
      clear.addEventListener('click', function () { active = {}; render(true); });
      status.appendChild(clear);
    } else {
      status.hidden = true;
    }

    if (push && window.history.replaceState) {
      var q = new URLSearchParams();
      keys.forEach(function (k) { q.set(k, active[k]); });
      var qs = q.toString();
      window.history.replaceState(null, '', qs ? '?' + qs : window.location.pathname);
    }
  }

  links.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var key = link.dataset.filter;
      active[key] = link.dataset.value || null;
      dropdowns.forEach(function (d) { d.open = false; });
      render(true);
    });
  });

  // Close an open dropdown when the click lands outside it.
  document.addEventListener('click', function (e) {
    dropdowns.forEach(function (d) {
      if (d.open && !d.contains(e.target)) d.open = false;
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') dropdowns.forEach(function (d) { d.open = false; });
  });

  // Honour ?type=, ?category= and ?tag= on load, so a shared link opens filtered.
  var params = new URLSearchParams(window.location.search);
  ['type', 'category', 'tag'].forEach(function (k) {
    if (params.get(k)) active[k] = params.get(k);
  });
  render(false);
  }
})();
