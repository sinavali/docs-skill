---
id: {{ID}}
parent: {{PARENT}}
title: {{TITLE}}
level: {{LEVEL}}
kind: contract
parties: [{{PARTIES}}]
domains: [{{DOMAINS}}]
flows: [{{FLOWS}}]
keywords: [{{KEYWORDS}}]
implements: [{{FLOW_IDS}}]
references: [{{REFERENCES}}]
affects: [{{AFFECTS}}]
code_paths: [{{CODE_PATHS}}]
test_paths: [{{TEST_PATHS}}]
---

# {{TITLE}}

## Endpoints

| Method | Path | Request | Response |
|---|---|---|---|
{{ENDPOINT_ROWS}}

## Schemas

{{SCHEMAS}}

## Compatibility
- Additive changes only in minor revisions.
- Breaking changes require a new contract version and a decision doc.

## Change Policy
Changes to this contract MUST originate at the level at which it lives.

<!--
Contract template rules (do not emit in generated files):

- A contract MUST carry `code_paths` and `test_paths` when it governs code.
- `domains`, `flows`, and `keywords` drive impact discovery. Without them the
  contract cannot be found as a seed.
- `implements` links the contract to the flow(s) it realizes.
- `affects` records downstream docs whose behavior a contract change may change.
- MUST NOT author reverse edges (affected_by / referenced_by / implemented_by).
- See rules/frontmatter.md, rules/relationships.md, rules/impact.md.
-->