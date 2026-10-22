# Falcon Application Verification

Build a small Flask web app that verifies an uploaded application binary.

## Flow

- [ ] Configure the app to receive these values through environment variables:
  - `APPLICATION_HASH`: expected application SHA-256 hash.
  - `APPLICATION_SIGNATURE`: expected application signature.
  - `FALCON_VERIFICATION_KEY`: Falcon verification key.
- [ ] Read the expected application SHA-256 hash from the
      `APPLICATION_HASH` environment variable.
- [ ] Read the expected application signature from the
      `APPLICATION_SIGNATURE` environment variable.
- [ ] Read the Falcon verification key from the
      `FALCON_VERIFICATION_KEY` environment variable.
- [ ] Provide a page where a user can upload the application binary.
- [ ] Compute the SHA-256 hash of the uploaded binary.
- [ ] Compare the computed hash with `APPLICATION_HASH`.
- [ ] Stop and report failure when the hashes do not match.
- [ ] Falcon-verify the computed hash using the application signature and
      verification key.
- [ ] Report success only when both the hash and signature checks pass.
- [ ] Report a clear failure for missing configuration, invalid uploads,
      hash mismatches, or invalid signatures.
- [ ] Never execute or otherwise load the uploaded binary.
- [ ] Never expose secrets or uploaded binary contents in logs or responses.

## Tests

- [ ] Matching binary, hash, and signature returns a successful result.
- [ ] Modified binary fails the hash comparison.
- [ ] Invalid signature fails Falcon verification.
- [ ] Missing environment variables fail safely.
