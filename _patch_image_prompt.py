from pathlib import Path

path = Path("server/image_prompt.py")
text = path.read_text(encoding="utf-8")
marker = "def build_anchored_edit_prompt("
idx = text.index(marker)

new_tail = '''def prepare_native_edit_prompt(
    user_prompt: str,
    *,
    bypass: bool = False,
    limit: int = 1400,
) -> str:
    """ChatGPT / Grok-style prompt for native image-to-image edit models.

    Native edit models already see the source pixels. Over-rewriting into a full
    text-to-image brief often *hurts* fidelity. Keep the user's natural language,
    lightly normalize whitespace, and (unless bypass) add a short preserve-identity
    cue only when the request is short and conversational.
    """
    prompt = re.sub(r"\\s+", " ", str(user_prompt or "")).strip()
    if not prompt:
        return "Improve clarity and detail while preserving the subject, identity, pose, and composition."
    if bypass or not _looks_short(prompt):
        return clamp_surplus_image_prompt(prompt, limit=limit)
    # Short conversational edits ("make the sky purple") work best as-is with a light guardrail.
    if re.search(r"\\b(keep|preserve|same person|same face|don't change|do not change)\\b", prompt, re.I):
        return clamp_surplus_image_prompt(prompt, limit=limit)
    guarded = (
        f"{prompt.rstrip('.')}. "
        "Keep the same subject identity, face, pose, wardrobe, and composition "
        "unless I explicitly asked to change them."
    )
    return clamp_surplus_image_prompt(guarded, limit=limit)


def build_anchored_edit_prompt(
    *,
    provider: str,
    api_key: str,
    base_url: str,
    image_parts: list[dict[str, Any]],
    user_prompt: str,
    timeout: float = 120.0,
    vision_model: str = "",
    identity_analysis: str = "",
    bypass: bool = False,
    native_i2i: bool = False,
) -> str:
    """Produce an edit prompt from a source image and a change request.

    For native image-to-image models (``native_i2i=True`` / Surplus), use a
    ChatGPT/Grok-style natural-language instruction — do not vision-rewrite into
    a full generation brief.

    For chat-modality image models that regenerate from text, identity-anchor via vision.
    When bypass=True, returns the user's prompt unchanged (raw path).
    On refusal or failure, returns the user's prompt unchanged.
    """
    user_prompt = (user_prompt or "").strip()
    if bypass or not image_parts:
        return user_prompt
    # Native I2I path (Surplus /images/edits, Grok Imagine edit, etc.): keep it natural.
    if native_i2i or provider == "surplusintelligence":
        return prepare_native_edit_prompt(user_prompt, bypass=False)
    if not identity_analysis:
        identity_analysis = analyze_source_identity(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            image_parts=image_parts,
            timeout=timeout,
            vision_model=vision_model,
            bypass=bypass,
        )
    if not identity_analysis:
        return user_prompt
    composed = (
        f"SOURCE IMAGE ANALYSIS (identity ground truth):\\n{identity_analysis}\\n\\n"
        f"USER EDIT REQUEST:\\n{user_prompt or '(no explicit change; reproduce the source image)'}"
    )
    model = _resolve_vision_model(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
        preferred_model=vision_model,
    )
    try:
        result = call_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=[
                {"role": "system", "content": _EDIT_SYSTEM_PROMPT},
                {"role": "user", "content": composed},
            ],
            timeout=timeout,
            base_url=base_url,
            max_tokens=900,
        )
        anchored = _clean_enriched_prompt(str(result.get("content", "")))
        if _looks_like_refusal(anchored):
            return user_prompt
        return anchored or user_prompt
    except Exception:
        return user_prompt
'''

old_doc_bit = """2. Anchoring subject identity when editing/redefining: extract facial features, hair,
   attire, pose, and distinguishing marks from the source image with a vision LLM,
   then embed those anchors into the regeneration prompt so the same person comes back.
3. Reusing the same vision analysis even on the native-edit path when the model can
   accept reference images, so identity-locked language accompanies the image."""
new_doc_bit = """2. For native image-to-image edit endpoints (Surplus /images/edits, Grok Imagine edit),
   keep short conversational edit requests in natural language — like ChatGPT/Grok —
   so the model edits the source pixels instead of regenerating from a text rewrite.
3. For chat-modality image models without a true edit endpoint, anchor identity via a
   vision LLM and embed those anchors into a regeneration-style prompt."""
if old_doc_bit in text:
    text = text.replace(old_doc_bit, new_doc_bit)

path.write_text(text[:idx] + new_tail + "\n", encoding="utf-8")
print("patched", path)
