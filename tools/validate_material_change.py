"""Material-change invalidation for evaluation basis records.

Loads and enforces the checked-in evaluation-basis schema.
Does not implement runtime monitoring. Returns non-authorizing result.
authority_effect remains NONE.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "evaluation-basis.schema.json"


class ContractError(Exception):
    pass


def _load_schema() -> dict[str, Any]:
    try:
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"evaluation-basis schema unavailable: {exc}") from exc


def _require_digest(value: Any, name: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ContractError(f"{name} must match ^sha256:[a-f0-9]{{64}}$")


def validate_material_change_invalidation(
    prior_evaluation: dict[str, Any],
    current_subject_id: str,
    current_dataset_id: str,
    current_model_id: str,
    current_context_boundary: str,
    current_configuration_digest: str,
    current_dataset_digest: str,
    current_model_digest: str,
) -> dict[str, Any]:
    """Compare prior evaluation basis to current identities and digests.

    On material change or identity mismatch, prior evaluation cannot establish current assurance.
    On no change, report NO_CHANGE_DETECTED. Do not claim operational validity.
    """
    if not isinstance(prior_evaluation, dict):
        raise ContractError("prior_evaluation must be an object")

    schema = _load_schema()
    required = set(schema.get("required", []))
    missing = required - set(prior_evaluation)
    if missing:
        raise ContractError(f"missing required evaluation basis fields: {', '.join(sorted(missing))}")
    if schema.get("additionalProperties") is False and set(prior_evaluation) - required:
        raise ContractError("unsupported evaluation basis fields")

    if prior_evaluation.get("authority_effect") != "NONE":
        raise ContractError("authority_effect must be NONE")
    if prior_evaluation.get("reference_only") is not True:
        raise ContractError("must be reference_only")
    triggers = prior_evaluation.get("invalidation_triggers")
    if not isinstance(triggers, list) or not triggers or not all(isinstance(t, str) and t for t in triggers):
        raise ContractError("invalidation_triggers must be a nonempty array of strings")

    for field in ("dataset_digest", "model_digest", "configuration_digest"):
        _require_digest(prior_evaluation.get(field), field)
    _require_digest(current_configuration_digest, "current_configuration_digest")
    _require_digest(current_dataset_digest, "current_dataset_digest")
    _require_digest(current_model_digest, "current_model_digest")

    prov = prior_evaluation.get("evidence_provenance")
    if not isinstance(prov, dict):
        raise ContractError("evidence_provenance must be an object")
    if set(prov) - {"source", "timestamp", "digest"}:
        raise ContractError("unsupported provenance fields")
    if not prov.get("source") or not prov.get("timestamp") or not DIGEST_RE.fullmatch(prov.get("digest", "")):
        raise ContractError("evidence_provenance incomplete or malformed")

    # Identity and context must match before digest comparison
    identity_mismatch = (
        prior_evaluation.get("subject_id") != current_subject_id
        or prior_evaluation.get("dataset_id") != current_dataset_id
        or prior_evaluation.get("model_id") != current_model_id
        or prior_evaluation.get("context_boundary") != current_context_boundary
    )
    if identity_mismatch:
        return {
            "status": "IDENTITY_MISMATCH",
            "historical_record_valid": True,
            "current_assurance_from_prior": False,
            "requires_re_evaluation": True,
            "authority_effect": "NONE",
            "note": "Subject, dataset, model, or context mismatch. Prior evaluation cannot establish current assurance.",
        }

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
        "note": "No material change detected against supplied identities and digests. Does not establish current operational validity or authenticity.",
    }
