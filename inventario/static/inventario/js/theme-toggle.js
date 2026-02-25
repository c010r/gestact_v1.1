(function () {
    var STORAGE_KEY = 'asse-gestit-theme';
    var root = document.documentElement;

    function getPreferredTheme() {
        try {
            var stored = localStorage.getItem(STORAGE_KEY);
            if (stored === 'light' || stored === 'dark') {
                return stored;
            }
        } catch (error) {
            console.warn('No se pudo leer el tema almacenado.', error);
        }

        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        return 'light';
    }

    function applyTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            theme = 'light';
        }
        root.setAttribute('data-theme', theme);
        root.setAttribute('data-bs-theme', theme);
        document.documentElement.classList.add('theme-initialized');
        updateToggleState(theme);
    }

    function persistTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (error) {
            console.warn('No se pudo almacenar la preferencia de tema.', error);
        }
    }

    function updateToggleState(theme) {
        var toggles = document.querySelectorAll('[data-theme-toggle]');
        if (!toggles.length) {
            return;
        }
        var nextTheme = theme === 'light' ? 'dark' : 'light';
        toggles.forEach(function (toggle) {
            toggle.setAttribute('data-next-theme', nextTheme);
            toggle.setAttribute('title', theme === 'light' ? 'Activar modo oscuro' : 'Activar modo claro');
            toggle.setAttribute('aria-pressed', theme === 'dark');
        });
    }

    function toggleTheme() {
        var current = root.getAttribute('data-theme') || getPreferredTheme();
        var next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
        persistTheme(next);
    }

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(getPreferredTheme());
        var toggles = document.querySelectorAll('[data-theme-toggle]');
        toggles.forEach(function (toggle) {
            toggle.addEventListener('click', toggleTheme);
            toggle.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    toggleTheme();
                }
            });
        });

        if (window.matchMedia) {
            var mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            var handleChange = function (event) {
                var stored = null;
                try {
                    stored = localStorage.getItem(STORAGE_KEY);
                } catch (error) {
                    stored = null;
                }
                if (stored === 'light' || stored === 'dark') {
                    return;
                }
                applyTheme(event.matches ? 'dark' : 'light');
            };
            mediaQuery.addEventListener('change', handleChange);
        }
    });
})();
