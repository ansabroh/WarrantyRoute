# Verification evidence

Verified on 2026-11-04 with Python 3.12.14, genlayer-test 0.29.2 and the pinned GenVM SDK v0.2.16 runner.

- 34 SDK direct-mode tests pass. External web/LLM I/O is mocked; captured validators are explicitly executed.
- `genvm-lint check contracts/warranty_route.py`: lint and SDK validation pass; nine public methods.
- ABI extracted to `evidence/abi.json`.
- Test vectors include all four outcomes, inclusive end dates, late reports, pre-purchase onset, role isolation, immutable data, duplicate claims, evidence integrity, bounded retry chains, malformed model output and independent validator rejection.
- Direct mode auto-parses mock JSON strings even for text mode, so tests encode mock text as JSON strings to preserve the contract's strict duplicate-key JSON parser. This is a test-runner adaptation; production parsing is unchanged.

Live deployment verification is in progress. No deployed address or finalized transaction is asserted by this document until a deployment record is added.
