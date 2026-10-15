from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.validate_assurance_kernel import FILES, ContractError, validate_kernel_directory, validate_record

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "sample-data" / "assurance-kernel"


def load(name: str) -> dict:
    return json.loads((SAMPLE_DIR / f"{name}.json").read_text(encoding="utf-8"))


class AssuranceKernelTests(unittest.TestCase):
    def test_samples_pass(self) -> None:
        validate_kernel_directory()
        for name in FILES:
            result = validate_record(name, load(name))
            self.assertEqual(result["authority_effect"], "NONE")
            self.assertTrue(result["reference_only"])

    def test_evidence_class_does_not_relax_limits(self) -> None:
        for evidence_class in ("OBSERVED", "MODEL_INFERENCE", "SIMULATION", "HUMAN_INFERENCE"):
            record = load("evidence-object")
            record["evidence_class"] = evidence_class
            result = validate_record("evidence-object", record)
            self.assertIn("does not establish truth", result["note"])

    def test_unknown_and_reconciliation_and_drift_fail_closed(self) -> None:
        cases = [
            ("unknown-object", {**load("unknown-object"), "status": "RESOLVED"}, "resolved without evidence"),
            ("unknown-object", {**load("unknown-object"), "blocking": True, "status": "ACCEPTED"}, "hidden blocking unknown"),
            ("state-reconciliation-record", {**load("state-reconciliation-record"), "outcome": "UNKNOWN", "reconciled_state": "MATCH"}, "unknown promoted"),
            ("state-reconciliation-record", {**load("state-reconciliation-record"), "outcome": "DIVERGENCE", "reconciled_state": "DIVERGENCE", "reassessment_required": False}, "divergence without reassessment"),
            ("observed-state-snapshot", {k: v for k, v in load("observed-state-snapshot").items() if k != "provenance"}, "observation without provenance"),
            ("drift-event", {**load("drift-event"), "material": True, "reassessment_required": False}, "material drift"),
            ("drift-event", {**load("drift-event"), "automatic_retrain": True}, "automatic retrain"),
            ("evidence-object", {**load("evidence-object"), "authority_effect": "AUTHORIZE"}, "authority transfer"),
            ("context-boundary-record", {**load("context-boundary-record"), "reference_only": False}, "legal-style override"),
        ]
        for name, record, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    validate_record(name, record)

    def test_match_unknown_and_divergence_are_distinct(self) -> None:
        unknown = {**load("state-reconciliation-record"), "outcome": "UNKNOWN", "reconciled_state": "UNKNOWN", "reassessment_required": True}
        divergence = {**load("state-reconciliation-record"), "outcome": "DIVERGENCE", "reconciled_state": "DIVERGENCE", "reassessment_required": True}
        self.assertEqual(validate_record("state-reconciliation-record", unknown)["valid"], True)
        self.assertEqual(validate_record("state-reconciliation-record", divergence)["valid"], True)


if __name__ == "__main__":
    unittest.main()
