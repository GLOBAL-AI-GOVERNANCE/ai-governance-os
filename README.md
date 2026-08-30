# AI Governance Foundations

**Foundational governance models, schemas, registers, templates, and playbooks for accountable AI oversight.**

**Status:** Foundational public reference repository. The existing `v1.1` release remains part of this repository's historical lineage.

This repository preserves reusable governance foundations for making AI systems visible, owned, risk-tiered, reviewed, monitored, and controllable.

It is not the current operational flagship.

## Start Here

For the current released end-to-end workflow, begin with the [Global AI Governance Toolkit](https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit) (current tagged release: `v2.3.0`).

The toolkit converts an authorized AI system inventory record into schema validation, preliminary risk classification, policy-driven findings, an executive governance report, and a reproducible AI Governance Decision Pack for human review and decision.

Use this foundations repository when you need reusable doctrine, data structures, registers, templates, playbooks, and reporting patterns that can support or extend that workflow.

## Repository Role

```text
AI Governance Foundations
→ doctrine and operating principles
→ schemas and registers
→ templates and playbooks
→ reporting structures
→ supporting inputs for governed workflows
```

This repository does not replace the toolkit runtime and does not independently approve deployment.

## Core Doctrine

Low-risk AI should move fast.

High-impact AI should move carefully.

Frontier AI should move only through gates.

Unowned AI should not move at all.

## Governance Formula

```text
Issue
→ Evidence
→ Risk
→ Control
→ Owner
→ Trigger
→ Audit
→ Consequence
```

## Minimum Rules

- No owner, no deployment.
- No inventory, no governance.
- No evidence, no approval.
- No shutdown path, no frontier release.
- No major capability jump without reauthorization.
- AI may assist. Humans retain authority.

## Repository Map

- [`doctrine/`](doctrine/): policy and operating principles
- [`schemas/`](schemas/): JSON structures for governance data
- [`registers/`](registers/): CSV structures for inventories and governance records
- [`templates/`](templates/): reusable governance work products
- [`playbooks/`](playbooks/): incident and capability-change response guidance
- [`sample-data/`](sample-data/): illustrative enterprise research and development data
- [`reports/`](reports/): board, regulator, and post-incident reporting templates
- [`source-lock.md`](source-lock.md): dated source notes that require current-source revalidation before consequential use

## Version Lineage

The `v1.1` release added the field:

```text
strategic_knowledge_impact_note
```

Its purpose is to record whether an AI system may improve, degrade, or obscure verifiable understanding.

Preserving this release history does not mean every artifact is a deployed control or current legal determination.

## What This Repository Is

- A foundational governance model
- A reusable template and schema collection
- A historical and conceptual predecessor to the current toolkit workflow
- A source of governance patterns for authorized implementation
- A public reference for accountable human decision-making

## What This Repository Is Not

- A production AI governance platform
- A deployed policy engine
- A monitoring or enforcement service
- A certification or proof of compliance
- A legal or regulatory opinion
- A deployment authorization
- A substitute for security, privacy, legal, compliance, procurement, executive, or board review

## Evidence Boundary

Schemas, registers, templates, and playbooks define structures and recommended practices. Their presence does not prove that an organization implemented them, supplied accurate evidence, operated controls effectively, or satisfied a legal or regulatory obligation.

Dated source notes may become stale. Verify controlling laws, standards, policies, and institutional requirements against current authoritative sources before consequential use.

**Use foundations to structure the work. Use the toolkit to produce the decision-ready outcome. Keep final authority human-owned.**
