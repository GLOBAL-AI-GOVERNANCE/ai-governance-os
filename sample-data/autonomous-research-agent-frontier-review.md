# Frontier Gate Review: Autonomous Research Agent

System ID: AI-005
System Name: Autonomous Research Agent
Owner: R&D Director
Current Status: Testing
Decision: Delay pending evidence

## Gate Findings

| Gate | Finding | Status |
|---|---|---|
| Capability Forecasting | Agent may plan research, summarize technical literature, generate hypotheses, and recommend next steps | Amber |
| Truth and Verifiability | Unknown. May improve synthesis, but may also overstate weak evidence | Amber |
| Access Control | Read-only access approved. No write, purchase, email-send, or code execution permissions | Green |
| Independent Red Teaming | Not complete | Red |
| Staged Deployment | Lab testing only | Green |
| Live Monitoring | Prompt logs and tool calls captured | Green |
| Incident Response | Shutdown path exists, but has not been tested | Amber |
| Reauthorization | Required after model update, new tool access, or serious incident | Green |

## Verdict

Do not scale yet. Complete independent red-team testing, truth-verifiability testing, prompt-injection testing, and shutdown-path exercise first.
