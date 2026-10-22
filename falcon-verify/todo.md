# Trustworthy AI Authentication and Model Verification

This checklist starts from [`todo.txt`](./todo.txt) and expands the
**Trustworthy AI Authentication** flow shown in the design:

```text
Application binary
        |
     SHA-256
        |
  Falcon-512 verification
        |
   Correct application?
      /              \
 FLAG UNSAFE        EXECUTE
 AND REPORT
```

The result should be a standalone web application that lets a person verify a
downloaded final model/application artifact before running or deploying it.
The verifier should report authenticity and integrity; it must not imply that
the model is safe, unbiased, malware-free, or correct merely because a
signature is valid.

## 1. Define the trust model and artifact contract

- [ ] Confirm the artifact types that may be verified:
  - [ ] Model binary or archive.
  - [ ] Application binary, if supported.
  - [ ] Metadata/manifest and detached signature.
- [ ] Define the signed artifact contract:
  - [ ] Exact bytes that are hashed and signed.
  - [ ] SHA-256 digest encoding and casing.
  - [ ] Falcon parameter set, initially Falcon-512.
  - [ ] Signature encoding and serialization.
  - [ ] Artifact name, version, release identifier, and build timestamp.
  - [ ] Optional size, media type, and platform fields.
- [ ] Decide whether signatures are detached or bundled with the artifact.
      Prefer a detached signature or a clearly defined signed manifest so the
      verifier hashes exactly the distributed artifact bytes.
- [ ] Define the trust anchor:
  - [ ] Publish the Falcon-512 public key through a trusted, versioned channel.
  - [ ] Pin or explicitly select the expected key identifier.
  - [ ] Document how key rotation and revocation work.
  - [ ] Never retrieve a verification key from the uploaded artifact alone.
  - [ ] Never upload, extract, store, or expose the Falcon private signing key.
- [ ] Define what a valid result means:
  - [ ] The digest matches the signed digest/manifest.
  - [ ] The signature validates under a trusted public key.
  - [ ] Metadata matches the selected artifact and expected release.
- [ ] Define what a valid result does not mean:
  - [ ] It does not prove the artifact is benign or bug-free.
  - [ ] It does not replace malware scanning, dependency review, or runtime
        isolation.
  - [ ] It does not authorize execution without the user's final decision.

## 2. Standalone web application architecture

- [ ] Create a small Flask application dedicated to verification.
- [ ] Separate the web UI, verification service, key/trust-anchor provider,
      and audit/reporting components behind clear interfaces.
- [ ] Decide where verification runs:
  - [ ] Prefer local/client-side verification when practical so model binaries
        and sensitive artifacts do not leave the user's machine.
  - [ ] If server-side verification is required, document upload handling,
        retention, access control, privacy, and deletion guarantees.
- [ ] Add a health endpoint that exposes no keys, uploaded content, or secrets.
- [ ] Add configuration for:
  - [ ] Maximum upload size.
  - [ ] Allowed artifact and signature formats.
  - [ ] Trusted key source and key identifiers.
  - [ ] Upload retention and temporary-directory behavior.
  - [ ] Verification timeout and resource limits.
  - [ ] Application environment and logging level.
- [ ] Keep verification deterministic and side-effect free: verifying an
      artifact must not execute, import, deserialize, or load it as code/model.
- [ ] Ensure the server never places an uploaded artifact in a web-accessible
      directory.
- [ ] Add secure deployment guidance for HTTPS, reverse proxies, process
      isolation, and non-debug production mode.

## 3. Artifact publication and signing pipeline

- [ ] Build the final model/application artifact from a reproducible or
      documented build process.
- [ ] Hash the exact release bytes with SHA-256.
- [ ] Produce a signed manifest containing at least:
  - [ ] Artifact filename and release/version identifier.
  - [ ] SHA-256 digest.
  - [ ] Falcon algorithm/parameter-set identifier.
  - [ ] Public-key identifier and key version.
  - [ ] Signature encoding/version.
  - [ ] Optional platform and build metadata.
- [ ] Sign the canonical manifest using the protected Falcon-512 private key.
- [ ] Publish the artifact, manifest, signature, and public-key metadata
      together, with checksums and stable download URLs.
- [ ] Protect the signing operation:
  - [ ] Keep the private key out of source control and application containers.
  - [ ] Restrict signing access and record signing events.
  - [ ] Use an approved key-management mechanism where available.
  - [ ] Test key backup, rotation, revocation, and compromise response.
