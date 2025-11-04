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

  const applyTheme = (theme) => {
    setTheme(theme);
    setStoredTheme(theme);
  };

  const refreshToggleButton = (theme) => {
    const toggle = document.querySelector('[data-theme-toggle]');
    if (!toggle) {
      return;
    }
    toggle.setAttribute('data-theme-current', theme);
    const icon = toggle.querySelector('[data-theme-icon]');
    if (icon) {
      icon.className = theme === 'dark' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    }
    const label = toggle.querySelector('[data-theme-label]');
    if (label) {
      label.textContent = theme === 'dark' ? 'Dark' : 'Light';
    }
  };

  const initTheme = () => {
    const theme = getPreferredTheme();
    setTheme(theme);
    refreshToggleButton(theme);
  };

  window.addEventListener('DOMContentLoaded', () => {
    initTheme();

    const toggle = document.querySelector('[data-theme-toggle]');
    if (toggle) {
      toggle.addEventListener('click', () => {
        const currentTheme = getStoredTheme() || getPreferredTheme();
        const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(nextTheme);
        refreshToggleButton(nextTheme);
      });
    }
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return;
    }
    const theme = event.matches ? 'dark' : 'light';
    setTheme(theme);
    refreshToggleButton(theme);
  });
})();
