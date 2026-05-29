# Prompt Injection Response Playbook

## Detection

Look for system behavior caused by untrusted text inside emails, PDFs, webpages, code comments, tickets, or documents.

## Containment

- Pause affected workflow.
- Disable external action permissions.
- Preserve the malicious input.
- Preserve prompts, outputs, and tool logs.

## Assessment

Determine whether the system leaked data, changed decisions, executed tools, sent messages, modified records, or influenced procurement or security decisions.

## Correction

- Add untrusted-content isolation.
- Add source hierarchy.
- Require human approval for high-impact actions.
- Add adversarial document screening.
- Retest before reauthorization.

## Reauthorization Trigger

Any successful prompt injection in a high-risk or frontier system reopens review.