- [ ] Verify a release independently before publication.
- [ ] Add release tests that reject changed bytes, changed metadata, invalid
      signatures, wrong keys, and unsupported algorithm identifiers.

## 4. Verification workflow

- [ ] Present a clear upload form for:
  - [ ] Application/model binary or archive.
  - [ ] Detached signature or signed manifest.
  - [ ] Optional release/version selection.
- [ ] Validate request size, file type, filename, and required fields before
      processing.
- [ ] Generate a server-side temporary identifier; do not trust the original
      filename as a path.
- [ ] Stream or bounded-read the upload while computing SHA-256.
- [ ] Reject empty, truncated, oversized, malformed, or unsupported inputs.
- [ ] Load the trusted public key by key identifier and verify its format,
      parameter set, and provenance.
- [ ] Canonicalize and validate the manifest before signature verification.
- [ ] Verify the Falcon-512 signature over the canonical manifest.
- [ ] Compare the computed artifact SHA-256 digest with the signed digest using
      a constant-time comparison.
- [ ] Check that the artifact metadata matches the user-selected release and
      expected platform, where those checks are part of the contract.
- [ ] Return a structured result with separate states:
  - [ ] **Verified:** digest and Falcon signature are valid under the trusted
        key and metadata checks pass.
  - [ ] **Integrity failed:** uploaded bytes do not match the signed digest.
  - [ ] **Signature failed:** the signature is invalid or the key is not
        trusted.
  - [ ] **Unsupported:** unknown algorithm, format, key version, or manifest
        schema.
  - [ ] **Processing failed:** an operational error prevented a conclusion.
- [ ] Fail closed: any verification error must not produce a success result.
- [ ] Do not execute, preview, import, unpickle, decompress without limits, or
      otherwise interpret the uploaded artifact during verification.
- [ ] Delete temporary uploads after the configured retention period and on
      failure paths where possible.

## 5. User experience and safety messaging

- [ ] Show the computed SHA-256 digest so the user can compare it with an
      independent release source.
- [ ] Show the signing key identifier, algorithm, artifact version, and
      verification timestamp.
- [ ] Make the final state unambiguous:
  - [ ] Green/positive state only for a complete verified result.
  - [ ] Red/unsafe state for failed, mismatched, revoked, or unknown results.
  - [ ] Neutral/error state for inconclusive operational failures.
- [ ] For an unsafe or inconclusive result, explicitly instruct the user not
      to execute or deploy the artifact and to report the artifact/version.
- [ ] Do not provide an "execute" button by default. If execution is ever
      integrated, require a separate, explicit approval and a sandboxed runner.
- [ ] Explain that a valid signature authenticates the publisher-controlled
      bytes, not the model's behavior or the absence of vulnerabilities.
- [ ] Make the UI accessible by keyboard and screen reader, and do not rely on
      color alone to communicate status.
- [ ] Avoid showing sensitive upload contents in errors, browser history,
      analytics, or logs.

## 6. API and data model

- [ ] Define a versioned verification endpoint, for example:
  - [ ] `POST /api/v1/verify` for multipart artifact and manifest upload.
  - [ ] `GET /api/v1/keys/<key-id>` for public trust-anchor metadata only.
  - [ ] `GET /healthz` for liveness/readiness.
- [ ] Define a stable response schema:

```json
{
  "status": "verified",
  "artifact": {
    "name": "model.bin",
    "version": "1.0.0",
    "sha256": "<lowercase-hex-digest>"
  },
  "signature": {
    "algorithm": "Falcon-512",
    "key_id": "release-key-2026-v1",
    "valid": true
  },
  "checks": {
    "sha256_match": true,
    "trusted_key": true,
    "metadata_match": true
  },
  "warnings": [
    "Signature verification does not prove model safety."
  ]
}
```

- [ ] Never return private keys, raw signatures when unnecessary, uploaded
      content, internal stack traces, or filesystem paths.
- [ ] Use explicit schema validation and reject unknown or ambiguous algorithm
      identifiers.
- [ ] Define error codes that let the UI distinguish invalid input, failed
      verification, unsupported formats, and service failures.
- [ ] Add request correlation IDs that contain no artifact or user secrets.

## 7. Security hardening

