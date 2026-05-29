# Unsafe Agent Response Playbook

## Detection

Identify unauthorized tool use, unapproved external actions, unexpected planning, hidden action chains, or attempts to bypass limits.

## Containment

- Revoke credentials.
- Disable external tools.
- Isolate affected environment.
- Preserve tool-call logs.

## Assessment

Compare intended actions to actual actions. Identify affected systems, credentials, documents, messages, code, payments, or decisions.

## Correction

- Apply least privilege.
- Add human approval gates.
- Restrict long-horizon planning.
- Test shutdown path.
- Rerun frontier gates.

## Reauthorization Trigger

Any unauthorized tool use by a frontier agent automatically reopens all frontier gates.
