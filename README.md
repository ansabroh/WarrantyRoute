# WarrantyRoute

Standalone GenLayer Intelligent Contract for product warranty eligibility. It combines deterministic coverage deadlines with independent AI interpretation of original warranty terms, reported defects, exclusions and repair history. It records **COVERED**, **PARTIALLY_COVERED**, **EXCLUDED** or **INCONCLUSIVE** without approving payments or transferring assets.

## Why GenLayer

Whether a winding failure is a manufacturing defect, a scratch is cosmetic, or a repair history triggers an exclusion requires interpreting evidence. Each validator independently fetches the exact registered documents and performs its own assessment with `gl.vm.run_nondet_unsafe`. It compares identity and every item classification, validates the leader's quotations against the fetched bytes, then independently audits contextual grounding. Deterministic code derives the final outcome and hash-linked receipt.

## Lifecycle

1. Deployment binds one warranty issuer to the deployment account.
2. Issuer calls `register_warranty(id, warranty_json)`, committing original purchase evidence, terms, product, claimant, authorized service account and coverage deadlines.
3. Claimant calls `file_claim(id, warranty_id, claim_json)`. Reporting day is taken from chain time; defect onset is an allegation checked against service evidence.
4. Registered service account calls `attest_service(claim_id, report_json)`, binding immutable evidence to the exact claim hash.
5. Issuer or claimant calls `assess(claim_id)`. Only an INCONCLUSIVE assessment can be retried, at most three total attempts. Terminal results cannot be replaced. Failed consensus transactions do not create receipts.
6. Read `get_status`, `get_receipt`, `get_claim`, `get_warranty`, and `get_service_report`.

An assessment is advisory contractual evidence, not a legal determination of consumer rights. A partial result means a mix of explicitly covered and excluded claim items, not an invented payout percentage. Any unknown item or uncertain identity makes the entire assessment INCONCLUSIVE. A verified identity with failure after the coverage end or reporting after the deadline is EXCLUDED. A failure before purchase is INCONCLUSIVE. End dates are inclusive.

## Run verification

Python 3.12+:

```sh
python -m pip install -r requirements-dev.txt
gltest tests -q
genvm-lint check contracts/warranty_route.py
genvm-lint schema contracts/warranty_route.py --output evidence/abi.json
```

Tests use the actual GenLayer SDK direct runner, with external web/LLM I/O mocked. They explicitly execute captured validator callbacks, including disagreement and fabricated quotations. They are not proof of live network consensus. See [EVIDENCE.md](EVIDENCE.md) for the current live status.

## Evidence format

Every document is a public UTF-8 plaintext file at `https://raw.githubusercontent.com/OWNER/REPO/40_CHARACTER_COMMIT/path.txt`, with exact lowercase `sha256` and byte count (`bytes`, 1–12,000). No branch refs, queries, credentials or arbitrary hosts. Checks run separately on leader and validators. Limits are checked after the network response has been obtained; this is not a transport download limit. Three documents maximum per review; eight claim items; three successful assessment attempts maximum.

Publish synthetic fixtures first, then build exact inputs:

```sh
python scripts/build_inputs.py --commit COMMIT_SHA --claimant 0xACCOUNT --service-provider 0xSERVICE
```

Use the generated positional arguments in Studio. Distinct claimant and service accounts are recommended. A single Studio account can demonstrate all roles, but that does not demonstrate organizational independence.

See [API](docs/API.md), [security and trust boundaries](SECURITY.md), [Studio deployment](DEPLOYMENT.md), and [submission text](SUBMISSION.md). Public fixtures are synthetic. Never publish personal receipts, addresses or private customer records to this demonstration repository.
