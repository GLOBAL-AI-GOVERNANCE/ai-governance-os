"""Positive and negative tests for material-change invalidation of evaluation basis.
"""
from __future__ import annotations

import unittest

from tools.validate_material_change import ContractError, validate_material_change_invalidation

PRIOR = {
    "evaluation_id": "eval-001",
    "subject_id": "synthetic-system",
    "dataset_id": "synth-dataset-v1",
    "dataset_digest": "sha256:" + "a" * 64,
    "model_id": "synth-model-v1",
    "model_digest": "sha256:" + "b" * 64,
    "configuration_digest": "sha256:" + "c" * 64,
    "context_boundary": "synthetic evaluation environment",
    "evaluation_outcome": "synthetic outcome recorded",
    "evidence_provenance": {
        "source": "synthetic evaluation run",
        "timestamp": "2026-10-15T00:00:00Z",
        "digest": "sha256:" + "d" * 64,
    },
    "invalidation_triggers": ["dataset change", "model change", "configuration change"],
    "reference_only": True,
    "authority_effect": "NONE",
}


class MaterialChangeTests(unittest.TestCase):
    def test_no_change_reports_no_change(self) -> None:
        result = validate_material_change_invalidation(
            PRIOR, PRIOR["configuration_digest"], PRIOR["dataset_digest"], PRIOR["model_digest"]
        )
        self.assertEqual(result["status"], "NO_CHANGE_DETECTED")
        self.assertFalse(result["current_assurance_from_prior"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_dataset_change_invalidates(self) -> None:
        result = validate_material_change_invalidation(
            PRIOR, PRIOR["configuration_digest"], "sha256:" + "e" * 64, PRIOR["model_digest"]
        )
        self.assertEqual(result["status"], "MATERIAL_CHANGE")
        self.assertFalse(result["current_assurance_from_prior"])
        self.assertTrue(result["requires_re_evaluation"])

    def test_model_change_invalidates(self) -> None:
        result = validate_material_change_invalidation(
            PRIOR, PRIOR["configuration_digest"], PRIOR["dataset_digest"], "sha256:" + "f" * 64
        )
        self.assertEqual(result["status"], "MATERIAL_CHANGE")
        self.assertTrue(result["requires_re_evaluation"])

    def test_config_change_invalidates(self) -> None:
        result = validate_material_change_invalidation(
            PRIOR, "sha256:" + "0" * 64, PRIOR["dataset_digest"], PRIOR["model_digest"]
        )
        self.assertEqual(result["status"], "MATERIAL_CHANGE")

    def test_negative_cases(self) -> None:
        cases = [
            ({**PRIOR, "authority_effect": "AUTHORIZE"}, PRIOR["configuration_digest"], PRIOR["dataset_digest"], PRIOR["model_digest"], "non-NONE authority"),
            ({**PRIOR, "invalidation_triggers": []}, PRIOR["configuration_digest"], PRIOR["dataset_digest"], PRIOR["model_digest"], "empty triggers"),
            (PRIOR, "sha256:short", PRIOR["dataset_digest"], PRIOR["model_digest"], "malformed current digest"),
            ({**PRIOR, "dataset_digest": "sha256:" + "a" * 63}, PRIOR["configuration_digest"], PRIOR["dataset_digest"], PRIOR["model_digest"], "malformed prior digest"),
            ({**PRIOR, "extra": "bad"}, PRIOR["configuration_digest"], PRIOR["dataset_digest"], PRIOR["model_digest"], "unsupported field"),
        ]
        for prior, config, dataset, model, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    validate_material_change_invalidation(prior, config, dataset, model)


if __name__ == "__main__":
    unittest.main()
