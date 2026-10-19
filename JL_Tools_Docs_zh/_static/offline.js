/* Offline copy of the Jieli Tools documentation: navigation, image zoom and local search. */
(function () {
  "use strict";
  var LANG = "zh";

  function qs(sel, root) { return (root || document).querySelector(sel); }

  function closest(el, sel) {
    while (el && el.nodeType === 1) {
      if (el.matches(sel)) return el;
      el = el.parentElement;
    }
    return null;
  }

  function closeLightbox() {
    var box = qs(".offline-lightbox");
    if (box) box.parentNode.removeChild(box);
  }

  function openLightbox(src) {
    closeLightbox();
    var box = document.createElement("div");
    box.className = "offline-lightbox";
    var img = document.createElement("img");
    img.src = src;
    box.appendChild(img);
    box.addEventListener("click", closeLightbox);
    document.body.appendChild(box);
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeLightbox();
  });

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (closest(t, '[data-toggle="wy-nav-top"]')) {
      qs(".wy-nav-side").classList.toggle("shift");
      qs(".wy-nav-content-wrap").classList.toggle("shift");
      return;
    }
    var btn = closest(t, "button.toctree-expand");
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      var li = closest(btn, "li");
      if (li) li.classList.toggle("current");
      return;
    }
    if (closest(t, ".wy-menu-vertical a")) {
      qs(".wy-nav-side").classList.remove("shift");
      qs(".wy-nav-content-wrap").classList.remove("shift");
    }
    var img = closest(t, '[itemprop="articleBody"] img');
    if (img) {
      var link = closest(img, "a[href]");
      if (!link || link.classList.contains("image-reference")) {
        e.preventDefault();
        openLightbox(img.currentSrc || img.src);
      }
    }
  });

  // Keep the current page visible in the sidebar.
  var cur = qs(".wy-menu-vertical a.current") || qs(".wy-menu-vertical li.current > a");
  var scroller = qs(".wy-side-scroll");
  if (cur && scroller) {
    var delta = cur.getBoundingClientRect().top - scroller.getBoundingClientRect().top;
    if (delta > scroller.clientHeight * 0.6) scroller.scrollTop += delta - scroller.clientHeight / 3;
  }

  // ------------------------------------------------------------------ search page
  var results = qs("#offline-search-results");
  if (!results || !window.SEARCH_INDEX) return;
  var input = qs("#offline-q");
  var status = qs("#offline-search-status");

  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function highlight(text, terms) {
    var out = esc(text);
    terms.forEach(function (term) {
      var re = new RegExp(esc(term).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      out = out.replace(re, function (m) { return "<mark>" + m + "</mark>"; });
    });
    return out;
  }

  function snippet(text, terms) {
    var lower = text.toLowerCase();
    var pos = -1;
    for (var i = 0; i < terms.length && pos < 0; i++) pos = lower.indexOf(terms[i]);
    if (pos < 0) return text.slice(0, 160) + (text.length > 160 ? " …" : "");
    var start = Math.max(0, pos - 60);
    var end = Math.min(text.length, pos + 140);
    return (start > 0 ? "… " : "") + text.slice(start, end) + (end < text.length ? " …" : "");
  }

  function count(hay, needle) {
    var n = 0, i = hay.indexOf(needle);
    while (i >= 0 && n < 20) { n++; i = hay.indexOf(needle, i + needle.length); }
    return n;
  }

  function run(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    results.innerHTML = "";
    if (!terms.length) { status.textContent = ""; return; }
    var found = [];
    window.SEARCH_INDEX.forEach(function (e) {
      var h = e.h.toLowerCase(), t = e.t.toLowerCase(), x = e.x.toLowerCase();
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var term = terms[i];
        var inH = h.indexOf(term) >= 0, inT = t.indexOf(term) >= 0, nX = count(x, term);
        if (!inH && !inT && !nX) return;
        score += (inH ? 10 : 0) + (inT ? 3 : 0) + (nX ? 1 + nX * 0.2 : 0);
      }
      found.push({ e: e, s: score });
    });
    found.sort(function (a, b) { return b.s - a.s; });
    status.textContent = found.length
      ? status.getAttribute("data-found").replace("{n}", found.length)
      : status.getAttribute("data-none");
    var html = [];
    found.slice(0, 300).forEach(function (r) {
      var e = r.e;
      var href = e.p.split("/").map(encodeURIComponent).join("/") + (e.a ? "#" + e.a : "");
      html.push(
        '<li><a class="res-title" href="' + href + '">' + highlight(e.h, terms) + "</a>" +
        '<span class="res-page">' + esc(e.t) + "</span>" +
        '<p class="context">' + highlight(snippet(e.x, terms), terms) + "</p></li>"
      );
    });
    results.innerHTML = html.join("");
  }

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      run(input.value);
      try { history.replaceState(null, "", "?q=" + encodeURIComponent(input.value)); } catch (err) { /* file:// may refuse */ }
    }, 200);
  });
  var m = /[?&]q=([^&]*)/.exec(location.search);
  if (m) {
    input.value = decodeURIComponent(m[1].replace(/\+/g, " "));
    var side = qs('#rtd-search-form input[name="q"]');
    if (side) side.value = input.value;
  }
  run(input.value);
})();
