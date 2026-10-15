"""Material-change invalidation for evaluation basis records.

Does not implement runtime monitoring. Accepts explicitly supplied prior evaluation basis and current digests.
Returns non-authorizing result. authority_effect remains NONE.
Does not equate digest equality with operational validity.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


class ContractError(Exception):
    pass


def _require_digest(value: Any, name: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ContractError(f"{name} must match ^sha256:[a-f0-9]{{64}}$")


def validate_material_change_invalidation(
    prior_evaluation: dict[str, Any],
    current_configuration_digest: str,
    current_dataset_digest: str,
    current_model_digest: str,
) -> dict[str, Any]:
    """Compare prior evaluation basis to current digests.

    On material change, prior evaluation is historical only and cannot establish current assurance.
    On no change, report NO CHANGE DETECTED. Do not claim current operational validity.
    """
    if not isinstance(prior_evaluation, dict):
        raise ContractError("prior_evaluation must be an object")

    required = {
        "evaluation_id", "subject_id", "dataset_id", "dataset_digest", "model_id", "model_digest",
        "configuration_digest", "context_boundary", "evaluation_outcome", "evidence_provenance",
        "invalidation_triggers", "reference_only", "authority_effect",
    }
    missing = required - set(prior_evaluation)
    if missing:
        raise ContractError(f"missing required evaluation basis fields: {', '.join(sorted(missing))}")
    if set(prior_evaluation) - required:
        raise ContractError("unsupported evaluation basis fields")

    if prior_evaluation.get("authority_effect") != "NONE":
        raise ContractError("authority_effect must be NONE")
    if prior_evaluation.get("reference_only") is not True:
        raise ContractError("must be reference_only")
    if not prior_evaluation.get("invalidation_triggers"):
        raise ContractError("invalidation_triggers required and nonempty")

    for field in ("dataset_digest", "model_digest", "configuration_digest"):
        _require_digest(prior_evaluation.get(field), field)
    _require_digest(current_configuration_digest, "current_configuration_digest")
    _require_digest(current_dataset_digest, "current_dataset_digest")
    _require_digest(current_model_digest, "current_model_digest")

    prov = prior_evaluation.get("evidence_provenance")
    if not isinstance(prov, dict) or not prov.get("source") or not prov.get("timestamp") or not DIGEST_RE.fullmatch(prov.get("digest", "")):
        raise ContractError("evidence_provenance incomplete or malformed")

    changed = (
        prior_evaluation["configuration_digest"] != current_configuration_digest
        or prior_evaluation["dataset_digest"] != current_dataset_digest
        or prior_evaluation["model_digest"] != current_model_digest
    )

    if changed:
        return {
            "status": "MATERIAL_CHANGE",
            "historical_record_valid": True,
            "current_assurance_from_prior": False,
            "requires_re_evaluation": True,
            "authority_effect": "NONE",
            "note": "Material dataset, model, or configuration change. Prior evaluation is historical only. Re-evaluation required before current assurance.",
        }

    return {
        "status": "NO_CHANGE_DETECTED",
        "historical_record_valid": True,
        "current_assurance_from_prior": False,
        "requires_re_evaluation": False,
        "authority_effect": "NONE",
        "note": "No material change detected against supplied digests. Does not establish current operational validity or authenticity.",
    }
