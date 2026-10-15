#!/usr/bin/env python3
"""Validate public positioning and repository artifact integrity."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INTEROP_SCHEMA = ROOT / "schemas" / "portfolio-handoff-reference.schema.json"
INTEROP_EXAMPLE = ROOT / "sample-data" / "portfolio-handoff-reference.json"
BINDING_SCHEMA = ROOT / "schemas" / "assurance-context-binding.schema.json"
BINDING_EXAMPLE = ROOT / "sample-data" / "assurance-context-binding.json"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
SECURITY = ROOT / "SECURITY.md"

REQUIRED_HEADINGS = (
    "# AI Governance Foundations",
    "## Start Here",
    "## Repository Role",
    "## Core Doctrine",
    "## Governance Formula",
    "## Minimum Rules",
    "## Repository Map",
    "## Version Lineage",
    "## What This Repository Is",
    "## What This Repository Is Not",
    "## Evidence Boundary",
)

REQUIRED_PHRASES = (
    "Global AI Governance Toolkit",
    "AI Governance Decision Pack",
    "Foundational public reference repository",
    "It is not the current operational flagship.",
    "does not independently approve deployment",
    "Humans retain authority",
    "not prove that an organization implemented them",
    "current authoritative sources",
    "https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit",
    "current tagged release:",
)

FORBIDDEN_PHRASES = (
    "global-ai-governance-toolkit/tree/v2.1.0",
    "global-ai-governance-solutions",
    "deployable governance system",
    "Flagship repository:",
)

MARKDOWN_LINK = re.compile(
    r"!?\[[^\]]*\]\((?P<destination>[^)\n]+)\)"
)
FENCED_CODE = re.compile(
    r"```.*?```|~~~.*?~~~",
    re.DOTALL,
)
SHA256_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")


def fail(message: str) -> None:
    raise SystemExit(f"Foundations validation failed: {message}")


def repository_files() -> list[Path]:
    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        ROOT / item.decode("utf-8")
        for item in completed.stdout.split(b"\0")
        if item
    ]


def validate_readme(text: str) -> None:
    heading_lines = [
        line.strip()
        for line in text.splitlines()
        if line.lstrip().startswith("#")
    ]

    for heading in REQUIRED_HEADINGS:
        if heading_lines.count(heading) != 1:
            fail(f"heading must appear exactly once: {heading}")

    lowered = text.lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            fail(f"required positioning is missing: {phrase}")

    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lowered:
            fail(f"stale or overbroad claim remains: {phrase}")

    if "\t" in text:
        fail("README contains tab characters.")

    for number, line in enumerate(text.splitlines(), start=1):
        if line.rstrip() != line:
            fail(f"README has trailing whitespace on line {number}")


def validate_public_terminology() -> None:
    contributing = CONTRIBUTING.read_text(encoding="utf-8-sig")
    security = SECURITY.read_text(encoding="utf-8-sig")
    if "contributing to AI Governance Foundations" not in contributing:
        fail("CONTRIBUTING does not use the current Foundations identity")
    for phrase in (
        "historical AI Governance OS v1.1 release and provenance",
        "historical public release remains AI Governance OS v1.1",
        "does not relabel or reissue that release",
    ):
        if phrase not in contributing + security:
            fail(f"v1.1 provenance boundary is missing: {phrase}")


def validate_json(files: list[Path]) -> None:
    for path in files:
        if path.suffix.lower() != ".json":
            continue
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            fail(
                "invalid JSON in "
                f"{path.relative_to(ROOT)}: {exc}"
            )


def extract_destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1:value.index(">")].strip()
    return value.split()[0].strip() if value else ""


def validate_markdown_links(files: list[Path]) -> None:
    for markdown in files:
        if markdown.suffix.lower() != ".md":
            continue

        text = markdown.read_text(encoding="utf-8-sig")
        text = FENCED_CODE.sub("", text)

        for match in MARKDOWN_LINK.finditer(text):
            destination = extract_destination(
                match.group("destination")
            )
            lower = destination.lower()

            if (
                not destination
                or destination.startswith("#")
                or lower.startswith(
                    (
                        "http://",
                        "https://",
                        "mailto:",
                        "tel:",
                        "data:",
                    )
                )
            ):
                continue

            path_part = unquote(urlsplit(destination).path)
            if not path_part:
                continue

            target = (
                ROOT / path_part.lstrip("/")
                if path_part.startswith("/")
                else markdown.parent / path_part
            )

            if not target.exists():
                fail(
                    "broken local Markdown link in "
                    f"{markdown.relative_to(ROOT)}: "
                    f"{destination}"
                )


def validate_portfolio_handoff() -> None:
    schema = json.loads(INTEROP_SCHEMA.read_text(encoding="utf-8"))
    example = json.loads(INTEROP_EXAMPLE.read_text(encoding="utf-8"))

    if schema.get("properties", {}).get("reference_only", {}).get("const") is not True:
        fail("portfolio handoff schema must remain reference-only")
    if schema.get("properties", {}).get("authority_effect", {}).get("const") != "NONE":
        fail("portfolio handoff schema must have no authority effect")

    required = set(schema.get("required", []))
    if not required.issubset(example):
        fail("portfolio handoff example is missing required fields")
    if not set(example).issubset(schema.get("properties", {})):
        fail("portfolio handoff example contains unsupported fields")
    if example.get("reference_only") is not True or example.get("authority_effect") != "NONE":
        fail("portfolio handoff example exceeds its reference-only boundary")


def validate_assurance_context_binding() -> None:
    schema = json.loads(BINDING_SCHEMA.read_text(encoding="utf-8"))
    example = json.loads(BINDING_EXAMPLE.read_text(encoding="utf-8"))

    if schema.get("properties", {}).get("reference_only", {}).get("const") is not True:
        fail("assurance context binding schema must remain reference-only")
    if schema.get("properties", {}).get("authority_effect", {}).get("const") != "NONE":
        fail("assurance context binding schema must have no authority effect")

    required = set(schema.get("required", []))
    if not required.issubset(example):
        fail("assurance context binding example is missing required fields")
    if not set(example).issubset(schema.get("properties", {})):
        fail("assurance context binding example contains unsupported fields")
    if example.get("reference_only") is not True or example.get("authority_effect") != "NONE":
        fail("assurance context binding example exceeds its reference-only boundary")

    if not SHA256_PATTERN.match(example.get("configuration_digest", "")):
        fail("assurance context binding configuration_digest is not a valid sha256")
    prov = example.get("evidence_provenance", {})
    if not isinstance(prov, dict):
        fail("assurance context binding evidence_provenance must be an object")
    if not SHA256_PATTERN.match(prov.get("digest", "")):
        fail("assurance context binding evidence digest is not a valid sha256")
    if not prov.get("source") or not prov.get("timestamp"):
        fail("assurance context binding evidence provenance is incomplete")
    triggers = example.get("invalidation_triggers", [])
    if not isinstance(triggers, list) or len(triggers) < 1:
        fail("assurance context binding must have nonempty invalidation triggers")
    if not example.get("context_boundary") or not example.get("validity_from"):
        fail("assurance context binding missing context boundary or validity start")

    # Negative path checks (in-memory mutations of a copy)
    bad = dict(example)
    bad["authority_effect"] = "AUTHORIZE"
    if bad.get("authority_effect") == "NONE":
        fail("negative test failed: non-NONE authority should be detectable")
    bad = dict(example)
    bad["reference_only"] = False
    if bad.get("reference_only") is True:
        fail("negative test failed: non-true reference_only should be detectable")
    bad = dict(example)
    bad["invalidation_triggers"] = []
    if len(bad.get("invalidation_triggers", [])) > 0:
        fail("negative test failed: empty triggers should be detectable")
    bad = dict(example)
    bad["configuration_digest"] = "not-a-digest"
    if SHA256_PATTERN.match(bad["configuration_digest"]):
        fail("negative test failed: malformed digest should be detectable")


def validate_hygiene(files: list[Path]) -> None:
    for path in files:
        relative = path.relative_to(ROOT)
        if "__pycache__" in relative.parts:
            fail(f"tracked Python cache directory: {relative}")
        if path.suffix.lower() in {".pyc", ".pyo"}:
            fail(f"tracked Python bytecode: {relative}")


def main() -> None:
    if not README.is_file():
        fail("README.md is missing.")

    files = repository_files()
    text = README.read_text(encoding="utf-8-sig")

    validate_readme(text)
    validate_public_terminology()
    validate_json(files)
    validate_markdown_links(files)
    validate_portfolio_handoff()
    validate_assurance_context_binding()
    validate_hygiene(files)

    print(
        "Foundations validation passed: "
        f"{len(files)} repository files checked; "
        "positioning, JSON, links, handoff, assurance binding, and hygiene verified."
    )


if __name__ == "__main__":
    main()
