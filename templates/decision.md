---
id: {{ID}}
parent: {{PARENT}}
title: {{TITLE}}
level: {{LEVEL}}
kind: decision
date: {{DATE}}
deciders: [{{DECIDERS}}]
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
keywords: [{{KEYWORDS}}]
references: [{{REFERENCES}}]
affects: [{{AFFECTS}}]
---

# {{TITLE}}

## Context
{{CONTEXT}}

## Decision
{{DECISION}}

## Consequences
{{CONSEQUENCES}}

## Alternatives Considered
{{ALTERNATIVES}}

<!--
Decision template rules (do not emit in generated files):

- A decision overrides parent docs within its scope (rules/precedence.md).
- Carry `domains`, `flows`, `keywords` so the decision is discoverable during impact analysis.
- `affects` records docs whose behavior the decision changes.
- MUST NOT author reverse edges.
-->