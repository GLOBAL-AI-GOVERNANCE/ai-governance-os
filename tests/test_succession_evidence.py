from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.validate_succession_evidence import ContractError, validate_succession_evidence

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = json.loads((ROOT / "sample-data" / "succession-evidence-record.json").read_text(encoding="utf-8"))


class SuccessionEvidenceTests(unittest.TestCase):
    def test_valid_success(self) -> None:
        result = validate_succession_evidence(SAMPLE)
        self.assertTrue(result["valid"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_partial_and_failed_preserve_incomplete_state(self) -> None:
        partial = {**SAMPLE, "outcome": "PARTIAL", "recovery_demonstrated": False}
        failed = {**SAMPLE, "outcome": "FAILED", "capability_resumed": False, "undocumented_dependencies_found": ["synthetic-gap"]}
        self.assertEqual(validate_succession_evidence(partial)["outcome"], "PARTIAL")
        self.assertEqual(validate_succession_evidence(failed)["outcome"], "FAILED")

    def test_success_negatives(self) -> None:
        cases = [
            ({**SAMPLE, "creator_assistance_required": True}, "creator assistance"),
            ({**SAMPLE, "recovery_demonstrated": False}, "missing recovery"),
            ({**SAMPLE, "fallback_demonstrated": False}, "failed fallback"),
            ({**SAMPLE, "undocumented_dependencies_found": ["hidden-api"]}, "undocumented dependency"),
            ({**SAMPLE, "support_owner": ""}, "missing support owner"),
            ({**SAMPLE, "support_commitment_ref": ""}, "missing support commitment"),
            ({**SAMPLE, "configuration_digest": "sha256:short"}, "malformed digest"),
            ({**SAMPLE, "authority_effect": "AUTHORIZE"}, "non-NONE authority"),
            ({**SAMPLE, "reference_only": False}, "false reference_only"),
            ({**SAMPLE, "human_review_required": False}, "false human review"),
            ({**SAMPLE, "extra": "bad"}, "unsupported field"),
        ]
        for record, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    validate_succession_evidence(record)


if __name__ == "__main__":
    unittest.main()
