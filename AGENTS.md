# AGENTS.md

Instructions for coding agents working in this repository.

## Setup and checks

```bash
python3 -B tools/validate_foundations.py
python3 -B tools/check_schema_ids.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

## Rules

- Foundations supply doctrine, schemas, registers, templates, and playbooks. They do not replace the toolkit runtime and do not authorize deployment.
- Every public result keeps `authority_effect: "NONE"`. Do not add a path that approves, certifies, or authorizes.
- Prefer squash-merge through green CI. Do not force-push `main`.

## Setup guide

End-to-end local setup for the toolkit and MCP: [AGENT_SETUP](https://ai-governance.solutions/AGENT_SETUP.html).
