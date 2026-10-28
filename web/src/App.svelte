<script lang="ts">
  import { onMount } from "svelte";
  import { i18n, setLanguage, t, type Key, type Language } from "./lib/i18n.svelte";
  import { loadPython, python, setTheme, theme } from "./lib/state.svelte";
  import ConvertTab from "./tabs/ConvertTab.svelte";
  import DiagnoseTab from "./tabs/DiagnoseTab.svelte";
  import ParametersTab from "./tabs/ParametersTab.svelte";
  import ResultsTab from "./tabs/ResultsTab.svelte";

  type Page = "convert" | "parameters" | "results" | "diagnose";

  // feather-style icons, as in the other LithoVox apps
  const ICONS: Record<Page, string> = {
    convert:
      '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    parameters:
      '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/>',
    results: '<polyline points="3 3 3 21 21 21"/><path d="M6 6c3 0 4 8 7 10s5 2 8 2"/>',
    diagnose: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
  };

  const MENU: { heading: Key; pages: Page[] }[] = [
    { heading: "menu.tools", pages: ["convert", "parameters", "results"] },
    { heading: "menu.support", pages: ["diagnose"] },
  ];

  const LANGUAGES: Language[] = ["nl", "en"];

  // #diagnose opens the diagnostics directly, handy to send to IT
  let page = $state<Page>(location.hash === "#diagnose" ? "diagnose" : "convert");
  let collapsed = $state(false);
  let helpOpen = $state(false);
  let languagesOpen = $state(false);

  onMount(() => {
    setLanguage(i18n.language);
    setTheme(theme.value);
    loadPython();
  });

  let status = $derived(
    python.state === "ready"
      ? t("python.ready")
      : python.state === "failed"
        ? t("python.failed")
        : t(`python.${python.step}` as Key),
  );

  const pageTitle = (name: Page) => t(`tab.${name}` as Key);
</script>

<svelte:window
  onkeydown={(e) => {
    if (e.key === "Escape") {
      helpOpen = false;
      languagesOpen = false;
    }
  }}
  onclick={() => (languagesOpen = false)}
/>

