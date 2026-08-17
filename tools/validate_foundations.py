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
)

FORBIDDEN_PHRASES = (
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
    validate_json(files)
    validate_markdown_links(files)
    validate_portfolio_handoff()
    validate_hygiene(files)

    print(
        "Foundations validation passed: "
        f"{len(files)} repository files checked; "
        "positioning, JSON, links, and hygiene verified."
    )


if __name__ == "__main__":
    main()
