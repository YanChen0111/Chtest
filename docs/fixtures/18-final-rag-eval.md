# Final RAG Acceptance Fixture

This fixture is intentionally provider-neutral. It evaluates the evidence
contract rather than a provider's private payload:

- query: `expired coupon checkout`
- required cards: `coupon-api-notes`, `coupon-checkout-contract`
- distractor: `inventory-notes`
- forbidden inputs: one unsafe card and one card from another project

Acceptance thresholds:

| Metric | Required |
| --- | ---: |
| Required-card recall | 1.0 |
| Evidence precision | 1.0 |
| Unsafe/cross-project exclusion | 1.0 |
| Provider fallback visibility | 1.0 |

The test also checks that returned context evidence exposes provider-neutral
fields (artifact id, source reference, score, matched terms, snippet hash, and
prompt eligibility/redaction state) without retaining raw provider payloads.
