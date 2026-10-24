# Changelog

## Unreleased

## v1.1.1 — Resolvable Schema Identifiers

- The `portfolio-handoff-reference` schema `$id` uses the release-pinned form `https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/ai-governance-os/v1.1.1/schemas/portfolio-handoff-reference.schema.json`, which returns the exact schema published in this release. The earlier identifier named a `github.com` path that did not resolve. Schema content is unchanged; only the `$id` differs.
- CI checks that every absolute schema `$id` names the file's own path at a release listed in this changelog. The Release Assets workflow fetches every such `$id` from the tag and requires the identical document before it attaches assets.
- Add reference-only Qualification Evidence Record, Unresolved Decision Record, and Protected Concern Disposition Record schemas, synthetic fixtures, and fail-closed validation.
- Qualification interval endpoints are inclusive. A record remains valid when future or expired; only a current QUALIFIED outcome can satisfy readiness.
- Unresolved decisions require an owner, an evidence-needed array, and an escalation route while OPEN or ESCALATED. Silence is not approval.

## v1.1 — AI Governance OS

- Published deployable AI Governance OS structure.
- Added doctrine, schemas, registers, reports, playbooks, templates, and sample data.
- Added truth and verifiability field: `strategic_knowledge_impact_note`.
- Added community governance files.
- Added roadmap and flagship repository cross-link.

## v1.0 — Foundation

- Established the core governance doctrine.
- Defined the master governance formula.
- Defined minimum rules for ownership, inventory, evidence, shutdown, and reauthorization.
