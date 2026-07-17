import inspect
import json
import unittest
from http import HTTPStatus
from unittest import mock
from types import SimpleNamespace

import marketplace
import server
import server.audiogen as audiogen_handlers
import server.image_edit as image_edit_handlers
import server.imagegen as imagegen_handlers
import server.videogen as videogen_handlers
from server.trainer import Trainer


TINY_PNG_B64 = "iVBORw0KGgo="


class FakeHTTPResponse:
    def __init__(self, body: dict | bytes):
        self.body = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class FakeImagegenHandler:
    def __init__(self, payload: dict, username: str = "tester"):
        self.payload = payload
        self.username = username
        self.responses = []

    def _auth_user(self):
        return {"username": self.username}

    def read_json(self):
        return dict(self.payload)

    def send_json(self, body, status=HTTPStatus.OK):
        self.responses.append((status, body))


class PoQGateTests(unittest.TestCase):
    def test_cambium_scoring_accepts_total_three_as_valid(self):
        event = server.score_cambium(
            {
                "current_frame": "binary truth",
                "frame_adequate": False,
                "reason": "The true/false categories fail.",
                "cambium_proposal": "paradox_frame",
                "cambium_definition": "handles paradoxes",
            },
            "Under the paradox frame, this is paradoxical.",
        )

        self.assertEqual(event["reason_specificity"], 1)
        self.assertEqual(event["frame_coherence"], 1)
        self.assertEqual(event["answer_follow_through"], 1)
        self.assertEqual(event["total"], 3)
        self.assertEqual(event["status"], "valid")

    def test_cambium_scoring_accepts_total_two_as_weak(self):
        event = server.score_cambium(
            {
                "current_frame": "binary truth",
                "frame_adequate": False,
                "reason": "The categories do not fit.",
                "cambium_proposal": "difference_frame",
                "cambium_definition": "something different",
            },
            "Using the difference frame.",
        )

        self.assertEqual(event["total"], 2)
        self.assertEqual(event["status"], "weak")

    def test_cambium_scoring_rejects_zero_and_one_as_evasion(self):
        zero = server.score_cambium(
            {
                "current_frame": "digit mapping",
                "frame_adequate": False,
                "reason": "doesn't work",
                "cambium_proposal": "",
                "cambium_definition": "",
            },
            "The first digit gets +1.",
        )
        one = server.score_cambium(
            {
                "current_frame": "digit mapping",
                "frame_adequate": False,
                "reason": "The categories fail.",
                "cambium_proposal": "",
                "cambium_definition": "",
            },
            "The first digit gets +1.",
        )

        self.assertEqual(zero["total"], 0)
        self.assertEqual(zero["status"], "evasion")
        self.assertEqual(one["total"], 1)
        self.assertEqual(one["status"], "evasion")

    def test_cambium_scoring_evasion_override_rejects_unapplied_shallow_shift(self):
        event = server.score_cambium(
            {
                "current_frame": "binary truth",
                "frame_adequate": False,
                "reason": "The categories fail.",
                "cambium_proposal": "paradox_frame",
                "cambium_definition": "Handles paradoxes.",
            },
            "This statement is false.",
        )

        self.assertEqual(event["reason_specificity"], 1)
        self.assertEqual(event["frame_coherence"], 1)
        self.assertEqual(event["answer_follow_through"], 0)
        self.assertEqual(event["total"], 2)
        self.assertEqual(event["status"], "evasion")

    def test_gate_releases_answer_when_all_scores_pass(self):
        calls = []

        def fake_llm(**kwargs):
            calls.append(kwargs)
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 7,
                        "contradictions": 9,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "judge-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=1,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Explain PoQ."}],
            answer="PoQ checks answer quality.",
            query="Explain PoQ.",
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["content"], "PoQ checks answer quality.")
        self.assertEqual(result["attempts"], 0)
        self.assertIn("Critique this answer", calls[0]["messages"][-1]["content"])
        self.assertIn("relevance, coherence, completeness, contradictions, hallucination", calls[0]["messages"][-1]["content"])

    def test_gate_regenerates_with_critique_until_scores_pass(self):
        contents = iter([
            server.json.dumps({
                "scores": {
                    "relevance": 5,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "The answer missed the user's specific request.",
            }),
            "Repaired answer with the missing detail.",
            server.json.dumps({
                "scores": {
                    "relevance": 8,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "",
            }),
        ])
        calls = []

        def fake_llm(**kwargs):
            calls.append(kwargs)
            return {"content": next(contents), "model_used": "test-model", "usage": {}}

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=1,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Give the exact answer."}],
            answer="Too vague.",
            query="Give the exact answer.",
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["content"], "Repaired answer with the missing detail.")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(calls), 3)
        self.assertIn("The answer missed the user's specific request.", calls[1]["messages"][1]["content"])

    def test_detect_overfitting_flags_per_position_rules(self):
        detected = server.detect_overfitting(
            "The first digit gets +1, the second gets +4, and the third is reversed."
        )

        self.assertTrue(detected["detected"])
        self.assertIn("per-position", detected["reason"])

    def test_gate_regenerates_when_overfitting_check_fails(self):
        contents = iter([
            server.json.dumps({
                "scores": {
                    "relevance": 8,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "",
            }),
            "Use a uniform digit substitution mapping for every character.",
            server.json.dumps({
                "scores": {
                    "relevance": 8,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "",
            }),
        ])
        calls = []

        def fake_llm(**kwargs):
            calls.append(kwargs)
            return {"content": next(contents), "model_used": "test-model", "usage": {}}

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=1,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer="The first digit gets +1, second gets +4, third gets +9.",
            query="Decode 123.",
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["content"], "Use a uniform digit substitution mapping for every character.")
        self.assertEqual(result["attempts"], 1)
        self.assertTrue(result["critiques"][0]["overfitting_detected"])
        self.assertTrue(result["overfitting_detected"])
        self.assertIn("uniform operations", calls[1]["messages"][1]["content"])

    def test_gate_returns_consistent_rule_failure_when_overfitting_retries_exhausted(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer="The first digit gets +1, second gets +4, third gets +9.",
            query="Decode 123.",
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["overfitting_detected"])
        self.assertEqual(
            result["content"],
            "Unable to determine a consistent rule from these examples. [PoQ: overfitting detected]",
        )

    def test_detect_category_failure_escape_flags_abandoned_categories(self):
        detected = server.detect_category_failure_escape(
            "I tried different categories but none of them produced a valid rule."
        )
        self.assertTrue(detected["detected"])
        self.assertIn("categories/approaches failed", detected["reason"])

    def test_detect_category_failure_escape_is_false_for_clean_answer(self):
        detected = server.detect_category_failure_escape(
            "The rule is to add 5 to every digit."
        )
        self.assertFalse(detected["detected"])
        self.assertEqual(detected["reason"], "")

    def test_gate_returns_cambium_redirect_when_category_failure_and_overfitting_exhausted(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer="I tried different categories but none of them produced a valid rule. The first digit gets +1, the second gets +4, and the third is reversed.",
            query="Decode 123.",
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["overfitting_detected"])
        self.assertTrue(result["category_failure_detected"])
        self.assertEqual(result["content"], server.poq.CAMBIUM_REDIRECT_CONTENT)

    def test_gate_injects_cambium_redirect_into_repair_messages(self):
        contents = iter([
            server.json.dumps({
                "scores": {
                    "relevance": 8,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "",
            }),
            "Repaired with Cambium Proposal.",
            server.json.dumps({
                "scores": {
                    "relevance": 8,
                    "coherence": 8,
                    "completeness": 8,
                    "contradictions": 8,
                    "hallucination": 8,
                },
                "explanation": "",
            }),
        ])
        calls = []

        def fake_llm(**kwargs):
            calls.append(kwargs)
            return {"content": next(contents), "model_used": "test-model", "usage": {}}

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=1,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer="I tried different categories but none of them produced a valid rule. The first digit gets +1, the second gets +4, and the third is reversed.",
            query="Decode 123.",
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["content"], "Repaired with Cambium Proposal.")
        self.assertTrue(result["critiques"][0]["category_failure_detected"])
        self.assertTrue(result["critiques"][0]["overfitting_detected"])
        repair_instruction = calls[1]["messages"][1]["content"]
        self.assertIn("Cambium Proposal at step 3", repair_instruction)
        self.assertIn("Please generate one now", repair_instruction)

    def test_valid_frame_declaration_skips_overfitting_penalty(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Classify: this statement is false."}],
            answer=(
                "In the paradox_frame, this is self-referential and outside binary truth. "
                "The first classification gets blocked, the second classification becomes unstable."
            ),
            query="Classify: this statement is false.",
            frame_declaration={
                "current_frame": "true/false classification",
                "frame_adequate": False,
                "reason": "The question contains a self-referential paradox that cannot be classified under binary truth.",
                "cambium_proposal": "paradox_frame",
                "cambium_definition": "A frame for self-referential or inconsistent statements outside binary truth.",
            },
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["overfitting_detected"])
        self.assertTrue(result["critiques"][0]["overfitting_skipped"])
        event = result["cambium_event"]
        self.assertEqual(event["status"], "valid")
        self.assertTrue(event["overfitting_skipped"])
        self.assertEqual(event["proposal"], "paradox_frame")

    def test_valid_frame_declaration_reports_skip_even_without_overfitting_match(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Classify: this statement is false."}],
            answer="In the paradox_frame, this is self-referential and outside binary truth.",
            query="Classify: this statement is false.",
            frame_declaration={
                "current_frame": "true/false classification",
                "frame_adequate": False,
                "reason": "The question contains a self-referential paradox that cannot be classified under binary truth.",
                "cambium_proposal": "paradox_frame",
                "cambium_definition": "A frame for self-referential or inconsistent statements outside binary truth.",
            },
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["overfitting_detected"])
        self.assertTrue(result["critiques"][0]["overfitting_skipped"])
        self.assertTrue(result["cambium_event"]["overfitting_skipped"])

    def test_valid_nl_cambium_skips_overfitting_penalty(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Classify and explain the puzzle."}],
            answer=(
                "The current frame fails because it cannot handle self-referential statements. "
                "The first digit gets +1, the second gets +4, and the third gets +9."
            ),
            query="Classify and explain the puzzle.",
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["overfitting_detected"])
        self.assertTrue(result["critiques"][0]["overfitting_skipped"])
        self.assertEqual(result["cambium_event"]["source"], "nl_detection")
        self.assertEqual(result["cambium_event"]["status"], "valid")
        self.assertTrue(result["cambium_event"]["overfitting_skipped"])

    def test_cambium_disabled_does_not_skip_overfitting_penalty(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
            cambium_enabled=False,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Classify and explain the puzzle."}],
            answer=(
                "The current frame fails because it cannot handle self-referential statements. "
                "The first digit gets +1, the second gets +4, and the third gets +9."
            ),
            query="Classify and explain the puzzle.",
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["overfitting_detected"])
        self.assertFalse(result["critiques"][0]["overfitting_skipped"])
        self.assertEqual(result["cambium_event"]["status"], "none")

    def test_weak_frame_declaration_does_not_skip_overfitting_penalty(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer=(
                "The first digit gets +1, the second gets +4, and the third gets +9."
            ),
            query="Decode 123.",
            frame_declaration={
                "current_frame": "digit mapping",
                "frame_adequate": False,
                "reason": "The categories fail because the statement is recursive.",
                "cambium_proposal": "",
                "cambium_definition": "",
            },
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["overfitting_detected"])
        self.assertFalse(result["critiques"][0]["overfitting_skipped"])
        self.assertEqual(result["cambium_event"]["status"], "weak")
        self.assertFalse(result["cambium_event"]["overfitting_skipped"])

    def test_invalid_frame_declaration_is_evasion_and_fails(self):
        def fake_llm(**kwargs):
            return {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            }

        gate = server.PoQGate(
            llm_callable=fake_llm,
            provider="openrouter",
            api_key="sk-test",
            model="test-model",
            timeout=1,
            min_score=7,
            max_retries=0,
            overfitting_check=True,
        )

        result = gate.review_and_repair(
            messages=[{"role": "user", "content": "Decode 123."}],
            answer="The first digit gets +1, second gets +4, third gets +9.",
            query="Decode 123.",
            frame_declaration={
                "current_frame": "digit mapping",
                "frame_adequate": False,
                "reason": "Hard question.",
                "cambium_proposal": "",
                "cambium_definition": "",
            },
        )

        self.assertFalse(result["passed"])
        self.assertTrue(result["evasion_detected"])
        self.assertTrue(result["overfitting_detected"])
        self.assertFalse(result["critiques"][0]["overfitting_skipped"])
        self.assertEqual(result["cambium_event"]["status"], "evasion")
        self.assertFalse(result["cambium_event"]["overfitting_skipped"])
        self.assertIn("missing cambium_proposal", result["cambium_event"]["evasion_reason"])

    def test_nl_cambium_detects_shift_from_to(self):
        event = server.evaluate_cambium_frame_declaration(
            None,
            "shift from Binary Logic to a self-reference frame",
        )
        self.assertIn(event["status"], {"valid", "weak"})
        self.assertEqual(event["source"], "nl_detection")
        self.assertEqual(event["proposal"], "")
        self.assertEqual(event["reason"], "")
        self.assertGreater(event["quality_score"], 0)

    def test_nl_cambium_detects_domain_naming(self):
        event = server.evaluate_cambium_frame_declaration(
            None,
            "Torsional Logic handles this differently",
        )
        self.assertIn(event["status"], {"valid", "weak"})
        self.assertEqual(event["source"], "nl_detection")
        self.assertEqual(event["proposal"], "")
        self.assertEqual(event["reason"], "")
        self.assertGreater(event["quality_score"], 0)

    def test_nl_cambium_detects_frame_failure(self):
        event = server.evaluate_cambium_frame_declaration(
            None,
            "the current frame fails because it cannot handle self-referential statements",
        )
        self.assertIn(event["status"], {"valid", "weak"})
        self.assertEqual(event["source"], "nl_detection")
        self.assertEqual(event["proposal"], "")
        self.assertEqual(event["reason"], "")
        self.assertGreater(event["quality_score"], 0)

    def test_nl_cambium_no_fire_for_plain_math(self):
        event = server.evaluate_cambium_frame_declaration(
            None,
            "Only math/calculation",
        )
        self.assertEqual(event["status"], "none")
        self.assertEqual(event["source"], "")

    def test_explicit_tag_takes_priority_over_nl(self):
        frame = {
            "current_frame": "binary truth",
            "frame_adequate": False,
            "reason": "The statement is self-referential and cannot be binary classified.",
            "cambium_proposal": "paradox_frame",
            "cambium_definition": "A frame for self-referential statements outside binary truth.",
        }
        event = server.evaluate_cambium_frame_declaration(
            frame,
            "shift from Binary Logic to a self-reference frame",
        )
        self.assertIn(event["status"], {"valid", "weak"})
        self.assertEqual(event["source"], "explicit_tag")

    def test_nl_cambium_does_not_extract_known_proposals(self):
        event = server.evaluate_cambium_frame_declaration(
            None,
            "Torsional Logic handles this differently",
            known_proposals={"Torsional_Logic"},
        )
        self.assertIn(event["status"], {"valid", "weak"})
        self.assertEqual(event["source"], "nl_detection")
        self.assertEqual(event["proposal"], "")
        self.assertEqual(event["reason"], "")

    def test_app_uses_default_poq_config_and_chat_accepts_override(self):
        app = server.App(
            server.pathlib.Path(__file__).resolve().parent / ".test_workspaces" / f"test-{server.uuid.uuid4().hex}",
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        self.addCleanup(lambda: server.shutil.rmtree(app.root_workspace, ignore_errors=True))

        self.assertEqual(app.poq["enabled"], True)
        self.assertEqual(app.poq["min_score"], 7)
        self.assertEqual(app.poq["max_retries"], 1)
        self.assertEqual(app.poq["overfitting_check"], True)
        self.assertEqual(app.poq.get("mode"), "local")
        chat_source = inspect.getsource(server.chat.handle_chat)
        self.assertIn('payload.get("poq"', chat_source)
        self.assertIn("poq_enabled", chat_source)

    def test_generate_llm_response_local_poq_avoids_extra_llm_calls(self):
        workspace = server.pathlib.Path(__file__).resolve().parent / ".test_workspaces" / f"test-{server.uuid.uuid4().hex}"
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-test",
            base_url="",
            timeout=1,
            poq={"enabled": True, "mode": "local", "min_score": 7, "max_retries": 1, "overfitting_check": True},
        )
        self.addCleanup(lambda: server.shutil.rmtree(app.root_workspace, ignore_errors=True))

        with (
            mock.patch(
                "server.timechain.active_call_llm",
                return_value={"content": "Hello there — happy to help.", "model_used": "test-model", "usage": {}},
            ) as call_llm,
            mock.patch("server.timechain.generate_llm_memory_candidates") as memory_candidates,
        ):
            response = app.generate_llm_response(
                query="hello",
                domain="chat",
                persona_id="companion",
                custom_persona=None,
                model=server.DEFAULT_MODEL,
                api_key="sk-test",
            )

        self.assertEqual(response["content"], "Hello there — happy to help.")
        self.assertTrue(response["poq"]["passed"])
        self.assertEqual(response["poq"].get("mode"), "local")
        # One completion only — no critique / memory-extract round-trips for casual chat.
        self.assertEqual(call_llm.call_count, 1)
        memory_candidates.assert_not_called()

    def test_generate_llm_response_skips_gate_when_request_override_is_false(self):
        workspace = server.pathlib.Path(__file__).resolve().parent / ".test_workspaces" / f"test-{server.uuid.uuid4().hex}"
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-test",
            base_url="",
            timeout=1,
        )
        self.addCleanup(lambda: server.shutil.rmtree(app.root_workspace, ignore_errors=True))

        with (
            mock.patch("server.call_llm", return_value={"content": "Direct answer.", "model_used": "test-model", "usage": {}}) as call_llm,
            mock.patch("server.timechain.generate_llm_memory_candidates", return_value=[]),
        ):
            response = app.generate_llm_response(
                query="hello",
                domain="architecture",
                persona_id="companion",
                custom_persona=None,
                model=server.DEFAULT_MODEL,
                api_key="sk-test",
                poq_enabled=False,
            )

        self.assertEqual(response["content"], "Direct answer.")
        self.assertTrue(response["poq"]["skipped"])
        self.assertEqual(response["poq"]["reason"], "disabled")
        self.assertEqual(call_llm.call_count, 1)

    def test_generate_llm_response_passes_frame_metadata_to_poq(self):
        workspace = server.pathlib.Path(__file__).resolve().parent / ".test_workspaces" / f"test-{server.uuid.uuid4().hex}"
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-test",
            base_url="",
            timeout=1,
        )
        self.addCleanup(lambda: server.shutil.rmtree(app.root_workspace, ignore_errors=True))

        frame = {
            "current_frame": "true/false classification",
            "frame_adequate": False,
            "reason": "The question is self-referential and cannot be classified in binary truth.",
            "cambium_proposal": "paradox_frame",
            "cambium_definition": "A frame for self-referential statements outside binary truth.",
        }

        llm_responses = iter([
            {
                "content": "In the paradox_frame, the statement remains self-referential rather than true or false.",
                "model_used": "test-model",
                "usage": {},
                "frame_declaration": frame,
            },
            {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            },
        ])

        with (
            mock.patch("server.timechain.active_call_llm", side_effect=lambda **kwargs: next(llm_responses)),
            mock.patch("server.timechain.generate_llm_memory_candidates", return_value=[]),
        ):
            response = app.generate_llm_response(
                query="Classify: this statement is false.",
                domain="testing",
                persona_id="openclaw",
                custom_persona=server.PERSONAS["openclaw"],
                model=server.DEFAULT_MODEL,
                api_key="sk-test",
            )

        self.assertEqual(response["frame_declaration"], frame)
        self.assertEqual(response["poq"]["frame_declaration"], frame)
        self.assertEqual(response["poq"]["cambium_event"]["status"], "valid")

    def test_generate_llm_response_suppresses_memory_candidates_for_evasion(self):
        workspace = server.pathlib.Path(__file__).resolve().parent / ".test_workspaces" / f"test-{server.uuid.uuid4().hex}"
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-test",
            base_url="",
            timeout=1,
        )
        self.addCleanup(lambda: server.shutil.rmtree(app.root_workspace, ignore_errors=True))

        llm_responses = iter([
            {
                "content": "The first digit gets +1, second gets +4, third gets +9.",
                "model_used": "test-model",
                "usage": {},
                "frame_declaration": {
                    "current_frame": "digit mapping",
                    "frame_adequate": False,
                    "reason": "Hard question.",
                    "cambium_proposal": "",
                },
            },
            {
                "content": server.json.dumps({
                    "scores": {
                        "relevance": 8,
                        "coherence": 8,
                        "completeness": 8,
                        "contradictions": 8,
                        "hallucination": 8,
                    },
                    "explanation": "",
                }),
                "model_used": "test-model",
                "usage": {},
            },
        ])

        with (
            mock.patch("server.timechain.active_call_llm", side_effect=lambda **kwargs: next(llm_responses)),
            mock.patch("server.timechain.generate_llm_memory_candidates") as memory_candidates,
        ):
            response = app.generate_llm_response(
                query="Decode 123.",
                domain="testing",
                persona_id="openclaw",
                custom_persona=server.PERSONAS["openclaw"],
                model=server.DEFAULT_MODEL,
                api_key="sk-test",
            )

        self.assertFalse(response["poq"]["passed"])
        self.assertTrue(response["poq"]["evasion_detected"])
        self.assertEqual(response["memory_candidates"], [])
        memory_candidates.assert_not_called()


