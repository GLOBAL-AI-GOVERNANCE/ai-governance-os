# Portfolio Interoperability

AI Governance Foundations supplies reusable structures. It does not own specialist repository semantics and does not become a portfolio runtime.

The `portfolio-handoff-reference` schema defines a generic **reference envelope** for connecting independently governed artifacts.

It deliberately carries references rather than embedding another repository's schema.

## Design rules

- `reference_only` is always `true`.
- `authority_effect` is always `NONE`.
- source and target repositories remain explicit;
- source artifact identity and version remain explicit;
- configuration, evidence, and authority references remain optional references;
- unsupported semantics must be rejected by the receiving repository; and
- the envelope does not approve, certify, authorize, close, or prove a control.

The synthetic sample in `sample-data/portfolio-handoff-reference.json` is illustrative only.

## Assurance Context Binding

The `assurance-context-binding` schema provides a reference-only binding of subject, configuration digest, context boundary, and evidence provenance.

It records material-change invalidation triggers. It does not implement runtime change detection or automatic revocation. `authority_effect` remains `NONE`.

The synthetic fixture in `sample-data/assurance-context-binding.json` uses deterministic SHA-256 digests of documented synthetic bytes. Hash values do not establish authenticity of any external system. The fixture is illustrative only and does not establish operational readiness.

## Succession Evidence Record

The `succession-evidence-record` schema is a foundational reference record for a bounded capability-transfer exercise. It is owned by AI Governance Foundations. JSON Schema validates structure. `tools/validate_succession_evidence.py` enforces semantic outcome constraints, so a structurally valid record is not a SUCCESS by itself. A declared SUCCESS is accepted only when restoration, reproduction, fallback, recovery, authority-boundary explanation, resumption, support ownership, and the absence of creator dependence and undocumented dependencies are all recorded. The record remains `reference_only: true`, `human_review_required: true`, and `authority_effect: NONE`. It does not authorize use, certify a team, or establish operational readiness. The synthetic FAILED fixture is `sample-data/succession-evidence-failed.json`.

## Assurance kernel

Foundations also defines reference-only records for evidence, unknowns, context boundaries, declared and observed state, reconciliation, dataset and model assurance, evaluation runs, and drift events.

Evidence class does not imply truth. An unknown stays visible while it is blocking. Observation does not overwrite a declaration, and UNKNOWN is not MATCH. Material drift requires reassessment and does not retrain or promote a model. Context boundary records are technical metadata, not legal ownership. `authority_effect` remains `NONE`.

Synthetic fixtures under `sample-data/assurance-kernel/` are illustrative only.

