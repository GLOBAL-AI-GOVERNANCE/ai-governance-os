"""Minimal material-change invalidation check for evaluation bindings.

Does not implement runtime monitoring. Accepts explicitly supplied prior binding and current configuration.
Returns non-authorizing result. authority_effect remains NONE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ContractError(Exception):
    pass


def validate_material_change_invalidation(
    prior_binding: dict[str, Any],
    current_configuration_digest: str,
    current_dataset_digest: str | None = None,
) -> dict[str, Any]:
    """Reject silent acceptance of prior evaluation when configuration or dataset digest changes.

    Historical record remains valid as history. Current assurance requires re-evaluation.
    """
    if not isinstance(prior_binding, dict):
        raise ContractError("prior_binding must be an object")
    if prior_binding.get("authority_effect") != "NONE":
        raise ContractError("prior_binding authority_effect must be NONE")
    if prior_binding.get("reference_only") is not True:
        raise ContractError("prior_binding must be reference_only")
    if not prior_binding.get("invalidation_triggers"):
        raise ContractError("invalidation_triggers required")

    prior_config = prior_binding.get("configuration_digest")
    if not isinstance(prior_config, str) or not prior_config.startswith("sha256:"):
        raise ContractError("prior configuration_digest malformed")
    if not isinstance(current_configuration_digest, str) or not current_configuration_digest.startswith("sha256:"):
        raise ContractError("current_configuration_digest malformed")

    material_change = prior_config != current_configuration_digest
    if current_dataset_digest is not None and current_dataset_digest != prior_binding.get("dataset_digest"):
        material_change = True

    if material_change:
        return {
            "current_assurance_valid": False,
            "historical_record_valid": True,
            "requires_re_evaluation": True,
            "authority_effect": "NONE",
            "note": "Material configuration or dataset change. Prior evaluation is historical only. Re-evaluation or human reauthorization required before current assurance.",
        }

    return {
        "current_assurance_valid": True,
        "historical_record_valid": True,
        "requires_re_evaluation": False,
        "authority_effect": "NONE",
        "note": "No material configuration or dataset change detected against supplied values. Does not establish operational validity.",
    }
