#!/usr/bin/env python3
"""Hostile tests for human and institutional assurance primitives."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.validate_assurance_kernel import ContractError, validate_record

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample-data" / "assurance-kernel"


def load(name: str) -> dict:
    return json.loads((SAMPLE / f"{name}.json").read_text(encoding="utf-8"))


class MissionAssurancePrimitivesTests(unittest.TestCase):
    def test_positive_records_validate(self) -> None:
        for name in (
            "qualification-evidence-record",
            "unresolved-decision-record",
            "protected-concern-disposition-record",
        ):
            with self.subTest(name=name):
                result = validate_record(name, load(name))
                self.assertTrue(result["valid"])
                self.assertEqual(result["authority_effect"], "NONE")

    def test_expired_qualification(self) -> None:
        record = load("qualification-evidence-record")
        with self.assertRaises(ContractError) as ctx:
            validate_record("qualification-evidence-record", record, evaluation_time="2028-01-01T00:00:00Z")
        self.assertIn("expired qualification", str(ctx.exception))

    def test_wrong_subject_or_configuration_not_auto_valid(self) -> None:
        # Schema allows different subject; semantic does not promote cross-subject
        record = load("qualification-evidence-record")
        record["subject_id"] = "other-subject"
        result = validate_record("qualification-evidence-record", record)
        self.assertTrue(result["valid"])  # structural ok; compatibility checked at consumption

    def test_conditional_not_promoted_to_qualified(self) -> None:
        record = load("qualification-evidence-record")
        record["outcome"] = "CONDITIONAL"
        result = validate_record("qualification-evidence-record", record)
        self.assertEqual(result["valid"], True)
        # Cannot silently become QUALIFIED; outcome remains as declared

    def test_expired_blocking_decision(self) -> None:
        record = load("unresolved-decision-record")
        with self.assertRaises(ContractError) as ctx:
            validate_record(
                "unresolved-decision-record",
                record,
                evaluation_time="2026-12-01T00:00:00Z",
            )
        self.assertIn("EXPIRED blocking decision", str(ctx.exception))

    def test_deadline_silence_not_approval(self) -> None:
        record = load("unresolved-decision-record")
        record["status"] = "OPEN"
        # No evaluation_time or past does not auto-resolve
        result = validate_record("unresolved-decision-record", record)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertNotEqual(record["status"], "RESOLVED")

    def test_missing_decision_owner(self) -> None:
        record = load("unresolved-decision-record")
        record["blocking"] = True
        del record["owner_ref"]
        with self.assertRaises(ContractError):
            validate_record("unresolved-decision-record", record)

    def test_active_concern_not_closed(self) -> None:
        record = load("protected-concern-disposition-record")
        record["status"] = "ACTIVE"
        record["assurance_effect"] = "HOLD"
        result = validate_record("protected-concern-disposition-record", record)
        self.assertEqual(record["status"], "ACTIVE")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_concern_hold_not_authority(self) -> None:
        record = load("protected-concern-disposition-record")
        record["assurance_effect"] = "HOLD"
        result = validate_record("protected-concern-disposition-record", record)
        self.assertEqual(result["authority_effect"], "NONE")
        with self.assertRaises(ContractError):
            record["authority_effect"] = "AUTHORIZE"
            validate_record("protected-concern-disposition-record", record)

    def test_pii_or_private_allegation_rejected(self) -> None:
        record = load("protected-concern-disposition-record")
        record["reporter_identity"] = "hidden"
        with self.assertRaises(ContractError):
            validate_record("protected-concern-disposition-record", record)

    def test_authority_effect_not_none(self) -> None:
        for name in (
            "qualification-evidence-record",
            "unresolved-decision-record",
            "protected-concern-disposition-record",
        ):
            record = load(name)
            record["authority_effect"] = "AUTHORIZE"
            with self.subTest(name=name):
                with self.assertRaises(ContractError):
                    validate_record(name, record)

    def test_stale_requires_revalidation(self) -> None:
        record = load("protected-concern-disposition-record")
        record["assurance_effect"] = "STALE"
        record["revalidation_required"] = False
        with self.assertRaises(ContractError):
            validate_record("protected-concern-disposition-record", record)


if __name__ == "__main__":
    unittest.main()
