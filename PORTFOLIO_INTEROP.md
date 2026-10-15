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
