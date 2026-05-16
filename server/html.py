"""HTML + CSS template for the CypherTempre chat interface."""

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#000000">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" type="image/svg+xml" href="/icon.svg">
  <link rel="apple-touch-icon" href="/icon.svg">
  <title>CypherTempre</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #000000;
      --surface: #0f0f0f;
      --surface-2: #1a1a1a;
      --surface-3: #262626;
      --line: #333333;
      --line-soft: #1a1a1a;
      --text: #ededed;
      --muted: #a3a3a3;
      --faint: #525252;
      --green: #22c55e;
      --blue: #10aceb;
      --amber: #d6b36a;
      --red: #ef4444;
      --shadow: rgba(0, 0, 0, 0.45);
      --nav-bg: rgba(17, 17, 17, 0.6);
      --nav-active-bg: linear-gradient(180deg, #10aceb, #0a8ec5);
      --nav-active-text: #ffffff;
      --input-bg: #0f0f0f;
      --panel-bg: rgba(10, 10, 10, 0.72);
      --bubble-bg: rgba(17, 17, 17, 0.82);
      --user-bubble-bg: linear-gradient(180deg, #0d1f2d, #0a1822);
      --composer-bg: rgba(0, 0, 0, 0.88);
      --chat-top-bg: rgba(0, 0, 0, 0.72);
      --status-card-bg: linear-gradient(180deg, #111111, #0a0a0a);
      --rail-inspector-bg: rgba(8, 8, 8, 0.82);
      --mobile-nav-bg: rgba(8, 8, 8, 0.92);
      --overlay-bg: rgba(0, 0, 0, 0.65);
      --guide-hero-bg: linear-gradient(135deg, rgba(16, 172, 235, 0.08), rgba(0, 0, 0, 0.96) 44%, rgba(34, 197, 94, 0.06));
      --feature-card-bg: rgba(17, 17, 17, 0.72);
      --project-attribution-bg: rgba(15, 15, 15, 0.88);
      --memory-card-bg: rgba(17, 17, 17, 0.72);
      --ring-card-bg: rgba(17, 17, 17, 0.72);
      --thinking-bg: linear-gradient(180deg, rgba(13, 31, 45, 0.95), rgba(8, 18, 26, 0.95));
      --rejected-bg: #1a0f0f;
      --orb-1: rgba(16, 172, 235, 0.15);
      --orb-2: rgba(34, 197, 94, 0.10);
      --orb-3: rgba(214, 179, 106, 0.08);
    }

    .light {
      color-scheme: light;
      --bg: #f7f7f5;
      --surface: #ffffff;
      --surface-2: #f0f0ee;
      --surface-3: #e8e8e6;
      --line: #d4d4d0;
      --line-soft: #e8e8e4;
      --text: #1a1a1a;
      --muted: #6b6b6b;
      --faint: #9a9a9a;
      --green: #16a34a;
      --blue: #0284c7;
      --amber: #b5892a;
      --red: #dc2626;
      --shadow: rgba(0, 0, 0, 0.08);
      --nav-bg: rgba(240, 240, 238, 0.6);
      --nav-active-bg: linear-gradient(180deg, #10aceb, #0a8ec5);
      --nav-active-text: #ffffff;
      --input-bg: #f7f7f5;
      --panel-bg: rgba(255, 255, 255, 0.82);
      --bubble-bg: rgba(255, 255, 255, 0.88);
      --user-bubble-bg: linear-gradient(180deg, #e8f4fa, #dceef7);
      --composer-bg: rgba(247, 247, 245, 0.92);
      --chat-top-bg: rgba(247, 247, 245, 0.82);
      --status-card-bg: linear-gradient(180deg, #ffffff, #f0f0ee);
      --rail-inspector-bg: rgba(255, 255, 255, 0.88);
      --mobile-nav-bg: rgba(255, 255, 255, 0.95);
      --overlay-bg: rgba(0, 0, 0, 0.35);
      --guide-hero-bg: linear-gradient(135deg, rgba(16, 172, 235, 0.06), rgba(247, 247, 245, 0.96) 44%, rgba(34, 197, 94, 0.04));
      --feature-card-bg: rgba(255, 255, 255, 0.82);
      --project-attribution-bg: rgba(247, 247, 245, 0.92);
      --memory-card-bg: rgba(247, 247, 245, 0.72);
      --ring-card-bg: rgba(247, 247, 245, 0.72);
      --thinking-bg: linear-gradient(180deg, rgba(232, 244, 250, 0.98), rgba(220, 238, 247, 0.98));
      --rejected-bg: #f5e8e8;
      --orb-1: rgba(16, 172, 235, 0.10);
      --orb-2: rgba(34, 197, 94, 0.06);
      --orb-3: rgba(214, 179, 106, 0.04);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      transition: background-color 0.3s, color 0.3s;
    }

    button, input, textarea, select { font: inherit; }
    button, a, [role="button"] { -webkit-tap-highlight-color: transparent; touch-action: manipulation; }

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
      grid-template-columns: 286px minmax(0, 1fr) 360px;
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
      position: relative;
    }

    .rail, .inspector {
      background: var(--rail-inspector-bg);
      border-color: var(--line);
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
      transition: background-color 0.3s;
    }

    .rail {
      border-right: 1px solid var(--line);
      grid-template-rows: auto minmax(0, 1fr) auto;
      background: linear-gradient(180deg, #0f0f0f 0%, #111111 100%);
      position: relative;
      z-index: 2;
    }

    .light .rail {
      background: linear-gradient(180deg, #f0f0ee 0%, #f7f7f5 100%);
    }

    .inspector {
      backdrop-filter: blur(20px) saturate(1.2);
    }

    .brand {
      padding: 22px 18px;
      border-bottom: 1px solid var(--line-soft);
      background: linear-gradient(180deg, rgba(16, 172, 235, 0.06), transparent);
    }

    .brand-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .brand h1 {
      margin: 0;
      font-size: 24px;
      letter-spacing: -0.02em;
      line-height: 1.1;
      font-weight: 750;
      background: linear-gradient(180deg, #ededed, #a3a3a3);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .brand p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .settings-icon {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--nav-bg);
      color: var(--muted);
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s, border-color 0.2s, transform 0.15s;
    }

    .settings-icon:hover,
    .settings-icon.active {
      color: var(--text);
      border-color: var(--blue);
      background: var(--surface-2);
      transform: scale(1.05);
    }

    .theme-toggle {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 50%;
      background: var(--nav-bg);
      color: var(--muted);
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s, border-color 0.2s, transform 0.2s;
    }

    .theme-toggle:hover {
      color: var(--text);
      border-color: var(--blue);
      background: var(--surface-2);
      transform: scale(1.05);
    }

    .theme-toggle svg {
      width: 18px;
      height: 18px;
    }

    .rail-section {
      padding: 16px;
      display: grid;
      gap: 20px;
      align-content: start;
      overflow: auto;
    }

    .group {
      display: grid;
      gap: 9px;
    }

    .nav {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 3px;
      padding: 3px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(17, 17, 17, 0.8);
      width: 100%;
      overflow: hidden;
    }

    .nav button {
      min-height: 34px;
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-weight: 700;
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 0 8px;
      transition: background-color 0.2s, color 0.2s;
    }

    .nav button:hover {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
    }

    .nav button.active {
      color: var(--nav-active-text);
      background: var(--nav-active-bg);
      box-shadow: 0 2px 12px rgba(16, 172, 235, 0.25);
    }

    .nav button svg {
      width: 15px;
      height: 15px;
      flex-shrink: 0;
    }

    label {
      color: var(--faint);
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-top: 4px;
    }

    .rail-section label:first-child,
    .group label:first-child {
      margin-top: 0;
    }

    input, select, textarea {
      width: 100%;
      color: var(--text);
      background: var(--input-bg);
      border: 1px solid var(--line);
      border-radius: 8px;
      outline: none;
      transition: background-color 0.3s, border-color 0.2s, box-shadow 0.2s;
    }

    input, select {
      height: 36px;
      padding: 0 10px;
    }

    textarea {
      resize: vertical;
      min-height: 50px;
      max-height: 120px;
      padding: 11px 12px;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--blue);
      box-shadow: 0 0 0 3px rgba(16, 172, 235, 0.12);
    }

    .hint {
      color: var(--faint);
      font-size: 11px;
    }

    .status-card {
      margin: 10px 12px 12px;
      padding: 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--status-card-bg);
      color: var(--muted);
      font-size: 13px;
      transition: background-color 0.3s;
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
      grid-template-rows: auto minmax(0, 1fr) auto;
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
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--nav-bg);
      backdrop-filter: blur(12px);
      width: fit-content;
    }

    .settings-tabs button {
      min-height: 32px;
      border: 0;
      border-radius: 999px;
      padding: 0 14px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-weight: 700;
      font-size: 12px;
      transition: background-color 0.2s, color 0.2s;
    }

    .settings-tabs button.active {
      background: rgba(16, 172, 235, 0.14);
      color: var(--blue);
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
      border-radius: 12px;
      padding: 24px;
      background: var(--guide-hero-bg);
      box-shadow: 0 18px 44px var(--shadow);
      transition: background-color 0.3s;
    }

    .guide-hero h2 {
      margin: 0;
      font-size: 30px;
      letter-spacing: -0.02em;
    }

    .guide-hero p {
      max-width: 760px;
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 15px;
    }

    .guide-controls {
      display: inline-flex;
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--nav-bg);
      backdrop-filter: blur(12px);
    }

    .guide-controls button {
      border: 0;
      border-radius: 999px;
      min-height: 32px;
      padding: 0 14px;
      color: var(--muted);
      background: transparent;
      cursor: pointer;
      font-weight: 700;
      font-size: 12px;
      transition: background-color 0.2s, color 0.2s;
    }

    .guide-controls button.active {
      color: #ffffff;
      background: linear-gradient(180deg, #10aceb, #0a8ec5);
      box-shadow: 0 2px 8px rgba(16, 172, 235, 0.25);
    }

    .feature-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .feature-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--feature-card-bg);
      backdrop-filter: blur(12px);
      padding: 16px;
      transition: background-color 0.3s, transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 24px var(--shadow);
    }

    .feature-card h3 {
      margin: 0 0 8px;
      font-size: 16px;
      letter-spacing: -0.01em;
    }

    .feature-card p {
      margin: 0;
      color: var(--muted);
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
      padding: 16px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--chat-top-bg);
      backdrop-filter: blur(16px) saturate(1.2);
      transition: background-color 0.3s;
    }

    .chat-title {
      min-width: 0;
      flex: 1 1 auto;
    }

    .chat-title strong {
      display: block;
      font-size: 16px;
      letter-spacing: -0.01em;
    }

    .chat-title span {
      display: block;
      color: var(--muted);
      font-size: 13px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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
      background: var(--surface);
      color: var(--muted);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
      letter-spacing: 0.01em;
    }

    .badge.ok { color: var(--green); border-color: rgba(34, 197, 94, 0.3); }
    .badge.warn { color: var(--amber); border-color: rgba(214, 179, 106, 0.3); }
    .badge.info { color: var(--blue); border-color: rgba(16, 172, 235, 0.3); }
    .badge.bad { color: var(--red); border-color: rgba(239, 68, 68, 0.3); }

    .messages {
      overflow: auto;
      min-height: 0;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .empty {
      margin: auto;
      width: min(640px, 100%);
      color: var(--muted);
      text-align: center;
      display: grid;
      gap: 12px;
    }

    .empty h2 {
      margin: 0;
      color: var(--text);
      font-size: 28px;
      letter-spacing: -0.02em;
    }

    .empty p { margin: 0; }

    .message {
      display: grid;
      grid-template-columns: 38px minmax(0, 1fr);
      gap: 12px;
      max-width: 980px;
      width: 100%;
    }

    .message.user {
      align-self: flex-end;
      grid-template-columns: minmax(0, 1fr) 38px;
    }

    .avatar {
      width: 38px;
      height: 38px;
      display: grid;
      place-items: center;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--green);
      font-weight: 800;
      font-size: 13px;
    }

    .message.user .avatar {
      grid-column: 2;
      color: var(--blue);
    }

    .bubble {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--bubble-bg);
      backdrop-filter: blur(12px);
      box-shadow: 0 18px 44px var(--shadow);
      overflow: hidden;
      transition: background-color 0.3s;
    }

    .message.user .bubble {
      grid-column: 1;
      grid-row: 1;
      background: var(--user-bubble-bg);
      border-color: rgba(16, 172, 235, 0.35);
    }

    .light .message.user .bubble {
      border-color: #7dd3fc;
    }

    .message.rejected .bubble {
      background: var(--rejected-bg);
      border-color: var(--red);
    }

    .message.thinking-message .bubble {
      border-color: rgba(16, 172, 235, 0.4);
      background: var(--thinking-bg);
    }

    .light .message.thinking-message .bubble {
      border-color: #7dd3fc;
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
        radial-gradient(circle at 20% 30%, rgba(16, 172, 235, 0.10), transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(34, 197, 94, 0.08), transparent 50%),
        rgba(5, 5, 5, 0.92);
      transition: opacity 0.35s ease, visibility 0.35s ease;
    }
    .light .auth-overlay {
      background:
        radial-gradient(circle at 20% 30%, rgba(16, 172, 235, 0.06), transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(34, 197, 94, 0.04), transparent 50%),
        rgba(247, 247, 245, 0.92);
    }
    .auth-overlay.hidden {
      opacity: 0;
      pointer-events: none;
      visibility: hidden;
    }
    .auth-card {
      width: min(400px, 92vw);
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--surface);
      padding: 36px 32px;
      display: grid;
      gap: 18px;
      box-shadow:
        0 32px 64px -12px rgba(0, 0, 0, 0.55),
        0 0 0 1px rgba(255, 255, 255, 0.03) inset;
      animation: authEnter 0.5s cubic-bezier(0.22, 1, 0.36, 1);
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
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: linear-gradient(135deg, #10aceb, #0a8ec5);
      display: grid;
      place-items: center;
      font-size: 24px;
      font-weight: 900;
      color: #ffffff;
      margin: 0 auto;
      box-shadow: 0 8px 24px rgba(16, 172, 235, 0.30);
    }
    .auth-card h2 { margin: 0; font-size: 24px; text-align: center; letter-spacing: -0.02em; }
    .auth-card .subtitle { margin: -10px 0 0; color: var(--muted); font-size: 14px; text-align: center; }
    .auth-tabs {
      display: inline-flex;
      gap: 0;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--surface-2);
      overflow: hidden;
      padding: 3px;
    }
    .auth-tabs button {
      flex: 1;
      min-height: 36px;
      border: 0;
      border-radius: 9px;
      background: transparent;
      color: var(--muted);
      font-weight: 700;
      cursor: pointer;
      font-size: 13px;
      transition: background-color 0.2s, color 0.2s;
    }
    .auth-tabs button.active {
      color: #ffffff;
      background: linear-gradient(180deg, #10aceb, #0a8ec5);
      box-shadow: 0 2px 8px rgba(16, 172, 235, 0.25);
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
      height: 44px;
      padding: 0 14px;
      border-radius: 10px;
      font-size: 14px;
      background: var(--input-bg);
    }
    .auth-submit {
      min-height: 48px;
      border-radius: 12px;
      border: 0;
      color: #ffffff;
      background: linear-gradient(180deg, #10aceb, #0a8ec5);
      cursor: pointer;
      font-weight: 800;
      font-size: 15px;
      box-shadow: 0 4px 16px rgba(16, 172, 235, 0.30);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .auth-submit:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(16, 172, 235, 0.40);
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
      padding: 0 12px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--text);
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      transition: background-color 0.2s, border-color 0.2s;
    }
    .account-btn:hover {
      background: var(--surface-3);
      border-color: var(--blue);
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
      padding: 30px;
    }
    .marketplace.active { display: block; }
    .marketplace-hero {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 24px;
      background: var(--guide-hero-bg);
      box-shadow: 0 18px 44px var(--shadow);
      margin-bottom: 18px;
    }
    .marketplace-hero h2 { margin: 0; font-size: 26px; letter-spacing: -0.02em; }
    .marketplace-hero p { margin: 8px 0 0; color: var(--muted); font-size: 15px; }
    .marketplace-filters {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 18px;
      align-items: center;
    }
    .marketplace-filters input {
      flex: 1 1 220px;
      min-width: 180px;
    }
    .filter-pill {
      min-height: 34px;
      padding: 0 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--surface);
      color: var(--muted);
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s;
    }
    .filter-pill:hover {
      background: var(--surface-2);
      color: var(--text);
    }
    .filter-pill.active {
      color: #ffffff;
      background: linear-gradient(180deg, #10aceb, #0a8ec5);
      border-color: transparent;
      box-shadow: 0 2px 8px rgba(16, 172, 235, 0.25);
    }
    .marketplace-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 16px;
    }
    .persona-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--feature-card-bg);
      backdrop-filter: blur(12px);
      padding: 16px;
      display: grid;
      gap: 10px;
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .persona-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 28px var(--shadow);
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
    .price-badge.premium { background: rgba(16, 172, 235, 0.14); color: var(--blue); }
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
    .status-pending { background: rgba(16, 172, 235, 0.12); color: var(--blue); }
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
      gap: 12px;
      padding: 9px 12px;
      border-bottom: 1px solid var(--line-soft);
      color: var(--muted);
      font-size: 12px;
      background: rgba(255, 255, 255, 0.015);
    }

    .bubble-content {
      padding: 13px 14px;
      overflow-wrap: anywhere;
      font-size: 15px;
      line-height: 1.55;
      white-space: pre-wrap;
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
      padding: 16px 22px 20px;
      border-top: 1px solid var(--line);
      background: var(--composer-bg);
      backdrop-filter: blur(16px) saturate(1.2);
      transition: background-color 0.3s;
    }

    .composer-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      max-width: 1020px;
      margin: 0 auto;
    }

    .send {
      width: 46px;
      min-height: 46px;
      border-radius: 10px;
      border: 1px solid rgba(16, 172, 235, 0.5);
      color: #ffffff;
      background: linear-gradient(180deg, #10aceb, #0a8ec5);
      cursor: pointer;
      font-size: 18px;
      font-weight: 900;
      box-shadow: 0 4px 14px rgba(16, 172, 235, 0.25);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .send:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(16, 172, 235, 0.35);
    }

    .send:disabled {
      opacity: 0.55;
      cursor: not-allowed;
      transform: none;
    }

    .composer-warning {
      display: none;
      max-width: 1020px;
      margin: 0 auto 12px;
      padding: 10px 12px;
      border: 1px solid var(--amber);
      border-radius: 8px;
      background: rgba(214, 179, 106, 0.10);
      color: var(--amber);
      font-size: 13px;
      line-height: 1.45;
    }
    .composer-warning.active {
      display: block;
    }

    .inspector {
      border-left: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
    }

    .inspector-head {
      padding: 16px;
      border-bottom: 1px solid var(--line-soft);
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
      border-radius: 10px;
      background: var(--panel-bg);
      backdrop-filter: blur(12px);
      overflow: hidden;
      transition: background-color 0.3s;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px;
      cursor: pointer;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
    }

    .panel-header:hover {
      background: var(--surface-2);
    }

    .panel-header h2 {
      margin: 0;
      color: var(--muted);
      font-size: 11px;
      letter-spacing: 0.07em;
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
      border-radius: 8px;
      background: var(--surface-2);
      color: var(--text);
      cursor: pointer;
      font-weight: 700;
      font-size: 13px;
      transition: background-color 0.2s, border-color 0.2s, transform 0.1s;
    }

    .secondary:hover {
      background: var(--surface-3);
      border-color: var(--blue);
    }

    .secondary.danger {
      border-color: rgba(239, 68, 68, 0.4);
      color: #fca5a5;
      background: rgba(91, 36, 34, 0.32);
    }

    .secondary.danger:hover {
      border-color: var(--red);
      background: rgba(91, 36, 34, 0.45);
    }

    .secondary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
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
      border-radius: 8px;
      background: var(--memory-card-bg);
      padding: 9px;
      display: grid;
      gap: 7px;
      transition: background-color 0.3s;
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
      border-radius: 8px;
      background: var(--ring-card-bg);
      padding: 9px;
      display: grid;
      gap: 6px;
      transition: background-color 0.3s;
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

    @media (max-width: 1120px) {
      .app { grid-template-columns: 238px minmax(0, 1fr) 300px; }
      .inspector { border-left: 1px solid var(--line); border-top: 0; }
      .feature-grid { grid-template-columns: 1fr; }
      .nav button { font-size: 0; gap: 0; padding: 0 6px; }
      .nav button svg { width: 17px; height: 17px; }
      .nav button.active svg { filter: drop-shadow(0 0 4px rgba(16,172,235,0.5)); }
    }

    @media (max-width: 760px) {
      .app { display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
      .chat { height: auto; flex: 1; min-height: 0; }
      .guide { min-height: 0; }
      .guide.active { flex: 1; min-height: 0; }
      .settings { height: auto; }
      .settings.active { flex: 1; min-height: 0; }
      .rail { position: fixed; left: 0; top: 0; bottom: 0; width: min(320px, 86vw); z-index: 100; transform: translateX(-101%); transition: transform .25s ease; border-right: 1px solid var(--line); background: linear-gradient(180deg, #0f0f0f 0%, #111111 100%); display: grid; grid-template-rows: auto minmax(0, 1fr) auto; overflow-y: auto; -webkit-overflow-scrolling: touch; }
      .rail.open { transform: translateX(0); }
      .brand { padding: 12px 14px; }
      .brand-row { display: block; }
      .rail-section { min-height: 0; overflow-y: auto; padding: 10px 10px 18px; }
      .nav { display: grid; grid-template-columns: repeat(2, 1fr); }
      .nav button { min-height: 38px; font-size: 13px; }
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
      .mobile-nav button.active { color: var(--blue); background: rgba(16, 172, 235, 0.08); }
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

    /* ImageGen Studio */
    .imagegen { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
    .imagegen-shell { display: grid; grid-template-columns: 1fr 300px; gap: 20px; height: 100%; overflow: hidden; padding: 24px; }
    .imagegen-workspace { display: flex; flex-direction: column; gap: 16px; overflow: hidden; min-width: 0; }
    .imagegen-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-shrink: 0; }
    .imagegen-header h2 { margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.3px; }
    .imagegen-header p { margin: 0; font-size: 13px; color: var(--muted); }
    .imagegen-modes { display: inline-flex; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 4px; gap: 2px; flex-shrink: 0; }
    .imagegen-modes button { padding: 8px 16px; border-radius: 8px; border: none; background: transparent; color: var(--muted); cursor: pointer; font-size: 13px; font-weight: 500; transition: all .2s; }
    .imagegen-modes button:hover { color: var(--text); }
    .imagegen-modes button.active { background: var(--accent); color: #fff; }
    .imagegen-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 14px; overflow: auto; }
    .imagegen-panel { display: flex; flex-direction: column; gap: 14px; }
    .imagegen-panel.hidden { display: none; }
    .imagegen-prompt-wrap { position: relative; }
    .imagegen-prompt-wrap textarea { width: 100%; min-height: 100px; resize: vertical; border-radius: 12px; border: 1px solid var(--border); background: var(--bg); color: var(--text); padding: 14px; font-size: 14px; line-height: 1.5; }
    .imagegen-prompt-wrap textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(16,172,235,0.12); }
    .imagegen-controls { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .imagegen-controls select { flex: 1; min-width: 160px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font-size: 13px; cursor: pointer; }
    .imagegen-controls button.primary { min-width: 120px; padding: 10px 20px; border-radius: 10px; border: none; background: linear-gradient(135deg, var(--accent), #0ea5e9); color: #fff; font-size: 14px; font-weight: 600; cursor: pointer; transition: transform .15s, box-shadow .15s; }
    .imagegen-controls button.primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(16,172,235,0.35); }
    .imagegen-controls button.primary:active { transform: translateY(0); }
    .imagegen-status { font-size: 13px; color: var(--muted); min-height: 18px; display: flex; align-items: center; gap: 8px; }
    .imagegen-spinner { width: 16px; height: 16px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: imagegen-spin 0.8s linear infinite; }
    @keyframes imagegen-spin { to { transform: rotate(360deg); } }
    .imagegen-result { display: flex; flex-direction: column; gap: 12px; }
    .imagegen-result-card { background: var(--bg); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
    .imagegen-result-card img { display: block; width: 100%; height: auto; }
    .imagegen-result-meta { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; font-size: 12px; color: var(--muted); background: var(--surface); border-top: 1px solid var(--border); }
    .imagegen-result-meta .badge { background: rgba(16,172,235,0.12); color: var(--accent); padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .imagegen-lineage { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 12px; color: var(--muted); padding: 10px 12px; border: 1px solid var(--border); border-radius: 10px; background: var(--surface); }
    .imagegen-lineage.hidden { display: none; }
    .imagegen-lineage .crumb { color: var(--text); background: var(--bg); border: 1px solid var(--border); border-radius: 999px; padding: 3px 9px; }
    .imagegen-lineage .arrow { opacity: 0.55; }
    .imagegen-dropzone { border: 2px dashed var(--border); border-radius: 14px; padding: 40px 24px; text-align: center; color: var(--muted); cursor: pointer; transition: all .2s; background: var(--bg); }
    .imagegen-dropzone:hover { border-color: var(--accent); background: rgba(16,172,235,0.06); }
    .imagegen-dropzone svg { width: 36px; height: 36px; stroke-width: 1.5; margin-bottom: 10px; opacity: 0.6; }
    .imagegen-dropzone p { margin: 0; font-size: 13px; }
    .imagegen-dropzone .hint { font-size: 11px; margin-top: 6px; opacity: 0.7; }
    .imagegen-dropzone input { display: none; }
    .imagegen-preview { max-width: 100%; max-height: 260px; border-radius: 12px; border: 1px solid var(--border); object-fit: contain; background: var(--bg); }
    .imagegen-preview.hidden { display: none; }
    .imagegen-sidebar { display: flex; flex-direction: column; gap: 12px; overflow: hidden; background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }
    .imagegen-sidebar-head { display: flex; align-items: center; justify-content: space-between; }
    .imagegen-sidebar-head h3 { margin: 0; font-size: 14px; font-weight: 600; }
    .imagegen-sidebar-head .count { font-size: 12px; color: var(--muted); background: var(--bg); padding: 2px 8px; border-radius: 10px; }
    .imagegen-gallery-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; overflow: auto; }
    .imagegen-gallery-grid .empty { color: var(--muted); font-size: 12px; text-align: center; padding: 24px 8px; }
    .imagegen-gallery-grid .empty svg { width: 32px; height: 32px; stroke-width: 1.5; margin-bottom: 8px; opacity: 0.5; }
    .imagegen-gallery-grid .thumb { position: relative; aspect-ratio: 1; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); cursor: pointer; background: var(--bg); transition: transform .15s, box-shadow .15s; }
    .imagegen-gallery-grid .thumb:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.25); }
    .imagegen-gallery-grid .thumb img { width: 100%; height: 100%; object-fit: cover; }
    .imagegen-gallery-grid .thumb .ring { position: absolute; left: 6px; bottom: 6px; min-width: 24px; padding: 2px 7px; border-radius: 999px; background: rgba(0,0,0,0.62); color: #fff; font-size: 11px; font-weight: 600; backdrop-filter: blur(4px); }
    .imagegen-gallery-grid .thumb .del { position: absolute; top: 6px; right: 6px; width: 26px; height: 26px; border-radius: 8px; background: rgba(0,0,0,0.55); color: #fff; border: none; display: none; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; backdrop-filter: blur(4px); transition: background .2s; }
    .imagegen-gallery-grid .thumb .del:hover { background: rgba(180,40,40,0.85); }
    .imagegen-gallery-grid .thumb:hover .del { display: flex; }
    .imagegen-mini-gallery { display: flex; gap: 10px; overflow-x: auto; padding: 6px 0; }
    .imagegen-mini-gallery .thumb { width: 88px; height: 88px; flex-shrink: 0; border-radius: 10px; overflow: hidden; border: 2px solid transparent; cursor: pointer; background: var(--bg); transition: transform .15s; }
    .imagegen-mini-gallery .thumb:hover { transform: translateY(-2px); }
    .imagegen-mini-gallery .thumb img { width: 100%; height: 100%; object-fit: cover; }
    .imagegen-mini-gallery .thumb.active { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(16,172,235,0.18); }
    .imagegen-error { color: var(--red); font-size: 13px; padding: 10px 14px; background: rgba(180,40,40,0.08); border-radius: 10px; border: 1px solid rgba(180,40,40,0.15); }
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
    </style>
</head>
<body>
  <div class="orb-field" aria-hidden="true">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="brand-row">
          <h1>CypherTempre</h1>
          <div class="brand-actions">
            <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle theme" title="Toggle theme">
            <svg id="theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            <svg id="theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
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
        <p>Local LLM chat with PoQ-gated memory.</p>
      </div>

      <div class="rail-section">
        <div class="nav" aria-label="Main view">
          <button id="nav-chat" class="active" type="button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            Chat
          </button>
          <button id="nav-guide" type="button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            Guide
          </button>
          <button id="nav-marketplace" type="button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
            Marketplace
          </button>
          <button id="nav-imagegen" type="button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            ImageGen
          </button>
          <button id="nav-settings" type="button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 5 15.4a1.65 1.65 0 0 0-1.51 1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 5 10.6a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 5.4a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Settings
          </button>
        </div>

        <div class="group">
          <label for="persona">Persona</label>
          <select id="persona"></select>
          <div class="hint" id="persona-lock-hint"></div>
        </div>

        <div class="group">
          <label for="domain">Memory domain</label>
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

        <div class="group">
          <label for="session-list">Sessions</label>
          <select id="session-list"></select>
          <div class="inline-field">
            <input id="session-name" placeholder="New session name">
            <button id="new-session" class="secondary" type="button">New</button>
          </div>
          <div class="hint">Each session has its own local Timechain memory.</div>
        </div>
      </div>

      <div class="status-card" id="setup-status">Checking configuration...</div>
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
          <span class="badge info" id="model-badge">venice-uncensored</span>
          <span class="badge" id="rings-badge">rings: -</span>
          <span class="badge" id="verify-badge">verify: -</span>
        </div>
        <button id="inspector-toggle" class="mobile-only settings-icon" type="button" aria-label="Memory">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
        </button>
      </div>

      <section id="messages" class="messages" aria-live="polite">
        <div class="empty" id="empty-state">
          <h2>Start a remembered conversation.</h2>
          <p>Responses come from the configured LLM provider, then CypherTempre scores them through PoQ before sealing accepted rings.</p>
        </div>
      </section>

      <div class="composer">
        <div class="composer-warning" id="composer-warning">
          <strong>CT OpenClaw Runtime consumes many tokens.</strong>
          <span id="composer-warning-detail">
            Paid or higher-context models can run it with this warning. Free models are blocked for this persona.
          </span>
        </div>
        <div class="composer-options" style="max-width:1020px;margin:0 auto 8px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
          <label style="display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);cursor:pointer;">
            <input type="checkbox" id="shared-memory-toggle" style="width:16px;height:16px;">
            Use shared memory
          </label>
        </div>
        <form id="composer-form" class="composer-form">
          <textarea id="message" placeholder="Ask anything..." required enterkeyhint="send"></textarea>
          <button id="send" class="send" type="submit" aria-label="Send">→</button>
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
          <p class="simple-only">A neat map of what each part of the CypherTempre chat interface does.</p>
          <p class="comprehensive-only hidden">This page explains the full local loop: persona selection, LLM generation, Timechain recall, PoQ gating, memory sealing, visible conversation restoration, and chain verification.</p>
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
              <p>Personas provide the system prompt and default memory domain for the request. Custom personas are saved in the local PoC workspace and mirrored in your browser.</p>
              <ul>
                <li>Companion is general conversational help.</li>
                <li>Architect focuses on design tradeoffs.</li>
                <li>Socratic Tutor asks sharper learning questions.</li>
                <li>Memory Critic audits weak or contradictory memory.</li>
                <li>CypherTempre Researcher focuses on the PoC itself.</li>
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
              <p>The server loads `cyphertempre-chat-poc/.env.local` on startup.</p>
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
                <li>Accepted conversation rings live in `cyphertempre-chat-poc/.timechain/chain.jsonl`.</li>
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
              <p>Each session stores its Timechain in a separate workspace under the PoC sessions folder.</p>
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
              <p>The reset button deletes the PoC workspace `.timechain` directory and immediately creates a new chain.</p>
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
          <div class="imagegen-header">
            <div>
              <h2>ImageGen Studio</h2>
              <p>Generate, edit, and redefine images with your configured provider.</p>
            </div>
            <div class="imagegen-modes">
              <button id="imagegen-mode-generate" class="active" type="button">Generate</button>
              <button id="imagegen-mode-edit" type="button">Edit</button>
              <button id="imagegen-mode-redefine" type="button">Redefine</button>
            </div>
          </div>

          <div id="imagegen-panel-generate" class="imagegen-panel">
            <div class="imagegen-card">
              <div class="imagegen-prompt-wrap">
                <textarea id="imagegen-prompt" placeholder="Describe the image you want to create in detail..."></textarea>
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
              <div id="imagegen-status" class="imagegen-status"></div>
              <div id="imagegen-result" class="imagegen-result"></div>
              <div id="imagegen-lineage" class="imagegen-lineage hidden"></div>
            </div>
          </div>

          <div id="imagegen-panel-edit" class="imagegen-panel hidden">
            <div class="imagegen-card">
              <div class="imagegen-dropzone" id="imagegen-edit-dropzone">
                <input type="file" id="imagegen-edit-file" accept="image/*">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                <p>Drop an image here, or click to browse</p>
                <div class="hint">Supports PNG, JPG, WEBP</div>
              </div>
              <img id="imagegen-edit-preview" class="imagegen-preview hidden" alt="Edit preview">
              <div class="imagegen-prompt-wrap">
                <textarea id="imagegen-edit-prompt" placeholder="Describe what changes to make..."></textarea>
              </div>
              <div class="imagegen-controls">
                <select id="imagegen-edit-model">
                  <option value="google/gemini-2.5-flash-image-preview">Gemini Flash Image (Edit)</option>
                </select>
                <button id="imagegen-edit-btn" class="primary" type="button">Apply Edit</button>
              </div>
              <div id="imagegen-edit-result" class="imagegen-result"></div>
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
              <div id="imagegen-redefine-result" class="imagegen-result"></div>
            </div>
          </div>
        </div>

        <aside class="imagegen-sidebar">
          <div class="imagegen-sidebar-head">
            <h3>Gallery</h3>
            <span class="count" id="imagegen-gallery-count">0</span>
          </div>
          <div id="imagegen-gallery-grid" class="imagegen-gallery-grid"></div>
        </aside>
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
          <div class="settings-row">
            <div class="settings-field">
              <label for="provider">Provider</label>
              <select id="provider">
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
              <input id="model" value="venice-uncensored">
              <div class="hint" id="model-hint">Morpheus default: venice-uncensored.</div>
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

          <div class="settings-status-panel" id="settings-status">
            <div class="status-header">
              <span class="status-indicator" id="status-dot"></span>
              <span class="status-label" id="status-label">Checking configuration...</span>
            </div>
            <div class="status-detail" id="status-detail"></div>
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
        <strong>Memory Inspector</strong>
        <span>Recall, verify, and inspect the local chain.</span>
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
      <button id="mob-settings" type="button">Settings</button>
    </nav>
  </div>
  <div id="overlay-backdrop" class="overlay-backdrop"></div>

  <!-- Auth Overlay -->
  <div class="auth-overlay hidden" id="auth-overlay">
    <div class="auth-card">
      <div class="auth-logo">C</div>
      <h2>CypherTempre</h2>
      <p class="subtitle">Persona-powered conversations</p>
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

  <script>
    const els = {
{ui_js}  </script>
</body>
</html>
"""
