#!/usr/bin/env python3
"""Validate a succession evidence record. Standard library only. Fail closed."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "succession-evidence-record.schema.json"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
SUCCESS_FLAGS = (
    "configuration_restored",
    "evaluation_reproduced",
    "fallback_demonstrated",
    "recovery_demonstrated",
    "authority_boundary_explained",
    "capability_resumed",
)


class ContractError(Exception):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_succession_evidence(record: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    _require(isinstance(record, dict), "record must be an object")
    required = set(schema["required"])
    missing = required - set(record)
    _require(not missing, f"missing required fields: {', '.join(sorted(missing))}")
    extra = set(record) - set(schema["properties"])
    _require(not extra, f"unsupported fields: {', '.join(sorted(extra))}")
    _require(record.get("schema_version") == "1.0.0", "schema_version mismatch")
    _require(record.get("reference_only") is True, "reference_only must be true")
    _require(record.get("human_review_required") is True, "human_review_required must be true")
    _require(record.get("authority_effect") == "NONE", "authority_effect must be NONE")
    _require(record.get("outcome") in {"SUCCESS", "PARTIAL", "FAILED"}, "unsupported outcome")
    _require(DIGEST.fullmatch(str(record.get("configuration_digest", ""))), "configuration_digest malformed")
    artifacts = record.get("handoff_artifacts")
    _require(isinstance(artifacts, list) and artifacts, "handoff_artifacts must be a nonempty array")
    for item in artifacts:
        _require(isinstance(item, dict), "handoff artifact must be an object")
        _require(set(item) == {"reference", "digest"}, "unsupported handoff artifact fields")
        _require(isinstance(item.get("reference"), str) and item["reference"].strip(), "handoff reference missing")
        _require(DIGEST.fullmatch(str(item.get("digest", ""))), "handoff digest malformed")
    dependencies = record.get("undocumented_dependencies_found")
    _require(isinstance(dependencies, list), "undocumented_dependencies_found must be an array")
    if record["outcome"] == "SUCCESS":
        for flag in SUCCESS_FLAGS:
            _require(record.get(flag) is True, f"SUCCESS requires {flag}")
        _require(record.get("creator_assistance_required") is False, "SUCCESS cannot require creator assistance")
        _require(dependencies == [], "SUCCESS cannot retain undocumented dependencies")
        _require(isinstance(record.get("support_owner"), str) and record["support_owner"].strip(), "support_owner required")
        _require(isinstance(record.get("support_commitment_ref"), str) and record["support_commitment_ref"].strip(), "support_commitment_ref required")
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
