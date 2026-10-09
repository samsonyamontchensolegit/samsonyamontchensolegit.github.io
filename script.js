(function () {
  var root = document.documentElement;
  var langBtn = document.getElementById('lang');
  var themeBtn = document.getElementById('theme');
  var titles = {
    fr: 'Samson Yamontche – Expert LaTeX',
    en: 'Samson Yamontche – LaTeX Expert'
  };
  var themeLabels = {
    fr: { dark: 'Passer en mode sombre', light: 'Passer en mode clair' },
    en: { dark: 'Switch to dark mode', light: 'Switch to light mode' }
  };

  function save(key, value) {
    try { localStorage.setItem(key, value); } catch (e) {}
  }

  function isDark() {
    var t = root.getAttribute('data-theme');
    if (t) return t === 'dark';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function render() {
    var lang = root.lang === 'fr' ? 'fr' : 'en';
    document.title = titles[lang];
    langBtn.textContent = lang === 'fr' ? 'EN' : 'FR';
    var dark = isDark();
    themeBtn.textContent = dark ? '☀' : '☾';
    themeBtn.setAttribute('aria-label', themeLabels[lang][dark ? 'light' : 'dark']);
  }

  langBtn.addEventListener('click', function () {
    root.lang = root.lang === 'fr' ? 'en' : 'fr';
    save('lang', root.lang);
    render();
  });

  themeBtn.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    save('theme', next);
    render();
  });

  render();
})();
