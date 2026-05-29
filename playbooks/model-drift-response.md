# Model Drift Response Playbook

## Detection

Monitor quality degradation, accuracy decline, changed refusal behavior, increased hallucination, changed tone, new unsafe outputs, or truth-verifiability degradation.

## Containment

- Pause or limit affected workflows.
- Compare current outputs with baseline tests.
- Preserve examples.

## Assessment

Determine whether drift came from model update, data change, prompt change, user shift, vendor update, or tool environment change.

## Correction

- Restore known-good version where possible.
- Update tests.
- Add monitoring thresholds.
- Reassess risk tier if capability changed.

## Reauthorization Trigger

Material drift in high-risk or frontier systems requires review before scaled use.
