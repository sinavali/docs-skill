---
id: {{ID}}
parent: {{PARENT}}
title: {{TITLE}}
level: {{LEVEL}}
kind: cross-cutting
applies_to: [{{APPLIES_TO}}]
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
keywords: [{{KEYWORDS}}]
references: [{{REFERENCES}}]
affects: [{{AFFECTS}}]
code_paths: [{{CODE_PATHS}}]
test_paths: [{{TEST_PATHS}}]
---

# {{TITLE}}

## Threats / Concerns
{{THREATS}}

## MUST
{{RULES}}

## Validation
{{VALIDATION}}

## Exceptions
Any exception MUST be recorded in a decision doc.

<!--
Cross-cutting template rules (do not emit in generated files):

- `applies_to` lists the scopes this rule constrains.
- Carry `domains`, `flows`, `keywords` so the rule is discoverable.
- When the rule constrains code, carry `code_paths` and `test_paths`.
- MUST NOT author reverse edges.
-->