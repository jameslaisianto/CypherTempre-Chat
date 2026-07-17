"""Inline JavaScript SPA for Forge — CypherTempre PoC host UI."""

UI_JS = r"""      apiKey: document.getElementById('api-key'),
      model: document.getElementById('model'),
      persona: document.getElementById('persona'),
      domain: document.getElementById('domain'),
      setup: document.getElementById('setup-status'),
      title: document.getElementById('active-title'),
      workspace: document.getElementById('workspace-line'),
      modelBadge: document.getElementById('model-badge'),
      ringsBadge: document.getElementById('rings-badge'),
      verifyBadge: document.getElementById('verify-badge'),
      trustStrip: document.getElementById('trust-strip'),
      trustSkill: document.getElementById('trust-skill'),
      trustVerify: document.getElementById('trust-verify'),
      trustRings: document.getElementById('trust-rings'),
      trustSeal: document.getElementById('trust-seal'),
      trustProduct: document.getElementById('trust-product'),
      streamRepliesToggle: document.getElementById('stream-replies-toggle'),
      identityBridgeToggle: document.getElementById('identity-bridge-toggle'),
      memoryAutopilot: document.getElementById('memory-autopilot'),
      applyRecommendedDefaults: document.getElementById('apply-recommended-defaults'),
      exportBackup: document.getElementById('export-backup'),
      restoreBackup: document.getElementById('restore-backup'),
      projectObjective: document.getElementById('project-objective'),
      makeProjectSession: document.getElementById('make-project-session'),
      makeChatSession: document.getElementById('make-chat-session'),
      commandPalette: document.getElementById('command-palette'),
      commandPaletteInput: document.getElementById('command-palette-input'),
      commandPaletteList: document.getElementById('command-palette-list'),
      messages: document.getElementById('messages'),
      empty: document.getElementById('empty-state'),
      form: document.getElementById('composer-form'),
      message: document.getElementById('message'),
      send: document.getElementById('send'),
      summary: document.getElementById('summary'),
      ringTimeline: document.getElementById('ring-timeline'),
      cambiumResults: document.getElementById('cambium-results'),
      refreshWorkbench: document.getElementById('refresh-workbench'),
      copySyncSnapshot: document.getElementById('copy-sync-snapshot'),
      dreamDomains: document.getElementById('dream-domains'),
      dreamCycles: document.getElementById('dream-cycles'),
      runDream: document.getElementById('run-dream'),
      overlayTag: document.getElementById('overlay-tag'),
      overlayWeight: document.getElementById('overlay-weight'),
      saveOverlay: document.getElementById('save-overlay'),
      overlayList: document.getElementById('overlay-list'),
      runMemorySync: document.getElementById('run-memory-sync'),
      fleetSource: document.getElementById('fleet-source'),
      fleetRingJson: document.getElementById('fleet-ring-json'),
      runFleetImport: document.getElementById('run-fleet-import'),
      challengeIndices: document.getElementById('challenge-indices'),
      challengeNonce: document.getElementById('challenge-nonce'),
      runChallenge: document.getElementById('run-challenge'),
      sharedMemoryToggle: document.getElementById('shared-memory-toggle'),
      sharedMemoryQuery: document.getElementById('shared-memory-query'),
      searchSharedMemory: document.getElementById('search-shared-memory'),
      sharedMemoryResults: document.getElementById('shared-memory-results'),
      importSharedMemory: document.getElementById('import-shared-memory'),
      synthesizeSharedMemory: document.getElementById('synthesize-shared-memory'),
      advancedTimechainResults: document.getElementById('advanced-timechain-results'),
      pendingMemories: document.getElementById('pending-memories'),
      acceptedMemories: document.getElementById('accepted-memories'),
      recallForm: document.getElementById('recall-form'),
      recallQuery: document.getElementById('recall-query'),
      recallResults: document.getElementById('recall-results'),
      verify: document.getElementById('verify'),
      verifyResult: document.getElementById('verify-result'),
      resetChain: document.getElementById('reset-chain'),
      navChat: document.getElementById('nav-chat'),
      navGuide: document.getElementById('nav-guide'),
      navSettings: document.getElementById('nav-settings'),
      chatView: document.getElementById('chat-view'),
      guideView: document.getElementById('guide-view'),
      settingsView: document.getElementById('settings-view'),
      settingsProviderTab: document.getElementById('settings-provider-tab'),
      settingsPersonaTab: document.getElementById('settings-persona-tab'),
      settingsManageTab: document.getElementById('settings-manage-tab'),
      settingsWorkbenchTab: document.getElementById('settings-workbench-tab'),
      providerSettingsSection: document.getElementById('provider-settings-section'),
      personaSettingsSection: document.getElementById('persona-settings-section'),
      manageSettingsSection: document.getElementById('manage-settings-section'),
      workbenchSettingsSection: document.getElementById('workbench-settings-section'),
      settingsStatus: document.getElementById('settings-status'),
      provider: document.getElementById('provider'),
      modelHint: document.getElementById('model-hint'),
      chatModelOptions: document.getElementById('chat-model-options'),

      // Separate providers for creative modalities
      imageProvider: document.getElementById('image-provider'),
      imageModel: document.getElementById('image-model'),
      imageApiKey: document.getElementById('image-api-key'),
      imageBaseUrl: document.getElementById('image-base-url'),
      videoProvider: document.getElementById('video-provider'),
      videoModel: document.getElementById('video-model'),
      videoApiKey: document.getElementById('video-api-key'),
      videoBaseUrl: document.getElementById('video-base-url'),
      audioProvider: document.getElementById('audio-provider'),
      audioModel: document.getElementById('audio-model'),
      audioModelOptions: document.getElementById('audio-model-options'),
      audioApiKey: document.getElementById('audio-api-key'),
      audioBaseUrl: document.getElementById('audio-base-url'),
      audioTestProvider: document.getElementById('audio-test-provider'),
      statusDot: document.getElementById('status-dot'),
      statusLabel: document.getElementById('status-label'),
      statusDetail: document.getElementById('status-detail'),
      baseUrl: document.getElementById('base-url'),
      baseUrlField: document.getElementById('base-url-field'),
      guideTopicGrid: document.getElementById('guide-topic-grid'),
      guideSimple: document.getElementById('guide-simple'),
      guideComprehensive: document.getElementById('guide-comprehensive'),
      personaName: document.getElementById('persona-name'),
      personaSeed: document.getElementById('persona-seed'),
      personaLockHint: document.getElementById('persona-lock-hint'),
      generatePersona: document.getElementById('generate-persona'),
      testProvider: document.getElementById('test-provider'),
      clearProviderOverride: document.getElementById('clear-provider-override'),
      manageStatusDot: document.getElementById('manage-status-dot'),
      manageStatusLabel: document.getElementById('manage-status-label'),
      manageStatusDetail: document.getElementById('manage-status-detail'),
      manageFreeze: document.getElementById('manage-freeze'),
      manageRingSelect: document.getElementById('manage-ring-select'),
      manageRewind: document.getElementById('manage-rewind'),
      manageSessionSelect: document.getElementById('manage-session-select'),
      manageSessionName: document.getElementById('manage-session-name'),
      manageRenameSession: document.getElementById('manage-rename-session'),
      manageDeleteSession: document.getElementById('manage-delete-session'),
      managePersonaSelect: document.getElementById('manage-persona-select'),
      managePersonaName: document.getElementById('manage-persona-name'),
      managePersonaSystem: document.getElementById('manage-persona-system'),
      managePersonaDomain: document.getElementById('manage-persona-domain'),
      managePersonaVisibility: document.getElementById('manage-persona-visibility'),
      manageSavePersona: document.getElementById('manage-save-persona'),
      manageDeletePersona: document.getElementById('manage-delete-persona'),
      sessionList: document.getElementById('session-list'),
      sessionChips: document.getElementById('session-chips'),
      sessionsCount: document.getElementById('sessions-count'),
      sessionName: document.getElementById('session-name'),
      newSession: document.getElementById('new-session'),
      railCollapse: document.getElementById('rail-collapse'),
      composerWarning: document.getElementById('composer-warning'),
      mobChat: document.getElementById('mob-chat'),
      mobGuide: document.getElementById('mob-guide'),
      mobSettings: document.getElementById('mob-settings'),
      themeToggle: document.getElementById('theme-toggle'),
      themeIconMoon: document.getElementById('theme-icon-moon'),
      themeIconSun: document.getElementById('theme-icon-sun'),
      densityToggle: document.getElementById('density-toggle'),
      authOverlay: document.getElementById('auth-overlay'),
      authTabLogin: document.getElementById('auth-tab-login'),
      authTabRegister: document.getElementById('auth-tab-register'),
      authLoginForm: document.getElementById('auth-login-form'),
      authRegisterForm: document.getElementById('auth-register-form'),
      authLoginUser: document.getElementById('auth-login-user'),
      authLoginPass: document.getElementById('auth-login-pass'),
      authLoginBtn: document.getElementById('auth-login-btn'),
      authRegUser: document.getElementById('auth-reg-user'),
      authRegDisplay: document.getElementById('auth-reg-display'),
      authRegPass: document.getElementById('auth-reg-pass'),
      authRegisterBtn: document.getElementById('auth-register-btn'),
      authMessage: document.getElementById('auth-message'),
      accountWrap: document.getElementById('account-wrap'),
      accountBtn: document.getElementById('account-btn'),
      accountName: document.getElementById('account-name'),
      accountMenu: document.getElementById('account-menu'),
      accountRole: document.getElementById('account-role'),
      accountLogout: document.getElementById('account-logout'),
      navMarketplace: document.getElementById('nav-marketplace'),
      marketplaceView: document.getElementById('marketplace-view'),
      mpSearch: document.getElementById('mp-search'),
      marketplaceGrid: document.getElementById('marketplace-grid'),
      detailDrawer: document.getElementById('detail-drawer'),
      detailClose: document.getElementById('detail-close'),
      detailName: document.getElementById('detail-name'),
      detailDomain: document.getElementById('detail-domain'),
      detailDomainText: document.getElementById('detail-domain-text'),
      detailTagline: document.getElementById('detail-tagline'),
      detailMassValue: document.getElementById('detail-mass-value'),
      detailMassBar: document.getElementById('detail-mass-bar'),
      detailCapsule: document.getElementById('detail-capsule'),
      detailSubscribe: document.getElementById('detail-subscribe'),
      detailUnsubscribe: document.getElementById('detail-unsubscribe'),
      detailSubHint: document.getElementById('detail-sub-hint'),
      mobMarketplace: document.getElementById('mob-marketplace'),
      navImagegen: document.getElementById('nav-imagegen'),
      mobImagegen: document.getElementById('mob-imagegen'),
      imagegenView: document.getElementById('imagegen-view'),
      imagegenModeGenerate: document.getElementById('imagegen-mode-generate'),
      imagegenModeEdit: document.getElementById('imagegen-mode-edit'),
      imagegenModeRedefine: document.getElementById('imagegen-mode-redefine'),
      imagegenPanelGenerate: document.getElementById('imagegen-panel-generate'),
      imagegenPanelEdit: document.getElementById('imagegen-panel-edit'),
      imagegenPanelRedefine: document.getElementById('imagegen-panel-redefine'),
      imagegenPrompt: document.getElementById('imagegen-prompt'),
      imagegenModel: document.getElementById('imagegen-model'),
      imagegenAspect: document.getElementById('imagegen-aspect'),
      imagegenGenerateBtn: document.getElementById('imagegen-generate-btn'),
      imagegenBypassGenerate: document.getElementById('imagegen-bypass-generate'),
      imagegenBypassEdit: document.getElementById('imagegen-bypass-edit'),
      imagegenBypassRedefine: document.getElementById('imagegen-bypass-redefine'),
      imagegenStatus: document.getElementById('imagegen-status'),
      imagegenResult: document.getElementById('imagegen-result'),
      imagegenLineage: document.getElementById('imagegen-lineage'),
      imagegenEditDropzone: document.getElementById('imagegen-edit-dropzone'),
      imagegenEditFile: document.getElementById('imagegen-edit-file'),
      imagegenEditPreview: document.getElementById('imagegen-edit-preview'),
      imagegenEditPrompt: document.getElementById('imagegen-edit-prompt'),
      imagegenEditBtn: document.getElementById('imagegen-edit-btn'),
      imagegenEditResult: document.getElementById('imagegen-edit-result'),
      imagegenEditAspect: document.getElementById('imagegen-edit-aspect'),
      imagegenSourceStage: document.getElementById('imagegen-source-stage'),
      imagegenReplaceSource: document.getElementById('imagegen-replace-source'),
      imagegenRedefineGallery: document.getElementById('imagegen-redefine-gallery'),
      imagegenRedefinePrompt: document.getElementById('imagegen-redefine-prompt'),
      imagegenRedefineBtn: document.getElementById('imagegen-redefine-btn'),
      imagegenRedefineResult: document.getElementById('imagegen-redefine-result'),
      imagegenGalleryGrid: document.getElementById('imagegen-gallery-grid'),
      imagegenGalleryCount: document.getElementById('imagegen-gallery-count'),
      imagegenEditModel: document.getElementById('imagegen-edit-model'),
      imagegenLightbox: document.getElementById('imagegen-lightbox'),
      imagegenLightboxImage: document.getElementById('imagegen-lightbox-image'),
      imagegenLightboxClose: document.getElementById('imagegen-lightbox-close'),

      // CineTempre VideoGen (2026 Director's Cut)
      navVideogen: document.getElementById('nav-videogen'),
      mobVideogen: document.getElementById('mob-videogen'),
      videogenView: document.getElementById('videogen-view'),
      navAudiogen: document.getElementById('nav-audiogen'),
      audiogenView: document.getElementById('audiogen-view'),
      audiogenText: document.getElementById('audiogen-text'),
      audiogenVoice: document.getElementById('audiogen-voice'),
      audiogenFormat: document.getElementById('audiogen-format'),
      audiogenSpeed: document.getElementById('audiogen-speed'),
      audiogenSpeedLabel: document.getElementById('audiogen-speed-label'),
      audiogenGenerateBtn: document.getElementById('audiogen-generate-btn'),
      audiogenStatus: document.getElementById('audiogen-status'),
      audiogenResult: document.getElementById('audiogen-result'),
      videogenModeText: document.getElementById('videogen-mode-text2video'),
      videogenModeImg: document.getElementById('videogen-mode-img2vid'),
      videogenModeRemix: document.getElementById('videogen-mode-remix'),
      videogenPanelText: document.getElementById('videogen-panel-text2video'),
      videogenPanelImg: document.getElementById('videogen-panel-img2vid'),
      videogenPanelRemix: document.getElementById('videogen-panel-remix'),
      videogenPrompt: document.getElementById('videogen-prompt'),
      videogenAspect: document.getElementById('videogen-aspect'),
      videogenRes: document.getElementById('videogen-res'),
      videogenMotion: document.getElementById('videogen-motion'),
      videogenRenderBtn: document.getElementById('videogen-render-btn'),
      videogenStatus: document.getElementById('videogen-status'),
      videogenResult: document.getElementById('videogen-result'),
      videogenLineage: document.getElementById('videogen-lineage'),
      videogenLexicon: document.getElementById('videogen-lexicon'),
      videogenImgDrop: document.getElementById('videogen-img-drop'),
      videogenImgFile: document.getElementById('videogen-img-file'),
      videogenImgPreview: document.getElementById('videogen-img-preview'),
      videogenImgPrompt: document.getElementById('videogen-img-prompt'),
      videogenImgBtn: document.getElementById('videogen-img-btn'),
      videogenImgResult: document.getElementById('videogen-img-result'),
      videogenRemixGallery: document.getElementById('videogen-remix-gallery'),
      videogenRemixPrompt: document.getElementById('videogen-remix-prompt'),
      videogenRemixBtn: document.getElementById('videogen-remix-btn'),
      videogenRemixResult: document.getElementById('videogen-remix-result'),
      videogenGallery: document.getElementById('videogen-gallery'),
      videogenCount: document.getElementById('videogen-count'),
      videogenModel: document.getElementById('videogen-model'),
      videogenImgModel: document.getElementById('videogen-img-model'),
      settingsCreatorTab: document.getElementById('settings-creator-tab'),
      creatorSettingsSection: document.getElementById('creator-settings-section'),
      creatorName: document.getElementById('creator-name'),
      creatorTagline: document.getElementById('creator-tagline'),
      creatorDomain: document.getElementById('creator-domain'),
      creatorSourceSession: document.getElementById('creator-source-session'),
      creatorSystem: document.getElementById('creator-system'),
      creatorPriceModel: document.getElementById('creator-price-model'),
      creatorPriceAmount: document.getElementById('creator-price-amount'),
      creatorSave: document.getElementById('creator-save'),
      creatorList: document.getElementById('creator-list')
    };

    let personas = {};
    let customPersonas = {};
    let creatorPersonas = {};
    let publicPersonas = {};
    let marketplacePersonas = {};
    let activeSession = localStorage.getItem('ct_active_session') || 'default';
    let sessionPersonaLocks = {};
    let sessionRows = [];
    let ringRows = [];
    let currentFrozen = false;
    let isSending = false;
    let currentUser = null;
    let marketplaceData = [];
    let currentDetailId = null;
    let configPersistTimer = null;
    const discoveredModelProviders = new Set();
    const providerEndpoints = {
      surplusintelligence: 'https://api.surplusintelligence.ai/v1',
      morpheus: 'https://api.mor.org/api/v1/chat/completions',
      openrouter: 'https://openrouter.ai/api/v1/chat/completions',
      'kimi-code': 'https://api.kimi.com/coding/v1/chat/completions',
      kimi: 'https://api.moonshot.ai/v1/chat/completions',
      other: ''
    };

    // Per-provider model catalogs. Seeded with curated defaults; /api/models discovery replaces when available.
    const chatProviderDefaults = {
      surplusintelligence: '',
      morpheus: 'gemma-4-uncensored',
      openrouter: 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
      kimi: 'kimi-k2.6',
      'kimi-code': 'kimi-for-coding',
      other: ''
    };
    const chatModelsByProvider = {
      surplusintelligence: [],
      morpheus: ['gemma-4-uncensored', 'llama-3.3-70b', 'qwen3-32b', 'mistral-small-3.1-24b'],
      openrouter: [
        'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
        'openrouter/auto',
        'anthropic/claude-sonnet-4',
        'openai/gpt-4.1-mini',
        'google/gemini-2.5-flash',
        'meta-llama/llama-3.3-70b-instruct',
        'qwen/qwen3-32b',
        'mistralai/mistral-small-3.1-24b-instruct',
      ],
      kimi: ['kimi-k2.6', 'moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
      'kimi-code': ['kimi-for-coding'],
      other: []
    };
    const chatDiscoverable = new Set(['surplusintelligence', 'morpheus', 'openrouter', 'kimi', 'kimi-code']);

    const imageProviderDefaults = {
      surplusintelligence: '',
      openrouter: 'black-forest-labs/flux.2-pro',
      morpheus: 'grok-imagine-image',
      other: ''
    };

    const imageEditProviderDefaults = {
      // Default uncensored Surplus edit model — exact user prompt, no policy filter.
      surplusintelligence: 'qwen-edit-uncensored',
      openrouter: 'google/gemini-2.5-flash-image-preview',
      morpheus: 'nano-banana-2',
      other: ''
    };

    const videoProviderDefaults = {
      surplusintelligence: '',
      openrouter: 'black-forest-labs/flux-video-pro',
      morpheus: 'grok-video-2026',
      demo: 'demo-cinematic',
      other: ''
    };

    const audioProviderDefaults = {
      surplusintelligence: '',
      morpheus: 'tts-kokoro',
      openrouter: 'openrouter-audio',
      other: ''
    };

    // Curated model lists for Image / Video / Audio (used to populate the selects)
    const imageModelsByProvider = {
      surplusintelligence: [],
      openrouter: [
        'black-forest-labs/flux.2-pro',
        'google/gemini-2.5-flash-image-preview',
        'sourceful/riverflow-v2-pro'
      ],
      morpheus: [
        'grok-imagine-image',
        'nano-banana-2',
        'lustify-v8'
      ],
      other: []
    };

    const imageEditModelsByProvider = {
      // Seed known Surplus /v1/images/edits models (uncensored first). Discovery replaces when available.
      surplusintelligence: [
        'qwen-edit-uncensored',
        'qwen-image-2-edit',
        'qwen-image-2-pro-edit',
        'grok-imagine-edit',
        'grok-imagine-quality-edit',
        'flux-2-max-edit',
        'gpt-image-2-edit',
        'gpt-image-1-5-edit',
        'seedream-v4-edit',
        'seedream-v5-lite-edit',
        'firered-image-edit',
        'wan-2-7-pro-edit',
        'nano-banana-2-edit',
        'nano-banana-pro-edit',
        'nano-banana-2-lite-edit',
        'luma-uni-1-edit',
        'luma-uni-1-max-edit'
      ],
      openrouter: [
        'google/gemini-2.5-flash-image-preview',
        'google/gemini-2.5-flash-image',
        'sourceful/riverflow-v2-pro'
      ],
      morpheus: [
        'nano-banana-2',
        'grok-imagine-image'
      ],
      other: []
    };

    const videoModelsByProvider = {
      surplusintelligence: [],
      openrouter: [
        'black-forest-labs/flux-video-pro'
      ],
      morpheus: [
        'grok-video-2026'
      ],
      demo: [
        'demo-cinematic'
      ],
      other: []
    };

    const audioModelsByProvider = {
      surplusintelligence: [],
      morpheus: ['tts-kokoro'],
      openrouter: ['openrouter-audio'],
      other: []
    };

    function applyProviderCatalogs(catalogs) {
      if (!catalogs || typeof catalogs !== 'object') return;
      const applyModality = (bucket, modelsMap, defaultsMap, discoverSet) => {
        const table = catalogs[bucket];
        if (!table || typeof table !== 'object') return;
        Object.entries(table).forEach(([provider, cfg]) => {
          if (!cfg || typeof cfg !== 'object') return;
          if (Array.isArray(cfg.models)) modelsMap[provider] = cfg.models.slice();
          if (cfg.default_model !== undefined) defaultsMap[provider] = cfg.default_model || '';
          if (discoverSet) {
            if (cfg.discover) discoverSet.add(provider);
            else discoverSet.delete(provider);
          }
        });
      };
      applyModality('chat', chatModelsByProvider, chatProviderDefaults, chatDiscoverable);
      applyModality('image', imageModelsByProvider, imageProviderDefaults, null);
      applyModality('video', videoModelsByProvider, videoProviderDefaults, null);
      applyModality('audio', audioModelsByProvider, audioProviderDefaults, null);
    }

    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    function setSelectValue(selectEl, value) {
      if (!selectEl) return;
      const next = String(value ?? '').trim();
      if (!next) return;
      const hasOption = Array.from(selectEl.options || []).some(opt => String(opt.value) === next);
      if (!hasOption) {
        const opt = document.createElement('option');
        opt.value = next;
        opt.textContent = next;
        selectEl.appendChild(opt);
      }
      selectEl.value = next;
    }

    function providerDiscoveryCredentials(provider, modality = '') {
      const prov = String(provider || '').trim();
      const mode = String(modality || '').trim().toLowerCase();
      const chatKey = localStorage.getItem('ct_api_key') || '';
      const chatBase = localStorage.getItem('ct_base_url') || els.baseUrl?.value?.trim() || '';
      if (mode === 'image') {
        return {
          apiKey: localStorage.getItem('ct_image_api_key') || chatKey,
          baseUrl: localStorage.getItem('ct_image_base_url') || '',
        };
      }
      if (mode === 'video') {
        return {
          apiKey: localStorage.getItem('ct_video_api_key') || chatKey,
          baseUrl: localStorage.getItem('ct_video_base_url') || '',
        };
      }
      if (mode === 'audio') {
        return {
          apiKey: localStorage.getItem('ct_audio_api_key') || chatKey,
          baseUrl: localStorage.getItem('ct_audio_base_url') || '',
        };
      }
      return { apiKey: chatKey, baseUrl: chatBase };
    }

    function syncCreativeStudioModelsFromSettings() {
      const imageModel = els.imageModel?.value?.trim() || localStorage.getItem('ct_image_model') || '';
      const imageEditModel = localStorage.getItem('ct_image_edit_model') || '';
      const videoModel = els.videoModel?.value?.trim() || '';
      const imageProv = els.imageProvider?.value || localStorage.getItem('ct_image_provider') || '';
      const editList = imageEditModelsByProvider[imageProv] || [];

      if (imageModel) {
        setSelectValue(els.imagegenModel, imageModel);
      }
      if (imageEditModel) {
        setSelectValue(els.imagegenEditModel, imageEditModel);
      } else if (imageModel && editList.includes(imageModel)) {
        setSelectValue(els.imagegenEditModel, imageModel);
      }
      if (videoModel) {
        setSelectValue(els.videogenModel, videoModel);
        setSelectValue(els.videogenImgModel, videoModel);
      }
    }

    function renderContent(content) {
      const text = String(content ?? '');
      const parts = [];
      const pattern = /\*([^*\n][\s\S]*?[^*\n]|\S)\*/g;
      let lastIndex = 0;
      let match;
      while ((match = pattern.exec(text)) !== null) {
        if (match.index > lastIndex) {
          parts.push({ type: 'text', value: text.slice(lastIndex, match.index) });
        }
        parts.push({ type: 'thought', value: match[1] });
        lastIndex = pattern.lastIndex;
      }
      if (lastIndex < text.length) {
        parts.push({ type: 'text', value: text.slice(lastIndex) });
      }
      if (!parts.length) parts.push({ type: 'text', value: text });
      return parts
        .filter(part => part.value.length > 0)
        .map(part => `<span class="${part.type === 'thought' ? 'thought-segment' : 'text-segment'}">${esc(part.value)}</span>`)
        .join('');
    }

    function applyTheme(isLight) {
      document.documentElement.classList.toggle('light', isLight);
      document.body.classList.toggle('light', isLight);
      document.documentElement.style.colorScheme = isLight ? 'light' : 'dark';
      updateThemeIcon(isLight);
      const metaTheme = document.querySelector('meta[name="theme-color"]');
      if (metaTheme) metaTheme.content = isLight ? '#faf6f3' : '#0a0706';
    }

    function initTheme() {
      // Dark-first product: only light when user explicitly chose it.
      const saved = localStorage.getItem('ct_theme');
      const isLight = saved === 'light';
      applyTheme(isLight);
    }

    function toggleTheme() {
      const isLight = !document.documentElement.classList.contains('light');
      localStorage.setItem('ct_theme', isLight ? 'light' : 'dark');
      applyTheme(isLight);
    }

    function updateThemeIcon(isLight) {
      if (els.themeIconMoon) els.themeIconMoon.style.display = isLight ? 'none' : 'block';
      if (els.themeIconSun) els.themeIconSun.style.display = isLight ? 'block' : 'none';
      if (els.themeToggle) {
        els.themeToggle.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
        els.themeToggle.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
        els.themeToggle.setAttribute('aria-pressed', isLight ? 'true' : 'false');
      }
    }

    function initDensity() {
      const compact = localStorage.getItem('ct_density') === 'compact';
      document.documentElement.classList.toggle('density-compact', compact);
      updateDensityToggle(compact);
    }

    function toggleDensity() {
      const compact = document.documentElement.classList.toggle('density-compact');
      localStorage.setItem('ct_density', compact ? 'compact' : 'comfortable');
      updateDensityToggle(compact);
    }

    function updateDensityToggle(compact) {
      if (!els.densityToggle) return;
      els.densityToggle.classList.toggle('active', compact);
      els.densityToggle.setAttribute('aria-pressed', compact ? 'true' : 'false');
      els.densityToggle.title = compact ? 'Comfortable density' : 'Compact density';
      els.densityToggle.setAttribute('aria-label', compact ? 'Switch to comfortable density' : 'Switch to compact density');
    }

    function setRailCollapsed(collapsed) {
      document.documentElement.classList.toggle('rail-collapsed', !!collapsed);
      // Also stamp data attr for CSS debugging / future hooks
      document.documentElement.dataset.rail = collapsed ? 'collapsed' : 'expanded';
      localStorage.setItem('ct_rail_collapsed', collapsed ? 'true' : 'false');
      updateRailCollapse(!!collapsed);
    }

    function initRailCollapse() {
      const collapsed = localStorage.getItem('ct_rail_collapsed') === 'true';
      setRailCollapsed(collapsed);
    }

    function toggleRailCollapse() {
      const collapsed = !document.documentElement.classList.contains('rail-collapsed');
      setRailCollapsed(collapsed);
    }

    function updateRailCollapse(collapsed) {
      if (!els.railCollapse) return;
      els.railCollapse.classList.toggle('active', collapsed);
      els.railCollapse.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
      els.railCollapse.title = collapsed ? 'Expand sidebar' : 'Collapse sidebar';
      els.railCollapse.setAttribute('aria-label', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
    }

    function renderSessionChips() {
      if (!els.sessionChips) return;
      const sessions = sessionRows || [];
      if (els.sessionsCount) {
        els.sessionsCount.textContent = sessions.length ? `${sessions.length}` : '';
      }
      if (!sessions.length) {
        els.sessionChips.innerHTML = '<div class="hint" style="padding:6px 4px">No sessions yet.</div>';
        return;
      }
      els.sessionChips.innerHTML = sessions.map(session => {
        const active = session.id === activeSession;
        const rings = session.rings ?? 0;
        return `<button type="button" role="option" class="session-chip${active ? ' active' : ''}" data-session-id="${esc(session.id)}" aria-selected="${active ? 'true' : 'false'}" title="${esc(session.name)} · ${rings} rings"><span class="session-chip-name">${esc(session.name)}</span><span class="session-chip-meta">${rings}</span></button>`;
      }).join('');
    }

    function applyPromptPill(prompt) {
      if (!els.message || !prompt) return;
      els.message.value = prompt;
      els.message.focus();
      els.message.dispatchEvent(new Event('input', { bubbles: true }));
      // Place caret at end
      const len = els.message.value.length;
      try { els.message.setSelectionRange(len, len); } catch (_) {}
    }

    function emptyStateHtml() {
      return `
          <div class="empty" id="empty-state">
            <div class="empty-mark" aria-hidden="true">F</div>
            <h2>What should we remember together?</h2>
            <p>Forge is a PoC host for CypherTempre. Accepted replies seal into your local Timechain — verifiable memory that grows with you.</p>
            <div class="prompt-pills" id="prompt-pills" role="group" aria-label="Suggested prompts">
              <button type="button" class="prompt-pill" data-prompt="What do you already remember about how I like to work?">Recall my working style</button>
              <button type="button" class="prompt-pill" data-prompt="Summarize the key decisions sealed in this session's Timechain so far.">Summarize this chain</button>
              <button type="button" class="prompt-pill" data-prompt="Help me think through a design tradeoff carefully — surface assumptions, risks, and a recommended path.">Design tradeoff</button>
              <button type="button" class="prompt-pill" data-prompt="Verify your self-model: what are you confident about, uncertain about, and what would change your mind?">Honest self-check</button>
            </div>
            <div class="empty-hints" aria-hidden="true">
              <span>PoQ-gated</span>
              <span>Hash-linked memory</span>
              <span>Your chain, your keys</span>
            </div>
          </div>
        `;
    }

    let currentMainView = localStorage.getItem('ct_view') || 'chat';
    let viewTransitionToken = 0;

    function getViewElement(view) {
      if (view === 'forge') view = 'imagegen';
      if (view === 'chat') return els.chatView;
      if (view === 'guide') return els.guideView;
      if (view === 'settings') return els.settingsView;
      if (view === 'marketplace') return els.marketplaceView;
      if (view === 'imagegen') return els.imagegenView;
      if (view === 'videogen') return els.videogenView;
      if (view === 'audiogen') return els.audiogenView;
      return null;
    }

    function animateViewEnter(el) {
      if (!el) return;
      el.classList.remove('view-exit');
      el.classList.remove('view-enter');
      // Force reflow so re-adding the class restarts the animation
      void el.offsetWidth;
      el.classList.add('view-enter');
      const token = ++viewTransitionToken;
      window.setTimeout(() => {
        if (token === viewTransitionToken) el.classList.remove('view-enter');
      }, 420);
    }

    function initPanels() {
      const saved = localStorage.getItem('ct_panels');
      const expanded = saved ? JSON.parse(saved) : { self: true };
      document.querySelectorAll('.inspector-body .panel').forEach(panel => {
        const key = panel.dataset.panel;
        if (key && expanded[key]) panel.classList.add('expanded');
        else if (key && !expanded[key]) panel.classList.remove('expanded');
        const header = panel.querySelector('.panel-header');
        if (header) {
          header.addEventListener('click', () => {
            panel.classList.toggle('expanded');
            const state = {};
            document.querySelectorAll('.inspector-body .panel').forEach(p => {
              if (p.dataset.panel) state[p.dataset.panel] = p.classList.contains('expanded');
            });
            localStorage.setItem('ct_panels', JSON.stringify(state));
          });
        }
      });
    }

    function setSettingsSection(section) {
      const active = ['provider', 'persona', 'manage', 'workbench'].includes(section) ? section : 'provider';
      els.providerSettingsSection.classList.toggle('hidden', active !== 'provider');
      els.personaSettingsSection.classList.toggle('hidden', active !== 'persona');
      els.manageSettingsSection.classList.toggle('hidden', active !== 'manage');
      els.workbenchSettingsSection.classList.toggle('hidden', active !== 'workbench');
      els.settingsProviderTab.classList.toggle('active', active === 'provider');
      els.settingsPersonaTab.classList.toggle('active', active === 'persona');
      els.settingsManageTab.classList.toggle('active', active === 'manage');
      els.settingsWorkbenchTab.classList.toggle('active', active === 'workbench');
      localStorage.setItem('ct_settings_section', active);
    }

    function setGuideDepth(depth) {
      const comprehensive = depth === 'comprehensive';
      document.querySelectorAll('.simple-only').forEach(node => node.classList.toggle('hidden', comprehensive));
      document.querySelectorAll('.comprehensive-only').forEach(node => node.classList.toggle('hidden', !comprehensive));
      els.guideSimple.classList.toggle('active', !comprehensive);
      els.guideComprehensive.classList.toggle('active', comprehensive);
      localStorage.setItem('ct_guide_depth', depth);
    }

    function renderGuideTopics(topics) {
      els.guideTopicGrid.innerHTML = topics.map(topic => {
        const detailItems = String(topic.details || '')
          .split('\n')
          .map(line => line.trim())
          .filter(Boolean)
          .map(line => `<li>${esc(line)}</li>`)
          .join('');
        const sourceText = (topic.sources || []).join(', ');
        return `
          <article class="feature-card">
            <h3>${esc(topic.title)}</h3>
            <p class="simple-only">${esc(topic.summary)}</p>
            <div class="comprehensive-only hidden">
              <ul>${detailItems}</ul>
              <p class="hint">Sources: ${esc(sourceText)}</p>
            </div>
            <div class="feature-actions">
              <button class="secondary explain-guide-topic" type="button" data-topic-id="${esc(topic.id)}">Explain</button>
            </div>
          </article>
        `;
      }).join('');
      els.guideTopicGrid.querySelectorAll('.explain-guide-topic').forEach(button => {
        button.addEventListener('click', () => {
          explainGuideTopic(button.dataset.topicId).catch(error => setStatus(error.message, '#6b3c3c'));
        });
      });
      setGuideDepth(localStorage.getItem('ct_guide_depth') || 'simple');
    }

    async function loadGuideTopics() {
      const data = await api('/api/guide/topics');
      renderGuideTopics(data.topics || []);
    }

    async function explainGuideTopic(topicId) {
      saveLocalConfig();
      setStatus('Creating source-grounded guide explanation...');
      const data = await api('/api/guide/explain', {
        method: 'POST',
        body: JSON.stringify({
          topicId,
          model: els.model.value.trim(),
          apiKey: els.apiKey.value.trim(),
          provider: els.provider.value,
          baseUrl: els.baseUrl.value.trim()
        })
      });
      if (data.session?.id) {
        await switchSession(data.session.id);
      }
      setMainView('chat');
      setStatus(data.provider_error ? `Guide explanation used local fallback: ${data.provider_error}` : `Guide explanation created: ${data.topic?.title || topicId}.`, data.provider_error ? '#6b5730' : '#35674f');
    }

    async function api(path, options = {}, timeoutMs = 0) {
      const token = localStorage.getItem('ct_auth_token') || '';
      const controller = timeoutMs > 0 ? new AbortController() : null;
      const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
      try {
        const response = await fetch(path, {
          ...options,
          credentials: 'same-origin',
          signal: controller?.signal,
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'X-Auth-Token': token } : {}),
            ...(options.headers || {})
          }
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
        if (body.ok === false && body.error) throw new Error(body.error);
        return body;
      } catch (error) {
        if (error?.name === 'AbortError') {
          throw new Error(
            timeoutMs >= 60000
              ? 'Request timed out. Image edits can take several minutes — try Raw prompt mode or a smaller image.'
              : `Request timed out after ${Math.round(timeoutMs / 1000)}s.`
          );
        }
        if (error instanceof TypeError && /fetch/i.test(error.message || '')) {
          throw new Error(
            timeoutMs >= 60000
              ? 'Network error — connection dropped before the edit finished. Try Raw prompt mode or a smaller image.'
              : 'Network error — could not reach the server.'
          );
        }
        throw error;
      } finally {
        if (timer) clearTimeout(timer);
      }
    }

    const IMAGEGEN_EDIT_TIMEOUT_MS = 10 * 60 * 1000;
    let imagegenEditSourceId = '';

    function aspectRatioFromDimensions(width, height) {
      const w = Number(width) || 1;
      const h = Number(height) || 1;
      const r = w / h;
      if (Math.abs(r - 1) < 0.08) return '1:1';
      if (r >= 1.6) return '16:9';
      if (r >= 1.2) return '4:3';
      if (r <= 0.7) return '9:16';
      if (r < 1) return '9:16';
      return '4:3';
    }

    async function loadImageAsDataUrl(src) {
      if (!src) return '';
      if (src.startsWith('data:image')) return src;
      const response = await fetch(src, { credentials: 'same-origin' });
      if (!response.ok) throw new Error('Could not load the source image.');
      const blob = await response.blob();
      return await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error('Could not read the source image.'));
        reader.readAsDataURL(blob);
      });
    }

    async function compressImageForEdit(dataUrl, maxDim = 2048, quality = 0.92) {
      if (!dataUrl || !dataUrl.startsWith('data:image')) return dataUrl;
      try {
        const image = await new Promise((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(img);
          img.onerror = () => reject(new Error('Could not read the uploaded image.'));
          img.src = dataUrl;
        });
        if (els.imagegenEditAspect) {
          const detected = aspectRatioFromDimensions(image.width, image.height);
          if ([...els.imagegenEditAspect.options].some(opt => opt.value === detected)) {
            els.imagegenEditAspect.value = detected;
          }
        }
        const scale = Math.min(1, maxDim / Math.max(image.width, image.height));
        // Keep small images untouched for fidelity.
        if (scale === 1 && dataUrl.length < 1_500_000) return dataUrl;
        const width = Math.max(1, Math.round(image.width * scale));
        const height = Math.max(1, Math.round(image.height * scale));
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (!ctx) return dataUrl;
        ctx.drawImage(image, 0, 0, width, height);
        const preferPng = dataUrl.includes('image/png') && scale === 1;
        return canvas.toDataURL(preferPng ? 'image/png' : 'image/jpeg', quality);
      } catch {
        return dataUrl;
      }
    }

    async function useImageAsEditSource(src, { sourceId = '', alt = 'Edit source' } = {}) {
      if (!src) return;
      setImagegenMode('edit');
      const dataUrl = await loadImageAsDataUrl(src);
      const compressed = await compressImageForEdit(dataUrl);
      if (!els.imagegenEditPreview) return;
      els.imagegenEditPreview.src = compressed;
      els.imagegenEditPreview.classList.remove('hidden');
      els.imagegenSourceStage?.classList.add('has-source');
      els.imagegenEditPreview.onclick = () => openImagePreview(compressed, alt);
      imagegenEditSourceId = sourceId || '';
      if (els.imagegenEditResult && !els.imagegenEditResult.querySelector('.imagegen-result-card, .imagegen-progress')) {
        els.imagegenEditResult.innerHTML = '<div class="imagegen-stage-empty"><strong>Ready to edit</strong>Describe a change below — like ChatGPT or Grok.</div>';
      }
    }

    function sessionQuery() {
      return `?session=${encodeURIComponent(activeSession)}`;
    }

    async function loadSessions() {
      const data = await api('/api/sessions');
      sessionRows = data.sessions || [];
      if (!data.sessions.some(session => session.id === activeSession)) {
        activeSession = data.active || 'default';
        localStorage.setItem('ct_active_session', activeSession);
      }
      sessionPersonaLocks = Object.fromEntries((data.sessions || []).map(session => [session.id, {
        id: session.persona_id || '',
        name: session.persona_name || ''
      }]));
      els.sessionList.innerHTML = data.sessions
        .map(session => `<option value="${esc(session.id)}">${esc(session.name)} (${session.rings})</option>`)
        .join('');
      els.sessionList.value = activeSession;
      renderSessionChips();
      renderManageSessions();
      renderCreatorSourceSessions();
      applySessionPersonaLock();
    }

    async function switchSession(sessionId) {
      activeSession = sessionId || 'default';
      localStorage.setItem('ct_active_session', activeSession);
      if (els.workspace) els.workspace.textContent = `Workspace: ${activeSession}…`;
      // Don't let one slow panel block the whole session switch (or freeze nav).
      await Promise.allSettled([
        refreshSummary(),
        refreshMemories(),
        refreshWorkbench(),
        verifyChain(),
        restoreHistory(),
        refreshTrustStrip(),
      ]);
      await loadSessions().catch(() => null);
      applySessionPersonaLock();
    }

    async function createSession() {
      const name = els.sessionName.value.trim() || 'New conversation';
      const data = await api('/api/sessions', {
        method: 'POST',
        body: JSON.stringify({
          name,
          persona: els.persona.value,
          customPersona: customPersonas[els.persona.value] || publicPersonas[els.persona.value] || null
        })
      });
      els.sessionName.value = '';
      await switchSession(data.session.id);
    }

    function saveLocalConfig() {
      localStorage.setItem('ct_model', els.model.value.trim());
      localStorage.setItem('ct_provider', els.provider.value);
      localStorage.setItem('ct_base_url', els.baseUrl.value.trim());
      localStorage.setItem('ct_persona', els.persona.value);
      localStorage.setItem('ct_domain', els.domain.value);
      if (els.memoryAutopilot) localStorage.setItem('ct_memory_autopilot', els.memoryAutopilot.value);
      if (els.identityBridgeToggle) localStorage.setItem('ct_identity_bridge', els.identityBridgeToggle.checked ? 'true' : 'false');
      if (els.streamRepliesToggle) localStorage.setItem('ct_stream_replies', els.streamRepliesToggle.checked ? 'true' : 'false');
      if (els.apiKey.value.trim()) {
        localStorage.setItem('ct_api_key', els.apiKey.value.trim());
      } else {
        localStorage.removeItem('ct_api_key');
      }

      // Image Generation specific
      if (els.imageProvider) localStorage.setItem('ct_image_provider', els.imageProvider.value);
      if (els.imageModel) localStorage.setItem('ct_image_model', els.imageModel.value.trim());
      if (els.imagegenEditModel) localStorage.setItem('ct_image_edit_model', els.imagegenEditModel.value.trim());
      if (els.imageBaseUrl) {
        const imageBaseUrl = els.imageBaseUrl.value.trim();
        if (imageBaseUrl) localStorage.setItem('ct_image_base_url', imageBaseUrl);
        else localStorage.removeItem('ct_image_base_url');
      }
      if (els.imageApiKey) {
        const ik = els.imageApiKey.value.trim();
        if (ik) localStorage.setItem('ct_image_api_key', ik);
        else localStorage.removeItem('ct_image_api_key');
      }

      // Video Generation specific
      if (els.videoProvider) localStorage.setItem('ct_video_provider', els.videoProvider.value);
      if (els.videoModel) localStorage.setItem('ct_video_model', els.videoModel.value.trim());
      if (els.videoBaseUrl) localStorage.setItem('ct_video_base_url', els.videoBaseUrl.value.trim());
      if (els.videoApiKey) {
        const vk = els.videoApiKey.value.trim();
        if (vk) localStorage.setItem('ct_video_api_key', vk);
        else localStorage.removeItem('ct_video_api_key');
      }

      // Audio Generation specific
      if (els.audioProvider) localStorage.setItem('ct_audio_provider', els.audioProvider.value);
      if (els.audioModel) localStorage.setItem('ct_audio_model', els.audioModel.value.trim());
      if (els.audioBaseUrl) localStorage.setItem('ct_audio_base_url', els.audioBaseUrl.value.trim());
      if (els.audioApiKey) {
        const ak = els.audioApiKey.value.trim();
        if (ak) localStorage.setItem('ct_audio_api_key', ak);
        else localStorage.removeItem('ct_audio_api_key');
      }

      schedulePersistUserConfig();
    }

    function schedulePersistUserConfig() {
      if (configPersistTimer) {
        clearTimeout(configPersistTimer);
      }
      configPersistTimer = setTimeout(() => {
        configPersistTimer = null;
        persistUserConfig();
      }, 350);
    }

    async function persistUserConfig() {
      const token = localStorage.getItem('ct_auth_token') || '';
      if (!token) return;
      try {
        await api('/api/config', {
          method: 'POST',
          body: JSON.stringify({
            provider: els.provider?.value || '',
            default_model: els.model?.value?.trim() || '',
            base_url: els.baseUrl?.value?.trim() || '',
            image_provider: els.imageProvider?.value || '',
            image_model: els.imageModel?.value?.trim() || '',
            image_edit_model: els.imagegenEditModel?.value?.trim() || '',
            image_base_url: els.imageBaseUrl?.value?.trim() || '',
            video_provider: els.videoProvider?.value || '',
            video_model: els.videoModel?.value?.trim() || '',
            video_base_url: els.videoBaseUrl?.value?.trim() || '',
            audio_provider: els.audioProvider?.value || '',
            audio_model: els.audioModel?.value?.trim() || '',
            audio_base_url: els.audioBaseUrl?.value?.trim() || '',
            memory_autopilot: els.memoryAutopilot?.value || 'conservative',
            identity_bridge: els.identityBridgeToggle?.checked ? 'true' : 'false',
            stream_replies: els.streamRepliesToggle?.checked ? 'true' : 'false',
          }),
        });
      } catch {
        // Ignore persistence failures; local settings still apply.
      }
    }

    function loadCustomPersonas() {
      try {
        return JSON.parse(localStorage.getItem('ct_custom_personas') || '{}') || {};
      } catch {
        return {};
      }
    }

    function saveCustomPersonas() {
      localStorage.setItem('ct_custom_personas', JSON.stringify(customPersonas));
    }

    function renderPersonaOptions() {
      const builtIns = Object.entries(personas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)}</option>`)
        .join('');
      const custom = Object.entries(customPersonas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)} · custom</option>`)
        .join('');
      const created = Object.entries(creatorPersonas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)} - created</option>`)
        .join('');
      const pub = Object.entries(publicPersonas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)} · public (${esc(persona.owner || '')})</option>`)
        .join('');
      const mp = Object.entries(marketplacePersonas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)} · subscribed</option>`)
        .join('');
      let options = '';
      if (builtIns) options += `<optgroup label="Built-in">${builtIns}</optgroup>`;
      if (custom) options += `<optgroup label="My Personas">${custom}</optgroup>`;
      if (created) options += `<optgroup label="My Created Personas">${created}</optgroup>`;
      if (pub) options += `<optgroup label="Public Personas">${pub}</optgroup>`;
      if (mp) options += `<optgroup label="Subscribed">${mp}</optgroup>`;
      els.persona.innerHTML = options || '<option value="companion">Companion</option>';
      renderManagePersonas();
    }

    function renderManageSessions() {
      els.manageSessionSelect.innerHTML = sessionRows
        .map(session => `<option value="${esc(session.id)}">${esc(session.name)} (${session.rings})</option>`)
        .join('');
      els.manageSessionSelect.value = activeSession;
      const selected = sessionRows.find(session => session.id === els.manageSessionSelect.value);
      if (els.manageSessionName) els.manageSessionName.value = selected?.name || session_name_from_id_js(els.manageSessionSelect.value);
      els.manageDeleteSession.disabled = activeSession === 'default';
    }

    function renderManagePersonas() {
      const entries = Object.entries(customPersonas);
      els.managePersonaSelect.innerHTML = entries.length
        ? entries.map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)}</option>`).join('')
        : '<option value="">No custom personas</option>';
      els.managePersonaSelect.disabled = entries.length === 0;
      els.manageSavePersona.disabled = entries.length === 0;
      els.manageDeletePersona.disabled = entries.length === 0;
      if (entries.length && !customPersonas[els.managePersonaSelect.value]) {
        els.managePersonaSelect.value = entries[0][0];
      }
      loadSelectedManagePersona();
    }

    function loadSelectedManagePersona() {
      const id = els.managePersonaSelect.value;
      const persona = customPersonas[id] || null;
      els.managePersonaName.value = persona?.name || '';
      els.managePersonaSystem.value = persona?.system || '';
      els.managePersonaDomain.value = persona?.domain || 'auto';
      els.managePersonaVisibility.value = persona?.visibility || 'private';
    }

    function applySessionPersonaLock() {
      const lock = sessionPersonaLocks[activeSession] || {};
      const lockedPersonaId = lock.id || '';
      if (lockedPersonaId && (personas[lockedPersonaId] || customPersonas[lockedPersonaId] || creatorPersonas[lockedPersonaId] || publicPersonas[lockedPersonaId] || marketplacePersonas[lockedPersonaId])) {
        els.persona.value = lockedPersonaId;
        els.persona.disabled = true;
        els.personaLockHint.textContent = `Persona locked to this session: ${lock.name || getActivePersona()?.name || lockedPersonaId}.`;
      } else {
        els.persona.disabled = false;
        els.personaLockHint.textContent = 'New sessions lock to the persona selected when they are created.';
      }
      updatePersonaText();
      validatePersonaModel();
    }

    function getActivePersona() {
      return marketplacePersonas[els.persona.value] || publicPersonas[els.persona.value] || creatorPersonas[els.persona.value] || customPersonas[els.persona.value] || personas[els.persona.value] || personas.companion;
    }

    function resolvePersonaById(pid) {
      return marketplacePersonas[pid] || publicPersonas[pid] || creatorPersonas[pid] || customPersonas[pid] || personas[pid] || null;
    }

    function applyLocalConfig(config) {
      personas = config.personas || {};
      customPersonas = loadCustomPersonas();
      customPersonas = { ...(config.custom_personas || {}), ...customPersonas };
      creatorPersonas = config.creator_personas || {};
      publicPersonas = config.public_personas || {};
      marketplacePersonas = config.marketplace_personas || {};
      saveCustomPersonas();
      renderPersonaOptions();
      // Server-side curated catalogs (provider -> supported models / defaults).
      applyProviderCatalogs(config.provider_catalogs);
      // Browser settings should win so user-selected values persist across reloads.
      els.provider.value = localStorage.getItem('ct_provider') || config.provider || 'morpheus';
      els.baseUrl.value = localStorage.getItem('ct_base_url') || config.base_url || providerEndpoints[els.provider.value] || '';
      // Temporary value; updateChatModelOptions() rebinds to a model supported by the provider.
      els.model.value = localStorage.getItem('ct_model') || config.default_model || chatProviderDefaults[els.provider.value] || 'gemma-4-uncensored';
      els.apiKey.value = '';
      els.persona.value = localStorage.getItem('ct_persona') || 'companion';

      // Restore Image Generation settings
      if (els.imageProvider) {
        els.imageProvider.value = localStorage.getItem('ct_image_provider') || config.image_provider || 'openrouter';
      }
      if (els.imageModel) {
        const storedImageModel = localStorage.getItem('ct_image_model') || config.image_model;
        if (storedImageModel) {
          els.imageModel.value = storedImageModel;
        } else if (els.imageProvider) {
          els.imageModel.value = imageProviderDefaults[els.imageProvider.value] || 'black-forest-labs/flux.2-pro';
        }
      }
      if (els.imageApiKey) els.imageApiKey.value = '';
      if (els.imageBaseUrl) els.imageBaseUrl.value = localStorage.getItem('ct_image_base_url') || config.image_base_url || '';
      if (config.image_edit_model && !localStorage.getItem('ct_image_edit_model')) {
        localStorage.setItem('ct_image_edit_model', config.image_edit_model);
      }

      // Restore Video Generation settings
      if (els.videoProvider) {
        els.videoProvider.value = localStorage.getItem('ct_video_provider') || config.video_provider || 'openrouter';
      }
      if (els.videoModel) {
        const storedVideoModel = localStorage.getItem('ct_video_model') || config.video_model;
        if (storedVideoModel) {
          els.videoModel.value = storedVideoModel;
        } else if (els.videoProvider) {
          els.videoModel.value = videoProviderDefaults[els.videoProvider.value] || 'black-forest-labs/flux-video-pro';
        }
      }
      if (els.videoApiKey) els.videoApiKey.value = '';
      if (els.videoBaseUrl) els.videoBaseUrl.value = localStorage.getItem('ct_video_base_url') || config.video_base_url || '';
      
      // Restore Audio Generation settings
      if (els.audioProvider) {
        els.audioProvider.value = localStorage.getItem('ct_audio_provider') || config.audio_provider || 'morpheus';
      }
      if (els.audioModel) {
        els.audioModel.value = normalizeAudioModel(localStorage.getItem('ct_audio_model') || config.audio_model || 'tts-kokoro');
      }
      if (els.audioApiKey) els.audioApiKey.value = '';
      if (els.audioBaseUrl) els.audioBaseUrl.value = localStorage.getItem('ct_audio_base_url') || config.audio_base_url || '';
      
      if (!personas[els.persona.value] && !customPersonas[els.persona.value] && !creatorPersonas[els.persona.value] && !publicPersonas[els.persona.value] && !marketplacePersonas[els.persona.value]) els.persona.value = 'companion';
      els.domain.value = localStorage.getItem('ct_domain') || 'auto';
      const product = config.product || {};
      if (els.memoryAutopilot) {
        els.memoryAutopilot.value = localStorage.getItem('ct_memory_autopilot') || product.memory_autopilot || 'conservative';
      }
      if (els.identityBridgeToggle) {
        const storedBridge = localStorage.getItem('ct_identity_bridge');
        els.identityBridgeToggle.checked = storedBridge === null
          ? product.identity_bridge !== false
          : storedBridge !== 'false';
      }
      if (els.streamRepliesToggle) {
        const storedStream = localStorage.getItem('ct_stream_replies');
        els.streamRepliesToggle.checked = storedStream === null
          ? product.stream_replies !== false
          : storedStream !== 'false';
      }
      window.__recommendedProfile = config.recommended_profile || null;
      window.__skillVersion = config.skill_version || '';
      window.__appVersion = config.app_version || 'Forge/0.1';
      // Rebind chat/image/video/audio model pickers to the selected providers.
      updateChatModelOptions();
      updateImageModelOptions();
      updateImageEditModelOptions();
      updateVideoModelOptions();
      updateAudioModelOptions();
      updateProviderHint();
      updatePersonaText();
      updateSetup(config.has_env_key);
      validatePersonaModel();
      syncCreativeStudioModelsFromSettings();
      applySessionPersonaLock();
      refreshTrustStrip();
    }

    function applyTrustStatus(status) {
      if (!status) return;
      if (els.trustSkill) els.trustSkill.textContent = `skill: ${status.skill_version || window.__skillVersion || '—'}`;
      if (els.trustVerify) {
        els.trustVerify.textContent = `verify: ${status.verify_ok ? 'PASS' : 'FAIL'}`;
      }
      if (els.trustRings) els.trustRings.textContent = `height: ${status.height ?? status.ring_count ?? '—'}`;
      if (els.trustSeal) {
        const ts = status.last_seal_ts || '';
        const short = ts ? String(ts).replace('T', ' ').slice(0, 16) : '—';
        els.trustSeal.textContent = `last seal: ${short}`;
      }
      if (els.trustProduct) {
        const p = status.product || {};
        els.trustProduct.textContent = `memory: ${p.memory_autopilot || '—'} · identity: ${p.identity_bridge === false ? 'off' : 'on'}`;
      }
      if (els.trustStrip) {
        els.trustStrip.classList.toggle('ok', !!status.verify_ok);
        els.trustStrip.classList.toggle('bad', status.verify_ok === false);
      }
      if (els.verifyBadge) {
        els.verifyBadge.textContent = `verify: ${status.verify_ok ? 'PASS' : 'FAIL'}`;
        els.verifyBadge.className = `badge ${status.verify_ok ? 'ok' : 'bad'}`;
      }
      if (els.ringsBadge && status.ring_count != null) {
        els.ringsBadge.textContent = `rings: ${status.ring_count}`;
      }
    }

    async function refreshTrustStrip() {
      try {
        const data = await api(`/api/status${sessionQuery()}`);
        applyTrustStatus(data);
      } catch {
        if (els.trustSkill && window.__skillVersion) {
          els.trustSkill.textContent = `skill: ${window.__skillVersion}`;
        }
      }
    }

    async function syncCustomPersonasToServer(config) {
      const serverPersonas = config.custom_personas || {};
      const missingOnServer = Object.entries(customPersonas)
        .filter(([id]) => !serverPersonas[id]);
      await Promise.all(missingOnServer.map(([id, persona]) => api('/api/personas', {
        method: 'POST',
        body: JSON.stringify({ id, persona })
      }).catch(() => null)));
    }

    function setStatus(text, type = '') {
      els.setup.textContent = text;
      if (els.statusLabel) els.statusLabel.textContent = text;
      if (els.statusDot) {
        els.statusDot.className = 'status-indicator';
        if (type === 'ok') els.statusDot.classList.add('ok');
        if (type === 'warn') els.statusDot.classList.add('warn');
        if (type === 'error') els.statusDot.classList.add('error');
      }
    }

    function setStatusDetail(text) {
      if (els.statusDetail) els.statusDetail.textContent = text;
    }

    function updateProviderHint() {
      const provider = els.provider?.value || 'morpheus';
      const list = chatModelsByProvider[provider] || [];
      const fallback = chatProviderDefaults[provider] || '';
      if (els.modelHint) {
        if (provider === 'other') {
          els.modelHint.textContent = 'Enter the model name your custom provider expects.';
        } else if (list.length) {
          els.modelHint.textContent = `${list.length} model${list.length === 1 ? '' : 's'} for ${provider}`
            + (fallback ? ` · default: ${fallback}` : '')
            + '. Pick from the list or type a provider-supported id.';
        } else if (chatDiscoverable.has(provider)) {
          els.modelHint.textContent = 'Fetching models supported by this provider…';
        } else {
          els.modelHint.textContent = fallback
            ? `Use model: ${fallback}`
            : 'Enter a model id supported by this provider.';
        }
      }
      if (els.baseUrl && !els.baseUrl.value.trim() && providerEndpoints[provider]) {
        els.baseUrl.value = providerEndpoints[provider];
      }
    }

    function updateChatModelOptions({ forceDefault = false } = {}) {
      if (!els.model) return;
      const prov = els.provider?.value || 'morpheus';
      const list = chatModelsByProvider[prov] || [];
      const preferred = chatProviderDefaults[prov] || list[0] || '';
      const current = (els.model.value || '').trim();

      // Datalist suggestions = models this provider actually supports (curated and/or discovered).
      populateModelDatalist(
        els.chatModelOptions,
        list.map(id => ({ id, name: id }))
      );

      if (prov === 'other') {
        updateProviderHint();
        return;
      }

      const supported = current && list.includes(current);
      if (forceDefault || !current || (list.length > 0 && !supported)) {
        // Always land on a model the selected provider supports.
        els.model.value = preferred || (list[0] || current);
        localStorage.setItem('ct_model', els.model.value.trim());
      } else if (!list.length && preferred && forceDefault) {
        els.model.value = preferred;
        localStorage.setItem('ct_model', els.model.value.trim());
      }

      updateProviderHint();
      updateSetup();
    }

    function openImagePreview(src, alt = 'Image preview') {
      if (!src || !els.imagegenLightbox || !els.imagegenLightboxImage) return;
      els.imagegenLightboxImage.src = src;
      els.imagegenLightboxImage.alt = alt;
      els.imagegenLightbox.classList.remove('hidden');
    }

    function closeImagePreview() {
      if (!els.imagegenLightbox || !els.imagegenLightboxImage) return;
      els.imagegenLightbox.classList.add('hidden');
      els.imagegenLightboxImage.removeAttribute('src');
    }

    function downloadImage(src, filename = 'cyphertempre-image.png') {
      if (!src) return;
      const link = document.createElement('a');
      link.href = src;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
    }

    function renderImageResultCard(data, operation) {
      if (!data?.image?.id) {
        return '<div class="imagegen-error">Edit finished but the response was incomplete. Refresh the gallery — your image may still have been saved.</div>';
      }
      const src = data.data_url || `/api/imagegen/image/${encodeURIComponent(data.image.id)}`;
      const filename = `cyphertempre-${operation}-${data.image.id}.png`;
      const imageId = data.image.id;
      return `
        <div class="imagegen-result-card">
          <img src="${esc(src)}" alt="${esc(operation)} image" data-preview-src="${esc(src)}">
          <div class="imagegen-result-meta">
            <span class="badge">${esc(data.image.model)}</span>
            <span>${esc(operation)} · ${esc(data.image.aspect_ratio)}</span>
            <div class="imagegen-action-row">
              <button class="imagegen-action" type="button" data-image-preview="${esc(src)}">Preview</button>
              <button class="imagegen-action" type="button" data-image-download="${esc(src)}" data-filename="${esc(filename)}">Download</button>
              <button class="imagegen-action primary-ish" type="button" data-use-as-edit-source="${esc(src)}" data-source-id="${esc(imageId)}">Edit further</button>
            </div>
          </div>
        </div>`;
    }

    function wireImageActions(container) {
      if (!container) return;
      container.querySelectorAll('[data-image-preview]').forEach(button => {
        button.addEventListener('click', () => openImagePreview(button.dataset.imagePreview));
      });
      container.querySelectorAll('[data-image-download]').forEach(button => {
        button.addEventListener('click', () => downloadImage(button.dataset.imageDownload, button.dataset.filename));
      });
      container.querySelectorAll('[data-use-as-edit-source]').forEach(button => {
        button.addEventListener('click', () => {
          useImageAsEditSource(button.dataset.useAsEditSource, {
            sourceId: button.dataset.sourceId || '',
            alt: 'Edit source',
          }).catch(error => {
            if (els.imagegenEditResult) {
              els.imagegenEditResult.innerHTML = `<div class="imagegen-error">${esc(error.message || 'Could not load image for editing.')}</div>`;
            }
          });
        });
      });
      container.querySelectorAll('img[data-preview-src]').forEach(image => {
        image.addEventListener('click', () => openImagePreview(image.dataset.previewSrc, image.alt));
      });
    }

    async function setImageEditSource(file) {
      if (!file || !file.type.startsWith('image/')) return;
      const reader = new FileReader();
      reader.onload = async () => {
        imagegenEditSourceId = '';
        const compressed = await compressImageForEdit(reader.result);
        els.imagegenEditPreview.src = compressed;
        els.imagegenEditPreview.classList.remove('hidden');
        els.imagegenSourceStage?.classList.add('has-source');
        els.imagegenEditPreview.onclick = () => openImagePreview(compressed, file.name);
      };
      reader.readAsDataURL(file);
    }

    function populateModelDatalist(element, models) {
      if (!element) return;
      element.innerHTML = '';
      (models || []).forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.label = model.name || model.id;
        element.appendChild(option);
      });
    }

    function chooseSupportedModel(element, models, fallback = '') {
      if (!element || !models?.length) return;
      const ids = models.map(model => model.id);
      const current = element.value?.trim() || fallback;
      element.value = ids.includes(current) ? current : ids[0];
    }

    function providerSupportsDiscovery(provider) {
      const prov = String(provider || '').trim().toLowerCase();
      if (!prov || prov === 'other' || prov === 'demo') return false;
      // Chat providers use the discover set; image/video/audio use OpenAI-compatible /models.
      return true;
    }

    async function refreshProviderModels(provider = 'surplusintelligence', force = false, modality = '') {
      const prov = String(provider || '').trim().toLowerCase() || 'surplusintelligence';
      if (!providerSupportsDiscovery(prov)) {
        // Still refresh UI from curated catalogs for demo/other.
        if (els.provider?.value === prov) updateChatModelOptions({ forceDefault: true });
        if (els.imageProvider?.value === prov) {
          updateImageModelOptions();
          updateImageEditModelOptions();
        }
        if (els.videoProvider?.value === prov) updateVideoModelOptions();
        if (els.audioProvider?.value === prov) updateAudioModelOptions();
        return null;
      }
      if (!force && discoveredModelProviders.has(prov)) return null;

      let resolvedModality = String(modality || '').trim().toLowerCase();
      if (!resolvedModality) {
        if (els.provider?.value === prov) resolvedModality = 'chat';
        else if (els.imageProvider?.value === prov) resolvedModality = 'image';
        else if (els.videoProvider?.value === prov) resolvedModality = 'video';
        else if (els.audioProvider?.value === prov) resolvedModality = 'audio';
        else resolvedModality = 'chat';
      }
      const creds = providerDiscoveryCredentials(prov, resolvedModality);
      const params = new URLSearchParams({ provider: prov, modality: resolvedModality });
      if (creds.apiKey) params.set('apiKey', creds.apiKey);
      if (creds.baseUrl) params.set('baseUrl', creds.baseUrl);

      let data;
      try {
        // Hard timeout: discovery must never hang app boot / workspace load.
        data = await api('/api/models?' + params, {}, 8000);
      } catch (error) {
        // Discovery failed — keep curated lists so the selector still shows valid options.
        if (els.provider?.value === prov) {
          updateChatModelOptions();
          if (els.modelHint) {
            const n = (chatModelsByProvider[prov] || []).length;
            els.modelHint.textContent = n
              ? `Using ${n} curated model${n === 1 ? '' : 's'} (live catalog unavailable: ${error.message || error}).`
              : `Could not load live models: ${error.message || error}`;
          }
        }
        if (els.imageProvider?.value === prov) {
          updateImageModelOptions();
          updateImageEditModelOptions();
        }
        if (els.videoProvider?.value === prov) updateVideoModelOptions();
        if (els.audioProvider?.value === prov) updateAudioModelOptions();
        throw error;
      }

      const catalog = data.catalog || {};
      discoveredModelProviders.add(prov);

      const chatIds = (catalog.chat || []).map(model => model.id).filter(Boolean);
      if (chatIds.length) {
        chatModelsByProvider[prov] = chatIds;
        if (!chatProviderDefaults[prov]) chatProviderDefaults[prov] = chatIds[0];
      }

      const audioIds = (catalog.audio || []).map(model => model.id).filter(Boolean);
      if (audioIds.length) {
        audioModelsByProvider[prov] = audioIds;
        if (!audioProviderDefaults[prov]) audioProviderDefaults[prov] = audioIds[0];
      }
      populateModelDatalist(els.audioModelOptions, catalog.audio);

      const discoveredImageModels = (catalog.image || []).map(model => model.id).filter(Boolean);
      if (discoveredImageModels.length) {
        imageModelsByProvider[prov] = discoveredImageModels;
        if (!imageProviderDefaults[prov]) imageProviderDefaults[prov] = discoveredImageModels[0];
      }
      const discoveredEditModels = (catalog.image_edit || []).map(model => model.id).filter(Boolean);
      if (discoveredEditModels.length) {
        // Prefer uncensored / least-filtered edit models at the top of the selector.
        imageEditModelsByProvider[prov] = discoveredEditModels.slice().sort((a, b) => {
          const rank = (id) => {
            const l = String(id || '').toLowerCase();
            if (l.includes('uncensored')) return 0;
            if (l.includes('qwen-edit') || l.includes('lustify') || l.includes('venice') || l.includes('firered')) return 1;
            if (l.includes('grok-imagine') || l.includes('flux')) return 2;
            return 3;
          };
          return rank(a) - rank(b) || String(a).localeCompare(String(b));
        });
        if (!imageEditProviderDefaults[prov]) imageEditProviderDefaults[prov] = imageEditModelsByProvider[prov][0];
      }
      const discoveredVideoModels = (catalog.video || []).map(model => model.id).filter(Boolean);
      if (discoveredVideoModels.length) {
        videoModelsByProvider[prov] = discoveredVideoModels;
        if (!videoProviderDefaults[prov]) videoProviderDefaults[prov] = discoveredVideoModels[0];
      }

      if (els.provider?.value === prov) {
        updateChatModelOptions();
        if (els.modelHint && chatIds.length) {
          els.modelHint.textContent = `${chatIds.length} supported chat model${chatIds.length === 1 ? '' : 's'} detected for ${prov}.`;
        }
      }
      if (els.imageProvider?.value === prov) {
        updateImageModelOptions();
        updateImageEditModelOptions();
      }
      if (els.videoProvider?.value === prov) updateVideoModelOptions();
      if (els.audioProvider?.value === prov) {
        updateAudioModelOptions();
        chooseSupportedModel(els.audioModel, catalog.audio, localStorage.getItem('ct_audio_model') || audioProviderDefaults[prov] || '');
      }
      syncCreativeStudioModelsFromSettings();
      updateEffectiveProviderSummary();
      return catalog;
    }

    function updateAudioModelOptions() {
      if (!els.audioProvider || !els.audioModel) return;
      const prov = els.audioProvider.value;
      const list = audioModelsByProvider[prov] || [];
      const current = (els.audioModel.value || '').trim();
      populateModelDatalist(
        els.audioModelOptions,
        list.map(id => ({ id, name: id }))
      );
      if (prov === 'other') return;
      if (!current || (list.length && !list.includes(current))) {
        const next = audioProviderDefaults[prov] || list[0] || current;
        if (next) {
          els.audioModel.value = next;
          localStorage.setItem('ct_audio_model', next);
        }
      }
    }

    function updateImageModelOptions({ forceDefault = false } = {}) {
      if (!els.imageProvider || !els.imageModel) return;
      const prov = els.imageProvider.value;
      const list = imageModelsByProvider[prov] || [];
      const preferred = imageProviderDefaults[prov] || list[0] || '';
      const current = (els.imageModel.value || '').trim();

      els.imageModel.innerHTML = '';

      if (list.length === 0) {
        const opt = document.createElement('option');
        const fallback = (!forceDefault && current) ? current : (preferred || current || '');
        opt.value = fallback;
        opt.textContent = fallback || 'Enter custom model';
        els.imageModel.appendChild(opt);
        if (fallback) {
          els.imageModel.value = fallback;
          localStorage.setItem('ct_image_model', fallback);
        }
        if (els.imageModelHint) {
          els.imageModelHint.textContent = prov === 'other'
            ? 'Enter the exact model name your provider expects.'
            : (preferred ? `Default: ${preferred}` : 'No curated models — enter a provider-supported model id.');
        }
        return;
      }

      list.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        els.imageModel.appendChild(opt);
      });

      if (!forceDefault && current && list.includes(current)) {
        els.imageModel.value = current;
      } else {
        els.imageModel.value = preferred || list[0];
      }
      localStorage.setItem('ct_image_model', els.imageModel.value);

      if (els.imageModelHint) {
        els.imageModelHint.textContent = prov === 'other'
          ? 'Enter the exact model name your provider expects.'
          : `${list.length} model(s) for ${prov}` + (preferred ? ` · default: ${preferred}` : '');
      }
    }

    function updateImageEditModelOptions({ forceDefault = false } = {}) {
      if (!els.imageProvider || !els.imagegenEditModel) return;
      const prov = els.imageProvider.value;
      const list = imageEditModelsByProvider[prov] || [];
      const current = forceDefault ? '' : (els.imagegenEditModel.value || localStorage.getItem('ct_image_edit_model') || '');

      els.imagegenEditModel.innerHTML = '';
      els.imagegenEditModel.disabled = false;
      if (els.imagegenEditBtn) els.imagegenEditBtn.disabled = false;

      if (list.length === 0) {
        const opt = document.createElement('option');
        const fallback = current || imageEditProviderDefaults[prov] || '';
        opt.value = fallback;
        opt.textContent = fallback || 'Enter custom edit model';
        els.imagegenEditModel.appendChild(opt);
        if (fallback) localStorage.setItem('ct_image_edit_model', fallback);
        els.imagegenEditModel.title = prov === 'surplusintelligence'
          ? 'Uses POST /v1/images/edits with your source image. Prefer *-edit models (e.g. gpt-image-2-edit).'
          : '';
        return;
      }

      list.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        els.imagegenEditModel.appendChild(opt);
      });

      if (current && list.includes(current)) {
        els.imagegenEditModel.value = current;
      } else {
        els.imagegenEditModel.value = imageEditProviderDefaults[prov] || list[0];
      }
      localStorage.setItem('ct_image_edit_model', els.imagegenEditModel.value);
      els.imagegenEditModel.title = prov === 'surplusintelligence'
        ? 'Native image-to-image edit via /v1/images/edits. Requires a source image and an edit model.'
        : '';
    }

    function updateVideoModelOptions({ forceDefault = false } = {}) {
      if (!els.videoProvider || !els.videoModel) return;
      const prov = els.videoProvider.value;
      const list = videoModelsByProvider[prov] || [];
      const preferred = videoProviderDefaults[prov] || list[0] || '';
      const current = (els.videoModel.value || '').trim();

      els.videoModel.innerHTML = '';

      if (list.length === 0) {
        const opt = document.createElement('option');
        const fallback = (!forceDefault && current) ? current : (preferred || current || '');
        opt.value = fallback;
        opt.textContent = fallback || 'Enter custom model';
        els.videoModel.appendChild(opt);
        if (fallback) {
          els.videoModel.value = fallback;
          localStorage.setItem('ct_video_model', fallback);
        }
        if (els.videoModelHint) {
          els.videoModelHint.textContent = prov === 'other'
            ? 'Enter the exact model name your provider expects.'
            : (preferred ? `Default: ${preferred}` : 'No curated models — enter a provider-supported model id.');
        }
        return;
      }

      list.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        els.videoModel.appendChild(opt);
      });

      if (!forceDefault && current && list.includes(current)) {
        els.videoModel.value = current;
      } else {
        els.videoModel.value = preferred || list[0];
      }
      localStorage.setItem('ct_video_model', els.videoModel.value);

      if (els.videoModelHint) {
        els.videoModelHint.textContent = prov === 'demo'
          ? 'Built-in demo clip. No API key required.'
          : (prov === 'other'
            ? 'Enter the exact model name your provider expects.'
            : `${list.length} model(s) for ${prov}` + (preferred ? ` · default: ${preferred}` : ''));
      }
    }

    function updateSetup(hasEnvKey = false) {
      const hasBrowserKey = Boolean(els.apiKey.value.trim());
      const configured = hasEnvKey || hasBrowserKey;
      const providerMap = { morpheus: 'Morpheus', openrouter: 'OpenRouter', 'kimi-code': 'Kimi Code', kimi: 'Kimi Platform', other: 'Custom' };
      const providerName = providerMap[els.provider.value] || 'Morpheus';
      if (configured) {
        setStatus('Provider ready', 'ok');
        setStatusDetail(`${providerName} · ${els.model.value.trim() || 'default model'} · ${els.baseUrl.value.trim() || 'default endpoint'}`);
      } else {
        setStatus('Provider not configured', 'warn');
        setStatusDetail('Add an API key or set API_KEY in .env.local to get real LLM responses.');
      }
      els.modelBadge.textContent = els.model.value.trim() || 'gemma-4-uncensored';
    }

    function clearProviderOverride() {
      localStorage.removeItem('ct_provider');
      localStorage.removeItem('ct_model');
      localStorage.removeItem('ct_base_url');
      localStorage.removeItem('ct_api_key');
      localStorage.removeItem('ct_image_provider');
      localStorage.removeItem('ct_image_model');
      localStorage.removeItem('ct_image_edit_model');
      localStorage.removeItem('ct_image_base_url');
      localStorage.removeItem('ct_image_api_key');
      localStorage.removeItem('ct_video_provider');
      localStorage.removeItem('ct_video_model');
      localStorage.removeItem('ct_video_api_key');
      localStorage.removeItem('ct_video_base_url');
      localStorage.removeItem('ct_audio_provider');
      localStorage.removeItem('ct_audio_model');
      localStorage.removeItem('ct_audio_api_key');
      localStorage.removeItem('ct_audio_base_url');
      api('/api/config').then(config => applyLocalConfig(config));
    }

    async function testProvider() {
      saveLocalConfig();
      setStatus('Testing provider...', '');
      setStatusDetail('Sending a test request...');
      els.testProvider.disabled = true;
      try {
        const data = await api('/api/test', {
          method: 'POST',
          body: JSON.stringify({
            provider: els.provider.value,
            model: els.model.value.trim(),
            apiKey: els.apiKey.value.trim(),
            baseUrl: els.baseUrl.value.trim()
          })
        });
        setStatus('Provider OK', 'ok');
        setStatusDetail(`Connected · ${data.model_used || data.model}`);
      } catch (error) {
        setStatus('Connection failed', 'error');
        setStatusDetail(error.message);
      } finally {
        els.testProvider.disabled = false;
      }
    }

    async function testAudioProvider() {
      saveLocalConfig();
      setStatus('Testing audio provider...', '');
      setStatusDetail('Sending a tiny TTS request...');
      if (els.audioTestProvider) els.audioTestProvider.disabled = true;
      try {
        const data = await api('/api/audiogen/generate', {
          method: 'POST',
          body: JSON.stringify({
            text: 'Audio connection test.',
            voice: 'af_alloy',
            response_format: 'mp3',
            speed: 1,
            provider: els.audioProvider?.value || localStorage.getItem('ct_audio_provider') || 'morpheus',
            baseUrl: els.audioBaseUrl?.value || localStorage.getItem('ct_audio_base_url') || '',
            model: normalizeAudioModel(els.audioModel?.value || localStorage.getItem('ct_audio_model') || 'tts-kokoro'),
            apiKey: (els.audioApiKey?.value || els.apiKey?.value || '').trim(),
          })
        });
        setStatus('Audio provider OK', 'ok');
        setStatusDetail(`Connected · ${data.format || 'mp3'} · ${normalizeAudioModel(els.audioModel?.value || localStorage.getItem('ct_audio_model') || 'tts-kokoro')}`);
      } catch (error) {
        setStatus('Audio connection failed', 'error');
        setStatusDetail(error.message);
      } finally {
        if (els.audioTestProvider) els.audioTestProvider.disabled = false;
      }
    }

    function validatePersonaModel() {
      const isFree = (els.model.value || '').trim().endsWith(':free');
      const persona = getActivePersona();
      const requiresHighContext = !!persona?.requires_high_context || persona?.runtime_profile === 'cyphertempre_full';
      const personaName = persona?.name || 'This persona';
      const warn = isFree && requiresHighContext;
      const block = warn;
      els.composerWarning.classList.toggle('active', requiresHighContext);
      const warningDetail = document.getElementById('composer-warning-detail');
      if (warningDetail) {
        warningDetail.textContent = block
          ? 'Free models are blocked for this persona. Switch to a non-free model to use OpenClaw.'
          : `Paid or higher-context models can run it with this warning. ${personaName === 'Cypher Tempre OpenClaw Runtime' ? 'This persona' : personaName} consumes many tokens on this model.`;
      }
      els.send.disabled = block || isSending;
      els.message.placeholder = block
        ? 'Switch to a non-free model to use OpenClaw.'
        : requiresHighContext
        ? 'Ask anything... This persona consumes many tokens on this model.'
        : 'Ask anything...';
    }

    function updatePersonaText() {
      const persona = getActivePersona();
      els.title.textContent = persona?.name || 'Companion';
      if (!els.domain.value || els.domain.value !== 'auto') return;
    }

    function generatePersonaFromSeed(name, seed) {
      const personaName = name.trim();
      if (!personaName) throw new Error('Persona name is required.');
      const duplicate = Object.values({ ...personas, ...customPersonas })
        .some(persona => persona.name.toLowerCase() === personaName.toLowerCase());
      if (duplicate) throw new Error(`Persona name already exists: ${personaName}`);
      const style = seed || 'warm, practical, observant conversational partner';
      const system = [
        `You are ${personaName}, a fictional AI persona inspired by this vibe: ${style}.`,
        'Do not claim to be, impersonate, or have a personal relationship with any real public figure.',
        'Communicate in clear English with a calm, observant, slightly literary voice.',
        'Keep replies elegant, grounded, emotionally intelligent, and conversational.',
        'Be helpful and specific. Remember useful user preferences through the CypherTempre memory flow.',
      ].join(' ');
      return {
        name: personaName,
        domain: 'auto',
        seed: style,
        system,
      };
    }

    async function createPersona() {
      try {
        const seed = els.personaSeed.value.trim();
        const persona = generatePersonaFromSeed(els.personaName.value, seed);
        const id = `custom_${Date.now()}`;
        await api('/api/personas', {
          method: 'POST',
          body: JSON.stringify({ id, persona })
        });
        customPersonas[id] = persona;
        saveCustomPersonas();
        renderPersonaOptions();
        els.persona.value = id;
        els.domain.value = 'auto';
        saveLocalConfig();
        updatePersonaText();
        els.setup.textContent = `Created persona: ${persona.name}.`;
      } catch (error) {
        els.setup.textContent = error.message;
      }
    }

    function appendMessage(role, content, meta = {}, rejected = false) {
      els.empty?.remove();
      const wrapper = document.createElement('article');
      const isUser = role === 'You';
      wrapper.className = `message ${isUser ? 'user' : 'assistant'}${rejected ? ' rejected' : ''}`;
      const avatar = isUser ? 'Y' : 'C';
      const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const metaHtml = Object.entries(meta)
        .filter(([, value]) => value !== undefined && value !== null && value !== '')
        .map(([key, value]) => `<span class="badge ${key === 'accepted' ? (value ? 'ok' : 'bad') : 'info'}">${esc(key)}: ${esc(value)}</span>`)
        .join('');
      const headHtml = isUser
        ? ''
        : `<div class="bubble-head"><span>${esc(role)}</span><span>${timeLabel}</span></div>`;
      wrapper.innerHTML = `
        <div class="avatar" aria-hidden="true">${esc(avatar)}</div>
        <div class="bubble">
          ${headHtml}
          <div class="bubble-content">${renderContent(content)}</div>
          ${metaHtml ? `<div class="bubble-meta">${metaHtml}</div>` : ''}
        </div>
      `;
      els.messages.appendChild(wrapper);
      els.messages.scrollTop = els.messages.scrollHeight;
      return wrapper;
    }

    function appendThinkingMessage(personaName) {
      removeThinkingMessage();
      const wrapper = appendMessage(personaName || 'CypherTempre', '', {}, false);
      wrapper.classList.add('thinking-message');
      const content = wrapper.querySelector('.bubble-content');
      if (content) {
        content.innerHTML = `
          <span class="thinking-row" role="status" aria-live="polite">
            <span>Thinking and creating a response</span>
            <span class="thinking-dot"></span>
            <span class="thinking-dot"></span>
            <span class="thinking-dot"></span>
          </span>
        `;
      }
      return wrapper;
    }

    function removeThinkingMessage() {
      els.messages.querySelectorAll('.thinking-message').forEach(node => node.remove());
    }

    function clearRenderedMessages() {
      els.messages.querySelectorAll('.message').forEach(node => node.remove());
    }

    async function restoreHistory() {
      const data = await api(`/api/history${sessionQuery()}`, {}, 30000);
      clearRenderedMessages();
      if (!data.history?.length) {
        if (els.setup && /loading/i.test(els.setup.textContent || '')) {
          els.setup.textContent = 'Ready';
        }
        return;
      }
      els.empty?.remove();
      data.history.forEach(item => {
        if (item.role === 'user') {
          appendMessage('You', item.content, { domain: item.domain, ring: item.ring });
        } else {
          appendMessage('CypherTempre', item.content, {
            accepted: true,
            ring: item.ring,
            brightness: item.brightness,
            epistemic: item.epistemic,
            hash: item.hash_prefix
          });
        }
      });
      els.setup.textContent = `Restored ${Math.floor(data.history.length / 2)} remembered exchanges.`;
    }

    function renderSummary(model) {
      els.workspace.textContent = `Workspace: ${model.workspace || '(local)'}`;
      els.ringsBadge.textContent = `rings: ${model.ring_count}`;
      currentFrozen = Boolean(model.frozen);
      els.manageFreeze.textContent = currentFrozen ? 'Unfreeze Chain' : 'Freeze Chain';
      els.manageStatusLabel.textContent = currentFrozen ? 'Active session frozen' : 'Active session writable';
      els.manageStatusDot.className = `status-indicator ${currentFrozen ? 'warn' : 'ok'}`;
      els.manageStatusDetail.textContent = `${session_name_from_id_js(activeSession)} · rings ${model.ring_count} · ${model.workspace || '(local)'}`;
      const facts = model.memory_facts || [];
      const factSummary = facts.length
        ? facts.slice(0, 6).map(fact => `${fact.key}=${fact.value} (#${fact.source_ring})`).join('\n')
        : '(none)';
      const rows = {
        agent: model.name,
        rings: model.ring_count,
        mass: model.temporal_mass,
        frozen: model.frozen,
        facts: model.memory_fact_count || 0,
        active: `${model.active_memory_count || 0} memories, ${model.active_ring_count || 0} rings`,
        stale: `${model.stale_memory_count || 0} memories, ${model.stale_ring_count || 0} rings`,
        window: `${model.active_context_days || 90} days`,
        domains: (model.top_domains || []).join(', ') || '(none)',
        genesis: String(model.genesis_hash || '').slice(0, 16),
        memory: factSummary
      };
      els.summary.innerHTML = Object.entries(rows)
        .map(([key, value]) => `<dt>${esc(key)}</dt><dd>${esc(value)}</dd>`)
        .join('');
    }

    function session_name_from_id_js(sessionId) {
      if (sessionId === 'default') return 'Default';
      return String(sessionId || '').replace(/[-_]+/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase()) || sessionId;
    }

    async function refreshSummary() {
      try {
        const data = await api(`/api/self-model${sessionQuery()}`, {}, 20000);
        if (data?.model) {
          renderSummary(data.model);
          return data;
        }
      } catch (error) {
        if (els.workspace) {
          els.workspace.textContent = `Workspace: ${activeSession || 'default'} (summary unavailable)`;
        }
        if (els.ringsBadge) els.ringsBadge.textContent = 'rings: —';
        throw error;
      }
      if (els.workspace) {
        els.workspace.textContent = `Workspace: ${activeSession || 'default'}`;
      }
      return null;
    }

    function renderRings(rings) {
      ringRows = rings || [];
      els.manageRingSelect.innerHTML = ringRows.length
        ? ringRows.map(ring => `<option value="${esc(ring.n)}">#${esc(ring.n)} ${esc(ring.kind)} · ${esc(ring.domain)}</option>`).join('')
        : '<option value="">No rings available</option>';
      els.manageRewind.disabled = ringRows.length === 0;
      els.ringTimeline.innerHTML = rings?.length
        ? rings.map(ring => {
            const scoreText = ring.scores && Object.keys(ring.scores).length
              ? Object.entries(ring.scores).map(([key, value]) => `${key}=${value}`).join(' ')
              : 'scores unavailable';
            const lineage = [
              ring.supersedes ? `supersedes #${ring.supersedes}` : '',
              ring.retrieved?.length ? `retrieved ${ring.retrieved.join(', ')}` : '',
              ring.hash_prefix ? `hash ${ring.hash_prefix}` : ''
            ].filter(Boolean).join(' · ');
            return `
              <article class="ring-card">
                <strong>#${esc(ring.n)} ${esc(ring.kind)} · ${esc(ring.domain)} · brightness ${esc(ring.brightness)}</strong>
                <p>${esc(ring.query || ring.content || '(empty ring)')}</p>
                <div class="memory-meta">${esc(ring.epistemic || 'unknown')} · ${esc(scoreText)}</div>
                ${lineage ? `<div class="memory-meta">${esc(lineage)}</div>` : ''}
              </article>
            `;
          }).join('')
        : 'No rings yet.';
    }

    function renderCambium(data) {
      const gaps = data.gaps?.length
        ? data.gaps.map(gap => `gap ${gap.domain}: mean brightness ${gap.mean_brightness}`).join('\n')
        : 'No repeated low-brightness gaps.';
      const consolidations = data.consolidations?.length
        ? data.consolidations.map(domain => `consolidate ${domain}`).join('\n')
        : 'No consolidation candidates yet.';
      const proposals = data.proposals?.length
        ? data.proposals.slice(0, 8).map(proposal => `proposal ${proposal.proposed_domain}: ${proposal.reason}`).join('\n')
        : 'No growth proposals yet.';
      els.cambiumResults.textContent = `Gaps\n${gaps}\n\nConsolidations\n${consolidations}\n\nProposals\n${proposals}`;
    }

    function renderOverlays(data) {
      const overlays = data.overlays || {};
      const entries = Object.entries(overlays);
      els.overlayList.textContent = entries.length
        ? entries.map(([tag, weight]) => `${tag}: ${weight}`).join(' | ')
        : 'No active overlays.';
    }

    async function refreshWorkbench() {
      const [rings, cambium, overlays] = await Promise.all([
        api(`/api/rings${sessionQuery()}&limit=24`, {}, 20000),
        api(`/api/cambium${sessionQuery()}`, {}, 20000),
        api(`/api/overlays${sessionQuery()}`, {}, 20000)
      ]);
      renderRings(rings.rings || []);
      renderCambium(cambium);
      renderOverlays(overlays);
    }

    async function copySyncSnapshot() {
      const data = await api(`/api/sync-snapshot${sessionQuery()}`);
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(data.snapshot || '');
        els.cambiumResults.textContent = `Sync Snapshot copied.\n\n${data.snapshot || ''}`;
      } else {
        els.cambiumResults.textContent = data.snapshot || 'Sync Snapshot unavailable.';
      }
    }

    function confirmTimechainMutation(label) {
      return window.confirm(`${label} will modify the active Timechain session. Continue?`);
    }

    function showAdvancedTimechainResult(label, data) {
      els.advancedTimechainResults.textContent = `${label}\n${JSON.stringify(data, null, 2)}`;
    }

    async function runDream() {
      if (!confirmTimechainMutation('Dream synthesis')) return;
      const data = await api('/api/dream', {
        method: 'POST',
        body: JSON.stringify({
          session: activeSession,
          domains: els.dreamDomains.value.trim(),
          cycles: Number(els.dreamCycles.value || 3)
        })
      });
      showAdvancedTimechainResult('Dream synthesis', data);
      await refreshOperationalState();
    }

    async function saveOverlay() {
      if (!confirmTimechainMutation('Overlay update')) return;
      const data = await api('/api/overlays', {
        method: 'POST',
        body: JSON.stringify({
          session: activeSession,
          tag: els.overlayTag.value.trim(),
          weight: Number(els.overlayWeight.value || 1)
        })
      });
      renderOverlays(data);
      showAdvancedTimechainResult('Overlay update', data);
      await refreshSummary();
    }

    async function runMemorySync() {
      if (!confirmTimechainMutation('Memory sync')) return;
      const data = await api('/api/memory-sync', {
        method: 'POST',
        body: JSON.stringify({ session: activeSession })
      });
      showAdvancedTimechainResult('Memory sync', data);
      await refreshOperationalState();
    }

    async function runFleetImport() {
      if (!confirmTimechainMutation('Fleet import')) return;
      const data = await api('/api/fleet-import', {
        method: 'POST',
        body: JSON.stringify({
          session: activeSession,
          source: els.fleetSource.value.trim(),
          ring: JSON.parse(els.fleetRingJson.value || '{}')
        })
      });
      showAdvancedTimechainResult('Fleet import', data);
      await refreshOperationalState();
    }

    async function runChallenge() {
      const data = await api('/api/challenge', {
        method: 'POST',
        body: JSON.stringify({
          session: activeSession,
          indices: els.challengeIndices.value.trim(),
          nonce: els.challengeNonce.value.trim()
        })
      });
      showAdvancedTimechainResult('Temporal challenge', data);
    }

    let sharedMemoryHits = [];
    let selectedSharedHitIds = new Set();

    async function searchSharedMemory() {
      const query = els.sharedMemoryQuery.value.trim();
      if (!query) return;
      els.sharedMemoryResults.textContent = 'Searching...';
      try {
        const data = await api(`/api/shared-memory?session=${encodeURIComponent(activeSession)}&query=${encodeURIComponent(query)}&limit=12`);
        sharedMemoryHits = data.hits || [];
        selectedSharedHitIds.clear();
        if (!sharedMemoryHits.length) {
          els.sharedMemoryResults.textContent = 'No shared memory hits found.';
          return;
        }
        els.sharedMemoryResults.innerHTML = sharedMemoryHits.map((hit, idx) => {
          const content = esc(hit.content || '');
          return `<div style="margin:6px 0;padding:8px;border:1px solid var(--line);border-radius:8px;cursor:pointer;" data-idx="${idx}">
            <label style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;">
              <input type="checkbox" data-hit-id="${esc(hit.id)}" style="margin-top:2px;">
              <div style="font-size:13px;line-height:1.4;">
                <div style="color:var(--muted);font-size:12px;">session=${esc(hit.source_session)} ring=${esc(hit.source_ring)} score=${esc(hit.score)} brightness=${esc(hit.brightness)}</div>
                <div>[${esc(hit.domain)}] ${content}</div>
              </div>
            </label>
          </div>`;
        }).join('');
        els.sharedMemoryResults.querySelectorAll('input[type="checkbox"]').forEach(cb => {
          cb.addEventListener('change', () => {
            if (cb.checked) selectedSharedHitIds.add(cb.dataset.hitId);
            else selectedSharedHitIds.delete(cb.dataset.hitId);
          });
        });
      } catch (error) {
        els.sharedMemoryResults.textContent = error.message;
      }
    }

    async function importSharedMemory() {
      if (!selectedSharedHitIds.size) {
        showAdvancedTimechainResult('Shared memory import', { ok: false, error: 'No hits selected.' });
        return;
      }
      for (const hitId of selectedSharedHitIds) {
        const data = await api('/api/shared-memory/import', {
          method: 'POST',
          body: JSON.stringify({ session: activeSession, hitId })
        });
        showAdvancedTimechainResult('Shared memory import', data);
      }
      await refreshOperationalState();
    }

    async function synthesizeSharedMemory() {
      if (!selectedSharedHitIds.size) {
        showAdvancedTimechainResult('Shared memory synthesis', { ok: false, error: 'No hits selected.' });
        return;
      }
      const query = els.sharedMemoryQuery.value.trim() || 'shared memory comprehension synthesis';
      const data = await api('/api/shared-memory/synthesize', {
        method: 'POST',
        body: JSON.stringify({
          session: activeSession,
          query,
          hitIds: Array.from(selectedSharedHitIds)
        })
      });
      showAdvancedTimechainResult('Shared memory synthesis', data);
      await refreshOperationalState();
    }

    function memoryMeta(memory) {
      const scope = memory.scope || 'legacy';
      const confidence = Number(memory.confidence || 0).toFixed(2);
      const source = memory.source_ring || '?';
      const session = memory.scope === 'session' ? ` | ${memory.session_id || activeSession}` : '';
      const state = memory.active ? 'Active context' : (memory.status === 'pending' ? 'Pending' : 'Stale');
      const age = Number.isFinite(Number(memory.age_days)) ? ` | ${Number(memory.age_days)}d old` : '';
      const reason = memory.stale_reason ? ` | ${memory.stale_reason}` : '';
      const supersedes = memory.supersedes ? ` | supersedes ${memory.supersedes}` : '';
      return `${state} | ${scope} | ${memory.kind || 'memory'} | confidence ${confidence} | ring #${source}${session}${age}${reason}${supersedes}`;
    }

    function renderMemoryCard(memory, pending) {
      const actions = pending
        ? `<button class="accept-memory" type="button" data-action="accept" data-id="${esc(memory.id)}">Accept</button>
           <button class="reject-memory" type="button" data-action="reject" data-id="${esc(memory.id)}">Reject</button>
           <button class="edit-memory" type="button" data-action="edit" data-id="${esc(memory.id)}">Edit</button>`
        : `<button class="forget-memory" type="button" data-action="forget" data-id="${esc(memory.id)}">Forget</button>
           <button class="edit-memory" type="button" data-action="edit" data-id="${esc(memory.id)}">Edit</button>`;
      return `
        <article class="memory-card">
          <strong>${esc(memory.key || 'memory')}: ${esc(memory.value || '')}</strong>
          <div class="memory-meta">${esc(memoryMeta(memory))}</div>
          ${memory.evidence ? `<div class="memory-meta">source: ${esc(memory.evidence)}</div>` : ''}
          <div class="memory-actions">${actions}</div>
        </article>
      `;
    }

    function renderMemories(data) {
      const pending = data.pending || [];
      const accepted = data.accepted || [];
      els.pendingMemories.innerHTML = pending.length
        ? pending.map(memory => renderMemoryCard(memory, true)).join('')
        : 'No pending memories.';
      els.acceptedMemories.innerHTML = accepted.length
        ? accepted.slice(0, 16).map(memory => renderMemoryCard(memory, false)).join('')
        : 'No accepted memories.';
    }

    async function refreshMemories() {
      const data = await api(`/api/memories${sessionQuery()}`, {}, 20000);
      renderMemories(data);
    }

    async function updateMemory(id, action, memory = null) {
      const payload = { id, action, session: activeSession };
      if (memory) payload.memory = memory;
      const data = await api('/api/memories', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      renderMemories(data);
      await refreshSummary();
      await refreshWorkbench();
    }

    async function verifyChain() {
      try {
        const data = await api(`/api/verify${sessionQuery()}`, {}, 20000);
        if (els.verifyResult) {
          els.verifyResult.textContent = `${data.ok ? 'OK' : 'FAILED'}: ${data.status} | rings=${data.rings}`;
        }
        if (els.verifyBadge) {
          els.verifyBadge.textContent = data.ok ? 'verify: ok' : 'verify: failed';
          els.verifyBadge.className = `badge ${data.ok ? 'ok' : 'bad'}`;
        }
      } catch (error) {
        if (els.verifyBadge) {
          els.verifyBadge.textContent = 'verify: —';
          els.verifyBadge.className = 'badge';
        }
        if (els.verifyResult) {
          els.verifyResult.textContent = `Verify unavailable: ${error.message || error}`;
        }
      }
    }

    async function resetChainMemory() {
      els.verifyResult.textContent = 'Resetting chain memory...';
      const data = await api(`/api/reset${sessionQuery()}`, { method: 'POST', body: JSON.stringify({}) });
      clearRenderedMessages();
      if (!document.getElementById('empty-state')) {
        els.messages.innerHTML = emptyStateHtml();
        els.empty = document.getElementById('empty-state');
      }
      els.recallResults.textContent = 'Memory reset. No recall query yet.';
      els.verifyResult.textContent = `Reset complete. New genesis chain created. rings=${data.rings}`;
      await refreshSummary();
      await refreshMemories();
      await refreshWorkbench();
      await verifyChain();
    }

    async function refreshOperationalState() {
      await Promise.all([refreshSummary(), refreshMemories(), refreshWorkbench(), verifyChain(), restoreHistory(), refreshTrustStrip()]);
      await loadSessions();
      renderManageSessions();
      renderManagePersonas();
    }

    async function toggleFreeze() {
      const data = await api('/api/freeze', {
        method: 'POST',
        body: JSON.stringify({ session: activeSession, frozen: !currentFrozen })
      });
      currentFrozen = Boolean(data.frozen);
      await refreshOperationalState();
      if (currentFrozen) {
        els.manageStatusDetail.innerHTML = 'Session is frozen. New rings will not seal. <a href="#" id="freeze-post-link" style="color:var(--accent);text-decoration:underline;">Post to Creator Studio</a>';
        const link = document.getElementById('freeze-post-link');
        if (link) link.addEventListener('click', (e) => { e.preventDefault(); setSettingsSection('creator'); });
      } else {
        els.manageStatusDetail.textContent = 'Session is writable again.';
      }
    }

    async function rewindActiveSession() {
      const ring = Number(els.manageRingSelect.value);
      if (!Number.isInteger(ring)) throw new Error('Choose a ring to rewind to.');
      const ok = window.confirm(`Archive and rewind ${session_name_from_id_js(activeSession)} to ring #${ring}? Later rings will be removed from the active chain.`);
      if (!ok) return;
      const data = await api('/api/rewind', {
        method: 'POST',
        body: JSON.stringify({ session: activeSession, ring })
      });
      await refreshOperationalState();
      els.manageStatusDetail.textContent = `Rewound to ring #${data.rewound_to}. Archive: ${data.archive}. Verify: ${data.verify_status}`;
    }

    async function deleteSelectedSession() {
      const sessionId = els.manageSessionSelect.value;
      if (!sessionId || sessionId === 'default') throw new Error('Default session cannot be deleted.');
      const ok = window.confirm(`Delete session "${session_name_from_id_js(sessionId)}"? This cannot be undone from the app.`);
      if (!ok) return;
      const data = await api('/api/sessions/delete', {
        method: 'POST',
        body: JSON.stringify({ session: sessionId })
      });
      activeSession = data.active || 'default';
      localStorage.setItem('ct_active_session', activeSession);
      await refreshOperationalState();
      els.manageStatusDetail.textContent = `Deleted session ${session_name_from_id_js(sessionId)}.`;
    }

    async function renameSelectedSession() {
      const sessionId = els.manageSessionSelect.value;
      const name = els.manageSessionName.value.trim();
      if (!sessionId) throw new Error('Choose a session to rename.');
      if (!name) throw new Error('Session name is required.');
      const data = await api('/api/sessions/rename', {
        method: 'POST',
        body: JSON.stringify({ session: sessionId, name })
      });
      sessionRows = data.sessions || sessionRows;
      renderManageSessions();
      if (sessionId === activeSession) {
        await loadSessions();
      }
      els.manageStatusDetail.textContent = `Renamed session to ${data.name}.`;
    }

    async function saveManagedPersona() {
      const id = els.managePersonaSelect.value;
      if (!id || !customPersonas[id]) throw new Error('Choose a custom persona to edit.');
      const persona = {
        name: els.managePersonaName.value.trim(),
        domain: els.managePersonaDomain.value,
        system: els.managePersonaSystem.value.trim(),
        visibility: els.managePersonaVisibility.value
      };
      const data = await api('/api/personas', {
        method: 'POST',
        body: JSON.stringify({ id, persona })
      });
      customPersonas = data.custom_personas || customPersonas;
      saveCustomPersonas();
      renderPersonaOptions();
      applySessionPersonaLock();
      els.manageStatusDetail.textContent = `Saved persona ${data.persona?.name || id}.`;
    }

    async function deleteManagedPersona() {
      const id = els.managePersonaSelect.value;
      if (!id || !customPersonas[id]) throw new Error('Choose a custom persona to delete.');
      const ok = window.confirm(`Delete custom persona "${customPersonas[id].name}"? Existing sessions will fall back if this persona is missing.`);
      if (!ok) return;
      const data = await api('/api/personas/delete', {
        method: 'POST',
        body: JSON.stringify({ id })
      });
      customPersonas = data.custom_personas || {};
      localStorage.setItem('ct_custom_personas', JSON.stringify(customPersonas));
      renderPersonaOptions();
      if (!customPersonas[els.persona.value] && !personas[els.persona.value] && !publicPersonas[els.persona.value] && !marketplacePersonas[els.persona.value]) els.persona.value = 'companion';
      applySessionPersonaLock();
      els.manageStatusDetail.textContent = `Deleted persona ${id}.`;
    }

    function chatPayload(message) {
      return {
        message,
        session: activeSession,
        domain: els.domain.value,
        persona: els.persona.value,
        customPersona: customPersonas[els.persona.value] || publicPersonas[els.persona.value] || null,
        model: els.model.value.trim() || 'gemma-4-uncensored',
        apiKey: els.apiKey.value.trim(),
        provider: els.provider.value,
        baseUrl: els.baseUrl.value.trim(),
        sharedMemory: els.sharedMemoryToggle?.checked || false
      };
    }

    function citationHtml(citations) {
      if (!citations || typeof citations !== 'object') return '';
      const unsupported = citations.unsupported || citations.unsupported_spans || [];
      const used = citations.used_rings || citations.used || [];
      const nUn = citations.n_unsupported != null ? citations.n_unsupported : (Array.isArray(unsupported) ? unsupported.length : 0);
      const usedLabel = Array.isArray(used) ? used.join(', ') : String(used || '');
      if (!usedLabel && !nUn) return '';
      let body = `<strong>Citations</strong> · used rings: ${esc(usedLabel || '—')}`;
      if (nUn > 0) {
        const sample = Array.isArray(unsupported)
          ? unsupported.slice(0, 2).map(u => (typeof u === 'string' ? u : (u.text || u.span || JSON.stringify(u)))).join(' · ')
          : '';
        body += `<br>⚠ ${esc(String(nUn))} unsupported span(s)${sample ? `: ${esc(sample)}` : ''}`;
      } else {
        body += `<br>✓ spans grounded against declared rings`;
      }
      return `<div class="citation-box">${body}</div>`;
    }

    function applyChatResult(data, streamWrapper) {
      if (data.persona_id) {
        sessionPersonaLocks[activeSession] = { id: data.persona_id, name: data.persona_name || '' };
        applySessionPersonaLock();
      }
      if (data.trust) applyTrustStatus(data.trust);
      const role = data.persona_name || 'CypherTempre';
      const cite = citationHtml(data.citations);
      if (streamWrapper && streamWrapper.isConnected) {
        streamWrapper.classList.remove('streaming', 'thinking-message');
        const contentEl = streamWrapper.querySelector('.bubble-content');
        const metaEl = streamWrapper.querySelector('.bubble-meta');
        if (contentEl) contentEl.innerHTML = renderContent(data.content || data.reason || '') + cite;
        if (data.accepted) {
          streamWrapper.classList.remove('rejected');
          if (metaEl) {
            metaEl.innerHTML = Object.entries({
              accepted: true,
              ring: data.ring,
              brightness: data.brightness,
              epistemic: data.epistemic,
              model: data.model_used || data.model,
              domain: data.domain,
              offline: data.offline ? 'yes' : '',
              retry: data.retry?.attempted ? 'yes' : '',
              memory: (data.memory_hits || []).length || '',
              autoMem: (data.memory_auto_accepted || []).length || '',
              cites: data.citations?.n_unsupported != null ? `${(data.citations.used_rings || []).length || 0}r` : ''
            }).filter(([, v]) => v !== undefined && v !== null && v !== '')
              .map(([k, v]) => `<span class="badge ${k === 'accepted' ? 'ok' : 'info'}">${esc(k)}: ${esc(v)}</span>`)
              .join('');
          }
        } else {
          streamWrapper.classList.add('rejected');
          if (contentEl) contentEl.innerHTML = renderContent(data.reason || data.content || 'Rejected by PoQ gate.');
        }
        return;
      }
      if (data.accepted) {
        const wrapper = appendMessage(role, data.content, {
          accepted: true,
          ring: data.ring,
          brightness: data.brightness,
          epistemic: data.epistemic,
          model: data.model_used || data.model,
          provider: data.provider_error ? 'fallback' : '',
          error: data.provider_error || '',
          domain: data.domain,
          offline: data.offline ? 'yes' : '',
          retry: data.retry?.attempted ? 'yes' : '',
          memory: (data.memory_hits || []).length || '',
          autoMem: (data.memory_auto_accepted || []).length || ''
        });
        if (cite) {
          const contentEl = wrapper.querySelector('.bubble-content');
          if (contentEl) contentEl.insertAdjacentHTML('beforeend', cite);
        }
      } else {
        appendMessage(role, data.reason || data.content || 'Rejected by PoQ gate.', {
          accepted: false,
          brightness: data.brightness,
          provider: data.provider_error ? 'fallback' : '',
          error: data.provider_error || ''
        }, true);
      }
    }

    async function sendChatStreaming(message) {
      const personaName = getActivePersona()?.name || 'CypherTempre';
      const streamWrapper = appendThinkingMessage(personaName);
      streamWrapper.classList.add('streaming');
      const contentEl = streamWrapper.querySelector('.bubble-content');
      let assembled = '';
      const token = localStorage.getItem('ct_auth_token') || '';
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(chatPayload(message))
      });
      if (!response.ok || !response.body) {
        throw new Error(`Stream failed (${response.status})`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalData = null;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';
        for (const part of parts) {
          const lines = part.split('\n');
          let event = 'message';
          let dataLine = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            if (line.startsWith('data:')) dataLine += line.slice(5).trim();
          }
          if (!dataLine) continue;
          let data;
          try { data = JSON.parse(dataLine); } catch { continue; }
          if (event === 'token' && data.text) {
            assembled += data.text;
            if (contentEl) contentEl.innerHTML = renderContent(assembled);
            els.messages.scrollTop = els.messages.scrollHeight;
          } else if (event === 'meta' && data.persona_name && streamWrapper) {
            const head = streamWrapper.querySelector('.bubble-head span');
            if (head) head.textContent = data.persona_name;
          } else if (event === 'final') {
            finalData = data;
          } else if (event === 'error') {
            throw new Error(data.error || 'Stream error');
          }
        }
      }
      if (!finalData) throw new Error('Stream ended without a final result');
      applyChatResult(finalData, streamWrapper);
    }

    async function sendChatBlocking(message) {
      const thinkingMessage = appendThinkingMessage(getActivePersona()?.name || 'CypherTempre');
      try {
        const data = await api('/api/chat', {
          method: 'POST',
          body: JSON.stringify(chatPayload(message))
        });
        removeThinkingMessage();
        applyChatResult(data, null);
      } finally {
        if (thinkingMessage && thinkingMessage.isConnected) thinkingMessage.remove();
      }
    }

    els.form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const message = els.message.value.trim();
      if (!message) return;

      saveLocalConfig();
      appendMessage('You', message, { domain: els.domain.value });
      els.message.value = '';
      isSending = true;
      validatePersonaModel();
      const preferStream = !els.streamRepliesToggle || els.streamRepliesToggle.checked;

      try {
        if (preferStream) {
          try {
            await sendChatStreaming(message);
          } catch (streamErr) {
            removeThinkingMessage();
            await sendChatBlocking(message);
          }
        } else {
          await sendChatBlocking(message);
        }
        await refreshSummary();
        await refreshMemories();
        await refreshWorkbench();
        await verifyChain();
        await refreshTrustStrip();
      } catch (error) {
        removeThinkingMessage();
        try {
          await restoreHistory();
          await refreshSummary();
          await verifyChain();
          await refreshTrustStrip();
        } catch (_) {
          appendMessage('CypherTempre', error.message, { accepted: false }, true);
        }
      } finally {
        isSending = false;
        validatePersonaModel();
        els.message.focus();
      }
    });

    if (els.applyRecommendedDefaults) {
      els.applyRecommendedDefaults.addEventListener('click', () => {
        const rec = window.__recommendedProfile || {};
        if (els.provider && rec.provider) els.provider.value = rec.provider;
        if (els.model && rec.default_model) els.model.value = rec.default_model;
        if (els.baseUrl && rec.base_url) els.baseUrl.value = rec.base_url;
        if (els.memoryAutopilot) els.memoryAutopilot.value = rec.memory_autopilot || 'conservative';
        if (els.identityBridgeToggle) els.identityBridgeToggle.checked = rec.identity_bridge !== false;
        if (els.streamRepliesToggle) els.streamRepliesToggle.checked = rec.stream_replies !== false;
        updateProviderHint();
        saveLocalConfig();
        if (els.setup) els.setup.textContent = 'Recommended defaults applied. Add your API key if the env file is empty.';
        refreshTrustStrip();
      });
    }
    ['memoryAutopilot', 'identityBridgeToggle', 'streamRepliesToggle'].forEach(key => {
      const node = els[key];
      if (node) node.addEventListener('change', () => saveLocalConfig());
    });

    // --- Backup / project ---
    if (els.exportBackup) {
      els.exportBackup.addEventListener('click', async () => {
        try {
          const token = localStorage.getItem('ct_auth_token') || '';
          const response = await fetch('/api/backup/export?media=1', {
            credentials: 'same-origin',
            headers: token ? { Authorization: `Bearer ${token}` } : {}
          });
          if (!response.ok) throw new Error(`Export failed (${response.status})`);
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `cyphertempre-backup-${Date.now()}.zip`;
          a.click();
          URL.revokeObjectURL(url);
          if (els.setup) els.setup.textContent = 'Backup zip downloaded.';
        } catch (err) {
          if (els.setup) els.setup.textContent = err.message || 'Export failed';
        }
      });
    }
    if (els.restoreBackup) {
      els.restoreBackup.addEventListener('change', async () => {
        const file = els.restoreBackup.files && els.restoreBackup.files[0];
        if (!file) return;
        try {
          const token = localStorage.getItem('ct_auth_token') || '';
          const buf = await file.arrayBuffer();
          const response = await fetch('/api/backup/restore?mode=merge', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
              'Content-Type': 'application/zip',
              ...(token ? { Authorization: `Bearer ${token}` } : {})
            },
            body: buf
          });
          const data = await response.json();
          if (!data.ok) throw new Error(data.error || 'Restore failed');
          if (els.setup) els.setup.textContent = `Restored ${data.restored_files || 0} files. Reload recommended.`;
          await loadSessions();
          await restoreHistory();
          await refreshTrustStrip();
        } catch (err) {
          if (els.setup) els.setup.textContent = err.message || 'Restore failed';
        } finally {
          els.restoreBackup.value = '';
        }
      });
    }
    async function setSessionMode(mode) {
      const objective = (els.projectObjective?.value || '').trim();
      const data = await api('/api/session/project', {
        method: 'POST',
        body: JSON.stringify({ session: activeSession, mode, objective })
      });
      if (els.setup) {
        els.setup.textContent = mode === 'project'
          ? `Project mode on: ${data.objective || objective}`
          : 'Session marked as normal chat.';
      }
    }
    if (els.makeProjectSession) {
      els.makeProjectSession.addEventListener('click', async () => {
        try { await setSessionMode('project'); } catch (err) {
          if (els.setup) els.setup.textContent = err.message || 'Could not set project mode';
        }
      });
    }
    if (els.makeChatSession) {
      els.makeChatSession.addEventListener('click', async () => {
        try { await setSessionMode('chat'); } catch (err) {
          if (els.setup) els.setup.textContent = err.message || 'Could not set chat mode';
        }
      });
    }

    // --- Command palette (Ctrl/Cmd+K) ---
    let paletteIndex = 0;
    let paletteItems = [];
    function paletteCommands() {
      return [
        { id: 'new-session', label: 'New session', hint: 'Create conversation', run: async () => {
          const name = prompt('Session name', `Session ${new Date().toLocaleString()}`);
          if (!name) return;
          const data = await api('/api/sessions', { method: 'POST', body: JSON.stringify({ name }) });
          await switchSession(data.session.id);
        }},
        { id: 'focus-composer', label: 'Focus composer', hint: 'Type a message', run: () => els.message?.focus() },
        { id: 'recall', label: 'Open recall', hint: 'Search sealed memory', run: () => {
          document.querySelector('[data-panel="recall"]')?.classList.add('expanded');
          els.recallQuery?.focus();
        }},
        { id: 'verify', label: 'Verify chain', hint: 'Tamper-evidence check', run: () => verifyChain() },
        { id: 'trust', label: 'Refresh trust strip', hint: 'Skill / verify / seal', run: () => refreshTrustStrip() },
        { id: 'settings', label: 'Open settings', hint: 'Provider & product prefs', run: () => {
          document.getElementById('nav-settings')?.click();
        }},
        { id: 'toggle-shared', label: 'Toggle shared memory', hint: 'Composer checkbox', run: () => {
          if (els.sharedMemoryToggle) {
            els.sharedMemoryToggle.checked = !els.sharedMemoryToggle.checked;
          }
        }},
        { id: 'export', label: 'Export backup', hint: 'Download zip', run: () => els.exportBackup?.click() },
        { id: 'project', label: 'Mark session as project', hint: 'Uses objective field', run: async () => {
          document.getElementById('nav-settings')?.click();
          els.projectObjective?.focus();
        }},
        { id: 'task-note', label: 'Seal project progress note', hint: 'Project sessions only', run: async () => {
          const note = prompt('Progress note to seal on the task chain');
          if (!note) return;
          const data = await api('/api/session/task-progress', {
            method: 'POST',
            body: JSON.stringify({ session: activeSession, note })
          });
          if (els.setup) els.setup.textContent = data.ok ? `Task note sealed (ring ${data.task_ring})` : (data.error || 'Failed');
        }},
        { id: 'guide', label: 'Open guide', hint: 'Architecture help', run: () => document.getElementById('nav-guide')?.click() },
        { id: 'reload-history', label: 'Reload history', hint: 'From sealed rings', run: () => restoreHistory() },
      ];
    }
    function renderPalette(filter = '') {
      const q = filter.trim().toLowerCase();
      paletteItems = paletteCommands().filter(cmd =>
        !q || cmd.label.toLowerCase().includes(q) || cmd.hint.toLowerCase().includes(q) || cmd.id.includes(q)
      );
      paletteIndex = 0;
      if (!els.commandPaletteList) return;
      els.commandPaletteList.innerHTML = paletteItems.map((cmd, i) => `
        <div class="command-palette-item ${i === 0 ? 'active' : ''}" data-idx="${i}">
          <span>${esc(cmd.label)}</span>
          <span class="hint">${esc(cmd.hint)}</span>
        </div>
      `).join('') || `<div class="command-palette-item"><span>No matches</span></div>`;
      els.commandPaletteList.querySelectorAll('.command-palette-item[data-idx]').forEach(node => {
        node.addEventListener('click', () => runPaletteItem(Number(node.dataset.idx)));
      });
    }
    function openPalette() {
      if (!els.commandPalette) return;
      els.commandPalette.classList.add('open');
      els.commandPalette.setAttribute('aria-hidden', 'false');
      if (els.commandPaletteInput) {
        els.commandPaletteInput.value = '';
        els.commandPaletteInput.focus();
      }
      renderPalette('');
    }
    function closePalette() {
      if (!els.commandPalette) return;
      els.commandPalette.classList.remove('open');
      els.commandPalette.setAttribute('aria-hidden', 'true');
    }
    async function runPaletteItem(idx) {
      const cmd = paletteItems[idx];
      closePalette();
      if (!cmd) return;
      try { await cmd.run(); } catch (err) {
        if (els.setup) els.setup.textContent = err.message || 'Command failed';
      }
    }
    if (els.commandPaletteInput) {
      els.commandPaletteInput.addEventListener('input', () => renderPalette(els.commandPaletteInput.value));
      els.commandPaletteInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { e.preventDefault(); closePalette(); return; }
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          paletteIndex = Math.min(paletteIndex + 1, Math.max(0, paletteItems.length - 1));
          els.commandPaletteList?.querySelectorAll('.command-palette-item').forEach((n, i) => n.classList.toggle('active', i === paletteIndex));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          paletteIndex = Math.max(paletteIndex - 1, 0);
          els.commandPaletteList?.querySelectorAll('.command-palette-item').forEach((n, i) => n.classList.toggle('active', i === paletteIndex));
        } else if (e.key === 'Enter') {
          e.preventDefault();
          runPaletteItem(paletteIndex);
        }
      });
    }
    if (els.commandPalette) {
      els.commandPalette.addEventListener('click', (e) => {
        if (e.target === els.commandPalette) closePalette();
      });
    }
    document.addEventListener('keydown', (e) => {
      const key = (e.key || '').toLowerCase();
      if ((e.ctrlKey || e.metaKey) && key === 'k') {
        e.preventDefault();
        if (els.commandPalette?.classList.contains('open')) closePalette();
        else openPalette();
      }
    });

    els.recallForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const query = els.recallQuery.value.trim();
      if (!query) return;
      els.recallResults.textContent = 'Searching...';
      try {
        const data = await api('/api/recall', {
          method: 'POST',
          body: JSON.stringify({ query, session: activeSession, domain: els.domain.value === 'auto' ? '' : els.domain.value, limit: 12 })
        });
        const factText = data.facts?.length
          ? data.facts.map(f => `fact ${f.key}=${f.value} confidence=${f.confidence} source=#${f.source_ring} score=${f.score}`).join('\n')
          : 'No durable fact hits.';
        const ringText = data.rings?.length
          ? data.rings.map(r => {
              const revived = r.revived ? ' revived' : '';
              const age = r.relative_time ? ` ${r.relative_time}` : '';
              return `#${r.n} score=${r.score} brightness=${r.brightness} ${r.domain}${age}${revived}\n${r.content}`;
            }).join('\n\n')
          : 'No matching rings.';
        const diagnostics = data.diagnostics?.length ? data.diagnostics.join(' | ') : 'No diagnostics.';
        els.recallResults.textContent = `Durable facts\n${factText}\n\nRings\n${ringText}\n\nDiagnostics\n${diagnostics}`;
      } catch (error) {
        els.recallResults.textContent = error.message;
      }
    });

    els.verify.addEventListener('click', () => {
      els.verifyResult.textContent = 'Checking...';
      verifyChain().catch(error => { els.verifyResult.textContent = error.message; });
    });
    els.resetChain.addEventListener('click', () => {
      resetChainMemory().catch(error => { els.verifyResult.textContent = error.message; });
    });
    els.refreshWorkbench.addEventListener('click', () => {
      refreshWorkbench().catch(error => { els.cambiumResults.textContent = error.message; });
    });
    els.copySyncSnapshot.addEventListener('click', () => {
      copySyncSnapshot().catch(error => { els.cambiumResults.textContent = error.message; });
    });
    els.runDream.addEventListener('click', () => {
      runDream().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    els.saveOverlay.addEventListener('click', () => {
      saveOverlay().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    els.runMemorySync.addEventListener('click', () => {
      runMemorySync().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    els.runFleetImport.addEventListener('click', () => {
      runFleetImport().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    els.runChallenge.addEventListener('click', () => {
      runChallenge().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    if (els.searchSharedMemory) els.searchSharedMemory.addEventListener('click', () => {
      searchSharedMemory().catch(error => { els.sharedMemoryResults.textContent = error.message; });
    });
    if (els.importSharedMemory) els.importSharedMemory.addEventListener('click', () => {
      importSharedMemory().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    if (els.synthesizeSharedMemory) els.synthesizeSharedMemory.addEventListener('click', () => {
      synthesizeSharedMemory().catch(error => { els.advancedTimechainResults.textContent = error.message; });
    });
    document.querySelector('.inspector')?.addEventListener('click', (event) => {
      const button = event.target.closest('[data-action][data-id]');
      if (!button) return;
      const action = button.dataset.action;
      const id = button.dataset.id;
      let memory = null;
      if (action === 'edit') {
        const card = button.closest('.memory-card');
        const current = card?.querySelector('strong')?.textContent?.split(':').slice(1).join(':').trim() || '';
        const value = window.prompt('Memory value', current);
        if (value === null) return;
        memory = { value };
      }
      updateMemory(id, action, memory).catch(error => { els.verifyResult.textContent = error.message; });
    });

    els.persona.addEventListener('change', () => { updatePersonaText(); saveLocalConfig(); validatePersonaModel(); });
    els.provider.addEventListener('change', () => {
      if (providerEndpoints[els.provider.value]) els.baseUrl.value = providerEndpoints[els.provider.value];
      // Immediately switch model list + default to what this provider supports.
      updateChatModelOptions({ forceDefault: true });
      updateSetup();
      saveLocalConfig();
      refreshProviderModels(els.provider.value, true, 'chat')
        .then(() => updateChatModelOptions())
        .catch(error => setStatusDetail(error.message));
    });
    els.model.addEventListener('input', () => { updateSetup(); saveLocalConfig(); validatePersonaModel(); });
    els.apiKey.addEventListener('input', () => { updateSetup(); saveLocalConfig(); });
    if (els.baseUrl) els.baseUrl.addEventListener('input', saveLocalConfig);
    els.testProvider.addEventListener('click', () => {
      testProvider().catch(error => { setStatus(error.message, '#6b3c3c'); });
    });
    if (els.audioTestProvider) els.audioTestProvider.addEventListener('click', () => {
      testAudioProvider().catch(error => { setStatus(error.message, '#6b3c3c'); });
    });
    if (els.clearProviderOverride) els.clearProviderOverride.addEventListener('click', clearProviderOverride);
    els.domain.addEventListener('change', saveLocalConfig);

    // New modality-specific provider fields
    const refreshProviderSummary = () => updateEffectiveProviderSummary();

    if (els.imageProvider) {
      els.imageProvider.addEventListener('change', () => {
        updateImageModelOptions({ forceDefault: true });
        updateImageEditModelOptions({ forceDefault: true });
        saveLocalConfig();
        refreshProviderSummary();
        refreshProviderModels(els.imageProvider.value, true, 'image')
          .then(() => {
            updateImageModelOptions();
            updateImageEditModelOptions();
          })
          .catch(error => {
            updateImageModelOptions();
            updateImageEditModelOptions();
            if (els.imageModelHint) {
              const n = (imageModelsByProvider[els.imageProvider.value] || []).length;
              els.imageModelHint.textContent = n
                ? `Using ${n} curated image model(s). Live catalog: ${error.message || error}`
                : (error.message || String(error));
            }
          });
      });
    }
    if (els.imageModel) {
      els.imageModel.addEventListener('change', () => {
        const selected = els.imageModel.value?.trim() || '';
        const prov = els.imageProvider?.value || '';
        const editList = imageEditModelsByProvider[prov] || [];
        if (selected && editList.includes(selected)) {
          setSelectValue(els.imagegenEditModel, selected);
          localStorage.setItem('ct_image_edit_model', selected);
        }
        syncCreativeStudioModelsFromSettings();
        saveLocalConfig();
        refreshProviderSummary();
      });
    }
    let imageModelDiscoveryTimer = null;
    if (els.imageApiKey) els.imageApiKey.addEventListener('input', () => {
      saveLocalConfig();
      refreshProviderSummary();
      if (imageModelDiscoveryTimer) clearTimeout(imageModelDiscoveryTimer);
      imageModelDiscoveryTimer = setTimeout(() => {
        imageModelDiscoveryTimer = null;
        discoveredModelProviders.delete(els.imageProvider?.value || 'surplusintelligence');
        refreshProviderModels(els.imageProvider?.value || 'surplusintelligence', true, 'image').catch(() => null);
      }, 500);
    });
    if (els.imageBaseUrl) els.imageBaseUrl.addEventListener('input', () => {
      saveLocalConfig();
      refreshProviderSummary();
    });

    if (els.videoProvider) {
      els.videoProvider.addEventListener('change', () => {
        // Always rebind the model select to this provider first (curated/default).
        updateVideoModelOptions({ forceDefault: true });
        saveLocalConfig();
        refreshProviderSummary();
        refreshProviderModels(els.videoProvider.value, true, 'video')
          .then(() => updateVideoModelOptions())
          .catch(error => {
            updateVideoModelOptions();
            if (els.videoModelHint) {
              const n = (videoModelsByProvider[els.videoProvider.value] || []).length;
              els.videoModelHint.textContent = n
                ? `Using ${n} curated video model(s). Live catalog: ${error.message || error}`
                : (error.message || String(error));
            }
          });
      });
    }
    if (els.videoModel) {
      els.videoModel.addEventListener('change', () => {
        syncCreativeStudioModelsFromSettings();
        saveLocalConfig();
        refreshProviderSummary();
      });
    }
    if (els.videoApiKey) els.videoApiKey.addEventListener('input', () => {
      saveLocalConfig();
      refreshProviderSummary();
    });
    if (els.audioProvider) els.audioProvider.addEventListener('change', () => {
      updateAudioModelOptions();
      saveLocalConfig();
      refreshProviderSummary();
      refreshProviderModels(els.audioProvider.value, true, 'audio')
        .then(() => updateAudioModelOptions())
        .catch(error => {
          updateAudioModelOptions();
          setStatusDetail(error.message);
        });
    });

    // Also refresh summary when main chat provider changes
    if (els.provider) els.provider.addEventListener('change', refreshProviderSummary);
    if (els.model) els.model.addEventListener('input', refreshProviderSummary);


    if (els.navChat) els.navChat.addEventListener('click', () => setMainView('chat'));
    if (els.navGuide) els.navGuide.addEventListener('click', () => setMainView('guide'));
    if (els.navSettings) els.navSettings.addEventListener('click', () => setMainView('settings'));
    if (els.settingsProviderTab) els.settingsProviderTab.addEventListener('click', () => setSettingsSection('provider'));
    if (els.settingsPersonaTab) els.settingsPersonaTab.addEventListener('click', () => setSettingsSection('persona'));
    if (els.settingsManageTab) els.settingsManageTab.addEventListener('click', () => setSettingsSection('manage'));
    if (els.settingsWorkbenchTab) els.settingsWorkbenchTab.addEventListener('click', () => setSettingsSection('workbench'));
    if (els.mobChat) els.mobChat.addEventListener('click', () => setMainView('chat'));
    if (els.mobGuide) els.mobGuide.addEventListener('click', () => setMainView('guide'));
    if (els.mobSettings) els.mobSettings.addEventListener('click', () => setMainView('settings'));
    if (els.guideSimple) els.guideSimple.addEventListener('click', () => setGuideDepth('simple'));
    if (els.guideComprehensive) els.guideComprehensive.addEventListener('click', () => setGuideDepth('comprehensive'));
    if (els.generatePersona) els.generatePersona.addEventListener('click', () => {
      createPersona().catch(error => { if (els.setup) els.setup.textContent = error.message; });
    });
    if (els.sessionList) els.sessionList.addEventListener('change', () => {
      switchSession(els.sessionList.value).catch(error => { if (els.setup) els.setup.textContent = error.message; });
    });
    if (els.sessionChips) {
      els.sessionChips.addEventListener('click', (event) => {
        const chip = event.target.closest('.session-chip');
        if (!chip) return;
        const sessionId = chip.getAttribute('data-session-id');
        if (!sessionId || sessionId === activeSession) return;
        switchSession(sessionId).catch(error => { els.setup.textContent = error.message; });
      });
    }
    els.newSession.addEventListener('click', () => {
      createSession().catch(error => { els.setup.textContent = error.message; });
    });
    // Prompt pills (empty state) — event delegation survives re-renders
    if (els.messages) {
      els.messages.addEventListener('click', (event) => {
        const pill = event.target.closest('.prompt-pill');
        if (!pill) return;
        event.preventDefault();
        applyPromptPill(pill.getAttribute('data-prompt') || pill.dataset.prompt || '');
      });
    }
    els.manageSessionSelect.addEventListener('change', () => {
      activeSession = els.manageSessionSelect.value || 'default';
      localStorage.setItem('ct_active_session', activeSession);
      switchSession(activeSession).catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    if (els.manageRenameSession) els.manageRenameSession.addEventListener('click', () => {
      renameSelectedSession().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.managePersonaSelect.addEventListener('change', loadSelectedManagePersona);
    els.manageFreeze.addEventListener('click', () => {
      toggleFreeze().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.manageRewind.addEventListener('click', () => {
      rewindActiveSession().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.manageDeleteSession.addEventListener('click', () => {
      deleteSelectedSession().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.manageSavePersona.addEventListener('click', () => {
      saveManagedPersona().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.manageDeletePersona.addEventListener('click', () => {
      deleteManagedPersona().catch(error => { els.manageStatusDetail.textContent = error.message; });
    });
    els.sessionName.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        createSession().catch(error => { els.setup.textContent = error.message; });
      }
    });
    els.message.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        els.form.requestSubmit();
      }
    });

    // Auth
    function showAuth() {
      if (els.authOverlay) els.authOverlay.classList.remove('hidden');
    }
    function hideAuth() {
      if (els.authOverlay) els.authOverlay.classList.add('hidden');
    }
    function setAuthTab(tab) {
      const isLogin = tab === 'login';
      els.authTabLogin?.classList.toggle('active', isLogin);
      els.authTabRegister?.classList.toggle('active', !isLogin);
      els.authLoginForm?.classList.toggle('hidden', !isLogin);
      els.authRegisterForm?.classList.toggle('hidden', isLogin);
      if (els.authMessage) els.authMessage.textContent = '';
    }
    async function checkAuth() {
      try {
        const data = await api('/api/auth/me');
        if (data.user) {
          currentUser = data.user;
          updateAccountUI();
          hideAuth();
          return true;
        }
      } catch {
        // not logged in
      }
      currentUser = null;
      updateAccountUI();
      showAuth();
      return false;
    }
    function updateAccountUI() {
      if (!currentUser) {
        if (els.accountBtn) els.accountBtn.style.display = 'none';
        if (els.settingsCreatorTab) els.settingsCreatorTab.classList.add('hidden');
        return;
      }
      if (els.accountBtn) {
        els.accountBtn.style.display = 'inline-flex';
        els.accountName.textContent = currentUser.display_name || currentUser.username;
      }
      if (els.accountRole) els.accountRole.textContent = currentUser.role;
      if (els.settingsCreatorTab) {
        els.settingsCreatorTab.classList.toggle('hidden', currentUser.role !== 'creator' && currentUser.role !== 'admin');
      }
    }
    async function login() {
      if (els.authMessage) els.authMessage.textContent = '';
      try {
        const data = await api('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ username: els.authLoginUser.value, password: els.authLoginPass.value })
        });
        currentUser = data.user;
        localStorage.setItem('ct_auth_token', data.token || '');
        updateAccountUI();
        hideAuth();
        els.authLoginUser.value = '';
        els.authLoginPass.value = '';
        // Full app boot — login previously skipped this, leaving "Workspace loading..." stuck.
        await bootAuthenticatedApp();
      } catch (error) {
        if (els.authMessage) els.authMessage.textContent = error.message;
      }
    }
    async function register() {
      if (els.authMessage) els.authMessage.textContent = '';
      try {
        const data = await api('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            username: els.authRegUser.value,
            display_name: els.authRegDisplay.value,
            password: els.authRegPass.value
          })
        });
        currentUser = data.user;
        localStorage.setItem('ct_auth_token', data.token || '');
        updateAccountUI();
        hideAuth();
        els.authRegUser.value = '';
        els.authRegDisplay.value = '';
        els.authRegPass.value = '';
        await bootAuthenticatedApp();
      } catch (error) {
        if (els.authMessage) els.authMessage.textContent = error.message;
      }
    }
    async function logout() {
      try { await api('/api/auth/logout', { method: 'POST', body: '{}' }); } catch {}
      localStorage.removeItem('ct_auth_token');
      currentUser = null;
      updateAccountUI();
      showAuth();
      if (els.accountMenu) els.accountMenu.classList.remove('open');
    }

    // Marketplace
    function setMainView(view) {
      if (view === 'forge') view = 'imagegen';
      const prevView = currentMainView;
      const guide = view === 'guide';
      const settings = view === 'settings';
      const marketplace = view === 'marketplace';
      const imagegen = view === 'imagegen';
      const videogen = view === 'videogen';
      const audiogen = view === 'audiogen';
      const switched = prevView !== view;

      if (els.chatView) els.chatView.classList.toggle('hidden', guide || settings || marketplace || imagegen || videogen || audiogen);
      if (els.guideView) els.guideView.classList.toggle('active', guide);
      if (els.settingsView) els.settingsView.classList.toggle('active', settings);
      if (els.marketplaceView) els.marketplaceView.classList.toggle('active', marketplace);
      if (els.imagegenView) els.imagegenView.classList.toggle('hidden', !imagegen);
      if (els.videogenView) els.videogenView.classList.toggle('hidden', !videogen);
      if (els.audiogenView) els.audiogenView.classList.toggle('hidden', !audiogen);

      if (els.navChat) els.navChat.classList.toggle('active', !guide && !settings && !marketplace && !imagegen && !videogen && !audiogen);
      if (els.navGuide) els.navGuide.classList.toggle('active', guide);
      if (els.navSettings) els.navSettings.classList.toggle('active', settings);
      if (els.navMarketplace) els.navMarketplace.classList.toggle('active', marketplace);
      if (els.navImagegen) els.navImagegen.classList.toggle('active', imagegen);
      if (els.navVideogen) els.navVideogen.classList.toggle('active', videogen);
      if (els.navAudiogen) els.navAudiogen.classList.toggle('active', audiogen);

      if (els.mobChat) els.mobChat.classList.toggle('active', !guide && !settings && !marketplace && !imagegen && !audiogen);
      if (els.mobGuide) els.mobGuide.classList.toggle('active', guide);
      if (els.mobSettings) els.mobSettings.classList.toggle('active', settings);
      if (els.mobMarketplace) els.mobMarketplace.classList.toggle('active', marketplace);
      if (els.mobImagegen) els.mobImagegen.classList.toggle('active', imagegen);
      if (els.mobVideogen) els.mobVideogen.classList.toggle('active', videogen);

      currentMainView = view;
      localStorage.setItem('ct_view', view);

      if (switched) {
        try {
          const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          if (!reduceMotion) animateViewEnter(getViewElement(view));
        } catch (_) { /* ignore animation errors */ }
      }

      // Fire-and-forget studio loads — never block nav chrome on network/API.
      if (marketplace) Promise.resolve().then(() => loadMarketplace()).catch(() => null);
      if (imagegen) Promise.resolve().then(() => loadImagegen()).catch(() => null);
      if (videogen) Promise.resolve().then(() => loadVideogen()).catch(() => null);
    }
    async function loadMarketplace() {
      if (!els.marketplaceGrid) return;
      els.marketplaceGrid.innerHTML = '<div style="color:var(--muted);padding:20px 0;">Loading marketplace...</div>';
      try {
        const data = await api('/api/marketplace');
        marketplaceData = data.personas || [];
        renderMarketplace();
      } catch (error) {
        els.marketplaceGrid.innerHTML = `<div style="color:var(--red);padding:20px 0;">${esc(error.message)}</div>`;
      }
    }
    function renderMarketplace() {
      const filter = document.querySelector('.filter-pill.active')?.dataset.filter || 'all';
      const query = (els.mpSearch?.value || '').toLowerCase().trim();
      let items = marketplaceData;
      if (filter === 'free') items = items.filter(p => p.price?.model === 'free');
      if (filter === 'premium') items = items.filter(p => p.price?.model !== 'free');
      if (filter === 'subscribed') items = items.filter(p => p.is_subscribed);
      if (query) {
        items = items.filter(p =>
          (p.name || '').toLowerCase().includes(query) ||
          (p.tagline || '').toLowerCase().includes(query) ||
          (p.domain || '').toLowerCase().includes(query)
        );
      }
      if (!items.length) {
        els.marketplaceGrid.innerHTML = '<div style="color:var(--muted);padding:20px 0;">No personas found.</div>';
        return;
      }
      els.marketplaceGrid.innerHTML = items.map((p, index) => {
        const isFree = p.price?.model === 'free';
        const priceLabel = isFree ? 'Free' : `$${p.price?.amount}`;
        const priceClass = isFree ? 'free' : 'premium';
        const mass = p.stats?.temporal_mass || 0;
        const subs = p.stats?.subscribers || 0;
        const stagger = Math.min(index, 12);
        return `
          <article class="persona-card" data-id="${esc(p.persona_id)}" style="--stagger:${stagger}" tabindex="0" role="button" aria-label="Open ${esc(p.name || 'persona')}">
            <div class="persona-card-header">
              <span class="domain-badge"><span class="domain-dot"></span>${esc(p.domain || 'general')}</span>
              <span class="price-badge ${priceClass}">${esc(priceLabel)}</span>
            </div>
            <h3>${esc(p.name)}</h3>
            <p class="tagline">${esc(p.tagline || 'No description.')}</p>
            <div class="persona-card-meta">
              <span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg> ${subs}</span>
              <span><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"></path></svg> ${Math.round(mass * 10) / 10} mass</span>
            </div>
          </article>
        `;
      }).join('');
      els.marketplaceGrid.querySelectorAll('.persona-card').forEach(card => {
        const open = () => openDetail(card.dataset.id);
        card.addEventListener('click', open);
        card.addEventListener('keydown', (event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            open();
          }
        });
      });
    }
    async function openDetail(personaId) {
      currentDetailId = personaId;
      if (els.detailDrawer) els.detailDrawer.classList.add('open');
      try {
        const data = await api(`/api/marketplace/${encodeURIComponent(personaId)}`);
        const p = data.persona;
        if (els.detailName) els.detailName.textContent = p.name || 'Untitled';
        if (els.detailDomainText) els.detailDomainText.textContent = p.domain || 'general';
        if (els.detailTagline) els.detailTagline.textContent = p.tagline || 'No description.';
        const mass = p.capsule?.temporal_mass || 0;
        if (els.detailMassValue) els.detailMassValue.textContent = Math.round(mass * 10) / 10;
        if (els.detailMassBar) els.detailMassBar.style.width = Math.min(100, mass * 5) + '%';
        const domains = p.capsule?.top_domains || [];
        const ringCount = p.capsule?.ring_count ?? (p.capsule?.rings || []).length;
        if (els.detailCapsule) {
          els.detailCapsule.innerHTML = ringCount
            ? `
              <div style="border:1px solid var(--line-soft);border-radius:8px;padding:10px;background:var(--memory-card-bg);">
                <div style="font-size:12px;color:var(--faint);margin-bottom:4px;">Frozen capsule</div>
                <div style="font-size:13px;color:var(--muted);line-height:1.45;">
                  ${esc(ringCount)} accepted rings available for persona recall. Prior conversation is hidden.
                </div>
              </div>
              ${domains.length ? `<div style="font-size:12px;color:var(--faint);">Domains: ${esc(domains.join(', '))}</div>` : ''}
            `
            : '<div style="color:var(--muted);font-size:13px;">No frozen capsule yet.</div>';
        }
        const isSubbed = p.is_subscribed;
        if (els.detailSubscribe) {
          els.detailSubscribe.style.display = isSubbed ? 'none' : 'block';
          els.detailSubscribe.textContent = p.price?.model === 'free' ? 'Subscribe Free' : `Subscribe — $${p.price?.amount}`;
          els.detailSubscribe.disabled = false;
        }
        if (els.detailUnsubscribe) {
          els.detailUnsubscribe.style.display = isSubbed ? 'block' : 'none';
        }
        if (els.detailSubHint) els.detailSubHint.textContent = isSubbed ? 'You already have access to this persona.' : '';
      } catch (error) {
        if (els.detailTagline) els.detailTagline.textContent = error.message;
      }
    }
    async function doSubscribe() {
      if (!currentDetailId || !currentUser) return;
      try {
        const data = await api(`/api/marketplace/${encodeURIComponent(currentDetailId)}/subscribe`, { method: 'POST', body: '{}' });
        if (els.detailSubscribe) els.detailSubscribe.style.display = 'none';
        if (els.detailUnsubscribe) els.detailUnsubscribe.style.display = 'block';
        if (els.detailSubHint) els.detailSubHint.textContent = 'Subscribed successfully.';
        loadMarketplace();
      } catch (error) {
        if (els.detailSubHint) els.detailSubHint.textContent = error.message;
      }
    }
    async function doUnsubscribe() {
      if (!currentDetailId || !currentUser) return;
      try {
        const data = await api(`/api/marketplace/${encodeURIComponent(currentDetailId)}/unsubscribe`, { method: 'POST', body: '{}' });
        if (els.detailSubscribe) els.detailSubscribe.style.display = 'block';
        if (els.detailUnsubscribe) els.detailUnsubscribe.style.display = 'none';
        if (els.detailSubHint) els.detailSubHint.textContent = 'Unsubscribed.';
        loadMarketplace();
      } catch (error) {
        if (els.detailSubHint) els.detailSubHint.textContent = error.message;
      }
    }
    function closeDetail() {
      if (els.detailDrawer) els.detailDrawer.classList.remove('open');
      currentDetailId = null;
    }

    // Creator
    function setSettingsSection(section) {
      const active = ['provider', 'persona', 'manage', 'workbench', 'creator'].includes(section) ? section : 'provider';
      els.providerSettingsSection.classList.toggle('hidden', active !== 'provider');
      els.personaSettingsSection.classList.toggle('hidden', active !== 'persona');
      els.manageSettingsSection.classList.toggle('hidden', active !== 'manage');
      els.workbenchSettingsSection.classList.toggle('hidden', active !== 'workbench');
      els.creatorSettingsSection.classList.toggle('hidden', active !== 'creator');
      els.settingsProviderTab.classList.toggle('active', active === 'provider');
      els.settingsPersonaTab.classList.toggle('active', active === 'persona');
      els.settingsManageTab.classList.toggle('active', active === 'manage');
      els.settingsWorkbenchTab.classList.toggle('active', active === 'workbench');
      els.settingsCreatorTab.classList.toggle('active', active === 'creator');
      localStorage.setItem('ct_settings_section', active);
      if (active === 'creator') loadCreatorPersonas();
      if (active === 'provider') {
        // Restore last used provider sub-tab (chat/image/video)
        const lastSub = localStorage.getItem('ct_provider_subtab') || 'chat';
        setProviderSubtab(lastSub);
        updateEffectiveProviderSummary();
      }
    }

    // Switch between Chat / Image / Video / Audio provider sub-views
    function setProviderSubtab(subtab) {
      const valid = ['chat', 'image', 'video', 'audio'];
      if (!valid.includes(subtab)) subtab = 'chat';

      const sections = {
        chat: document.getElementById('provider-sub-chat'),
        image: document.getElementById('provider-sub-image'),
        video: document.getElementById('provider-sub-video'),
        audio: document.getElementById('provider-sub-audio')
      };

      Object.keys(sections).forEach(key => {
        const el = sections[key];
        if (el) el.classList.toggle('hidden', key !== subtab);
      });

      // Update active state on sub-tab buttons
      document.querySelectorAll('.provider-subtab').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.subtab === subtab);
        btn.setAttribute('aria-selected', btn.dataset.subtab === subtab);
      });

      localStorage.setItem('ct_provider_subtab', subtab);

      // Refresh model options when switching to Image or Video
      if (subtab === 'image') updateImageModelOptions();
      if (subtab === 'video') updateVideoModelOptions();
    }

    function normalizeAudioModel(value) {
      const model = String(value || '').trim();
      if (!model || model === 'tts-1') return 'tts-kokoro';
      return model;
    }

    // Compute and display the effective provider configuration (with fallbacks)
    function updateEffectiveProviderSummary() {
      const chatProv = els.provider?.value || localStorage.getItem('ct_provider') || 'morpheus';
      const chatModel = els.model?.value?.trim() || localStorage.getItem('ct_model') || 'gemma-4-uncensored';

      const imageProv = els.imageProvider?.value || localStorage.getItem('ct_image_provider') || chatProv;
      const imageModel = els.imageModel?.value?.trim() || localStorage.getItem('ct_image_model') || imageProviderDefaults[imageProv] || '—';

      const videoProv = els.videoProvider?.value || localStorage.getItem('ct_video_provider') || chatProv;
      const videoModel = els.videoModel?.value?.trim() || localStorage.getItem('ct_video_model') || videoProviderDefaults[videoProv] || '—';

      const chatEl = document.getElementById('effective-chat');
      const imageEl = document.getElementById('effective-image');
      const videoEl = document.getElementById('effective-video');

      if (chatEl) chatEl.textContent = `${chatProv} · ${chatModel}`;
      if (imageEl) {
        const isFallback = imageProv === chatProv && !localStorage.getItem('ct_image_provider');
        imageEl.textContent = isFallback 
          ? `${imageProv} · ${imageModel} (using Chat)` 
          : `${imageProv} · ${imageModel}`;
      }
      if (videoEl) {
        const isFallback = videoProv === chatProv && !localStorage.getItem('ct_video_provider');
        videoEl.textContent = isFallback 
          ? `${videoProv} · ${videoModel} (using Chat)` 
          : `${videoProv} · ${videoModel}`;
      }
    }
    async function loadCreatorPersonas() {
      if (!els.creatorList || !currentUser) return;
      els.creatorList.innerHTML = '<div style="color:var(--muted);font-size:13px;">Loading...</div>';
      renderCreatorSourceSessions();
      try {
        const data = await api('/api/creator/personas');
        const personas = data.personas || [];
        if (!personas.length) {
          els.creatorList.innerHTML = '<div style="color:var(--muted);font-size:13px;">No personas created yet.</div>';
          return;
        }
        els.creatorList.innerHTML = personas.map(p => {
          const statusClass = `status-${p.status || 'draft'}`;
          return `
            <div class="creator-persona-row">
              <div>
                <div style="font-weight:800;font-size:14px;">${esc(p.name)}</div>
                <div style="font-size:12px;color:var(--faint);">${esc(p.domain)} · ${p.rings} rings</div>
              </div>
              <span class="status ${statusClass}">${esc(p.status || 'draft')}</span>
              <button class="secondary" type="button" data-action="rename" data-id="${esc(p.persona_id)}" data-name="${esc(p.name)}">Rename</button>
              <button class="secondary" type="button" data-action="train" data-id="${esc(p.persona_id)}">Train</button>
              <button class="secondary" type="button" data-action="publish" data-id="${esc(p.persona_id)}" data-source="${esc(p.source_session || '')}">Publish</button>
              <button class="secondary danger" type="button" data-action="delete" data-id="${esc(p.persona_id)}" data-name="${esc(p.name)}">Delete</button>
            </div>
          `;
        }).join('');
        els.creatorList.querySelectorAll('button[data-action]').forEach(btn => {
          btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const action = btn.dataset.action;
            if (action === 'train') {
              await trainCreatorPersona(id);
            } else if (action === 'rename') {
              await renameCreatorPersona(id, btn.dataset.name || id);
            } else if (action === 'publish') {
              await publishCreatorPersona(id, btn.dataset.source || '');
            } else if (action === 'delete') {
              await deleteCreatorPersona(id, btn.dataset.name || id);
            }
          });
        });
      } catch (error) {
        els.creatorList.innerHTML = `<div style="color:var(--red);font-size:13px;">${esc(error.message)}</div>`;
      }
    }
    function autoFillCreatorFromSession(sessionId) {
      if (!els.creatorSourceSession) return;
      const session = sessionRows.find(s => s.id === sessionId);
      const pid = session?.persona_id || '';
      const persona = pid ? resolvePersonaById(pid) : null;
      if (!persona) return;
      if (!els.creatorName.value.trim()) els.creatorName.value = persona.name || '';
      if (!els.creatorDomain.value.trim() || els.creatorDomain.value === 'auto') els.creatorDomain.value = persona.domain || 'auto';
      if (!els.creatorSystem.value.trim()) els.creatorSystem.value = persona.system || '';
    }

    function renderCreatorSourceSessions() {
      if (!els.creatorSourceSession) return;
      const rows = sessionRows.length ? sessionRows : [{ id: activeSession, name: session_name_from_id_js(activeSession), rings: 0 }];
      els.creatorSourceSession.innerHTML = rows
        .map(session => `<option value="${esc(session.id)}">${esc(session.name || session.id)} (${session.rings || 0})</option>`)
        .join('');
      els.creatorSourceSession.value = rows.some(session => session.id === activeSession) ? activeSession : rows[0]?.id || 'default';
      autoFillCreatorFromSession(els.creatorSourceSession.value);
    }

    function updateCreatorPriceControls() {
      if (!els.creatorPriceModel || !els.creatorPriceAmount) return;
      const premium = els.creatorPriceModel.value === 'premium';
      els.creatorPriceAmount.classList.toggle('hidden', !premium);
      if (!premium) els.creatorPriceAmount.value = '';
    }

    function creatorPublishPrice() {
      const model = els.creatorPriceModel?.value === 'premium' ? 'premium' : 'free';
      const amount = model === 'premium' ? Math.max(0, Number(els.creatorPriceAmount?.value || 0)) : 0;
      return { model, amount, currency: 'USD' };
    }

    async function saveCreatorPersona() {
      if (!currentUser) return;
      const name = els.creatorName.value.trim();
      if (!name) { els.manageStatusDetail.textContent = 'Name is required.'; return; }
      try {
        await api('/api/creator/personas', {
          method: 'POST',
          body: JSON.stringify({
            persona: {
              name: name,
              tagline: els.creatorTagline.value.trim(),
              domain: els.creatorDomain.value,
              system: els.creatorSystem.value.trim(),
              sourceSession: els.creatorSourceSession?.value || activeSession
            }
          })
        });
        els.creatorName.value = '';
        els.creatorTagline.value = '';
        els.creatorSystem.value = '';
        await loadCreatorPersonas();
        applyLocalConfig(await api('/api/config'));
        els.manageStatusDetail.textContent = 'Persona created.';
      } catch (error) {
        els.manageStatusDetail.textContent = error.message;
      }
    }
    async function trainCreatorPersona(personaId) {
      if (!personaId) return;
      const persona = resolvePersonaById(personaId);
      const existingSessionId = persona?.source_session && sessionRows.some(session => session.id === persona.source_session)
        ? persona.source_session
        : '';
      let sessionId = existingSessionId;
      if (!sessionId) {
        const sessionName = persona?.name || `train-${personaId}`;
        const data = await api('/api/sessions', {
          method: 'POST',
          body: JSON.stringify({ name: sessionName, persona: personaId })
        });
        sessionId = data.session?.id || '';
      }
      if (sessionId) {
        await api('/api/creator/personas', {
          method: 'POST',
          body: JSON.stringify({ id: personaId, persona: { sourceSession: sessionId } })
        });
        await loadCreatorPersonas();
        applyLocalConfig(await api('/api/config'));
        await switchSession(sessionId);
        setMainView('chat');
        els.setup.textContent = `Training mode for ${personaId}. Chat to build temporal mass.`;
      }
    }

    async function renameCreatorPersona(personaId, currentName) {
      if (!personaId) return;
      const name = window.prompt('Rename created persona', currentName || personaId);
      if (!name || !name.trim()) return;
      await api('/api/creator/personas', {
        method: 'POST',
        body: JSON.stringify({ id: personaId, persona: { name: name.trim() } })
      });
      await loadCreatorPersonas();
      applyLocalConfig(await api('/api/config'));
      els.manageStatusDetail.textContent = `Renamed created persona to ${name.trim()}.`;
    }

    async function deleteCreatorPersona(personaId, personaName) {
      if (!personaId) return;
      const ok = window.confirm(`Delete created persona "${personaName || personaId}"? If it was published, its marketplace entry will be archived.`);
      if (!ok) return;
      await api(`/api/creator/personas/${encodeURIComponent(personaId)}/delete`, {
        method: 'POST',
        body: '{}'
      });
      await loadCreatorPersonas();
      applyLocalConfig(await api('/api/config'));
      if (els.persona.value === personaId) els.persona.value = 'companion';
      els.manageStatusDetail.textContent = `Deleted created persona ${personaName || personaId}.`;
    }

    async function publishCreatorPersona(personaId, savedSourceSession = '') {
      if (!personaId) return;
      const sourceSession = creatorPersonas[personaId]?.source_session || savedSourceSession || els.creatorSourceSession?.value || activeSession;
      try {
        await api(`/api/creator/personas/${encodeURIComponent(personaId)}/distill`, {
          method: 'POST',
          body: JSON.stringify({ sourceSession })
        });
        await api(`/api/creator/personas/${encodeURIComponent(personaId)}/publish`, { method: 'POST', body: JSON.stringify({ price: creatorPublishPrice() }) });
        await loadCreatorPersonas();
        applyLocalConfig(await api('/api/config'));
        els.manageStatusDetail.textContent = 'Published to marketplace.';
      } catch (error) {
        els.manageStatusDetail.textContent = error.message;
      }
    }

    // Event listeners for new UI
    if (els.authTabLogin) els.authTabLogin.addEventListener('click', () => setAuthTab('login'));
    if (els.authTabRegister) els.authTabRegister.addEventListener('click', () => setAuthTab('register'));
    if (els.authLoginBtn) els.authLoginBtn.addEventListener('click', login);
    if (els.authRegisterBtn) els.authRegisterBtn.addEventListener('click', register);
    if (els.authLoginUser) els.authLoginUser.addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
    if (els.authLoginPass) els.authLoginPass.addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
    if (els.authRegUser) els.authRegUser.addEventListener('keydown', (e) => { if (e.key === 'Enter') register(); });
    if (els.authRegDisplay) els.authRegDisplay.addEventListener('keydown', (e) => { if (e.key === 'Enter') register(); });
    if (els.authRegPass) els.authRegPass.addEventListener('keydown', (e) => { if (e.key === 'Enter') register(); });
    if (els.accountBtn) els.accountBtn.addEventListener('click', () => els.accountMenu?.classList.toggle('open'));
    if (els.accountLogout) els.accountLogout.addEventListener('click', logout);
    if (els.navMarketplace) els.navMarketplace.addEventListener('click', () => setMainView('marketplace'));
    if (els.mobMarketplace) els.mobMarketplace.addEventListener('click', () => setMainView('marketplace'));
    if (els.navImagegen) els.navImagegen.addEventListener('click', () => setMainView('imagegen'));
    if (els.mobImagegen) els.mobImagegen.addEventListener('click', () => setMainView('imagegen'));
    if (els.navVideogen) els.navVideogen.addEventListener('click', () => setMainView('videogen'));
    if (els.mobVideogen) els.mobVideogen.addEventListener('click', () => setMainView('videogen'));
    if (els.navAudiogen) els.navAudiogen.addEventListener('click', () => setMainView('audiogen'));
    if (els.audiogenGenerateBtn) els.audiogenGenerateBtn.addEventListener('click', audiogenGenerate);
    if (els.audiogenSpeed) els.audiogenSpeed.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      if (els.audiogenSpeedLabel) els.audiogenSpeedLabel.textContent = val.toFixed(2) + 'x';
    });
    if (els.detailClose) els.detailClose.addEventListener('click', closeDetail);
    if (els.detailSubscribe) els.detailSubscribe.addEventListener('click', doSubscribe);
    if (els.detailUnsubscribe) els.detailUnsubscribe.addEventListener('click', doUnsubscribe);
    if (els.mpSearch) els.mpSearch.addEventListener('input', renderMarketplace);
    document.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        renderMarketplace();
      });
    });
    if (els.settingsCreatorTab) els.settingsCreatorTab.addEventListener('click', () => setSettingsSection('creator'));

    // Wire provider sub-tabs (Chat / Image / Video)
    document.querySelectorAll('.provider-subtab').forEach(btn => {
      btn.addEventListener('click', () => {
        const sub = btn.dataset.subtab;
        setProviderSubtab(sub);
      });
    });
    if (els.creatorSave) els.creatorSave.addEventListener('click', saveCreatorPersona);
    if (els.creatorSourceSession) els.creatorSourceSession.addEventListener('change', () => autoFillCreatorFromSession(els.creatorSourceSession.value));
    if (els.creatorPriceModel) els.creatorPriceModel.addEventListener('change', updateCreatorPriceControls);
    updateCreatorPriceControls();
    document.addEventListener('click', (e) => {
      if (!els.accountWrap?.contains(e.target)) {
        els.accountMenu?.classList.remove('open');
      }
      if (!els.detailDrawer?.contains(e.target) && !e.target.closest('.persona-card')) {
        closeDetail();
      }
    });

    (function setupMobileDrawers() {
      const rail = document.querySelector('.rail');
      const inspector = document.querySelector('.inspector');
      const backdrop = document.getElementById('overlay-backdrop');
      const menuToggle = document.getElementById('menu-toggle');
      const inspectorToggle = document.getElementById('inspector-toggle');
      function closeAll() {
        rail && rail.classList.remove('open');
        inspector && inspector.classList.remove('open');
        backdrop && backdrop.classList.remove('active');
      }
      if (menuToggle) menuToggle.addEventListener('click', () => {
        const wasOpen = rail && rail.classList.contains('open');
        closeAll();
        if (!wasOpen) { rail && rail.classList.add('open'); backdrop && backdrop.classList.add('active'); }
      });
      if (inspectorToggle) inspectorToggle.addEventListener('click', () => {
        const wasOpen = inspector && inspector.classList.contains('open');
        closeAll();
        if (!wasOpen) { inspector && inspector.classList.add('open'); backdrop && backdrop.classList.add('active'); }
      });
      if (backdrop) backdrop.addEventListener('click', closeAll);
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(); });
      window.addEventListener('resize', () => { if (window.innerWidth > 760) closeAll(); });
      document.querySelectorAll('.rail .nav button, .rail .secondary, .rail .settings-icon').forEach(btn => {
        btn.addEventListener('click', () => { if (window.innerWidth <= 760) closeAll(); });
      });
      [els.mobChat, els.mobGuide, els.mobSettings, els.mobMarketplace, els.mobImagegen].forEach(btn => {
        if (btn) btn.addEventListener('click', closeAll);
      });
    })();

    // ImageGen Studio
    let imagegenActiveMode = 'generate';
    let imagegenSelectedImageId = '';
    let imagegenBusy = false;
    // imagegenEditSourceId is declared near compressImageForEdit

    function imagegenBypassCheckboxes() {
      return [els.imagegenBypassGenerate, els.imagegenBypassEdit, els.imagegenBypassRedefine].filter(Boolean);
    }

    function syncImagegenBypassCheckboxes(checked) {
      imagegenBypassCheckboxes().forEach(el => { el.checked = checked; });
      localStorage.setItem('ct_imagegen_bypass_prompt', checked ? '1' : '0');
    }

    function restoreImagegenBypassPreference() {
      // Default ON for uncensored editing: exact user prompt, no helper rewrite/filter.
      // Only turn off when the user has explicitly saved '0'.
      const saved = localStorage.getItem('ct_imagegen_bypass_prompt');
      const enabled = saved === null ? true : saved === '1';
      syncImagegenBypassCheckboxes(enabled);
    }

    function imagegenBypassPayload(mode) {
      const map = {
        generate: els.imagegenBypassGenerate,
        edit: els.imagegenBypassEdit,
        redefine: els.imagegenBypassRedefine,
      };
      return { bypass_prompt: !!map[mode]?.checked };
    }

    function setImagegenMode(mode) {
      imagegenActiveMode = mode;
      els.imagegenModeGenerate.classList.toggle('active', mode === 'generate');
      els.imagegenModeEdit.classList.toggle('active', mode === 'edit');
      els.imagegenModeRedefine.classList.toggle('active', mode === 'redefine');
      els.imagegenPanelGenerate.classList.toggle('hidden', mode !== 'generate');
      els.imagegenPanelEdit.classList.toggle('hidden', mode !== 'edit');
      els.imagegenPanelRedefine.classList.toggle('hidden', mode !== 'redefine');
      if (mode === 'redefine') renderImagegenRedefineGallery();
    }

    async function loadImagegen() {
      if (!els.imagegenGalleryGrid) return;
      renderImagegenGallery([]);
      try {
        const data = await api('/api/imagegen/gallery');
        renderImagegenGallery(data.images || []);
      } catch (error) {
        if (els.imagegenGalleryGrid) els.imagegenGalleryGrid.innerHTML = `<div style="color:var(--red);padding:8px;">${esc(error.message)}</div>`;
      }
    }

    function imagegenLineageLabel(item) {
      const mode = item.mode === 'redefine' ? 'Refine' : (item.mode === 'edit' ? 'Edit' : 'Gen');
      const ring = Number(item.ring_n || 0);
      return ring > 0 ? `${mode} v${ring}` : mode;
    }

    function renderImagegenLineage(data) {
      if (!els.imagegenLineage) return;
      if (!data || !data.ok || !data.chain?.length) {
        els.imagegenLineage.classList.add('hidden');
        els.imagegenLineage.innerHTML = '';
        return;
      }
      const chain = [...data.chain].reverse();
      els.imagegenLineage.innerHTML = chain.map((item, index) => {
        const arrow = index ? '<span class="arrow">/</span>' : '';
        return `${arrow}<span class="crumb" title="${esc(item.prompt || '')}">${esc(imagegenLineageLabel(item))}</span>`;
      }).join('');
      els.imagegenLineage.classList.remove('hidden');
    }

    async function loadImagegenLineage(imageId) {
      if (!imageId) {
        renderImagegenLineage(null);
        return;
      }
      try {
        const data = await api(`/api/imagegen/lineage?image_id=${encodeURIComponent(imageId)}`);
        renderImagegenLineage(data);
      } catch {
        renderImagegenLineage(null);
      }
    }

    function renderImagegenGallery(images) {
      if (!els.imagegenGalleryGrid) return;
      if (els.imagegenGalleryCount) els.imagegenGalleryCount.textContent = images.length;
      if (!images.length) {
        renderImagegenLineage(null);
        els.imagegenGalleryGrid.innerHTML = `
          <div class="empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            <div>No images in the archive yet</div>
          </div>`;
        return;
      }
      els.imagegenGalleryGrid.innerHTML = images.map(img => `
        <div class="thumb" data-id="${esc(img.id)}" data-ring="${esc(img.ring_n || '')}" title="${esc(img.prompt)}">
          <img src="/api/imagegen/image/${esc(img.id)}" loading="lazy" alt="${esc(img.prompt)}" data-preview-src="/api/imagegen/image/${esc(img.id)}">
          ${img.ring_n ? `<span class="ring">v${esc(img.ring_n)}</span>` : ''}
          <button class="edit-src" data-id="${esc(img.id)}" title="Edit this image">✎</button>
          <button class="download" data-id="${esc(img.id)}" title="Download">↓</button>
          <button class="del" data-id="${esc(img.id)}" title="Delete">&times;</button>
        </div>
      `).join('');
      els.imagegenGalleryGrid.querySelectorAll('.thumb').forEach(thumb => {
        thumb.addEventListener('click', (e) => {
          if (e.target.classList.contains('del')) {
            e.stopPropagation();
            deleteImagegenImage(thumb.dataset.id);
            return;
          }
          if (e.target.classList.contains('download')) {
            e.stopPropagation();
            downloadImage(`/api/imagegen/image/${thumb.dataset.id}`, `cyphertempre-${thumb.dataset.id}.png`);
            return;
          }
          if (e.target.classList.contains('edit-src')) {
            e.stopPropagation();
            const src = `/api/imagegen/image/${thumb.dataset.id}`;
            useImageAsEditSource(src, { sourceId: thumb.dataset.id, alt: 'Archive image' })
              .catch(error => alert(error.message || 'Could not open image for editing.'));
            return;
          }
          if (e.target.tagName === 'IMG') {
            openImagePreview(e.target.src, e.target.alt);
          }
          imagegenSelectedImageId = thumb.dataset.id;
          renderImagegenRedefineGallery();
          loadImagegenLineage(thumb.dataset.id);
        });
      });
    }

    function renderImagegenRedefineGallery() {
      if (!els.imagegenRedefineGallery) return;
      const thumbs = els.imagegenGalleryGrid?.querySelectorAll('.thumb');
      if (!thumbs || !thumbs.length) {
        els.imagegenRedefineGallery.innerHTML = '<div style="color:var(--muted);font-size:12px;">Generate some images first.</div>';
        imagegenSelectedImageId = '';
        return;
      }
      els.imagegenRedefineGallery.innerHTML = Array.from(thumbs).map(thumb => {
        const id = thumb.dataset.id;
        const src = thumb.querySelector('img')?.src || '';
        return `<div class="thumb ${id === imagegenSelectedImageId ? 'active' : ''}" data-id="${esc(id)}"><img src="${esc(src)}" loading="lazy" alt=""></div>`;
      }).join('');
      els.imagegenRedefineGallery.querySelectorAll('.thumb').forEach(t => {
        t.addEventListener('click', () => {
          imagegenSelectedImageId = t.dataset.id;
          renderImagegenRedefineGallery();
        });
      });
    }

    async function imagegenGenerate() {
      if (imagegenBusy) return;
      const prompt = els.imagegenPrompt?.value?.trim();
      if (!prompt) { els.imagegenStatus.innerHTML = '<span class="imagegen-error" style="display:inline-flex;padding:6px 12px;">Enter a prompt first.</span>'; return; }
      imagegenBusy = true;
      const bypass = imagegenBypassPayload('generate').bypass_prompt;
      els.imagegenStatus.innerHTML = bypass
        ? '<div class="imagegen-spinner"></div><span>Generating with your raw prompt...</span>'
        : '<div class="imagegen-spinner"></div><span>Generating your image...</span>';
      els.imagegenResult.innerHTML = '';
      try {
        const data = await api('/api/imagegen/generate', {
          method: 'POST',
          body: JSON.stringify({
            prompt,
            model: els.imagegenModel?.value,
            aspect_ratio: els.imagegenAspect?.value,
            apiKey: localStorage.getItem('ct_image_api_key') || localStorage.getItem('ct_api_key') || '',
            provider: localStorage.getItem('ct_image_provider') || localStorage.getItem('ct_provider') || 'openrouter',
            baseUrl: localStorage.getItem('ct_image_base_url') || '',
            ...imagegenBypassPayload('generate'),
          })
        });
        els.imagegenStatus.textContent = '';
        els.imagegenResult.innerHTML = renderImageResultCard(data, 'Generate');
        wireImageActions(els.imagegenResult);
        renderImagegenLineage({ ok: true, chain: [data.image] });
        loadImagegen();
      } catch (error) {
        els.imagegenStatus.textContent = '';
        els.imagegenResult.innerHTML = `<div class="imagegen-error">${esc(error.message)}</div>`;
      } finally {
        imagegenBusy = false;
      }
    }

    async function imagegenEdit() {
      if (imagegenBusy) return;
      const prompt = els.imagegenEditPrompt?.value?.trim();
      const fileInput = els.imagegenEditFile;
      if (!prompt) { els.imagegenEditResult.innerHTML = '<div class="imagegen-error">Describe the change — e.g. “make the background blue” or “add soft rim light”.</div>'; return; }
      if (!fileInput?.files?.length && !els.imagegenEditPreview?.src?.startsWith('data:')) {
        els.imagegenEditResult.innerHTML = '<div class="imagegen-error">Upload an image, or pick one from the archive (✎).</div>'; return;
      }
      imagegenBusy = true;
      els.imagegenEditBtn.disabled = true;
      els.imagegenEditBtn.textContent = 'Editing…';
      const bypass = imagegenBypassPayload('edit').bypass_prompt;
      els.imagegenEditResult.innerHTML = bypass
        ? '<div class="imagegen-progress"><div><div class="imagegen-spinner"></div><strong>Editing with your exact prompt</strong><span>Sending the source image + your words to the native edit model…</span></div></div>'
        : '<div class="imagegen-progress"><div><div class="imagegen-spinner"></div><strong>Editing your image</strong><span>Applying your change to the source pixels — like ChatGPT or Grok. Keep this tab open.</span></div></div>';
      try {
        let imageData = '';
        if (els.imagegenEditPreview?.src?.startsWith('data:')) {
          imageData = els.imagegenEditPreview.src;
        } else if (fileInput.files[0]) {
          imageData = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Could not read the uploaded image.'));
            reader.readAsDataURL(fileInput.files[0]);
          });
        }
        imageData = await compressImageForEdit(imageData);
        const data = await api('/api/imagegen/edit', {
          method: 'POST',
          body: JSON.stringify({
            prompt,
            image: imageData,
            model: els.imagegenEditModel?.value,
            aspect_ratio: els.imagegenEditAspect?.value || els.imagegenAspect?.value,
            source_id: imagegenEditSourceId || '',
            apiKey: localStorage.getItem('ct_image_api_key') || localStorage.getItem('ct_api_key') || '',
            provider: localStorage.getItem('ct_image_provider') || localStorage.getItem('ct_provider') || 'openrouter',
            baseUrl: localStorage.getItem('ct_image_base_url') || '',
            ...imagegenBypassPayload('edit'),
          })
        }, IMAGEGEN_EDIT_TIMEOUT_MS);
        els.imagegenEditResult.innerHTML = renderImageResultCard(data, 'Edit');
        wireImageActions(els.imagegenEditResult);
        // Seamless iterative edit: result becomes the next source (ChatGPT/Grok style).
        if (data.data_url || data.image?.id) {
          const nextSrc = data.data_url || `/api/imagegen/image/${data.image.id}`;
          try {
            const nextData = data.data_url || await loadImageAsDataUrl(nextSrc);
            const compressed = await compressImageForEdit(nextData);
            els.imagegenEditPreview.src = compressed;
            els.imagegenEditPreview.classList.remove('hidden');
            els.imagegenSourceStage?.classList.add('has-source');
            els.imagegenEditPreview.onclick = () => openImagePreview(compressed, 'Edited image');
            imagegenEditSourceId = data.image?.id || imagegenEditSourceId;
          } catch {
            /* keep previous source if promote fails */
          }
        }
        if (data.image) {
          renderImagegenLineage({ ok: true, chain: [data.image] });
          loadImagegenLineage(data.image.id);
        }
        loadImagegen();
        els.imagegenEditResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } catch (error) {
        els.imagegenEditResult.innerHTML = `<div class="imagegen-error">${esc(error.message || 'Image edit failed.')}</div>`;
        els.imagegenEditResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } finally {
        imagegenBusy = false;
        els.imagegenEditBtn.disabled = false;
        els.imagegenEditBtn.textContent = 'Apply Edit';
      }
    }

    async function imagegenRedefine() {
      if (imagegenBusy) return;
      if (!imagegenSelectedImageId) {
        els.imagegenRedefineResult.innerHTML = '<div class="imagegen-error">Select a source image from the gallery above.</div>';
        return;
      }
      const prompt = els.imagegenRedefinePrompt?.value?.trim();
      if (!prompt) {
        els.imagegenRedefineResult.innerHTML = '<div class="imagegen-error">Enter a prompt first.</div>';
        return;
      }
      imagegenBusy = true;
      els.imagegenRedefineBtn.disabled = true;
      const bypass = imagegenBypassPayload('redefine').bypass_prompt;
      els.imagegenRedefineResult.innerHTML = bypass
        ? '<div class="imagegen-progress"><div><div class="imagegen-spinner"></div><strong>Raw redefine in progress</strong><span>Sending your prompt and source image to the edit endpoint.</span></div></div>'
        : '<div class="imagegen-progress"><div><div class="imagegen-spinner"></div><strong>Building a new interpretation</strong><span>Re-interpreting the source image via native image-to-image edit. This may take several minutes.</span></div></div>';
      try {
        const data = await api('/api/imagegen/redefine', {
          method: 'POST',
          body: JSON.stringify({
            source_id: imagegenSelectedImageId,
            prompt,
            model: els.imagegenEditModel?.value || els.imagegenModel?.value,
            aspect_ratio: els.imagegenAspect?.value,
            apiKey: localStorage.getItem('ct_image_api_key') || localStorage.getItem('ct_api_key') || '',
            provider: localStorage.getItem('ct_image_provider') || localStorage.getItem('ct_provider') || 'openrouter',
            baseUrl: localStorage.getItem('ct_image_base_url') || '',
            ...imagegenBypassPayload('redefine'),
          })
        }, IMAGEGEN_EDIT_TIMEOUT_MS);
        els.imagegenRedefineResult.innerHTML = renderImageResultCard(data, 'Redefine');
        wireImageActions(els.imagegenRedefineResult);
        if (data.image?.id) loadImagegenLineage(data.image.id);
        loadImagegen();
        els.imagegenRedefineResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } catch (error) {
        els.imagegenRedefineResult.innerHTML = `<div class="imagegen-error">${esc(error.message || 'Redefine failed.')}</div>`;
        els.imagegenRedefineResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } finally {
        imagegenBusy = false;
        els.imagegenRedefineBtn.disabled = false;
      }
    }

    async function deleteImagegenImage(imageId) {
      if (!imageId) return;
      try {
        await api('/api/imagegen/delete', { method: 'POST', body: JSON.stringify({ image_id: imageId }) });
        loadImagegen();
        if (imagegenSelectedImageId === imageId) {
          imagegenSelectedImageId = '';
          renderImagegenLineage(null);
        }
      } catch (error) {
        alert('Delete failed: ' + error.message);
      }
    }

    restoreImagegenBypassPreference();
    imagegenBypassCheckboxes().forEach(el => {
      el.addEventListener('change', () => syncImagegenBypassCheckboxes(el.checked));
    });

    if (els.imagegenModeGenerate) els.imagegenModeGenerate.addEventListener('click', () => setImagegenMode('generate'));
    if (els.imagegenModeEdit) els.imagegenModeEdit.addEventListener('click', () => setImagegenMode('edit'));
    if (els.imagegenModeRedefine) els.imagegenModeRedefine.addEventListener('click', () => setImagegenMode('redefine'));

    // ImageGen inspiration chips (creative prompt helpers)
    const editInspo = document.getElementById('imagegen-edit-inspiration');
    if (editInspo) {
      editInspo.querySelectorAll('button[data-edit-chip]').forEach(btn => {
        btn.addEventListener('click', () => {
          const ta = els.imagegenEditPrompt;
          if (!ta) return;
          const chip = btn.dataset.editChip || btn.textContent || '';
          ta.value = ta.value?.trim() ? `${ta.value.trim()}, ${chip}` : chip;
          ta.focus();
        });
      });
    }
    const imgInspo = document.getElementById('imagegen-inspiration');
    if (imgInspo) {
      imgInspo.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
          const ta = els.imagegenPrompt;
          if (!ta) return;
          const chip = btn.dataset.chip || btn.textContent;
          if (ta.value.trim()) ta.value += ', ' + chip;
          else ta.value = chip;
          ta.focus();
        });
      });
    }
    if (els.imagegenGenerateBtn) els.imagegenGenerateBtn.addEventListener('click', imagegenGenerate);
    if (els.imagegenEditBtn) els.imagegenEditBtn.addEventListener('click', imagegenEdit);
    if (els.imagegenRedefineBtn) els.imagegenRedefineBtn.addEventListener('click', imagegenRedefine);
    if (els.imagegenEditFile) {
      els.imagegenEditFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        setImageEditSource(file);
      });
    }
    if (els.imagegenReplaceSource) {
      els.imagegenReplaceSource.addEventListener('click', (event) => {
        event.stopPropagation();
        els.imagegenEditFile?.click();
      });
    }
    if (els.imagegenEditDropzone) {
      els.imagegenEditDropzone.addEventListener('click', () => els.imagegenEditFile?.click());
      els.imagegenEditDropzone.addEventListener('dragover', (e) => { e.preventDefault(); els.imagegenEditDropzone.style.borderColor = 'var(--accent)'; });
      els.imagegenEditDropzone.addEventListener('dragleave', () => { els.imagegenEditDropzone.style.borderColor = ''; });
      els.imagegenEditDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        els.imagegenEditDropzone.style.borderColor = '';
        const file = e.dataTransfer.files[0];
        if (!file || !file.type.startsWith('image/')) return;
        const dt = new DataTransfer();
        dt.items.add(file);
        els.imagegenEditFile.files = dt.files;
        setImageEditSource(file);
      });
    }
    if (els.imagegenLightboxClose) els.imagegenLightboxClose.addEventListener('click', closeImagePreview);
    if (els.imagegenLightbox) {
      els.imagegenLightbox.addEventListener('click', event => {
        if (event.target === els.imagegenLightbox) closeImagePreview();
      });
    }
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !els.imagegenLightbox?.classList.contains('hidden')) closeImagePreview();
    });

    // ===================================================================
    // CINE TEMPRE STUDIO — 2026 VideoGen (creative, filmic, director-grade)
    // ===================================================================
    let videogenActiveMode = 'text2video';
    let videogenSelectedId = '';
    let videogenBusy = false;

    function setVideogenMode(mode) {
      videogenActiveMode = mode;
      els.videogenModeText?.classList.toggle('active', mode === 'text2video');
      els.videogenModeImg?.classList.toggle('active', mode === 'img2vid');
      els.videogenModeRemix?.classList.toggle('active', mode === 'remix');
      els.videogenPanelText?.classList.toggle('hidden', mode !== 'text2video');
      els.videogenPanelImg?.classList.toggle('hidden', mode !== 'img2vid');
      els.videogenPanelRemix?.classList.toggle('hidden', mode !== 'remix');
      if (mode === 'remix') renderVideogenRemixGallery();
    }

    function attachLexiconChips() {
      if (!els.videogenLexicon) return;
      els.videogenLexicon.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
          const ta = els.videogenPrompt;
          if (!ta) return;
          const chip = btn.dataset.chip || btn.textContent;
          if (ta.value.trim()) ta.value += ', ' + chip;
          else ta.value = chip;
          ta.focus();
        });
      });
    }

    function setupSegmented(id) {
      const el = document.getElementById(id);
      if (!el) return;
      el.querySelectorAll('button').forEach(b => {
        b.addEventListener('click', () => {
          el.querySelectorAll('button').forEach(x => x.classList.remove('active'));
          b.classList.add('active');
        });
      });
    }

    async function loadVideogen() {
      if (!els.videogenGallery) return;
      els.videogenGallery.innerHTML = '';
      if (els.videogenCount) els.videogenCount.textContent = '0';
      try {
        const data = await api('/api/videogen/gallery');
        renderVideogenGallery(data.videos || []);
      } catch (e) {
        if (els.videogenGallery) els.videogenGallery.innerHTML = `<div class="empty" style="color:#c33;">${esc(e.message)}</div>`;
      }
    }

    function renderVideogenGallery(videos) {
      if (!els.videogenGallery) return;
      if (els.videogenCount) els.videogenCount.textContent = videos.length;
      if (!videos.length) {
        els.videogenGallery.innerHTML = `<div class="empty"><div>No clips yet — render your first one</div></div>`;
        return;
      }
      els.videogenGallery.innerHTML = videos.map(v => {
        // For demo items, use a rock-solid public small MP4 so it never 404s
        let videoSrc;
        if (v.provider === 'demo' || (v.model && v.model.startsWith('demo'))) {
          videoSrc = 'https://test-streams.github.io/streams/vod/mp4/bbb_720p_10s.mp4';
        } else {
          videoSrc = v.source_url || `/api/videogen/video/${esc(v.id)}`;
        }
        return `
        <div class="reel-card" data-id="${esc(v.id)}" title="${esc(v.prompt)}">
          <video muted preload="metadata" playsinline poster="">
            <source src="${esc(videoSrc)}" type="video/mp4">
          </video>
          <div class="meta">
            <span>${esc(v.duration || '')}</span>
            <span>v${v.ring_n || 1}</span>
          </div>
          <button class="del" data-id="${esc(v.id)}" title="Delete">×</button>
        </div>`;
      }).join('');

      els.videogenGallery.querySelectorAll('.reel-card').forEach(card => {
        const vid = card.querySelector('video');
        if (vid) {
          card.addEventListener('mouseenter', () => { vid.currentTime = 0; vid.play().catch(()=>{}); });
          card.addEventListener('mouseleave', () => { vid.pause(); });
        }
        card.addEventListener('click', e => {
          if (e.target.classList.contains('del')) {
            e.stopPropagation();
            deleteVideogenClip(card.dataset.id);
            return;
          }
          videogenSelectedId = card.dataset.id;
          loadVideogenLineage(card.dataset.id);
          // Prefer the actual src used in the gallery card (may be external source_url for demo)
          const actualSrc = card.querySelector('video source')?.src || '';
          loadVideogenIntoPlayer(card.dataset.id, actualSrc);
        });
      });
    }

    function renderVideogenRemixGallery() {
      if (!els.videogenRemixGallery) return;
      const cards = els.videogenGallery?.querySelectorAll('.reel-card') || [];
      if (!cards.length) {
        els.videogenRemixGallery.innerHTML = '<div style="color:#666;font-size:11px;padding:4px;">Generate some clips first.</div>';
        videogenSelectedId = '';
        return;
      }
      els.videogenRemixGallery.innerHTML = Array.from(cards).map(c => {
        const id = c.dataset.id;
        const src = c.querySelector('video')?.querySelector('source')?.src || '';
        return `<div class="thumb ${id===videogenSelectedId?'active':''}" data-id="${esc(id)}" style="width:92px;height:52px;"><video muted style="width:100%;height:100%;object-fit:cover;"><source src="${esc(src)}"></video></div>`;
      }).join('');
      els.videogenRemixGallery.querySelectorAll('.thumb').forEach(t => {
        t.addEventListener('click', () => {
          videogenSelectedId = t.dataset.id;
          renderVideogenRemixGallery();
        });
      });
    }

    async function loadVideogenLineage(id) {
      if (!els.videogenLineage) return;
      if (!id) { els.videogenLineage.innerHTML = ''; return; }
      try {
        const d = await api(`/api/videogen/lineage?video_id=${encodeURIComponent(id)}`);
        if (!d.ok) return;
        els.videogenLineage.innerHTML = d.chain.map((item, i) => {
          const arrow = i ? '→' : '';
          return `<div class="film-cell" data-id="${esc(item.video_id)}" title="${esc(item.prompt)}"><video muted><source src="/api/videogen/video/${esc(item.video_id)}"></video><div class="label">${esc(item.mode||'clip')}</div></div>`;
        }).join('');
        els.videogenLineage.querySelectorAll('.film-cell').forEach(cell => {
          cell.addEventListener('click', () => loadVideogenIntoPlayer(cell.dataset.id));
        });
      } catch {}
    }

    function loadVideogenIntoPlayer(videoId, preferredSrc = '') {
      if (!els.videogenResult) return;
      let src = preferredSrc || `/api/videogen/video/${esc(videoId)}`;

      // If this is a demo clip (we can detect by checking if we have a card with demo), force stable URL
      // Simpler: if no preferredSrc and it's likely demo, use stable one
      if (!preferredSrc) {
        // Will be improved later; for now the gallery cards already use stable for demo
      }

      els.videogenResult.innerHTML = `
        <div class="cine-player-perforation left"></div>
        <video controls playsinline style="max-height:420px;width:100%;background:#000;">
          <source src="${esc(src)}" type="video/mp4">
        </video>
        <div class="cine-player-perforation right"></div>
      `;
      loadVideogenLineage(videoId);
    }

    async function videogenRenderText2Video() {
      if (videogenBusy) return;
      const prompt = els.videogenPrompt?.value?.trim();
      if (!prompt) { els.videogenStatus.innerHTML = '<span class="cine-error">Enter a scene description</span>'; return; }
      videogenBusy = true;
      els.videogenRenderBtn?.classList.add('loading');
      els.videogenStatus.innerHTML = '<div class="cine-spinner"></div><span>Exposing temporal layer… locking motion vectors</span>';
      els.videogenResult.innerHTML = '';
      try {
        const durEl = document.querySelector('#videogen-duration .active');
        const duration = durEl ? durEl.dataset.val : '8s';
        const model = els.videogenModel?.value || 'demo-cinematic';
        const prov = model.startsWith('demo') ? 'demo' : (localStorage.getItem('ct_provider') || 'openrouter');
        const data = await api('/api/videogen/generate', {
          method: 'POST',
          body: JSON.stringify({
            prompt,
            model,
            aspect_ratio: els.videogenAspect?.value || '16:9',
            duration,
            motion_preset: els.videogenMotion?.value || 'Static',
            apiKey: localStorage.getItem('ct_video_api_key') || localStorage.getItem('ct_api_key') || '',
            provider: localStorage.getItem('ct_video_provider') || prov,
            baseUrl: localStorage.getItem('ct_video_base_url') || '',
          })
        });
        els.videogenStatus.textContent = '';
        els.videogenResult.innerHTML = `
          <div class="cine-player-perforation left"></div>
          <video controls playsinline style="max-height:420px;width:100%;background:#000;">
            <source src="${data.video_url || data.data_url || `/api/videogen/video/${data.video.id}`}" type="video/mp4">
          </video>
          <div class="cine-player-perforation right"></div>`;
        loadVideogenLineage(data.video.id);
        loadVideogen();
      } catch (e) {
        els.videogenStatus.innerHTML = `<span class="cine-error">${esc(e.message)}</span>`;
      } finally {
        videogenBusy = false;
        els.videogenRenderBtn?.classList.remove('loading');
      }
    }

    let audiogenBusy = false;
    async function audiogenGenerate() {
      if (audiogenBusy) return;
      const text = els.audiogenText?.value?.trim();
      if (!text) {
        els.audiogenStatus.innerHTML = '<span style="color:var(--error);display:inline-flex;padding:6px 12px;">Enter text first.</span>';
        return;
      }
      audiogenBusy = true;
      els.audiogenStatus.innerHTML = '<div style="display:flex;align-items:center;gap:8px;"><div style="width:16px;height:16px;border:2px solid var(--primary);border-radius:50%;border-top-color:transparent;animation:spin 0.6s linear infinite;"></div><span>Generating audio...</span></div>';
      els.audiogenResult.innerHTML = '';
      try {
        const data = await api('/api/audiogen/generate', {
          method: 'POST',
          body: JSON.stringify({
            text,
            voice: els.audiogenVoice?.value || 'af_alloy',
            response_format: els.audiogenFormat?.value || 'mp3',
            speed: parseFloat(els.audiogenSpeed?.value || 1),
            model: normalizeAudioModel(els.audioModel?.value || localStorage.getItem('ct_audio_model') || 'tts-kokoro'),
            apiKey: localStorage.getItem('ct_audio_api_key') || localStorage.getItem('ct_api_key') || '',
            provider: localStorage.getItem('ct_audio_provider') || localStorage.getItem('ct_provider') || 'morpheus',
            baseUrl: localStorage.getItem('ct_audio_base_url') || '',
          })
        });
        els.audiogenStatus.textContent = '';
        const mimeMap = { 'mp3': 'audio/mpeg', 'wav': 'audio/wav', 'aac': 'audio/aac', 'opus': 'audio/opus', 'flac': 'audio/flac' };
        const mimeType = mimeMap[data.format] || 'audio/mpeg';
        els.audiogenResult.innerHTML = `
          <div style="margin-top:16px;padding:16px;background:var(--bg-secondary);border-radius:8px;">
            <audio controls style="width:100%;margin-bottom:8px;">
              <source src="data:${mimeType};base64,${data.audio_data}" type="${mimeType}">
            </audio>
            <div style="font-size:11px;color:var(--text-muted);word-break:break-all;">${esc(data.audio_id)}</div>
          </div>`;
      } catch (error) {
        els.audiogenStatus.textContent = '';
        els.audiogenResult.innerHTML = `<div style="color:var(--error);padding:12px;background:rgba(255,0,0,0.1);border-radius:4px;">${esc(error.message)}</div>`;
      } finally {
        audiogenBusy = false;
      }
    }

    async function videogenRenderImg2Vid() {
      if (videogenBusy) return;
      const prompt = els.videogenImgPrompt?.value?.trim();
      const fileInput = els.videogenImgFile;
      if (!prompt) { els.videogenImgResult.innerHTML = '<div class="cine-error">Describe the motion</div>'; return; }
      if (!fileInput?.files?.length && !els.videogenImgPreview?.src?.startsWith('data:')) {
        els.videogenImgResult.innerHTML = '<div class="cine-error">Upload a reference still</div>'; return;
      }
      videogenBusy = true;
      els.videogenImgResult.innerHTML = '<div class="cine-status"><div class="cine-spinner"></div><span>Animating still into motion…</span></div>';
      let imageData = els.videogenImgPreview?.src || '';
      if (fileInput.files[0]) {
        imageData = await new Promise(r => { const rd = new FileReader(); rd.onload = () => r(rd.result); rd.readAsDataURL(fileInput.files[0]); });
      }
      try {
        const durEl = document.querySelector('#videogen-img-duration .active');
        const duration = durEl ? durEl.dataset.val : '10s';
        const model = els.videogenImgModel?.value || 'demo-cinematic';
        const configuredVideoProvider = localStorage.getItem('ct_video_provider') || localStorage.getItem('ct_provider') || 'openrouter';
        const provider = model.startsWith('demo') ? 'demo' : configuredVideoProvider;
        const data = await api('/api/videogen/img2vid', {
          method: 'POST',
          body: JSON.stringify({
            prompt, image: imageData,
            model,
            aspect_ratio: '16:9',
            duration,
            motion_preset: els.videogenImgMotion?.value || 'Dolly In',
            apiKey: localStorage.getItem('ct_video_api_key') || localStorage.getItem('ct_api_key') || '',
            provider,
            baseUrl: localStorage.getItem('ct_video_base_url') || '',
          })
        });
        els.videogenImgResult.innerHTML = `
          <div class="cine-player-perforation left"></div>
          <video controls playsinline style="max-height:380px;width:100%;">
            <source src="${data.video_url || data.data_url || `/api/videogen/video/${data.video.id}`}">
          </video>
          <div class="cine-player-perforation right"></div>`;
        loadVideogen();
      } catch (e) {
        els.videogenImgResult.innerHTML = `<div class="cine-error">${esc(e.message)}</div>`;
      } finally { videogenBusy = false; }
    }

    async function videogenRenderRemix() {
      if (videogenBusy || !videogenSelectedId) {
        els.videogenRemixResult.innerHTML = '<div class="cine-error">Select a source reel from the strip above</div>';
        return;
      }
      const prompt = els.videogenRemixPrompt?.value?.trim();
      if (!prompt) { els.videogenRemixResult.innerHTML = '<div class="cine-error">Describe the new direction</div>'; return; }
      videogenBusy = true;
      els.videogenRemixResult.innerHTML = '<div class="cine-status"><div class="cine-spinner"></div><span>Branching new cut…</span></div>';
      try {
        const model = els.videogenModel?.value || 'demo-cinematic';
        const configuredVideoProvider = localStorage.getItem('ct_video_provider') || localStorage.getItem('ct_provider') || 'openrouter';
        const provider = model.startsWith('demo') ? 'demo' : configuredVideoProvider;
        const data = await api('/api/videogen/remix', {
          method: 'POST',
          body: JSON.stringify({
            source_id: videogenSelectedId,
            prompt,
            model,
            aspect_ratio: '16:9',
            duration: '8s',
            motion_preset: 'Remix',
            apiKey: localStorage.getItem('ct_video_api_key') || localStorage.getItem('ct_api_key') || '',
            provider,
            baseUrl: localStorage.getItem('ct_video_base_url') || '',
          })
        });
        els.videogenRemixResult.innerHTML = `
          <div class="cine-player-perforation left"></div>
          <video controls playsinline style="max-height:380px;width:100%;">
            <source src="${data.video_url || data.data_url || `/api/videogen/video/${data.video.id}`}">
          </video>
          <div class="cine-player-perforation right"></div>`;
        loadVideogenLineage(data.video.id);
        loadVideogen();
      } catch (e) {
        els.videogenRemixResult.innerHTML = `<div class="cine-error">${esc(e.message)}</div>`;
      } finally { videogenBusy = false; }
    }

    async function deleteVideogenClip(id) {
      if (!id) return;
      try {
        await api('/api/videogen/delete', { method: 'POST', body: JSON.stringify({ video_id: id }) });
        loadVideogen();
        if (videogenSelectedId === id) videogenSelectedId = '';
      } catch (e) { alert('Delete failed: ' + e.message); }
    }

    // Wire CineTempre controls
    if (els.videogenModeText) els.videogenModeText.addEventListener('click', () => setVideogenMode('text2video'));
    if (els.videogenModeImg) els.videogenModeImg.addEventListener('click', () => setVideogenMode('img2vid'));
    if (els.videogenModeRemix) els.videogenModeRemix.addEventListener('click', () => setVideogenMode('remix'));
    if (els.imagegenModel) {
      els.imagegenModel.addEventListener('change', () => {
        const selected = els.imagegenModel.value?.trim() || '';
        if (!selected) return;
        localStorage.setItem('ct_image_model', selected);
        setSelectValue(els.imageModel, selected);
        schedulePersistUserConfig();
        refreshProviderSummary();
      });
    }
    if (els.imagegenEditModel) {
      els.imagegenEditModel.addEventListener('change', () => {
        const selected = els.imagegenEditModel.value?.trim() || '';
        if (!selected) return;
        localStorage.setItem('ct_image_edit_model', selected);
        schedulePersistUserConfig();
        refreshProviderSummary();
      });
    }
    if (els.videogenModel) {
      els.videogenModel.addEventListener('change', () => {
        const selected = els.videogenModel.value?.trim() || '';
        if (!selected) return;
        localStorage.setItem('ct_video_model', selected);
        setSelectValue(els.videoModel, selected);
        setSelectValue(els.videogenImgModel, selected);
        schedulePersistUserConfig();
        refreshProviderSummary();
      });
    }
    if (els.videogenImgModel) {
      els.videogenImgModel.addEventListener('change', () => {
        const selected = els.videogenImgModel.value?.trim() || '';
        if (!selected) return;
        localStorage.setItem('ct_video_model', selected);
        setSelectValue(els.videoModel, selected);
        setSelectValue(els.videogenModel, selected);
        schedulePersistUserConfig();
        refreshProviderSummary();
      });
    }
    if (els.videogenRenderBtn) els.videogenRenderBtn.addEventListener('click', videogenRenderText2Video);
    if (els.videogenImgBtn) els.videogenImgBtn.addEventListener('click', videogenRenderImg2Vid);
    if (els.videogenRemixBtn) els.videogenRemixBtn.addEventListener('click', videogenRenderRemix);

    attachLexiconChips();
    setupSegmented('videogen-duration');
    setupSegmented('videogen-img-duration');

    if (els.videogenImgDrop) {
      els.videogenImgDrop.addEventListener('click', () => els.videogenImgFile?.click());
      els.videogenImgFile?.addEventListener('change', e => {
        const f = e.target.files[0]; if (!f) return;
        const r = new FileReader();
        r.onload = () => { els.videogenImgPreview.src = r.result; els.videogenImgPreview.classList.remove('hidden'); };
        r.readAsDataURL(f);
      });
    }

    initTheme();
    initDensity();
    initRailCollapse();
    initPanels();
    if (els.themeToggle) els.themeToggle.addEventListener('click', toggleTheme);
    if (els.densityToggle) els.densityToggle.addEventListener('click', toggleDensity);
    if (els.railCollapse) els.railCollapse.addEventListener('click', toggleRailCollapse);

    let bootInFlight = null;
    async function bootAuthenticatedApp() {
      // Serialize boots so login + page load don't race.
      if (bootInFlight) return bootInFlight;
      bootInFlight = (async () => {
        try {
          if (els.workspace) {
            els.workspace.textContent = `Workspace: ${activeSession || 'default'}…`;
          }
          setStatus('Loading workspace…', '');

          const config = await api('/api/config', {}, 15000);
          applyLocalConfig(config);

          // Curated models first so Settings never looks empty while discovery runs.
          updateChatModelOptions();
          updateImageModelOptions();
          updateImageEditModelOptions();
          updateVideoModelOptions();
          updateAudioModelOptions();
          updateEffectiveProviderSummary();

          // Non-blocking persona sync + live model discovery (must not stall UI).
          syncCustomPersonasToServer(config).catch(() => null);
          const startupProviders = [...new Set([
            els.provider?.value,
            els.imageProvider?.value,
            els.videoProvider?.value,
            els.audioProvider?.value,
          ].filter(Boolean))];
          Promise.allSettled(
            startupProviders.map(provider => refreshProviderModels(provider, true))
          ).then(results => {
            updateChatModelOptions();
            updateImageModelOptions();
            updateImageEditModelOptions();
            updateVideoModelOptions();
            updateAudioModelOptions();
            updateEffectiveProviderSummary();
            const discoveryFailure = results.find(result => result.status === 'rejected');
            if (discoveryFailure) {
              setStatusDetail(`Model discovery: ${discoveryFailure.reason?.message || discoveryFailure.reason}`);
            }
          }).catch(() => null);

          setMainView(localStorage.getItem('ct_view') || 'chat');
          setSettingsSection(localStorage.getItem('ct_settings_section') || 'provider');

          await loadGuideTopics().catch(() => null);
          await loadSessions().catch(error => {
            if (els.workspace) els.workspace.textContent = `Workspace: ${activeSession || 'default'}`;
            throw error;
          });

          // Session chrome loads independently so one slow endpoint can't freeze the shell.
          const sessionLoads = await Promise.allSettled([
            refreshSummary(),
            refreshMemories(),
            refreshWorkbench(),
            verifyChain(),
            restoreHistory(),
            refreshTrustStrip(),
          ]);
          const failed = sessionLoads.filter(r => r.status === 'rejected');
          if (failed.length) {
            const msg = failed[0].reason?.message || String(failed[0].reason || 'session load failed');
            setStatusDetail(`Some session panels failed: ${msg}`);
          }

          if (els.workspace && /loading/i.test(els.workspace.textContent || '')) {
            els.workspace.textContent = `Workspace: ${activeSession || 'default'}`;
          }
          setStatus('Ready', 'ok');
          updateSetup(Boolean(config.has_env_key));

          loadMarketplace().catch(() => null);
          loadCreatorPersonas().catch(() => null);
        } catch (error) {
          if (els.workspace) {
            els.workspace.textContent = `Workspace: ${activeSession || 'default'} (error)`;
          }
          setStatus(error.message || 'Boot failed', 'error');
          try {
            appendMessage('CypherTempre', error.message || 'Boot failed', { accepted: false }, true);
          } catch (_) { /* ignore */ }
          throw error;
        } finally {
          bootInFlight = null;
        }
      })();
      return bootInFlight;
    }

    checkAuth().then((authenticated) => {
      if (!authenticated) {
        if (els.workspace) els.workspace.textContent = 'Workspace: sign in to load';
        return null;
      }
      return bootAuthenticatedApp();
    }).catch(error => {
      setStatus(error.message || 'Startup failed', 'error');
    });

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
"""