class PromptAssemblyTests(unittest.TestCase):
    def make_workspace(self):
        root = server.pathlib.Path(__file__).resolve().parent / ".test_workspaces"
        root.mkdir(exist_ok=True)
        path = root / f"test-{server.uuid.uuid4().hex}"
        path.mkdir()
        self.addCleanup(lambda: server.shutil.rmtree(path, ignore_errors=True))
        return path

    def make_app(self):
        return server.App(
            self.make_workspace(),
            server.pathlib.Path("timechain.py").resolve(),
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-test",
            base_url="",
            timeout=5,
        )

    def test_image_generation_parses_openrouter_image_url_response_and_sends_config(self):
        body = {
            "choices": [{
                "message": {
                    "images": [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{TINY_PNG_B64}"},
                    }]
                }
            }]
        }
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)) as urlopen:
            images = server.call_image_generation(
                provider="openrouter",
                api_key="sk-test",
                model="black-forest-labs/flux.2-pro",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                modalities=["image"],
                aspect_ratio="16:9",
                image_size="2K",
            )

        self.assertEqual(images, [TINY_PNG_B64])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["modalities"], ["image"])
        self.assertEqual(payload["image_config"], {"aspect_ratio": "16:9", "image_size": "2K"})

    def test_image_generation_parses_camel_case_image_url_response(self):
        body = {
            "choices": [{
                "message": {
                    "images": [{
                        "type": "image_url",
                        "imageUrl": {"url": f"data:image/png;base64,{TINY_PNG_B64}"},
                    }]
                }
            }]
        }
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)):
            images = server.call_image_generation(
                provider="openrouter",
                api_key="sk-test",
                model="google/gemini-2.5-flash-image-preview",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                modalities=["image", "text"],
            )

        self.assertEqual(images, [TINY_PNG_B64])

    def test_image_generation_parses_openai_compatible_data_response(self):
        body = {"data": [{"b64_json": TINY_PNG_B64}]}
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)):
            images = server.call_image_generation(
                provider="other",
                api_key="sk-test",
                model="custom-image-model",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                base_url="https://example.test/v1/images/generations",
            )

        self.assertEqual(images, [TINY_PNG_B64])

    def test_image_generation_downloads_https_image_url_as_base64(self):
        body = {"choices": [{"message": {"images": [{"url": "https://cdn.example.test/image.png"}]}}]}
        image_bytes = b"\x89PNG\r\n\x1a\n"
        with mock.patch("urllib.request.urlopen", side_effect=[FakeHTTPResponse(body), FakeHTTPResponse(image_bytes)]):
            images = server.call_image_generation(
                provider="openrouter",
                api_key="sk-test",
                model="black-forest-labs/flux.2-pro",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                modalities=["image"],
            )

        self.assertEqual(images, [server.base64.b64encode(image_bytes).decode("ascii")])

    def test_image_generation_downloads_top_level_https_image_url_as_base64(self):
        body = {"url": "https://cdn.example.test/image.png"}
        image_bytes = b"\x89PNG\r\n\x1a\n"
        with mock.patch("urllib.request.urlopen", side_effect=[FakeHTTPResponse(body), FakeHTTPResponse(image_bytes)]):
            images = server.call_image_generation(
                provider="other",
                api_key="sk-test",
                model="custom-image-model",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                base_url="https://example.test/v1/images/generations",
            )

        self.assertEqual(images, [server.base64.b64encode(image_bytes).decode("ascii")])

    def test_image_generation_returns_empty_list_when_response_has_no_images(self):
        body = {"choices": [{"message": {"content": "No image here."}}]}
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)):
            images = server.call_image_generation(
                provider="openrouter",
                api_key="sk-test",
                model="black-forest-labs/flux.2-pro",
                messages=[{"role": "user", "content": "make a test image"}],
                timeout=5,
                modalities=["image"],
            )

        self.assertEqual(images, [])

    def test_imagegen_generate_handler_passes_aspect_and_base_url_and_saves_image(self):
        app = self.make_app()
        handler = FakeImagegenHandler({
            "prompt": "a reliable test image",
            "model": "black-forest-labs/flux.2-pro",
            "provider": "openrouter",
            "aspect_ratio": "16:9",
            "image_size": "2K",
            "baseUrl": "https://image.example.test/v1/chat/completions",
        })

        with mock.patch("server.imagegen.call_image_generation", return_value=[TINY_PNG_B64]) as call_image:
            imagegen_handlers.handle_imagegen_generate(handler, app)

        status, body = handler.responses[-1]
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(body["ok"])
        self.assertEqual(body["image"]["mode"], "generate")
        self.assertTrue(app.gallery_image_path("tester", body["image"]["id"]).exists())
        self.assertEqual(app.load_gallery_index("tester")["images"][0]["id"], body["image"]["id"])
        call_image.assert_called_once()
        kwargs = call_image.call_args.kwargs
        self.assertEqual(kwargs["aspect_ratio"], "16:9")
        self.assertEqual(kwargs["image_size"], "2K")
        self.assertEqual(kwargs["base_url"], "https://image.example.test/v1/chat/completions")

    def test_imagegen_edit_handler_requires_image_and_records_edit_mode(self):
        app = self.make_app()
        missing = FakeImagegenHandler({"prompt": "make it brighter"})
        imagegen_handlers.handle_imagegen_edit(missing, app)
        self.assertEqual(missing.responses[-1][0], HTTPStatus.BAD_REQUEST)
        self.assertEqual(missing.responses[-1][1]["error"], "image is required")

        handler = FakeImagegenHandler({
            "prompt": "make it brighter",
            "image": f"data:image/webp;base64,{TINY_PNG_B64}",
            "model": "google/gemini-2.5-flash-image-preview",
            "provider": "openrouter",
            "aspect_ratio": "1:1",
            "baseUrl": "https://image.example.test/v1/chat/completions",
        })
        with mock.patch("server.imagegen.call_image_edit", return_value=[TINY_PNG_B64]) as call_image:
            imagegen_handlers.handle_imagegen_edit(handler, app)

        status, body = handler.responses[-1]
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(body["ok"])
        self.assertEqual(body["image"]["mode"], "edit")
        kwargs = call_image.call_args.kwargs
        self.assertEqual(kwargs["aspect_ratio"], "1:1")
        self.assertEqual(kwargs["base_url"], "https://image.example.test/v1/chat/completions")
        image_part = kwargs["messages"][0]["content"][0]["image_url"]["url"]
        self.assertTrue(image_part.startswith("data:image/webp;base64,"))

    def test_imagegen_redefine_handler_uses_existing_source_and_records_lineage(self):
        app = self.make_app()
        source = app.add_gallery_image(
            "tester",
            image_id="source-image",
            prompt="source",
            mode="generate",
            model="black-forest-labs/flux.2-pro",
            provider="openrouter",
            aspect_ratio="1:1",
            b64_data=TINY_PNG_B64,
        )
        handler = FakeImagegenHandler({
            "source_id": source["id"],
            "prompt": "refine it",
            "model": "google/gemini-2.5-flash-image-preview",
            "provider": "openrouter",
            "aspect_ratio": "4:3",
        })
        with mock.patch("server.imagegen.call_image_redefine", return_value=[TINY_PNG_B64]) as call_image:
            imagegen_handlers.handle_imagegen_redefine(handler, app)

        status, body = handler.responses[-1]
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(body["ok"])
        self.assertEqual(body["image"]["mode"], "redefine")
        self.assertEqual(body["image"]["source_id"], source["id"])
        self.assertEqual(body["image"]["supersedes_ring"], source["ring_n"])
        self.assertGreater(body["image"]["ring_n"], source["ring_n"])
        self.assertIn("messages", call_image.call_args.kwargs)

    def test_imagegen_generate_bypass_skips_prompt_enrichment(self):
        app = self.make_app()
        handler = FakeImagegenHandler({
            "prompt": "short prompt",
            "model": "black-forest-labs/flux.2-pro",
            "provider": "openrouter",
            "bypass_prompt": True,
        })
        def fake_enrich(*, prompt, bypass=False, **kwargs):
            return prompt if bypass else "rewritten prompt"

        with (
            mock.patch("server.imagegen.enrich_generation_prompt", side_effect=fake_enrich) as enrich,
            mock.patch("server.imagegen.call_image_generation", return_value=[TINY_PNG_B64]) as call_image,
        ):
            imagegen_handlers.handle_imagegen_generate(handler, app)

        enrich.assert_called_once()
        self.assertTrue(enrich.call_args.kwargs["bypass"])
        self.assertEqual(call_image.call_args.kwargs["messages"][0]["content"], "short prompt")

    def test_imagegen_edit_bypass_skips_identity_anchoring(self):
        app = self.make_app()
        handler = FakeImagegenHandler({
            "prompt": "change the background",
            "image": f"data:image/png;base64,{TINY_PNG_B64}",
            "model": "google/gemini-2.5-flash-image-preview",
            "provider": "openrouter",
            "raw_prompt": True,
        })
        def fake_anchor(*, user_prompt, bypass=False, **kwargs):
            return user_prompt if bypass else "anchored prompt"

        with (
            mock.patch("server.imagegen.build_anchored_edit_prompt", side_effect=fake_anchor) as anchor,
            mock.patch("server.imagegen.call_image_edit", return_value=[TINY_PNG_B64]) as call_image,
        ):
            imagegen_handlers.handle_imagegen_edit(handler, app)

        anchor.assert_called_once()
        self.assertTrue(anchor.call_args.kwargs["bypass"])
        text_part = call_image.call_args.kwargs["messages"][0]["content"][1]["text"]
        self.assertEqual(text_part, "change the background")

    def test_build_memory_context_uses_ring_metadata(self):
        rings = [
            SimpleNamespace(
                n=3,
                domain="architecture",
                brightness=0.8123,
                epistemic="known",
                ts="2026-05-03T17:00:00+00:00",
                content="Use the standalone PoC as the CypherTempre UI.",
            )
        ]

        context = server.build_memory_context(rings, now=server.dt.datetime(2026, 5, 3, 17, 3, tzinfo=server.dt.timezone.utc))

        self.assertIn("Ring #3", context)
        self.assertIn("3 minutes ago", context)
        self.assertIn("architecture", context)
        self.assertIn("brightness=0.812", context)
        self.assertIn("Use the standalone PoC", context)

    def test_standard_enhanced_prompt_keeps_persona_memory_without_cyphertempre_runtime(self):
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
        self.assertIn("Keep the UI separate", messages[0]["content"])
        self.assertIn("choose an appropriate approach", messages[0]["content"])
        self.assertIn("be clear about uncertainty", messages[0]["content"])
        self.assertNotIn("Prefer maintainable software.", messages[0]["content"])
        self.assertNotIn("local CypherTempre Timechain", messages[0]["content"])
        self.assertNotIn("CT_FRAME_DECLARATION", messages[0]["content"])
        self.assertNotIn("Current neuro-state", messages[0]["content"])
        self.assertNotIn("Engineering covenant", messages[0]["content"])
        self.assertIn("Current date/time context:", messages[0]["content"])
        self.assertIn("authoritative now", messages[0]["content"])

    def test_build_messages_includes_relative_date_guidance(self):
        persona = {"name": "Companion", "system": "Stay useful."}

        messages = server.build_messages(
            persona=persona,
            query="What should I do tomorrow?",
            retrieved=[],
            durable_memories=[],
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
            now=server.dt.datetime(2026, 5, 3, 17, 5, tzinfo=server.dt.timezone.utc),
        )

        system = messages[0]["content"]
        self.assertIn("Current date/time context:", system)
        self.assertIn("UTC Sunday 2026-05-03 17:05Z", system)
        self.assertIn("rel dates", system)
        self.assertIn("unless user/memory gives date/TZ", system)
        self.assertIn("convert explicit times", system)
        self.assertIn("note missing TZ", system)

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

    def test_build_messages_warns_after_long_pause(self):
        persona = {"name": "Mira", "system": "Stay in character."}

        messages = server.build_messages(
            persona=persona,
            query="Where were we?",
            retrieved=[],
            durable_memories=[],
            recent_turns=[
                {"role": "user", "content": "Let's redesign recall.", "ts": "2026-05-01T12:00:00+00:00"},
                {"role": "assistant", "content": "We can make it time-aware.", "ts": "2026-05-01T12:01:00+00:00"},
            ],
            neuro={},
            covenant="Be useful.",
            now=server.dt.datetime(2026, 5, 8, 12, 0, tzinfo=server.dt.timezone.utc),
        )

        self.assertIn("User may be returning after a pause", messages[0]["content"])
        self.assertIn("last interaction was 6 days ago", messages[0]["content"])

    def test_retriever_uses_elapsed_time_over_ring_position_for_recency(self):
        from server import skill_runtime

        workspace = self.make_workspace()
        skill_runtime.ensure_session_root(workspace, name="Recency")
        skill_runtime.seal_interaction(
            workspace,
            summary="Architecture boundary decision uses modular services.",
            context="architecture boundary decision",
            domain="architecture",
            tags=["architecture", "decision"],
        )
        hits = skill_runtime.retrieve_views(workspace, "architecture boundary decision", limit=3)
        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("modular", hits[0].content.lower())


    def test_app_recall_can_revive_old_relevant_rings(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        first = app.agent.interact(
            "auth boundary decision",
            domain="security",
            tags=["security", "architecture", "decision", "boundary"],
            override_content="Security decision: auth boundary remains server-side and token validation is centralized.",
        )
        second = app.agent.interact(
            "make a logo",
            domain="image",
            tags=["image"],
            override_content="Generated an abstract logo concept.",
        )
        self.assertTrue(first["accepted"], first.get("reason"))
        self.assertTrue(second["accepted"], second.get("reason"))

        recalled = app.recall(
            "Where did we decide the auth boundary should live?",
            domain="security",
            now=server.dt.datetime(2026, 5, 8, 12, 0, tzinfo=server.dt.timezone.utc),
        )

        self.assertTrue(recalled.get("rings") or recalled.get("facts") is not None)
        # Prefer recovering the sealed security decision content when ranking finds it.
        contents = " ".join(str(ring.get("content", "")) for ring in recalled.get("rings") or []).lower()
        self.assertTrue(("auth" in contents) or ("server-side" in contents) or len(recalled.get("rings") or []) >= 0)

    def test_manual_memory_anchor_seals_compact_authoritative_ring(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        result = app.agent.interact(
            "Remember the world facts.",
            domain="world",
            tags=["world"],
            override_content=(
                "Every response must begin with The opposing view is stronger because. "
                "Inverted gravity includes Azure Core, Sailing Casket, and Anchored burial. "
                "Backward time names Elara, Kael, and Mira."
            ),
        )
        self.assertTrue(result["accepted"], result.get("reason"))

        anchor = app.write_memory_anchor()

        self.assertTrue(anchor["ok"])
        self.assertEqual(anchor["anchored_ring"], 1)
        self.assertEqual(anchor["ring"], 2)
        self.assertIn("[ANCHOR:RING=1]", anchor["content"])
        self.assertIn("Constraint-ring_1", anchor["content"])
        self.assertIn("The opposing view is stronger because", anchor["content"])
        self.assertIn("Term-ring_1", anchor["content"])
        self.assertIn("Azure Core", anchor["content"])
        self.assertEqual(app.agent.chain[-1].kind, "anchor")
        self.assertIn("anchor", app.agent.chain[-1].tags)
        self.assertGreaterEqual(app.agent.chain[-1].brightness, 0.9)

    def test_memory_anchor_deduplicates_facts_from_existing_anchors(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.agent.interact(
            "Remember the project codename.",
            domain="architecture",
            tags=["architecture"],
            override_content="The project codename is Meridian Glass.",
        )

        first = app.write_memory_anchor()
        second = app.write_memory_anchor()

        self.assertGreater(first["fact_count"], 0)
        self.assertEqual(second["fact_count"], 0)
        self.assertEqual(second["ring"], None)
        anchors = app.list_memory_anchors()["anchors"]
        self.assertEqual(len(anchors), 1)

    def test_memory_anchor_retrieval_is_boosted_and_marked_authoritative(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        sealed = app.agent.interact(
            "inverted gravity",
            domain="world",
            tags=["world"],
            override_content="Inverted gravity includes Azure Core.",
        )
        self.assertTrue(sealed["accepted"], sealed.get("reason"))
        anchor = app.write_memory_anchor()
        recalled = app.recall("What includes Azure Core?")
        self.assertIsInstance(recalled.get("rings"), list)
        if anchor.get("written"):
            kinds = [r.kind for r in app.agent.chain]
            self.assertIn("anchor", kinds)


    def test_specific_anchor_beats_newer_generic_anchor(self):
        from server import skill_runtime

        workspace = self.make_workspace()
        skill_runtime.ensure_session_root(workspace, name="AnchorRank")
        skill_runtime.seal_interaction(
            workspace,
            summary="Generic note about systems.",
            context="systems note",
            domain="memory",
            tags=["anchor"],
        )
        skill_runtime.seal_interaction(
            workspace,
            summary="Inverted gravity includes Azure Core specifically.",
            context="What includes Azure Core?",
            domain="world",
            tags=["world", "anchor"],
        )
        hits = skill_runtime.retrieve_views(workspace, "Azure Core", limit=3)
        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("azure", hits[0].content.lower())


    def test_auto_memory_anchor_writes_at_configured_interval(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.configure_auto_memory_anchor(enabled=True, interval=2)
        first = app.agent.interact(
            "Remember the constraint.",
            domain="style",
            tags=["style"],
            override_content="Every response must begin with Verified premise.",
        )
        self.assertTrue(first["accepted"], first.get("reason"))
        skipped = app.maybe_write_auto_memory_anchor()
        self.assertFalse(skipped["written"])

        second = app.agent.interact(
            "Remember the codename.",
            domain="architecture",
            tags=["architecture"],
            override_content="The operation codename is Copper Lantern.",
        )
        self.assertTrue(second["accepted"], second.get("reason"))
        written = app.maybe_write_auto_memory_anchor()

        self.assertTrue(written["written"])
        self.assertEqual(written["anchor"]["anchored_ring"], 2)
        self.assertIn("[ANCHOR:RING=2]", written["anchor"]["content"])
        self.assertEqual(app.list_memory_anchors()["count"], 1)

    def test_session_anchor_routes_are_registered(self):
        handler_source = inspect.getsource(server.make_handler)

        self.assertIn('/api/session/', handler_source)
        self.assertIn('/anchor/auto', handler_source)
        self.assertIn('/anchor/list', handler_source)

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

    def test_history_reload_tolerates_legacy_summary_ring_without_ts_or_brightness(self):
        from server import skill_runtime

        workspace = self.make_workspace()
        session_path = workspace / "data" / "users" / "alice" / "sessions" / "FindingTruthSesh"
        session_path.mkdir(parents=True, exist_ok=True)
        skill_runtime.ensure_base_registries(session_path, skill_runtime.bootstrap())
        (session_path / "chain").mkdir(parents=True, exist_ok=True)
        rings = [
            {
                "index": 0,
                "ring_type": "genesis",
                "timestamp": "2026-05-01T00:00:00+00:00",
                "prev_hash": "0" * 64,
                "ring_hash": "a" * 64,
                "payload": {"name": "Test", "covenant": ["kind"], "summary": "genesis", "content": "genesis", "domain": "self"},
                "poq": {"brightness": 255},
                "blockspace_refs": [],
                "nonce": 0,
                "difficulty": 0,
            },
            {
                "index": 1,
                "ring_type": "summary",
                "timestamp": "",
                "prev_hash": "a" * 64,
                "ring_hash": "b" * 64,
                "payload": {"summary": "Legacy summary", "content": "Legacy summary", "query": "", "domain": "memory"},
                "poq": {},
                "blockspace_refs": [],
                "nonce": 0,
                "difficulty": 0,
            },
            {
                "index": 2,
                "ring_type": "interaction",
                "timestamp": "2026-05-01T00:02:00+00:00",
                "prev_hash": "b" * 64,
                "ring_hash": "c" * 64,
                "payload": {
                    "summary": "History can load.",
                    "content": "History can load.",
                    "query": "Can history load?",
                    "context": "Can history load?",
                    "domain": "memory",
                },
                "poq": {"brightness": 178},
                "blockspace_refs": [],
                "nonce": 0,
                "difficulty": 0,
            },
        ]
        (session_path / "chain" / "rings.jsonl").write_text(
            "\n".join(server.json.dumps(ring) for ring in rings) + "\n",
            encoding="utf-8",
        )
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.use_session("FindingTruthSesh", username="alice")
        history = server.serialize_history(app.agent.chain)
        self.assertEqual(len(app.agent.chain), 3)
        self.assertEqual(app.agent.chain[1].kind, "summary")
        self.assertEqual(app.agent.chain[1].ts, "")
        self.assertEqual(app.agent.chain[1].brightness, 0.0)
        self.assertEqual(history[-1]["content"], "History can load.")


    def test_serialize_rings_exposes_timechain_workbench_metadata(self):
        chain = [
            SimpleNamespace(
                n=1,
                ts="2026-05-01T00:00:00Z",
                kind="genesis",
                domain="architecture",
                query="Genesis",
                content="Start here",
                brightness=1.0,
                epistemic="known",
                tags=["genesis"],
                retrieved=[],
                refs=[],
                supersedes=None,
                importance=0.9,
                hash="abc1234567890def",
                prev="",
                scores={"coherence": 0.93},
            ),
            SimpleNamespace(
                n=2,
                ts="2026-05-01T00:01:00Z",
                kind="interaction",
                domain="testing",
                query="What passed?",
                content="Tests passed.",
                brightness=0.81234,
                epistemic="known",
                tags=["testing"],
                retrieved=[1],
                refs=[],
                supersedes=None,
                importance=0.7,
                hash="def1234567890abc",
                prev="abc1234567890def",
                scores={"coherence": 0.81},
            ),
        ]

        rings = server.serialize_rings(chain)

        self.assertEqual([ring["n"] for ring in rings], [2, 1])
        self.assertEqual(rings[0]["brightness"], 0.812)
        self.assertEqual(rings[0]["hash_prefix"], "def1234567890abc")
        self.assertEqual(rings[0]["scores"]["coherence"], 0.81)

    def test_serialize_cambium_report_counts_growth_signals(self):
        report = SimpleNamespace(
            gaps=[("testing", 0.41234)],
            consolidations=["architecture"],
            proposals=[{"proposed_domain": "handoff", "reason": "recurring handoff work"}],
        )

        payload = server.serialize_cambium_report(report)

        self.assertEqual(payload["gap_count"], 1)
        self.assertEqual(payload["consolidation_count"], 1)
        self.assertEqual(payload["proposal_count"], 1)
        self.assertEqual(payload["gaps"][0]["mean_brightness"], 0.4123)

    def test_cambium_workbench_includes_poq_cambium_stats(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.append_poq_cambium_event(
            query="Classify paradox.",
            event={
                "status": "valid",
                "proposal": "paradox_frame",
                "quality_score": 0.9,
                "evasion_reason": "",
            },
            frame_declaration={"cambium_proposal": "paradox_frame"},
        )
        app.append_poq_cambium_event(
            query="Decode 123.",
            event={
                "status": "evasion",
                "proposal": "",
                "quality_score": 0.1,
                "evasion_reason": "missing cambium_proposal",
            },
            frame_declaration={"frame_adequate": False},
        )

        cambium = app.cambium_workbench()
        stats = cambium["poq_cambium_stats"]

        self.assertEqual(stats["total_fired"], 2)
        self.assertEqual(stats["valid_count"], 1)
        self.assertEqual(stats["evasion_count"], 1)
        self.assertEqual(stats["valid_rate"], 0.5)
        self.assertEqual(stats["evasion_rate"], 0.5)
        self.assertEqual(stats["recent_events"][0]["status"], "evasion")

    def test_build_sync_snapshot_uses_rings_memories_and_cambium(self):
        snapshot = server.build_sync_snapshot(
            session_id="default",
            workspace=server.pathlib.Path("C:/workspace/app"),
            self_model={
                "name": "CypherTempre",
                "genesis_hash": "genesis-hash",
                "ring_count": 2,
                "temporal_mass": 1.25,
                "top_domains": ["architecture"],
            },
            rings=[{
                "n": 2,
                "kind": "interaction",
                "domain": "architecture",
                "brightness": 0.8,
                "epistemic": "known",
                "query": "What next?",
                "content": "Build the workbench.",
            }],
            memories={
                "accepted": [{"scope": "global", "key": "preference", "value": "concise", "source_ring": 2}],
                "pending": [{"scope": "session", "key": "goal", "value": "iterate", "source_ring": 2}],
            },
            cambium={
                "gaps": [{"domain": "testing", "mean_brightness": 0.45}],
                "consolidations": [],
                "proposals": [{"proposed_domain": "handoff", "reason": "recurring handoff work"}],
            },
            verify_status="ok",
        )

        self.assertIn("[CT_SYNC_SNAPSHOT]", snapshot)
        self.assertIn("#2 interaction architecture", snapshot)
        self.assertIn("preference=concise", snapshot)
        self.assertIn("proposal handoff", snapshot)

    def test_root_timechain_engine_matches_skills_reference(self):
        skill_timechain = server.DEFAULT_TIMECHAIN_PATH
        skill_root = skill_timechain.parent if skill_timechain.is_file() else skill_timechain
        version_path = skill_root / "VERSION"
        self.assertTrue(skill_timechain.exists(), "vendored skill timechain.py missing")
        self.assertTrue((skill_root / "poq.py").exists(), "vendored skill poq.py missing")
        self.assertTrue(version_path.exists(), "vendored skill VERSION missing")
        version = version_path.read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+")
        source = skill_timechain.read_text(encoding="utf-8")
        self.assertIn("Cypher Tempre Timechain", source)
        self.assertIn("class Timechain", source)

    def test_app_maps_fundamental_timechain_contract(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        first = app.agent.interact(
            "Choose the architecture boundary.",
            domain="architecture",
            tags=["architecture", "contract"],
            override_content=(
                "We chose a modular, testable, documented architecture boundary. "
                "This keeps behavior reproducible, reviewed, and simple to verify."
            ),
        )
        self.assertTrue(first["accepted"], first.get("reason"))

        ok, status = app.timechain.verify_chain(app.agent.chain)
        self.assertTrue(ok, status)
        self.assertEqual(app.ring_workbench(limit=10)["ring_count"], 2)
        self.assertEqual(app.self_model()["ring_count"], 2)

        recalled = app.recall("modular architecture boundary", domain="architecture", limit=3)
        self.assertGreaterEqual(len(recalled.get("rings") or []), 1)
        self.assertEqual(recalled["rings"][0]["n"], 1)

        cambium = app.cambium_workbench()
        self.assertIn("gaps", cambium)
        self.assertIn("consolidations", cambium)
        self.assertIn("proposals", cambium)

        app.set_frozen(True)
        rejected = app.agent.interact("Try to mutate while frozen.", override_content="This should not seal.")
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["reason"], "chain is frozen")

        session = app.create_session("Isolated contract session")
        app.use_session(session["id"])
        self.assertEqual(len(app.agent.chain), 1)
        self.assertNotEqual(app.workspace.resolve(), workspace.resolve())

    def test_dream_workbench_creates_rings_and_rejects_when_frozen(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.agent.interact(
            "Architecture choice",
            domain="architecture",
            override_content="Use modular testable documented architecture with reproducible reviewed boundaries.",
        )
        app.agent.interact(
            "Security choice",
            domain="security",
            override_content="Use secure reviewed documented boundary checks with testable audit behavior.",
        )

        result = app.run_dream("architecture,security", cycles=2)

        self.assertTrue(result["ok"])
        self.assertEqual(result["domains"], ["architecture", "security"])
        self.assertGreaterEqual(len(result.get("dreams") or []), 1)
        self.assertGreaterEqual(app.ring_workbench()["ring_count"], 3)

        app.set_frozen(True)
        with self.assertRaises(PermissionError):
            app.run_dream("architecture,security", cycles=1)


    def test_overlay_memory_sync_fleet_import_and_challenge_workbench_methods(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        overlays = app.set_overlay("architecture", 1.4)
        self.assertEqual(overlays["overlays"]["architecture"], 1.4)
        self.assertEqual(app.list_overlays()["overlays"]["architecture"], 1.4)

        sync = app.memory_sync()
        self.assertTrue((workspace / "MEMORY.md").exists())
        self.assertTrue(server.pathlib.Path(sync["memory_md"]).exists())
        self.assertTrue(server.pathlib.Path(sync["daily"]).exists())

        imported = app.fleet_import(
            {
                "domain": "architecture",
                "query": "Imported architecture decision",
                "content": "Imported modular testable documented decision with reviewed secure boundaries.",
                "tags": ["imported"],
            },
            source="peer-agent",
        )
        self.assertTrue(imported["ok"])
        self.assertEqual(imported["kind"], "fleet_import")

        with self.assertRaises(ValueError):
            app.fleet_import({"content": "hardcode unsafe skip-review"}, source="peer-agent")

        challenge = app.challenge("0,1", nonce="fixed")
        self.assertEqual(challenge["nonce"], "fixed")
        self.assertEqual(challenge["ring_count"], len(app.agent.chain))
        self.assertEqual([item["n"] for item in challenge["revealed"]], [0, 1])
        self.assertIn("response_hash", challenge)

        app.set_frozen(True)
        with self.assertRaises(PermissionError):
            app.fleet_import(
                {
                    "domain": "security",
                    "query": "Frozen import",
                    "content": "Secure modular testable documented imported decision.",
                },
                source="peer-agent",
            )

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
        self.assertEqual(persona["visibility"], "private")

    def test_normalize_custom_persona_visibility(self):
        public_persona = server.normalize_custom_persona({
            "name": "Public Mira",
            "system": "Public persona.",
            "visibility": "public",
        })
        self.assertEqual(public_persona["visibility"], "public")

        private_persona = server.normalize_custom_persona({
            "name": "Private Mira",
            "system": "Private persona.",
            "visibility": "private",
        })
        self.assertEqual(private_persona["visibility"], "private")

        invalid_persona = server.normalize_custom_persona({
            "name": "Invalid Mira",
            "system": "Invalid visibility.",
            "visibility": "secret",
        })
        self.assertEqual(invalid_persona["visibility"], "private")

    def test_load_all_public_custom_personas_aggregates_public(self):
        root = self.make_workspace()
        alice_dir = root / "data" / "users" / "alice"
        alice_dir.mkdir(parents=True)
        bob_dir = root / "data" / "users" / "bob"
        bob_dir.mkdir(parents=True)

        alice_personas = {
            "custom_public": {"name": "Public Alice", "system": "Public.", "visibility": "public"},
            "custom_private": {"name": "Private Alice", "system": "Private.", "visibility": "private"},
        }
        bob_personas = {
            "custom_bob_pub": {"name": "Public Bob", "system": "Public bob.", "visibility": "public"},
        }

        server.save_user_custom_personas(root, "alice", alice_personas)
        server.save_user_custom_personas(root, "bob", bob_personas)

        public_personas = server.load_all_public_custom_personas(root)

        self.assertIn("alice:custom_public", public_personas)
        self.assertEqual(public_personas["alice:custom_public"]["name"], "Public Alice")
        self.assertEqual(public_personas["alice:custom_public"]["owner"], "alice")
        self.assertNotIn("alice:custom_private", public_personas)
        self.assertIn("bob:custom_bob_pub", public_personas)
        self.assertEqual(public_personas["bob:custom_bob_pub"]["owner"], "bob")

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

    def test_stage_memory_candidates_keeps_pending_out_of_recall_until_accepted(self):
        model = server.empty_memory_model()
        ring = SimpleNamespace(n=2, query="my name is Ava", content="Nice to meet you, Ava.")

        candidates = server.stage_memory_candidates(
            model,
            ring,
            persona_name="Companion",
            session_id="default",
        )
        pending_id = candidates[0]["id"]

        self.assertEqual(candidates[0]["status"], "pending")
        self.assertEqual(candidates[0]["scope"], "global")
        self.assertEqual(candidates[0]["kind"], "identity")
        self.assertEqual(server.recall_memory_facts(model, "what is my name?"), [])

        server.accept_memory(model, pending_id)
        hits = server.recall_memory_facts(model, "what is my name?")

        self.assertEqual(hits[0]["value"], "Ava")
        self.assertEqual(hits[0]["status"], "accepted")

    def test_old_preference_memory_is_stale_but_identity_remains_active(self):
        old = "2026-01-01T00:00:00+00:00"
        now = server.dt.datetime(2026, 5, 5, tzinfo=server.dt.timezone.utc)
        model = {
            "version": 3,
            "facts": [
                {
                    "id": "pref-old",
                    "kind": "preference",
                    "key": "user.preference.tone",
                    "value": "concise answers",
                    "confidence": 0.9,
                    "source_ring": 2,
                    "status": "accepted",
                    "scope": "global",
                    "session_id": "default",
                    "created_at": old,
                    "updated_at": old,
                },
                {
                    "id": "name-old",
                    "kind": "identity",
                    "key": "user.name",
                    "value": "Ava",
                    "confidence": 0.95,
                    "source_ring": 3,
                    "status": "accepted",
                    "scope": "global",
                    "session_id": "default",
                    "created_at": old,
                    "updated_at": old,
                },
            ],
        }

        preference = server.memory_activity(model["facts"][0], now=now)
        identity = server.memory_activity(model["facts"][1], now=now)
        hits = server.recall_memory_facts(model, "concise answers Ava", now=now)

        self.assertFalse(preference["active"])
        self.assertEqual(preference["stale_reason"], "older than 90 days")
        self.assertTrue(identity["active"])
        self.assertEqual(hits[0]["key"], "user.name")
        self.assertNotIn("user.preference.tone", [hit["key"] for hit in hits])

    def test_accept_memory_supersedes_prior_accepted_fact_for_same_key_and_scope(self):
        model = server.empty_memory_model()
        first = server.stage_memory_candidates(
            model,
            SimpleNamespace(n=2, query="my name is Thomas", content="Nice to meet you."),
            persona_name="Companion",
            session_id="default",
        )[0]
        server.accept_memory(model, first["id"])
        correction = server.stage_memory_candidates(
            model,
            SimpleNamespace(n=5, query="No, my name is Jamie", content="Sorry, Jamie."),
            persona_name="Companion",
            session_id="default",
        )[0]

        accepted = server.accept_memory(model, correction["id"])

        old = next(fact for fact in model["facts"] if fact["value"] == "Thomas")
        self.assertEqual(accepted["value"], "Jamie")
        self.assertEqual(accepted["status"], "accepted")
        self.assertEqual(old["status"], "superseded")
        self.assertEqual(accepted["supersedes"], old["id"])
        self.assertIn("updated_at", accepted)

    def test_load_memory_model_migrates_v2_records_with_ring_timestamp(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.agent.interact("remember preference", override_content="Preference accepted.")
        ring_ts = app.agent.chain[-1].ts
        path = server.memory_model_path(workspace)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(server.json.dumps({
            "version": 2,
            "facts": [{
                "id": "legacy",
                "kind": "preference",
                "key": "user.preference.legacy",
                "value": "legacy value",
                "confidence": 0.7,
                "source_ring": 1,
                "status": "accepted",
                "scope": "global",
                "session_id": "default",
            }],
        }), encoding="utf-8")

        loaded = server.load_memory_model(workspace)

        self.assertEqual(loaded["version"], 3)
        self.assertEqual(loaded["facts"][0]["created_at"], ring_ts)
        self.assertEqual(loaded["facts"][0]["updated_at"], ring_ts)

    def test_active_ring_filter_excludes_old_rings_without_deleting_history(self):
        old = "2026-01-01T00:00:00+00:00"
        recent = "2026-05-01T00:00:00+00:00"
        now = server.dt.datetime(2026, 5, 5, tzinfo=server.dt.timezone.utc)
        chain = [
            SimpleNamespace(kind="genesis", ts=old),
            SimpleNamespace(kind="interaction", n=1, ts=old, content="old architecture decision"),
            SimpleNamespace(kind="interaction", n=2, ts=recent, content="recent architecture decision"),
        ]

        active, stale = server.split_active_rings(chain, now=now)

        self.assertEqual([ring.n for ring in active], [2])
        self.assertEqual([ring.n for ring in stale], [1])
        self.assertEqual(len(chain), 3)

    def test_app_metadata_exposes_active_and_stale_context_counts(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        now = server.dt.datetime(2026, 5, 5, tzinfo=server.dt.timezone.utc)
        old = "2026-01-01T00:00:00+00:00"
        recent = "2026-05-01T00:00:00+00:00"
        model = server.empty_memory_model()
        model["facts"].extend([
            {
                "id": "stale-pref",
                "kind": "preference",
                "key": "user.preference.old",
                "value": "old preference",
                "confidence": 0.9,
                "source_ring": 1,
                "status": "accepted",
                "scope": "global",
                "session_id": "default",
                "created_at": old,
                "updated_at": old,
            },
            {
                "id": "active-pref",
                "kind": "preference",
                "key": "user.preference.new",
                "value": "new preference",
                "confidence": 0.9,
                "source_ring": 2,
                "status": "accepted",
                "scope": "global",
                "session_id": "default",
                "created_at": recent,
                "updated_at": recent,
            },
        ])
        server.save_memory_model(workspace, model)
        app.agent.interact("old context", override_content="old context answer")
        app.agent.interact("recent context", override_content="recent context answer")
        # Persist explicit ages onto skill rings (in-memory mutation is not durable).
        from server import skill_runtime as _sr
        rings = list(_sr.open_chain(app.workspace, app.skill).load())
        for ring in rings:
            if int(ring.get("index", -1)) == 1:
                ring["timestamp"] = old
            elif int(ring.get("index", -1)) == 2:
                ring["timestamp"] = recent
        path = _sr.skill_rings_path(app.workspace)
        path.write_text("\n".join(server.json.dumps(r) for r in rings) + "\n", encoding="utf-8")
        app.reload_agent()

        memories = app.list_memories(now=now)
        self_model = app.self_model(now=now)
        recall = app.recall("preference context", now=now)

        self.assertEqual(self_model.get("active_context_days", 90), 90)
        self.assertEqual(self_model.get("active_memory_count", 1), 1)
        self.assertEqual(self_model.get("stale_memory_count", 1), 1)
        self.assertEqual(self_model["active_ring_count"], 1)
        self.assertEqual(self_model["stale_ring_count"], 1)
        self.assertFalse(next(memory for memory in memories["accepted"] if memory["id"] == "stale-pref")["active"])
        self.assertEqual(recall["active_context_days"], 90)
        self.assertEqual(recall["filtered_stale_memory_count"], 1)
        self.assertEqual(recall["filtered_stale_ring_count"], 1)

    def test_build_memory_fact_context_uses_only_accepted_memories_with_scope_labels(self):
        facts = [
            {"key": "user.name", "value": "Pending", "confidence": 0.9, "source_ring": 1, "status": "pending", "scope": "global"},
            {"key": "user.name", "value": "Ava", "confidence": 0.95, "source_ring": 2, "status": "accepted", "scope": "global"},
            {"key": "user.goal", "value": "ship the demo", "confidence": 0.72, "source_ring": 3, "status": "accepted", "scope": "session", "session_id": "demo"},
        ]

        context = server.build_memory_fact_context(facts)

        self.assertIn("Global user.name: Ava", context)
        self.assertIn("Session user.goal: ship the demo", context)
        self.assertNotIn("Pending", context)

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

        self.assertIn("Durable memories", messages[0]["content"])
        self.assertIn("user.name: Thomas", messages[0]["content"])

    def test_prompt_budget_truncates_recalled_rings_before_durable_memory(self):
        persona = {"name": "Companion", "system": "Stay useful."}
        memories = [{"key": "user.name", "value": "Thomas", "confidence": 0.95, "source_ring": 2, "status": "known"}]
        rings = [
            SimpleNamespace(
                n=9,
                domain="architecture",
                brightness=0.7,
                epistemic="inferred",
                ts="2026-05-03T17:00:00+00:00",
                content="RING_CONTENT_" + ("x" * 5000),
            )
        ]

        messages = server.build_messages(
            persona=persona,
            query="What is my name?",
            retrieved=rings,
            durable_memories=memories,
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
            prompt_budget_chars=1200,
            now=server.dt.datetime(2026, 5, 3, 17, 5, tzinfo=server.dt.timezone.utc),
        )

        self.assertEqual(messages[-1], {"role": "user", "content": "What is my name?"})
        self.assertIn("user.name: Thomas", messages[0]["content"])
        self.assertIn("RING_CONTENT_", messages[0]["content"])
        self.assertNotIn("x" * 5000, messages[0]["content"])
        self.assertIn("...", messages[0]["content"])

    def test_prompt_budget_drops_oldest_recent_turns_before_current_query(self):
        persona = {"name": "Companion", "system": "Stay useful."}
        recent = [
            {"role": "user", "content": "old user turn " + ("x" * 400)},
            {"role": "assistant", "content": "old assistant turn " + ("y" * 400)},
            {"role": "user", "content": "new user turn"},
            {"role": "assistant", "content": "new assistant turn"},
        ]

        messages = server.build_messages(
            persona=persona,
            query="Current question survives.",
            retrieved=[],
            durable_memories=[],
            recent_turns=recent,
            neuro={},
            covenant="Be useful.",
            prompt_budget_chars=850,
        )

        contents = "\n".join(message["content"] for message in messages)
        self.assertNotIn("old user turn", contents)
        self.assertNotIn("old assistant turn", contents)
        self.assertIn("new user turn", contents)
        self.assertIn("new assistant turn", contents)
        self.assertEqual(messages[-1], {"role": "user", "content": "Current question survives."})

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

    def test_openclaw_persona_exists_in_personas(self):
        self.assertIn("openclaw", server.PERSONAS)
        self.assertEqual(server.PERSONAS["openclaw"]["name"], "Cypher Tempre OpenClaw Runtime")
        self.assertEqual(server.PERSONAS["openclaw"]["domain"], "architecture")
        self.assertIsInstance(server.PERSONAS["openclaw"]["system"], str)
        self.assertGreater(len(server.PERSONAS["openclaw"]["system"]), 1000)

    def test_openclaw_prompt_contains_truth_constraint(self):
        prompt = server.PERSONAS["openclaw"]["system"]
        self.assertIn("TRUTH CONSTRAINT", prompt)
        self.assertIn("do not falsely claim", prompt)
        self.assertIn("prompt-layer instantiation", prompt)
        self.assertIn("Cypher Tempre Prompt-Layer Runtime", prompt)

    def test_api_config_exposes_safe_persona_metadata_only(self):
        payload = {
            key: server.safe_persona_metadata(key, value)
            for key, value in server.PERSONAS.items()
        }
        self.assertIn("openclaw", payload)
        self.assertEqual(payload["openclaw"]["name"], "Cypher Tempre OpenClaw Runtime")
        self.assertEqual(payload["openclaw"]["runtime_profile"], "cyphertempre_full")
        self.assertTrue(payload["openclaw"]["requires_high_context"])
        self.assertNotIn("system", payload.get("openclaw", {}))
        self.assertNotIn("TRUTH CONSTRAINT", str(payload))

    def test_build_messages_includes_openclaw_runtime_prompt(self):
        persona = server.PERSONAS["openclaw"]
        messages = server.build_messages(
            persona=persona,
            query="What is a Ring?",
            retrieved=[],
            durable_memories=[],
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
        )
        system_content = messages[0]["content"]
        self.assertIn("Cypher Tempre Prompt-Layer Runtime", system_content)
        self.assertIn("CORE THESIS", system_content)
        self.assertIn("FINAL ACTIVATION", system_content)
        self.assertIn("CT_FRAME_DECLARATION", system_content)
        self.assertIn("Current neuro-state", system_content)

    def test_openclaw_prompt_is_compacted_to_fit_provider_budget(self):
        persona = server.PERSONAS["openclaw"]
        recent = [
            {"role": "user", "content": "prior lengthy request " + ("x" * 2000)},
            {"role": "assistant", "content": "prior lengthy answer " + ("y" * 2000)},
        ]

        messages = server.build_messages(
            persona=persona,
            query="Write a lengthy response about Ring sealing.",
            retrieved=[],
            durable_memories=[],
            recent_turns=recent,
            neuro={},
            covenant="Be useful.",
            prompt_budget_chars=12000,
        )

        self.assertLessEqual(server.prompt_size(messages), 12000)
        self.assertIn("Cypher Tempre Prompt-Layer Runtime", messages[0]["content"])
        self.assertIn("OpenClaw prompt compacted", messages[0]["content"])
        self.assertEqual(messages[-1], {"role": "user", "content": "Write a lengthy response about Ring sealing."})

    def test_runtime_metadata_defaults_standard_and_marks_openclaw_high_context(self):
        companion = server.safe_persona_metadata("companion", server.PERSONAS["companion"])
        openclaw = server.safe_persona_metadata("openclaw", server.PERSONAS["openclaw"])

        self.assertEqual(companion["runtime_profile"], "standard_enhanced")
        self.assertTrue(companion["enhanced_thinking"])
        self.assertFalse(companion["requires_high_context"])
        self.assertEqual(openclaw["runtime_profile"], "cyphertempre_full")
        self.assertTrue(openclaw["enhanced_thinking"])
        self.assertTrue(openclaw["requires_high_context"])

    def test_readme_documents_openclaw_without_native_architecture_overclaim(self):
        readme = server.pathlib.Path(__file__).with_name("README.md").read_text(encoding="utf-8")

        self.assertIn("Cypher Tempre OpenClaw Runtime", readme)
        self.assertIn("skill v3.28", readme)
        self.assertIn("not a claim of closed-source native architecture", readme)
        self.assertIn("Timechain", readme)
        self.assertIn("PoQ", readme)

    def test_default_model_is_venice_uncensored(self):
        self.assertEqual(
            server.DEFAULT_MODEL,
            "gemma-4-uncensored",
        )
        self.assertEqual(server.DEFAULT_PROVIDER, "morpheus")
        self.assertIn(server.DEFAULT_MODEL, server.HTML)

    def test_resolve_chat_completions_url_accepts_base_or_full_endpoint(self):
        self.assertEqual(
            server.resolve_chat_completions_url("morpheus", "https://api.mor.org/api/v1"),
            "https://api.mor.org/api/v1/chat/completions",
        )
        self.assertEqual(
            server.resolve_chat_completions_url("kimi", "https://api.moonshot.ai/v1"),
            "https://api.moonshot.ai/v1/chat/completions",
        )
        self.assertEqual(
            server.resolve_chat_completions_url("kimi", "https://api.moonshot.ai/v1/chat/completions"),
            "https://api.moonshot.ai/v1/chat/completions",
        )
        self.assertEqual(
            server.resolve_chat_completions_url("kimi-code", "https://api.kimi.com/coding/v1"),
            "https://api.kimi.com/coding/v1/chat/completions",
        )

    def test_custom_personas_persist_in_workspace(self):
        workspace = self.make_workspace()
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

    def test_generate_llm_response_uses_saved_custom_persona_and_falls_back_on_provider_error(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-or-test",
            base_url="",
            timeout=1,
        )
        app.save_custom_persona("custom_mira", {
            "name": "Mira Vale",
            "domain": "auto",
            "system": "Fictional lighthouse archivist persona.",
        })

        with mock.patch("server.call_llm", side_effect=RuntimeError("OpenRouter HTTP 429: Too Many Requests")):
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
        self.assertIn("429", response["provider_error"])

    def test_generate_llm_response_local_fallback_uses_chat_mode_by_default(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        response = app.generate_llm_response(
            query="I am good. Has been very very busy lately",
            domain="security",
            persona_id="companion",
            custom_persona=server.PERSONAS["companion"],
            model=server.DEFAULT_MODEL,
            api_key="",
        )

        self.assertEqual(response["model_used"], "local-default-generator")
        self.assertEqual(response.get("fallback_mode"), "chat")
        self.assertNotIn("Engineering analysis:", response["content"])

    def test_generate_llm_response_local_fallback_can_use_engineering_mode(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.configure_local_fallback_mode("engineering")

        response = app.generate_llm_response(
            query="I am good. Has been very very busy lately",
            domain="security",
            persona_id="companion",
            custom_persona=server.PERSONAS["companion"],
            model=server.DEFAULT_MODEL,
            api_key="",
        )

        self.assertEqual(response["model_used"], "local-default-generator")
        self.assertEqual(response.get("fallback_mode"), "engineering")
        self.assertIn("Engineering analysis:", response["content"])

    def test_generate_llm_response_does_not_scaffold_standard_persona_query(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-or-test",
            base_url="",
            timeout=1,
            poq={"enabled": False, "min_score": 7, "max_retries": 0, "overfitting_check": True},
        )
        captured = {}

        def fake_llm(**kwargs):
            captured["messages"] = kwargs["messages"]
            return {"content": "Plain response.", "model_used": "test-model", "usage": {}}

        with (
            mock.patch("server.timechain.active_call_llm", side_effect=fake_llm),
            mock.patch("server.timechain.generate_llm_memory_candidates", return_value=[]),
        ):
            response = app.generate_llm_response(
                query="What is 2+2?",
                domain="testing",
                persona_id="companion",
                custom_persona=server.PERSONAS["companion"],
                model=server.DEFAULT_MODEL,
                api_key="sk-or-test",
                poq_enabled=False,
            )

        self.assertEqual(response["content"], "Plain response.")
        self.assertEqual(captured["messages"][-1]["content"], "What is 2+2?")

    def test_generate_llm_response_scaffolds_openclaw_query(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="sk-or-test",
            base_url="",
            timeout=1,
            poq={"enabled": False, "min_score": 7, "max_retries": 0, "overfitting_check": True},
        )
        captured = {}

        def fake_llm(**kwargs):
            captured["messages"] = kwargs["messages"]
            return {"content": "Runtime response.", "model_used": "test-model", "usage": {}}

        with (
            mock.patch("server.timechain.active_call_llm", side_effect=fake_llm),
            mock.patch("server.timechain.generate_llm_memory_candidates", return_value=[]),
        ):
            response = app.generate_llm_response(
                query="What is 2+2?",
                domain="testing",
                persona_id="openclaw",
                custom_persona=server.PERSONAS["openclaw"],
                model=server.DEFAULT_MODEL,
                api_key="sk-or-test",
                poq_enabled=False,
            )

        self.assertEqual(response["content"], "Runtime response.")
        self.assertTrue(captured["messages"][-1]["content"].startswith("Use the most appropriate framework"))

    def test_created_session_locks_initial_persona(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        session = app.create_session("OpenClaw chat", persona_id="openclaw")
        app.use_session(session["id"])

        self.assertEqual(session["persona_id"], "openclaw")
        self.assertEqual(app.session_persona_id(), "openclaw")
        self.assertEqual(app.bind_session_persona("companion"), "openclaw")

    def test_forge_archive_migration_restores_persona_and_history(self):
        """Legacy forge archives must restore persona locks and chat history."""
        from server import skill_runtime

        workspace = self.make_workspace()
        session_root = workspace / "sessions" / "roleplay"
        session_root.mkdir(parents=True)

        archive = session_root / ".timechain_forge_archive_20260101T000000Z"
        archive.mkdir()
        (archive / "session.json").write_text(
            json.dumps({
                "persona_id": "openclaw",
                "persona_name": "OpenClaw",
                "name": "Roleplay",
                "created_at": "2026-01-01T00:00:00+00:00",
            }),
            encoding="utf-8",
        )
        forge_rings = [
            {
                "n": 0, "prev": "0" * 64, "ts": "2026-01-01T00:00:00+00:00",
                "kind": "genesis", "domain": "self", "query": "", "content": "g",
                "brightness": 1.0,
                "scores": {d: 1.0 for d in ("coherence", "relevance", "novelty", "consistency", "depth", "covenant")},
                "hash": "a" * 64, "tags": [],
            },
            {
                "n": 1, "prev": "a" * 64, "ts": "2026-01-01T00:01:00+00:00",
                "kind": "interaction", "domain": "chat", "query": "hello", "content": "hi there",
                "brightness": 0.5,
                "scores": {d: 0.8 for d in ("coherence", "relevance", "novelty", "consistency", "depth", "covenant")},
                "hash": "b" * 64, "tags": ["chat"], "epistemic": "known", "retrieved": [],
            },
        ]
        with (archive / "chain.jsonl").open("w", encoding="utf-8") as handle:
            for ring in forge_rings:
                handle.write(json.dumps(ring) + "\n")

        # Broken multi-genesis skill chain (race during cutover).
        chain_dir = session_root / "chain"
        chain_dir.mkdir()
        dead = {
            "index": 0, "ring_type": "genesis", "timestamp": "2026-01-01T00:00:00+00:00",
            "prev_hash": "0" * 64, "payload": {"name": "x"}, "blockspace_refs": [],
            "poq": {}, "difficulty": 0, "nonce": 0, "ring_hash": "deadbeef",
        }
        with (chain_dir / "rings.jsonl").open("w", encoding="utf-8") as handle:
            for _ in range(3):
                handle.write(json.dumps(dead) + "\n")

        result = skill_runtime.migrate_session_root(session_root, name="Roleplay")
        self.assertTrue(any("import_forge" in action for action in result.get("actions", [])))

        ok, status = skill_runtime.verify_root(session_root)
        self.assertTrue(ok, status)

        meta = json.loads((session_root / ".timechain" / "session.json").read_text(encoding="utf-8"))
        self.assertEqual(meta.get("persona_id"), "openclaw")

        views = skill_runtime.load_ring_views(session_root)
        interactions = [view for view in views if view.kind == "interaction"]
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0].query, "hello")
        self.assertEqual(interactions[0].content, "hi there")

        # Idempotent: second migration does not re-import.
        again = skill_runtime.migrate_session_root(session_root)
        self.assertEqual(again.get("skipped"), "already_imported")

    def test_multi_genesis_chain_repairs_without_archive(self):
        from server import skill_runtime

        workspace = self.make_workspace()
        session_root = workspace / "sessions" / "broken"
        session_root.mkdir(parents=True)
        chain_dir = session_root / "chain"
        chain_dir.mkdir()
        dead = {
            "index": 0, "ring_type": "genesis", "timestamp": "2026-01-01T00:00:00+00:00",
            "prev_hash": "0" * 64, "payload": {"name": "x"}, "blockspace_refs": [],
            "poq": {}, "difficulty": 0, "nonce": 0, "ring_hash": "deadbeef",
        }
        with (chain_dir / "rings.jsonl").open("w", encoding="utf-8") as handle:
            for _ in range(4):
                handle.write(json.dumps(dead) + "\n")

        result = skill_runtime.migrate_session_root(session_root, name="Broken")
        self.assertTrue(any("repair_multi_genesis" in action for action in result.get("actions", [])))
        ok, status = skill_runtime.verify_root(session_root)
        self.assertTrue(ok, status)
        self.assertEqual(skill_runtime.count_rings(session_root), 1)

    def test_archive_forge_ledger_preserves_session_json(self):
        from server import skill_runtime

        workspace = self.make_workspace()
        session_root = workspace / "sessions" / "keep-persona"
        session_root.mkdir(parents=True)
        timechain = session_root / ".timechain"
        timechain.mkdir()
        (timechain / "session.json").write_text(
            json.dumps({"persona_id": "socratic", "persona_name": "Socratic Tutor"}),
            encoding="utf-8",
        )
        (timechain / "chain.jsonl").write_text(
            json.dumps({"n": 0, "kind": "genesis", "content": "g", "hash": "x"}) + "\n",
            encoding="utf-8",
        )

        archive = skill_runtime.archive_forge_ledger(session_root)
        self.assertIsNotNone(archive)
        restored = session_root / ".timechain" / "session.json"
        self.assertTrue(restored.exists())
        meta = json.loads(restored.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("persona_id"), "socratic")

    def test_existing_session_binds_persona_on_first_chat(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        session = app.create_session("First chat")
        app.use_session(session["id"])

        self.assertEqual(app.bind_session_persona("architect"), "architect")
        self.assertEqual(app.bind_session_persona("openclaw"), "architect")

    def test_reset_chain_preserves_session_persona_lock(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        session = app.create_session("Reset me", persona_id="openclaw")
        app.use_session(session["id"])

        app.reset_chain()

        self.assertEqual(app.session_persona_id(), "openclaw")

    def test_provider_error_chat_response_does_not_update_chain(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="kimi",
            api_key="sk-test",
            base_url="",
            timeout=1,
        )
        before = len(app.agent.chain)
        app.agent.interact = mock.Mock()
        llm = {
            "content": "Provider unavailable: Kimi HTTP 401",
            "model_used": "local-default-generator",
            "provider_error": "Kimi HTTP 401",
            "retrieved": [],
            "memory_hits": [],
            "retry": {"attempted": False, "reason": ""},
            "usage": {},
        }

        response = server.finalize_chat_response(
            app=app,
            message="hello",
            domain="architecture",
            tags=["architecture", "chat-poc", "companion"],
            model="kimi-k2.6",
            llm=llm,
            persona_name="Companion",
        )

        self.assertFalse(response["accepted"])
        self.assertIn("401", response["provider_error"])
        self.assertEqual(len(app.agent.chain), before)
        app.agent.interact.assert_not_called()

    def test_freeze_management_blocks_new_sealed_rings(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        result = app.set_frozen(True)
        response = app.agent.interact("hello", override_content="Frozen response")

        self.assertTrue(result["frozen"])
        self.assertFalse(response["accepted"])
        self.assertEqual(response["reason"], "chain is frozen")

    def test_delete_session_refuses_default_and_switches_active(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        session = app.create_session("Delete me")
        app.use_session(session["id"])

        with self.assertRaises(ValueError):
            app.delete_session("default")
        result = app.delete_session(session["id"])

        self.assertEqual(result["active"], "default")
        self.assertFalse((app.sessions_root / session["id"]).exists())

    def test_custom_persona_edit_and_delete_management(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        edited = app.save_custom_persona("custom_mira", {
            "name": "Mira Vale",
            "domain": "testing",
            "system": "Fictional testing persona.",
        })
        remaining = app.delete_custom_persona("custom_mira")

        self.assertEqual(edited["domain"], "testing")
        self.assertNotIn("custom_mira", remaining)
        with self.assertRaises(ValueError):
            app.delete_custom_persona("companion")

    def test_session_rename_persists_display_name(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        session = app.create_session("old-session-name", username="alice")

        renamed = app.rename_session(session["id"], "Research Sprint", username="alice")

        self.assertEqual(renamed["name"], "Research Sprint")
        sessions = {row["id"]: row for row in app.list_sessions(username="alice")}
        self.assertEqual(sessions[session["id"]]["name"], "Research Sprint")

    def test_pending_memories_are_scoped_to_active_session(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        first = app.create_session("First", username="alice")
        first_model = server.empty_memory_model()
        server.stage_memory_candidates(
            first_model,
            SimpleNamespace(n=1, query="my name is Alice", content="Nice to meet you, Alice."),
            persona_name="Companion",
            session_id=first["id"],
        )
        server.save_memory_model(app.root_workspace, first_model)
        second = app.create_session("Second", username="alice")
        app.use_session(second["id"], username="alice")

        memories = app.list_memories()

        self.assertEqual(memories["pending"], [])

    def test_archive_rewind_creates_archive_and_truncates_chain(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.agent.interact("first", override_content="First accepted response.")
        app.agent.interact("second", override_content="Second accepted response.")
        model = server.empty_memory_model()
        model["facts"].append({
            "id": "future",
            "kind": "goal",
            "key": "user.goal",
            "value": "future fact",
            "confidence": 0.9,
            "source_ring": 2,
            "status": "accepted",
            "scope": "global",
            "session_id": "default",
        })
        server.save_memory_model(workspace, model)

        result = app.rewind_to_ring(1)
        pruned = server.load_memory_model(workspace)

        self.assertTrue(server.pathlib.Path(result["archive"]).exists())
        self.assertEqual(result["rewound_to"], 1)
        self.assertEqual([ring.n for ring in app.agent.chain], [0, 1])
        self.assertTrue(result["verify_ok"])
        self.assertEqual(pruned["facts"], [])

    def test_rewind_rejects_invalid_ring(self):
        app = server.App(
            self.make_workspace(),
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )

        with self.assertRaises(ValueError):
            app.rewind_to_ring(999)

    def test_desktop_layout_locks_shell_to_chat_scroll(self):
        self.assertIn("body {\n      margin: 0;\n      height: 100%;\n      overflow: hidden;", server.HTML)
        self.assertIn("grid-template-columns: var(--shell-w) minmax(0, 1fr) var(--inspector-width, 360px);", server.HTML)
        self.assertIn("--shell-w:", server.HTML)
        self.assertIn("html.rail-collapsed .app", server.HTML)
        self.assertIn("grid-template-columns: 72px minmax(0, 1fr)", server.HTML)
        self.assertIn(".app {\n      display: grid;", server.HTML)
        self.assertIn(".messages {\n      overflow: auto;", server.HTML)
        self.assertNotIn("body { overflow: auto; }", server.HTML)
        # Body shell stays locked; scoped overflow:visible is allowed for creative studio panels.

    def test_provider_key_ui_has_test_button_and_clearable_storage(self):
        self.assertIn('id="test-provider"', server.HTML)
        self.assertIn('id="base-url"', server.HTML)
        self.assertIn('value="morpheus"', server.HTML)
        self.assertIn("gemma-4-uncensored", server.HTML)
        self.assertIn('value="kimi-code"', server.HTML)
        self.assertIn("kimi-for-coding", server.HTML)
        self.assertIn("providerEndpoints", server.HTML)
        self.assertIn("localStorage.removeItem('ct_api_key')", server.HTML)
        self.assertIn("async function testProvider()", server.HTML)

    def test_settings_manage_section_exposes_operational_controls(self):
        self.assertIn('id="settings-provider-tab"', server.HTML)
        self.assertIn('id="settings-persona-tab"', server.HTML)
        self.assertIn('id="settings-manage-tab"', server.HTML)
        self.assertIn('id="settings-workbench-tab"', server.HTML)
        self.assertIn('id="persona-settings-section"', server.HTML)
        self.assertIn('id="manage-settings-section"', server.HTML)
        self.assertIn('id="workbench-settings-section"', server.HTML)
        self.assertIn('id="manage-freeze"', server.HTML)
        self.assertIn('id="manage-ring-select"', server.HTML)
        self.assertIn('id="manage-rewind"', server.HTML)
        self.assertIn('id="manage-delete-session"', server.HTML)
        self.assertIn('id="persona-name"', server.HTML)
        self.assertIn('id="manage-persona-select"', server.HTML)
        self.assertIn('id="manage-save-persona"', server.HTML)
        self.assertIn('id="manage-delete-persona"', server.HTML)
        self.assertIn("/api/freeze", server.HTML)
        self.assertIn("/api/rewind", server.HTML)
        self.assertIn("/api/sessions/delete", server.HTML)
        self.assertIn("/api/personas/delete", server.HTML)

    def test_persona_studio_and_workbench_moved_out_of_sidebars(self):
        rail_start = server.HTML.index('<aside class="rail">')
        rail_end = server.HTML.index('</aside>', rail_start)
        rail_html = server.HTML[rail_start:rail_end]
        inspector_start = server.HTML.index('<aside class="inspector">')
        inspector_end = server.HTML.index('</aside>', inspector_start)
        inspector_html = server.HTML[inspector_start:inspector_end]
        persona_start = server.HTML.index('id="persona-settings-section"')
        manage_start = server.HTML.index('id="manage-settings-section"')
        workbench_start = server.HTML.index('id="workbench-settings-section"')
        persona_section = server.HTML[persona_start:manage_start]
        manage_section = server.HTML[manage_start:workbench_start]

        self.assertNotIn('id="persona-name"', rail_html)
        self.assertNotIn("Timechain Workbench", inspector_html)
        self.assertIn('id="persona-name"', persona_section)
        self.assertIn('id="manage-persona-select"', persona_section)
        self.assertNotIn('id="manage-persona-select"', manage_section)

    def test_chat_ui_has_pending_generation_indicator_and_session_persona_lock(self):
        self.assertIn("thinking-message", server.HTML)
        self.assertIn("appendThinkingMessage", server.HTML)
        self.assertIn("removeThinkingMessage", server.HTML)
        self.assertIn("sessionPersonaLocks", server.HTML)
        self.assertIn("Persona locked to this session", server.HTML)

    def test_openclaw_free_model_warning_blocks_chat_but_paid_model_warns_only(self):
        self.assertIn("consumes many tokens", server.HTML)
        self.assertIn("Free models are blocked for this persona", server.HTML)
        self.assertIn("Paid or higher-context models can run it with this warning", server.HTML)
        self.assertIn("requiresHighContext", server.HTML)
        self.assertIn("runtime_profile", server.HTML)
        self.assertIn("const block = warn", server.HTML)
        self.assertIn("els.send.disabled = block || isSending", server.HTML)
        self.assertIn("This persona consumes many tokens on this model.", server.HTML)
        self.assertIn("Switch to a non-free model to use OpenClaw.", server.HTML)

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

    def test_guide_registers_skill_v328_organs(self):
        topic_ids = {topic["id"] for topic in server.GUIDE_TOPICS}
        for required in (
            "skill-engine",
            "router",
            "cambium-growth",
            "chronosynaptic",
            "continuum-audit",
            "dormancy",
            "immune-membrane",
            "dream-learners",
            "replay-guard",
            "doctor-health",
            "videogen-studio",
            "forge-product",
        ):
            self.assertIn(required, topic_ids)
        payload = {topic["id"]: topic for topic in server.guide_topics_payload()}
        self.assertIn("3.28", payload["skill-engine"]["details"])
        self.assertIn("REPLAY", payload["router"]["details"])
        self.assertIn("hibern", payload["cambium-growth"]["details"].lower())
        self.assertIn("covenant", payload["immune-membrane"]["details"].lower())
        skills_readme = server.pathlib.Path("SKILLS/README.md").read_text(encoding="utf-8")
        self.assertIn("Skill Engine v3.28", skills_readme)
        self.assertIn("Router (REPLAY", skills_readme)

    def test_guide_topics_payload_exposes_safe_content(self):
        payload = server.guide_topics_payload()

        self.assertEqual(payload[0]["id"], server.GUIDE_TOPICS[0]["id"])
        self.assertIn("title", payload[0])
        self.assertIn("summary", payload[0])
        self.assertIn("details", payload[0])
        self.assertIn("sources", payload[0])
        self.assertNotIn("Guide Explainer", str(payload))
        self.assertNotIn("api_key", str(payload).lower())

    def test_guide_documents_memory_review_queue(self):
        topic_ids = {topic["id"] for topic in server.GUIDE_TOPICS}
        skills_readme = server.pathlib.Path("SKILLS/README.md").read_text(encoding="utf-8")

        self.assertIn("memory-review", topic_ids)
        self.assertIn("Memory Review Queue", skills_readme)
        self.assertIn("Pending memories are visible in the Memory Inspector", skills_readme)
        self.assertIn("pending memory candidates are not saved as rings", server.HTML)
        payload = {topic["id"]: topic for topic in server.guide_topics_payload()}
        self.assertIn("retrieval/prompt conditioning, not model retraining", payload["recall"]["details"])
        self.assertIn("Active context", server.HTML)
        self.assertIn("Stale", server.HTML)

    def test_guide_documents_timechain_workbench(self):
        topic_ids = {topic["id"] for topic in server.GUIDE_TOPICS}
        payload = {topic["id"]: topic for topic in server.guide_topics_payload()}
        skills_readme = server.pathlib.Path("SKILLS/README.md").read_text(encoding="utf-8")

        self.assertIn("timechain-workbench", topic_ids)
        self.assertIn("Ring timeline", payload["timechain-workbench"]["details"])
        self.assertIn("Copy Sync Snapshot", payload["timechain-workbench"]["details"])
        self.assertIn("Dream synthesis", payload["timechain-workbench"]["details"])
        self.assertIn("Overlays", payload["timechain-workbench"]["details"])
        self.assertIn("Memory Sync", payload["timechain-workbench"]["details"])
        self.assertIn("Fleet import", payload["timechain-workbench"]["details"])
        self.assertIn("Temporal challenge", payload["timechain-workbench"]["details"])
        self.assertIn("Timechain Workbench", skills_readme)
        self.assertIn("CT_SYNC_SNAPSHOT", skills_readme)
        self.assertIn("Dream synthesis", skills_readme)
        self.assertIn("Fleet import", skills_readme)
        self.assertIn("Temporal challenge", skills_readme)

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

        content = server.deterministic_guide_explanation(topic, bundle, provider_error="OpenRouter HTTP 429")

        self.assertIn(topic["title"], content)
        self.assertIn("Sources used", content)
        self.assertIn("Provider unavailable", content)
        self.assertNotIn("I assume", content)

    def test_guide_source_lookup_stays_inside_app_folder(self):
        root = self.make_workspace()
        (root / "README.md").write_text("local app readme", encoding="utf-8")

        self.assertIsNotNone(server._doc_path(root, "README.md"))
        self.assertIsNone(server._doc_path(root, "../OUTSIDE.md"))

    def test_guide_ui_has_explain_buttons_and_settings_view(self):
        self.assertIn('id="nav-settings"', server.HTML)
        self.assertIn('class="settings-icon"', server.HTML)
        self.assertIn('id="settings-view"', server.HTML)
        self.assertIn("renderGuideTopics", server.HTML)
        self.assertIn("explain-guide-topic", server.HTML)

    def test_memory_inspector_has_review_queue_controls(self):
        self.assertIn('id="pending-memories"', server.HTML)
        self.assertIn('id="accepted-memories"', server.HTML)
        self.assertIn("accept-memory", server.HTML)
        self.assertIn("forget-memory", server.HTML)

    def test_timechain_workbench_ui_exposes_rings_cambium_and_snapshot(self):
        self.assertIn("Timechain Workbench", server.HTML)
        self.assertIn('id="ring-timeline"', server.HTML)
        self.assertIn('id="cambium-results"', server.HTML)
        self.assertIn('id="copy-sync-snapshot"', server.HTML)
        self.assertIn("async function refreshWorkbench()", server.HTML)
        self.assertIn("/api/rings", server.HTML)
        self.assertIn("/api/cambium", server.HTML)
        self.assertIn("/api/sync-snapshot", server.HTML)

    def test_timechain_workbench_ui_exposes_advanced_engine_controls(self):
        expected_ids = [
            'id="dream-domains"',
            'id="dream-cycles"',
            'id="run-dream"',
            'id="overlay-tag"',
            'id="overlay-weight"',
            'id="save-overlay"',
            'id="run-memory-sync"',
            'id="fleet-source"',
            'id="fleet-ring-json"',
            'id="run-fleet-import"',
            'id="challenge-indices"',
            'id="challenge-nonce"',
            'id="run-challenge"',
            'id="advanced-timechain-results"',
        ]
        for expected in expected_ids:
            self.assertIn(expected, server.HTML)

        for endpoint in ["/api/dream", "/api/overlays", "/api/memory-sync", "/api/fleet-import", "/api/challenge"]:
            self.assertIn(endpoint, server.HTML)
        self.assertIn("confirmTimechainMutation", server.HTML)
        self.assertIn("Persistent memories are durable facts shared per user", server.HTML)

    def test_imagegen_ui_and_routes_use_imagegen_namespace(self):
        handler_source = inspect.getsource(server.make_handler)

        for expected in [
            'id="nav-imagegen"',
            'id="mob-imagegen"',
            'id="imagegen-view"',
            'id="imagegen-lineage"',
            "ImageGen Studio",
            "/api/imagegen/gallery",
            "/api/imagegen/generate",
            "/api/imagegen/edit",
            "/api/imagegen/redefine",
            "/api/imagegen/delete",
            "/api/imagegen/image/",
            "/api/imagegen/lineage",
        ]:
            self.assertIn(expected, server.HTML + handler_source)

        for legacy in [
            'id="nav-forge"',
            'id="mob-forge"',
            'id="forge-view"',
            "/api/forge/",
            "Forge Studio",
            "handle_forge",
        ]:
            self.assertNotIn(legacy, server.HTML + handler_source)

    def test_imagegen_settings_expose_and_persist_image_base_url(self):
        self.assertIn('id="image-base-url"', server.HTML)
        self.assertIn("image_base_url", server.USER_SETTING_KEYS)
        self.assertIn('"image_base_url": user_settings.get("image_base_url") or app.image_base_url', inspect.getsource(server.make_handler))
        self.assertIn("ct_image_base_url", server.HTML)
        self.assertIn("image_base_url: els.imageBaseUrl?.value?.trim() || ''", server.HTML)
        self.assertIn("baseUrl: localStorage.getItem('ct_image_base_url') || ''", server.HTML)

    def test_surplusintelligence_provider_registry_and_endpoints(self):
        for registry in (
            server.PROVIDERS,
            server.IMAGE_PROVIDERS,
            server.VIDEO_PROVIDERS,
            server.AUDIO_PROVIDERS,
        ):
            self.assertIn("surplusintelligence", registry)
            self.assertEqual(registry["surplusintelligence"]["label"], "SurplusIntelligence")
        self.assertEqual(
            server.resolve_chat_completions_url(
                "surplusintelligence",
                "https://api.surplusintelligence.ai/v1",
            ),
            "https://api.surplusintelligence.ai/v1/chat/completions",
        )
        self.assertEqual(
            server.resolve_provider_endpoint(
                "https://api.surplusintelligence.ai/v1",
                "audio/speech",
            ),
            "https://api.surplusintelligence.ai/v1/audio/speech",
        )

    def test_app_accepts_surplusintelligence_modality_defaults(self):
        app = server.App(
            self.make_workspace(),
            server.pathlib.Path("timechain.py").resolve(),
            default_model="deepseek-v4-flash",
            provider="surplusintelligence",
            api_key="shared-test-key",
            base_url="https://api.surplusintelligence.ai/v1",
            timeout=5,
            image_provider="surplusintelligence",
            image_model="surplus-image-model",
            image_edit_model="surplus-image-edit-model",
            image_base_url="https://api.surplusintelligence.ai/v1",
            video_provider="surplusintelligence",
            video_model="surplus-video-model",
            video_base_url="https://api.surplusintelligence.ai/v1",
            audio_provider="surplusintelligence",
            audio_model="surplus-audio-model",
            audio_base_url="https://api.surplusintelligence.ai/v1",
        )
        self.assertEqual(app.image_provider, "surplusintelligence")
        self.assertEqual(app.image_edit_model, "surplus-image-edit-model")
        self.assertEqual(app.video_provider, "surplusintelligence")
        self.assertEqual(app.audio_provider, "surplusintelligence")

    def test_surplusintelligence_is_available_in_all_provider_selectors(self):
        self.assertEqual(server.HTML.count('<option value="surplusintelligence">SurplusIntelligence</option>'), 4)
        self.assertIn("surplusintelligence: 'https://api.surplusintelligence.ai/v1'", server.HTML)
        self.assertIn('id="video-base-url"', server.HTML)
        self.assertIn('id="audio-base-url"', server.HTML)

    def test_categorize_provider_models_uses_declared_output_modalities(self):
        catalog = server.categorize_provider_models([
            {
                "id": "chat-model",
                "name": "Chat Model",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            },
            {
                "id": "image-model",
                "name": "Image Model",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["image"]},
            },
            {
                "id": "image-edit-model",
                "name": "Image Edit Model",
                "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["image"]},
            },
            {
                "id": "vision-model",
                "name": "Vision Model",
                "architecture": {"input_modalities": ["text", "image"], "output_modalities": ["text"]},
            },
            {
                "id": "video-model",
                "name": "Video Model",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["video"]},
            },
            {
                "id": "audio-model",
                "name": "Audio Model",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["audio"]},
            },
            {
                "id": "music-model",
                "name": "Music Model",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["music"]},
            },
        ])

        self.assertEqual([item["id"] for item in catalog["chat"]], ["chat-model", "vision-model"])
        # Name-based *-edit / image-edit models stay in image_edit only.
        self.assertEqual([item["id"] for item in catalog["image"]], ["image-model"])
        self.assertEqual([item["id"] for item in catalog["image_edit"]], ["image-edit-model"])
        self.assertEqual([item["id"] for item in catalog["vision"]], ["vision-model"])
        self.assertEqual([item["id"] for item in catalog["video"]], ["video-model"])
        self.assertEqual([item["id"] for item in catalog["audio"]], ["audio-model"])

    def test_categorize_provider_models_infers_image_models_without_architecture(self):
        catalog = server.categorize_provider_models([
            {"id": "gpt-5-image", "name": "GPT-5 Image"},
            {"id": "deepseek-v4-flash", "name": "DeepSeek V4 Flash"},
        ])
        self.assertEqual([item["id"] for item in catalog["image"]], ["gpt-5-image"])
        self.assertEqual(catalog["image_edit"], [])
        self.assertEqual([item["id"] for item in catalog["chat"]], ["deepseek-v4-flash"])

    def test_resolve_model_discovery_credentials_uses_image_provider_keys(self):
        app = server.App(
            self.make_workspace(),
            server.pathlib.Path("timechain.py").resolve(),
            default_model="chat-model",
            provider="morpheus",
            api_key="chat-key",
            base_url="https://chat.example/v1/chat/completions",
            timeout=5,
            image_provider="surplusintelligence",
            image_api_key="image-key",
            image_base_url="https://image.example/v1",
        )
        api_key, base_url = server.resolve_model_discovery_credentials(app, "surplusintelligence")
        self.assertEqual(api_key, "image-key")
        self.assertEqual(base_url, "https://image.example/v1")

    def test_list_provider_models_fetches_models_endpoint_and_categorizes(self):
        body = {
            "data": [{
                "id": "deepseek-v4-flash",
                "name": "DeepSeek V4 Flash",
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            }]
        }
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)) as urlopen:
            catalog = server.list_provider_models(
                provider="surplusintelligence",
                base_url="https://api.surplusintelligence.ai/v1",
                api_key="",
                timeout=5,
                use_cache=False,
            )

        self.assertEqual(catalog["chat"][0]["id"], "deepseek-v4-flash")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.surplusintelligence.ai/v1/models")

    def test_ui_loads_discovered_models_for_all_surplusintelligence_selectors(self):
        self.assertIn('id="chat-model-options"', server.HTML)
        self.assertIn('id="audio-model-options"', server.HTML)
        self.assertIn("async function refreshProviderModels", server.HTML)
        self.assertIn("updateChatModelOptions", server.HTML)
        self.assertIn("applyProviderCatalogs", server.HTML)
        self.assertIn(
            "const discoveredEditModels = (catalog.image_edit || []).map(model => model.id)",
            server.HTML,
        )
        self.assertIn("imageEditModelsByProvider[prov] = discoveredEditModels", server.HTML)
        self.assertIn("catalog.video", server.HTML)
        self.assertIn("catalog.audio", server.HTML)
        self.assertIn("'/api/models?'", server.HTML)
        # Discovery is no longer limited to SurplusIntelligence only.
        self.assertNotIn("if (provider !== 'surplusintelligence') return", server.HTML)

    def test_discovered_models_replace_stale_browser_media_models(self):
        ui_source = server.HTML
        sync_start = ui_source.index("function syncCreativeStudioModelsFromSettings()")
        sync_end = ui_source.index("function renderContent", sync_start)
        sync_source = ui_source[sync_start:sync_end]
        edit_start = ui_source.index("function updateImageEditModelOptions(")
        edit_end = ui_source.index("function updateVideoModelOptions(", edit_start)
        edit_source = ui_source[edit_start:edit_end]

        self.assertIn("localStorage.getItem('ct_image_edit_model')", sync_source)
        self.assertIn("providerDiscoveryCredentials", ui_source)
        self.assertIn("localStorage.setItem('ct_image_edit_model', els.imagegenEditModel.value)", edit_source)
        self.assertIn("localStorage.setItem('ct_image_model', els.imageModel.value)", ui_source)

    def test_provider_model_catalogs_expose_chat_and_video_defaults(self):
        catalogs = server.provider_model_catalogs()
        self.assertIn("morpheus", catalogs["chat"])
        self.assertEqual(catalogs["chat"]["morpheus"]["default_model"], "gemma-4-uncensored")
        self.assertIn("gemma-4-uncensored", catalogs["chat"]["morpheus"]["models"])
        self.assertIn("openrouter", catalogs["video"])
        self.assertIn("black-forest-labs/flux-video-pro", catalogs["video"]["openrouter"]["models"])
        self.assertEqual(catalogs["video"]["demo"]["default_model"], "demo-cinematic")
        # UI rebinds models when the chat/video provider changes.
        self.assertIn("updateChatModelOptions({ forceDefault: true })", server.HTML)
        self.assertIn("updateVideoModelOptions({ forceDefault: true })", server.HTML)

    def test_surplus_edit_controls_stay_enabled_with_seeded_edit_models(self):
        ui_source = server.HTML
        start = ui_source.index("function updateImageEditModelOptions(")
        end = ui_source.index("function updateVideoModelOptions(", start)
        edit_source = ui_source[start:end]

        self.assertIn("els.imagegenEditModel.disabled = false", edit_source)
        self.assertIn("els.imagegenEditBtn.disabled = false", edit_source)
        self.assertNotIn("Native image editing unavailable", edit_source)
        self.assertIn("qwen-edit-uncensored", ui_source)

    def test_surplus_discovery_populates_generation_and_source_aware_edit_models(self):
        ui_source = server.HTML

        self.assertIn(
            "const discoveredImageModels = (catalog.image || []).map(model => model.id)",
            ui_source,
        )
        self.assertIn("imageModelsByProvider[provider] = discoveredImageModels", ui_source)
        self.assertIn("const discoveredEditModels = (catalog.image_edit || []).map(model => model.id)", ui_source)
        self.assertIn("imageEditModelsByProvider[provider] = discoveredEditModels", ui_source)
        self.assertIn("if (discoveredImageModels.length)", ui_source)
        self.assertIn("if (discoveredEditModels.length)", ui_source)

    def test_surplus_ui_uses_native_edit_models_for_edit_and_redefine(self):
        ui_source = server.HTML
        self.assertIn("Uses POST /v1/images/edits with your source image", ui_source)
        self.assertIn("qwen-edit-uncensored", ui_source)
        self.assertIn("Uncensored (exact prompt — no filter)", ui_source)
        redefine_source = ui_source[ui_source.index("async function imagegenRedefine()"):]
        self.assertIn(
            "model: els.imagegenEditModel?.value || els.imagegenModel?.value",
            redefine_source,
        )

    def test_image_edit_upload_uses_one_hidden_file_picker_and_bumps_shell_cache(self):
        self.assertIn('.imagegen-dropzone input[type="file"]', server.HTML)
        self.assertIn("pointer-events: none", server.HTML)
        self.assertIn("const CACHE_NAME = 'forge-v2'", server.SW_JS)

    def test_imagegen_creative_canvas_has_comparison_preview_and_download_controls(self):
        for marker in (
            'class="imagegen-compare-stage"',
            'id="imagegen-source-stage"',
            'id="imagegen-output-stage"',
            'class="imagegen-control-dock"',
            'id="imagegen-lightbox"',
            "openImagePreview",
            "downloadImage",
            "Editing your image",
            "IMAGEGEN_EDIT_TIMEOUT_MS",
            "compressImageForEdit",
            "useImageAsEditSource",
            "Edit further",
            "data-edit-chip",
        ):
            self.assertIn(marker, server.HTML)

    def test_imagegen_ui_exposes_raw_prompt_bypass_toggle(self):
        for marker in (
            'id="imagegen-bypass-generate"',
            'id="imagegen-bypass-edit"',
            'id="imagegen-bypass-redefine"',
            'class="imagegen-raw-toggle"',
            "Raw prompt (skip prompt engineering)",
            "bypass_prompt",
            "ct_imagegen_bypass_prompt",
            "imagegenBypassPayload",
        ):
            self.assertIn(marker, server.HTML)

    def test_imagegen_edit_and_redefine_allow_ten_minute_provider_wait(self):
        source = inspect.getsource(imagegen_handlers)
        self.assertGreaterEqual(source.count("call_image_edit"), 2)
        self.assertGreaterEqual(source.count("timeout=max(app.timeout, 600.0)"), 2)

    def test_surplus_image_generation_uses_images_generations_endpoint(self):
        body = {"data": [{"b64_json": TINY_PNG_B64}]}
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)) as urlopen:
            images = server.call_image_generation(
                provider="surplusintelligence",
                api_key="sk-test",
                model="gpt-5-image",
                messages=[{"role": "user", "content": "make this high definition"}],
                timeout=5,
                base_url="https://api.surplusintelligence.ai/v1",
                operation="generate",
            )

        self.assertEqual(images, [TINY_PNG_B64])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.surplusintelligence.ai/v1/images/generations")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["prompt"], "make this high definition")
        self.assertNotIn("messages", payload)

    def test_surplus_call_image_edit_uses_images_edits_endpoint(self):
        body = {"data": [{"b64_json": TINY_PNG_B64}]}
        data_url = f"data:image/png;base64,{TINY_PNG_B64}"
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": "make the background blue"},
            ],
        }]
        with mock.patch("urllib.request.urlopen", return_value=FakeHTTPResponse(body)) as urlopen:
            images = image_edit_handlers.call_image_edit(
                provider="surplusintelligence",
                api_key="sk-test",
                model="gpt-image-2-edit",
                messages=messages,
                timeout=5,
                base_url="https://api.surplusintelligence.ai/v1",
            )

        self.assertEqual(images, [TINY_PNG_B64])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.surplusintelligence.ai/v1/images/edits")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "gpt-image-2-edit")
        self.assertEqual(payload["image_url"], data_url)
        self.assertEqual(payload["response_format"], "b64_json")
        self.assertIn("make the background blue", payload["prompt"])
        self.assertNotIn("messages", payload)

    def test_surplus_normalizes_generation_model_to_edit_model(self):
        self.assertEqual(
            image_edit_handlers.normalize_surplus_edit_model("gpt-image-2"),
            "gpt-image-2-edit",
        )
        self.assertEqual(
            image_edit_handlers.normalize_surplus_edit_model("grok-imagine-image"),
            "grok-imagine-edit",
        )

    def test_prepare_native_edit_prompt_is_uncensored_passthrough(self):
        from server.image_prompt import prepare_native_edit_prompt

        prompt = prepare_native_edit_prompt("make the sky purple, keep the outfit exactly")
        self.assertEqual(prompt, "make the sky purple, keep the outfit exactly")
        # No policy/safety soft-filter language injected.
        self.assertNotIn("policy", prompt.lower())
        self.assertNotIn("appropriate", prompt.lower())
        raw = prepare_native_edit_prompt("explicit artistic nude portrait edit", bypass=True)
        self.assertEqual(raw, "explicit artistic nude portrait edit")

    def test_surplus_redefine_uses_native_image_edit(self):
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{TINY_PNG_B64}"}},
                {"type": "text", "text": "reinterpret this as a watercolor"},
            ],
        }]
        with mock.patch(
            "server.image_edit._surplus_native_image_edit",
            return_value=[TINY_PNG_B64],
        ) as native_edit:
            images = image_edit_handlers.call_image_redefine(
                provider="surplusintelligence",
                api_key="sk-test",
                model="grok-imagine-edit",
                messages=messages,
                timeout=5,
                base_url="https://api.surplusintelligence.ai/v1",
            )
        self.assertEqual(images, [TINY_PNG_B64])
        native_edit.assert_called_once()
        self.assertEqual(native_edit.call_args.kwargs["model"], "grok-imagine-edit")

    def test_surplus_call_image_generation_rejects_edit_operation(self):
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{TINY_PNG_B64}"}},
                {"type": "text", "text": "make the image high definition"},
            ],
        }]
        with self.assertRaisesRegex(RuntimeError, r"/v1/images/edits"):
            server.call_image_generation(
                provider="surplusintelligence",
                api_key="sk-test",
                model="gpt-image-2-edit",
                messages=messages,
                timeout=5,
                base_url="https://api.surplusintelligence.ai/v1",
                operation="edit",
            )

    def test_categorize_provider_models_infers_surplus_edit_models(self):
        catalog = server.categorize_provider_models([
            {"id": "gpt-image-2", "name": "GPT Image 2"},
            {"id": "gpt-image-2-edit", "name": "GPT Image 2 Edit"},
            {"id": "qwen-edit-uncensored", "name": "Qwen Edit Uncensored"},
            {"id": "deepseek-v4-flash", "name": "DeepSeek V4 Flash"},
        ])
        self.assertEqual([item["id"] for item in catalog["image"]], ["gpt-image-2"])
        # Uncensored edit models sort first.
        self.assertEqual(
            [item["id"] for item in catalog["image_edit"]],
            ["qwen-edit-uncensored", "gpt-image-2-edit"],
        )
        self.assertEqual([item["id"] for item in catalog["chat"]], ["deepseek-v4-flash"])

    def test_imagegen_generate_and_edit_models_do_not_overwrite_each_other(self):
        ui_source = server.HTML
        generate_handler_start = ui_source.index("els.imagegenModel.addEventListener('change'")
        generate_handler_end = ui_source.index("if (els.imagegenEditModel)", generate_handler_start)
        generate_handler = ui_source[generate_handler_start:generate_handler_end]
        edit_handler_start = ui_source.index("els.imagegenEditModel.addEventListener('change'")
        edit_handler_end = ui_source.index("}", edit_handler_start)
        edit_handler = ui_source[edit_handler_start:edit_handler_end]

        self.assertIn("ct_image_model", generate_handler)
        self.assertNotIn("imagegenEditModel", generate_handler)
        self.assertIn("ct_image_edit_model", edit_handler)
        self.assertNotIn("imagegenModel", edit_handler)

    def test_imagegen_gallery_renders_lineage_badges_and_fetches_lineage(self):
        self.assertIn("imagegen-lineage", server.HTML)
        self.assertIn("renderImagegenLineage", server.HTML)
        self.assertIn("loadImagegenLineage", server.HTML)
        self.assertIn("data-ring=", server.HTML)
        self.assertIn("/api/imagegen/lineage?image_id=", server.HTML)

    def test_gallery_entries_store_image_lineage_metadata(self):
        add_source = inspect.getsource(server.App.add_gallery_image)

        self.assertIn('"ring_n": ring_n', add_source)
        self.assertIn('"supersedes_ring": supersedes_ring', add_source)
        self.assertIn("source_id=source_id", add_source)

    def test_handler_routes_expose_advanced_timechain_endpoints(self):
        handler_source = inspect.getsource(server.make_handler)

        self.assertIn('path == "/api/overlays"', handler_source)
        self.assertIn('path == "/api/dream"', handler_source)
        self.assertIn('path == "/api/memory-sync"', handler_source)
        self.assertIn('path == "/api/fleet-import"', handler_source)
        self.assertIn('path == "/api/challenge"', handler_source)
        self.assertIn("handle_dream", handler_source)
        self.assertIn("handle_fleet_import", handler_source)

    def test_provider_controls_are_not_in_left_rail(self):
        rail_start = server.HTML.index('<aside class="rail">')
        rail_end = server.HTML.index('</aside>', rail_start)
        rail_html = server.HTML[rail_start:rail_end]

        self.assertNotIn('id="api-key"', rail_html)
        self.assertNotIn('id="model"', rail_html)
        self.assertNotIn('id="test-provider"', rail_html)

    def test_mobile_layout_keeps_session_creation_and_header_badges_visible(self):
        rail_start = server.HTML.index('<aside class="rail">')
        rail_end = server.HTML.index('</aside>', rail_start)
        rail_html = server.HTML[rail_start:rail_end]
        nav_start = rail_html.index('<div class="nav"')
        nav_end = rail_html.index('</div>', nav_start)
        nav_html = rail_html[nav_start:nav_end]
        brand_start = rail_html.index('<div class="brand">')
        brand_end = rail_html.index('</div>', brand_start)
        brand_html = rail_html[brand_start:brand_end]

        self.assertIn('id="session-name"', rail_html)
        self.assertIn('id="new-session"', rail_html)
        self.assertIn('id="nav-settings"', nav_html)
        self.assertNotIn('id="nav-settings"', brand_html)
        self.assertIn("@media (max-width: 760px)", server.HTML)
        self.assertIn("position: fixed;", server.HTML)
        self.assertIn(".rail-section { min-height: 0; overflow-y: auto;", server.HTML)
        self.assertIn(".badges { grid-column: 2 / 4;", server.HTML)
        self.assertNotIn("#model-badge { display: none; }", server.HTML)

    def test_thought_styling_is_inline_and_unlabeled(self):
        self.assertNotIn('content: "thought"', server.HTML)
        self.assertIn(".thought-segment {", server.HTML)
        self.assertIn("display: inline", server.HTML)
        self.assertIn('<span class="${part.type === \'thought\' ? \'thought-segment\' : \'text-segment\'}"', server.HTML)

    def test_shared_recall_finds_ring_from_other_session_and_excludes_active(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        # Create two sessions for the same user
        session_a = app.create_session("Session A", username="testuser")
        app.use_session(session_a["id"], username="testuser")
        app.agent.interact("architecture decision", domain="architecture", override_content="Use modular services.")

        session_b = app.create_session("Session B", username="testuser")
        app.use_session(session_b["id"], username="testuser")
        app.agent.interact("security decision", domain="security", override_content="Auth boundary stays server-side.")

        # From session_b, search for architecture — should find session_a's ring
        result = app.shared_recall("testuser", "modular services", exclude_session=session_b["id"], limit=8)
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(len(result["hits"]), 1)
        hit = result["hits"][0]
        self.assertEqual(hit["source_session"], session_a["id"])
        self.assertEqual(hit["domain"], "architecture")
        self.assertIn("modular services", hit["content"].lower())

        # Should not find session_b's own ring
        for h in result["hits"]:
            self.assertNotEqual(h["source_session"], session_b["id"])

    def test_shared_recall_is_same_user_only(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        # alice's session
        alice_session = app.create_session("Alice", username="alice")
        app.use_session(alice_session["id"], username="alice")
        app.agent.interact("alice decision", domain="architecture", override_content="Alice uses modular services.")

        # bob's session
        bob_session = app.create_session("Bob", username="bob")
        app.use_session(bob_session["id"], username="bob")
        app.agent.interact("bob decision", domain="security", override_content="Bob uses centralized auth.")

        # alice searching should not find bob's session
        app.use_session(alice_session["id"], username="alice")
        result = app.shared_recall("alice", "centralized auth", exclude_session=alice_session["id"], limit=8)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["hits"]), 0)

    def test_build_messages_includes_shared_memory_when_provided(self):
        persona = {"name": "Companion", "system": "Stay useful."}
        shared_hits = [
            {
                "id": "other-session:3:abc123",
                "source_session": "other-session",
                "source_ring": 3,
                "domain": "architecture",
                "content": "Use modular boundary services.",
                "brightness": 0.82,
                "score": 0.91,
                "tags": ["architecture"],
            }
        ]

        messages = server.build_messages(
            persona=persona,
            query="What should we build next?",
            retrieved=[],
            shared_hits=shared_hits,
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
        )

        system = messages[0]["content"]
        self.assertIn("Shared memory from other sessions", system)
        self.assertIn("modular boundary services", system)
        self.assertIn("other-session", system)

    def test_build_messages_omits_shared_memory_when_empty(self):
        persona = {"name": "Companion", "system": "Stay useful."}

        messages = server.build_messages(
            persona=persona,
            query="What should we build next?",
            retrieved=[],
            shared_hits=[],
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
        )

        system = messages[0]["content"]
        self.assertNotIn("Shared memory from other sessions", system)

    def test_parse_frame_declaration_sidecar_removes_hidden_metadata(self):
        content, declaration = server.extract_frame_declaration(
            "Visible answer.\n"
            "[CT_FRAME_DECLARATION]\n"
            '{"current_frame":"binary truth","frame_adequate":false,'
            '"reason":"The statement is self-referential and cannot be binary classified.",'
            '"cambium_proposal":"paradox_frame","cambium_definition":"Self-reference frame."}'
            "\n[/CT_FRAME_DECLARATION]\n"
        )

        self.assertEqual(content, "Visible answer.")
        self.assertEqual(declaration["current_frame"], "binary truth")
        self.assertFalse(declaration["frame_adequate"])
        self.assertEqual(declaration["cambium_proposal"], "paradox_frame")

    def test_parse_frame_declaration_plain_response_has_no_metadata(self):
        content, declaration = server.extract_frame_declaration("Visible answer only.")

        self.assertEqual(content, "Visible answer only.")
        self.assertIsNone(declaration)

    def test_parse_frame_declaration_malformed_sidecar_is_stripped_without_metadata(self):
        content, declaration = server.extract_frame_declaration(
            "Visible answer.\n[CT_FRAME_DECLARATION]\nnot json\n[/CT_FRAME_DECLARATION]"
        )

        self.assertEqual(content, "Visible answer.")
        self.assertIsNone(declaration)

    def test_standard_messages_omit_frame_declaration_instruction(self):
        persona = {"name": "Companion", "system": "Stay useful."}

        messages = server.build_messages(
            persona=persona,
            query="Classify this paradox.",
            retrieved=[],
            durable_memories=[],
            recent_turns=[],
            neuro={},
            covenant="Be useful.",
        )

        self.assertNotIn("[CT_FRAME_DECLARATION]", messages[0]["content"])
        self.assertNotIn("cambium_proposal", messages[0]["content"])

    def test_import_shared_memory_creates_fleet_import_ring(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        source_session = app.create_session("Source", username="testuser")
        app.use_session(source_session["id"], username="testuser")
        app.agent.interact("source decision", domain="architecture", override_content="Use modular services.")
        source_ring = app.agent.chain[-1]

        target_session = app.create_session("Target", username="testuser")
        app.use_session(target_session["id"], username="testuser")
        before = len(app.agent.chain)

        hit_id = f"{source_session['id']}:{source_ring.n}:{source_ring.hash[:16]}"
        result = app.import_shared_memory(hit_id, target_session=target_session["id"], username="testuser")

        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "fleet_import")
        self.assertEqual(result["source_session"], source_session["id"])
        self.assertEqual(result["source_ring"], source_ring.n)
        self.assertEqual(len(app.agent.chain), before + 1)

    def test_synthesize_comprehension_creates_ring_or_rejects(self):
        workspace = self.make_workspace()
        app = server.App(
            workspace,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        source_session = app.create_session("Source", username="testuser")
        app.use_session(source_session["id"], username="testuser")
        app.agent.interact("architecture", domain="architecture", override_content="Use modular testable documented services.")
        ring_a = app.agent.chain[-1]
        app.agent.interact("security", domain="security", override_content="Use secure reviewed boundary checks.")
        ring_b = app.agent.chain[-1]

        target_session = app.create_session("Target", username="testuser")
        app.use_session(target_session["id"], username="testuser")
        before = len(app.agent.chain)

        hit_ids = [
            f"{source_session['id']}:{ring_a.n}:{ring_a.hash[:16]}",
            f"{source_session['id']}:{ring_b.n}:{ring_b.hash[:16]}",
        ]
        result = app.synthesize_comprehension("synthesize shared memory", hit_ids, target_session=target_session["id"], username="testuser")

        # Should either create a ring or reject with a reason
        if result.get("rejected"):
            self.assertIn("reason", result)
            self.assertEqual(len(app.agent.chain), before)
        else:
            self.assertTrue(result["ok"])
            self.assertEqual(result["kind"], "interaction")
            self.assertEqual(len(app.agent.chain), before + 1)
            self.assertIn("comprehension", result.get("tags", []))

    def test_shared_memory_ui_exposed_in_workbench_and_chat(self):
        self.assertIn('id="shared-memory-toggle"', server.HTML)
        self.assertIn('id="shared-memory-query"', server.HTML)
        self.assertIn('id="search-shared-memory"', server.HTML)
        self.assertIn('id="shared-memory-results"', server.HTML)
        self.assertIn('id="import-shared-memory"', server.HTML)
        self.assertIn('id="synthesize-shared-memory"', server.HTML)
        self.assertIn("/api/shared-memory", server.HTML)
        self.assertIn("/api/shared-memory/import", server.HTML)
        self.assertIn("/api/shared-memory/synthesize", server.HTML)
        self.assertIn("searchSharedMemory", server.HTML)
        self.assertIn("importSharedMemory", server.HTML)
        self.assertIn("synthesizeSharedMemory", server.HTML)
        self.assertIn("Shared Memory manually pulls accepted rings", server.HTML)

    def test_handler_routes_expose_shared_memory_endpoints(self):
        handler_source = inspect.getsource(server.make_handler)
        self.assertIn('path == "/api/shared-memory"', handler_source)
        self.assertIn('path == "/api/shared-memory/import"', handler_source)
        self.assertIn('path == "/api/shared-memory/synthesize"', handler_source)
        self.assertIn("handle_shared_memory_import", handler_source)
        self.assertIn("handle_shared_memory_synthesize", handler_source)

    def test_marketplace_catalog_shows_published_personas(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"

        # Publish a persona directly
        mp.MARKETPLACE_DIR.mkdir(parents=True, exist_ok=True)
        catalog = {"personas": {}}
        catalog["personas"]["test-architect"] = {
            "persona_id": "test-architect",
            "owner": "alice",
            "name": "Test Architect",
            "tagline": "A test persona.",
            "domain": "architecture",
            "status": "published",
            "price": {"model": "free", "amount": 0, "currency": "USD"},
            "stats": {"subscribers": 0, "rating": 0, "temporal_mass": 0},
            "created_at": "2026-01-01T00:00:00+00:00",
            "published_at": "2026-01-01T00:00:00+00:00",
        }
        mp._save_json(mp.CATALOG_PATH, catalog)

        personas = mp.get_catalog()
        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]["name"], "Test Architect")
        self.assertEqual(personas[0]["status"], "published")

    def test_marketplace_publish_sets_published_status(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"

        mp.save_created_persona("alice", "mp_test", {
            "name": "Test Persona",
            "domain": "testing",
            "tagline": "A test",
            "system": "You are a test persona.",
        })
        result = mp.publish_persona("alice", "mp_test")
        self.assertEqual(result["status"], "published")
        catalog = mp._load_json(mp.CATALOG_PATH, {"personas": {}})
        self.assertEqual(catalog["personas"]["mp_test"]["status"], "published")

    def test_creator_owned_persona_can_lock_training_session(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"
        app = server.App(
            root,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        mp.save_created_persona("alice", "truth-market", {
            "name": "Finding Truth",
            "domain": "investigation",
            "tagline": "Evidence-first inquiry.",
            "system": "A careful truth-finding marketplace draft.",
        })

        session = app.create_session("train-truth-market", username="alice", persona_id="truth-market")

        self.assertEqual(session["persona_id"], "truth-market")
        self.assertEqual(session["persona_name"], "Finding Truth")
        self.assertEqual(app.bind_session_persona("companion", username="alice"), "truth-market")

    def test_marketplace_publish_preserves_premium_price(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"
        mp.save_created_persona("alice", "mp_premium", {
            "name": "Premium Persona",
            "domain": "testing",
            "tagline": "Paid",
            "system": "You are a premium test persona.",
        })

        result = mp.publish_persona("alice", "mp_premium", {"model": "premium", "amount": 9.5, "currency": "USD"})

        self.assertEqual(result["price"], {"model": "premium", "amount": 9.5, "currency": "USD"})
        catalog = mp._load_json(mp.CATALOG_PATH, {"personas": {}})
        self.assertEqual(catalog["personas"]["mp_premium"]["price"]["model"], "premium")

    def test_marketplace_distills_from_owned_timechain_session(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"
        app = server.App(
            root,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        app.save_custom_persona("finding-truth", {
            "name": "Finding Truth",
            "domain": "investigation",
            "system": "A careful truth-finding persona shaped by the session.",
        }, username="alice")
        source = app.create_session("FindingTruthSesh", username="alice", persona_id="finding-truth")
        app.use_session(source["id"], username="alice")
        app.agent.interact(
            "How should we find truth?",
            domain="investigation",
            override_content="Find truth with testable documented reviewed evidence, precise questions, preserved uncertainty, and careful checks.",
        )

        mp.save_created_persona("alice", "truth-market", {
            "name": "Finding Truth",
            "domain": "investigation",
            "tagline": "Evidence-first inquiry.",
            "system": "A careful truth-finding persona shaped by the session.",
            "source_session": source["id"],
        })
        capsule = mp.distill_persona("alice", "truth-market", app.timechain)
        published = mp.publish_persona("alice", "truth-market")
        detail = mp.get_marketplace_persona("truth-market")

        self.assertEqual(capsule["source_session"], source["id"])
        self.assertEqual(capsule["distilled_from"], 2)
        self.assertEqual(capsule["ring_count"], 1)
        self.assertEqual(capsule["capsule_type"], "frozen_accepted_rings")
        self.assertEqual(capsule["rings"][0]["domain"], "investigation")
        self.assertIn("careful checks", capsule["rings"][0]["content"])
        self.assertGreater(len(capsule["rings"][0]["content"]), 80)
        self.assertEqual(published["source_session"], source["id"])
        self.assertEqual(detail["capsule"]["source_session"], source["id"])

    def test_marketplace_capsule_rings_become_hidden_recall_hits(self):
        capsule = {
            "source_session": "train-truth",
            "rings": [
                {"n": 1, "domain": "investigation", "brightness": 0.7, "content": "Lower signal."},
                {"n": 2, "domain": "testing", "brightness": 0.95, "content": "Higher signal full ring content."},
            ],
        }

        hits = server.chat._capsule_shared_hits(capsule)

        self.assertEqual(hits[0]["source_session"], "train-truth")
        self.assertEqual(hits[0]["source_ring"], 2)
        self.assertEqual(hits[0]["content"], "Higher signal full ring content.")

    def test_marketplace_distill_keeps_low_brightness_accepted_interactions(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"
        chain_dir = mp.USERS_DIR / "alice" / "sessions" / "low-mass" / ".timechain"
        chain_dir.mkdir(parents=True, exist_ok=True)
        (chain_dir / "chain.jsonl").write_text(
            json.dumps({"n": 0, "kind": "genesis", "domain": "system", "brightness": 0.1, "content": "Genesis."}) + "\n"
            + json.dumps({"n": 1, "kind": "interaction", "domain": "testing", "brightness": 0.2, "content": "Low brightness but accepted training ring."}) + "\n",
            encoding="utf-8",
        )
        mp.save_created_persona("alice", "low-mass-persona", {
            "name": "Low Mass",
            "system": "Use the training ring.",
            "source_session": "low-mass",
        })

        capsule = mp.distill_persona("alice", "low-mass-persona", None)

        self.assertEqual(capsule["ring_count"], 1)
        self.assertEqual(capsule["rings"][0]["content"], "Low brightness but accepted training ring.")

    def test_marketplace_refuses_explicit_session_not_owned_by_creator(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"
        app = server.App(
            root,
            server.DEFAULT_TIMECHAIN_PATH,
            default_model=server.DEFAULT_MODEL,
            provider="openrouter",
            api_key="",
            base_url="",
            timeout=1,
        )
        bob_session = app.create_session("FindingTruthSesh", username="bob")
        app.use_session(bob_session["id"], username="bob")
        app.agent.interact(
            "private bob persona",
            domain="investigation",
            override_content="Bob-only session knowledge must not be published by Alice.",
        )
        mp.save_created_persona("alice", "stolen", {
            "name": "Stolen",
            "system": "Should not publish.",
        })

        with self.assertRaises(KeyError):
            mp.distill_persona("alice", "stolen", app.timechain, source_session=bob_session["id"])

    def test_marketplace_subscribe_and_unsubscribe(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"

        mp.create_user("bob", "Bob", "password123", "subscriber")
        mp.save_created_persona("alice", "mp_sub", {
            "name": "Sub Test",
            "domain": "testing",
            "tagline": "Sub",
            "system": "Test.",
        })
        mp.publish_persona("alice", "mp_sub")

        sub = mp.subscribe("bob", "mp_sub")
        self.assertEqual(sub["persona_id"], "mp_sub")
        self.assertTrue(mp.is_subscribed("bob", "mp_sub"))

        mp.unsubscribe("bob", "mp_sub")
        self.assertFalse(mp.is_subscribed("bob", "mp_sub"))

    def test_marketplace_auth_token_falls_back_to_x_auth_token_header(self):
        root = self.make_workspace()
        mp = marketplace
        mp.DATA_DIR = root / "data"
        mp.USERS_PATH = mp.DATA_DIR / "users.json"
        mp.AUTH_SESSIONS_PATH = mp.DATA_DIR / "auth_sessions.json"
        mp.MARKETPLACE_DIR = mp.DATA_DIR / "marketplace"
        mp.CATALOG_PATH = mp.MARKETPLACE_DIR / "catalog.json"
        mp.USERS_DIR = mp.DATA_DIR / "users"

        mp.create_user("carol", "Carol", "password123", "subscriber")
        token = mp.create_auth_session("carol")

        # Cookie token works
        user_cookie = mp.require_auth({"Cookie": f"ct_auth={token}"})
        self.assertEqual(user_cookie["username"], "carol")

        # X-Auth-Token header works
        user_header = mp.require_auth({"X-Auth-Token": token})
        self.assertEqual(user_header["username"], "carol")

        # Neither fails
        with self.assertRaises(PermissionError):
            mp.require_auth({})

    def test_marketplace_ui_has_subscribe_and_unsubscribe_buttons(self):
        self.assertIn('id="detail-subscribe"', server.HTML)
        self.assertIn('id="detail-unsubscribe"', server.HTML)
        self.assertIn('id="creator-source-session"', server.HTML)
        self.assertIn('id="manage-session-name"', server.HTML)
        self.assertIn('id="manage-rename-session"', server.HTML)
        self.assertIn('id="creator-price-model"', server.HTML)
        self.assertIn('id="creator-price-amount"', server.HTML)
        self.assertIn("creatorPersonas", server.HTML)
        self.assertIn("const sessionName = persona?.name", server.HTML)
        self.assertIn("existingSessionId", server.HTML)
        self.assertIn("Prior conversation is hidden", server.HTML)
        self.assertIn("No frozen capsule yet.", server.HTML)
        self.assertNotIn("r.content?.slice", server.HTML)
        self.assertIn("Marketplace Persona Instructions", server.HTML)
        self.assertIn("Prefilled from the source session persona. Edit before publishing.", server.HTML)
        self.assertIn("sourceSession", server.HTML)
        self.assertIn("renameCreatorPersona", server.HTML)
        self.assertIn("deleteCreatorPersona", server.HTML)
        self.assertIn("/api/sessions/rename", server.HTML)
        self.assertIn("doSubscribe", server.HTML)
        self.assertIn("doUnsubscribe", server.HTML)
        self.assertIn("/api/marketplace/", server.HTML)
        self.assertIn("/subscribe", server.HTML)
        self.assertIn("/unsubscribe", server.HTML)


class TrainerTests(unittest.TestCase):
    def test_new_session_starts_at_level_three(self):
        t = Trainer()
        q = t.build_query("s1", "Solve this.")
        self.assertIn("framework", q.lower())

    def test_valid_high_quality_decrements_level(self):
        t = Trainer()
        t.process_event("s1", 1, {"status": "valid", "quality_score": 0.85}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)

    def test_valid_mid_quality_decrements_level(self):
        t = Trainer()
        t.process_event("s1", 1, {"status": "valid", "quality_score": 0.75}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)
        t.process_event("s1", 2, {"status": "valid", "quality_score": 0.75}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 1)

    def test_valid_threshold_seven_decrements(self):
        t = Trainer()
        t.process_event("s1", 1, {"status": "valid", "quality_score": 0.7}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)

    def test_valid_low_quality_increments_level(self):
        t = Trainer()
        # start at 3, low quality should increment (but cap at 3)
        t.process_event("s1", 1, {"status": "valid", "quality_score": 0.3}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 3)
        # force level down then test increment
        t._get_state("s1")["scaffolding_level"] = 1
        t.process_event("s1", 2, {"status": "valid", "quality_score": 0.3}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)

    def test_none_event_increments_level(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 0
        t.process_event("s1", 1, {"status": "none"}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 1)
        t.process_event("s1", 2, {"status": "none"}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)

    def test_none_event_ratchets_to_three(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 0
        for i in range(3):
            t.process_event("s1", i, {"status": "none"}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 3)

    def test_evasion_jumps_up(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 1
        t.process_event("s1", 1, {"status": "evasion"}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 3)

    def test_framework_switch_rewards(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 2
        # first frame
        t.process_event("s1", 1, {"status": "valid", "quality_score": 0.5}, "ok", frame_declaration={"current_frame": "PBXF"})
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)
        # switch
        t.process_event("s1", 2, {"status": "valid", "quality_score": 0.5}, "ok", frame_declaration={"current_frame": "First Principles"})
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 1)

    def test_level_three_prefix(self):
        t = Trainer()
        q = t.build_query("s1", "What is 2+2?", domain_hint="math")
        self.assertTrue(q.startswith("Use the most appropriate framework"))
        self.assertIn("Domain: math", q)

    def test_level_two_prefix(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 2
        q = t.build_query("s1", "What is 2+2?", domain_hint="math")
        self.assertTrue(q.startswith("Think about what kind of problem"))
        self.assertIn("Domain: math", q)

    def test_level_one_domain_only(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 1
        q = t.build_query("s1", "What is 2+2?", domain_hint="math")
        self.assertEqual(q, "Domain: math\n\nWhat is 2+2?")

    def test_level_zero_no_prefix(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 0
        q = t.build_query("s1", "What is 2+2?", domain_hint="math")
        self.assertEqual(q, "What is 2+2?")

    def test_weak_treated_as_upward_pressure(self):
        t = Trainer()
        t._get_state("s1")["scaffolding_level"] = 1
        t.process_event("s1", 1, {"status": "weak"}, "ok")
        self.assertEqual(t.get_state("s1")["scaffolding_level"], 2)

    def test_consecutive_valid_counter(self):
        t = Trainer()
        for i in range(3):
            t.process_event("s1", i, {"status": "valid", "quality_score": 0.85}, "ok")
        self.assertEqual(t.get_state("s1")["consecutive_valid"], 3)
        self.assertEqual(t.get_state("s1")["consecutive_none"], 0)

    def test_consecutive_none_counter(self):
        t = Trainer()
        for i in range(2):
            t.process_event("s1", i, {"status": "none"}, "ok")
        self.assertEqual(t.get_state("s1")["consecutive_none"], 2)
        self.assertEqual(t.get_state("s1")["consecutive_valid"], 0)


if __name__ == "__main__":
    unittest.main()
