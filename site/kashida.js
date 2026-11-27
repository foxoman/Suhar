// Kashida justification for the web: the same rules as tools/kashida.py.
// justifyElement(el) stretches every line of an Arabic paragraph but the last with tatweels, then lets the browser
// justify what is left with the word spaces.
(function (g) {
  var T = 'ـ', RIGHT = 'اأإآٱدذرزوؤةىءٹڈڑژۃے', SEEN = 'سشصض', P2 = 'هةدذ', P3 = 'الك', P4 = 'ريىنعغز';
  function isLetter(c) { return c >= 'ؠ' && c <= 'ۿ' && c !== T && !/[ً-ٰٟۖ-ۭ]/.test(c); }
  function places(w) {
    var L = [], out = [], i;
    for (i = 0; i < w.length; i++) if (isLetter(w[i])) L.push(i);
    if (L.length < 3 || w.indexOf(T) >= 0) return out;
    for (i = 0; i + 1 < L.length; i++) {
      var a = w[L[i]], b = w[L[i + 1]], last = i + 2 === L.length;
      if (RIGHT.indexOf(a) >= 0 || (a === 'ل' && 'اأإآٱ'.indexOf(b) >= 0)) continue;
      var p = SEEN.indexOf(a) >= 0 ? 1 : last && P2.indexOf(b) >= 0 ? 2 : last && P3.indexOf(b) >= 0 ? 3 : last && P4.indexOf(b) >= 0 ? 4 : 5;
      out.push([p, L[i + 1]]);
    }
    return out;
  }
  function justify(words, width, measure) {
    words = words.slice();
    var used = words.map(function () { return 0; });
    for (;;) {
      var best = null;
      words.forEach(function (w, wi) {
        if (used[wi]) return;
        places(w).forEach(function (pl) {
          var c = [pl[0], -w.length, wi, pl[1]];
          if (!best || c[0] < best[0] || (c[0] === best[0] && c[1] < best[1])) best = c;
        });
      });
      if (!best) break;
      var wi = best[2], t = words[wi].slice(0, best[3]) + T + words[wi].slice(best[3]);
      var trial = words.slice(); trial[wi] = t;
      used[wi] = 1;
      if (measure(trial.join(' ')) <= width) words = trial;
    }
    return words;
  }
  function justifyElement(el) {
    var text = (el.dataset.plain || (el.dataset.plain = el.textContent)).trim(), cs = getComputedStyle(el);
    var cv = justifyElement.cv || (justifyElement.cv = document.createElement('canvas')), ctx = cv.getContext('2d');
    ctx.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily; ctx.direction = 'rtl';
    var measure = function (s) { return ctx.measureText(s).width; }, width = el.clientWidth - 1, lines = [], cur = [];
    text.split(/\s+/).forEach(function (w) {
      if (cur.length && measure(cur.concat([w]).join(' ')) > width) { lines.push(cur); cur = [w]; } else cur.push(w);
    });
    if (cur.length) lines.push(cur);
    el.textContent = lines.map(function (l, i) { return (i < lines.length - 1 ? justify(l, width, measure) : l).join(' '); }).join(' ');
  }
  g.SuharKashida = { places: places, justify: justify, justifyElement: justifyElement };
})(window);
