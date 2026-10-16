#!/usr/bin/env python3
"""Validate foundational assurance-kernel records. Standard library only. Fail closed."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
SAMPLE_DIR = ROOT / "sample-data" / "assurance-kernel"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

FILES = (
    "evidence-object",
    "unknown-object",
    "context-boundary-record",
    "declared-state-snapshot",
    "observed-state-snapshot",
    "state-reconciliation-record",
    "dataset-assurance-record",
    "model-assurance-record",
    "evaluation-run",
    "drift-event",
    "qualification-evidence-record",
    "unresolved-decision-record",
    "protected-concern-disposition-record",
)


class ContractError(Exception):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _check(value: Any, schema: dict, label: str) -> None:
    if "const" in schema and value != schema["const"]:
        raise ContractError(f"{label} must equal {schema['const']}")
    expected = schema.get("type")
    if isinstance(expected, list):
        raise ContractError(f"{label} uses an unsupported type list")
    if expected == "object":
        _require(isinstance(value, dict), f"{label} must be an object")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(props)
            _require(not extra, f"{label} unsupported fields: {', '.join(sorted(extra))}")
        for key in schema.get("required", []):
            _require(key in value, f"{label} missing {key}")
        for key, item in value.items():
            if key in props:
                _check(item, props[key], f"{label}.{key}")
        return
    if expected == "array":
        _require(isinstance(value, list), f"{label} must be an array")
        minimum = schema.get("minItems", 0)
        _require(len(value) >= minimum, f"{label} must contain at least {minimum} items")
        for index, item in enumerate(value):
            _check(item, schema.get("items", {}), f"{label}[{index}]")
        return
    if expected == "string":
        _require(isinstance(value, str), f"{label} must be a string")
        if "minLength" in schema:
            _require(len(value.strip()) >= schema["minLength"], f"{label} must be a nonempty string")
        if "enum" in schema:
            _require(value in schema["enum"], f"{label} unsupported value")
        if "pattern" in schema:
            _require(re.fullmatch(schema["pattern"], value) is not None, f"{label} is malformed")
        return
    if expected == "boolean":
        _require(isinstance(value, bool), f"{label} must be a boolean")
        return
    if expected == "integer":
        _require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
        return
    raise ContractError(f"{label} has an unsupported schema type")


def _boundary(record: dict) -> None:
    _require(record.get("reference_only") is True, "reference_only must be true")
    _require(record.get("authority_effect") == "NONE", "authority_effect must be NONE")


def _semantic(name: str, record: dict) -> None:
    _boundary(record)
    if name == "unknown-object":
        if record["status"] == "RESOLVED":
            _require(record["resolution_evidence_refs"], "RESOLVED unknown requires resolution evidence")
        if record["blocking"] is True:
            _require(record["status"] == "OPEN", "blocking unknown must remain OPEN")
    elif name == "state-reconciliation-record":
        outcome = record["outcome"]
        state = record["reconciled_state"]
        if outcome == "UNKNOWN":
            _require(state != "MATCH", "UNKNOWN must not be promoted into MATCH")
            _require(state == "UNKNOWN", "UNKNOWN reconciliation must stay UNKNOWN")
        elif outcome == "DIVERGENCE":
            _require(record["reassessment_required"] is True, "divergence requires reassessment")
            _require(state == "DIVERGENCE", "divergence must not be recorded as MATCH")
        elif outcome == "MATCH":
            _require(state == "MATCH", "MATCH cannot carry another reconciled state")
            _require(record["reassessment_required"] is False, "MATCH does not require reassessment")
    elif name == "drift-event":
        if record["material"] is True:
            _require(record["reassessment_required"] is True, "material drift requires reassessment")
        _require("automatic_retrain" not in record, "drift record cannot retrain a model")
        _require("automatic_promotion" not in record, "drift record cannot promote a model")
    elif name == "qualification-evidence-record":
        _require(record.get("human_review_required") is True, "human_review_required must be true")
        # Strict interval. Inclusive endpoints are applied only when evaluation_time is supplied.
        _require(record["qualified_from"] < record["expires_at"], "qualified_from must be strictly before expires_at")
    elif name == "unresolved-decision-record":
        owner = record.get("owner_ref")
        _require(isinstance(owner, str) and owner.strip(), "owner_ref must be nonempty")
        evidence_needed = record.get("evidence_needed_refs")
        _require(isinstance(evidence_needed, list), "evidence_needed_refs must be an array")
        if len(evidence_needed) == 0:
            limitations = " ".join(record.get("limitations") or []).lower()
            _require(
                "no additional evidence is currently identified" in limitations,
                "empty evidence_needed_refs requires limitations to state that no additional evidence is currently identified",
            )
        if record["status"] in ("OPEN", "ESCALATED"):
            route = record.get("escalation_route_ref")
            _require(isinstance(route, str) and route.strip(), "OPEN or ESCALATED decision requires nonempty escalation_route_ref")
        if record["status"] == "RESOLVED":
            resolution = record.get("resolution_reference")
            _require(isinstance(resolution, str) and resolution.strip(), "RESOLVED requires resolution_reference")
        # ESCALATED is a distinct status and is never rewritten to RESOLVED.
        # Deadline silence is never rewritten to approval.
        _require(record.get("authority_effect") == "NONE", "authority_effect must be NONE")
    elif name == "protected-concern-disposition-record":
        if record["status"] == "ACTIVE":
            _require(record["assurance_effect"] in ("QUESTIONED", "STALE", "HOLD"), "ACTIVE concern effect bounded")
        if record["status"] == "CLOSED":
            _require(record.get("closure_evidence_refs"), "closure requires bounded evidence reference")
        if record["assurance_effect"] == "STALE":
            _require(record["revalidation_required"] is True, "STALE requires revalidation")
        if record["assurance_effect"] == "HOLD":
            # cannot become authorization; enforced by authority_effect NONE
            pass
        _require(record.get("human_review_required") is True, "human_review_required must be true")


def validate_record(name: str, record: dict[str, Any], evaluation_time: str | None = None) -> dict[str, Any]:
    _require(name in FILES, f"unsupported kernel record: {name}")
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    _check(record, schema, name)
    _semantic(name, record)
    # Deterministic evaluation for decision records.
    # Deadline endpoint is exclusive of expiry: evaluation_time > deadline is EXPIRED.
    effective_status = record.get("status")
    temporal_state = None
    can_satisfy_readiness = None
    if name == "unresolved-decision-record" and evaluation_time and record.get("status") == "OPEN":
        if evaluation_time > record["deadline"]:
            effective_status = "EXPIRED"
            if record.get("blocking") is True:
                raise ContractError("EXPIRED blocking decision cannot satisfy readiness")
    if name == "qualification-evidence-record":
        # Inclusive endpoints: CURRENT iff qualified_from <= evaluation_time <= expires_at.
        # Record validity is independent of whether the outcome can satisfy readiness.
        start = record["qualified_from"]
        end = record["expires_at"]
        if evaluation_time is None:
            temporal_state = "UNEVALUATED"
            can_satisfy_readiness = False
        elif evaluation_time < start:
            temporal_state = "NOT_YET_EFFECTIVE"
            can_satisfy_readiness = False
        elif evaluation_time > end:
            temporal_state = "EXPIRED"
            can_satisfy_readiness = False
        else:
            temporal_state = "CURRENT"
            can_satisfy_readiness = record.get("outcome") == "QUALIFIED"
    result = {
        "valid": True,
        "record": name,
        "reference_only": True,
        "authority_effect": "NONE",
        "note": "Reference record only. It does not establish truth, authenticity, operational readiness, certification, or authority.",
    }
    if temporal_state is not None:
        result["temporal_state"] = temporal_state
        result["can_satisfy_readiness"] = can_satisfy_readiness
        result["interval"] = "inclusive"
        result["note"] += " Qualification interval is inclusive at both endpoints. A future or expired qualification cannot satisfy readiness. CONDITIONAL and NOT_QUALIFIED do not satisfy readiness."
    if effective_status == "EXPIRED":
        result["effective_status"] = "EXPIRED"
        result["note"] += " OPEN past deadline treated as EXPIRED."
    return result


def validate_kernel_directory(directory: Path | None = None) -> None:
    directory = directory or SAMPLE_DIR
    for name in FILES:
        path = directory / f"{name}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        validate_record(name, record)


def main() -> None:
    validate_kernel_directory()
    print(json.dumps({"valid": True, "records": len(FILES), "authority_effect": "NONE"}, sort_keys=True))


if __name__ == "__main__":
    main()
