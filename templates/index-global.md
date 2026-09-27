---
id: {{ID}}
title: Documentation Map
level: {{LEVEL}}
kind: blueprint
---

# Documentation Map

Routing only. Which domains exist, which flows exist, and which domains each flow spans.
This file stays tiny. It is the first thing an orchestrator reads.

## Domains

{{DOMAINS}}

## Flows

{{FLOWS}}

## Cross-domain flows

{{FLOW_PARTICIPATION}}

<!--
Global map rules (do not emit in generated files):

- Domains and flows are names only, never content.
- Cross-domain flow participation is derived from doc frontmatter (`implements`, `domains`).
- MUST stay tiny. If it grows, the domains/flows are wrong, not the file.
- See rules/index-format.md.
-->