- [ ] Set upload limits and enforce them before buffering the complete file.
- [ ] Use safe temporary files with restrictive permissions and unpredictable
      names.
- [ ] Prevent path traversal, symlink attacks, archive traversal, and
      decompression/resource-exhaustion attacks.
- [ ] Apply rate limiting and request timeouts.
- [ ] Use CSRF protection for browser-based state-changing requests.
- [ ] Configure secure headers, HTTPS, cookie flags, and an appropriate
      content-security policy.
- [ ] Disable Flask debug mode and detailed error pages in production.
- [ ] Redact filenames, digests where sensitive, key material, and upload
      metadata from logs according to the privacy policy.
- [ ] Restrict access to administrative key-management and audit operations.
- [ ] Pin and regularly review cryptographic and web dependencies.
- [ ] Establish key revocation behavior and ensure revoked keys cannot yield a
      positive verification result.
- [ ] Threat-model malicious manifests, malformed signatures, oversized files,
      repeated uploads, and compromised key metadata.

## 8. Testing and verification

- [ ] Unit-test SHA-256 hashing against known test vectors.
- [ ] Unit-test Falcon-512 verification against:
  - [ ] A valid artifact/manifest/signature tuple.
  - [ ] One-bit artifact changes.
  - [ ] One-bit manifest changes.
  - [ ] One-bit signature changes.
  - [ ] Wrong public key.
  - [ ] Wrong algorithm or parameter-set identifier.
  - [ ] Truncated and oversized inputs.
  - [ ] Malformed encodings and duplicate manifest fields.
  - [ ] Revoked or unknown key identifiers.
- [ ] Add integration tests for the upload endpoint and every response status.
- [ ] Test that no uploaded file is executed, imported, or model-deserialized.
- [ ] Test cleanup after success, failure, timeout, and client disconnect.
- [ ] Test concurrent uploads, rate limits, and maximum-size boundaries.
- [ ] Add browser tests for positive, negative, unsupported, and inconclusive
      states.
- [ ] Run dependency, static-analysis, and security checks in CI.
- [ ] Test the publication pipeline independently from the web verifier.
- [ ] Perform a human review of cryptographic API usage and trust-anchor
      configuration before production release.

## 9. Deployment and operations

- [ ] Package the verifier with reproducible dependency versions.
- [ ] Deploy behind HTTPS and a production WSGI server/reverse proxy.
- [ ] Run as a least-privileged account with a read-only application image
      where practical.
- [ ] Isolate temporary upload storage and set quotas.
- [ ] Monitor verification success/failure rates, unsupported formats, service
      errors, and abuse signals without collecting artifact contents.
- [ ] Alert on unexpected key changes, repeated signature failures, and
      signing-key revocation.
- [ ] Document incident response for:
  - [ ] Compromised signing key.
  - [ ] Incorrectly published artifact.
  - [ ] Revoked release.
  - [ ] Verifier compromise or false-positive result.
- [ ] Publish an operator runbook and user-facing verification instructions.
- [ ] Define retention and deletion policies for uploads, audit records, and
      operational logs.

## 10. Completion criteria

- [ ] A user can independently obtain an artifact, manifest/signature, and
      trusted public-key metadata.
- [ ] The web application computes the artifact SHA-256 digest and verifies the
      Falcon-512 signature without executing the artifact.
- [ ] Any byte or signed metadata change produces a non-success result.
- [ ] Unknown, revoked, malformed, and unsupported inputs fail closed.
- [ ] The service does not expose or require a Falcon private key.
- [ ] The UI clearly distinguishes verified, unsafe, unsupported, and
      inconclusive outcomes.
- [ ] Automated tests cover the cryptographic, web, cleanup, and abuse cases.
- [ ] Deployment, key rotation, revocation, privacy, and incident procedures
      are documented.
- [ ] A qualified reviewer confirms that the trust anchor and signing process
      match the security claims.

## Deliverables

- [ ] Standalone Flask verifier application.
- [ ] Versioned artifact/manifest/signature format.
- [ ] Secure Falcon-512 signing and public-key publication procedure.
- [ ] SHA-256 and Falcon verification module with unit tests.
- [ ] Upload UI and structured verification API.
- [ ] Positive, unsafe, unsupported, and inconclusive result views.
- [ ] Automated integration and browser tests.
- [ ] Deployment, operations, key-rotation, and incident-response documentation.

