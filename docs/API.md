# API

All writes accept positional arguments. JSON inputs reject unexpected keys.

| Method | Authorization | Purpose |
|---|---|---|
| `register_warranty(warranty_id, warranty_json)` | Deployment issuer | Immutable original agreement |
| `file_claim(claim_id, warranty_id, claim_json)` | Registered claimant | Immutable alleged defects |
| `attest_service(claim_id, report_json)` | Registered service provider | Immutable claim-bound service report |
| `assess(claim_id)` | Issuer or claimant | AI consensus plus deterministic verdict |
| `get_warranty(warranty_id)` | Public read | Warranty JSON |
| `get_claim(claim_id)` | Public read | Claim JSON including chain reporting day |
| `get_service_report(claim_id)` | Public read | Report descriptor, attestor, claim hash |
| `get_receipt(claim_id, sequence)` | Public read | Receipt JSON; sequence begins at 1 |
| `get_status(claim_id)` | Public read | Attempts, head hash, current outcome |

Warranty JSON keys: `product` (ASCII identifier); `claimant`, `service_provider` (addresses); `purchase_day`, `coverage_end_day`, `report_by_day` (Python date ordinals); `purchase`, `terms` (evidence descriptors). Purchase must not be in the future; coverage maximum 100 years; reporting grace maximum 366 days.

Claim JSON keys: `failure_day` (date ordinal no later than chain day), `items` (1–8). Each item: `id` (unique ASCII identifier), `component` (1–100 chars), `defect` (1–500 chars).

Evidence descriptor keys: `url`, `sha256`, `bytes`. Service attestation takes the descriptor directly. IDs are 1–64 ASCII letters, digits, hyphens or underscores. Top-level JSON length limits are 16,000 for warranty, 7,000 for claim and 1,000 for report. See `scripts/build_inputs.py` for an executable example.

Receipt hashing: remove only `receipt_hash`, serialize with `json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)`, UTF-8 encode, then SHA-256 hex. Each previous_hash is the full preceding receipt hash, first empty. Use `scripts/verify_receipt.py exported-receipts.json` with an ordered array.
