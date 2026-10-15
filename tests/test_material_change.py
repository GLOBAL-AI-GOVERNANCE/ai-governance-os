"""Positive and negative tests for material-change invalidation.
"""
from __future__ import annotations

import unittest

from tools.validate_material_change import ContractError, validate_material_change_invalidation

PRIOR = {
    "binding_id": "acb-001",
    "subject_id": "synthetic-system",
    "configuration_digest": "sha256:" + "a" * 64,
    "dataset_digest": "sha256:" + "b" * 64,
    "context_boundary": "synthetic evaluation",
    "evidence_provenance": {"source": "synth", "timestamp": "2026-10-15T00:00:00Z", "digest": "sha256:" + "c" * 64},
    "validity_from": "2026-10-15T00:00:00Z",
    "invalidation_triggers": ["configuration change", "dataset change"],
    "reference_only": True,
    "authority_effect": "NONE",
}


class MaterialChangeTests(unittest.TestCase):
    def test_no_change_accepted(self) -> None:
        result = validate_material_change_invalidation(PRIOR, PRIOR["configuration_digest"], PRIOR["dataset_digest"])
        self.assertTrue(result["current_assurance_valid"])
        self.assertFalse(result["requires_re_evaluation"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_config_change_invalidates(self) -> None:
        result = validate_material_change_invalidation(PRIOR, "sha256:" + "d" * 64, PRIOR["dataset_digest"])
        self.assertFalse(result["current_assurance_valid"])
        self.assertTrue(result["requires_re_evaluation"])
        self.assertTrue(result["historical_record_valid"])

    def test_dataset_change_invalidates(self) -> None:
        result = validate_material_change_invalidation(PRIOR, PRIOR["configuration_digest"], "sha256:" + "e" * 64)
        self.assertFalse(result["current_assurance_valid"])
        self.assertTrue(result["requires_re_evaluation"])

    def test_negative_authority(self) -> None:
        bad = {**PRIOR, "authority_effect": "AUTHORIZE"}
        with self.assertRaises(ContractError):
            validate_material_change_invalidation(bad, PRIOR["configuration_digest"])

    def test_negative_missing_triggers(self) -> None:
        bad = {**PRIOR, "invalidation_triggers": []}
        with self.assertRaises(ContractError):
            validate_material_change_invalidation(bad, PRIOR["configuration_digest"])


if __name__ == "__main__":
    unittest.main()
