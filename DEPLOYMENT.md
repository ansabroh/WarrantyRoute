# Studio deployment

1. Open https://studio.genlayer.com and select GenLayer Studio network.
2. Use the built-in Studio account. Import `contracts/warranty_route.py`. Do not import or expose a private key; no MetaMask is required.
3. Run schema generation. Deploy with no constructor arguments.
4. Record the actual deployed address and deployment transaction. Wait for finalization and verify successful execution; an accepted transaction alone is not final proof.
5. Publish fixtures to GitHub. Run `scripts/build_inputs.py` at the exact fixture commit and addresses used by Studio.
6. In issuer account execute register_warranty; in claimant account file_claim; in service account attest_service; in claimant or issuer account assess. Wait for each transaction and verify state before proceeding.
7. Read status and receipt. Expected synthetic demo: PARTIALLY_COVERED (motor covered, housing cosmetic exclusion). A strict review may instead produce INCONCLUSIVE; document actual observations rather than assuming this result.
8. Save receipts, network ID, exact source SHA-256 and explorer contract URL in `evidence/deployment.json` and EVIDENCE.md. Do not claim testnet deployment from a direct-mode test.

Current v1.1 deployment: https://explorer-studio.genlayer.com/address/0x15a7F0799E6cc6E1123aafaC92A29855886fBEc1

No automatic deployment script signs with a user key. The intended deployment surface is Studio's built-in account. See EVIDENCE.md for performed steps and remaining blockers, if any.
