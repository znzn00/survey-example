// This should run before first render, just to make the page feels more natural on first visit
(() => {
    let theme = localStorage.getItem("theme");
    if (theme == null) {
        theme = 'auto';
        localStorage.setItem("theme", theme);
    }
    switch (theme) {
        case 'dark':
            document.documentElement.setAttribute('data-theme', 'dark');
            break;
        case 'auto':
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.documentElement.setAttribute('data-theme', 'dark');
            }
            break;
        default:// 'light' theme doesn't need
            break;
    }
})()