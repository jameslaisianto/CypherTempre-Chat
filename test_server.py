import unittest
import tempfile
from unittest import mock
from types import SimpleNamespace

import server


class PromptAssemblyTests(unittest.TestCase):
    def test_build_memory_context_uses_ring_metadata(self):
        rings = [
            SimpleNamespace(
                n=3,
                domain="architecture",
                brightness=0.8123,
                epistemic="known",
                content="Use the standalone PoC as the CypherTempre UI.",
            )
        ]

        context = server.build_memory_context(rings)

        self.assertIn("Ring #3", context)
        self.assertIn("architecture", context)
        self.assertIn("brightness=0.812", context)
        self.assertIn("Use the standalone PoC", context)

    def test_build_messages_includes_persona_memory_and_covenant(self):
        persona = {
            "name": "Architect",
            "system": "You are an architect.",
        }
        rings = [
            SimpleNamespace(
                n=1,
                domain="system-design",
                brightness=0.7,
                epistemic="speculated",
                content="Keep the UI separate from any host application.",
            )
        ]

        messages = server.build_messages(
            persona=persona,
            query="What should we build next?",
            retrieved=rings,
            durable_memories=[],
            recent_turns=[],
            neuro={"dopamine": 0.3, "serotonin": 0.5},
            covenant="Prefer maintainable software.",
        )

        self.assertEqual(messages[-1], {"role": "user", "content": "What should we build next?"})
        self.assertIn("You are an architect.", messages[0]["content"])
        self.assertIn("Prefer maintainable software.", messages[0]["content"])
        self.assertIn("Keep the UI separate", messages[1]["content"])
        self.assertIn("dopamine=0.30", messages[1]["content"])

    def test_build_messages_includes_recent_turns_before_current_query(self):
        persona = {"name": "Mira", "system": "Stay in character."}
        recent = [
            {"role": "user", "content": "My name is Kai."},
            {"role": "assistant", "content": "I'll remember that, Kai."},
        ]

        messages = server.build_messages(
            persona=persona,
            query="What is my name?",
            retrieved=[],
            durable_memories=[],
            recent_turns=recent,
            neuro={},
            covenant="Be useful.",
        )

        self.assertEqual(messages[-3:], [
            {"role": "user", "content": "My name is Kai."},
            {"role": "assistant", "content": "I'll remember that, Kai."},
            {"role": "user", "content": "What is my name?"},
        ])

    def test_serialize_history_reconstructs_user_and_assistant_turns(self):
        chain = [
            SimpleNamespace(kind="genesis"),
            SimpleNamespace(
                kind="interaction",
                query="Can you remember this?",
                content="Yes, this is sealed.",
                domain="architecture",
                n=4,
                ts="2026-05-01T00:00:00Z",
                brightness=0.7123,
                epistemic="known",
                hash="abcdef1234567890abcdef1234567890",
            ),
        ]

        history = server.serialize_history(chain)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Can you remember this?")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["brightness"], 0.712)
        self.assertEqual(history[1]["hash_prefix"], "abcdef1234567890")

    def test_classify_domain_auto_uses_message_keywords(self):
        persona = {"name": "Companion", "domain": "architecture", "system": ""}

        domain = server.classify_domain("Can you help debug this stack trace?", persona, "auto")

        self.assertEqual(domain, "debugging")

    def test_normalize_custom_persona_accepts_valid_prompt(self):
        persona = server.normalize_custom_persona({
            "name": "Mira Vale",
            "domain": "auto",
            "system": "Fictional lighthouse archivist persona.",
        })

        self.assertEqual(persona["name"], "Mira Vale")
        self.assertEqual(persona["domain"], "auto")
        self.assertIn("Fictional", persona["system"])

    def test_classify_domain_respects_manual_domain(self):
        persona = {"name": "Companion", "domain": "architecture", "system": ""}

        domain = server.classify_domain("debug this crash", persona, "security")

        self.assertEqual(domain, "security")

    def test_sanitize_session_id_keeps_safe_slug(self):
        self.assertEqual(server.sanitize_session_id("My New Chat!"), "My-New-Chat")
        self.assertEqual(server.sanitize_session_id(""), "default")

    def test_build_recent_turns_serializes_prior_interactions(self):
        chain = [
            SimpleNamespace(kind="genesis"),
            SimpleNamespace(kind="interaction", query="Hello", content="Hi there"),
        ]

        turns = server.build_recent_turns(chain)

        self.assertEqual(turns, [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ])

    def test_extract_memory_facts_captures_user_name(self):
        ring = SimpleNamespace(n=2, query="hey I am Thomas, nice to meet you", content="Nice to meet you.")

        facts = server.extract_memory_facts(ring, persona_name="Companion")

        self.assertEqual(facts[0]["key"], "user.name")
        self.assertEqual(facts[0]["value"], "Thomas")
        self.assertEqual(facts[0]["status"], "known")
        self.assertEqual(facts[0]["source_ring"], 2)

    def test_extract_memory_facts_rejects_uncertain_user_name(self):
        ring = SimpleNamespace(n=3, query="I am tired", content="Rest for a bit.")

        facts = server.extract_memory_facts(ring, persona_name="Companion")

        self.assertFalse(any(fact["key"] == "user.name" for fact in facts))

    def test_update_memory_model_correction_replaces_prior_fact(self):
        model = server.empty_memory_model()
        first = SimpleNamespace(n=2, query="my name is Thomas", content="Nice to meet you.")
        correction = SimpleNamespace(n=8, query="No, my name is Jamie", content="Sorry, Jamie.")

        server.update_memory_model(model, first, persona_name="Companion")
        server.update_memory_model(model, correction, persona_name="Companion")

        facts = [fact for fact in model["facts"] if fact["key"] == "user.name" and fact["status"] == "known"]
        old = [fact for fact in model["facts"] if fact["key"] == "user.name" and fact["status"] == "superseded"]
        self.assertEqual(facts[0]["value"], "Jamie")
        self.assertEqual(old[0]["value"], "Thomas")
        self.assertEqual(facts[0]["supersedes"], old[0]["id"])

    def test_memory_recall_returns_name_after_many_unrelated_rings(self):
        model = server.empty_memory_model()
        server.update_memory_model(
            model,
            SimpleNamespace(n=2, query="hey I am Thomas, nice to meet you", content="Nice to meet you."),
            persona_name="Companion",
        )
        for index in range(3, 34):
            server.update_memory_model(
                model,
                SimpleNamespace(n=index, query=f"unrelated topic {index}", content="We discussed something else."),
                persona_name="Companion",
            )

        hits = server.recall_memory_facts(model, "what is my name?")

        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(hits[0]["key"], "user.name")
        self.assertEqual(hits[0]["value"], "Thomas")

    def test_build_messages_includes_durable_memory_before_ring_context(self):
        persona = {"name": "Companion", "system": "Stay useful."}
        memories = [{"key": "user.name", "value": "Thomas", "confidence": 0.95, "source_ring": 2, "status": "known"}]

        messages = server.build_messages(
            persona=persona,
            query="What is my name?",
            retrieved=[],
            durable_memories=memories,
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
        )

        self.assertIn("Durable memories", messages[1]["content"])
        self.assertIn("user.name: Thomas", messages[1]["content"])

    def test_needs_memory_retry_when_name_answer_omits_known_name(self):
        memories = [{"key": "user.name", "value": "Thomas", "confidence": 0.95, "source_ring": 2, "status": "known"}]

        reason = server.memory_retry_reason("what is my name?", "I do not know your name.", memories, "Companion")

        self.assertIn("Thomas", reason)

    def test_local_memory_answer_repairs_missing_llm_name_answer(self):
        memories = [{"key": "user.name", "value": "Thomas", "confidence": 0.95, "source_ring": 2, "status": "known"}]

        answer = server.local_memory_answer("what is my name?", memories, "Companion")

        self.assertEqual(answer, "Your name is Thomas.")

    def test_generate_persona_from_seed_uses_requested_name(self):
        persona = server.generate_persona_from_seed("Winter", "quiet archive companion")

        self.assertEqual(persona["name"], "Winter")
        self.assertIn("You are Winter", persona["system"])

    def test_default_model_is_venice_uncensored(self):
        self.assertEqual(
            server.DEFAULT_MODEL,
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        )
        self.assertIn(server.DEFAULT_MODEL, server.HTML)

    def test_custom_personas_persist_in_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = server.pathlib.Path(temp)
            personas = {
                "custom_mira": {
                    "name": "Mira Vale",
                    "domain": "auto",
                    "system": "Fictional lighthouse archivist persona.",
                }
            }

            server.save_custom_personas(workspace, personas)
            loaded = server.load_custom_personas(workspace)

        self.assertEqual(loaded["custom_mira"]["name"], "Mira Vale")
        self.assertEqual(loaded["custom_mira"]["domain"], "auto")

    def test_generate_llm_response_uses_saved_custom_persona_and_falls_back_on_openrouter_error(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = server.pathlib.Path(temp)
            app = server.App(
                workspace,
                server.DEFAULT_TIMECHAIN_PATH,
                default_model=server.DEFAULT_MODEL,
                openrouter_api_key="sk-or-test",
                openrouter_timeout=1,
            )
            app.save_custom_persona("custom_mira", {
                "name": "Mira Vale",
                "domain": "auto",
                "system": "Fictional lighthouse archivist persona.",
            })

            with mock.patch("server.call_openrouter", side_effect=RuntimeError("OpenRouter HTTP 429: Too Many Requests")):
                response = app.generate_llm_response(
                    query="hello",
                    domain="architecture",
                    persona_id="custom_mira",
                    custom_persona=None,
                    model=server.DEFAULT_MODEL,
                    api_key="sk-or-test",
                )

        self.assertEqual(response["persona"]["name"], "Mira Vale")
        self.assertEqual(response["model_used"], "local-default-generator")
        self.assertIn("429", response["openrouter_error"])

    def test_desktop_layout_locks_shell_to_chat_scroll(self):
        self.assertIn("body {\n      margin: 0;\n      height: 100%;\n      overflow: hidden;", server.HTML)
        self.assertIn(".app {\n      display: grid;\n      grid-template-columns: 286px minmax(0, 1fr) 360px;\n      height: 100vh;", server.HTML)
        self.assertIn(".messages {\n      overflow: auto;", server.HTML)
        self.assertNotIn("body { overflow: auto; }", server.HTML)
        self.assertNotIn("overflow: visible;", server.HTML)

    def test_openrouter_key_ui_has_test_button_and_clearable_storage(self):
        self.assertIn('id="test-openrouter"', server.HTML)
        self.assertIn("localStorage.removeItem('ct_openrouter_key')", server.HTML)
        self.assertIn("async function testOpenRouter()", server.HTML)

    def test_guide_topics_have_unique_required_fields(self):
        topic_ids = [topic["id"] for topic in server.GUIDE_TOPICS]

        self.assertEqual(len(topic_ids), len(set(topic_ids)))
        self.assertGreaterEqual(len(topic_ids), 8)
        for topic in server.GUIDE_TOPICS:
            self.assertTrue(topic["id"])
            self.assertTrue(topic["title"])
            self.assertTrue(topic["summary"])
            self.assertTrue(topic["details"])
            self.assertIsInstance(topic["sources"], list)

    def test_guide_topics_payload_exposes_safe_content(self):
        payload = server.guide_topics_payload()

        self.assertEqual(payload[0]["id"], server.GUIDE_TOPICS[0]["id"])
        self.assertIn("title", payload[0])
        self.assertIn("summary", payload[0])
        self.assertIn("details", payload[0])
        self.assertIn("sources", payload[0])
        self.assertNotIn("Guide Explainer", str(payload))
        self.assertNotIn("api_key", str(payload).lower())

    def test_guide_explainer_messages_are_source_grounded(self):
        topic = server.get_guide_topic("poq")
        bundle = server.build_guide_source_bundle(topic, server.pathlib.Path(__file__).resolve().parent)
        messages = server.build_guide_explainer_messages(topic, bundle)

        system = messages[0]["content"]
        user = messages[-1]["content"]
        self.assertIn("Guide Explainer", system)
        self.assertIn("only from the provided source excerpts", system)
        self.assertIn("not covered in the provided sources", system)
        self.assertIn("Source excerpts", user)
        self.assertIn(topic["title"], user)

    def test_missing_guide_topic_raises_key_error(self):
        with self.assertRaises(KeyError):
            server.get_guide_topic("missing-topic")

    def test_guide_explanation_falls_back_without_unsupported_claims(self):
        topic = server.get_guide_topic("poq")
        bundle = server.build_guide_source_bundle(topic, server.pathlib.Path(__file__).resolve().parent)

        content = server.deterministic_guide_explanation(topic, bundle, openrouter_error="OpenRouter HTTP 429")

        self.assertIn(topic["title"], content)
        self.assertIn("Sources used", content)
        self.assertIn("OpenRouter unavailable", content)
        self.assertNotIn("I assume", content)

    def test_guide_source_lookup_stays_inside_app_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = server.pathlib.Path(temp)
            (root / "README.md").write_text("local app readme", encoding="utf-8")

            self.assertIsNotNone(server._doc_path(root, "README.md"))
            self.assertIsNone(server._doc_path(root, "../OUTSIDE.md"))

    def test_guide_ui_has_explain_buttons_and_settings_view(self):
        self.assertIn('id="nav-settings"', server.HTML)
        self.assertIn('class="settings-icon"', server.HTML)
        self.assertIn('id="settings-view"', server.HTML)
        self.assertIn("renderGuideTopics", server.HTML)
        self.assertIn("explain-guide-topic", server.HTML)

    def test_openrouter_controls_are_not_in_left_rail(self):
        rail_start = server.HTML.index('<aside class="rail">')
        rail_end = server.HTML.index('</aside>', rail_start)
        rail_html = server.HTML[rail_start:rail_end]

        self.assertNotIn('id="api-key"', rail_html)
        self.assertNotIn('id="model"', rail_html)
        self.assertNotIn('id="test-openrouter"', rail_html)

    def test_thought_styling_is_inline_and_unlabeled(self):
        self.assertNotIn('content: "thought"', server.HTML)
        self.assertIn(".thought-segment {", server.HTML)
        self.assertIn("display: inline", server.HTML)
        self.assertIn('<span class="${part.type === \'thought\' ? \'thought-segment\' : \'text-segment\'}"', server.HTML)


if __name__ == "__main__":
    unittest.main()
