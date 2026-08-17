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
