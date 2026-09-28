---
id: {{ID}}
parent: {{PARENT}}
title: {{TITLE}}
level: {{LEVEL}}
kind: operational
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
keywords: [{{KEYWORDS}}]
code_paths: [{{CODE_PATHS}}]
test_paths: [{{TEST_PATHS}}]
---

# {{TITLE}}

## Symptoms
{{SYMPTOMS}}

## Steps
{{STEPS}}

## Rollback
{{ROLLBACK}}

## Escalation
{{ESCALATION}}

<!--
Runbook template rules (do not emit in generated files):

- Carry `domains`, `flows`, `keywords` so the runbook is discoverable.
- When it references code, carry `code_paths`.
- MUST NOT author reverse edges.
-->