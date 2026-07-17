"""HTML + CSS template for Forge — the CypherTempre PoC host UI."""

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0a0706">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" type="image/svg+xml" href="/icon.svg">
  <link rel="apple-touch-icon" href="/icon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700;800&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
  <title>Forge</title>
  <script>
    /* Boot before paint: dark-first theme + rail collapse (no FOUC) */
    (function () {
      try {
        var theme = localStorage.getItem('ct_theme');
        if (theme === 'light') document.documentElement.classList.add('light');
        else document.documentElement.classList.remove('light');
        if (localStorage.getItem('ct_rail_collapsed') === 'true') {
          document.documentElement.classList.add('rail-collapsed');
        }
        if (localStorage.getItem('ct_density') === 'compact') {
          document.documentElement.classList.add('density-compact');
        }
      } catch (e) {}
    })();
  </script>
  <style>
    /* Animate shell width (required for smooth grid tuck) */
    @property --shell-w {
      syntax: "<length>";
      inherits: true;
      initial-value: 268px;
    }
    :root {
      color-scheme: dark;
      /* Canvas — deep charcoal with forge ember */
      --bg: #0a0706;
      --surface: #14100e;
      --surface-2: #1c1613;
      --surface-3: #261e19;
      /* Borders — vapor, not wireframes */
      --line: rgba(255, 230, 210, 0.07);
      --line-soft: rgba(255, 230, 210, 0.035);
      --line-strong: rgba(255, 230, 210, 0.12);
      /* Type */
      --text: #f6f0ea;
      --muted: #a8988c;
      --faint: #6f6258;
      --font-ui: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --font-display: "Syne", Inter, ui-sans-serif, system-ui, sans-serif;
      --font-serif: "Instrument Serif", Georgia, "Times New Roman", serif;
      /* Accents — Forge fire (kept --blue* names for legacy selectors) */
      --green: #34d399;
      --blue: #ff8a5c;
      --blue-deep: #e85d2a;
      --indigo: #f59e0b;
      --amber: #f0b429;
      --red: #f87171;
      --violet: #fb923c;
      --fire: #ff8a5c;
      --fire-deep: #e85d2a;
      --ember: #c2410c;
      --cyan-glow: rgba(255, 122, 77, 0.42);
      /* Elevation — soft air, not hard cards */
      --shadow: rgba(0, 0, 0, 0.52);
      --shadow-soft: 0 10px 40px -12px rgba(0, 0, 0, 0.52);
      --shadow-card: 0 16px 48px -18px rgba(0, 0, 0, 0.58);
      --shadow-float: 0 28px 72px -20px rgba(0, 0, 0, 0.72);
      --glow-blue: 0 0 0 1px rgba(255, 122, 77, 0.24), 0 12px 36px -8px rgba(232, 93, 42, 0.32);
      --glow-fire: var(--glow-blue);
      --fire-gradient: var(--fire-gradient);
      /* Surfaces & chrome */
      --nav-bg: rgba(18, 12, 10, 0.45);
      --nav-active-bg: linear-gradient(145deg, #ff8a5c 0%, #e85d2a 50%, #c2410c 100%);
      --nav-active-text: #ffffff;
      --input-bg: rgba(10, 7, 6, 0.6);
      --panel-bg: rgba(18, 14, 12, 0.5);
      --bubble-bg: transparent;
      --user-bubble-bg: linear-gradient(160deg, rgba(72, 28, 18, 0.92) 0%, rgba(48, 18, 12, 0.95) 55%, rgba(36, 14, 10, 0.94) 100%);
      --composer-bg: transparent;
      --chat-top-bg: transparent;
      --status-card-bg: linear-gradient(165deg, rgba(32, 22, 18, 0.75), rgba(14, 10, 8, 0.85));
      --rail-inspector-bg: rgba(12, 9, 8, 0.78);
      --mobile-nav-bg: rgba(10, 7, 6, 0.94);
      --overlay-bg: rgba(6, 3, 2, 0.68);
      --guide-hero-bg: linear-gradient(135deg, rgba(255, 122, 77, 0.10), rgba(10, 7, 6, 0.97) 42%, rgba(245, 158, 11, 0.07));
      --feature-card-bg: rgba(24, 18, 15, 0.58);
      --project-attribution-bg: rgba(16, 12, 10, 0.85);
      --memory-card-bg: rgba(24, 18, 15, 0.52);
      --ring-card-bg: rgba(24, 18, 15, 0.52);
      --thinking-bg: linear-gradient(180deg, rgba(56, 24, 14, 0.55), rgba(28, 14, 10, 0.42));
      --rejected-bg: rgba(40, 16, 18, 0.55);
      --orb-1: rgba(255, 122, 77, 0.16);
      --orb-2: rgba(245, 158, 11, 0.12);
      --orb-3: rgba(239, 68, 68, 0.08);
      /* Radius scale — softer organic */
      --r-sm: 12px;
      --r-md: 16px;
      --r-lg: 22px;
      --r-xl: 28px;
      --r-pill: 999px;
      /* Motion */
      --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
      --ease-spring: cubic-bezier(0.34, 1.3, 0.64, 1);
      --dur-fast: 0.15s;
      --dur: 0.24s;
      --dur-slow: 0.42s;
      /* Chat stage width */
      --stage: min(720px, 100%);
      /* Shell instrument — one system for rail + menu + layout */
      --shell-w-expanded: 268px;
      --shell-w-collapsed: 72px;
      --shell-w: var(--shell-w-expanded);
      --shell-pad: 14px;
      --shell-gap: 4px;
      --shell-section-gap: 16px;
      --shell-radius: 11px;
      --shell-item-h: 36px;
      --shell-fill: rgba(255, 230, 210, 0.04);
      --shell-fill-hover: rgba(255, 230, 210, 0.07);
      --shell-fill-active: linear-gradient(135deg, rgba(255, 122, 77, 0.20) 0%, rgba(245, 158, 11, 0.12) 100%);
      --shell-edge: rgba(255, 122, 77, 0.62);
      --shell-muted: var(--muted);
      --shell-faint: var(--faint);
      --shell-ease: cubic-bezier(0.32, 0.72, 0, 1);
      --shell-dur: 0.42s;
    }

    .light {
      color-scheme: light;
      --shell-fill: rgba(68, 28, 14, 0.05);
      --shell-fill-hover: rgba(68, 28, 14, 0.08);
      --shell-fill-active: linear-gradient(135deg, rgba(234, 88, 12, 0.12) 0%, rgba(245, 158, 11, 0.10) 100%);
      --shell-edge: rgba(234, 88, 12, 0.5);
      --bg: #faf6f3;
      --surface: #ffffff;
      --surface-2: #f5eeea;
      --surface-3: #ebe1da;
      --line: rgba(15, 23, 42, 0.07);
      --line-soft: rgba(15, 23, 42, 0.04);
      --line-strong: rgba(15, 23, 42, 0.12);
      --text: #0c1222;
      --muted: #5b6b82;
      --faint: #8b97ab;
      --green: #059669;
      --blue: #ea580c;
      --blue-deep: #c2410c;
      --indigo: #f59e0b;
      --amber: #b45309;
      --red: #dc2626;
      --violet: #7c3aed;
      --cyan-glow: rgba(234, 88, 12, 0.28);
      --shadow: rgba(15, 23, 42, 0.07);
      --shadow-soft: 0 12px 36px -14px rgba(15, 23, 42, 0.10);
      --shadow-card: 0 16px 44px -18px rgba(15, 23, 42, 0.10);
      --shadow-float: 0 28px 64px -22px rgba(15, 23, 42, 0.14);
      --glow-blue: 0 0 0 1px rgba(234, 88, 12, 0.18), 0 12px 28px -8px rgba(234, 88, 12, 0.14);
      --nav-bg: rgba(238, 241, 246, 0.65);
      --nav-active-bg: linear-gradient(145deg, #e85d2a 0%, #f59e0b 100%);
      --nav-active-text: #ffffff;
      --input-bg: rgba(255, 255, 255, 0.85);
      --panel-bg: rgba(255, 255, 255, 0.72);
      --bubble-bg: transparent;
      --user-bubble-bg: linear-gradient(160deg, #ffedd5 0%, #fed7aa 100%);
      --composer-bg: transparent;
      --chat-top-bg: transparent;
      --status-card-bg: linear-gradient(165deg, rgba(255,255,255,0.92), rgba(245,238,234,0.96));
      --rail-inspector-bg: rgba(255, 255, 255, 0.82);
      --mobile-nav-bg: rgba(255, 255, 255, 0.96);
      --overlay-bg: rgba(40, 20, 12, 0.28);
      --guide-hero-bg: linear-gradient(135deg, rgba(234, 88, 12, 0.08), rgba(250, 246, 243, 0.98) 42%, rgba(245, 158, 11, 0.06));
      --feature-card-bg: rgba(255, 255, 255, 0.82);
      --project-attribution-bg: rgba(255, 247, 237, 0.92);
      --memory-card-bg: rgba(255, 255, 255, 0.78);
      --ring-card-bg: rgba(255, 255, 255, 0.78);
      --thinking-bg: linear-gradient(180deg, rgba(255, 237, 213, 0.7), rgba(254, 215, 170, 0.45));
      --rejected-bg: rgba(254, 242, 242, 0.75);
      --orb-1: rgba(234, 88, 12, 0.12);
      --orb-2: rgba(245, 158, 11, 0.10);
      --orb-3: rgba(239, 68, 68, 0.06);
      --fire-gradient: linear-gradient(145deg, #fb923c 0%, #ea580c 45%, #dc2626 100%);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      min-height: 100vh;
      background:
        radial-gradient(ellipse 900px 520px at 12% -8%, rgba(255, 122, 77, 0.11), transparent 58%),
        radial-gradient(ellipse 700px 480px at 92% 108%, rgba(245, 158, 11, 0.08), transparent 52%),
        radial-gradient(ellipse 500px 400px at 70% 20%, rgba(239, 68, 68, 0.05), transparent 55%),
        var(--bg);
      color: var(--text);
      font-family: var(--font-ui);
      font-size: 14px;
      line-height: 1.55;
      font-feature-settings: "ss01", "cv11";
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
      transition: background-color var(--dur-slow) var(--ease-out), color var(--dur-slow) var(--ease-out);
    }

    .light body,
    body.light,
    html.light body {
      background:
        radial-gradient(ellipse 900px 520px at 12% -8%, rgba(234, 88, 12, 0.08), transparent 58%),
        radial-gradient(ellipse 700px 480px at 92% 108%, rgba(245, 158, 11, 0.06), transparent 52%),
        radial-gradient(ellipse 500px 400px at 70% 20%, rgba(220, 38, 38, 0.04), transparent 55%),
        var(--bg);
    }

    button, input, textarea, select { font: inherit; }
    button, a, [role="button"] { -webkit-tap-highlight-color: transparent; touch-action: manipulation; }

    /* Premium scrollbars */
    * {
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,0.12) transparent;
    }
    .light * {
      scrollbar-color: rgba(15,23,42,0.15) transparent;
    }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.12);
      border-radius: var(--r-pill);
      border: 2px solid transparent;
      background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.20); background-clip: padding-box; }
    .light ::-webkit-scrollbar-thumb {
      background: rgba(15,23,42,0.14);
      background-clip: padding-box;
    }

    ::selection {
      background: rgba(255, 122, 77, 0.28);
      color: var(--text);
    }

    html { height: 100%; }

    /* Orb background field */
    .orb-field {
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      overflow: hidden;
    }
    .orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.6;
      animation: orbFloat 20s ease-in-out infinite;
    }
    .orb-1 {
      width: 500px;
      height: 500px;
      background: var(--orb-1);
      top: -15%;
      left: -10%;
      animation-delay: 0s;
    }
    .orb-2 {
      width: 400px;
      height: 400px;
      background: var(--orb-2);
      bottom: -15%;
      right: -10%;
      animation-delay: -7s;
    }
    .orb-3 {
      width: 350px;
      height: 350px;
      background: var(--orb-3);
      top: 50%;
      left: 60%;
      animation-delay: -14s;
    }
    @keyframes orbFloat {
      0%, 100% { transform: translate(0, 0) scale(1); }
      25% { transform: translate(30px, -20px) scale(1.05); }
      50% { transform: translate(-20px, 30px) scale(0.95); }
      75% { transform: translate(20px, 20px) scale(1.02); }
    }

    .app {
      display: grid;
      /* Explicit lengths so browsers can interpolate (vars alone often won't) */
      grid-template-columns: 268px minmax(0, 1fr) var(--inspector-width, 360px);
      grid-template-columns: var(--shell-w) minmax(0, 1fr) var(--inspector-width, 360px);
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
      position: relative;
      transition: grid-template-columns 0.4s cubic-bezier(0.32, 0.72, 0, 1);
    }

    .rail, .inspector {
      background: var(--rail-inspector-bg);
      border-color: var(--line);
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      min-width: 0; /* critical: allow grid track to shrink below content min-size */
      overflow: hidden;
      transition: background-color 0.3s, border-color 0.3s;
    }

    /* ============================================================
       LEFT RAIL — The Cognitive Spine (2026 Multimodal Redesign)
       Layered, living, premium temporal interface
       ============================================================ */
    .rail {
      display: grid;
      border-right: 1px solid rgba(255,255,255,0.05);
      grid-template-rows: auto minmax(0, 1fr) auto;
      /* Deep, rich, multi-layered glass with subtle holographic depth */
      background: 
        linear-gradient(180deg, 
          rgba(13,13,16,0.94) 0%, 
          rgba(15,15,18,0.97) 28%,
          rgba(11,11,14,0.98) 72%,
          rgba(10,10,13,0.99) 100%);
      position: relative;
      z-index: 2;
      transition: background-color 0.3s, width var(--dur-slow) var(--ease-out);
      box-shadow: 
        inset -1px 0 0 rgba(255,255,255,0.04),
        inset 0 1px 0 rgba(255,255,255,0.02),
        6px 0 40px -12px rgba(0,0,0,0.65);
      backdrop-filter: blur(24px) saturate(1.25);
    }

    .light .rail {
      background: 
        linear-gradient(180deg, 
          rgba(242,242,240,0.94) 0%, 
          rgba(248,248,246,0.97) 100%);
      box-shadow: 
        inset -1px 0 0 rgba(0,0,0,0.05),
        6px 0 40px -12px rgba(0,0,0,0.08);
    }

    /* Primary "Spine" — elegant vertical continuity element */
    .rail::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 2px;
      background: linear-gradient(
        to bottom,
        transparent 5%,
        rgba(232,93,42,0.22) 14%,
        rgba(245,158,11,0.18) 32%,
        rgba(232,93,42,0.14) 58%,
        rgba(245,158,11,0.19) 76%,
        rgba(232,93,42,0.12) 88%,
        transparent 95%
      );
      pointer-events: none;
      z-index: 1;
      opacity: 0.9;
    }

    /* Very subtle holographic rim light on the right edge of the rail */
    .rail::after {
      content: '';
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      width: 1px;
      background: linear-gradient(
        to bottom,
        transparent 10%,
        rgba(255,140,90,0.08) 25%,
        rgba(253,186,116,0.07) 55%,
        rgba(255,140,90,0.09) 80%,
        transparent 90%
      );
      pointer-events: none;
      z-index: 2;
    }

    .inspector {
      backdrop-filter: blur(20px) saturate(1.2);
    }

    .brand {
      padding: 26px 20px 20px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      position: relative;
      z-index: 2;
      background: 
        linear-gradient(180deg, 
          rgba(232,93,42,0.028) 0%, 
          rgba(245,158,11,0.018) 52%, 
          transparent 100%);
    }

    .brand-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .brand h1 {
      margin: 0;
      font-size: 21px;
      letter-spacing: -0.035em;
      line-height: 0.95;
      font-weight: 900;
      background: linear-gradient(135deg, #f8f8fc 0%, #e0e0e8 42%, #c8c8d4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      position: relative;
      font-feature-settings: "tnum";
      text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }

    .brand p {
      margin: 5px 0 0;
      color: #6f6f7a;
      font-size: 12px;
      letter-spacing: 0.015em;
      opacity: 0.8;
    }

    /* Stronger holographic spine connection on brand */
    .brand::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(
        to right,
        transparent 8%,
        rgba(255,140,90,0.28) 22%,
        rgba(253,186,116,0.22) 48%,
        rgba(255,140,90,0.26) 72%,
        transparent 92%
      );
      z-index: 3;
    }

    .settings-icon {
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: var(--r-sm);
      background: var(--nav-bg);
      color: var(--muted);
      cursor: pointer;
      transition:
        background-color var(--dur) var(--ease-spring),
        color var(--dur) var(--ease-spring),
        border-color var(--dur) var(--ease-spring),
        transform var(--dur) var(--ease-spring),
        box-shadow var(--dur) var(--ease-spring);
    }

    .settings-icon:hover,
    .settings-icon.active {
      color: var(--text);
      border-color: rgba(255, 122, 77, 0.35);
      background: var(--surface-2);
      transform: translateY(-1px);
      box-shadow: var(--glow-blue);
    }

    .theme-toggle,
    .density-toggle {
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 50%;
      background: var(--nav-bg);
      color: var(--muted);
      cursor: pointer;
      transition:
        background-color var(--dur) var(--ease-spring),
        color var(--dur) var(--ease-spring),
        border-color var(--dur) var(--ease-spring),
        transform var(--dur) var(--ease-spring),
        box-shadow var(--dur) var(--ease-spring);
    }

    .theme-toggle:hover {
      color: var(--text);
      border-color: rgba(255, 122, 77, 0.35);
      background: var(--surface-2);
      transform: rotate(-12deg) scale(1.06);
      box-shadow: var(--glow-blue);
    }

    .density-toggle:hover,
    .density-toggle.active {
      color: var(--text);
      border-color: rgba(255, 122, 77, 0.35);
      background: var(--surface-2);
      box-shadow: var(--glow-blue);
    }

    .density-toggle.active {
      color: var(--blue);
      background: rgba(255, 122, 77, 0.10);
    }

    .theme-toggle svg,
    .density-toggle svg {
      width: 18px;
      height: 18px;
    }

    .rail-section {
      padding: 18px 18px 22px;
      display: grid;
      gap: 22px;
      align-content: start;
      overflow: auto;
    }

    /* Elegant section grouping with better breathing and subtle separation */
    .group {
      display: grid;
      gap: 8px;
      position: relative;
    }

    .group + .group::before {
      content: '';
      position: absolute;
      top: -11px;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(
        to right,
        transparent,
        rgba(255,255,255,0.035),
        transparent
      );
    }

    /* Vertical shell nav — same list language as sessions */
    .nav {
      display: flex;
      flex-direction: column;
      gap: var(--shell-gap);
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      width: 100%;
      overflow: visible;
      box-shadow: none;
      position: relative;
    }

    .nav button {
      min-height: var(--shell-item-h);
      border: 0;
      border-radius: var(--shell-radius);
      background: transparent;
      color: var(--shell-muted);
      cursor: pointer;
      font-weight: 600;
      font-size: 13px;
      letter-spacing: -0.01em;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 10px;
      padding: 0 11px;
      position: relative;
      z-index: 1;
      width: 100%;
      transition:
        color var(--dur) var(--ease-out),
        background var(--dur) var(--ease-out),
        box-shadow var(--dur) var(--ease-out);
      overflow: hidden;
    }

    .nav button:hover {
      color: var(--text);
      background: var(--shell-fill-hover);
    }

    .nav button.active {
      color: var(--text);
      background: var(--shell-fill-active);
      font-weight: 650;
      box-shadow: inset 2px 0 0 var(--shell-edge);
    }

    .nav button.active::before {
      display: none;
    }

    .nav button svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
      position: relative;
      z-index: 1;
      opacity: 0.85;
      transition: opacity var(--dur) var(--ease-out), filter var(--dur) var(--ease-out);
    }

    .nav button:hover svg,
    .nav button.active svg {
      opacity: 1;
    }

    .nav button.active svg {
      filter: drop-shadow(0 0 6px rgba(255, 122, 77, 0.35));
    }

    .nav-label {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      opacity: 1;
      max-width: 160px;
      transition:
        opacity 0.22s var(--shell-ease, ease),
        max-width var(--shell-dur, 0.42s) var(--shell-ease, ease),
        margin var(--shell-dur, 0.42s) var(--shell-ease, ease);
    }

    label {
      color: #6f6f7a;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-top: 2px;
    }

    .rail-section label:first-child,
    .group label:first-child {
      margin-top: 0;
      color: #8a8a96;
    }

    /* More premium selects and inputs inside the rail */
    .rail select,
    .rail input {
      height: 38px;
      font-size: 13.5px;
      border-radius: 9px;
      background: rgba(10,10,12,0.7);
      border: 1px solid rgba(255,255,255,0.07);
      color: #e8e8ee;
      transition: border-color 0.15s, box-shadow 0.15s;
    }

    .rail select:focus,
    .rail input:focus {
      border-color: rgba(232,93,42,0.4);
      box-shadow: 0 0 0 3px rgba(232,93,42,0.1);
      outline: none;
    }

    input, select, textarea {
      width: 100%;
      color: var(--text);
      background: var(--input-bg);
      border: 1px solid var(--line);
      border-radius: var(--r-sm);
      outline: none;
      transition:
        background-color var(--dur) var(--ease-out),
        border-color var(--dur) var(--ease-out),
        box-shadow var(--dur) var(--ease-out),
        color var(--dur) var(--ease-out);
    }

    input, select {
      height: 40px;
      padding: 0 12px;
    }

    /* Dark-native dropdowns: avoid white flash / OS light menu */
    select {
      color-scheme: dark;
      accent-color: var(--blue-deep);
      cursor: pointer;
      /* Opaque fill — transparent shells often invert on hover in Chromium */
      background-color: var(--surface-2);
      background-image: linear-gradient(45deg, transparent 50%, var(--muted) 50%),
                        linear-gradient(135deg, var(--muted) 50%, transparent 50%);
      background-position: calc(100% - 16px) calc(50% - 2px), calc(100% - 11px) calc(50% - 2px);
      background-size: 5px 5px, 5px 5px;
      background-repeat: no-repeat;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      padding-right: 28px;
    }
    select:hover {
      color: var(--text);
      background-color: var(--surface-3);
      border-color: var(--line-strong);
    }
    select:focus {
      color: var(--text);
      background-color: var(--surface-3);
    }
    select:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
    option,
    optgroup {
      color-scheme: dark;
      background-color: #0c1017;
      color: #eef1f7;
    }
    option:checked {
      background-color: #15324a;
      color: #f2f4f8;
    }
    option:hover,
    option:focus {
      background-color: #1a2230;
      color: #ffffff;
    }
    .light select {
      color-scheme: light;
      background-color: #ffffff;
      background-image: linear-gradient(45deg, transparent 50%, #64748b 50%),
                        linear-gradient(135deg, #64748b 50%, transparent 50%);
      background-position: calc(100% - 16px) calc(50% - 2px), calc(100% - 11px) calc(50% - 2px);
      background-size: 5px 5px, 5px 5px;
      background-repeat: no-repeat;
    }
    .light select:hover,
    .light select:focus {
      background-color: #f1f5f9;
      color: var(--text);
    }
    .light option,
    .light optgroup {
      color-scheme: light;
      background-color: #ffffff;
      color: #0c1222;
    }
    .light option:checked {
      background-color: #e0f2fe;
      color: #0c1222;
    }

    textarea {
      resize: vertical;
      min-height: 54px;
      max-height: 140px;
      padding: 12px 14px;
      line-height: 1.5;
    }

    input::placeholder, textarea::placeholder {
      color: var(--faint);
      opacity: 0.9;
    }

    input:focus, select:focus, textarea:focus {
      border-color: rgba(255, 122, 77, 0.45);
      box-shadow: 0 0 0 3px rgba(255, 122, 77, 0.12);
    }

    .hint {
      color: var(--faint);
      font-size: 11.5px;
      line-height: 1.45;
    }

    .status-card {
      margin: 8px 14px 14px;
      padding: 13px 15px;
      border: 1px solid var(--line);
      border-radius: var(--r-md);
      background: var(--status-card-bg);
      color: var(--muted);
      font-size: 12.5px;
      line-height: 1.45;
      transition: background-color var(--dur) var(--ease-out), border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
      backdrop-filter: blur(12px) saturate(1.15);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .status-card:hover {
      border-color: var(--line-strong);
      box-shadow: var(--shadow-soft);
    }

    .inline-field {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
    }

    .inline-field button {
      min-width: 58px;
      min-height: 36px;
    }

    .chat {
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr) auto;
      min-width: 0;
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
      position: relative;
      contain: layout paint;
    }

    .chat.hidden {
      display: none;
    }

    .guide {
      display: none;
      min-width: 0;
      min-height: 100vh;
      overflow: auto;
      padding: 30px;
    }

    .guide.active {
      display: block;
    }

    .settings {
      display: none;
      min-width: 0;
      height: 100vh;
      height: 100dvh;
      overflow: auto;
      padding: 30px;
    }

    .settings.active {
      display: block;
    }

    .settings-form {
      display: grid;
      gap: 18px;
    }

    .settings-tabs {
      display: inline-flex;
      gap: 3px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: var(--r-pill);
      background: var(--nav-bg);
      backdrop-filter: blur(14px) saturate(1.15);
      width: fit-content;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .settings-tabs button {
      min-height: 34px;
      border: 0;
      border-radius: var(--r-pill);
      padding: 0 15px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-weight: 650;
      font-size: 12.5px;
      transition: background-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }

    .settings-tabs button:hover {
      color: var(--text);
      background: rgba(255,255,255,0.04);
    }

    .settings-tabs button.active {
      background: linear-gradient(145deg, rgba(255, 122, 77, 0.18), rgba(245, 158, 11, 0.14));
      color: var(--blue);
      box-shadow: 0 0 0 1px rgba(255, 122, 77, 0.22), inset 0 1px 0 rgba(255,255,255,0.08);
      font-weight: 700;
    }

    .settings-section.hidden {
      display: none;
    }

    .settings-row {
      display: grid;
      grid-template-columns: 220px 1fr;
      gap: 18px;
    }

    @media (max-width: 640px) {
      .settings-row {
        grid-template-columns: 1fr;
      }
    }

    .settings-field {
      display: grid;
      gap: 6px;
    }

    .settings-field label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .settings-divider {
      font-size: 11px;
      font-weight: 700;
      color: #888;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin: 16px 0 6px;
      padding-top: 10px;
      border-top: 1px solid rgba(255,255,255,0.06);
    }

    /* Provider sub-tabs (Chat / Image / Video) */
    .provider-subtabs {
      display: inline-flex;
      background: #111;
      border: 1px solid #222;
      border-radius: 999px;
      padding: 3px;
      margin-bottom: 14px;
      gap: 2px;
    }

    .provider-subtab {
      padding: 6px 18px;
      border-radius: 999px;
      border: none;
      background: transparent;
      color: #888;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all .15s ease;
      white-space: nowrap;
    }

    .provider-subtab:hover {
      color: #ddd;
    }

    .provider-subtab.active {
      background: linear-gradient(135deg, #e85d2a, #f97316);
      color: #fff;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(232,93,42,0.35);
    }

    .provider-subsection {
      display: block;
    }

    .provider-subsection.hidden {
      display: none;
    }

    .provider-effective-summary {
      margin-top: 18px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 10px;
    }

    .summary-title {
      font-size: 11px;
      font-weight: 700;
      color: #888;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    .summary-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      padding: 4px 0;
    }

    .summary-label {
      color: #777;
      font-weight: 600;
    }

    .summary-value {
      color: #ddd;
      font-weight: 600;
      text-align: right;
      max-width: 65%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .summary-note {
      margin-top: 10px;
      font-size: 11px;
      color: #666;
      line-height: 1.4;
    }

    .settings-status-panel {
      margin-top: 4px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--status-card-bg);
      display: grid;
      gap: 6px;
      transition: background-color 0.3s;
    }

    .status-header {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .status-indicator {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--faint);
      box-shadow: 0 0 0 2px rgba(82, 82, 82, 0.25);
      transition: background 0.2s, box-shadow 0.2s;
      flex-shrink: 0;
    }

    .status-indicator.ok {
      background: var(--green);
      box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);
    }

    .status-indicator.warn {
      background: var(--amber);
      box-shadow: 0 0 0 2px rgba(214, 179, 106, 0.25);
    }

    .status-indicator.error {
      background: var(--red);
      box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.25);
    }

    .status-label {
      color: var(--text);
      font-size: 14px;
      font-weight: 700;
    }

    .status-detail {
      color: var(--faint);
      font-size: 12px;
      padding-left: 20px;
    }

    .guide-shell {
      max-width: 1180px;
      margin: 0 auto;
      display: grid;
      gap: 18px;
    }

    .guide-hero {
      border: 1px solid var(--line);
      border-radius: var(--r-xl);
      padding: 28px 30px;
      background: var(--guide-hero-bg);
      box-shadow: var(--shadow-card);
      transition: background-color var(--dur-slow) var(--ease-out), box-shadow var(--dur) var(--ease-out);
      position: relative;
      overflow: hidden;
    }

    .guide-hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 100% 0%, rgba(255, 122, 77, 0.08), transparent 50%);
      pointer-events: none;
    }

    .guide-hero h2 {
      margin: 0;
      font-size: 30px;
      font-weight: 750;
      letter-spacing: -0.035em;
      position: relative;
    }

    .guide-hero p {
      max-width: 760px;
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
      position: relative;
    }

    .guide-controls {
      display: inline-flex;
      gap: 3px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: var(--r-pill);
      background: var(--nav-bg);
      backdrop-filter: blur(14px);
      position: relative;
      margin-bottom: 14px;
    }

    .guide-controls button {
      border: 0;
      border-radius: var(--r-pill);
      min-height: 34px;
      padding: 0 15px;
      color: var(--muted);
      background: transparent;
      cursor: pointer;
      font-weight: 650;
      font-size: 12.5px;
      transition: background-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }

    .guide-controls button.active {
      color: #ffffff;
      background: var(--fire-gradient);
      box-shadow: 0 4px 14px -2px rgba(232, 93, 42, 0.40);
      font-weight: 700;
    }

    .feature-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }

    .feature-card {
      border: 1px solid var(--line);
      border-radius: var(--r-lg);
      background: var(--feature-card-bg);
      backdrop-filter: blur(16px) saturate(1.1);
      padding: 18px 18px 16px;
      transition:
        background-color var(--dur-slow) var(--ease-out),
        transform var(--dur) var(--ease-spring),
        box-shadow var(--dur) var(--ease-out),
        border-color var(--dur) var(--ease-out);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .feature-card:hover {
      transform: translateY(-3px);
      box-shadow: var(--shadow-card);
      border-color: rgba(255, 122, 77, 0.22);
    }

    .feature-card h3 {
      margin: 0 0 10px;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .feature-card p {
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
    }

    .feature-card ul {
      margin: 10px 0 0;
      padding-left: 18px;
      color: var(--muted);
    }

    .feature-card li + li {
      margin-top: 6px;
    }

    .feature-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }

    .project-attribution {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--project-attribution-bg);
      padding: 16px;
      color: var(--muted);
      transition: background-color 0.3s;
    }

    .project-attribution h3 {
      margin: 0 0 8px;
      color: var(--text);
      font-size: 16px;
      letter-spacing: -0.01em;
    }

    .project-attribution p {
      margin: 0;
    }

    .project-attribution p + p {
      margin-top: 10px;
    }

    .project-attribution a {
      color: var(--blue);
      font-weight: 700;
      text-decoration: none;
    }

    .project-attribution a:hover {
      text-decoration: underline;
    }

    .simple-only.hidden, .comprehensive-only.hidden {
      display: none;
    }

    .hidden {
      display: none !important;
    }

    .chat-top {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line-soft);
      background: var(--chat-top-bg);
      backdrop-filter: blur(20px) saturate(1.25);
      transition: background-color var(--dur-slow) var(--ease-out);
      box-shadow: 0 1px 0 rgba(255,255,255,0.02);
    }

    .chat-title {
      min-width: 0;
      flex: 1 1 auto;
    }

    .chat-title strong {
      display: block;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .chat-title span {
      display: block;
      color: var(--muted);
      font-size: 12.5px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-top: 2px;
    }

    .badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
      min-width: 0;
    }

    .badge {
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.03);
      color: var(--muted);
      border-radius: var(--r-pill);
      padding: 5px 11px;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
      letter-spacing: 0.01em;
      backdrop-filter: blur(8px);
      transition: border-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), background var(--dur) var(--ease-out);
    }

    .badge.ok { color: var(--green); border-color: rgba(52, 211, 153, 0.28); background: rgba(52, 211, 153, 0.08); }
    .badge.warn { color: var(--amber); border-color: rgba(224, 179, 90, 0.30); background: rgba(224, 179, 90, 0.08); }
    .badge.info { color: var(--blue); border-color: rgba(255, 122, 77, 0.30); background: rgba(255, 122, 77, 0.08); }
    .badge.bad { color: var(--red); border-color: rgba(248, 113, 113, 0.30); background: rgba(248, 113, 113, 0.08); }
    .trust-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      align-items: center;
      padding: 6px 16px 8px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.12);
      background: rgba(15, 23, 42, 0.45);
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 0.01em;
    }
    .trust-item {
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }
    .trust-strip.ok .trust-item#trust-verify { color: var(--green); }
    .trust-strip.bad .trust-item#trust-verify { color: var(--red); }
    .message.streaming .bubble-content { opacity: 0.95; }
    .message.streaming .bubble-meta::after { content: " streaming…"; color: var(--blue); }
    .citation-box {
      margin-top: 8px;
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid rgba(255, 122, 77, 0.22);
      background: rgba(255, 122, 77, 0.06);
      font-size: 12px;
      color: var(--muted);
    }
    .citation-box strong { color: var(--text); }
    .command-palette-backdrop {
      position: fixed; inset: 0; z-index: 1200;
      background: rgba(2, 6, 23, 0.55);
      display: none; align-items: flex-start; justify-content: center;
      padding-top: min(18vh, 140px);
    }
    .command-palette-backdrop.open { display: flex; }
    .command-palette {
      width: min(560px, 92vw);
      background: var(--panel, #0f172a);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 14px;
      box-shadow: 0 24px 60px rgba(0,0,0,0.45);
      overflow: hidden;
    }
    .command-palette input {
      width: 100%;
      border: 0;
      outline: none;
      background: transparent;
      color: var(--text);
      font-size: 15px;
      padding: 14px 16px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    }
    .command-palette-list { max-height: 320px; overflow: auto; padding: 6px; }
    .command-palette-item {
      display: flex; justify-content: space-between; gap: 12px;
      padding: 10px 12px; border-radius: 10px; cursor: pointer;
      color: var(--text); font-size: 13px;
    }
    .command-palette-item:hover,
    .command-palette-item.active { background: rgba(255, 122, 77, 0.12); }
    .command-palette-item .hint { color: var(--muted); font-size: 11px; }
    .command-palette-hint {
      padding: 8px 14px 12px; font-size: 11px; color: var(--muted);
      border-top: 1px solid rgba(148, 163, 184, 0.12);
    }

    .messages {
      overflow: auto;
      min-height: 0;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      scroll-behavior: smooth;
    }

    .empty {
      margin: auto;
      width: min(560px, 100%);
      color: var(--muted);
      text-align: center;
      display: grid;
      gap: 14px;
      padding: 32px 20px;
      border-radius: var(--r-xl);
      background:
        radial-gradient(ellipse at 50% 0%, rgba(255, 122, 77, 0.08), transparent 60%),
        rgba(255,255,255,0.015);
      border: 1px solid var(--line-soft);
    }

    .empty h2 {
      margin: 0;
      color: var(--text);
      font-size: 26px;
      font-weight: 750;
      letter-spacing: -0.03em;
      line-height: 1.2;
    }

    .empty p {
      margin: 0;
      font-size: 14.5px;
      line-height: 1.6;
      color: var(--muted);
      max-width: 42ch;
      margin-inline: auto;
    }

    .message {
      display: grid;
      grid-template-columns: 40px minmax(0, 1fr);
      gap: 12px;
      max-width: 920px;
      width: 100%;
      animation: msgIn 0.35s var(--ease-out) both;
    }

    @keyframes msgIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message.user {
      align-self: flex-end;
      grid-template-columns: minmax(0, 1fr) 40px;
    }

    .avatar {
      width: 40px;
      height: 40px;
      display: grid;
      place-items: center;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: linear-gradient(145deg, var(--surface-2), var(--surface));
      color: var(--green);
      font-weight: 800;
      font-size: 13px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .message.user .avatar {
      grid-column: 2;
      color: var(--blue);
      background: linear-gradient(145deg, rgba(232, 93, 42, 0.18), rgba(245, 158, 11, 0.12));
      border-color: rgba(255, 122, 77, 0.22);
    }

    .bubble {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: var(--r-lg);
      background: var(--bubble-bg);
      backdrop-filter: blur(16px) saturate(1.15);
      box-shadow: var(--shadow-card);
      overflow: hidden;
      transition: background-color var(--dur-slow) var(--ease-out), border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }

    .message.user .bubble {
      grid-column: 1;
      grid-row: 1;
      background: var(--user-bubble-bg);
      border-color: rgba(255, 122, 77, 0.28);
      box-shadow: var(--shadow-card), 0 0 0 1px rgba(255, 122, 77, 0.06) inset;
    }

    .light .message.user .bubble {
      border-color: #ffc4a8;
    }

    .message.rejected .bubble {
      background: var(--rejected-bg);
      border-color: var(--red);
    }

    .message.thinking-message .bubble {
      border-color: rgba(232, 93, 42, 0.4);
      background: var(--thinking-bg);
    }

    .light .message.thinking-message .bubble {
      border-color: #ffc4a8;
    }

    /* Auth overlay */
    .auth-overlay {
      position: fixed;
      inset: 0;
      z-index: 200;
      display: grid;
      place-items: center;
      backdrop-filter: blur(24px) saturate(1.4);
      background:
        radial-gradient(circle at 20% 30%, rgba(232, 93, 42, 0.10), transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(34, 197, 94, 0.08), transparent 50%),
        rgba(5, 5, 5, 0.92);
      transition: opacity 0.35s ease, visibility 0.35s ease;
    }
    .light .auth-overlay {
      background:
        radial-gradient(circle at 20% 30%, rgba(232, 93, 42, 0.06), transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(34, 197, 94, 0.04), transparent 50%),
        rgba(247, 247, 245, 0.92);
    }
    .auth-overlay.hidden {
      opacity: 0;
      pointer-events: none;
      visibility: hidden;
    }
    .auth-card {
      width: min(420px, 92vw);
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(165deg, rgba(18, 22, 32, 0.98), rgba(12, 15, 22, 0.99));
      padding: 40px 34px;
      display: grid;
      gap: 18px;
      box-shadow:
        var(--shadow-float),
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 0 80px -20px rgba(255, 122, 77, 0.15);
      animation: authEnter 0.55s var(--ease-out);
      backdrop-filter: blur(24px);
    }

    .light .auth-card {
      background: linear-gradient(165deg, #ffffff, #f8fafc);
    }
    @keyframes authEnter {
      from { opacity: 0; transform: translateY(28px) scale(0.98); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .brand-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }
    .auth-logo {
      width: 52px;
      height: 52px;
      border-radius: 16px;
      background: var(--fire-gradient);
      display: grid;
      place-items: center;
      font-size: 24px;
      font-weight: 900;
      color: #ffffff;
      margin: 0 auto;
      box-shadow: 0 10px 28px rgba(232, 93, 42, 0.35), inset 0 1px 0 rgba(255,255,255,0.25);
    }
    .auth-card h2 { margin: 0; font-size: 24px; font-weight: 750; text-align: center; letter-spacing: -0.03em; }
    .auth-card .subtitle { margin: -6px 0 0; color: var(--muted); font-size: 14px; text-align: center; line-height: 1.5; }
    .auth-tabs {
      display: inline-flex;
      gap: 0;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.03);
      overflow: hidden;
      padding: 4px;
      width: 100%;
    }
    .auth-tabs button {
      flex: 1;
      min-height: 38px;
      border: 0;
      border-radius: 11px;
      background: transparent;
      color: var(--muted);
      font-weight: 650;
      cursor: pointer;
      font-size: 13.5px;
      transition: background-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }
    .auth-tabs button.active {
      color: #ffffff;
      background: var(--fire-gradient);
      box-shadow: 0 4px 14px -2px rgba(232, 93, 42, 0.40);
      font-weight: 700;
    }
    .auth-field { display: grid; gap: 8px; }
    .auth-field label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }
    .auth-field input {
      height: 46px;
      padding: 0 15px;
      border-radius: 12px;
      font-size: 14.5px;
      background: var(--input-bg);
    }
    .auth-submit {
      min-height: 50px;
      border-radius: 14px;
      border: 0;
      color: #ffffff;
      background: var(--fire-gradient);
      cursor: pointer;
      font-weight: 750;
      font-size: 15px;
      letter-spacing: -0.01em;
      box-shadow: 0 8px 24px -4px rgba(232, 93, 42, 0.45);
      transition: transform var(--dur-fast) var(--ease-spring), box-shadow var(--dur) var(--ease-out), filter var(--dur) var(--ease-out);
    }
    .auth-submit:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 32px -4px rgba(232, 93, 42, 0.55);
      filter: brightness(1.04);
    }
    .auth-submit:active {
      transform: translateY(0);
    }
    .auth-hint { color: var(--faint); font-size: 13px; text-align: center; min-height: 20px; }

    /* Account dropdown */
    .account-wrap {
      position: relative;
    }
    .brand > .account-wrap {
      margin-top: 10px;
    }
    .brand > .account-wrap .account-btn {
      width: 100%;
      justify-content: flex-start;
    }
    .brand > .account-wrap .account-menu {
      top: 38px;
      right: 0;
      left: 0;
      min-width: unset;
    }
    .account-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 0 13px;
      height: 36px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.06);
      background: rgba(255,255,255,0.025);
      color: #d4d4dc;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.23,1,0.32,1);
    }
    .account-btn:hover {
      background: rgba(255,255,255,0.05);
      border-color: rgba(255,140,90,0.25);
      color: #f4f4f8;
    }
    .account-menu {
      position: absolute;
      right: 0;
      top: 42px;
      min-width: 180px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--surface);
      box-shadow: 0 12px 36px var(--shadow);
      display: none;
      z-index: 50;
      overflow: hidden;
    }
    .account-menu.open { display: block; }
    .account-menu button {
      width: 100%;
      text-align: left;
      padding: 10px 14px;
      border: 0;
      background: transparent;
      color: var(--text);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }
    .account-menu button:hover { background: var(--surface-2); }
    .account-menu .account-role {
      padding: 8px 14px;
      color: var(--blue);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      border-bottom: 1px solid var(--line-soft);
    }

    /* Marketplace */
    .marketplace {
      display: none;
      min-width: 0;
      min-height: 100vh;
      overflow: auto;
      padding: 32px;
    }
    .marketplace.active { display: block; }
    .marketplace-hero {
      border: 1px solid var(--line);
      border-radius: var(--r-xl);
      padding: 28px 30px;
      background: var(--guide-hero-bg);
      box-shadow: var(--shadow-card);
      margin-bottom: 22px;
      position: relative;
      overflow: hidden;
    }
    .marketplace-hero::after {
      content: '';
      position: absolute;
      right: -40px;
      top: -40px;
      width: 180px;
      height: 180px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,122,77,0.12), transparent 70%);
      pointer-events: none;
    }
    .marketplace-hero h2 { margin: 0; font-size: 28px; font-weight: 750; letter-spacing: -0.035em; position: relative; }
    .marketplace-hero p { margin: 10px 0 0; color: var(--muted); font-size: 15px; line-height: 1.55; position: relative; max-width: 52ch; }
    .marketplace-filters {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 20px;
      align-items: center;
    }
    .marketplace-filters input {
      flex: 1 1 240px;
      min-width: 180px;
      height: 42px;
      border-radius: var(--r-pill);
      padding: 0 16px;
    }
    .filter-pill {
      min-height: 36px;
      padding: 0 15px;
      border-radius: var(--r-pill);
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.02);
      color: var(--muted);
      font-weight: 650;
      font-size: 12.5px;
      cursor: pointer;
      transition: background-color var(--dur) var(--ease-out), color var(--dur) var(--ease-out), border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out), transform var(--dur-fast) var(--ease-spring);
    }
    .filter-pill:hover {
      background: var(--surface-2);
      color: var(--text);
      transform: translateY(-1px);
    }
    .filter-pill.active {
      color: #ffffff;
      background: var(--fire-gradient);
      border-color: transparent;
      box-shadow: 0 4px 14px -2px rgba(232, 93, 42, 0.40);
      font-weight: 700;
    }
    .marketplace-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
      gap: 18px;
    }
    .persona-card {
      border: 1px solid var(--line);
      border-radius: var(--r-lg);
      background: var(--feature-card-bg);
      backdrop-filter: blur(16px) saturate(1.1);
      padding: 18px;
      display: grid;
      gap: 11px;
      cursor: pointer;
      position: relative;
      isolation: isolate;
      overflow: hidden;
      transition:
        transform var(--dur) var(--ease-spring),
        box-shadow var(--dur) var(--ease-out),
        border-color var(--dur) var(--ease-out),
        background var(--dur) var(--ease-out);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
      animation: cardIn 0.42s var(--ease-out) both;
      animation-delay: calc(var(--stagger, 0) * 45ms);
    }
    .persona-card::before {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: linear-gradient(135deg, rgba(255,122,77,0.10), transparent 42%, rgba(251,146,60,0.08));
      opacity: 0;
      transition: opacity var(--dur) var(--ease-out);
      z-index: 0;
      pointer-events: none;
    }
    .persona-card::after {
      content: '';
      position: absolute;
      top: -40%;
      left: -60%;
      width: 48%;
      height: 180%;
      background: linear-gradient(100deg, transparent, rgba(255,255,255,0.10), transparent);
      transform: translateX(-20%) rotate(18deg);
      transition: transform 0.55s var(--ease-out);
      pointer-events: none;
      z-index: 1;
    }
    .persona-card > * {
      position: relative;
      z-index: 2;
    }
    .persona-card:hover {
      transform: translateY(-5px) scale(1.01);
      box-shadow: var(--shadow-card), 0 0 0 1px rgba(255, 122, 77, 0.12);
      border-color: rgba(255, 122, 77, 0.32);
    }
    .persona-card:hover::before { opacity: 1; }
    .persona-card:hover::after {
      transform: translateX(280%) rotate(18deg);
    }
    .persona-card:active {
      transform: translateY(-1px) scale(0.99);
      transition-duration: 0.08s;
    }
    .persona-card:focus-visible {
      outline: none;
      border-color: rgba(255, 122, 77, 0.5);
      box-shadow: var(--glow-blue);
    }
    @keyframes cardIn {
      from { opacity: 0; transform: translateY(12px) scale(0.98); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .persona-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }
    .domain-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 800;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .domain-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--blue);
    }
    .price-badge {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
    }
    .price-badge.free { background: rgba(34, 197, 94, 0.14); color: var(--green); }
    .price-badge.premium { background: rgba(232, 93, 42, 0.14); color: var(--blue); }
    .persona-card h3 { margin: 0; font-size: 17px; letter-spacing: -0.01em; }
    .persona-card .tagline {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      min-height: 38px;
    }
    .persona-card-meta {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      font-size: 12px;
      color: var(--faint);
    }
    .persona-card-meta span {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* Detail drawer */
    .detail-drawer {
      position: fixed;
      right: 0;
      top: 0;
      bottom: 0;
      width: min(420px, 90vw);
      z-index: 150;
      background: var(--rail-inspector-bg);
      backdrop-filter: blur(24px) saturate(1.2);
      border-left: 1px solid var(--line);
      transform: translateX(101%);
      transition: transform 0.3s ease;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      overflow: hidden;
    }
    .detail-drawer.open {
      transform: translateX(0);
    }
    .detail-drawer-head {
      padding: 18px;
      border-bottom: 1px solid var(--line-soft);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }
    .detail-drawer-head h2 { margin: 0; font-size: 20px; letter-spacing: -0.01em; }
    .detail-drawer-body {
      overflow: auto;
      padding: 18px;
      display: grid;
      gap: 16px;
      align-content: start;
    }
    .detail-drawer-foot {
      padding: 14px 18px;
      border-top: 1px solid var(--line-soft);
      display: grid;
      gap: 8px;
    }
    .temporal-mass-bar {
      height: 6px;
      border-radius: 999px;
      background: var(--surface-3);
      overflow: hidden;
    }
    .temporal-mass-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--green), var(--blue));
      transition: width 0.6s ease;
    }

    /* Creator tab */
    .creator-persona-list {
      display: grid;
      gap: 10px;
    }
    .creator-persona-row {
      display: grid;
      grid-template-columns: 1fr auto auto auto;
      gap: 8px;
      align-items: center;
      padding: 10px 12px;
      border: 1px solid var(--line-soft);
      border-radius: 10px;
      background: var(--memory-card-bg);
    }
    .creator-persona-row .status {
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
    }
    .status-draft { background: rgba(143, 179, 255, 0.12); color: var(--blue); }
    .status-pending { background: rgba(232, 93, 42, 0.12); color: var(--blue); }
    .status-published { background: rgba(34, 197, 94, 0.12); color: var(--green); }
    .status-archived { background: rgba(82, 82, 82, 0.12); color: var(--faint); }

    .thinking-row {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      color: var(--muted);
      font-weight: 700;
    }

    .thinking-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--blue);
      animation: thinkingPulse 1s ease-in-out infinite;
    }

    .thinking-dot:nth-child(2) { animation-delay: 0.14s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.28s; }

    @keyframes thinkingPulse {
      0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }
      40% { opacity: 1; transform: translateY(-3px); }
    }

    .bubble-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-bottom: 1px solid var(--line-soft);
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
      background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.008));
    }

    .bubble-content {
      padding: 14px 16px;
      overflow-wrap: anywhere;
      font-size: 15px;
      line-height: 1.62;
      white-space: pre-wrap;
      letter-spacing: -0.005em;
    }

    .text-segment {
      display: inline;
    }

    .thought-segment {
      display: inline;
      color: var(--faint);
      font-style: italic;
      opacity: 0.88;
    }

    .bubble-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      padding: 0 12px 12px;
    }

    .composer {
      padding: 14px 24px 22px;
      border-top: 1px solid var(--line-soft);
      background: var(--composer-bg);
      backdrop-filter: blur(22px) saturate(1.25);
      transition: background-color var(--dur-slow) var(--ease-out);
    }

    .composer-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      max-width: 920px;
      margin: 0 auto;
      align-items: end;
      padding: 10px 10px 10px 14px;
      border: 1px solid var(--line);
      border-radius: var(--r-xl);
      background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
      box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.04);
      transition: border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }

    .composer-form:focus-within {
      border-color: rgba(255, 122, 77, 0.35);
      box-shadow: var(--glow-blue), var(--shadow-soft);
    }

    .composer-form textarea {
      border: 0;
      background: transparent;
      box-shadow: none;
      min-height: 48px;
      max-height: 160px;
      padding: 10px 4px;
      font-size: 15px;
      line-height: 1.5;
      resize: none;
    }

    .composer-form textarea:focus {
      border: 0;
      box-shadow: none;
    }

    .send {
      width: 48px;
      min-height: 48px;
      border-radius: 14px;
      border: 0;
      color: #ffffff;
      background: var(--fire-gradient);
      cursor: pointer;
      font-size: 18px;
      font-weight: 800;
      box-shadow: 0 6px 20px -4px rgba(232, 93, 42, 0.45);
      transition: transform var(--dur-fast) var(--ease-spring), box-shadow var(--dur) var(--ease-out), filter var(--dur) var(--ease-out);
    }

    .send:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 10px 28px -4px rgba(232, 93, 42, 0.55);
      filter: brightness(1.05);
    }

    .send:active {
      transform: translateY(0) scale(0.98);
    }

    .send:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
      filter: grayscale(0.2);
    }

    .composer-warning {
      display: none;
      max-width: 920px;
      margin: 0 auto 12px;
      padding: 12px 14px;
      border: 1px solid rgba(224, 179, 90, 0.35);
      border-radius: var(--r-md);
      background: rgba(224, 179, 90, 0.10);
      color: var(--amber);
      font-size: 13px;
      line-height: 1.5;
    }
    .composer-warning.active {
      display: block;
    }

    .composer-options {
      max-width: 920px;
      margin: 0 auto 10px;
      display: flex;
      gap: 14px;
      align-items: center;
      flex-wrap: wrap;
      padding: 0 4px;
    }

    .composer-option {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--muted);
      cursor: pointer;
      user-select: none;
      transition: color var(--dur) var(--ease-out);
    }

    .composer-option:hover {
      color: var(--text);
    }

    .composer-option input[type="checkbox"] {
      width: 16px;
      height: 16px;
      accent-color: var(--blue-deep);
      cursor: pointer;
    }

    .send svg {
      display: block;
      margin: 0 auto;
    }

    .inspector {
      border-left: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
    }

    .inspector-head {
      padding: 16px;
      border-bottom: 1px solid var(--line-soft);
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 8px;
    }
    .inspector-head-text {
      flex: 1;
      min-width: 0;
    }

    .inspector-head strong {
      display: block;
      font-size: 15px;
      letter-spacing: -0.01em;
    }

    .inspector-head span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 13px;
    }

    .inspector-body {
      overflow: auto;
      padding: 14px;
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: var(--r-md);
      background: var(--panel-bg);
      backdrop-filter: blur(16px) saturate(1.1);
      overflow: hidden;
      transition: background-color var(--dur-slow) var(--ease-out), border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.025);
    }

    .panel:hover {
      border-color: var(--line-strong);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 13px 14px;
      cursor: pointer;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      transition: background var(--dur) var(--ease-out);
    }

    .panel-header:hover {
      background: rgba(255,255,255,0.03);
    }

    .panel-header h2 {
      margin: 0;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .panel-chevron {
      width: 16px;
      height: 16px;
      color: var(--faint);
      transition: transform 0.25s ease;
      flex-shrink: 0;
    }

    .panel.expanded .panel-chevron {
      transform: rotate(180deg);
    }

    .panel-body {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease, padding 0.3s ease;
      padding: 0 12px;
    }

    .panel.expanded .panel-body {
      max-height: 2000px;
      padding: 0 12px 12px;
    }

    dl {
      display: grid;
      grid-template-columns: 112px minmax(0, 1fr);
      gap: 7px 10px;
      margin: 0;
    }

    dt { color: var(--muted); }
    dd { margin: 0; overflow-wrap: anywhere; }

    .stack {
      display: grid;
      gap: 8px;
    }

    .secondary {
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: var(--r-sm);
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.015));
      color: var(--text);
      cursor: pointer;
      font-weight: 650;
      font-size: 13px;
      letter-spacing: -0.01em;
      padding: 0 14px;
      transition:
        background-color var(--dur) var(--ease-out),
        border-color var(--dur) var(--ease-out),
        transform var(--dur-fast) var(--ease-spring),
        box-shadow var(--dur) var(--ease-out);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .secondary:hover {
      background: var(--surface-3);
      border-color: rgba(255, 122, 77, 0.35);
      transform: translateY(-1px);
      box-shadow: var(--shadow-soft);
    }

    .secondary:active {
      transform: translateY(0);
    }

    .secondary.danger {
      border-color: rgba(248, 113, 113, 0.35);
      color: #fca5a5;
      background: rgba(91, 36, 34, 0.28);
    }

    .secondary.danger:hover {
      border-color: var(--red);
      background: rgba(91, 36, 34, 0.42);
    }

    .secondary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    button.primary,
    .primary {
      min-height: 42px;
      border: 0;
      border-radius: var(--r-sm);
      padding: 0 18px;
      color: #ffffff;
      background: var(--fire-gradient);
      cursor: pointer;
      font-weight: 700;
      font-size: 13.5px;
      letter-spacing: -0.01em;
      box-shadow: 0 6px 18px -4px rgba(232, 93, 42, 0.40);
      transition: transform var(--dur-fast) var(--ease-spring), box-shadow var(--dur) var(--ease-out), filter var(--dur) var(--ease-out);
    }

    button.primary:hover,
    .primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 10px 26px -4px rgba(232, 93, 42, 0.50);
      filter: brightness(1.04);
    }

    button.primary:active,
    .primary:active {
      transform: translateY(0);
    }

    .result {
      border-top: 1px solid var(--line-soft);
      padding-top: 10px;
      margin-top: 10px;
      color: var(--muted);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 13px;
    }

    .memory-list {
      display: grid;
      gap: 8px;
    }

    .memory-card {
      border: 1px solid var(--line-soft);
      border-radius: var(--r-sm);
      background: var(--memory-card-bg);
      padding: 11px 12px;
      display: grid;
      gap: 8px;
      transition: background-color var(--dur) var(--ease-out), border-color var(--dur) var(--ease-out), transform var(--dur) var(--ease-out);
    }

    .memory-card:hover {
      border-color: var(--line);
      transform: translateY(-1px);
    }

    .memory-card strong {
      color: var(--text);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .memory-meta {
      color: var(--faint);
      font-size: 11px;
      overflow-wrap: anywhere;
    }

    .memory-actions {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .memory-actions button {
      min-height: 30px;
      padding: 0 9px;
      border-radius: 7px;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--text);
      cursor: pointer;
      font-size: 12px;
      font-weight: 800;
      transition: background-color 0.2s, border-color 0.2s;
    }

    .memory-actions button:hover {
      background: var(--surface-3);
      border-color: var(--blue);
    }

    .ring-list {
      display: grid;
      gap: 8px;
      max-height: 340px;
      overflow: auto;
      padding-right: 2px;
    }

    .ring-card {
      border: 1px solid var(--line-soft);
      border-radius: var(--r-sm);
      background: var(--ring-card-bg);
      padding: 11px 12px;
      display: grid;
      gap: 7px;
      transition: background-color var(--dur) var(--ease-out), border-color var(--dur) var(--ease-out), transform var(--dur) var(--ease-out);
    }

    .ring-card:hover {
      border-color: var(--line);
      transform: translateY(-1px);
    }

    .ring-card strong {
      color: var(--text);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .ring-card p {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }

    .workbench-actions {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }

    /* Collapsible global right inspector (Memory Inspector) — works on every page */
    .app.inspector-collapsed {
      --inspector-width: 46px;
    }
    .inspector.collapsed {
      border-left: 1px solid var(--line);
      overflow: hidden;
    }
    .inspector.collapsed .inspector-head {
      height: 100%;
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      padding: 10px 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border-bottom: none;
      cursor: pointer;
    }
    .inspector.collapsed .inspector-head-text {
      display: none;
    }
    .inspector.collapsed .inspector-body,
    .inspector.collapsed .panel {
      display: none !important;
    }
    .inspector.collapsed #inspector-collapse {
      transform: rotate(180deg);
    }
    .inspector-head #inspector-collapse {
      flex-shrink: 0;
      margin-left: auto;
    }

    @media (max-width: 1120px) {
      .app { grid-template-columns: 238px minmax(0, 1fr) var(--inspector-width, 300px); }
      .app { grid-template-columns: var(--shell-w) minmax(0, 1fr) var(--inspector-width, 300px); }
      html.rail-collapsed .app {
        grid-template-columns: 72px minmax(0, 1fr) var(--inspector-width, 300px) !important;
      }
      .inspector { border-left: 1px solid var(--line); border-top: 0; }
      .feature-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 760px) {
      .app { display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
      .chat { height: auto; flex: 1; min-height: 0; }
      .guide { min-height: 0; }
      .guide.active { flex: 1; min-height: 0; }
      .settings { height: auto; }
      .settings.active { flex: 1; min-height: 0; }
      .imagegen:not(.hidden) {
        flex: 1; min-height: 0; overflow-y: auto; -webkit-overflow-scrolling: touch;
      }
      .rail { 
        position: fixed; left: 0; top: 0; bottom: 0; width: min(320px, 86vw); z-index: 100; 
        transform: translateX(-101%); 
        transition: transform 0.32s cubic-bezier(0.23, 1, 0.32, 1); 
        border-right: 1px solid var(--line); 
        background: linear-gradient(180deg, rgba(15,15,15,0.96) 0%, rgba(12,12,14,0.98) 100%);
        display: grid; 
        grid-template-rows: auto minmax(0, 1fr) auto; 
        overflow-y: auto; 
        -webkit-overflow-scrolling: touch;
        box-shadow: 12px 0 40px -12px rgba(0,0,0,0.7);
      }
      .rail.open { transform: translateX(0); }
      .brand { padding: 12px 14px; }
      .brand-row { display: block; }
      .rail-section { min-height: 0; overflow-y: auto; padding: 10px 10px 18px; }
      .nav { display: flex; flex-direction: column; }
      .nav button { min-height: 40px; font-size: 13px; }
      .inspector { position: fixed; right: 0; top: 0; bottom: 0; width: min(320px, 85vw); z-index: 100; transform: translateX(101%); transition: transform .25s ease; border-left: 1px solid var(--line); background: var(--rail-inspector-bg); backdrop-filter: blur(24px); display: grid; grid-template-rows: auto minmax(0, 1fr); overflow-y: auto; -webkit-overflow-scrolling: touch; }
      .inspector.open { transform: translateX(0); }
      .overlay-backdrop { position: fixed; inset: 0; background: var(--overlay-bg); z-index: 99; display: none; }
      .overlay-backdrop.active { display: block; }
      .mobile-only { display: inline-flex; align-items: center; justify-content: center; }
      .guide { padding: 18px; }
      .chat-top { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: start; padding: 10px 12px; gap: 8px; }
      .chat-title { min-width: 0; overflow: hidden; }
      .chat-title strong { font-size: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .chat-title span { font-size: 12px; }
      .badges { grid-column: 2 / 4; justify-content: flex-start; gap: 6px; min-width: 0; }
      .badge { font-size: 11px; padding: 4px 8px; max-width: 100%; overflow: hidden; text-overflow: ellipsis; }
      .composer-form { grid-template-columns: 1fr; }
      .send { width: 100%; }
      .message, .message.user { grid-template-columns: 1fr; }
      .avatar { display: none; }
      .message.user .bubble { grid-column: auto; grid-row: auto; }
      .marketplace { padding: 14px; height: auto; }
      .marketplace.active { flex: 1; min-height: 0; }
      .marketplace-hero { padding: 14px; }
      .marketplace-hero h2 { font-size: 20px; }
      .marketplace-grid { grid-template-columns: 1fr; }
      .detail-drawer { width: min(360px, 92vw); }
    }

    .mobile-nav { display: none; }

    @media (max-width: 640px) {
      .mobile-nav { display: flex; flex: 0 0 56px; border-top: 1px solid var(--line); background: var(--mobile-nav-bg); padding-bottom: max(0px, env(safe-area-inset-bottom)); }
      .mobile-nav button { flex: 1; background: transparent; border: 0; color: var(--muted); font-size: 13px; font-weight: 700; cursor: pointer; }
      .mobile-nav button.active { color: var(--blue); background: rgba(232, 93, 42, 0.08); }
      .mobile-only { display: inline-flex; align-items: center; justify-content: center; }
      .composer { padding: 10px 12px 14px; }
      .composer-form { gap: 8px; }
      .send { width: 100%; min-height: 44px; border-radius: 10px; }
      .messages { padding: 12px; gap: 12px; }
      .message { gap: 8px; }
      .bubble-content { padding: 10px 12px; font-size: 15px; line-height: 1.5; }
      .bubble-head { padding: 8px 10px; font-size: 11px; }
      .bubble-meta { gap: 6px; padding: 0 10px 10px; }
      .guide { padding: 12px; }
      .guide-shell { gap: 12px; }
      .guide-hero { padding: 14px; }
      .guide-hero h2 { font-size: 20px; }
      .guide-hero p { font-size: 14px; margin-top: 6px; }
      .guide-controls button { min-height: 32px; padding: 0 12px; font-size: 13px; }
      .settings { padding: 12px; }
      .settings-form { gap: 14px; }
      .settings-row { grid-template-columns: 1fr; gap: 14px; }
      .settings-field { gap: 4px; }
      .feature-grid { grid-template-columns: 1fr; gap: 10px; }
      .feature-card { padding: 12px; }
      .feature-card h3 { font-size: 15px; }
      .feature-card p, .feature-card li { word-break: break-word; }
      .project-attribution { padding: 12px; }
      .empty h2 { font-size: 20px; }
      .empty p { font-size: 14px; }
      .brand { padding: 12px 14px; }
      .rail-section { padding: 12px; gap: 10px; }
      .nav button { min-height: 40px; font-size: 13px; }
      .inspector-head { padding: 12px; }
      .inspector-body { padding: 10px; gap: 10px; }
      .panel { padding: 10px; }
      .panel h2 { font-size: 11px; margin-bottom: 8px; }
      dl { grid-template-columns: 90px minmax(0, 1fr); gap: 6px 8px; }
      .secondary { min-height: 36px; font-size: 13px; }
      input, select, textarea { font-size: 16px; }
      .status-card { margin: 8px 10px 10px; padding: 10px; font-size: 12px; }
    }

    /* =====================================================
       ImageGen Studio — Elevated 2026 Artistic Treatment
       Premium creative photography / digital art workspace
       ===================================================== */
    .imagegen { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
    .imagegen-shell { display: grid; grid-template-columns: 1fr 320px; gap: 24px; height: 100%; overflow: hidden; padding: 24px 28px; }
    .imagegen-workspace { display: flex; flex-direction: column; gap: 18px; overflow: hidden; min-width: 0; }
    
    .imagegen-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-shrink: 0; }
    .imagegen-header h2 { margin: 0; font-size: 23px; font-weight: 600; letter-spacing: -0.4px; }
    .imagegen-header p { margin: 4px 0 0; font-size: 13px; color: #888; max-width: 48ch; }

    .imagegen-modes { display: inline-flex; background: #111; border: 1px solid #222; border-radius: 999px; padding: 4px; gap: 3px; flex-shrink: 0; }
    .imagegen-modes button { 
      padding: 8px 18px; border-radius: 999px; border: none; background: transparent; 
      color: #888; font-size: 12.5px; font-weight: 600; cursor: pointer; 
      transition: all .18s cubic-bezier(0.23,1,0.32,1); display: flex; align-items: center; gap: 6px;
    }
    .imagegen-modes button:hover { color: #ddd; }
    .imagegen-modes button.active { 
      background: linear-gradient(135deg, #e85d2a, #f97316); 
      color: #fff; font-weight: 700; box-shadow: 0 4px 16px rgba(232,93,42,0.35);
    }

    .imagegen-card { 
      background: rgba(18,18,22,0.92); border: 1px solid rgba(255,255,255,0.06); 
      border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 16px; 
      backdrop-filter: blur(20px); 
    }

    .imagegen-panel { display: flex; flex-direction: column; gap: 14px; }
    .imagegen-panel.hidden { display: none; }

    .imagegen-prompt-wrap { position: relative; }
    .imagegen-prompt-wrap textarea { 
      width: 100%; min-height: 108px; resize: vertical; border-radius: 12px; 
      border: 1px solid #222; background: #0a0a0c; color: #f1f1f5; 
      padding: 16px; font-size: 14.5px; line-height: 1.5; 
    }
    .imagegen-prompt-wrap textarea:focus { 
      outline: none; border-color: #e85d2a; box-shadow: 0 0 0 3px rgba(232,93,42,0.15); 
    }

    /* Inspiration chips */
    .imagegen-inspiration { display: flex; flex-wrap: wrap; gap: 6px; }
    .imagegen-inspiration button {
      font-size: 11px; padding: 5px 12px; border-radius: 999px; border: 1px solid #222;
      background: rgba(255,255,255,0.03); color: #aaa; cursor: pointer; transition: all .12s;
    }
    .imagegen-inspiration button:hover { border-color: #e85d2a; color: #fff; background: rgba(232,93,42,0.12); }

    .imagegen-controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .imagegen-controls select { 
      flex: 1; min-width: 170px; padding: 10px 14px; border-radius: 10px; 
      border: 1px solid #222; background: #111; color: #eee; font-size: 13px; cursor: pointer;
    }
    .imagegen-controls button.primary { 
      min-width: 130px; padding: 11px 22px; border-radius: 10px; border: none; 
      background: linear-gradient(135deg, #e85d2a, #f97316); color: #fff; 
      font-size: 14px; font-weight: 700; cursor: pointer; 
      transition: transform .15s cubic-bezier(0.23,1,0.32,1), box-shadow .2s; 
      box-shadow: 0 4px 14px rgba(232,93,42,0.3);
    }
    .imagegen-controls button.primary:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(232,93,42,0.4); }

    .imagegen-status { font-size: 13px; color: #888; min-height: 18px; display: flex; align-items: center; gap: 8px; }
    .imagegen-spinner { width: 16px; height: 16px; border: 2px solid #222; border-top-color: #e85d2a; border-radius: 50%; animation: imagegen-spin 0.7s linear infinite; }
    @keyframes imagegen-spin { to { transform: rotate(360deg); } }

    .imagegen-result { display: flex; flex-direction: column; gap: 12px; }
    .imagegen-result-card { 
      background: #0a0a0c; border: 1px solid #222; border-radius: 14px; overflow: hidden; 
      box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6);
    }
    .imagegen-result-card img { display: block; width: 100%; height: auto; }
    .imagegen-panel > .imagegen-card > .imagegen-result .imagegen-result-card img {
      max-height: 58vh; object-fit: contain; background: #08090c;
    }
    .imagegen-result-meta { 
      display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; 
      font-size: 12px; color: #888; background: #111; border-top: 1px solid #222; 
    }
    .imagegen-result-meta .badge { 
      background: rgba(232,93,42,0.15); color: #ffb088; padding: 3px 10px; 
      border-radius: 20px; font-size: 11px; font-weight: 600; 
    }

    .imagegen-lineage { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 12px; color: #777; padding: 10px 12px; border: 1px solid #222; border-radius: 10px; background: #111; }
    .imagegen-lineage.hidden { display: none; }
    .imagegen-lineage .crumb { color: #ddd; background: #0a0a0c; border: 1px solid #222; border-radius: 999px; padding: 3px 10px; }

    .imagegen-dropzone { 
      border: 2px dashed #333; border-radius: 16px; padding: 42px 24px; text-align: center; 
      color: #777; cursor: pointer; transition: all .2s; background: #0a0a0c; 
    }
    .imagegen-dropzone:hover { border-color: #e85d2a; background: rgba(232,93,42,0.06); }
    .imagegen-dropzone input[type="file"] { position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none; }
    .imagegen-dropzone svg { width: 36px; height: 36px; stroke-width: 1.6; margin-bottom: 12px; opacity: 0.7; }
    .imagegen-dropzone p { margin: 0; font-size: 14px; }
    .imagegen-dropzone .hint { font-size: 11.5px; margin-top: 6px; opacity: 0.6; }

    .imagegen-preview { max-width: 100%; max-height: 280px; border-radius: 12px; border: 1px solid #222; object-fit: contain; background: #0a0a0c; }

    .imagegen-sidebar { 
      background: rgba(18,18,22,0.9); border: 1px solid rgba(255,255,255,0.06); 
      border-radius: 16px; padding: 18px; display: flex; flex-direction: column; gap: 14px; 
      overflow: hidden; backdrop-filter: blur(18px); 
    }
    .imagegen-sidebar-head { display: flex; align-items: center; justify-content: space-between; }
    .imagegen-sidebar-head h3 { margin: 0; font-size: 14px; font-weight: 600; color: #ddd; }
    .imagegen-sidebar-head .count { font-size: 11px; color: #666; background: #111; padding: 2px 9px; border-radius: 999px; }

    .imagegen-gallery-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; overflow: auto; padding-right: 4px; }
    .imagegen-gallery-grid .empty { grid-column: 1/-1; text-align: center; padding: 32px 12px; color: #555; font-size: 13px; }
    .imagegen-gallery-grid .thumb { 
      position: relative; aspect-ratio: 1; border-radius: 12px; overflow: hidden; 
      border: 1px solid #222; cursor: pointer; background: #111; 
      transition: transform .2s cubic-bezier(0.23,1,0.32,1), box-shadow .2s; 
    }
    .imagegen-gallery-grid .thumb:hover { transform: translateY(-3px); box-shadow: 0 16px 32px -12px rgba(0,0,0,0.6); }
    .imagegen-gallery-grid .thumb img { width: 100%; height: 100%; object-fit: cover; }
    .imagegen-gallery-grid .thumb .ring { 
      position: absolute; left: 8px; bottom: 8px; font-size: 10px; padding: 2px 8px; 
      border-radius: 999px; background: rgba(0,0,0,0.7); color: #ddd; font-weight: 600; 
      backdrop-filter: blur(4px);
    }
    .imagegen-gallery-grid .thumb .del { 
      position: absolute; top: 8px; right: 8px; width: 26px; height: 26px; border-radius: 8px; 
      background: rgba(0,0,0,0.6); color: #fff; border: none; display: none; align-items: center; 
      justify-content: center; font-size: 15px; cursor: pointer; transition: background .15s;
    }
    .imagegen-gallery-grid .thumb .del:hover { background: #c33; }
    .imagegen-gallery-grid .thumb:hover .del { display: flex; }

    .imagegen-mini-gallery { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0; }
    .imagegen-mini-gallery .thumb { 
      width: 78px; height: 78px; flex-shrink: 0; border-radius: 10px; overflow: hidden; 
      border: 2px solid transparent; cursor: pointer; background: #111; transition: all .15s; 
    }
    .imagegen-mini-gallery .thumb:hover { transform: translateY(-1px); }
    .imagegen-mini-gallery .thumb.active { border-color: #e85d2a; box-shadow: 0 0 0 3px rgba(232,93,42,0.2); }

    .imagegen-error { color: #f66; font-size: 13px; padding: 10px 14px; background: rgba(180,40,40,0.1); border-radius: 10px; border: 1px solid rgba(180,40,40,0.2); }
    @media (max-width: 1120px) {
      .imagegen-shell { grid-template-columns: 1fr 260px; gap: 16px; padding: 20px; }
    }
    @media (max-width: 760px) {
      .imagegen-shell { grid-template-columns: 1fr; grid-template-rows: 1fr auto; padding: 16px; }
      .imagegen-sidebar { max-height: 220px; }
      .imagegen-gallery-grid { grid-template-columns: repeat(4, 1fr); }
      .imagegen-header { flex-direction: column; align-items: flex-start; gap: 10px; }
    }
    @media (max-width: 640px) {
      .imagegen-shell { padding: 12px; gap: 12px; }
      .imagegen-gallery-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
      .imagegen-card { padding: 14px; }
      .imagegen-controls button.primary { width: 100%; }
    }
    .imagegen-gallery-grid .thumb .download {
      position: absolute; top: 8px; left: 8px; width: 26px; height: 26px; border-radius: 8px;
      background: rgba(0,0,0,.62); color: #fff; border: 0; display: none; align-items: center;
      justify-content: center; font-size: 15px; cursor: pointer;
    }
    .imagegen-gallery-grid .thumb:hover .download { display: flex; }
    .imagegen-gallery-grid .thumb .edit-src {
      position: absolute; top: 8px; left: 40px; width: 26px; height: 26px; border-radius: 8px;
      background: rgba(232,93,42,.85); color: #fff; border: 0; display: none; align-items: center;
      justify-content: center; font-size: 13px; cursor: pointer;
    }
    .imagegen-gallery-grid .thumb:hover .edit-src { display: flex; }
    .imagegen-action.primary-ish {
      border-color: rgba(232,93,42,.45);
      color: #ffc4a8;
    }

    /* ImageGen Creative Canvas — base skin; FORGE STUDIOS + light overrides win */
    .imagegen {
      background:
        radial-gradient(circle at 20% 0%, rgba(232,93,42,.09), transparent 34%),
        radial-gradient(circle at 80% 100%, rgba(245,158,11,.08), transparent 32%),
        var(--bg);
    }
    .imagegen-shell { grid-template-columns: minmax(0,1fr) 230px; gap: 16px; padding: 18px 20px; }
    .imagegen-workspace { overflow-y: auto; padding-right: 3px; scrollbar-width: thin; }
    .imagegen-header { align-items: center; padding: 0 2px; }
    .imagegen-header h2 { font-size: 24px; font-weight: 750; letter-spacing: -.7px; }
    .imagegen-header p { margin-top: 2px; color: #777d89; }
    .imagegen-card {
      padding: 16px;
      gap: 14px;
      border-radius: 18px;
      background: linear-gradient(145deg, rgba(20,22,28,.96), rgba(12,13,17,.96));
      border-color: rgba(255,255,255,.075);
      box-shadow: 0 18px 55px rgba(0,0,0,.22);
    }
    .imagegen-compare-stage { display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 12px; }
    .imagegen-media-stage {
      position: relative; min-height: 330px; max-height: 54vh; overflow: hidden;
      display: grid; place-items: center; border: 1px solid rgba(255,255,255,.08);
      border-radius: 15px; background:
        linear-gradient(45deg, rgba(255,255,255,.018) 25%, transparent 25% 75%, rgba(255,255,255,.018) 75%),
        linear-gradient(45deg, rgba(255,255,255,.018) 25%, #090a0d 25% 75%, rgba(255,255,255,.018) 75%);
      background-size: 24px 24px; background-position: 0 0, 12px 12px;
    }
    .imagegen-stage-label {
      position: absolute; top: 10px; left: 10px; z-index: 2; padding: 5px 9px;
      border-radius: 999px; background: rgba(7,8,10,.78); border: 1px solid rgba(255,255,255,.08);
      color: #aeb4c0; font-size: 10px; font-weight: 750; letter-spacing: .08em; text-transform: uppercase;
      backdrop-filter: blur(10px);
    }
    .imagegen-media-stage .imagegen-preview,
    .imagegen-media-stage .imagegen-result-card,
    .imagegen-media-stage .imagegen-result-card img {
      width: 100%; height: 100%; max-height: 54vh; object-fit: contain; border: 0; border-radius: 0;
    }
    .imagegen-media-stage .imagegen-result { width: 100%; height: 100%; min-height: 330px; }
    .imagegen-media-stage .imagegen-result-card { display: grid; grid-template-rows: minmax(0,1fr) auto; }
    .imagegen-stage-empty { text-align: center; color: #606775; max-width: 240px; padding: 28px; }
    .imagegen-stage-empty strong { display: block; color: #aeb4c0; margin-bottom: 5px; font-size: 13px; }
    .imagegen-source-stage.has-source .imagegen-dropzone { display: none; }
    .imagegen-source-stage:not(.has-source) .imagegen-preview,
    .imagegen-source-stage:not(.has-source) .imagegen-replace-source { display: none; }
    .imagegen-replace-source {
      position: absolute; right: 10px; top: 10px; z-index: 3; border: 1px solid rgba(255,255,255,.12);
      background: rgba(7,8,10,.78); color: #e8edf5; border-radius: 999px; padding: 6px 11px;
      font-size: 11px; font-weight: 700; cursor: pointer; backdrop-filter: blur(10px);
    }
    .imagegen-source-stage .imagegen-dropzone {
      width: calc(100% - 24px); min-height: 230px; display: grid; place-items: center;
      align-content: center; padding: 24px; border-color: rgba(255,140,90,.24);
      background: rgba(232,93,42,.035);
    }
    .imagegen-control-dock {
      display: grid; grid-template-columns: minmax(220px,1fr) minmax(180px,.65fr) auto;
      gap: 10px; align-items: end; padding: 12px; border: 1px solid rgba(255,255,255,.07);
      border-radius: 14px; background: rgba(7,8,11,.72);
    }
    .imagegen-control-dock .imagegen-prompt-wrap { grid-column: 1 / -1; }
    .imagegen-control-dock textarea { min-height: 78px; max-height: 150px; }
    .imagegen-control-dock select { min-width: 0; width: 100%; }
    .imagegen-raw-toggle {
      display: inline-flex; align-items: center; gap: 8px;
      font-size: 12.5px; color: #7a808c; cursor: pointer; user-select: none;
      padding: 2px 0;
    }
    .imagegen-raw-toggle input { width: 15px; height: 15px; accent-color: #e85d2a; cursor: pointer; }
    .imagegen-raw-toggle:hover { color: #aeb4c0; }
    .imagegen-control-dock .imagegen-raw-toggle { grid-column: 1 / -1; }
    .imagegen-action-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .imagegen-action {
      min-height: 34px; border-radius: 9px; padding: 0 12px; border: 1px solid rgba(255,255,255,.1);
      background: rgba(255,255,255,.045); color: #dce3ec; font-size: 11px; font-weight: 700; cursor: pointer;
    }
    .imagegen-action:hover { border-color: rgba(255,140,90,.55); color: #fff; }
    .imagegen-result-meta { gap: 10px; flex-wrap: wrap; }
    .imagegen-result-meta .imagegen-action-row { margin-left: auto; }
    .imagegen-progress {
      min-height: 330px; display: grid; place-items: center; text-align: center; padding: 32px;
      color: #aeb4c0; background: radial-gradient(circle, rgba(232,93,42,.08), transparent 55%);
    }
    .imagegen-progress .imagegen-spinner { width: 28px; height: 28px; margin: 0 auto 12px; }
    .imagegen-progress strong { display: block; color: #eef5ff; margin-bottom: 6px; }
    .imagegen-sidebar { padding: 14px; border-radius: 16px; }
    .imagegen-gallery-grid { grid-template-columns: 1fr; gap: 9px; }
    .imagegen-gallery-grid .thumb { aspect-ratio: 4/3; }
    .imagegen-lightbox {
      position: fixed; inset: 0; z-index: 500; display: grid; place-items: center; padding: 32px;
      background: rgba(0,0,0,.88); backdrop-filter: blur(18px);
    }
    .imagegen-lightbox.hidden { display: none; }
    .imagegen-lightbox img { max-width: min(94vw, 1500px); max-height: 88vh; object-fit: contain; border-radius: 14px; box-shadow: 0 24px 90px #000; }
    .imagegen-lightbox-close {
      position: fixed; top: 20px; right: 24px; width: 42px; height: 42px; border-radius: 50%;
      border: 1px solid rgba(255,255,255,.16); background: rgba(20,20,24,.8); color: white; font-size: 24px; cursor: pointer;
    }
    @media (max-width: 1120px) {
      .imagegen-shell { grid-template-columns: minmax(0,1fr) 190px; padding: 16px; }
      .imagegen-control-dock { grid-template-columns: 1fr 1fr; }
      .imagegen-control-dock button.primary { grid-column: 1/-1; }
    }
    @media (max-width: 820px) {
      .imagegen-shell { grid-template-columns: 1fr; grid-template-rows: minmax(0,1fr) auto; overflow-y: auto; }
      .imagegen-workspace { overflow: visible; }
      .imagegen-sidebar { max-height: none; }
      .imagegen-gallery-grid { display: flex; overflow-x: auto; }
      .imagegen-gallery-grid .thumb { width: 128px; flex: 0 0 128px; }
    }
    @media (max-width: 680px) {
      .imagegen {
        height: auto; min-height: 100%; overflow: visible;
        padding-bottom: max(12px, env(safe-area-inset-bottom));
      }
      .imagegen-shell {
        display: flex; flex-direction: column; gap: 12px;
        height: auto; min-height: 0; overflow: visible;
        padding: 10px 12px max(14px, env(safe-area-inset-bottom));
      }
      .imagegen-workspace {
        overflow: visible; padding-right: 0; gap: 12px;
      }
      .imagegen-header {
        align-items: flex-start; flex-direction: column; gap: 10px;
      }
      .imagegen-header h2 { font-size: 20px; }
      .imagegen-header p { font-size: 12.5px; max-width: none; }
      .imagegen-modes {
        width: 100%; display: flex; overflow-x: auto;
        -webkit-overflow-scrolling: touch; scrollbar-width: none;
      }
      .imagegen-modes::-webkit-scrollbar { display: none; }
      .imagegen-modes button {
        flex: 1 0 auto; min-width: 88px; justify-content: center;
        padding: 10px 12px; font-size: 12px;
      }
      .imagegen-card { padding: 12px; gap: 12px; border-radius: 14px; }
      .imagegen-controls { flex-direction: column; align-items: stretch; }
      .imagegen-controls select,
      .imagegen-controls button.primary { width: 100%; min-width: 0; }
      .imagegen-controls button.primary {
        min-height: 44px; font-size: 15px;
      }
      .imagegen-prompt-wrap textarea {
        min-height: 96px; font-size: 16px; padding: 12px;
      }
      .imagegen-inspiration { gap: 5px; }
      .imagegen-inspiration button {
        min-height: 34px; padding: 6px 10px;
      }
      .imagegen-compare-stage { grid-template-columns: 1fr; gap: 10px; }
      .imagegen-media-stage {
        min-height: 200px; max-height: none; height: auto;
      }
      .imagegen-media-stage .imagegen-result { min-height: 200px; }
      .imagegen-progress { min-height: 200px; padding: 20px 16px; }
      .imagegen-progress span { display: block; font-size: 12.5px; line-height: 1.45; margin-top: 4px; }
      .imagegen-source-stage .imagegen-dropzone {
        width: calc(100% - 16px); min-height: 160px; padding: 18px 14px;
      }
      .imagegen-replace-source {
        top: auto; bottom: 10px; right: 10px; min-height: 36px;
      }
      .imagegen-control-dock {
        grid-template-columns: 1fr; gap: 10px; padding: 10px;
      }
      .imagegen-control-dock textarea,
      .imagegen-control-dock .imagegen-prompt-wrap,
      .imagegen-control-dock button.primary,
      .imagegen-control-dock .imagegen-raw-toggle { grid-column: auto; }
      .imagegen-control-dock button.primary { min-height: 44px; width: 100%; }
      .imagegen-control-dock select { min-height: 42px; font-size: 15px; }
      .imagegen-raw-toggle { font-size: 13px; padding: 4px 0; }
      .imagegen-raw-toggle input { width: 18px; height: 18px; }
      .imagegen-result-meta {
        flex-direction: column; align-items: flex-start; gap: 8px;
      }
      .imagegen-result-meta .imagegen-action-row { margin-left: 0; width: 100%; }
      .imagegen-action { flex: 1; min-height: 40px; font-size: 12px; }
      .imagegen-sidebar {
        order: 2; max-height: none; padding: 12px;
      }
      .imagegen-sidebar-head h3 { font-size: 13px; }
      .imagegen-gallery-grid {
        display: flex; gap: 10px; overflow-x: auto;
        -webkit-overflow-scrolling: touch; padding-bottom: 4px;
      }
      .imagegen-gallery-grid .thumb {
        width: 112px; flex: 0 0 112px; aspect-ratio: 4/3;
      }
      .imagegen-gallery-grid .thumb .del,
      .imagegen-gallery-grid .thumb .download,
      .imagegen-gallery-grid .thumb .edit-src {
        display: flex; opacity: 1;
      }
      .imagegen-mini-gallery .thumb { width: 72px; height: 72px; }
      .imagegen-lightbox { padding: 16px; }
      .imagegen-lightbox-close {
        top: max(12px, env(safe-area-inset-top));
        right: max(12px, env(safe-area-inset-right));
      }
      .imagegen-error { font-size: 14px; line-height: 1.45; }
    }

    /* =====================================================
       CineTempre Studio — 2026 Director's Cut (VideoGen)
       Futuristic, filmic, holographic, premium creative tool
       ===================================================== */
    .videogen { display: flex; flex-direction: column; height: 100%; overflow: hidden; background: #050505; }
    .videogen-shell { display: grid; grid-template-columns: 1fr 320px; gap: 22px; height: 100%; overflow: hidden; padding: 22px 26px; }
    .videogen-workspace { display: flex; flex-direction: column; gap: 14px; min-width: 0; overflow: hidden; }
    .videogen-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-shrink: 0; }
    .videogen-header h2 { margin: 0; font-size: 23px; font-weight: 600; letter-spacing: -0.4px; background: linear-gradient(90deg, #fff, #fdba74); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .videogen-header p { margin: 3px 0 0; font-size: 12.5px; color: #8a8a8a; max-width: 46ch; }
    .cine-badge { display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: 1.5px; padding: 2px 9px; border-radius: 999px; background: rgba(245,158,11,0.15); color: #fdba74; border: 1px solid rgba(245,158,11,0.3); margin-bottom: 6px; }

    .videogen-modes { display: inline-flex; background: #111; border: 1px solid #222; border-radius: 999px; padding: 3px; gap: 2px; flex-shrink: 0; }
    .videogen-modes button { padding: 7px 15px; border-radius: 999px; border: none; background: transparent; color: #888; font-size: 12px; font-weight: 600; cursor: pointer; transition: all .18s cubic-bezier(0.23,1,0.32,1); white-space: nowrap; }
    .videogen-modes button:hover { color: #ddd; }
    .videogen-modes button.active { background: linear-gradient(135deg, #f59e0b, #22d3ee); color: #111; font-weight: 700; box-shadow: 0 4px 14px rgba(245,158,11,0.35); }

    .videogen-panel { display: flex; flex-direction: column; gap: 14px; overflow: hidden; }
    .videogen-panel.hidden { display: none; }

    .cine-director-card { background: rgba(18,18,22,0.92); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 18px; display: flex; flex-direction: column; gap: 14px; backdrop-filter: blur(20px); }
    .cine-director-card .lexicon-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .cine-director-card .lexicon-chips button { font-size: 10px; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(163,163,172,0.25); background: rgba(255,255,255,0.03); color: #c0c0c8; cursor: pointer; transition: all .12s; }
    .cine-director-card .lexicon-chips button:hover { border-color: #f59e0b; color: #fff; background: rgba(245,158,11,0.12); }

    .videogen-prompt-wrap textarea { width: 100%; min-height: 92px; resize: vertical; border-radius: 12px; border: 1px solid #222; background: #0a0a0c; color: #f1f1f5; padding: 13px 14px; font-size: 13.5px; line-height: 1.45; }
    .videogen-prompt-wrap textarea:focus { outline: none; border-color: #f59e0b; box-shadow: 0 0 0 3px rgba(245,158,11,0.15); }

    .cine-controls-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(118px, 1fr)); gap: 10px; }
    .cine-control { display: flex; flex-direction: column; gap: 4px; }
    .cine-control label { font-size: 10px; font-weight: 600; color: #777; letter-spacing: .4px; }
    .cine-control select, .cine-control input[type="range"] { background: #111; border: 1px solid #222; color: #eee; border-radius: 8px; padding: 7px 9px; font-size: 12.5px; }
    .cine-control .segmented { display: flex; background: #111; border: 1px solid #222; border-radius: 8px; padding: 2px; }
    .cine-control .segmented button { flex: 1; font-size: 11px; padding: 5px 0; border: none; background: transparent; color: #888; border-radius: 6px; cursor: pointer; }
    .cine-control .segmented button.active { background: #222; color: #fff; font-weight: 600; }

    .cine-render-btn { margin-top: 4px; padding: 14px 22px; font-size: 15px; font-weight: 700; letter-spacing: .6px; border: none; border-radius: 12px; background: linear-gradient(135deg, #f59e0b, #22d3ee); color: #111; cursor: pointer; transition: transform .15s cubic-bezier(0.23,1,0.32,1), box-shadow .2s; position: relative; overflow: hidden; }
    .cine-render-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 30px -8px rgba(245,158,11,0.5); }
    .cine-render-btn:active { transform: scale(0.985); }
    .cine-render-btn .reel { display: inline-block; width: 15px; height: 15px; border: 2px solid #111; border-radius: 50%; margin-right: 8px; vertical-align: -2px; animation: cine-reel-spin 1.6s linear infinite paused; }
    .cine-render-btn.loading .reel { animation-play-state: running; }
    @keyframes cine-reel-spin { to { transform: rotate(360deg); } }

    .cine-status { font-size: 12px; color: #8a8a8a; min-height: 18px; display: flex; align-items: center; gap: 8px; }
    .cine-spinner { width: 15px; height: 15px; border: 2px solid #222; border-top-color: #f59e0b; border-radius: 50%; animation: cine-spin .75s linear infinite; }
    @keyframes cine-spin { to { transform: rotate(360deg); } }

    .cine-player-wrap { background: #0a0a0c; border: 1px solid #222; border-radius: 16px; overflow: hidden; position: relative; }
    .cine-player-wrap video { display: block; width: 100%; max-height: 420px; background: #000; }
    .cine-player-perforation { position: absolute; top: 0; bottom: 0; width: 11px; background: repeating-linear-gradient(180deg, transparent, transparent 6px, rgba(255,255,255,0.07) 6px, rgba(255,255,255,0.07) 11px); pointer-events: none; z-index: 2; }
    .cine-player-perforation.left { left: 0; }
    .cine-player-perforation.right { right: 0; }

    .cine-cut-history { display: flex; gap: 8px; overflow-x: auto; padding: 8px 2px; background: #0a0a0c; border: 1px solid #222; border-radius: 10px; }
    .cine-cut-history .film-cell { flex: 0 0 78px; height: 52px; border-radius: 6px; overflow: hidden; border: 1px solid #333; position: relative; cursor: pointer; background: #111; }
    .cine-cut-history .film-cell img, .cine-cut-history .film-cell video { width: 100%; height: 100%; object-fit: cover; }
    .cine-cut-history .film-cell .label { position: absolute; bottom: 2px; right: 3px; font-size: 9px; background: rgba(0,0,0,0.7); padding: 0 4px; border-radius: 3px; color: #ccc; }

    .videogen-reel-sidebar { background: rgba(18,18,22,0.9); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 16px; display: flex; flex-direction: column; gap: 12px; overflow: hidden; backdrop-filter: blur(18px); }
    .reel-head { display: flex; align-items: center; justify-content: space-between; }
    .reel-head h3 { margin: 0; font-size: 13px; font-weight: 600; color: #ddd; }
    .reel-head .count { font-size: 11px; color: #666; background: #111; padding: 1px 8px; border-radius: 999px; }

    .reel-wall { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; overflow: auto; padding-right: 2px; }
    .reel-wall .empty { grid-column: 1 / -1; text-align: center; padding: 30px 10px; color: #555; font-size: 12px; }
    .reel-wall .reel-card { position: relative; aspect-ratio: 16/9; background: #111; border-radius: 10px; overflow: hidden; border: 1px solid #222; cursor: pointer; transition: transform .15s cubic-bezier(0.23,1,0.32,1), box-shadow .15s; }
    .reel-wall .reel-card:hover { transform: translateY(-2px); box-shadow: 0 14px 28px -12px rgba(0,0,0,0.6); }
    .reel-wall .reel-card video { width: 100%; height: 100%; object-fit: cover; background: #000; }
    .reel-wall .reel-card .meta { position: absolute; bottom: 0; left: 0; right: 0; padding: 6px 8px; background: linear-gradient(transparent, rgba(0,0,0,0.85)); font-size: 10px; display: flex; justify-content: space-between; color: #ddd; }
    .reel-wall .reel-card .del { position: absolute; top: 5px; right: 5px; width: 22px; height: 22px; border-radius: 6px; background: rgba(0,0,0,0.6); color: #fff; border: none; display: none; align-items: center; justify-content: center; font-size: 13px; cursor: pointer; }
    .reel-wall .reel-card:hover .del { display: flex; }
    .reel-wall .reel-card .del:hover { background: #b22; }

    .cine-error { color: #f66; font-size: 12px; padding: 8px 12px; background: rgba(180,40,40,0.1); border-radius: 8px; border: 1px solid rgba(180,40,40,0.2); }

    @media (max-width: 1024px) {
      .videogen-shell { grid-template-columns: 1fr 280px; gap: 16px; padding: 16px; }
    }
    @media (max-width: 780px) {
      .videogen-shell { grid-template-columns: 1fr; grid-template-rows: 1fr auto; padding: 12px; }
      .videogen-reel-sidebar { max-height: 210px; }
      .reel-wall { grid-template-columns: repeat(4, 1fr); }
    }

    /* ============================================================
       PREMIUM POLISH LAYER — unified softness across all views
       ============================================================ */

    .guide, .settings, .marketplace {
      scroll-behavior: smooth;
    }

    .guide.active, .settings.active, .marketplace.active {
      animation: viewIn 0.32s var(--ease-out) both;
    }

    /* Main view transitions */
    .chat,
    .guide,
    .settings,
    .marketplace,
    .imagegen,
    .videogen,
    .audiogen {
      will-change: opacity, transform;
    }

    .chat:not(.hidden),
    .guide.active,
    .settings.active,
    .marketplace.active,
    .imagegen:not(.hidden),
    .videogen:not(.hidden),
    .audiogen:not(.hidden) {
      animation: viewIn 0.34s var(--ease-out) both;
    }

    .view-enter {
      animation: viewIn 0.38s var(--ease-out) both !important;
    }

    .view-exit {
      animation: viewOut 0.18s ease both !important;
      pointer-events: none;
    }

    @keyframes viewIn {
      from { opacity: 0; transform: translateY(10px) scale(0.992); filter: blur(2px); }
      to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
    }

    @keyframes viewOut {
      from { opacity: 1; transform: translateY(0) scale(1); }
      to { opacity: 0; transform: translateY(-6px) scale(0.995); }
    }

    .settings-form {
      max-width: 920px;
    }

    .settings-status-panel,
    .provider-effective-summary {
      border-radius: var(--r-md);
      border-color: var(--line);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .provider-subtabs {
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--line);
      border-radius: var(--r-pill);
      padding: 4px;
      gap: 3px;
    }

    .provider-subtab {
      border-radius: var(--r-pill);
      color: var(--muted);
      font-weight: 650;
      transition: all var(--dur) var(--ease-out);
    }

    .provider-subtab:hover { color: var(--text); background: rgba(255,255,255,0.04); }

    .provider-subtab.active {
      background: var(--fire-gradient);
      color: #fff;
      box-shadow: 0 4px 14px -2px rgba(232, 93, 42, 0.40);
    }

    .project-attribution {
      border-radius: var(--r-lg);
      border-color: var(--line);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .detail-drawer {
      box-shadow: -16px 0 48px -12px rgba(0,0,0,0.55);
      background: linear-gradient(180deg, rgba(14,17,24,0.97), rgba(10,12,18,0.99));
    }

    .light .detail-drawer {
      background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.99));
      box-shadow: -16px 0 48px -12px rgba(15,23,42,0.12);
    }

    .temporal-mass-bar {
      height: 7px;
      background: rgba(255,255,255,0.06);
    }

    .light .temporal-mass-bar {
      background: rgba(15,23,42,0.08);
    }

    .account-menu {
      border-radius: var(--r-md);
      border-color: var(--line);
      box-shadow: var(--shadow-float);
      backdrop-filter: blur(20px);
      overflow: hidden;
    }

    .account-btn {
      border-radius: var(--r-pill);
      border-color: var(--line);
      transition: all var(--dur) var(--ease-spring);
    }

    .account-btn:hover {
      box-shadow: var(--glow-blue);
    }

    .inspector-head {
      padding: 16px 16px 14px;
      background: linear-gradient(180deg, rgba(255,122,77,0.04), transparent);
    }

    .inspector-head strong {
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .mobile-nav {
      backdrop-filter: blur(20px) saturate(1.2);
      box-shadow: 0 -8px 32px -12px rgba(0,0,0,0.4);
    }

    .mobile-nav button {
      transition: color var(--dur) var(--ease-out), background var(--dur) var(--ease-out);
      font-size: 12px;
      gap: 2px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      letter-spacing: -0.01em;
    }

    .mobile-nav button.active {
      color: var(--blue);
      background: linear-gradient(180deg, rgba(255,122,77,0.10), transparent);
    }

    /* Creative studios — soft token alignment */
    .imagegen, .videogen, .audiogen {
      animation: viewIn 0.32s var(--ease-out) both;
    }

    .imagegen {
      background:
        radial-gradient(circle at 18% 0%, rgba(255,122,77,0.08), transparent 36%),
        radial-gradient(circle at 82% 100%, rgba(251,146,60,0.07), transparent 34%),
        var(--bg) !important;
    }

    .imagegen-card,
    .imagegen-sidebar,
    .videogen-card,
    .audiogen-card {
      border-radius: var(--r-lg) !important;
      border: 1px solid var(--line) !important;
      background: linear-gradient(155deg, rgba(20,24,34,0.94), rgba(12,15,22,0.96)) !important;
      box-shadow: var(--shadow-card) !important;
      backdrop-filter: blur(18px) saturate(1.1);
    }

    .light .imagegen-card,
    .light .imagegen-sidebar,
    .light .videogen-card,
    .light .audiogen-card {
      background: linear-gradient(155deg, rgba(255,255,255,0.96), rgba(248,250,252,0.98)) !important;
    }

    .imagegen-modes,
    .videogen-modes {
      background: rgba(255,255,255,0.03) !important;
      border: 1px solid var(--line) !important;
      border-radius: var(--r-pill) !important;
      padding: 4px !important;
    }

    .imagegen-modes button.active,
    .videogen-modes button.active {
      background: var(--fire-gradient) !important;
      box-shadow: 0 4px 16px -2px rgba(232,93,42,0.40) !important;
    }

    .imagegen-prompt-wrap textarea,
    .videogen-prompt-wrap textarea,
    .audiogen-prompt-wrap textarea {
      border: 1px solid var(--line) !important;
      border-radius: var(--r-md) !important;
      background: var(--input-bg) !important;
      color: var(--text) !important;
      transition: border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out) !important;
    }

    .imagegen-prompt-wrap textarea:focus,
    .videogen-prompt-wrap textarea:focus,
    .audiogen-prompt-wrap textarea:focus {
      border-color: rgba(255,122,77,0.45) !important;
      box-shadow: 0 0 0 3px rgba(255,122,77,0.12) !important;
    }

    .imagegen-controls select,
    .videogen-controls select,
    .audiogen-controls select {
      border: 1px solid var(--line) !important;
      border-radius: var(--r-sm) !important;
      background: var(--input-bg) !important;
      color: var(--text) !important;
    }

    .imagegen-controls button.primary,
    .videogen-controls button.primary,
    .audiogen-controls button.primary,
    .audiogen-controls .primary {
      background: var(--fire-gradient) !important;
      border-radius: var(--r-sm) !important;
      box-shadow: 0 6px 20px -4px rgba(232,93,42,0.42) !important;
    }

    .imagegen-dropzone,
    .videogen-dropzone {
      border: 1.5px dashed rgba(255,255,255,0.12) !important;
      border-radius: var(--r-lg) !important;
      background: rgba(255,255,255,0.02) !important;
      transition: border-color var(--dur) var(--ease-out), background var(--dur) var(--ease-out), transform var(--dur) var(--ease-out) !important;
    }

    .imagegen-dropzone:hover,
    .videogen-dropzone:hover {
      border-color: rgba(255,122,77,0.45) !important;
      background: rgba(255,122,77,0.06) !important;
      transform: translateY(-1px);
    }

    .imagegen-gallery-grid .thumb,
    .reel-wall .reel-card {
      border-radius: var(--r-md) !important;
      border-color: var(--line) !important;
      transition: transform var(--dur) var(--ease-spring), box-shadow var(--dur) var(--ease-out) !important;
    }

    .imagegen-gallery-grid .thumb:hover,
    .reel-wall .reel-card:hover {
      transform: translateY(-3px) scale(1.01) !important;
      box-shadow: var(--shadow-card) !important;
    }

    .imagegen-header h2,
    .videogen-header h2,
    .audiogen-header h2 {
      font-weight: 750 !important;
      letter-spacing: -0.035em !important;
    }

    .imagegen-header p,
    .videogen-header p,
    .audiogen-header p {
      color: var(--muted) !important;
      line-height: 1.55 !important;
    }

    .audiogen {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: auto;
      background:
        radial-gradient(circle at 20% 0%, rgba(255,122,77,0.07), transparent 36%),
        radial-gradient(circle at 80% 100%, rgba(52,211,153,0.05), transparent 34%),
        var(--bg);
    }

    .audiogen.hidden { display: none !important; }

    .audiogen-shell {
      max-width: 860px;
      margin: 0 auto;
      padding: 28px 24px 40px;
      width: 100%;
    }

    .audiogen-workspace {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .audiogen-header h2 {
      margin: 0;
      font-size: 26px;
    }

    .audiogen-header p {
      margin: 6px 0 0;
      max-width: 48ch;
    }

    .audiogen-card {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .audiogen-prompt-wrap textarea {
      min-height: 120px;
      resize: vertical;
      width: 100%;
      padding: 14px 16px;
      font-size: 14.5px;
      line-height: 1.55;
    }

    .audiogen-controls {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    .audiogen-controls select {
      min-width: 140px;
      height: 40px;
    }

    .audiogen-controls .primary {
      margin-left: auto;
    }

    @media (max-width: 640px) {
      .audiogen-shell { padding: 16px 14px 28px; }
      .audiogen-controls .primary { margin-left: 0; width: 100%; }
    }

    /* Soften rail hard-coded greys for light mode harmony */
    .light .rail select,
    .light .rail input {
      border-color: var(--line);
      color: var(--text);
    }

    .light .nav {
      background: transparent;
      border-color: transparent;
    }

    .light .nav button {
      color: var(--shell-muted);
    }

    .light .nav button:hover {
      color: var(--text);
      background: var(--shell-fill-hover);
    }

    .light .nav button.active {
      color: var(--text);
    }

    .light .brand h1 {
      background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
      -webkit-background-clip: text;
      background-clip: text;
    }

    .light .brand p,
    .light label {
      color: var(--muted);
    }

    .light .status-card {
      color: var(--muted);
    }

    .light .composer-form {
      background: linear-gradient(180deg, #ffffff, #f8fafc);
    }

    .light .empty {
      background:
        radial-gradient(ellipse at 50% 0%, rgba(232,93,42,0.06), transparent 60%),
        rgba(255,255,255,0.6);
    }

    /* Empty-state decorative mark */
    .empty-mark {
      width: 56px;
      height: 56px;
      margin: 0 auto 4px;
      border-radius: 18px;
      display: grid;
      place-items: center;
      background: linear-gradient(145deg, rgba(255,122,77,0.16), rgba(245,158,11,0.12));
      border: 1px solid rgba(255,122,77,0.22);
      box-shadow: 0 12px 32px -10px rgba(232,93,42,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
      color: var(--blue);
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.04em;
    }

    .empty-hints {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-top: 6px;
    }

    .empty-hints span {
      font-size: 12px;
      color: var(--faint);
      border: 1px solid var(--line);
      border-radius: var(--r-pill);
      padding: 5px 11px;
      background: rgba(255,255,255,0.02);
    }

    /* ============================================================
       COMPACT DENSITY — tighter spacing across the shell
       ============================================================ */
    html.density-compact {
      --r-sm: 8px;
      --r-md: 11px;
      --r-lg: 14px;
      --r-xl: 16px;
    }

    html.density-compact body {
      font-size: 13px;
      line-height: 1.45;
    }

    html.density-compact {
      --shell-w-expanded: 240px;
      --shell-w: var(--shell-w-expanded);
      --shell-item-h: 32px;
      --shell-pad: 10px;
      --shell-section-gap: 12px;
    }
    html.density-compact .app {
      grid-template-columns: var(--shell-w) minmax(0, 1fr) var(--inspector-width, 300px);
    }

    html.density-compact .brand {
      padding: 16px 14px 12px;
    }

    html.density-compact .brand h1 {
      font-size: 18px;
    }

    html.density-compact .brand p {
      font-size: 11px;
      margin-top: 3px;
    }

    html.density-compact .rail-section {
      padding: 12px 12px 14px;
      gap: 14px;
    }

    html.density-compact .nav {
      gap: 3px;
      padding: 0;
    }

    html.density-compact .nav button {
      min-height: var(--shell-item-h);
      font-size: 12px;
      padding: 0 10px;
      border-radius: var(--shell-radius);
      gap: 9px;
    }

    html.density-compact .nav button svg {
      width: 15px;
      height: 15px;
    }

    html.density-compact .rail select,
    html.density-compact .rail input,
    html.density-compact input,
    html.density-compact select {
      height: 34px;
      font-size: 12.5px;
    }

    html.density-compact .group {
      gap: 6px;
    }

    html.density-compact label {
      font-size: 9.5px;
    }

    html.density-compact .status-card {
      margin: 6px 10px 10px;
      padding: 10px 12px;
      font-size: 11.5px;
    }

    html.density-compact .chat-top {
      padding: 10px 16px;
      gap: 12px;
    }

    html.density-compact .chat-title strong {
      font-size: 14.5px;
    }

    html.density-compact .chat-title span {
      font-size: 11.5px;
    }

    html.density-compact .badge {
      padding: 3px 8px;
      font-size: 10.5px;
    }

    html.density-compact .messages {
      padding: 16px 16px;
      gap: 12px;
    }

    html.density-compact .message {
      gap: 8px;
      grid-template-columns: 32px minmax(0, 1fr);
    }

    html.density-compact .message.user {
      grid-template-columns: minmax(0, 1fr) 32px;
    }

    html.density-compact .avatar {
      width: 32px;
      height: 32px;
      font-size: 11px;
      border-radius: 9px;
    }

    html.density-compact .bubble-content {
      padding: 10px 12px;
      font-size: 13.5px;
      line-height: 1.5;
    }

    html.density-compact .bubble-head {
      padding: 7px 10px;
      font-size: 11px;
    }

    html.density-compact .bubble-meta {
      padding: 0 10px 10px;
      gap: 5px;
    }

    html.density-compact .composer {
      padding: 10px 16px 14px;
    }

    html.density-compact .composer-form {
      gap: 8px;
      padding: 6px 6px 6px 10px;
      border-radius: 14px;
    }

    html.density-compact .composer-form textarea {
      min-height: 40px;
      font-size: 13.5px;
      padding: 8px 2px;
    }

    html.density-compact .send {
      width: 40px;
      min-height: 40px;
      border-radius: 11px;
    }

    html.density-compact .inspector-head {
      padding: 12px;
    }

    html.density-compact .inspector-body {
      padding: 10px;
      gap: 10px;
    }

    html.density-compact .panel-header {
      padding: 10px 12px;
    }

    html.density-compact .guide,
    html.density-compact .settings,
    html.density-compact .marketplace {
      padding: 18px;
    }

    html.density-compact .guide-hero,
    html.density-compact .marketplace-hero {
      padding: 18px 20px;
      border-radius: var(--r-lg);
    }

    html.density-compact .guide-hero h2,
    html.density-compact .marketplace-hero h2 {
      font-size: 22px;
    }

    html.density-compact .feature-grid {
      gap: 10px;
    }

    html.density-compact .feature-card,
    html.density-compact .persona-card {
      padding: 12px 13px;
      gap: 8px;
      border-radius: var(--r-md);
    }

    html.density-compact .marketplace-grid {
      gap: 12px;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    }

    html.density-compact .persona-card h3 {
      font-size: 15px;
    }

    html.density-compact .settings-tabs button,
    html.density-compact .guide-controls button {
      min-height: 30px;
      padding: 0 12px;
      font-size: 11.5px;
    }

    html.density-compact .imagegen-shell,
    html.density-compact .videogen-shell {
      padding: 14px 16px !important;
      gap: 12px !important;
    }

    html.density-compact .imagegen-card,
    html.density-compact .imagegen-sidebar,
    html.density-compact .audiogen-card {
      padding: 12px !important;
      gap: 10px !important;
    }

    html.density-compact .empty {
      padding: 22px 16px;
      gap: 10px;
    }

    html.density-compact .empty h2 {
      font-size: 20px;
    }

    html.density-compact .empty-mark {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      font-size: 16px;
    }

    html.density-compact .secondary {
      min-height: 34px;
      font-size: 12px;
      padding: 0 11px;
    }

    html.density-compact button.primary,
    html.density-compact .primary {
      min-height: 36px;
      font-size: 12.5px;
      padding: 0 14px;
    }

    @media (max-width: 1120px) {
      html.density-compact {
        --shell-w-expanded: 220px;
      }
    }

    /* ============================================================
       LIVING CONTINUUM — dissolve the rigid box lattice
       Hierarchy by light, space, and type — not borders
       ============================================================ */

    /* Film grain — subtle materiality */
    .grain {
      position: fixed;
      inset: 0;
      z-index: 1;
      pointer-events: none;
      opacity: 0.035;
      mix-blend-mode: overlay;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
      background-size: 180px 180px;
    }
    .light .grain { opacity: 0.028; mix-blend-mode: multiply; }

    .app { position: relative; z-index: 2; }

    /* ============================================================
       SHELL INSTRUMENT — rail + nav + sessions + chrome = one system
       ============================================================ */
    .rail {
      border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
      background:
        linear-gradient(180deg, rgba(12, 15, 22, 0.92) 0%, rgba(7, 9, 14, 0.94) 100%) !important;
      box-shadow: none !important;
      backdrop-filter: blur(28px) saturate(1.25) !important;
      overflow: hidden !important;
      min-width: 0 !important; /* allow grid track shrink */
      max-width: 100%;
      width: auto;
    }
    .light .rail {
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(245, 247, 251, 0.92) 100%) !important;
      border-right-color: rgba(15, 23, 42, 0.08) !important;
    }
    .rail::before {
      left: 0 !important;
      width: 2px !important;
      background: linear-gradient(
        180deg,
        transparent 0%,
        rgba(255, 122, 77, 0.45) 18%,
        rgba(251, 146, 60, 0.35) 48%,
        rgba(52, 211, 153, 0.28) 78%,
        transparent 100%
      ) !important;
      opacity: 0.85 !important;
      filter: none;
    }
    .rail::after { display: none !important; }

    /* Brand = shell header */
    .brand {
      border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
      padding: 16px var(--shell-pad) 12px !important;
      background: transparent !important;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .brand::after { display: none !important; }
    .brand-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      min-width: 0;
    }
    .brand-mark {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      min-width: 0;
    }
    .brand-mark .pulse-ring {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #ffc4a8, #e85d2a 55%, #f59e0b);
      box-shadow: 0 0 0 0 rgba(255, 122, 77, 0.4);
      animation: pulseRing 2.8s ease-out infinite;
      flex-shrink: 0;
    }
    @keyframes pulseRing {
      0% { box-shadow: 0 0 0 0 rgba(255, 122, 77, 0.4); }
      70% { box-shadow: 0 0 0 8px rgba(255, 122, 77, 0); }
      100% { box-shadow: 0 0 0 0 rgba(255, 122, 77, 0); }
    }
    .brand h1 {
      font-family: var(--font-display) !important;
      font-size: 16px !important;
      font-weight: 750 !important;
      letter-spacing: -0.03em !important;
      line-height: 1.1 !important;
      background: linear-gradient(125deg, #fff7f2 0%, #ffd4bc 42%, #ff9a6b 100%) !important;
      -webkit-background-clip: text !important;
      background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
      text-shadow: none !important;
      filter: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .light .brand h1 {
      background: linear-gradient(125deg, #0c1222 0%, #c2410c 50%, #d97706 100%) !important;
      -webkit-background-clip: text !important;
      background-clip: text !important;
    }
    .brand p,
    .brand-tagline {
      display: block !important;
      margin: 2px 0 0 !important;
      font-size: 10px !important;
      font-weight: 650 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      color: var(--shell-faint) !important;
      opacity: 0.9 !important;
      line-height: 1.3 !important;
    }
    .brand-tagline strong {
      color: var(--shell-muted);
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: none;
    }
    .brand-actions {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-shrink: 0;
    }
    .brand > .account-wrap {
      margin-top: 0 !important;
    }
    .brand > .account-wrap .account-btn {
      height: var(--shell-item-h);
      border-radius: var(--shell-radius);
      border: 0 !important;
      background: var(--shell-fill) !important;
      font-size: 12.5px;
      padding: 0 11px;
    }

    /* One chrome button language */
    .theme-toggle,
    .density-toggle,
    .settings-icon,
    .rail-collapse {
      width: 32px !important;
      height: 32px !important;
      min-height: 32px !important;
      border: 0 !important;
      background: var(--shell-fill) !important;
      border-radius: var(--shell-radius) !important;
      color: var(--shell-muted) !important;
      box-shadow: none !important;
      display: grid !important;
      place-items: center;
      cursor: pointer;
      padding: 0;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out) !important;
    }
    .theme-toggle:hover,
    .density-toggle:hover,
    .settings-icon:hover,
    .rail-collapse:hover {
      background: var(--shell-fill-hover) !important;
      color: var(--text) !important;
      transform: none !important;
      box-shadow: none !important;
    }
    .density-toggle.active,
    .rail-collapse.active {
      color: var(--blue) !important;
      background: rgba(255, 122, 77, 0.10) !important;
    }
    .theme-toggle svg,
    .density-toggle svg,
    .rail-collapse svg {
      width: 15px !important;
      height: 15px !important;
    }
    .rail-collapse svg {
      transition: transform var(--dur) var(--ease-spring);
    }
    html.rail-collapsed .rail-collapse svg {
      transform: rotate(180deg);
    }

    /* Body of shell */
    .rail-section {
      padding: 10px var(--shell-pad) 12px !important;
      gap: var(--shell-section-gap) !important;
      display: grid;
      align-content: start;
      overflow: auto;
      min-height: 0;
    }

    /* Section labels — one quiet style */
    .rail-section > .group > label,
    .rail-section .sessions-head label,
    .group label {
      color: var(--shell-faint) !important;
      font-size: 10px !important;
      font-weight: 650 !important;
      letter-spacing: 0.08em !important;
      text-transform: uppercase !important;
      margin: 0 0 2px 2px !important;
      opacity: 1 !important;
    }
    .group {
      gap: 6px !important;
    }
    .group + .group::before {
      top: calc(var(--shell-section-gap) / -2 - 0.5px) !important;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent) !important;
    }
    .light .group + .group::before {
      background: linear-gradient(90deg, transparent, rgba(15,23,42,0.06), transparent) !important;
    }

    /* Nav + session chips share shell-item language */
    .nav {
      background: transparent !important;
      border: 0 !important;
      padding: 0 !important;
      gap: var(--shell-gap) !important;
      border-radius: 0 !important;
      box-shadow: none !important;
      backdrop-filter: none !important;
    }
    .nav button {
      border-radius: var(--shell-radius) !important;
      font-weight: 600 !important;
      letter-spacing: -0.01em !important;
      min-height: var(--shell-item-h) !important;
      padding: 0 11px !important;
      gap: 10px !important;
      justify-content: flex-start !important;
      color: var(--shell-muted) !important;
      background: transparent !important;
      box-shadow: none !important;
      transform: none !important;
      transition:
        color var(--dur) var(--ease-out),
        background var(--dur) var(--ease-out),
        box-shadow var(--dur) var(--ease-out),
        gap var(--shell-dur) var(--shell-ease),
        padding var(--shell-dur) var(--shell-ease),
        min-height var(--shell-dur) var(--shell-ease) !important;
    }
    html.rail-collapsed .nav button {
      gap: 0 !important;
      padding: 0 !important;
    }
    .nav button:hover {
      color: var(--text) !important;
      background: var(--shell-fill-hover) !important;
      transform: none !important;
    }
    .nav button.active {
      color: var(--text) !important;
      background: var(--shell-fill-active) !important;
      box-shadow: inset 2px 0 0 var(--shell-edge) !important;
      font-weight: 650 !important;
    }
    .nav button.active::before { display: none !important; }
    .nav button svg {
      width: 16px !important;
      height: 16px !important;
      opacity: 0.88;
      filter: none !important;
      transform: none !important;
    }
    .nav button:hover svg,
    .nav button.active svg {
      opacity: 1;
      transform: none !important;
    }
    .nav button.active svg {
      filter: drop-shadow(0 0 5px rgba(255, 122, 77, 0.3)) !important;
    }

    /* Controls match list items — solid fills so hover stays dark */
    .rail select,
    .rail input {
      border: 0 !important;
      border-radius: var(--shell-radius) !important;
      height: var(--shell-item-h) !important;
      font-size: 12.5px !important;
      color: var(--text) !important;
      box-shadow: none !important;
    }
    .rail input {
      background: #121722 !important;
      padding: 0 11px !important;
    }
    .rail select {
      color-scheme: dark !important;
      background-color: #121722 !important;
      background-image: linear-gradient(45deg, transparent 50%, #8b95a8 50%),
                        linear-gradient(135deg, #8b95a8 50%, transparent 50%) !important;
      background-position: calc(100% - 14px) calc(50% - 2px), calc(100% - 9px) calc(50% - 2px) !important;
      background-size: 5px 5px, 5px 5px !important;
      background-repeat: no-repeat !important;
      padding: 0 28px 0 11px !important;
    }
    .rail select:hover {
      color: #ffffff !important;
      background-color: #1a2230 !important;
      background-image: linear-gradient(45deg, transparent 50%, #c8d0dc 50%),
                        linear-gradient(135deg, #c8d0dc 50%, transparent 50%) !important;
      background-position: calc(100% - 14px) calc(50% - 2px), calc(100% - 9px) calc(50% - 2px) !important;
      background-size: 5px 5px, 5px 5px !important;
      background-repeat: no-repeat !important;
    }
    .rail select:focus,
    .rail input:focus {
      outline: none !important;
      box-shadow: inset 0 0 0 1px rgba(255, 122, 77, 0.35) !important;
    }
    .rail select:focus {
      color: #ffffff !important;
      background-color: #1a2230 !important;
    }
    .rail input:focus {
      background: #1a2230 !important;
    }
    .rail option,
    .rail optgroup {
      background-color: #0c1017 !important;
      color: #eef1f7 !important;
    }
    .rail option:checked {
      background-color: #15324a !important;
      color: #ffffff !important;
    }
    .light .rail input {
      background: #eef1f6 !important;
      color: var(--text) !important;
    }
    .light .rail select {
      color-scheme: light !important;
      color: var(--text) !important;
      background-color: #eef1f6 !important;
      background-image: linear-gradient(45deg, transparent 50%, #64748b 50%),
                        linear-gradient(135deg, #64748b 50%, transparent 50%) !important;
      background-position: calc(100% - 14px) calc(50% - 2px), calc(100% - 9px) calc(50% - 2px) !important;
      background-size: 5px 5px, 5px 5px !important;
      background-repeat: no-repeat !important;
    }
    .light .rail select:hover,
    .light .rail select:focus {
      background-color: #e2e8f0 !important;
      color: var(--text) !important;
    }
    .light .rail option,
    .light .rail optgroup {
      background-color: #ffffff !important;
      color: #0c1222 !important;
    }
    .light .rail option:checked {
      background-color: #e0f2fe !important;
      color: #0c1222 !important;
    }

    /* Global selects outside the rail (settings, studios) */
    .settings select,
    .imagegen select,
    .videogen select,
    .audiogen select,
    .marketplace select {
      color-scheme: dark;
      background-color: var(--surface-2);
      color: var(--text);
    }
    .settings select:hover,
    .imagegen select:hover,
    .videogen select:hover,
    .audiogen select:hover {
      background-color: var(--surface-3);
      color: var(--text);
    }
    .light .settings select,
    .light .imagegen select,
    .light .videogen select,
    .light .audiogen select {
      color-scheme: light;
      background-color: #ffffff;
      color: var(--text);
    }
    .rail .hint {
      font-size: 11px !important;
      color: var(--shell-faint) !important;
      line-height: 1.4;
      padding: 0 2px;
    }
    .rail .inline-field {
      gap: 6px;
    }
    .rail .inline-field .secondary,
    .rail .secondary {
      min-height: var(--shell-item-h) !important;
      height: var(--shell-item-h);
      border: 0 !important;
      border-radius: var(--shell-radius) !important;
      background: var(--shell-fill) !important;
      box-shadow: none !important;
      font-size: 12px !important;
      padding: 0 12px !important;
      transform: none !important;
    }
    .rail .secondary:hover {
      background: var(--shell-fill-hover) !important;
      transform: none !important;
      border-color: transparent !important;
    }

    /* Footer status */
    .rail-footer {
      padding: 10px var(--shell-pad) 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.04);
    }
    .light .rail-footer,
    .light .brand {
      border-color: rgba(15, 23, 42, 0.06) !important;
    }
    .status-card {
      margin: 0 !important;
      padding: 10px 11px !important;
      border: 0 !important;
      border-radius: var(--shell-radius) !important;
      background: var(--shell-fill) !important;
      box-shadow: none !important;
      font-size: 11.5px !important;
      line-height: 1.4 !important;
      color: var(--shell-muted) !important;
    }
    .status-card:hover {
      border-color: transparent !important;
      box-shadow: none !important;
      background: var(--shell-fill-hover) !important;
    }

    /* —— Chat stage — same material language as shell —— */
    .chat-top {
      border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
      background: rgba(8, 10, 14, 0.45) !important;
      backdrop-filter: blur(20px) saturate(1.2) !important;
      padding: 12px 24px !important;
      box-shadow: none !important;
      min-height: 56px;
      align-items: center;
    }
    .light .chat-top {
      background: rgba(255, 255, 255, 0.55) !important;
      border-bottom-color: rgba(15, 23, 42, 0.06) !important;
    }
    .chat-title strong {
      font-family: var(--font-display);
      font-size: 15px !important;
      font-weight: 700 !important;
      letter-spacing: -0.025em !important;
    }
    .chat-title span {
      font-size: 11.5px !important;
      opacity: 0.8;
      color: var(--shell-faint) !important;
    }
    .badge {
      border: 0 !important;
      background: var(--shell-fill) !important;
      backdrop-filter: none;
      font-weight: 600 !important;
      letter-spacing: 0.01em;
      border-radius: 999px !important;
      padding: 4px 10px !important;
      font-size: 11px !important;
    }
    .badge.ok { background: rgba(52, 211, 153, 0.12) !important; color: var(--green) !important; }
    .badge.warn { background: rgba(224, 179, 90, 0.12) !important; color: var(--amber) !important; }
    .badge.info { background: rgba(255, 122, 77, 0.12) !important; color: var(--blue) !important; }
    .badge.bad { background: rgba(248, 113, 113, 0.12) !important; color: var(--red) !important; }

    /* Trust as a quiet living ticker */
    .trust-strip {
      border-bottom: none !important;
      background: transparent !important;
      padding: 4px 24px 8px !important;
      gap: 6px 16px !important;
      font-size: 10.5px !important;
      letter-spacing: 0.03em !important;
      color: var(--shell-faint) !important;
      opacity: 0.9;
    }
    .trust-item {
      position: relative;
      padding-left: 10px;
    }
    .trust-item::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.18);
      transform: translateY(-50%);
    }
    .trust-strip.ok .trust-item#trust-verify::before {
      background: var(--green);
      box-shadow: 0 0 8px rgba(52, 211, 153, 0.55);
    }
    .trust-strip.bad .trust-item#trust-verify::before {
      background: var(--red);
      box-shadow: 0 0 8px rgba(248, 113, 113, 0.45);
    }

    /* Messages — editorial stage, not card stack */
    .messages {
      padding: 12px 28px 8px !important;
      gap: 8px !important;
      mask-image: linear-gradient(to bottom, transparent 0, #000 12px, #000 calc(100% - 8px), transparent 100%);
      -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 12px, #000 calc(100% - 8px), transparent 100%);
    }
    .message {
      max-width: var(--stage) !important;
      margin-inline: auto;
      width: 100%;
      gap: 14px !important;
      animation: msgIn 0.45s var(--ease-out) both;
    }
    .message + .message { margin-top: 6px; }
    .message.user { max-width: min(560px, 100%) !important; }

    .avatar {
      width: 34px !important;
      height: 34px !important;
      border-radius: 50% !important;
      border: 1px solid transparent !important;
      background: linear-gradient(145deg, rgba(255, 122, 77, 0.12), rgba(245, 158, 11, 0.08)) !important;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.04), 0 4px 16px -4px rgba(255, 122, 77, 0.25) !important;
      font-size: 11px !important;
      font-weight: 700 !important;
      letter-spacing: -0.02em;
      align-self: flex-start;
      margin-top: 4px;
    }
    .message.user .avatar {
      background: linear-gradient(145deg, rgba(255, 122, 77, 0.22), rgba(232, 93, 42, 0.12)) !important;
    }
    .message.assistant .avatar {
      color: #ffc4a8 !important;
    }

    /* Assistant: borderless prose, living document */
    .message.assistant .bubble,
    .message:not(.user) .bubble {
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      backdrop-filter: none !important;
      border-radius: 0 !important;
      overflow: visible !important;
      position: relative;
    }
    .message.assistant .bubble::before,
    .message:not(.user) .bubble::before {
      content: '';
      position: absolute;
      left: -14px;
      top: 10px;
      bottom: 10px;
      width: 2px;
      border-radius: 2px;
      background: linear-gradient(
        180deg,
        rgba(255, 122, 77, 0.0),
        rgba(255, 122, 77, 0.35) 20%,
        rgba(251, 146, 60, 0.30) 60%,
        rgba(52, 211, 153, 0.0)
      );
      opacity: 0.7;
    }
    .message.assistant .bubble-head,
    .message:not(.user) .bubble-head {
      border: none !important;
      background: transparent !important;
      padding: 0 0 6px !important;
      font-size: 11px !important;
      font-weight: 600 !important;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--faint) !important;
      opacity: 0.75;
    }
    .message.assistant .bubble-content,
    .message:not(.user) .bubble-content {
      padding: 0 !important;
      font-size: 15.5px !important;
      line-height: 1.72 !important;
      letter-spacing: -0.011em !important;
      color: var(--text);
    }
    .message.assistant .bubble-meta,
    .message:not(.user) .bubble-meta {
      padding: 10px 0 0 !important;
      gap: 6px !important;
      opacity: 0.85;
    }

    /* User: soft organic speech — asymmetric radius */
    .message.user .bubble {
      border: 1px solid rgba(255, 122, 77, 0.14) !important;
      background: var(--user-bubble-bg) !important;
      border-radius: 22px 22px 6px 22px !important;
      box-shadow:
        0 12px 36px -16px rgba(232, 93, 42, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
      backdrop-filter: blur(12px) saturate(1.15) !important;
      overflow: hidden !important;
    }
    .light .message.user .bubble {
      border-color: rgba(234, 88, 12, 0.16) !important;
      box-shadow: 0 10px 28px -14px rgba(234, 88, 12, 0.18) !important;
    }
    .message.user .bubble-head {
      display: none !important;
    }
    .message.user .bubble-content {
      padding: 13px 16px !important;
      font-size: 15px !important;
      line-height: 1.55 !important;
    }
    .message.user .bubble-meta {
      padding: 0 14px 12px !important;
    }

    /* Thinking — gentle bloom, not a boxed alert */
    .message.thinking-message .bubble {
      border: none !important;
      background: transparent !important;
      border-radius: 0 !important;
    }
    .message.thinking-message .bubble-content {
      color: var(--muted);
      font-size: 14px !important;
    }
    .thinking-row {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: var(--r-pill);
      background: rgba(255, 122, 77, 0.06);
      border: 1px solid rgba(255, 122, 77, 0.12);
    }

    .message.rejected .bubble {
      background: var(--rejected-bg) !important;
      border-radius: 16px !important;
      border: 1px solid rgba(248, 113, 113, 0.25) !important;
      padding: 4px 0;
    }
    .message.rejected.assistant .bubble::before,
    .message.rejected:not(.user) .bubble::before {
      background: linear-gradient(180deg, transparent, rgba(248,113,113,0.55), transparent);
    }

    /* Streaming caret */
    .message.streaming .bubble-content::after {
      content: '';
      display: inline-block;
      width: 2px;
      height: 1.05em;
      margin-left: 3px;
      vertical-align: text-bottom;
      background: linear-gradient(180deg, #ffc4a8, #fbbf24);
      border-radius: 1px;
      animation: caretBlink 1s steps(1) infinite;
      box-shadow: 0 0 10px rgba(255, 122, 77, 0.55);
    }
    @keyframes caretBlink {
      0%, 45% { opacity: 1; }
      50%, 100% { opacity: 0; }
    }

    /* Empty state — invitation, not a card */
    .empty {
      border: none !important;
      background:
        radial-gradient(ellipse 80% 60% at 50% 30%, rgba(255, 122, 77, 0.08), transparent 70%),
        transparent !important;
      padding: 48px 24px !important;
      gap: 16px !important;
      max-width: 520px;
    }
    .empty-mark {
      width: 64px !important;
      height: 64px !important;
      border-radius: 50% !important;
      border: 1px solid rgba(255, 122, 77, 0.20) !important;
      background:
        radial-gradient(circle at 35% 30%, rgba(125, 211, 252, 0.35), transparent 50%),
        linear-gradient(145deg, rgba(232, 93, 42, 0.18), rgba(245, 158, 11, 0.14)) !important;
      box-shadow:
        0 0 0 8px rgba(255, 122, 77, 0.04),
        0 20px 48px -12px rgba(232, 93, 42, 0.35) !important;
      font-family: var(--font-display);
      animation: emptyBreathe 5s ease-in-out infinite;
    }
    @keyframes emptyBreathe {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 122, 77, 0.04), 0 20px 48px -12px rgba(232, 93, 42, 0.35); }
      50% { transform: scale(1.04); box-shadow: 0 0 0 14px rgba(255, 122, 77, 0.06), 0 24px 56px -10px rgba(232, 93, 42, 0.42); }
    }
    .empty h2 {
      font-family: var(--font-serif) !important;
      font-size: 32px !important;
      font-weight: 400 !important;
      letter-spacing: -0.02em !important;
      line-height: 1.15 !important;
      background: linear-gradient(180deg, var(--text) 0%, var(--muted) 160%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .empty p {
      font-size: 15px !important;
      line-height: 1.65 !important;
      max-width: 36ch !important;
    }
    .empty-hints span {
      border: 1px solid transparent !important;
      background: rgba(255, 255, 255, 0.035) !important;
      padding: 6px 13px !important;
      font-size: 11.5px !important;
      letter-spacing: 0.02em;
      color: var(--muted) !important;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out), transform var(--dur) var(--ease-spring);
    }
    .empty-hints span:hover {
      background: rgba(255, 122, 77, 0.08) !important;
      color: var(--text) !important;
      transform: translateY(-1px);
    }

    /* Composer — floating glass dock */
    .composer {
      border-top: none !important;
      background: linear-gradient(
        180deg,
        transparent 0%,
        rgba(6, 8, 12, 0.55) 28%,
        rgba(6, 8, 12, 0.88) 100%
      ) !important;
      backdrop-filter: blur(20px) saturate(1.25) !important;
      padding: 8px 28px 22px !important;
    }
    .light .composer {
      background: linear-gradient(
        180deg,
        transparent 0%,
        rgba(243, 245, 249, 0.55) 28%,
        rgba(243, 245, 249, 0.92) 100%
      ) !important;
    }
    .composer-options {
      max-width: var(--stage) !important;
      margin-bottom: 8px !important;
      opacity: 0.8;
    }
    .composer-form {
      max-width: var(--stage) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      border-radius: 24px !important;
      background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)) !important;
      box-shadow:
        0 16px 48px -16px rgba(0, 0, 0, 0.55),
        0 0 0 1px rgba(255, 255, 255, 0.03) inset,
        0 -1px 0 rgba(255, 122, 77, 0.05) !important;
      padding: 8px 8px 8px 18px !important;
      gap: 10px !important;
      transition: border-color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out), transform var(--dur) var(--ease-out) !important;
    }
    .light .composer-form {
      background: linear-gradient(180deg, #ffffff, #f7f9fc) !important;
      border-color: rgba(15, 23, 42, 0.08) !important;
      box-shadow: 0 16px 40px -18px rgba(15, 23, 42, 0.14), 0 0 0 1px rgba(15, 23, 42, 0.03) inset !important;
    }
    .composer-form:focus-within {
      border-color: rgba(255, 122, 77, 0.32) !important;
      box-shadow:
        var(--glow-blue),
        0 20px 52px -14px rgba(232, 93, 42, 0.22) !important;
      transform: translateY(-1px);
    }
    .composer-form textarea {
      min-height: 44px !important;
      font-size: 15.5px !important;
      line-height: 1.5 !important;
      padding: 11px 4px !important;
    }
    .composer-form textarea::placeholder {
      color: var(--faint);
      opacity: 0.75;
    }
    .send {
      width: 46px !important;
      min-height: 46px !important;
      border-radius: 50% !important;
      background: linear-gradient(145deg, #ff8a5c 0%, #e85d2a 42%, #f59e0b 100%) !important;
      box-shadow:
        0 8px 24px -4px rgba(232, 93, 42, 0.50),
        inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
    }
    .send:hover {
      transform: translateY(-2px) scale(1.04) !important;
    }
    .composer-warning {
      max-width: var(--stage) !important;
      border-radius: 16px !important;
      border-color: transparent !important;
      background: rgba(224, 179, 90, 0.10) !important;
    }

    /* Inspector — mirror shell language on the right */
    .inspector {
      border-left: 1px solid rgba(255, 255, 255, 0.06) !important;
      background:
        linear-gradient(180deg, rgba(12, 15, 22, 0.92) 0%, rgba(7, 9, 14, 0.94) 100%) !important;
      backdrop-filter: blur(28px) saturate(1.25) !important;
    }
    .light .inspector {
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(245, 247, 251, 0.92) 100%) !important;
      border-left-color: rgba(15, 23, 42, 0.08) !important;
    }
    .inspector-head {
      border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
      padding: 14px 14px 12px !important;
      min-height: 56px;
      align-items: center;
    }
    .light .inspector-head {
      border-bottom-color: rgba(15, 23, 42, 0.06) !important;
    }
    .inspector-head strong {
      font-family: var(--font-display);
      font-size: 14px !important;
      letter-spacing: -0.02em;
    }
    .inspector-head span {
      font-size: 11.5px !important;
      color: var(--shell-faint) !important;
    }
    .inspector-body {
      padding: 12px !important;
      gap: 8px !important;
    }
    .panel {
      border: 0 !important;
      border-radius: var(--shell-radius) !important;
      background: var(--shell-fill) !important;
      box-shadow: none !important;
    }
    .panel:hover {
      border-color: transparent !important;
      background: var(--shell-fill-hover) !important;
    }
    .light .panel {
      background: var(--shell-fill) !important;
    }
    .panel-header {
      padding: 11px 12px !important;
    }
    .panel-header:hover {
      background: transparent;
    }

    /* Guide / marketplace / settings — softer cards */
    .guide-hero,
    .marketplace-hero {
      border: 1px solid transparent !important;
      border-radius: 24px !important;
      box-shadow: var(--shadow-soft) !important;
    }
    .guide-hero h2,
    .marketplace-hero h2 {
      font-family: var(--font-serif) !important;
      font-weight: 400 !important;
      letter-spacing: -0.02em !important;
    }
    .feature-card,
    .persona-card {
      border: 1px solid transparent !important;
      border-radius: 18px !important;
      background: rgba(255, 255, 255, 0.03) !important;
      box-shadow: none !important;
      transition: background var(--dur) var(--ease-out), transform var(--dur) var(--ease-spring), box-shadow var(--dur) var(--ease-out) !important;
    }
    .feature-card:hover,
    .persona-card:hover {
      background: rgba(255, 255, 255, 0.055) !important;
      transform: translateY(-2px);
      box-shadow: 0 16px 40px -18px rgba(0, 0, 0, 0.45) !important;
      border-color: transparent !important;
    }
    .light .feature-card,
    .light .persona-card {
      background: rgba(255, 255, 255, 0.72) !important;
    }
    .settings-tabs,
    .guide-controls,
    .auth-tabs,
    .provider-subtabs {
      border: 1px solid transparent !important;
      background: rgba(255, 255, 255, 0.03) !important;
      border-radius: 16px !important;
    }
    .settings-tabs button.active,
    .guide-controls button.active {
      box-shadow: 0 4px 16px -4px rgba(232, 93, 42, 0.35);
    }

    /* Auth — cinematic */
    .auth-card {
      border: 1px solid rgba(255, 255, 255, 0.06) !important;
      border-radius: 28px !important;
      background:
        radial-gradient(ellipse 80% 50% at 50% 0%, rgba(255, 122, 77, 0.10), transparent 60%),
        linear-gradient(165deg, rgba(14, 18, 28, 0.96), rgba(8, 10, 16, 0.98)) !important;
    }
    .auth-logo {
      border-radius: 50% !important;
      font-family: var(--font-display);
    }
    .auth-card h2 {
      font-family: var(--font-serif) !important;
      font-weight: 400 !important;
      font-size: 28px !important;
    }

    /* Command palette */
    .command-palette {
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      border-radius: 20px !important;
      background: rgba(12, 16, 24, 0.92) !important;
      backdrop-filter: blur(28px) saturate(1.3);
      box-shadow: var(--shadow-float) !important;
    }
    .command-palette-backdrop {
      background: rgba(2, 4, 10, 0.48) !important;
      backdrop-filter: blur(8px);
    }

    /* Secondary buttons — less boxed */
    .secondary {
      border: 1px solid transparent !important;
      background: rgba(255, 255, 255, 0.04) !important;
      border-radius: 12px !important;
      box-shadow: none !important;
    }
    .secondary:hover {
      background: rgba(255, 255, 255, 0.07) !important;
      border-color: transparent !important;
    }
    button.primary, .primary {
      border-radius: 12px !important;
      background: linear-gradient(145deg, #ff8a5c 0%, #e85d2a 42%, #f59e0b 100%) !important;
    }

    /* Image/video studios — dissolve hard cards */
    /* studio surfaces handled in FORGE STUDIOS block */

    /* Citation soft chip */
    .citation-box {
      border: 1px solid transparent !important;
      background: rgba(255, 122, 77, 0.06) !important;
      border-radius: 14px !important;
      border-left: 2px solid rgba(255, 122, 77, 0.45) !important;
    }

    /* Mobile adjustments for continuum */
    @media (max-width: 760px) {
      .message.assistant .bubble::before,
      .message:not(.user) .bubble::before { display: none; }
      .messages { padding: 10px 14px !important; mask-image: none; -webkit-mask-image: none; }
      .composer { padding: 8px 12px 14px !important; }
      .chat-top { padding: 12px 14px 8px !important; }
      .trust-strip { padding: 0 14px 8px !important; }
      .empty h2 { font-size: 26px !important; }
      .message.user .bubble { border-radius: 18px 18px 6px 18px !important; }
      .composer-form { border-radius: 20px !important; }
      .send { border-radius: 50% !important; width: 44px !important; min-height: 44px !important; }
      .composer-form { grid-template-columns: minmax(0, 1fr) auto !important; }
      .send { width: 44px !important; }
    }

    @media (max-width: 640px) {
      .composer-form { grid-template-columns: minmax(0, 1fr) auto !important; }
      .send { width: 44px !important; min-height: 44px !important; border-radius: 50% !important; }
    }

    html.density-compact .message.assistant .bubble-content,
    html.density-compact .message:not(.user) .bubble-content {
      font-size: 14px !important;
      line-height: 1.58 !important;
    }
    html.density-compact .empty h2 { font-size: 24px !important; }
    html.density-compact .composer-form { border-radius: 18px !important; }
    html.density-compact .messages { gap: 4px !important; }

    /* —— Session chips = same shell-item as nav —— */
    .sr-only {
      position: absolute !important;
      width: 1px !important;
      height: 1px !important;
      padding: 0 !important;
      margin: -1px !important;
      overflow: hidden !important;
      clip: rect(0, 0, 0, 0) !important;
      white-space: nowrap !important;
      border: 0 !important;
    }
    .sessions-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      min-height: 16px;
    }
    .sessions-head label { margin: 0 0 0 2px !important; }
    .sessions-count {
      font-size: 10px;
      font-weight: 650;
      color: var(--shell-faint);
      font-variant-numeric: tabular-nums;
      letter-spacing: 0.04em;
      padding: 0 4px;
    }
    .session-chips {
      display: flex;
      flex-direction: column;
      gap: var(--shell-gap);
      max-height: 152px;
      overflow: auto;
      padding: 0;
      margin: 0;
      scrollbar-width: thin;
    }
    .session-chip {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      width: 100%;
      min-height: var(--shell-item-h);
      text-align: left;
      border: 0;
      background: transparent;
      color: var(--shell-muted);
      border-radius: var(--shell-radius);
      padding: 0 11px;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.01em;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-out);
    }
    .session-chip:hover {
      color: var(--text);
      background: var(--shell-fill-hover);
    }
    .session-chip.active {
      color: var(--text);
      background: var(--shell-fill-active);
      box-shadow: inset 2px 0 0 var(--shell-edge);
    }
    .session-chip-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .session-chip-meta {
      font-size: 10px;
      font-weight: 700;
      color: var(--shell-faint);
      font-variant-numeric: tabular-nums;
      background: transparent;
      border-radius: 0;
      padding: 0;
      flex-shrink: 0;
      opacity: 0.85;
    }
    .session-chip.active .session-chip-meta {
      color: var(--blue);
      background: transparent;
    }

    /* Prompt pills — stage language, slightly softer */
    .prompt-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-top: 6px;
      max-width: 440px;
      margin-inline: auto;
    }
    .prompt-pill {
      border: 0;
      background: var(--shell-fill);
      color: var(--shell-muted);
      border-radius: var(--r-pill);
      padding: 9px 14px;
      font: inherit;
      font-size: 12.5px;
      font-weight: 600;
      letter-spacing: -0.01em;
      cursor: pointer;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out), transform var(--dur-fast) var(--ease-spring);
    }
    .prompt-pill:hover {
      color: var(--text);
      background: var(--shell-fill-active);
      transform: translateY(-1px);
    }

    /* ============================================================
       COLLAPSED SHELL — bulletproof tuck
       Explicit grid tracks + min-width:0 + hide non-icon chrome
       ============================================================ */
    @media (min-width: 761px) {
      /* Variable for @property animation (Chrome/Edge/Safari recent) */
      html.rail-collapsed {
        --shell-w: 72px;
        --shell-pad: 10px;
      }

      /* Explicit track override — always wins over media/density rules */
      html.rail-collapsed .app {
        grid-template-columns: 72px minmax(0, 1fr) var(--inspector-width, 360px) !important;
      }
      html.rail-collapsed.density-compact .app {
        grid-template-columns: 68px minmax(0, 1fr) var(--inspector-width, 300px) !important;
      }

      /* Rail must be allowed to shrink below content intrinsic width */
      html.rail-collapsed .rail {
        min-width: 0 !important;
        width: 100% !important;
        max-width: 72px !important;
        overflow: hidden !important;
      }
      html.rail-collapsed.density-compact .rail {
        max-width: 68px !important;
      }

      /* Hard-hide expandable chrome so min-content can't block tuck */
      html.rail-collapsed .rail-section .group,
      html.rail-collapsed .rail-footer,
      html.rail-collapsed .account-wrap,
      html.rail-collapsed .brand-mark h1,
      html.rail-collapsed .brand p,
      html.rail-collapsed .brand-tagline,
      html.rail-collapsed .brand-actions .density-toggle,
      html.rail-collapsed .nav-label {
        display: none !important;
      }

      html.rail-collapsed .brand {
        padding: 14px 6px 8px !important;
        gap: 10px !important;
        border-bottom: 0 !important;
        align-items: center;
      }
      html.rail-collapsed .brand-row {
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        width: 100%;
      }
      html.rail-collapsed .brand-mark {
        justify-content: center !important;
        width: auto !important;
      }
      html.rail-collapsed .brand-mark .pulse-ring {
        width: 11px;
        height: 11px;
        display: block !important;
      }
      /* Theme + collapse remain in icon strip */
      html.rail-collapsed .brand-actions {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 6px !important;
        width: 100%;
      }
      html.rail-collapsed .brand-actions .theme-toggle,
      html.rail-collapsed .brand-actions .rail-collapse {
        display: grid !important;
        width: 36px !important;
        height: 36px !important;
      }

      html.rail-collapsed .rail-section {
        padding: 4px 8px 12px !important;
        gap: 4px !important;
        overflow: hidden !important;
      }
      html.rail-collapsed .nav {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 3px !important;
        width: 100% !important;
      }
      html.rail-collapsed .nav button {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        gap: 0 !important;
        min-height: 42px !important;
        width: 100% !important;
        overflow: hidden !important;
      }
      html.rail-collapsed .nav button.active {
        box-shadow:
          inset 0 0 0 1px rgba(255, 122, 77, 0.25),
          0 0 18px -6px rgba(255, 122, 77, 0.4) !important;
      }
      html.rail-collapsed .nav button svg {
        width: 18px !important;
        height: 18px !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        display: block !important;
      }
    }

    @media (min-width: 761px) and (max-width: 1120px) {
      html.rail-collapsed .app {
        grid-template-columns: 72px minmax(0, 1fr) var(--inspector-width, 300px) !important;
      }
    }

    @media (max-width: 760px) {
      .session-chips { max-height: 132px; }
      .prompt-pills { max-width: 100%; }
      .brand p,
      .brand-tagline { display: block !important; font-size: 10px !important; color: var(--shell-faint) !important; margin: 0 !important; }
      .rail-footer { border-top: 1px solid rgba(255,255,255,0.04); }
      /* Mobile uses drawer — ignore desktop tuck */
      html.rail-collapsed .app {
        grid-template-columns: unset !important;
      }
      html.rail-collapsed .rail {
        max-width: none !important;
      }
      html.rail-collapsed .rail-section .group,
      html.rail-collapsed .rail-footer,
      html.rail-collapsed .account-wrap,
      html.rail-collapsed .brand-mark h1,
      html.rail-collapsed .brand p,
      html.rail-collapsed .brand-tagline,
      html.rail-collapsed .brand-actions .density-toggle,
      html.rail-collapsed .nav-label {
        display: revert !important;
      }
      html.rail-collapsed .nav-label {
        display: inline !important;
      }
      html.rail-collapsed .brand-mark h1 {
        display: block !important;
      }
      html.rail-collapsed .brand-tagline {
        display: block !important;
      }
    }

    /* Dark stage polish — deeper center canvas against shell */
    .chat {
      background: rgba(4, 6, 10, 0.45);
    }
    .light .chat {
      background: rgba(255, 255, 255, 0.25);
    }

    /* ============================================================
       FORGE STUDIOS — ImageGen + VidGen unified with shell language
       Replaces hard #111/#222 neon skins with design tokens
       ============================================================ */
    .imagegen,
    .videogen {
      min-width: 0;
      min-height: 0;
      height: 100vh;
      height: 100dvh;
      overflow: hidden;
      background:
        radial-gradient(ellipse 80% 50% at 12% -10%, rgba(255, 122, 77, 0.07), transparent 55%),
        radial-gradient(ellipse 70% 45% at 90% 110%, rgba(251, 146, 60, 0.06), transparent 50%),
        var(--bg) !important;
      color: var(--text);
    }
    .light .imagegen,
    .light .videogen {
      background:
        radial-gradient(ellipse 80% 50% at 12% -10%, rgba(232, 93, 42, 0.06), transparent 55%),
        radial-gradient(ellipse 70% 45% at 90% 110%, rgba(245, 158, 11, 0.05), transparent 50%),
        var(--bg) !important;
    }

    .imagegen-shell,
    .videogen-shell {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) minmax(220px, 280px) !important;
      gap: 16px !important;
      height: 100% !important;
      min-height: 0 !important;
      overflow: hidden !important;
      padding: 18px 20px !important;
    }

    .imagegen-workspace,
    .videogen-workspace {
      display: flex !important;
      flex-direction: column !important;
      gap: 14px !important;
      min-width: 0 !important;
      min-height: 0 !important;
      overflow: auto !important;
      padding-right: 2px;
    }

    .studio-header,
    .imagegen-header,
    .videogen-header {
      display: flex !important;
      align-items: flex-start !important;
      justify-content: space-between !important;
      gap: 14px !important;
      flex-shrink: 0 !important;
      padding: 0 2px 2px !important;
    }
    .studio-header-copy h2,
    .imagegen-header h2,
    .videogen-header h2 {
      margin: 0 !important;
      font-family: var(--font-display) !important;
      font-size: 22px !important;
      font-weight: 750 !important;
      letter-spacing: -0.03em !important;
      color: var(--text) !important;
      background: none !important;
      -webkit-text-fill-color: unset !important;
    }
    .studio-header-copy p,
    .imagegen-header p,
    .videogen-header p {
      margin: 4px 0 0 !important;
      font-size: 13px !important;
      color: var(--muted) !important;
      max-width: 48ch !important;
      line-height: 1.45 !important;
    }
    .studio-kicker,
    .cine-badge {
      display: inline-block !important;
      margin: 0 0 6px !important;
      padding: 3px 9px !important;
      border-radius: var(--r-pill) !important;
      border: 0 !important;
      background: rgba(255, 122, 77, 0.10) !important;
      color: var(--blue) !important;
      font-size: 10px !important;
      font-weight: 700 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      -webkit-text-fill-color: unset !important;
    }

    .studio-modes,
    .imagegen-modes,
    .videogen-modes {
      display: inline-flex !important;
      flex-shrink: 0 !important;
      gap: 3px !important;
      padding: 4px !important;
      border-radius: var(--r-pill) !important;
      border: 0 !important;
      background: var(--shell-fill) !important;
      box-shadow: none !important;
    }
    .imagegen-modes button,
    .videogen-modes button {
      min-height: 34px !important;
      padding: 0 14px !important;
      border: 0 !important;
      border-radius: var(--r-pill) !important;
      background: transparent !important;
      color: var(--muted) !important;
      font-size: 12.5px !important;
      font-weight: 600 !important;
      letter-spacing: -0.01em !important;
      cursor: pointer !important;
      box-shadow: none !important;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out) !important;
    }
    .imagegen-modes button:hover,
    .videogen-modes button:hover {
      color: var(--text) !important;
      background: var(--shell-fill-hover) !important;
    }
    .imagegen-modes button.active,
    .videogen-modes button.active {
      color: #fff !important;
      background: var(--fire-gradient) !important;
      box-shadow: 0 6px 18px -6px rgba(232, 93, 42, 0.45) !important;
      font-weight: 700 !important;
    }

    .studio-card,
    .imagegen-card,
    .imagegen-sidebar,
    .cine-director-card,
    .videogen-reel-sidebar,
    .audiogen-card {
      border: 0 !important;
      border-radius: 16px !important;
      background: rgba(14, 18, 26, 0.72) !important;
      box-shadow: none !important;
      backdrop-filter: blur(18px) saturate(1.15) !important;
      color: var(--text) !important;
    }
    .light .studio-card,
    .light .imagegen-card,
    .light .imagegen-sidebar,
    .light .cine-director-card,
    .light .videogen-reel-sidebar,
    .light .audiogen-card {
      background: rgba(255, 255, 255, 0.78) !important;
      box-shadow: 0 10px 30px -18px rgba(15, 23, 42, 0.12) !important;
    }
    .imagegen-card,
    .cine-director-card {
      padding: 16px !important;
      gap: 14px !important;
      display: flex !important;
      flex-direction: column !important;
    }
    .imagegen-sidebar,
    .videogen-reel-sidebar {
      padding: 14px !important;
      gap: 12px !important;
      overflow: hidden !important;
      min-height: 0 !important;
    }

    .studio-field {
      display: grid;
      gap: 6px;
    }
    .studio-field-label,
    .cine-control label {
      font-size: 10px !important;
      font-weight: 650 !important;
      letter-spacing: 0.07em !important;
      text-transform: uppercase !important;
      color: var(--faint) !important;
      margin: 0 !important;
    }
    .studio-select,
    .imagegen-controls select,
    .imagegen-control-dock select,
    .cine-control select,
    .videogen select.studio-select,
    #videogen-model,
    #videogen-aspect,
    #videogen-res,
    #videogen-motion,
    #imagegen-model,
    #imagegen-aspect,
    #imagegen-edit-model,
    #imagegen-edit-aspect {
      width: 100% !important;
      min-height: 40px !important;
      height: auto !important;
      border: 0 !important;
      border-radius: var(--shell-radius) !important;
      background-color: var(--surface-2) !important;
      color: var(--text) !important;
      color-scheme: inherit !important;
      font-size: 13px !important;
      font-weight: 600 !important;
      padding: 8px 28px 8px 12px !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }
    .studio-select:hover,
    .imagegen-controls select:hover,
    .imagegen-control-dock select:hover,
    .cine-control select:hover,
    #videogen-model:hover,
    #imagegen-model:hover,
    #imagegen-aspect:hover,
    #imagegen-edit-model:hover,
    #imagegen-edit-aspect:hover {
      background-color: var(--surface-3) !important;
      color: var(--text) !important;
    }

    .imagegen-prompt-wrap textarea,
    .videogen-prompt-wrap textarea,
    .audiogen-prompt-wrap textarea {
      width: 100% !important;
      min-height: 100px !important;
      border: 0 !important;
      border-radius: 14px !important;
      background: var(--surface-2) !important;
      color: var(--text) !important;
      padding: 14px 15px !important;
      font-size: 14.5px !important;
      line-height: 1.5 !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
      resize: vertical !important;
    }
    .imagegen-prompt-wrap textarea:focus,
    .videogen-prompt-wrap textarea:focus,
    .audiogen-prompt-wrap textarea:focus {
      outline: none !important;
      box-shadow: inset 0 0 0 1px rgba(255, 122, 77, 0.4), 0 0 0 3px rgba(232, 93, 42, 0.12) !important;
      background: var(--surface-3) !important;
    }

    .imagegen-inspiration,
    .lexicon-chips {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 6px !important;
    }
    .imagegen-inspiration button,
    .lexicon-chips button {
      border: 0 !important;
      border-radius: var(--r-pill) !important;
      background: var(--shell-fill) !important;
      color: var(--muted) !important;
      font-size: 11.5px !important;
      font-weight: 600 !important;
      padding: 6px 11px !important;
      cursor: pointer !important;
      transition: background var(--dur) var(--ease-out), color var(--dur) var(--ease-out) !important;
    }
    .imagegen-inspiration button:hover,
    .lexicon-chips button:hover {
      background: rgba(255, 122, 77, 0.12) !important;
      color: var(--text) !important;
      border-color: transparent !important;
    }

    .imagegen-controls {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 10px !important;
      align-items: center !important;
    }
    .imagegen-controls select {
      flex: 1 1 160px !important;
      min-width: 140px !important;
      width: auto !important;
    }
    .imagegen-controls button.primary,
    .imagegen-control-dock button.primary,
    .cine-render-btn,
    .audiogen-controls .primary {
      min-height: 42px !important;
      min-width: 128px !important;
      border: 0 !important;
      border-radius: 12px !important;
      padding: 0 18px !important;
      color: #fff !important;
      background: var(--fire-gradient) !important;
      font-size: 13.5px !important;
      font-weight: 700 !important;
      letter-spacing: -0.01em !important;
      box-shadow: 0 8px 22px -8px rgba(232, 93, 42, 0.45) !important;
      cursor: pointer !important;
    }
    .imagegen-controls button.primary:hover,
    .imagegen-control-dock button.primary:hover,
    .cine-render-btn:hover {
      transform: translateY(-1px) !important;
      filter: brightness(1.04);
    }
    .cine-render-btn {
      width: 100% !important;
      margin-top: 4px !important;
      color: #fff !important;
    }
    .cine-render-btn .reel {
      border-color: rgba(255,255,255,0.85) !important;
    }

    .imagegen-raw-toggle {
      color: var(--muted) !important;
      font-size: 12.5px !important;
    }
    .imagegen-raw-toggle:hover { color: var(--text) !important; }
    .imagegen-raw-toggle input { accent-color: var(--blue-deep) !important; }

    .imagegen-status,
    .cine-status {
      color: var(--muted) !important;
      font-size: 12.5px !important;
    }
    .imagegen-spinner,
    .cine-spinner {
      border-color: rgba(255,255,255,0.12) !important;
      border-top-color: var(--blue) !important;
    }

    .imagegen-result-card,
    .cine-player-wrap {
      border: 0 !important;
      border-radius: 14px !important;
      background: var(--surface-2) !important;
      overflow: hidden !important;
      box-shadow: var(--shadow-card) !important;
    }
    .imagegen-result-meta {
      background: var(--shell-fill) !important;
      border-top: 1px solid var(--line) !important;
      color: var(--muted) !important;
    }
    .imagegen-lineage,
    .cine-cut-history {
      border: 0 !important;
      background: var(--shell-fill) !important;
      border-radius: 12px !important;
      color: var(--muted) !important;
    }
    .imagegen-lineage .crumb {
      background: var(--surface-2) !important;
      border: 0 !important;
      color: var(--text) !important;
    }

    .imagegen-media-stage {
      border: 0 !important;
      border-radius: 14px !important;
      background:
        linear-gradient(45deg, rgba(128,128,128,0.04) 25%, transparent 25% 75%, rgba(128,128,128,0.04) 75%),
        linear-gradient(45deg, rgba(128,128,128,0.04) 25%, var(--surface-2) 25% 75%, rgba(128,128,128,0.04) 75%) !important;
      background-size: 22px 22px !important;
      background-position: 0 0, 11px 11px !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }
    .imagegen-stage-label,
    .imagegen-replace-source {
      border: 0 !important;
      background: color-mix(in srgb, var(--surface) 88%, transparent) !important;
      color: var(--muted) !important;
      backdrop-filter: blur(10px);
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }
    .imagegen-stage-empty { color: var(--faint) !important; }
    .imagegen-stage-empty strong { color: var(--muted) !important; }

    .imagegen-dropzone {
      border: 1px dashed rgba(255, 122, 77, 0.35) !important;
      border-radius: 14px !important;
      background: rgba(255, 122, 77, 0.05) !important;
      color: var(--muted) !important;
    }
    .imagegen-dropzone:hover {
      border-color: rgba(255, 122, 77, 0.55) !important;
      background: rgba(255, 122, 77, 0.09) !important;
      color: var(--text) !important;
    }
    .imagegen-control-dock {
      border: 0 !important;
      border-radius: 14px !important;
      background: var(--shell-fill) !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }
    .imagegen-action {
      border: 0 !important;
      background: var(--shell-fill) !important;
      color: var(--text) !important;
      border-radius: 10px !important;
    }
    .imagegen-action:hover {
      background: rgba(255, 122, 77, 0.12) !important;
      border-color: transparent !important;
      color: var(--text) !important;
    }

    .imagegen-sidebar-head h3,
    .reel-head h3 {
      margin: 0 !important;
      font-family: var(--font-display) !important;
      font-size: 13px !important;
      font-weight: 700 !important;
      letter-spacing: -0.01em !important;
      color: var(--text) !important;
    }
    .imagegen-sidebar-head .count,
    .reel-head .count {
      background: var(--shell-fill) !important;
      color: var(--faint) !important;
      border-radius: var(--r-pill) !important;
    }
    .imagegen-gallery-grid .empty,
    .reel-wall .empty {
      color: var(--faint) !important;
    }
    .imagegen-gallery-grid .thumb,
    .imagegen-mini-gallery .thumb,
    .reel-wall .reel-card,
    .cine-cut-history .film-cell {
      border: 0 !important;
      background: var(--surface-2) !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
      border-radius: 12px !important;
    }
    .imagegen-gallery-grid .thumb:hover,
    .reel-wall .reel-card:hover {
      transform: translateY(-2px) !important;
      box-shadow: var(--shadow-soft), inset 0 0 0 1px rgba(255,122,77,0.22) !important;
    }
    .imagegen-mini-gallery .thumb.active {
      box-shadow: 0 0 0 2px rgba(255, 122, 77, 0.45) !important;
      border-color: transparent !important;
    }
    .imagegen-preview {
      border: 0 !important;
      background: var(--surface-2) !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }

    .cine-controls-grid {
      display: grid !important;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)) !important;
      gap: 10px !important;
    }
    .cine-control .segmented {
      display: flex !important;
      gap: 2px !important;
      padding: 3px !important;
      border: 0 !important;
      border-radius: 10px !important;
      background: var(--surface-2) !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }
    .cine-control .segmented button {
      flex: 1 !important;
      border: 0 !important;
      border-radius: 8px !important;
      background: transparent !important;
      color: var(--muted) !important;
      font-size: 11.5px !important;
      font-weight: 600 !important;
      padding: 7px 0 !important;
      cursor: pointer !important;
    }
    .cine-control .segmented button.active {
      background: rgba(255, 122, 77, 0.14) !important;
      color: var(--text) !important;
      font-weight: 700 !important;
    }
    .cine-player-perforation { opacity: 0.35 !important; }

    .imagegen-error,
    .cine-error {
      border: 0 !important;
      border-radius: 12px !important;
      background: rgba(248, 113, 113, 0.10) !important;
      color: var(--red) !important;
    }

    .imagegen-lightbox {
      background: rgba(3, 5, 9, 0.88) !important;
      backdrop-filter: blur(18px) !important;
    }
    .imagegen-lightbox-close {
      border: 0 !important;
      background: color-mix(in srgb, var(--surface) 90%, transparent) !important;
      color: var(--text) !important;
      box-shadow: inset 0 0 0 1px var(--line) !important;
    }

    /* —— Light mode studio polish (white mode) —— */
    .light .imagegen,
    .light .videogen,
    .light .audiogen {
      color: var(--text) !important;
    }
    .light .studio-card,
    .light .imagegen-card,
    .light .imagegen-sidebar,
    .light .cine-director-card,
    .light .videogen-reel-sidebar,
    .light .audiogen-card {
      background: #ffffff !important;
      box-shadow: 0 12px 32px -18px rgba(68, 28, 14, 0.14), inset 0 0 0 1px rgba(68, 28, 14, 0.06) !important;
      color: var(--text) !important;
    }
    .light .imagegen-header h2,
    .light .videogen-header h2,
    .light .studio-header-copy h2,
    .light .imagegen-sidebar-head h3,
    .light .reel-head h3 {
      color: var(--text) !important;
      -webkit-text-fill-color: var(--text) !important;
    }
    .light .imagegen-header p,
    .light .videogen-header p,
    .light .imagegen-status,
    .light .cine-status,
    .light .imagegen-raw-toggle,
    .light .studio-field-label,
    .light .cine-control label {
      color: var(--muted) !important;
    }
    .light .studio-kicker,
    .light .cine-badge {
      background: rgba(234, 88, 12, 0.10) !important;
      color: #c2410c !important;
    }
    .light .studio-modes,
    .light .imagegen-modes,
    .light .videogen-modes {
      background: #f5eeea !important;
    }
    .light .imagegen-modes button,
    .light .videogen-modes button {
      color: #6f6258 !important;
    }
    .light .imagegen-modes button:hover,
    .light .videogen-modes button:hover {
      color: #0c1222 !important;
      background: rgba(255, 255, 255, 0.9) !important;
    }
    .light .imagegen-inspiration button,
    .light .lexicon-chips button {
      background: #f5eeea !important;
      color: #6f6258 !important;
    }
    .light .imagegen-inspiration button:hover,
    .light .lexicon-chips button:hover {
      background: rgba(234, 88, 12, 0.12) !important;
      color: #0c1222 !important;
    }
    .light .studio-select,
    .light .imagegen-controls select,
    .light .imagegen-control-dock select,
    .light .cine-control select,
    .light #videogen-model,
    .light #videogen-aspect,
    .light #videogen-res,
    .light #videogen-motion,
    .light #imagegen-model,
    .light #imagegen-aspect,
    .light #imagegen-edit-model,
    .light #imagegen-edit-aspect {
      color-scheme: light !important;
      background-color: #f5eeea !important;
      color: #0c1222 !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .studio-select:hover,
    .light .imagegen-controls select:hover,
    .light .imagegen-control-dock select:hover,
    .light .cine-control select:hover,
    .light #imagegen-model:hover,
    .light #imagegen-aspect:hover,
    .light #imagegen-edit-model:hover,
    .light #imagegen-edit-aspect:hover,
    .light #videogen-model:hover {
      background-color: #ebe1da !important;
      color: #0c1222 !important;
    }
    .light .imagegen-prompt-wrap textarea,
    .light .videogen-prompt-wrap textarea,
    .light .audiogen-prompt-wrap textarea {
      background: #faf6f3 !important;
      color: #0c1222 !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .imagegen-prompt-wrap textarea:focus,
    .light .videogen-prompt-wrap textarea:focus,
    .light .audiogen-prompt-wrap textarea:focus {
      background: #ffffff !important;
      box-shadow: inset 0 0 0 1px rgba(234, 88, 12, 0.4), 0 0 0 3px rgba(234, 88, 12, 0.12) !important;
    }
    .light .imagegen-prompt-wrap textarea::placeholder,
    .light .videogen-prompt-wrap textarea::placeholder {
      color: #8b97ab !important;
    }
    .light .imagegen-media-stage {
      background:
        linear-gradient(45deg, rgba(68, 28, 14, 0.03) 25%, transparent 25% 75%, rgba(68, 28, 14, 0.03) 75%),
        linear-gradient(45deg, rgba(68, 28, 14, 0.03) 25%, #f5eeea 25% 75%, rgba(68, 28, 14, 0.03) 75%) !important;
      background-size: 22px 22px !important;
      background-position: 0 0, 11px 11px !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .imagegen-stage-label,
    .light .imagegen-replace-source {
      background: rgba(255, 255, 255, 0.92) !important;
      color: #5b6b82 !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .imagegen-stage-empty { color: #8b97ab !important; }
    .light .imagegen-stage-empty strong { color: #5b6b82 !important; }
    .light .imagegen-dropzone {
      border-color: rgba(234, 88, 12, 0.35) !important;
      background: rgba(234, 88, 12, 0.05) !important;
      color: #5b6b82 !important;
    }
    .light .imagegen-dropzone:hover {
      color: #0c1222 !important;
      background: rgba(234, 88, 12, 0.09) !important;
    }
    .light .imagegen-control-dock {
      background: #f5eeea !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.06) !important;
    }
    .light .imagegen-result-card,
    .light .cine-player-wrap {
      background: #ffffff !important;
      box-shadow: 0 12px 28px -16px rgba(68, 28, 14, 0.16), inset 0 0 0 1px rgba(68, 28, 14, 0.06) !important;
    }
    .light .imagegen-result-meta {
      background: #faf6f3 !important;
      border-top-color: rgba(68, 28, 14, 0.08) !important;
      color: #5b6b82 !important;
    }
    .light .imagegen-lineage,
    .light .cine-cut-history {
      background: #f5eeea !important;
      color: #5b6b82 !important;
    }
    .light .imagegen-lineage .crumb {
      background: #ffffff !important;
      color: #0c1222 !important;
    }
    .light .imagegen-gallery-grid .thumb,
    .light .imagegen-mini-gallery .thumb,
    .light .reel-wall .reel-card,
    .light .cine-cut-history .film-cell,
    .light .imagegen-preview {
      background: #f5eeea !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .imagegen-gallery-grid .empty,
    .light .reel-wall .empty {
      color: #8b97ab !important;
    }
    .light .imagegen-action {
      background: #f5eeea !important;
      color: #0c1222 !important;
    }
    .light .imagegen-action:hover {
      background: rgba(234, 88, 12, 0.12) !important;
    }
    .light .cine-control .segmented {
      background: #f5eeea !important;
      box-shadow: inset 0 0 0 1px rgba(68, 28, 14, 0.08) !important;
    }
    .light .cine-control .segmented button {
      color: #6f6258 !important;
    }
    .light .cine-control .segmented button.active {
      background: rgba(234, 88, 12, 0.14) !important;
      color: #0c1222 !important;
    }
    .light .imagegen-progress {
      color: #5b6b82 !important;
      background: radial-gradient(circle, rgba(234, 88, 12, 0.08), transparent 55%) !important;
    }
    .light .imagegen-progress strong {
      color: #0c1222 !important;
    }
    .light .imagegen-spinner,
    .light .cine-spinner {
      border-color: rgba(68, 28, 14, 0.12) !important;
      border-top-color: #ea580c !important;
    }
    .light .imagegen-error,
    .light .cine-error {
      background: rgba(220, 38, 38, 0.08) !important;
      color: #b91c1c !important;
    }
    .light .imagegen-panel > .imagegen-card > .imagegen-result .imagegen-result-card img {
      background: #f5eeea !important;
    }
    .light .imagegen-lightbox {
      background: rgba(40, 20, 12, 0.55) !important;
    }
    .light .imagegen-lightbox-close {
      background: #ffffff !important;
      color: #0c1222 !important;
    }
    .light .imagegen-raw-toggle input {
      accent-color: #ea580c !important;
    }

    @media (max-width: 900px) {
      .imagegen-shell,
      .videogen-shell {
        grid-template-columns: 1fr !important;
        grid-template-rows: minmax(0, 1fr) auto !important;
        overflow: auto !important;
      }
      .imagegen-sidebar,
      .videogen-reel-sidebar {
        max-height: 240px !important;
      }
      .studio-header,
      .imagegen-header,
      .videogen-header {
        flex-direction: column !important;
        align-items: stretch !important;
      }
      .studio-modes,
      .imagegen-modes,
      .videogen-modes {
        width: 100% !important;
        overflow-x: auto !important;
      }
    }


    /* ============================================================
       FORGE MOBILE PASS — every section readable on phone
       ============================================================ */
    @media (max-width: 760px) {
      .app {
        display: flex !important;
        flex-direction: column !important;
        height: 100dvh !important;
        overflow: hidden !important;
      }
      .chat,
      .guide.active,
      .settings.active,
      .marketplace.active,
      .imagegen:not(.hidden),
      .videogen:not(.hidden),
      .audiogen:not(.hidden) {
        flex: 1 1 auto !important;
        min-height: 0 !important;
        height: auto !important;
        max-height: none !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
      }
      .imagegen.hidden,
      .videogen.hidden,
      .audiogen.hidden,
      .guide:not(.active),
      .settings:not(.active),
      .marketplace:not(.active) {
        display: none !important;
      }
      .chat {
        display: grid !important;
        grid-template-rows: auto auto minmax(0, 1fr) auto !important;
        overflow: hidden !important;
      }
      .messages {
        min-height: 0 !important;
        overflow: auto !important;
        padding: 12px 12px 8px !important;
        mask-image: none !important;
        -webkit-mask-image: none !important;
      }
      .composer {
        padding: 8px 12px max(12px, env(safe-area-inset-bottom)) !important;
        position: sticky !important;
        bottom: 0 !important;
      }
      .composer-form {
        grid-template-columns: minmax(0, 1fr) auto !important;
        border-radius: 18px !important;
        padding: 6px 6px 6px 12px !important;
      }
      .composer-form textarea {
        min-height: 42px !important;
        font-size: 16px !important; /* prevent iOS zoom */
      }
      .send {
        width: 44px !important;
        min-height: 44px !important;
        border-radius: 50% !important;
      }
      .chat-top {
        padding: 10px 12px !important;
        gap: 8px !important;
      }
      .trust-strip {
        padding: 2px 12px 8px !important;
        gap: 6px 10px !important;
        font-size: 10px !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        flex-wrap: nowrap !important;
      }
      .message {
        max-width: 100% !important;
      }
      .message.assistant .bubble::before,
      .message:not(.user) .bubble::before {
        display: none !important;
      }
      .empty {
        padding: 28px 14px !important;
      }
      .empty h2 {
        font-size: 24px !important;
      }
      .prompt-pills {
        max-width: 100% !important;
        gap: 6px !important;
      }
      .prompt-pill {
        font-size: 12px !important;
        padding: 8px 12px !important;
      }
      /* Mobile drawer rail */
      .rail {
        width: min(340px, 90vw) !important;
        max-width: 90vw !important;
      }
      .rail-collapse {
        display: none !important;
      }
      .brand-row {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
      }
      .brand-actions {
        flex-direction: row !important;
      }
      .nav button {
        min-height: 44px !important;
      }
      .rail select,
      .rail input,
      input, select, textarea {
        font-size: 16px !important;
        min-height: 44px !important;
      }
      /* Guide / settings / marketplace */
      .guide, .settings, .marketplace {
        padding: 14px 12px max(18px, env(safe-area-inset-bottom)) !important;
      }
      .guide-shell, .settings-form {
        gap: 12px !important;
      }
      .guide-hero, .marketplace-hero {
        padding: 16px !important;
        border-radius: 16px !important;
      }
      .guide-hero h2, .marketplace-hero h2 {
        font-size: 22px !important;
      }
      .settings-tabs, .guide-controls, .provider-subtabs {
        width: 100% !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch;
      }
      .settings-tabs button, .guide-controls button, .provider-subtab {
        min-height: 40px !important;
        white-space: nowrap !important;
      }
      .settings-row {
        grid-template-columns: 1fr !important;
      }
      .feature-grid, .marketplace-grid {
        grid-template-columns: 1fr !important;
        gap: 10px !important;
      }
      .detail-drawer {
        width: min(100vw, 420px) !important;
      }
      /* Studios */
      .imagegen-shell, .videogen-shell, .audiogen-shell {
        display: flex !important;
        flex-direction: column !important;
        height: auto !important;
        min-height: 0 !important;
        overflow: visible !important;
        padding: 12px 12px max(16px, env(safe-area-inset-bottom)) !important;
        gap: 12px !important;
      }
      .imagegen-workspace, .videogen-workspace {
        overflow: visible !important;
        gap: 12px !important;
      }
      .studio-header, .imagegen-header, .videogen-header, .audiogen-header {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
      }
      .studio-modes, .imagegen-modes, .videogen-modes {
        width: 100% !important;
        display: flex !important;
        overflow-x: auto !important;
      }
      .imagegen-modes button, .videogen-modes button {
        flex: 1 0 auto !important;
        min-height: 40px !important;
      }
      .imagegen-controls {
        flex-direction: column !important;
        align-items: stretch !important;
      }
      .imagegen-controls select,
      .imagegen-controls button.primary,
      .imagegen-control-dock button.primary,
      .cine-render-btn {
        width: 100% !important;
        min-height: 44px !important;
      }
      .imagegen-compare-stage {
        grid-template-columns: 1fr !important;
      }
      .imagegen-media-stage {
        min-height: 200px !important;
        max-height: none !important;
      }
      .imagegen-control-dock {
        grid-template-columns: 1fr !important;
      }
      .imagegen-sidebar, .videogen-reel-sidebar {
        max-height: none !important;
        order: 2 !important;
      }
      .imagegen-gallery-grid, .reel-wall {
        display: flex !important;
        overflow-x: auto !important;
        gap: 10px !important;
        -webkit-overflow-scrolling: touch;
      }
      .imagegen-gallery-grid .thumb {
        width: 120px !important;
        flex: 0 0 120px !important;
      }
      .reel-wall .reel-card {
        width: 160px !important;
        flex: 0 0 160px !important;
      }
      .cine-controls-grid {
        grid-template-columns: 1fr 1fr !important;
      }
      .audiogen-card, .imagegen-card, .cine-director-card {
        padding: 12px !important;
      }
      .mobile-nav {
        display: flex !important;
        flex: 0 0 auto !important;
        min-height: 56px !important;
        padding-bottom: max(0px, env(safe-area-inset-bottom)) !important;
        border-top: 1px solid rgba(255,230,210,0.08) !important;
        background: var(--mobile-nav-bg) !important;
      }
      .mobile-nav button {
        min-height: 48px !important;
        font-size: 11px !important;
      }
      .mobile-nav button.active {
        color: var(--blue) !important;
        background: rgba(255, 122, 77, 0.10) !important;
      }
      .auth-card {
        width: min(420px, 94vw) !important;
        padding: 28px 20px !important;
        margin: 12px !important;
      }
      .auth-field input, .auth-submit {
        min-height: 46px !important;
        font-size: 16px !important;
      }
      .command-palette {
        width: min(560px, 94vw) !important;
      }
    }

    @media (max-width: 420px) {
      .cine-controls-grid {
        grid-template-columns: 1fr !important;
      }
      .badges {
        width: 100%;
      }
      .imagegen-header h2, .videogen-header h2, .studio-header-copy h2 {
        font-size: 20px !important;
      }
    }

    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
      .persona-card::after { display: none; }
      .empty-mark { animation: none !important; }
      .brand-mark .pulse-ring { animation: none !important; }
      .message.streaming .bubble-content::after { animation: none !important; opacity: 1; }
    }
    </style>
</head>
<body>
  <div class="orb-field" aria-hidden="true">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>
  <div class="grain" aria-hidden="true"></div>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="brand-row">
          <div class="brand-mark">
            <span class="pulse-ring" aria-hidden="true"></span>
            <h1>Forge</h1>
          </div>
          <div class="brand-actions">
            <button class="density-toggle" id="density-toggle" type="button" aria-label="Toggle compact density" title="Compact density" aria-pressed="false">
              <svg id="density-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="3" y="3" width="7" height="7" rx="1.5"></rect>
                <rect x="14" y="3" width="7" height="7" rx="1.5"></rect>
                <rect x="3" y="14" width="7" height="7" rx="1.5"></rect>
                <rect x="14" y="14" width="7" height="7" rx="1.5"></rect>
              </svg>
            </button>
            <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle theme" title="Toggle theme">
              <svg id="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
              <svg id="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            </button>
            <button class="rail-collapse" id="rail-collapse" type="button" aria-label="Collapse sidebar" title="Collapse sidebar" aria-pressed="false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
          </div>
        </div>
        <div class="account-wrap" id="account-wrap">
          <button class="account-btn" id="account-btn" type="button" style="display:none;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <span id="account-name">Account</span>
          </button>
          <div class="account-menu" id="account-menu">
            <div class="account-role" id="account-role"></div>
            <button id="account-logout" type="button">Log out</button>
          </div>
        </div>
        <p class="brand-tagline">PoC for <strong>CypherTempre</strong></p>
      </div>

      <div class="rail-section">
        <div class="nav" aria-label="Main view">
          <button id="nav-chat" class="active" type="button" title="Chat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span class="nav-label">Chat</span>
          </button>
          <button id="nav-guide" type="button" title="Guide">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            <span class="nav-label">Guide</span>
          </button>
          <button id="nav-marketplace" type="button" title="Marketplace">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
            <span class="nav-label">Marketplace</span>
          </button>
          <button id="nav-imagegen" type="button" title="ImageGen">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            <span class="nav-label">ImageGen</span>
          </button>
          <button id="nav-videogen" type="button" title="VidGen">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"></rect><path d="M22 12l-5 3V9l5 3z"></path></svg>
            <span class="nav-label">VidGen</span>
          </button>
          <button id="nav-audiogen" type="button" title="AudioGen">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1v22M4.5 4.5c4.5 3.4 7.5 5.6 7.5 5.6s3-2.2 7.5-5.6M4.5 19.5c4.5-3.4 7.5-5.6 7.5-5.6s3 2.2 7.5 5.6"></path></svg>
            <span class="nav-label">AudioGen</span>
          </button>
          <button id="nav-settings" type="button" title="Settings">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 5 15.4a1.65 1.65 0 0 0-1.51 1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 5 10.6a1.65 1.65 0 0 0-.33-1.82l-.06-.06A1.65 1.65 0 0 0 9 5.4a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            <span class="nav-label">Settings</span>
          </button>
        </div>

        <div class="group">
          <label for="persona">Persona</label>
          <select id="persona"></select>
          <div class="hint" id="persona-lock-hint"></div>
        </div>

        <div class="group">
          <label for="domain">Domain</label>
          <select id="domain">
            <option value="auto">auto</option>
            <option value="architecture">architecture</option>
            <option value="system-design">system-design</option>
            <option value="testing">testing</option>
            <option value="security">security</option>
            <option value="debugging">debugging</option>
            <option value="performance">performance</option>
            <option value="refactoring">refactoring</option>
            <option value="api-design">api-design</option>
          </select>
        </div>

        <div class="group sessions-group">
          <div class="sessions-head">
            <label id="sessions-label">Sessions</label>
            <span class="sessions-count" id="sessions-count" aria-hidden="true"></span>
          </div>
          <div class="session-chips" id="session-chips" role="listbox" aria-labelledby="sessions-label"></div>
          <select id="session-list" class="sr-only" tabindex="-1" aria-hidden="true"></select>
          <div class="inline-field session-create-row">
            <input id="session-name" placeholder="New thread…" autocomplete="off">
            <button id="new-session" class="secondary" type="button">New</button>
          </div>
        </div>
      </div>

      <div class="rail-footer">
        <div class="status-card" id="setup-status">Checking configuration...</div>
      </div>
    </aside>

    <main id="chat-view" class="chat">
      <div class="chat-top">
        <button id="menu-toggle" class="mobile-only settings-icon" type="button" aria-label="Menu">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>
        <div class="chat-title">
          <strong id="active-title">Companion</strong>
          <span id="workspace-line">Workspace loading...</span>
        </div>
        <div class="badges">
          <span class="badge info" id="model-badge">gemma-4-uncensored</span>
          <span class="badge" id="rings-badge">rings: -</span>
          <span class="badge" id="verify-badge">verify: -</span>
        </div>
        <button id="inspector-toggle" class="mobile-only settings-icon" type="button" aria-label="Memory">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
        </button>
      </div>
      <div class="trust-strip" id="trust-strip" aria-live="polite">
        <span class="trust-item" id="trust-skill">skill: —</span>
        <span class="trust-item" id="trust-verify">verify: —</span>
        <span class="trust-item" id="trust-rings">height: —</span>
        <span class="trust-item" id="trust-seal">last seal: —</span>
        <span class="trust-item" id="trust-product">memory: — · identity: —</span>
      </div>

      <section id="messages" class="messages" aria-live="polite">
        <div class="empty" id="empty-state">
          <div class="empty-mark" aria-hidden="true">F</div>
          <h2>What should we remember together?</h2>
          <p>Forge is a PoC host for CypherTempre. Accepted replies seal into your local Timechain — verifiable memory that grows with you.</p>
          <div class="prompt-pills" id="prompt-pills" role="group" aria-label="Suggested prompts">
            <button type="button" class="prompt-pill" data-prompt="What do you already remember about how I like to work?">Recall my working style</button>
            <button type="button" class="prompt-pill" data-prompt="Summarize the key decisions sealed in this session’s Timechain so far.">Summarize this chain</button>
            <button type="button" class="prompt-pill" data-prompt="Help me think through a design tradeoff carefully — surface assumptions, risks, and a recommended path.">Design tradeoff</button>
            <button type="button" class="prompt-pill" data-prompt="Verify your self-model: what are you confident about, uncertain about, and what would change your mind?">Honest self-check</button>
          </div>
          <div class="empty-hints" aria-hidden="true">
            <span>PoQ-gated</span>
            <span>Hash-linked memory</span>
            <span>Your chain, your keys</span>
          </div>
        </div>
      </section>

      <div class="composer">
        <div class="composer-warning" id="composer-warning">
          <strong>CT OpenClaw Runtime consumes many tokens.</strong>
          <span id="composer-warning-detail">
            Paid or higher-context models can run it with this warning. Free models are blocked for this persona.
          </span>
        </div>
        <div class="composer-options">
          <label class="composer-option">
            <input type="checkbox" id="shared-memory-toggle" title="Also inject Shared Memory from other sessions (identity bridge is always on when enabled in Settings)">
            <span>Use shared memory</span>
          </label>
        </div>
        <form id="composer-form" class="composer-form">
          <textarea id="message" placeholder="Think with Forge…" required enterkeyhint="send"></textarea>
          <button id="send" class="send" type="submit" aria-label="Send">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
        </form>
      </div>
    </main>

    <main id="guide-view" class="guide">
      <div class="guide-shell">
        <section class="guide-hero">
          <div class="guide-controls" aria-label="Explanation depth">
            <button id="guide-simple" class="active" type="button">Simple</button>
            <button id="guide-comprehensive" type="button">Comprehensive</button>
          </div>
          <h2>System Guide</h2>
          <p class="simple-only">A map of Forge (the host) and CypherTempre skill v3.28 (the engine) — what each part does.</p>
          <p class="comprehensive-only hidden">Topics cover Forge product surfaces (chat, personas, studios, memory review) and the vendored skill organs: router, PoQ covenant confrontation, recall ladder, Cambium/hibernation, Chronosynaptic, Continuum/audit/tasks, dormancy, immune membrane, dream/learners, replay/guard, doctor/epochs/telemetry, and more. Topics load from the server guide registry.</p>
        </section>

        <section id="guide-topic-grid" class="feature-grid">
          <article class="feature-card">
            <h3>Chat</h3>
            <p class="simple-only">Send messages and receive assistant replies through the selected persona and model.</p>
          <div class="comprehensive-only hidden">
            <p>The chat composer sends your message, selected domain, persona, model, and optional browser API key to the local server.</p>
            <ul>
                <li>The server recalls relevant rings before the LLM call.</li>
                <li>The response is scored by PoQ before it is saved.</li>
                <li>Accepted replies appear with ring metadata and may create pending memory candidates for review.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Personas</h3>
            <p class="simple-only">Change the assistant's style, or generate a fictional inspired persona in Persona Studio.</p>
            <div class="comprehensive-only hidden">
              <p>Personas provide the system prompt and default memory domain for the request. Custom personas are saved in your local workspace and mirrored in your browser.</p>
              <ul>
                <li>Companion is general conversational help.</li>
                <li>Architect focuses on design tradeoffs.</li>
                <li>Socratic Tutor asks sharper learning questions.</li>
                <li>Memory Critic audits weak or contradictory memory.</li>
                <li>CypherTempre Researcher focuses on the runtime architecture itself.</li>
                <li>Cypher Tempre OpenClaw Runtime is the full prompt-layer v5.0 runtime with Timechain-oriented self-modeling, epistemic classes, and Cambium growth loops. It does not claim full native architecture capabilities.</li>
                <li>Generated personas can be inspired by aesthetics or communication styles, but should remain fictional.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Model</h3>
            <p class="simple-only">Choose which model answers the chat.</p>
            <div class="comprehensive-only hidden">
              <p>The model field defaults from `.env.local` or the server launch arguments.</p>
              <ul>
                <li>Your current persistent model is Venice Uncensored.</li>
                <li>If no key is available, the app falls back to the local deterministic generator.</li>
                <li>The response metadata shows which model path was used.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>API Key</h3>
            <p class="simple-only">Use `.env.local` for persistent local testing, or paste a key for the browser session.</p>
            <div class="comprehensive-only hidden">
              <p>The server loads `.env.local` from the app root on startup.</p>
              <ul>
                <li>`API_KEY` enables real LLM replies.</li>
                <li>`MODEL` sets the default model.</li>
                <li>The file is ignored by git so the key is not committed.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Memory Domain</h3>
            <p class="simple-only">Leave this on auto unless you want to force a specific memory topic.</p>
            <div class="comprehensive-only hidden">
              <p>Domains influence recall and self-model coverage. Auto mode classifies the message from keywords and persona context.</p>
              <ul>
                <li>Each accepted ring stores its domain.</li>
                <li>Recall can filter by the active domain.</li>
                <li>The self-model shows top and untouched domains.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>PoQ Gate</h3>
            <p class="simple-only">The app only saves responses that pass quality and covenant checks.</p>
            <div class="comprehensive-only hidden">
              <p>Proof-of-Qualia scores coherence, relevance, novelty, consistency, depth, and covenant alignment.</p>
              <ul>
                <li>Accepted responses become hash-linked rings.</li>
                <li>Rejected responses are shown but not sealed.</li>
                <li>Brightness is computed, not manually assigned.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Recall</h3>
            <p class="simple-only">Search accepted durable memories and prior accepted rings from the local Timechain.</p>
            <div class="comprehensive-only hidden">
              <p>Recall uses the same lightweight retrieval primitives as the Timechain CLI.</p>
              <ul>
                <li>Results include accepted durable memories, score, ring number, brightness, domain, and content.</li>
                <li>Pending, rejected, superseded, and forgotten memories are excluded from prompt recall.</li>
                <li>Accepted memories and recent rings steer prompts through retrieval/prompt conditioning, not model retraining.</li>
                <li>Recall reads from `.timechain/chain.jsonl` and `.timechain/memory_model.json`.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Memory Review</h3>
            <p class="simple-only">Approve or reject proposed durable memories before they affect future answers.</p>
            <div class="comprehensive-only hidden">
              <p>Accepted chat responses can propose user-continuity memories after PoQ sealing.</p>
              <ul>
                <li>Deterministic extraction handles basics, and the configured LLM may propose richer memories.</li>
                <li>Pending memories are visible in Memory Inspector but are not used in prompts or durable recall.</li>
                <li>You can accept, reject, edit, or forget memory records.</li>
                <li>Accepted memories carry global or session scope, confidence, source ring, evidence, and supersession lineage.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Self Model</h3>
            <p class="simple-only">See the agent's current memory state at a glance.</p>
            <div class="comprehensive-only hidden">
              <p>The self model summarizes local Timechain state.</p>
              <ul>
                <li>Ring count shows accepted memory size.</li>
                <li>Memory counts distinguish accepted durable facts from pending review candidates.</li>
                <li>Active context uses a 90-day prompt window while stale items remain in the audit trail.</li>
                <li>Temporal mass is accumulated brightness.</li>
                <li>Top domains show where the system has experience.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Verify Chain</h3>
            <p class="simple-only">Check whether the hash-linked memory chain is intact.</p>
            <div class="comprehensive-only hidden">
              <p>Verification replays the chain hashes and confirms each ring points to the previous one.</p>
              <ul>
                <li>`ok` means no tampering was detected.</li>
                <li>The visible ring count includes genesis.</li>
                <li>Use this after experiments or manual file inspection.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Persistence</h3>
            <p class="simple-only">Sealed rings, reviewed memories, pending candidates, and custom personas survive browser reloads and server restarts.</p>
            <div class="comprehensive-only hidden">
              <p>Persistence comes from the local append-only Timechain files.</p>
              <ul>
                <li>Accepted conversation rings live in each session's skill chain: `data/users/&lt;you&gt;/sessions/&lt;session&gt;/chain/rings.jsonl`.</li>
                <li>Durable memory candidates and accepted continuity memories live in `.timechain/memory_model.json`.</li>
                <li>The UI restores accepted exchanges from `/api/history`.</li>
                <li>Unsent drafts, rejected PoQ responses, and pending memory candidates are not saved as rings.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Sessions</h3>
            <p class="simple-only">Create separate conversations with separate local memory chains.</p>
            <div class="comprehensive-only hidden">
              <p>Each session stores its Timechain in a separate workspace under your user sessions folder.</p>
              <ul>
                <li>Stable global user profile memories are shared from the main workspace, while session notes stay local.</li>
                <li>Switching sessions reloads chat history, memory review state, recall, self-model, and verification state.</li>
                <li>Reset Chain Memory clears only the active session.</li>
                <li>Personas and provider settings remain shared across sessions.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Reset Chain Memory</h3>
            <p class="simple-only">Clear local demo memory and start again with a fresh genesis ring.</p>
            <div class="comprehensive-only hidden">
              <p>The reset button clears the active session Timechain and immediately creates a fresh genesis ring.</p>
              <ul>
                <li>Use it before sharing the demo with someone else.</li>
                <li>It does not delete `.env.local` or saved custom personas.</li>
                <li>After reset, recall history is empty except for the new genesis state.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>OpenClaw Runtime</h3>
            <p class="simple-only">A prompt-layer v5.0 persona with Timechain-oriented self-modeling, epistemic classes, and Cambium growth loops.</p>
            <div class="comprehensive-only hidden">
              <p>The Cypher Tempre OpenClaw Runtime is a built-in persona that injects the full v5.0 prompt-layer system prompt into the existing chat flow.</p>
              <ul>
                <li>It adds Timechain-oriented self-modeling, epistemic classification, POQ-lite scoring, and Cambium growth proposals.</li>
                <li>It includes security resistance, correction lineage with supersession language, and public-claims discipline.</li>
                <li>The prompt contains a truth constraint: it does not claim full native architecture capabilities unless the environment actually provides them.</li>
                <li>It is a prompt-layer approximation, not a fully implemented Timechain being.</li>
              </ul>
            </div>
            <div class="feature-actions">
              <button class="secondary explain-guide-topic" type="button" data-topic-id="openclaw-runtime">Explain</button>
            </div>
          </article>
        </section>

        <section class="project-attribution" aria-labelledby="project-attribution-title">
          <h3 id="project-attribution-title">Cypher Tempre Project</h3>
          <p>This demo is part of the Cypher Tempre cognitive architecture and is shared under the Cypher Tempre Open Intelligence License (CTOIL).</p>
          <p>Copyright (c) 2026 Michael Joseph, Contributor of Origin & Founder of CyberphysicsAI, Architect of Cypher Tempre. The Architecture is provided "as is", without warranty of any kind.</p>
          <p><a href="https://notebooklm.google.com/notebook/6486b26c-946a-4840-a5a7-368c3891a54c" target="_blank" rel="noopener noreferrer">Open the Cypher Tempre NotebookLM source notebook</a></p>
        </section>
      </div>
    </main>

    <main id="marketplace-view" class="marketplace">
      <div class="guide-shell">
        <section class="marketplace-hero">
          <h2>Persona Marketplace</h2>
          <p>Discover and subscribe to personas created by the community. Each persona carries a hidden frozen capsule of accepted experience, not just a prompt.</p>
        </section>
        <div class="marketplace-filters">
          <input id="mp-search" placeholder="Search personas...">
          <button class="filter-pill active" data-filter="all" type="button">All</button>
          <button class="filter-pill" data-filter="free" type="button">Free</button>
          <button class="filter-pill" data-filter="premium" type="button">Premium</button>
          <button class="filter-pill" data-filter="subscribed" type="button">Subscribed</button>
        </div>
        <section id="marketplace-grid" class="marketplace-grid">
          <div style="color:var(--muted);padding:20px 0;">Loading marketplace...</div>
        </section>
      </div>
    </main>

    <main id="imagegen-view" class="imagegen hidden">
      <div class="imagegen-shell">
        <div class="imagegen-workspace">
          <div class="imagegen-header studio-header">
            <div class="studio-header-copy">
              <span class="studio-kicker">Forge · Image</span>
              <h2>ImageGen</h2>
              <p>Create, edit, and redefine images — sealed into your local gallery.</p>
            </div>
            <div class="imagegen-modes studio-modes">
              <button id="imagegen-mode-generate" class="active" type="button">Generate</button>
              <button id="imagegen-mode-edit" type="button">Edit</button>
              <button id="imagegen-mode-redefine" type="button">Redefine</button>
            </div>
          </div>

          <div id="imagegen-panel-generate" class="imagegen-panel">
            <div class="imagegen-card">
              <div class="imagegen-inspiration" id="imagegen-inspiration">
                <button data-chip="ethereal lighting">ethereal lighting</button>
                <button data-chip="hyperreal detail">hyperreal detail</button>
                <button data-chip="cinematic color grade">cinematic grade</button>
                <button data-chip="moody atmosphere">moody atmosphere</button>
                <button data-chip="fine art photography">fine art</button>
                <button data-chip="dramatic rim light">dramatic rim light</button>
              </div>
              <div class="imagegen-prompt-wrap">
                <textarea id="imagegen-prompt" placeholder="Describe the image you want to create in exquisite detail..."></textarea>
              </div>
              <div class="imagegen-controls">
                <select id="imagegen-model">
                  <option value="black-forest-labs/flux.2-pro">FLUX.2 Pro (OpenRouter)</option>
                  <option value="google/gemini-2.5-flash-image-preview">Gemini Flash Image (OpenRouter)</option>
                  <option value="sourceful/riverflow-v2-pro">Riverflow V2 Pro (OpenRouter)</option>
                  <option value="grok-imagine-image">Grok Imagine — Standard (Morpheus)</option>
                  <option value="nano-banana-2">Nano Banana 2 — High Quality (Morpheus)</option>
                  <option value="lustify-v8">Lustify V8 — Uncensored (Morpheus)</option>
                </select>
                <select id="imagegen-aspect">
                  <option value="1:1">1:1 Square</option>
                  <option value="16:9">16:9 Widescreen</option>
                  <option value="4:3">4:3 Classic</option>
                  <option value="9:16">9:16 Portrait</option>
                </select>
                <button id="imagegen-generate-btn" class="primary" type="button">Generate Image</button>
              </div>
              <label class="imagegen-raw-toggle" title="Send your prompt verbatim and skip the LLM prompt-engineering preprocessor. Use this for uncensored models or when you want zero filtering between you and the image model.">
                <input type="checkbox" id="imagegen-bypass-generate">
                <span>Raw prompt (skip prompt engineering)</span>
              </label>
              <div id="imagegen-status" class="imagegen-status"></div>
              <div id="imagegen-result" class="imagegen-result"></div>
              <div id="imagegen-lineage" class="imagegen-lineage hidden"></div>
            </div>
          </div>

          <div id="imagegen-panel-edit" class="imagegen-panel hidden">
            <div class="imagegen-card">
              <div class="imagegen-compare-stage">
                <div id="imagegen-source-stage" class="imagegen-media-stage imagegen-source-stage">
                  <span class="imagegen-stage-label">Source</span>
                  <div class="imagegen-dropzone" id="imagegen-edit-dropzone">
                    <input type="file" id="imagegen-edit-file" accept="image/*">
                    <div>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                      <p>Drop an image here, or click to browse</p>
                      <div class="hint">PNG, JPG or WEBP · or pick ✎ from the archive</div>
                    </div>
                  </div>
                  <img id="imagegen-edit-preview" class="imagegen-preview hidden" alt="Edit preview">
                  <button id="imagegen-replace-source" class="imagegen-replace-source" type="button">Replace image</button>
                </div>
                <div id="imagegen-output-stage" class="imagegen-media-stage">
                  <span class="imagegen-stage-label">Result</span>
                  <div id="imagegen-edit-result" class="imagegen-result">
                    <div class="imagegen-stage-empty"><strong>Your edited image appears here</strong>Talk naturally like ChatGPT/Grok — uncensored, unfiltered. Results become the next source for iterative edits.</div>
                  </div>
                </div>
              </div>
              <div class="imagegen-control-dock">
                <div class="imagegen-inspiration" id="imagegen-edit-inspiration">
                  <button type="button" data-edit-chip="make the background a soft gradient blue">blue background</button>
                  <button type="button" data-edit-chip="add dramatic cinematic rim lighting">rim light</button>
                  <button type="button" data-edit-chip="enhance detail and sharpness while keeping the same face">enhance detail</button>
                  <button type="button" data-edit-chip="change the lighting to golden hour">golden hour</button>
                  <button type="button" data-edit-chip="convert to watercolor painting style">watercolor</button>
                  <button type="button" data-edit-chip="remove distractions from the background">clean background</button>
                </div>
                <div class="imagegen-prompt-wrap">
                  <textarea id="imagegen-edit-prompt" placeholder="Describe the change in plain language — like ChatGPT/Grok, uncensored. e.g. make the background blue…"></textarea>
                </div>
                <select id="imagegen-edit-model">
                  <option value="qwen-edit-uncensored">qwen-edit-uncensored</option>
                </select>
                <select id="imagegen-edit-aspect">
                  <option value="1:1">1:1 Square</option>
                  <option value="4:3">4:3 Classic</option>
                  <option value="16:9">16:9 Wide</option>
                  <option value="9:16">9:16 Portrait</option>
                </select>
                <button id="imagegen-edit-btn" class="primary" type="button">Apply Edit</button>
                <label class="imagegen-raw-toggle" title="Uncensored path: your exact prompt is sent to the edit model with no helper rewrite, policy softening, or content filter. Leave on for ChatGPT/Grok-like control without censorship.">
                  <input type="checkbox" id="imagegen-bypass-edit" checked>
                  <span>Uncensored (exact prompt — no filter)</span>
                </label>
              </div>
            </div>
          </div>

          <div id="imagegen-panel-redefine" class="imagegen-panel hidden">
            <div class="imagegen-card">
              <div id="imagegen-redefine-gallery" class="imagegen-mini-gallery"></div>
              <div class="imagegen-prompt-wrap">
                <textarea id="imagegen-redefine-prompt" placeholder="Describe how to redefine or refine the selected image..."></textarea>
              </div>
              <div class="imagegen-controls">
                <button id="imagegen-redefine-btn" class="primary" type="button">Redefine</button>
              </div>
              <label class="imagegen-raw-toggle" title="Uncensored path: exact prompt to the model with no helper rewrite or content filter.">
                <input type="checkbox" id="imagegen-bypass-redefine" checked>
                <span>Uncensored (exact prompt — no filter)</span>
              </label>
              <div id="imagegen-redefine-result" class="imagegen-result"></div>
            </div>
          </div>
        </div>

        <aside class="imagegen-sidebar">
          <div class="imagegen-sidebar-head">
            <h3>Archive</h3>
            <span class="count" id="imagegen-gallery-count">0</span>
          </div>
          <div id="imagegen-gallery-grid" class="imagegen-gallery-grid"></div>
        </aside>
      </div>
    </main>

    <div id="imagegen-lightbox" class="imagegen-lightbox hidden" role="dialog" aria-modal="true" aria-label="Image preview">
      <button id="imagegen-lightbox-close" class="imagegen-lightbox-close" type="button" aria-label="Close preview">&times;</button>
      <img id="imagegen-lightbox-image" alt="Full image preview">
    </div>

    <!-- ===================== 2026 CINE TEMPRE STUDIO (VideoGen) ===================== -->
    <main id="videogen-view" class="videogen hidden">
      <div class="videogen-shell">
        <div class="videogen-workspace">
          <div class="videogen-header studio-header">
            <div class="studio-header-copy">
              <span class="studio-kicker">Forge · Video</span>
              <h2>VidGen</h2>
              <p>Text-to-film, image-to-motion, and remix — with local reel history.</p>
            </div>
            <div class="videogen-modes studio-modes">
              <button id="videogen-mode-text2video" class="active" type="button">Text → Film</button>
              <button id="videogen-mode-img2vid" type="button">Image → Motion</button>
              <button id="videogen-mode-remix" type="button">Remix / Extend</button>
            </div>
          </div>

          <!-- TEXT → FILM -->
          <div id="videogen-panel-text2video" class="videogen-panel">
            <div class="cine-director-card studio-card">
              <div class="studio-field">
                <label class="studio-field-label" for="videogen-model">Video model</label>
                <select id="videogen-model" class="studio-select">
                  <option value="demo-cinematic">Demo (built-in test clip) — No key needed</option>
                  <option value="kling-2.1-pro">Kling 2.1 Pro — Cinematic</option>
                  <option value="luma-ray2-1080">Luma Ray2 1080p</option>
                  <option value="runway-gen4-turbo">Runway Gen-4 Turbo</option>
                  <option value="black-forest-labs/flux-video-pro">FLUX Video Pro</option>
                  <option value="grok-video-2026">Grok Video — Director Mode</option>
                </select>
              </div>

              <div class="lexicon-chips" id="videogen-lexicon">
                <button data-chip="slow push-in">slow push-in</button>
                <button data-chip="anamorphic flare">anamorphic flare</button>
                <button data-chip="golden hour">golden hour</button>
                <button data-chip="volumetric god rays">god rays</button>
                <button data-chip="handheld 8mm">handheld 8mm</button>
                <button data-chip="dutch angle">dutch angle</button>
                <button data-chip="tracking shot">tracking shot</button>
                <button data-chip="crane up">crane up</button>
              </div>
              <div class="videogen-prompt-wrap">
                <textarea id="videogen-prompt" placeholder="A lone courier sprints across a rain-slicked overpass at 3 a.m., slow push-in, anamorphic flares, melancholy cyber-noir tone..."></textarea>
              </div>
              <div class="cine-controls-grid">
                <div class="cine-control">
                  <label>DURATION</label>
                  <div class="segmented" id="videogen-duration">
                    <button data-val="5s">5s</button>
                    <button data-val="8s" class="active">8s</button>
                    <button data-val="12s">12s</button>
                    <button data-val="20s">20s</button>
                  </div>
                </div>
                <div class="cine-control">
                  <label>ASPECT</label>
                  <select id="videogen-aspect">
                    <option value="2.39:1">2.39:1 Scope</option>
                    <option value="16:9" selected>16:9 Widescreen</option>
                    <option value="9:16">9:16 Vertical Reel</option>
                    <option value="4:3">4:3 Academy</option>
                    <option value="1:1">1:1 Square</option>
                  </select>
                </div>
                <div class="cine-control">
                  <label>RESOLUTION</label>
                  <select id="videogen-res">
                    <option value="720p">720p</option>
                    <option value="1080p" selected>1080p</option>
                    <option value="4k">4K (slow)</option>
                  </select>
                </div>
                <div class="cine-control">
                  <label>MOTION LANGUAGE</label>
                  <select id="videogen-motion">
                    <option>Static</option>
                    <option>Dolly In</option>
                    <option>Orbit 180</option>
                    <option>Crane Up</option>
                    <option>Tracking Shot</option>
                    <option>Handheld Shake</option>
                    <option>Parallax Reveal</option>
                  </select>
                </div>
              </div>
              <button id="videogen-render-btn" class="cine-render-btn" type="button"><span class="reel"></span>RENDER CLIP</button>
              <div id="videogen-status" class="cine-status"></div>
              <div id="videogen-result" class="cine-player-wrap"></div>
              <div id="videogen-lineage" class="cine-cut-history"></div>
            </div>
          </div>

          <!-- IMAGE → MOTION -->
          <div id="videogen-panel-img2vid" class="videogen-panel hidden">
            <div class="cine-director-card">
              <div class="imagegen-dropzone" id="videogen-img-drop" style="padding:28px 18px;">
                <input type="file" id="videogen-img-file" accept="image/*">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                <p style="margin:8px 0 0;font-size:12.5px;">Drop a still or click to upload — we will give it life</p>
              </div>
              <img id="videogen-img-preview" class="imagegen-preview hidden" alt="Reference still" style="max-height:180px;">
              <div class="videogen-prompt-wrap">
                <textarea id="videogen-img-prompt" placeholder="Slow cinematic push across the subject, gentle wind in hair, golden hour rim light..."></textarea>
              </div>
              <div style="margin: 8px 0 12px;">
                <label style="font-size:10px; font-weight:700; color:#fdba74; letter-spacing:1px;">VIDEO MODEL</label>
                <select id="videogen-img-model" style="width:100%; font-size:13px; padding:8px; background:#111; border:1px solid #f59e0b; color:#fff; border-radius:6px;">
                  <option value="demo-cinematic">Demo (test clip)</option>
                  <option value="kling-2.1-pro">Kling 2.1 Pro</option>
                  <option value="luma-ray2-1080">Luma Ray2</option>
                </select>
              </div>
              <div class="cine-controls-grid">
                <div class="cine-control">
                  <label>DURATION</label>
                  <div class="segmented" id="videogen-img-duration">
                    <button data-val="6s">6s</button>
                    <button data-val="10s" class="active">10s</button>
                    <button data-val="16s">16s</button>
                  </div>
                </div>
                <div class="cine-control">
                  <label>MOTION</label>
                  <select id="videogen-img-motion">
                    <option>Dolly In</option><option>Orbit</option><option>Crane Reveal</option><option>Parallax</option>
                  </select>
                </div>
              </div>
              <button id="videogen-img-btn" class="cine-render-btn" type="button"><span class="reel"></span>ANIMATE STILL</button>
              <div id="videogen-img-result" class="cine-player-wrap"></div>
            </div>
          </div>

          <!-- REMIX / EXTEND -->
          <div id="videogen-panel-remix" class="videogen-panel hidden">
            <div class="cine-director-card">
              <div id="videogen-remix-gallery" class="imagegen-mini-gallery" style="padding-bottom:4px;"></div>
              <div class="videogen-prompt-wrap">
                <textarea id="videogen-remix-prompt" placeholder="Continue the shot into a dramatic wide reveal, same color grade, add subtle lens breathing..."></textarea>
              </div>
              <button id="videogen-remix-btn" class="cine-render-btn" type="button">BRANCH NEW CUT</button>
              <div id="videogen-remix-result" class="cine-player-wrap"></div>
            </div>
          </div>
        </div>

        <aside class="videogen-reel-sidebar">
          <div class="reel-head">
            <h3>Your Clips</h3>
            <span class="count" id="videogen-count">0</span>
          </div>
          <div id="videogen-gallery" class="reel-wall"></div>
        </aside>
      </div>
    </main>

    <main id="audiogen-view" class="audiogen hidden">
      <div class="audiogen-shell">
        <div class="audiogen-workspace">
          <div class="audiogen-header">
            <div>
              <h2>AudioGen Studio</h2>
              <p>Convert text to speech with AI voices via Morpheus.</p>
            </div>
          </div>

          <div class="audiogen-card">
            <div class="audiogen-prompt-wrap">
              <textarea id="audiogen-text" placeholder="Enter text to convert to speech..."></textarea>
            </div>
            <div class="audiogen-controls">
              <select id="audiogen-voice">
                <option value="af_alloy">Alloy</option>
                <option value="af_echo">Echo</option>
                <option value="af_fable">Fable</option>
                <option value="af_onyx">Onyx</option>
                <option value="af_nova">Nova</option>
                <option value="af_shimmer">Shimmer</option>
              </select>
              <select id="audiogen-format">
                <option value="mp3">MP3</option>
                <option value="wav">WAV</option>
                <option value="aac">AAC</option>
                <option value="opus">Opus</option>
                <option value="flac">FLAC</option>
              </select>
              <label style="display:flex;align-items:center;gap:8px;font-size:12px;">
                <span>Speed:</span>
                <input id="audiogen-speed" type="range" min="0.25" max="4" step="0.25" value="1" style="width:100px;">
                <span id="audiogen-speed-label">1x</span>
              </label>
              <button id="audiogen-generate-btn" class="primary" type="button">Generate Audio</button>
            </div>
            <div id="audiogen-status"></div>
            <div id="audiogen-result"></div>
          </div>
        </div>
      </div>
    </main>

    <main id="settings-view" class="settings">
      <div class="guide-shell">
        <section class="guide-hero">
          <h2>Settings</h2>
          <p>Configure provider access and the default model used by chat and source-grounded guide explanations.</p>
        </section>

        <div class="settings-tabs" aria-label="Settings sections">
          <button id="settings-provider-tab" class="active" type="button">Provider</button>
          <button id="settings-persona-tab" type="button">Persona</button>
          <button id="settings-manage-tab" type="button">Manage</button>
          <button id="settings-workbench-tab" type="button">Workbench</button>
          <button id="settings-creator-tab" type="button" class="hidden">Creator</button>
        </div>

        <section id="provider-settings-section" class="feature-card settings-form settings-section">
          <!-- Sub-tabs for Chat / Image / Video providers -->
          <div class="provider-subtabs" role="tablist" aria-label="Provider type">
            <button type="button" class="provider-subtab active" data-subtab="chat" role="tab" aria-selected="true">Chat</button>
            <button type="button" class="provider-subtab" data-subtab="image" role="tab" aria-selected="false">Image</button>
            <button type="button" class="provider-subtab" data-subtab="video" role="tab" aria-selected="false">Video</button>
            <button type="button" class="provider-subtab" data-subtab="audio" role="tab" aria-selected="false">Audio</button>
          </div>

          <!-- Chat / LLM Provider -->
          <div id="provider-sub-chat" class="provider-subsection">
            <div class="settings-row">
              <div class="settings-field">
                <label for="provider">Provider</label>
                <select id="provider">
                  <option value="surplusintelligence">SurplusIntelligence</option>
                  <option value="morpheus">Morpheus</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="kimi-code">Kimi Code</option>
                  <option value="kimi">Kimi Platform</option>
                  <option value="other">Other</option>
                </select>
                <div class="hint">Select your LLM provider</div>
              </div>
              <div class="settings-field">
                <label for="model">Model</label>
                <input id="model" list="chat-model-options" value="gemma-4-uncensored">
                <datalist id="chat-model-options"></datalist>
                <div class="hint" id="model-hint">Morpheus default: gemma-4-uncensored.</div>
              </div>
            </div>

            <div class="settings-field" id="base-url-field">
              <label for="base-url">Endpoint</label>
              <input id="base-url" type="text" autocomplete="off" placeholder="https://api.example.com/v1/chat/completions">
              <div class="hint">OpenAI-compatible /v1 base URL or full /chat/completions endpoint</div>
            </div>

            <div class="settings-field">
              <label for="api-key">API key</label>
              <div class="inline-field">
                <input id="api-key" type="password" autocomplete="off" placeholder="sk-...">
                <button id="test-provider" class="secondary" type="button">Test</button>
                <button id="clear-provider-override" class="secondary" type="button">Use .env</button>
              </div>
              <div class="hint">Stored in this browser only. You can also set API_KEY in .env.local.</div>
            </div>
          </div>

          <!-- Image Generation Provider -->
          <div id="provider-sub-image" class="provider-subsection hidden">
            <div class="settings-row">
              <div class="settings-field">
                <label for="image-provider">Provider</label>
                <select id="image-provider">
                  <option value="surplusintelligence">SurplusIntelligence</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="morpheus">Morpheus</option>
                  <option value="other">Other</option>
                </select>
                <div class="hint">Provider for ImageGen Studio</div>
              </div>
              <div class="settings-field">
                <label for="image-model">Model</label>
                <select id="image-model"></select>
                <div class="hint" id="image-model-hint"></div>
              </div>
            </div>
            <div class="settings-field">
              <label for="image-api-key">API Key (optional override)</label>
              <input id="image-api-key" type="password" autocomplete="off" placeholder="Leave empty to use main key">
              <div class="hint">Separate key for image generation. Falls back to main API key if empty.</div>
            </div>
            <div class="settings-field">
              <label for="image-base-url">Base URL (optional)</label>
              <input id="image-base-url" type="url" autocomplete="off" placeholder="Leave empty to use provider default">
              <div class="hint">Optional image endpoint override for custom providers.</div>
            </div>
          </div>

          <!-- Video Generation Provider -->
          <div id="provider-sub-video" class="provider-subsection hidden">
            <div class="settings-row">
              <div class="settings-field">
                <label for="video-provider">Provider</label>
                <select id="video-provider">
                  <option value="surplusintelligence">SurplusIntelligence</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="morpheus">Morpheus</option>
                  <option value="demo">Demo (built-in)</option>
                  <option value="other">Other</option>
                </select>
                <div class="hint">Provider for VidGen Studio</div>
              </div>
              <div class="settings-field">
                <label for="video-model">Model</label>
                <select id="video-model"></select>
                <div class="hint" id="video-model-hint"></div>
              </div>
            </div>
            <div class="settings-field">
              <label for="video-api-key">API Key (optional override)</label>
              <input id="video-api-key" type="password" autocomplete="off" placeholder="Leave empty to use main key">
              <div class="hint">Separate key for video generation. Falls back to main API key if empty.</div>
            </div>
            <div class="settings-field">
              <label for="video-base-url">Base URL (optional)</label>
              <input id="video-base-url" type="url" autocomplete="off" placeholder="Leave empty to use provider default">
            </div>
          </div>

          <!-- Audio Generation Provider -->
          <div id="provider-sub-audio" class="provider-subsection hidden">
            <div class="settings-row">
              <div class="settings-field">
                <label for="audio-provider">Provider</label>
                <select id="audio-provider">
                  <option value="surplusintelligence">SurplusIntelligence</option>
                  <option value="morpheus">Morpheus</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="other">Other</option>
                </select>
                <div class="hint">Provider for AudioGen Studio</div>
              </div>
              <div class="settings-field">
                <label for="audio-model">Model</label>
                <input id="audio-model" list="audio-model-options" type="text" placeholder="Select a supported audio model" value="tts-kokoro">
                <datalist id="audio-model-options"></datalist>
                <div class="hint" id="audio-model-hint">Use a real Morpheus TTS model id, such as tts-kokoro, not a chat model name</div>
              </div>
            </div>
            <div class="settings-field">
              <label for="audio-api-key">API Key (optional override)</label>
              <input id="audio-api-key" type="password" autocomplete="off" placeholder="Leave empty to use main key">
              <div class="hint">Separate key for audio generation. Falls back to main API key if empty.</div>
            </div>
            <div class="settings-field">
              <label for="audio-base-url">Base URL (optional)</label>
              <input id="audio-base-url" type="url" autocomplete="off" placeholder="Leave empty to use provider default">
            </div>
            <div class="settings-row" style="margin-top:12px;">
              <button id="audio-test-provider" class="secondary" type="button">Test Audio Connection</button>
              <div class="hint">Sends a tiny text-to-speech request to verify Morpheus audio access.</div>
            </div>
          </div>

          <div class="settings-field" style="margin-top:14px;">
            <label>Daily-driver preferences</label>
            <div class="settings-row" style="gap:12px;flex-wrap:wrap;">
              <label class="hint" style="display:flex;align-items:center;gap:8px;">
                <input type="checkbox" id="stream-replies-toggle" checked>
                Stream replies
              </label>
              <label class="hint" style="display:flex;align-items:center;gap:8px;">
                <input type="checkbox" id="identity-bridge-toggle" checked>
                Identity bridge (cross-session)
              </label>
            </div>
            <div class="settings-row" style="margin-top:8px;">
              <label for="memory-autopilot" class="hint">Memory autopilot</label>
              <select id="memory-autopilot">
                <option value="off">Off — review everything</option>
                <option value="conservative" selected>Conservative — high-confidence global facts</option>
                <option value="trusted">Trusted — broader auto-accept</option>
              </select>
            </div>
            <button id="apply-recommended-defaults" class="secondary" type="button" style="margin-top:10px;">Apply recommended defaults</button>
            <div class="hint">Sets provider profile + memory/identity defaults that make Forge feel ready without fiddling.</div>
            <div class="settings-row" style="margin-top:14px; gap:8px; flex-wrap:wrap;">
              <button id="export-backup" class="secondary" type="button">Export backup zip</button>
              <label class="secondary" style="display:inline-flex;align-items:center;gap:8px;cursor:pointer;padding:8px 12px;border-radius:10px;">
                Restore backup
                <input id="restore-backup" type="file" accept=".zip,application/zip" style="display:none;">
              </label>
            </div>
            <div class="hint">Backup includes sessions, identity chain, personas, settings (media optional on export).</div>
            <div class="settings-field" style="margin-top:12px;">
              <label for="project-objective">Project mode (active session)</label>
              <input id="project-objective" placeholder="Objective for long-horizon work">
              <div class="settings-row" style="margin-top:8px;gap:8px;">
                <button id="make-project-session" class="secondary" type="button">Mark as project</button>
                <button id="make-chat-session" class="secondary" type="button">Mark as chat</button>
              </div>
              <div class="hint">Project sessions keep a separate task sub-chain for progress notes without bloating the chat ledger.</div>
            </div>
          </div>

          <div class="settings-status-panel" id="settings-status">
            <div class="status-header">
              <span class="status-indicator" id="status-dot"></span>
              <span class="status-label" id="status-label">Checking configuration...</span>
            </div>
            <div class="status-detail" id="status-detail"></div>
          </div>

          <!-- Effective Providers Summary -->
          <div class="provider-effective-summary">
            <div class="summary-title">Effective Configuration</div>
            <div class="summary-row">
              <span class="summary-label">Chat</span>
              <span class="summary-value" id="effective-chat"></span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Image</span>
              <span class="summary-value" id="effective-image"></span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Video</span>
              <span class="summary-value" id="effective-video"></span>
            </div>
            <div class="summary-note">Image and Video fall back to the main Chat provider + key when not configured separately.</div>
          </div>
        </section>

        <section id="persona-settings-section" class="feature-card settings-form settings-section hidden">
          <div class="settings-row">
            <div class="settings-field">
              <label for="persona-seed">Persona Studio</label>
              <input id="persona-name" placeholder="Persona name">
              <textarea id="persona-seed" placeholder="Example: lighthouse archivist, warm dry wit, remembers details carefully"></textarea>
              <button id="generate-persona" class="secondary" type="button">Generate Persona</button>
              <div class="hint">Creates a fictional inspired persona. It does not claim to be a real person.</div>
            </div>
            <div class="settings-field">
              <label for="manage-persona-select">Custom persona editor</label>
              <select id="manage-persona-select"></select>
              <input id="manage-persona-name" placeholder="Persona name">
              <textarea id="manage-persona-system" placeholder="Persona system prompt"></textarea>
              <select id="manage-persona-domain">
                <option value="auto">auto</option>
                <option value="architecture">architecture</option>
                <option value="system-design">system-design</option>
                <option value="api-design">api-design</option>
                <option value="debugging">debugging</option>
                <option value="security">security</option>
                <option value="testing">testing</option>
                <option value="performance">performance</option>
              </select>
              <select id="manage-persona-visibility">
                <option value="private">Private</option>
                <option value="public">Public</option>
              </select>
              <button id="manage-save-persona" class="secondary" type="button">Save Persona</button>
              <button id="manage-delete-persona" class="secondary danger" type="button">Delete Persona</button>
            </div>
          </div>
        </section>

        <section id="manage-settings-section" class="feature-card settings-form settings-section hidden">
          <div class="settings-status-panel" id="manage-status">
            <div class="status-header">
              <span class="status-indicator" id="manage-status-dot"></span>
              <span class="status-label" id="manage-status-label">Manage active session</span>
            </div>
            <div class="status-detail" id="manage-status-detail">Session state will load after startup.</div>
          </div>

          <div class="settings-row">
            <div class="settings-field">
              <label for="manage-freeze">Chain controls</label>
              <button id="manage-freeze" class="secondary" type="button">Freeze Chain</button>
              <div class="hint">Frozen sessions reject new sealed rings until unfrozen.</div>
            </div>
            <div class="settings-field">
              <label for="manage-ring-select">Archive rewind</label>
              <select id="manage-ring-select"></select>
              <button id="manage-rewind" class="secondary danger" type="button">Archive Rewind To Ring</button>
              <div class="hint">Creates a local archive before truncating the active session chain.</div>
            </div>
          </div>

          <div class="settings-row">
            <div class="settings-field">
              <label for="manage-session-select">Sessions</label>
              <select id="manage-session-select"></select>
              <input id="manage-session-name" placeholder="Session name">
              <button id="manage-rename-session" class="secondary" type="button">Rename Session</button>
              <button id="manage-delete-session" class="secondary danger" type="button">Delete Session</button>
              <div class="hint">The Default session cannot be deleted.</div>
            </div>
          </div>
        </section>

        <section id="workbench-settings-section" class="feature-card settings-form settings-section hidden">
          <h2>Timechain Workbench</h2>
          <div class="workbench-actions">
            <button id="refresh-workbench" type="button" class="secondary">Refresh Workbench</button>
            <button id="copy-sync-snapshot" type="button" class="secondary">Copy Sync Snapshot</button>
          </div>
          <div class="settings-row">
            <div class="settings-field">
              <label for="dream-domains">Dream synthesis</label>
              <input id="dream-domains" value="architecture,security" placeholder="architecture,security">
              <input id="dream-cycles" type="number" min="1" max="12" value="3">
              <button id="run-dream" class="secondary" type="button">Run Dream</button>
              <div class="hint">Seals cross-domain synthesis rings from existing high-signal domains.</div>
            </div>
            <div class="settings-field">
              <label for="overlay-tag">Overlays</label>
              <input id="overlay-tag" placeholder="tag">
              <input id="overlay-weight" type="number" step="0.1" value="1.0">
              <button id="save-overlay" class="secondary" type="button">Save Overlay</button>
              <div id="overlay-list" class="hint">No overlays loaded.</div>
            </div>
          </div>
          <div class="settings-row">
            <div class="settings-field">
              <label for="shared-memory-query">Shared Memory</label>
              <input id="shared-memory-query" placeholder="Search across other sessions...">
              <button id="search-shared-memory" class="secondary" type="button">Search</button>
              <div id="shared-memory-results" class="hint">No shared memory search yet.</div>
              <div class="hint">Persistent memories are durable facts shared per user; Shared Memory manually pulls accepted rings from other sessions.</div>
              <button id="import-shared-memory" class="secondary" type="button" style="margin-top:6px;">Import Selected</button>
              <button id="synthesize-shared-memory" class="secondary" type="button" style="margin-top:6px;">Synthesize Selected</button>
            </div>
            <div class="settings-field">
              <label for="fleet-source">Fleet import</label>
              <input id="fleet-source" placeholder="source agent">
              <textarea id="fleet-ring-json" placeholder='{"domain":"architecture","query":"...","content":"..."}'></textarea>
              <button id="run-fleet-import" class="secondary" type="button">Import Ring</button>
            </div>
          </div>
          <div class="settings-row">
            <div class="settings-field">
              <label for="challenge-indices">Temporal challenge</label>
              <input id="challenge-indices" placeholder="0,1">
              <input id="challenge-nonce" placeholder="optional nonce">
              <button id="run-challenge" class="secondary" type="button">Run Challenge</button>
              <button id="run-memory-sync" class="secondary" type="button">Memory Sync</button>
            </div>
          </div>
          <div id="advanced-timechain-results" class="result">Advanced Timechain actions not run yet.</div>
          <div id="cambium-results" class="result">Cambium not loaded yet.</div>
          <div id="ring-timeline" class="ring-list">Ring timeline not loaded yet.</div>
        </section>

        <section id="creator-settings-section" class="feature-card settings-form settings-section hidden">
          <h2>Creator Studio</h2>
          <p style="color:var(--muted);margin:0 0 12px;">Create personas from a source Timechain session, keep training in that same session, and publish a hidden frozen accepted-ring capsule to the marketplace.</p>
          <div class="settings-row">
            <div class="settings-field">
              <label>Create New Persona</label>
              <input id="creator-name" placeholder="Persona name">
              <input id="creator-tagline" placeholder="Short tagline">
              <select id="creator-domain">
                <option value="auto">auto</option>
                <option value="architecture">architecture</option>
                <option value="system-design">system-design</option>
                <option value="api-design">api-design</option>
                <option value="debugging">debugging</option>
                <option value="security">security</option>
                <option value="testing">testing</option>
                <option value="performance">performance</option>
                <option value="finance">finance</option>
                <option value="creative">creative</option>
              </select>
              <label>Source Timechain Session</label>
              <select id="creator-source-session"></select>
              <label>Marketplace Persona Instructions</label>
              <textarea id="creator-system" placeholder="Prefilled from the source session persona. Edit before publishing."></textarea>
              <label>Marketplace Pricing</label>
              <select id="creator-price-model">
                <option value="free">Free</option>
                <option value="premium">Premium</option>
              </select>
              <input id="creator-price-amount" class="hidden" type="number" min="0" step="0.01" placeholder="Premium price in USD">
              <button id="creator-save" class="secondary" type="button">Create Persona</button>
            </div>
            <div class="settings-field">
              <label>My Personas</label>
              <div id="creator-list" class="creator-persona-list">
                <div style="color:var(--muted);font-size:13px;">No personas created yet.</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <aside class="inspector">
      <div class="inspector-head">
        <div class="inspector-head-text">
          <strong>Memory Inspector</strong>
          <span>Recall, verify, and inspect the local chain.</span>
        </div>
        <button id="inspector-collapse" type="button" class="settings-icon" aria-label="Collapse or expand inspector" title="Collapse inspector">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
        </button>
      </div>
      <div class="inspector-body">
        <section class="panel expanded" data-panel="self">
          <div class="panel-header">
            <h2>Self Model</h2>
            <svg class="panel-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
          <div class="panel-body">
            <dl id="summary"></dl>
          </div>
        </section>

        <section class="panel" data-panel="pending">
          <div class="panel-header">
            <h2>Pending Memories</h2>
            <svg class="panel-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
          <div class="panel-body">
            <div id="pending-memories" class="memory-list">No pending memories.</div>
          </div>
        </section>

        <section class="panel" data-panel="accepted">
          <div class="panel-header">
            <h2>Accepted Memories</h2>
            <svg class="panel-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
          <div class="panel-body">
            <div id="accepted-memories" class="memory-list">No accepted memories.</div>
          </div>
        </section>

        <section class="panel" data-panel="recall">
          <div class="panel-header">
            <h2>Recall</h2>
            <svg class="panel-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
          <div class="panel-body">
            <form id="recall-form" class="stack">
              <input id="recall-query" placeholder="Search prior rings" required>
              <button type="submit" class="secondary">Recall</button>
            </form>
            <div id="recall-results" class="result">No recall query yet.</div>
          </div>
        </section>

        <section class="panel" data-panel="chain">
          <div class="panel-header">
            <h2>Chain</h2>
            <svg class="panel-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </div>
          <div class="panel-body">
            <div class="stack">
              <button id="verify" type="button" class="secondary">Verify Chain</button>
              <button id="reset-chain" type="button" class="secondary">Reset Chain Memory</button>
              <div id="verify-result" class="result">Not checked yet.</div>
            </div>
          </div>
        </section>
      </div>
    </aside>
    <nav class="mobile-nav" aria-label="Mobile view">
      <button id="mob-chat" class="active" type="button">Chat</button>
      <button id="mob-guide" type="button">Guide</button>
      <button id="mob-marketplace" type="button">Market</button>
      <button id="mob-imagegen" type="button">ImageGen</button>
      <button id="mob-videogen" type="button">VidGen</button>
      <button id="mob-settings" type="button">Settings</button>
    </nav>
  </div>
  <div id="overlay-backdrop" class="overlay-backdrop"></div>

  <!-- Inspector collapse behavior (global, works on all pages) -->
  <script>
  (function(){
    const app = document.querySelector('.app');
    const inspector = document.querySelector('.inspector');
    const btn = document.getElementById('inspector-collapse');
    if (!app || !inspector || !btn) return;

    function apply(collapsed) {
      app.classList.toggle('inspector-collapsed', collapsed);
      inspector.classList.toggle('collapsed', collapsed);
    }

    // restore saved state
    const saved = localStorage.getItem('inspectorCollapsed') === 'true';
    apply(saved);

    // header button
    btn.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      const isCollapsed = app.classList.contains('inspector-collapsed');
      const next = !isCollapsed;
      apply(next);
      localStorage.setItem('inspectorCollapsed', next ? 'true' : 'false');
    });

    // click anywhere on the collapsed slim bar to expand
    inspector.addEventListener('click', (e) => {
      if (inspector.classList.contains('collapsed') && !e.target.closest('#inspector-collapse')) {
        apply(false);
        localStorage.setItem('inspectorCollapsed', 'false');
      }
    });
  })();
  </script>

  <!-- Auth Overlay -->
  <div class="auth-overlay hidden" id="auth-overlay">
    <div class="auth-card">
      <div class="auth-logo">F</div>
      <h2>Forge</h2>
      <p class="subtitle">PoC host for CypherTempre — local memory you can verify</p>
      <div class="auth-tabs">
        <button id="auth-tab-login" class="active" type="button">Log in</button>
        <button id="auth-tab-register" type="button">Register</button>
      </div>
      <div id="auth-login-form">
        <div class="auth-field">
          <label>Username</label>
          <input id="auth-login-user" placeholder="your-name" autocomplete="username">
        </div>
        <div class="auth-field">
          <label>Password</label>
          <input id="auth-login-pass" type="password" placeholder="••••" autocomplete="current-password">
        </div>
        <button class="auth-submit" id="auth-login-btn" type="button">Log in</button>
      </div>
      <div id="auth-register-form" class="hidden">
        <div class="auth-field">
          <label>Username</label>
          <input id="auth-reg-user" placeholder="your-name" autocomplete="username">
        </div>
        <div class="auth-field">
          <label>Display name</label>
          <input id="auth-reg-display" placeholder="Your Name" autocomplete="name">
        </div>
        <div class="auth-field">
          <label>Password</label>
          <input id="auth-reg-pass" type="password" placeholder="••••" autocomplete="new-password">
        </div>
        <button class="auth-submit" id="auth-register-btn" type="button">Create account</button>
      </div>
      <div class="auth-hint" id="auth-message"></div>
    </div>
  </div>

  <!-- Persona Detail Drawer -->
  <aside class="detail-drawer" id="detail-drawer">
    <div class="detail-drawer-head">
      <div>
        <div class="domain-badge" id="detail-domain"><span class="domain-dot"></span><span id="detail-domain-text">domain</span></div>
        <h2 id="detail-name">Persona</h2>
      </div>
      <button class="settings-icon" id="detail-close" type="button" aria-label="Close">✕</button>
    </div>
    <div class="detail-drawer-body">
      <p id="detail-tagline" style="color:var(--muted);margin:0;"></p>
      <div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:6px;">
          <span>Temporal Mass</span>
          <span id="detail-mass-value">0</span>
        </div>
        <div class="temporal-mass-bar"><div class="temporal-mass-fill" id="detail-mass-bar" style="width:0%"></div></div>
      </div>
      <div id="detail-capsule" style="display:grid;gap:10px;"></div>
    </div>
    <div class="detail-drawer-foot">
      <button class="auth-submit" id="detail-subscribe" type="button">Subscribe</button>
      <button class="secondary" id="detail-unsubscribe" type="button" style="display:none;">Unsubscribe</button>
      <div class="auth-hint" id="detail-sub-hint"></div>
    </div>
  </aside>

  <div class="command-palette-backdrop" id="command-palette" aria-hidden="true">
    <div class="command-palette" role="dialog" aria-label="Command palette">
      <input id="command-palette-input" type="text" placeholder="Type a command… (sessions, recall, verify, backup, project)" autocomplete="off">
      <div class="command-palette-list" id="command-palette-list"></div>
      <div class="command-palette-hint">↑↓ navigate · Enter run · Esc close · Ctrl/Cmd+K open</div>
    </div>
  </div>

  <script>
    const els = {
{ui_js}  </script>
</body>
</html>
"""
