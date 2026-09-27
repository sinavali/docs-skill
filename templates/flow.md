---
id: {{ID}}
title: {{TITLE}}
level: {{LEVEL}}
kind: contract
domains: [{{DOMAINS}}]
flows: [{{FLOW}}]
keywords: [{{KEYWORDS}}]
implements: [{{FLOW_ID}}]
code_paths: [{{CODE_PATHS}}]
test_paths: [{{TEST_PATHS}}]
---

# {{TITLE}}

## Purpose
What this flow accomplishes, in one paragraph.

## Participants
Domains that take part. Names only; behavior lives in the domain docs.

## Steps
1. {{STEP_1}}
2. {{STEP_2}}

## Domain References
- {{DOMAIN_DOC_ID}}: {{WHY}}

## Failure Modes
{{FAILURES}}

## Change Entry Point
This doc is the entry point for any change that touches this flow. Start impact
discovery here.

<!--
Flow doc rules (do not emit in generated files):

- A flow doc is a CHANGE ENTRY POINT, not a copy of domain rules.
- MUST NOT duplicate domain content. Reference domain docs by ID instead.
- A flow crosses domains. It records participation, not behavior.
- Section it per rules/sectioning.md when it grows.
- See rules/index-format.md and rules/relationships.md.
-->