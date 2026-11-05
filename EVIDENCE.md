# Verification evidence

## Source and automated checks

WarrantyRoute v1.1: source commit `fd55cc462b8352cbb4128d977f48d344d87c6b78`.

- **35 SDK direct-mode tests pass**, using Python 3.12.14, genlayer-test 0.29.2 and the pinned GenVM SDK v0.2.16 runner. External web/LLM I/O is mocked; captured validator callbacks are explicitly executed.
- **GenVM lint and SDK validation pass**, with nine public methods. ABI is in `evidence/abi.json`.
- Raw check outputs: `evidence/tests.txt`, `evidence/validation.txt`.
- Vectors cover all four outcomes, inclusive date boundaries, late reports, pre-purchase onset, role isolation, immutable data, duplicate claims, byte/hash integrity, bounded retries, receipt chains, malformed model responses and independent validator rejection.
- v1.1 requests structured JSON model output, checks exact returned fields, validates quotation grounding, and supplies deterministic ISO dates. Externally supplied JSON rejects duplicate keys.

## Current live instance

Network: GenLayer Studio / Studionet, chain ID 61999.

Contract: [`0x15a7F0799E6cc6E1123aafaC92A29855886fBEc1`](https://explorer-studio.genlayer.com/address/0x15a7F0799E6cc6E1123aafaC92A29855886fBEc1)

Deployment: [`0xde6d6cc8…89b1a3f1`](https://explorer-studio.genlayer.com/tx/0xde6d6cc8f70363354008450759ff0d5e7acb5dcfa7f71735ced20ae989b1a3f1) — FINALIZED, SUCCESS.

Deployed explorer source was compared character-for-character with the tested local source: exact match. `evidence/deployment.json` records its SHA-256, network and transaction hashes. `evidence/studio-inputs.json` contains the exact synthetic inputs. Fixtures are pinned to commit `87e0fcfd2d304032b02dc95448f0f9562f25bc1b`.

Deployment and all transactions use Studio's built-in account, Normal (Full Consensus), with simulation disabled. This demonstration uses one account for issuer, claimant and authorized service provider; distinct organizational identities are not demonstrated. Role isolation is covered by the multi-account direct tests.

On 2026-11-05, v1.1 registration (`0xee81…`), claim filing (`0x2d8e…`) and service attestation (`0x975b…`) were observed FINALIZED in Studio. These are abbreviated identifiers, not full transaction hashes. The v1.1 assessment was **not submitted**: automatic browser approval review failed because the session usage limit had been reached. No v1.1 assessment receipt or positive live eligibility outcome is claimed. Run `assess("c_demo")` in Studio and verify finalization and receipt before claiming the live lifecycle is complete.

## Earlier deployment

v1: `0x9EB4351825346fD068Cb68920bfA3f494bcEcc57`. Its deployment, registration, claim, service attestation and assessment finalized successfully. The assessment recorded **INCONCLUSIVE / INVALID_AI_REVIEW** after leader rotation. A same-source Studio code-upgrade transaction also finalized; it changed neither the source nor the assessment data. This earlier instance demonstrates strict failure handling, not successful semantic eligibility.

The earlier deployment and receipt are preserved in `evidence/legacy-deployment.json` and `evidence/legacy-receipts.json`. v1.1 improves model response transport with native structured JSON and deterministic calendar dates; it is a fresh deployment and does not overwrite that history.
