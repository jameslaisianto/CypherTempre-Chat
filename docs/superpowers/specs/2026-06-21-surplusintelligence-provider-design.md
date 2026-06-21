# SurplusIntelligence Provider Design

## Goal

Make SurplusIntelligence the configured provider across CypherTempre Chat while preserving separate model choices for each modality. The user will supply credentials after the change.

## Provider Identity and Endpoints

Add `surplusintelligence` as a first-class provider with the label `SurplusIntelligence`.

The provider uses the OpenAI-compatible base URL:

```text
https://api.surplusintelligence.ai/v1
```

Endpoint resolution:

- Chat: `/chat/completions`
- Image generation: `/chat/completions`
- Image editing and redefining: `/chat/completions`
- Video generation: `/chat/completions`
- Image-to-video: `/chat/completions`
- Video remix and extension: `/chat/completions`
- Audio generation: `/audio/speech`
- Model discovery, when used: `/models`

The request code must accept either the `/v1` base URL or a full operation endpoint without duplicating path segments.

## Environment Configuration

Update `.env.local` and `.env.example` so SurplusIntelligence is selected for chat, image, video, and audio.

Use modality-specific variables:

```text
PROVIDER=surplusintelligence
API_KEY=
MODEL=deepseek-v4-flash
BASE_URL=https://api.surplusintelligence.ai/v1

IMAGE_PROVIDER=surplusintelligence
IMAGE_API_KEY=
IMAGE_MODEL=
IMAGE_EDIT_MODEL=
IMAGE_BASE_URL=https://api.surplusintelligence.ai/v1

VIDEO_PROVIDER=surplusintelligence
VIDEO_API_KEY=
VIDEO_MODEL=
VIDEO_BASE_URL=https://api.surplusintelligence.ai/v1

AUDIO_PROVIDER=surplusintelligence
AUDIO_API_KEY=
AUDIO_MODEL=
AUDIO_BASE_URL=https://api.surplusintelligence.ai/v1
```

Existing real secrets in `.env.local` must not be copied, printed, or retained under the replaced provider variables. Authentication secrets unrelated to providers remain unchanged.

Known working model IDs are not assumed. The current chat model is retained, while media model values are left blank for the user unless an existing SurplusIntelligence-compatible value is already known locally.

## Server Configuration

Add SurplusIntelligence entries to the chat, image, video, and audio provider registries.

Server startup must load the generic chat variables and the modality-specific variables. Media handlers use this precedence:

1. Explicit request value from the browser.
2. Modality-specific environment value.
3. Shared chat provider credential or model where appropriate.
4. Provider registry default.

Blank modality-specific API keys fall back to the shared `API_KEY`, allowing one credential to serve every supported modality. Explicit modality keys remain supported.

## UI Configuration

Expose SurplusIntelligence in every provider selector:

- Chat
- Image
- Video
- Audio

Changing a provider should populate the SurplusIntelligence base URL without forcing an unverified model ID.

The UI keeps separate state for:

- Image generation model
- Image editing/redefinition model
- Video generation, image-to-video, and remix model
- Audio model

Persisted browser settings continue to override server defaults. Clearing overrides returns the UI to environment-backed SurplusIntelligence settings.

## Request Behavior

Chat requests use the normal OpenAI-compatible chat-completions payload.

Image generation sends image output modalities and optional image configuration. Image editing and redefining include the source image and use the separately configured edit model.

Video generation, image-to-video, and remix/extension use the selected video provider, key, model, and base URL. All three paths must forward the configured SurplusIntelligence endpoint rather than silently falling back to OpenRouter or Morpheus.

Audio generation uses the selected provider, key, model, and `/audio/speech` endpoint. Morpheus-only model-discovery behavior must not run for SurplusIntelligence.

## Error Handling

- Missing credentials produce the existing clear API-key error.
- Blank media models produce a clear model-required error before making a network request.
- Provider HTTP errors retain the SurplusIntelligence label and upstream message.
- Empty or unsupported image/video responses return the existing usable-media error without saving an invalid gallery item.

## Testing

Add tests before implementation for:

- SurplusIntelligence chat endpoint resolution from the `/v1` base.
- Provider registry entries for all four modalities.
- Environment-backed modality defaults and shared-key fallback.
- Image generation and image editing/redefinition forwarding provider, model, base URL, and operation.
- Video generation, image-to-video, and remix forwarding the configured base URL.
- Audio generation resolving `/audio/speech`.
- UI provider options and separate image generation/editing model persistence.
- Empty or failed model discovery preserving configured image generation and edit model IDs.
- SurplusIntelligence image-output models populating both generation and source-aware edit selectors.
- Stale browser model values being replaced only when a successful discovery response proves they are unsupported.

Run focused tests during development, then the complete unit-test suite.

## Confirmed Image Model Repair

Live model discovery on June 21, 2026 returned 254 SurplusIntelligence models. The configured
`venice-lustify-v8` model was present and declared:

```text
input_modalities: ["text"]
output_modalities: ["image"]
```

The provider and configured model are therefore available. The failure is local selection and
fallback behavior:

- The image-edit selector treats an empty discovery result as proof that editing is unsupported.
- It disables the edit controls and deletes the configured `IMAGE_EDIT_MODEL` browser override.
- A temporary discovery failure, missing browser credential, stale cache, or startup race can
  therefore make every image model appear unavailable even when the provider advertises them.

The repair will use successful provider discovery as the preferred catalog while preserving
configured model IDs whenever discovery is empty or fails. All discovered image-output models
are valid generation choices and source-aware edit choices because SurplusIntelligence editing
is implemented by analyzing the source with a vision model and then regenerating through
`/images/generations`.

Generation requests will continue to call `/images/generations`. Edit and redefine requests will
use the source-aware edit service: select a discovered vision model, analyze the source image and
requested change, then submit the resulting prompt to `/images/generations` using the separately
selected image edit model.

The UI must not disable image editing or remove configured model values merely because discovery
is temporarily unavailable. It may replace an unsupported selection only after a successful,
non-empty image catalog is received.

## Scope Boundaries

This change does not invent SurplusIntelligence model IDs, add new media response formats without evidence, or make live authenticated calls. It preserves unrelated working-tree changes and does not alter the CypherTempre memory architecture.
