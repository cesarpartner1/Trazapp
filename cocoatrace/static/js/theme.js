(() => {
  'use strict';

  const getStoredTheme = () => localStorage.getItem('theme');
  const setStoredTheme = (theme) => localStorage.setItem('theme', theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const setTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
  };

  setTheme(getPreferredTheme());

  window.addEventListener('DOMContentLoaded', () => {
    const themeToggler = document.createElement('button');
    themeToggler.classList.add('btn', 'btn-primary', 'position-fixed', 'bottom-0', 'end-0', 'm-3');
    themeToggler.textContent = 'Toggle Theme';
    document.body.appendChild(themeToggler);

    themeToggler.addEventListener('click', () => {
      const currentTheme = getStoredTheme() || getPreferredTheme();
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      setStoredTheme(newTheme);
      setTheme(newTheme);
    });
  });
})();
