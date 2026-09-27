# Change Surface

## Request
{{REQUEST}}

## Seeds
- {{SEED_ID}}

## Documentation inspected
- {{DOC_ID}}: {{WHY}}

## Related documentation identified
- {{DOC_ID}}: {{EDGE_TYPE}}

## Code surface
- {{CODE_PATH}}

## Test surface
- {{TEST_PATH}}

## Related flows
- {{FLOW_ID}}

## Explicitly checked and unaffected
- {{ID}}: {{WHY_RULED_OUT}}

## Risks
- {{RISK}}

## Open questions
- {{QUESTION}}

## Status
{{STATUS}}

<!--
Change Surface rules (do not emit in generated files):

- Produced BEFORE non-trivial implementation. See rules/impact.md.
- Status is READY_FOR_IMPLEMENTATION or NEEDS_CLARIFICATION.
- "Explicitly checked and unaffected" is mandatory. It is negative scope.
- The coder starts from this artifact, not from the raw request.
- The reviewer verifies coverage against it and may mark it incomplete.
-->