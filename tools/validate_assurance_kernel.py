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


def validate_record(name: str, record: dict[str, Any]) -> dict[str, Any]:
    _require(name in FILES, f"unsupported kernel record: {name}")
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    _check(record, schema, name)
    _semantic(name, record)
    return {
        "valid": True,
        "record": name,
        "reference_only": True,
        "authority_effect": "NONE",
        "note": "Reference record only. It does not establish truth, authenticity, operational readiness, certification, or authority.",
    }


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