<div class="app">
  <header class="topbar">
    <div class="brand">
      <a class="brand-link" href="https://lithovox.nl" target="_blank" rel="noopener noreferrer">
        <img class="brand-logo" src="./logo.png" alt="LithoVox" />
        <span class="brand-title"><span>Litho</span><span class="brand-vox">Vox</span></span>
      </a>
      <span class="brand-sub">slicmd <span class="brand-version">v{__APP_VERSION__}</span></span>
    </div>

    <div class="topbar-actions">
      <span class="python-status {python.state}" role="status">
        {#if python.state === "loading"}<span class="spinner" aria-hidden="true"></span>{/if}
        {status}
      </span>
      <div class="toolbar-divider"></div>
      <button
        type="button"
        class="toolbar-btn"
        title={t("help.button")}
        aria-label={t("help.button")}
        onclick={() => (helpOpen = true)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      </button>
      <div class="language-menu">
        <button
          type="button"
          class="toolbar-btn"
          title={t("language.title")}
          aria-label={t("language.title")}
          aria-haspopup="true"
          aria-expanded={languagesOpen}
          onclick={(e) => {
            e.stopPropagation();
            languagesOpen = !languagesOpen;
          }}
        >
          <img class="language-flag" src={`./flags/${i18n.language}.svg`} alt={i18n.language.toUpperCase()} />
        </button>
        {#if languagesOpen}
          <div class="language-options">
            {#each LANGUAGES as language (language)}
              <button
                type="button"
                class="language-option"
                class:active={i18n.language === language}
                aria-label={language.toUpperCase()}
                onclick={() => {
                  setLanguage(language);
                  languagesOpen = false;
                }}
              >
                <img class="language-flag" src={`./flags/${language}.svg`} alt="" />
              </button>
            {/each}
          </div>
        {/if}
      </div>
      <div class="toolbar-divider"></div>
      <button
        type="button"
        class="theme-switch"
        role="switch"
        aria-checked={theme.value === "dark"}
        aria-label={t("theme.dark")}
        title={t("theme.dark")}
        onclick={() => setTheme(theme.value === "dark" ? "light" : "dark")}
      >
        <span class="theme-switch-track"><span class="theme-switch-thumb"></span></span>
      </button>
    </div>
  </header>

  <div class="body">
    <aside class="sidebar" class:collapsed>
      <button
        type="button"
        class="icon-btn sidebar-toggle"
        aria-expanded={!collapsed}
        title={collapsed ? t("menu.unfold") : t("menu.fold")}
        aria-label={collapsed ? t("menu.unfold") : t("menu.fold")}
        onclick={() => (collapsed = !collapsed)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="11 17 6 12 11 7" /><polyline points="18 17 13 12 18 7" />
        </svg>
      </button>
      <nav class="sidebar-content" aria-label="Menu">
        {#each MENU as section (section.heading)}
          <section class="sidebar-section">
            <h3 class="sidebar-heading">{t(section.heading)}</h3>
            {#each section.pages as name (name)}
              <button
                type="button"
                class="toolbar-btn sidebar-btn"
                class:active={page === name}
                aria-current={page === name ? "page" : undefined}
                onclick={() => (page = name)}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  {@html ICONS[name]}
                </svg>
                <span>{pageTitle(name)}</span>
              </button>
            {/each}
          </section>
        {/each}
      </nav>
    </aside>

    <main class="content">
      <div class="page">
        <h1 class="page-title">{pageTitle(page)}</h1>

        {#if python.state === "failed" && page !== "diagnose"}
          <div class="message error">
            <strong>{t("python.failed")}</strong> — {python.error}
            <button type="button" class="link-btn" onclick={() => (page = "diagnose")}>{t("python.failed.help")}</button>
          </div>
        {/if}

        <!-- the pages stay mounted, so switching keeps their files -->
        <div hidden={page !== "convert"}><ConvertTab /></div>
        <div hidden={page !== "parameters"}><ParametersTab onuse={() => (page = "convert")} /></div>
        <div hidden={page !== "results"}><ResultsTab /></div>
        {#if page === "diagnose"}<DiagnoseTab />{/if}

        <p class="hint footer-note">🔒 {t("privacy")} ⚠ {t("warning")}</p>
      </div>
    </main>
  </div>
</div>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
<div
  class="modal-overlay"
  class:visible={helpOpen}
  onmousedown={(e) => {
    if (e.target === e.currentTarget) helpOpen = false;
  }}
>
  <div class="modal-card help-card" role="dialog" aria-modal="true" aria-labelledby="help-title">
    <button type="button" class="help-close" aria-label={t("help.close")} onclick={() => (helpOpen = false)}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
    <div class="help-hero">
      <img class="help-logo" src="./logo.png" alt="LithoVox" />
      <div>
        <h2 id="help-title" class="help-brand">Litho<span class="brand-vox">Vox</span> slicmd</h2>
        <p class="help-lead">{t("help.lead")}</p>
      </div>
    </div>
    <div class="help-body">
      <h3>{t("tab.convert")}</h3>
      <p>{t("help.convert")}</p>
      <h3>{t("tab.parameters")}</h3>
      <p>{t("help.parameters")}</p>
      <h3>{t("tab.results")}</h3>
      <p>{t("help.results")}</p>
      <p class="help-note">🔒 {t("privacy")}</p>
      <p class="help-warning">{t("warning")}</p>
      <p class="hint">
        slicmd v{__APP_VERSION__} ·
        <a href="https://github.com/lithovox/sli-commands" target="_blank" rel="noopener noreferrer">GitHub</a>
      </p>
    </div>
  </div>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }

  /* ============ Top bar ============ */
  .topbar {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    height: var(--topbar-height);
    padding: 0 20px;
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    z-index: 20;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }

  .brand-link {
    display: flex;
    align-items: center;
    gap: inherit;
    flex-shrink: 0;
    color: inherit;
    text-decoration: none;
  }

  .brand-logo {
    width: 32px;
    height: 32px;
    object-fit: contain;
  }

  .brand-title {
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: 0.01em;
  }

  .brand-vox {
    color: var(--color-teal);
  }

  .brand-sub {
    margin-left: 8px;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .brand-version {
    font-size: 0.85rem;
    font-weight: 400;
    opacity: 0.8;
  }

  .topbar-actions {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .toolbar-divider {
    width: 1px;
    height: 24px;
    margin: 0 6px;
    background: var(--border-color);
  }

  .python-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .python-status.ready {
    background: var(--ok-bg);
    color: var(--ok-color);
  }

  .python-status.loading {
    background: var(--color-teal-soft);
    color: var(--color-teal);
  }

  .python-status.failed {
    background: var(--danger-bg);
    color: var(--danger-color);
  }

  .spinner {
    width: 10px;
    height: 10px;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* ============ Language menu ============ */
  .language-menu {
    position: relative;
  }

  .language-options {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    z-index: 1100;
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(15, 53, 73, 0.15);
  }

  .language-option {
    display: flex;
    padding: 6px 8px;
    background: transparent;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  .language-option:hover,
  .language-option.active {
    background: var(--color-teal-soft);
  }

  .language-flag {
    display: block;
    width: 24px;
    height: 16px;
    border-radius: 2px;
    box-shadow: 0 0 0 1px var(--border-color);
    object-fit: cover;
  }

  /* ============ Theme switch ============ */
  .theme-switch {
    display: flex;
    align-items: center;
    padding: 0;
    margin: 0 4px;
    border: none;
    background: transparent;
    cursor: pointer;
  }

  .theme-switch-track {
    position: relative;
    width: 36px;
    height: 20px;
    border-radius: 999px;
    background: var(--border-color);
    transition: background-color 0.2s ease;
  }

  .theme-switch-thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--bg-card);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease;
  }

  .theme-switch[aria-checked="true"] .theme-switch-track {
    background: var(--accent-gradient);
  }

  .theme-switch[aria-checked="true"] .theme-switch-thumb {
    transform: translateX(16px);
  }

  /* ============ Body: left menu and content ============ */
  .body {
    flex: 1;
    display: flex;
    min-height: 0;
  }

  .sidebar {
    flex: 0 0 var(--sidebar-width);
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    overflow-x: hidden;
    overflow-y: auto;
    background: var(--bg-card);
    border-right: 1px solid var(--border-color);
    transition:
      flex-basis 0.2s ease,
      padding 0.2s ease;
  }

  .sidebar.collapsed {
    flex-basis: var(--sidebar-collapsed-width);
    padding: 12px 8px;
  }

  .sidebar-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: calc(var(--sidebar-width) - 32px);
  }

  .sidebar.collapsed .sidebar-content {
    display: none;
  }

  .sidebar-toggle {
    flex-shrink: 0;
    align-self: flex-end;
    margin: -8px -8px 0 0;
  }

  .sidebar-toggle svg {
    transition: transform 0.2s ease;
  }

  .sidebar.collapsed .sidebar-toggle {
    align-self: center;
    margin: 0;
  }

  .sidebar.collapsed .sidebar-toggle svg {
    transform: rotate(180deg);
  }

  .sidebar-section {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .sidebar-section + .sidebar-section {
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
  }

  .sidebar-heading {
    margin: 0 0 4px;
    padding: 0 12px;
    color: var(--text-secondary);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .sidebar-btn {
    width: 100%;
    justify-content: flex-start;
    padding: 0 12px;
  }

  .sidebar-btn.active,
  .sidebar-btn.active:hover {
    background: var(--color-teal-soft);
    color: var(--color-teal);
    font-weight: 600;
  }

  .content {
    flex: 1;
    min-width: 0;
    overflow-y: auto;
    background: var(--bg-panel);
  }

  .page {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 28px 32px;
  }

  .page-title {
    font-size: 1.3rem;
    font-weight: 600;
  }

  .footer-note {
    margin-top: 8px;
  }

  /* ============ Help ============ */
  .help-card {
    position: relative;
    max-width: 680px;
    max-height: 88vh;
    overflow-y: auto;
    padding: 32px 36px;
  }

  .help-close {
    position: absolute;
    top: 14px;
    right: 14px;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: 8px;
    color: var(--text-secondary);
    cursor: pointer;
  }

  .help-close:hover {
    background: var(--color-teal-soft);
    color: var(--text-primary);
  }

  .help-close svg {
    width: 20px;
    height: 20px;
  }

  .help-hero {
    display: flex;
    align-items: center;
    gap: 24px;
    padding-bottom: 20px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
  }

  .help-logo {
    width: 110px;
    height: 110px;
    object-fit: contain;
    flex-shrink: 0;
  }

  .help-brand {
    margin: 0 0 8px;
    font-size: 1.7rem;
    font-weight: 600;
  }

  .help-lead {
    color: var(--text-secondary);
  }

  .help-body {
    font-size: 0.92rem;
    line-height: 1.6;
  }

  .help-body h3 {
    margin: 18px 0 4px;
    font-size: 1rem;
    color: var(--color-teal);
  }

  .help-note {
    margin-top: 18px;
  }

  .help-warning {
    margin: 10px 0;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--danger-bg);
    color: var(--danger-color);
  }

  @media (max-width: 700px) {
    .brand-sub,
    .python-status {
      display: none;
    }

    .help-card {
      padding: 24px 20px;
    }

    .help-hero {
      flex-direction: column;
      text-align: center;
    }
  }
</style>
