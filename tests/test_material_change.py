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
    def _call(self, prior=PRIOR, subject=None, dataset=None, model=None, context=None,
              config=None, dataset_digest=None, model_digest=None):
        return validate_material_change_invalidation(
            prior,
            subject or prior["subject_id"],
            dataset or prior["dataset_id"],
            model or prior["model_id"],
            context or prior["context_boundary"],
            config or prior["configuration_digest"],
            dataset_digest or prior["dataset_digest"],
            model_digest or prior["model_digest"],
        )

    def test_no_change_reports_no_change(self) -> None:
        result = self._call()
        self.assertEqual(result["status"], "NO_CHANGE_DETECTED")
        self.assertFalse(result["current_assurance_from_prior"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_dataset_digest_change_invalidates(self) -> None:
        result = self._call(dataset_digest="sha256:" + "e" * 64)
        self.assertEqual(result["status"], "MATERIAL_CHANGE")
        self.assertFalse(result["current_assurance_from_prior"])
        self.assertTrue(result["requires_re_evaluation"])

    def test_model_digest_change_invalidates(self) -> None:
        result = self._call(model_digest="sha256:" + "f" * 64)
        self.assertEqual(result["status"], "MATERIAL_CHANGE")

    def test_config_digest_change_invalidates(self) -> None:
        result = self._call(config="sha256:" + "0" * 64)
        self.assertEqual(result["status"], "MATERIAL_CHANGE")

    def test_identity_mismatches(self) -> None:
        cases = [
            ("wrong-subject", None, None, None, "subject"),
            (None, "wrong-dataset", None, None, "dataset identity"),
            (None, None, "wrong-model", None, "model identity"),
            (None, None, None, "wrong context", "context"),
        ]
        for subject, dataset, model, context, label in cases:
            with self.subTest(label=label):
                result = self._call(subject=subject, dataset=dataset, model=model, context=context)
                self.assertEqual(result["status"], "IDENTITY_MISMATCH")
                self.assertFalse(result["current_assurance_from_prior"])

    def test_negative_cases(self) -> None:
        cases = [
            ({**PRIOR, "authority_effect": "AUTHORIZE"}, "non-NONE authority"),
            ({**PRIOR, "invalidation_triggers": []}, "empty triggers"),
            ({**PRIOR, "invalidation_triggers": "not-a-list"}, "non-array triggers"),
            ({**PRIOR, "dataset_digest": "sha256:short"}, "malformed prior digest"),
            ({**PRIOR, "extra": "bad"}, "unsupported field"),
            ({**PRIOR, "evidence_provenance": {**PRIOR["evidence_provenance"], "extra": "bad"}}, "extra provenance field"),
            ({**PRIOR, "evaluation_id": ""}, "empty evaluation_id"),
            ({**PRIOR, "subject_id": ""}, "empty subject_id"),
            ({**PRIOR, "evaluation_outcome": ""}, "empty outcome"),
            ({**PRIOR, "evidence_provenance": {**PRIOR["evidence_provenance"], "source": 123}}, "non-string provenance source"),
        ]
        for prior, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    self._call(prior=prior)


if __name__ == "__main__":
    unittest.main()
