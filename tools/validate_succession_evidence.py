#!/usr/bin/env python3
"""Validate a succession evidence record against its schema. Standard library only. Fail closed."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "succession-evidence-record.schema.json"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SUCCESS_FLAGS = (
    "configuration_restored",
    "evaluation_reproduced",
    "fallback_demonstrated",
    "recovery_demonstrated",
    "authority_boundary_explained",
    "capability_resumed",
)
BOOLEAN_FLAGS = SUCCESS_FLAGS + ("creator_assistance_required",)


class ContractError(Exception):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _nonempty_string(value: Any, label: str) -> None:
    _require(isinstance(value, str) and value.strip(), f"{label} must be a nonempty string")


def _string_array(value: Any, label: str, nonempty: bool) -> None:
    _require(isinstance(value, list), f"{label} must be an array")
    if nonempty:
        _require(bool(value), f"{label} must be nonempty")
    for item in value:
        _require(isinstance(item, str) and item.strip(), f"{label} must contain nonempty strings")


def validate_succession_evidence(record: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    _require(isinstance(record, dict), "record must be an object")
    required = set(schema["required"])
    missing = required - set(record)
    _require(not missing, f"missing required fields: {', '.join(sorted(missing))}")
    extra = set(record) - set(schema["properties"])
    _require(not extra, f"unsupported fields: {', '.join(sorted(extra))}")
    _require(record.get("schema_version") == "1.0.0", "schema_version mismatch")
    _nonempty_string(record.get("record_id"), "record_id")
    _nonempty_string(record.get("subject_id"), "subject_id")
    _require(DIGEST.fullmatch(str(record.get("configuration_digest", ""))), "configuration_digest malformed")
    _nonempty_string(record.get("environment_boundary"), "environment_boundary")
    _require(TIMESTAMP.fullmatch(str(record.get("evaluated_at", ""))), "evaluated_at must use YYYY-MM-DDTHH:MM:SSZ")
    _nonempty_string(record.get("successor_team_ref"), "successor_team_ref")
    artifacts = record.get("handoff_artifacts")
    _require(isinstance(artifacts, list) and artifacts, "handoff_artifacts must be a nonempty array")
    for item in artifacts:
        _require(isinstance(item, dict), "handoff artifact must be an object")
        _require(set(item) == {"reference", "digest"}, "unsupported handoff artifact fields")
        _nonempty_string(item.get("reference"), "handoff reference")
        _require(DIGEST.fullmatch(str(item.get("digest", ""))), "handoff digest malformed")
    for flag in BOOLEAN_FLAGS:
        _require(isinstance(record.get(flag), bool), f"{flag} must be a boolean")
    dependencies = record.get("undocumented_dependencies_found")
    _string_array(dependencies, "undocumented_dependencies_found", nonempty=False)
    _require(isinstance(record.get("support_owner"), str), "support_owner must be a string")
    _require(isinstance(record.get("support_commitment_ref"), str), "support_commitment_ref must be a string")
    _string_array(record.get("limitations"), "limitations", nonempty=True)
    _require(record.get("outcome") in {"SUCCESS", "PARTIAL", "FAILED"}, "unsupported outcome")
    _require(record.get("reference_only") is True, "reference_only must be true")
    _require(record.get("human_review_required") is True, "human_review_required must be true")
    _require(record.get("authority_effect") == "NONE", "authority_effect must be NONE")
    if record["outcome"] == "SUCCESS":
        for flag in SUCCESS_FLAGS:
            _require(record.get(flag) is True, f"SUCCESS requires {flag}")
        _require(record.get("creator_assistance_required") is False, "SUCCESS cannot require creator assistance")
        _require(dependencies == [], "SUCCESS cannot retain undocumented dependencies")
        _nonempty_string(record.get("support_owner"), "support_owner")
        _nonempty_string(record.get("support_commitment_ref"), "support_commitment_ref")
    return {
        "valid": True,
        "outcome": record["outcome"],
        "reference_only": True,
        "authority_effect": "NONE",
        "note": "Bounded transfer-exercise record only. Does not prove mission readiness, legal authority, production fitness, certification, or general organizational resilience.",
    }


def main() -> None:
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "sample-data" / "succession-evidence-record.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(validate_succession_evidence(record), sort_keys=True))


if __name__ == "__main__":
    main()
