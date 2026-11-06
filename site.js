// Graze & Rose - static site behaviors (mailto forms, date pickers, galleries)
(function () {
  "use strict";

  // ---- inquiry forms: compose a mailto: with the field values
  document.querySelectorAll("form.wixui-form").forEach(function (form) {
    form.setAttribute("action", "mailto:grazecatercda@gmail.com");
    form.setAttribute("method", "post");
    form.setAttribute("enctype", "text/plain");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var lines = [];
      form.querySelectorAll("input, select, textarea").forEach(function (inp) {
        if (!inp.name && !inp.id) return;
        var label = "";
        var lab = form.querySelector('label[for="' + inp.id + '"]');
        if (lab) label = lab.textContent.replace(/\*|required/g, "").trim();
        var val = inp.value || "";
        if (inp.type === "checkbox") val = inp.checked ? "Yes" : "No";
        lines.push(label + ": " + val);
      });
      var subj = "Inquiry from grazeandrose.com";
      var page = document.title.replace(/\s*\|.*$/, "");
      subj = page ? page + " - inquiry" : subj;
      var body = lines.join("\r\n");
      location.href = "mailto:grazecatercda@gmail.com?subject=" +
        encodeURIComponent(subj) + "&body=" + encodeURIComponent(body);
    });
  });

  // ---- date pickers: native picker behind the Wix-styled button
  document.querySelectorAll(".wixui-date-picker").forEach(function (dp) {
    var input = dp.querySelector("input");
    var btn = dp.querySelector("button");
    if (!input) return;
    input.removeAttribute("readonly");
    input.setAttribute("type", "date");
    if (btn) {
      btn.addEventListener("click", function () {
        try { input.showPicker && input.showPicker(); } catch (e) { input.focus(); }
      });
    }
  });

  // ---- slide-show galleries: cycle the restored slides
  document.querySelectorAll('[data-testid="slide-show-gallery"]').forEach(function (gal) {
    var slides = Array.prototype.slice.call(gal.querySelectorAll('.wixui-gallery__item'));
    if (!slides.length) return;
    var current = 0;
    var counter = gal.querySelector('[data-testid="gallery-counter"]');
    function show(idx) {
      current = (idx + slides.length) % slides.length;
      slides.forEach(function (s, i) {
        s.classList.toggle('on', i === current);
        s.setAttribute('aria-hidden', i === current ? 'false' : 'true');
      });
      if (counter) counter.textContent = (current + 1) + '/' + slides.length;
    }
    // Wix's own nav buttons (prev/next inside the gallery)
    var navBtns = gal.querySelectorAll('[data-testid="gallery-navButtons"] button');
    if (navBtns.length >= 2) {
      navBtns[0].addEventListener('click', function () { show(current - 1); });
      navBtns[1].addEventListener('click', function () { show(current + 1); });
    }
    // auto-advance, pause on hover
    var timer = setInterval(function () { show(current + 1); }, 4500);
    gal.addEventListener('mouseenter', function () { clearInterval(timer); });
    show(0);
  });
})();
