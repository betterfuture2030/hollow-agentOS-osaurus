(function () {
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let theme = prefersDark ? 'dark' : 'light';

  function iconFor(nextTheme) {
    if (nextTheme === 'dark') {
      return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/><circle cx="12" cy="12" r="4"/></svg>';
    }
    return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>';
  }

  function setTheme(nextTheme) {
    theme = nextTheme;
    root.setAttribute('data-theme', theme);
    if (toggle) {
      toggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
      toggle.innerHTML = iconFor(theme);
    }
  }

  setTheme(theme);

  if (toggle) {
    toggle.addEventListener('click', () => {
      setTheme(theme === 'dark' ? 'light' : 'dark');
    });
  }
})();
