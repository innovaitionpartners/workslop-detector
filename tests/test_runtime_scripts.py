#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/workslop-detector"
SCANNER = SKILL_DIR / "scripts/scan_ai_residue.py"
VALIDATOR = SKILL_DIR / "scripts/validate_agent_output.py"


class RuntimeScriptTests(unittest.TestCase):
    def run_scanner(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_text(text, encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCANNER), str(source)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

    def run_validator(self, role: str, payload: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "output.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), role, str(source)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_scanner_finds_direct_assistant_offer(self) -> None:
        result = self.run_scanner("Decision: launch Friday.\nWould you like me to make slides?")
        self.assertEqual(result["summary"]["high_confidence_count"], 1)
        self.assertEqual(result["high_confidence"][0]["pattern_id"], "assistant_offer")

    def test_scanner_does_not_flag_normal_delivery_language(self) -> None:
        result = self.run_scanner("Here is the recommendation: launch Friday.")
        self.assertEqual(result["summary"]["high_confidence_count"], 0)

    def test_scanner_surfaces_placeholder_for_contextual_review(self) -> None:
        result = self.run_scanner("Employee: [Insert employee name]")
        self.assertEqual(result["high_confidence"][0]["pattern_id"], "unresolved_placeholder")

    def test_baseline_contract_accepts_exact_shape(self) -> None:
        payload = {
            "reviewer_id": "baseline-a",
            "assignment_interpretation": "Recommend a vendor.",
            "response_outline": ["Recommendation", "Reasons"],
            "recommendations": ["Compare the vendors."],
            "specifics_available_from_request": ["Budget is $50,000."],
            "missing_information": ["Pilot results"],
            "assumptions": [],
        }
        result = self.run_validator("baseline", payload)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_baseline_contract_rejects_extra_keys(self) -> None:
        payload = {
            "reviewer_id": "baseline-a",
            "assignment_interpretation": "Recommend a vendor.",
            "response_outline": [],
            "recommendations": [],
            "specifics_available_from_request": [],
            "missing_information": [],
            "assumptions": [],
            "verdict": "WORKSLOP",
        }
        result = self.run_validator("baseline", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("keys mismatch", result.stderr)

    def valid_arbiter_payload(self) -> dict:
        return {
            "target_reader": "COO",
            "verdict": "NOT_WORKSLOP",
            "workslop": False,
            "human_delta": {
                "rating": "HIGH",
                "evidence": ["Contains verified pilot results."],
                "baseline_convergence": ["Baselines lacked the pilot data."],
            },
            "reader_burden": {"rating": "LOW", "evidence": ["Recommendation leads."]},
            "review_diligence": {
                "rating": "CLEAN",
                "evidence": ["No confirmed residue."],
                "confirmed_residue": [],
            },
            "trust_check": {
                "claims_needing_support": [],
                "contradictions": [],
                "effect_on_reader_burden": "",
            },
            "receipts": ["Recommendation leads.", "Pilot evidence is quantified."],
            "funny_diagnosis": "A human was here.",
            "serious_diagnosis": "The document is decision-ready.",
            "recommended_action": "ACCEPT",
            "funny_reply": "",
            "serious_reply": "",
            "limitations": [],
        }

    def test_arbiter_contract_accepts_matrix_result(self) -> None:
        result = self.run_validator("arbiter", self.valid_arbiter_payload())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_arbiter_contract_rejects_matrix_conflict(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["verdict"] = "WORKSLOP_POLISHED_GENERIC"
        payload["workslop"] = True
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("conflicts with matrix", result.stderr)

    def test_arbiter_contract_rejects_wrong_action(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["recommended_action"] = "REQUEST_JUDGMENT"
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("recommended_action must be ACCEPT", result.stderr)

    def test_arbiter_contract_rejects_internal_jargon_in_reply(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["serious_diagnosis"] = "This document has low human delta."
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("contains internal jargon: human delta", result.stderr)

    def test_arbiter_contract_accepts_material_trust_findings(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["trust_check"] = {
            "claims_needing_support": [
                {
                    "quote": "This will reduce costs by 30%.",
                    "reason": "No source or internal provenance is named.",
                    "materiality": "HIGH",
                }
            ],
            "contradictions": [
                {
                    "first_quote": "Launch weekly updates.",
                    "second_quote": "Publish updates every two weeks.",
                    "reason": "The proposed cadence conflicts.",
                    "materiality": "MODERATE",
                }
            ],
            "effect_on_reader_burden": "The reader must verify the savings claim and resolve the cadence.",
        }
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_arbiter_contract_rejects_malformed_trust_finding(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["trust_check"]["claims_needing_support"] = [
            {"quote": "Costs fall 30%.", "reason": "No source."}
        ]
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("claims_needing_support[0] has invalid shape", result.stderr)

    def test_moderate_burden_with_high_delta_requires_edit(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["verdict"] = "NOT_WORKSLOP_NEEDS_EDIT"
        payload["reader_burden"] = {
            "rating": "MODERATE",
            "evidence": ["Thirty-five percent is removable."],
        }
        payload["recommended_action"] = "REQUEST_COMPRESSION"
        payload["funny_reply"] = "Please tighten this before sending."
        payload["serious_reply"] = "Please shorten this before sending."
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_arbiter_contract_rejects_identical_funny_and_serious_replies(self) -> None:
        payload = self.valid_arbiter_payload()
        payload["verdict"] = "NOT_WORKSLOP_NEEDS_EDIT"
        payload["reader_burden"] = {
            "rating": "MODERATE",
            "evidence": ["Thirty-five percent is removable."],
        }
        payload["recommended_action"] = "REQUEST_COMPRESSION"
        payload["funny_reply"] = "Please shorten this before sending."
        payload["serious_reply"] = "Please shorten this before sending."
        result = self.run_validator("arbiter", payload)
        self.assertEqual(result.returncode, 3)
        self.assertIn("funny_reply must differ from serious_reply", result.stderr)


if __name__ == "__main__":
    unittest.main()
