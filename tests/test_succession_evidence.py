from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from tools.validate_succession_evidence import TIMESTAMP, ContractError, validate_succession_evidence

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



    def test_schema_parity_rejects_malformed_records(self) -> None:
        cases = [
            ({**SAMPLE, "subject_id": ""}, "empty subject"),
            ({**SAMPLE, "environment_boundary": ""}, "empty environment"),
            ({**SAMPLE, "evaluated_at": "15 October 2026"}, "invalid evaluated_at"),
            ({**SAMPLE, "successor_team_ref": ""}, "empty successor team"),
            ({**SAMPLE, "configuration_restored": "true"}, "string instead of boolean"),
            ({**SAMPLE, "limitations": []}, "empty limitations"),
            ({**SAMPLE, "undocumented_dependencies_found": [1]}, "non-string dependency"),
            ({**SAMPLE, "handoff_artifacts": [{"reference": "", "digest": "sha256:" + "a" * 64}]}, "malformed nested artifact"),
            ({**SAMPLE, "outcome": "PARTIAL", "evaluated_at": "not-a-time"}, "malformed partial"),
            ({**SAMPLE, "outcome": "FAILED", "limitations": [""]}, "malformed failed"),
        ]
        for record, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    validate_succession_evidence(record)

    def test_public_schema_rejects_malformed_timestamps_independently(self) -> None:
        schema = json.loads((ROOT / "schemas" / "succession-evidence-record.schema.json").read_text(encoding="utf-8"))
        pattern = schema["properties"]["evaluated_at"]["pattern"]
        self.assertEqual(pattern, TIMESTAMP.pattern)
        self.assertIsNotNone(re.fullmatch(pattern, SAMPLE["evaluated_at"]))
        for value in ("15 October 2026", "2026-10-15", "2026-10-15T00:00:00+00:00", ""):
            self.assertIsNone(re.fullmatch(pattern, value))
            with self.assertRaises(ContractError):
                validate_succession_evidence({**SAMPLE, "evaluated_at": value})


if __name__ == "__main__":
    unittest.main()
