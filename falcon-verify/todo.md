# Falcon Application Verification
Nonso Duaka

Build a small Flask web app that verifies an uploaded application binary.

## Flow

- [x] Read the expected application SHA-256 hash from
      `pqc-fl/app/dist/StockPredictor.sha256`.
- [x] Read the expected application signature from
      `pqc-fl/app/dist/StockPredictor.sig`.
- [x] Read the Falcon verification key from
      `pqc-fl/app/dist/StockPredictor.pub`.
- [x] Provide a page where a user can upload the application binary.
- [x] Compute the SHA-256 hash of the uploaded binary.
- [x] Compare the computed hash with the stored application hash.
- [x] Stop and report failure when the hashes do not match.
- [x] Falcon-verify the computed hash using the application signature and
      verification key.
- [x] Report success only when both the hash and signature checks pass.
- [x] Report a clear failure for missing configuration, invalid uploads,
      hash mismatches, or invalid signatures.
- [x] Never execute or otherwise load the uploaded binary.
- [x] Never expose secrets or uploaded binary contents in logs or responses.

## Tests

- [x] Matching binary, hash, and signature returns a successful result.
- [x] Modified binary fails the hash comparison.
- [x] Invalid signature fails Falcon verification.
- [x] Missing environment variables fail safely.
