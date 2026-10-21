# AI-Based Cryptanalysis and Code-Review Workflow

This checklist starts from [`todo.txt`](./todo.txt) and expands it into the work
represented by the **AI Based Cryptanalysis** design:

```text
System instructions
        |
Data-structure checks ----\
                            > AI code analyzer -> Analysis results -> Fix plan
Algorithm implementation --/                                      |
                                                                  v
                         PQC-FL: Kyber encryption/decryption <- Developer
```

The goal is to find and help remediate implementation weaknesses in this
repository's post-quantum federated-learning communication path. The workflow
must assess the code and its evidence; it must not claim that an algorithm is
"completely foolproof" or that a review proves security.

## 1. Project setup and scope

- [ ] Confirm the repository scope and the authorized files, commands, test
      fixtures, and generated artifacts that the analysis may inspect.
- [ ] Identify the PQC-FL entry points for:
  - [ ] Kyber key generation and key serialization.
  - [ ] Kyber encryption.
  - [ ] Kyber decryption.
  - [ ] Transport of encrypted model updates, weights, and gradients.
  - [ ] Error handling, retries, logging, and key lifecycle.
- [ ] Record the exact Kyber implementation, parameter set, bindings, and
      dependency versions. Verify that the implementation is a supported,
      maintained library rather than a home-grown primitive.
- [ ] Record the supported Python/runtime versions and the commands needed to
      run tests, static checks, and a local federated-learning example.
- [ ] Define the threat model:
  - [ ] Passive network interception.
  - [ ] Active tampering or replay of encrypted updates.
  - [ ] Malicious or compromised client.
  - [ ] Compromised aggregation server.
  - [ ] Accidental disclosure through logs, exceptions, temporary files, or
        debugging output.
- [ ] Define out-of-scope activity. Do not target third-party systems, real
      credentials, production data, or external services without explicit
      authorization.
- [ ] Create a baseline report before making fixes so regressions and newly
      introduced findings can be distinguished from pre-existing issues.

## 2. System description

- [ ] Write a short system description in the relevant README:
  - [ ] Local clients train on partitioned data.
  - [ ] Clients send model weights/gradients to a central aggregator.
  - [ ] Kyber protects the confidentiality of data in transit.
  - [ ] The aggregator decrypts and aggregates updates.
  - [ ] The final model artifact is hashed and signed with Falcon.
  - [ ] A verification tool checks the authenticity and integrity of a
        downloaded model.
- [ ] Add a component/data-flow diagram or equivalent text covering:
  - [ ] Trust boundaries.
  - [ ] Key ownership and distribution.
  - [ ] Plaintext and ciphertext locations.
  - [ ] Serialization formats.
  - [ ] Failure and retry paths.
  - [ ] Where authentication and replay protection occur.
- [ ] Explicitly document what Kyber provides and does not provide:
  - [ ] Confidentiality/key encapsulation.
  - [ ] No automatic sender authentication.
  - [ ] No automatic integrity of the application message or freshness.
  - [ ] The protocol's authentication, transcript binding, and replay
        defenses must be reviewed separately.
- [ ] Document the assumptions required for the security claims and list
      unresolved assumptions as risks rather than silently treating them as
      guarantees.

## 3. README prompt pack

- [ ] Put the final, versioned prompts in a README near the code they analyze.
- [ ] Give every prompt a stable name, intended model, inputs, expected output,
      and evidence requirements.
- [ ] Require models to cite file paths, line numbers, symbols, and tests.
- [ ] Require models to distinguish:
  - [ ] Confirmed defect.
  - [ ] Plausible concern requiring validation.
  - [ ] Informational hardening suggestion.
  - [ ] False positive or rejected hypothesis.
- [ ] Instruct models not to invent APIs, test results, vulnerabilities,
      cryptanalytic success, or repository behavior they did not observe.
- [ ] Instruct models to treat secrets, private keys, training data, and model
      updates as sensitive and to redact them from reports.
- [ ] Instruct models to recommend minimal fixes and tests, not rewrite
      cryptographic primitives without justification.

### 3.1 System-instructions prompt

```text
You are reviewing an authorized post-quantum federated-learning repository.
Analyze only the files and commands supplied in this task. Treat Kyber as a
cryptographic library, not as code to replace casually. Do not claim a break,
security proof, or exhaustive review without reproducible evidence.

For every finding, provide:
1. ID and severity (critical/high/medium/low/info).
2. Confidence from 1-10.
3. Exact file, line range, and symbol.
4. Threat actor and required preconditions.
5. Security property affected.
6. Evidence, including the code path and a reproducer or test when safe.
7. Minimal remediation.
8. Regression tests and residual risk.

Check confidentiality, authentication, integrity, freshness/replay resistance,
key lifecycle, nonce/randomness handling, serialization, error handling,
logging, dependency use, side channels, and denial-of-service behavior.
Never request or print real secrets. If evidence is insufficient, say what must
be inspected next instead of guessing.
```

### 3.2 Codebase reconnaissance prompt

```text
Search this repository for the complete PQC-FL message path. Start at the
client training/update boundary and trace key creation or loading, Kyber
encapsulation/encryption, serialization, transport, server decapsulation/
decryption, deserialization, aggregation, retries, and logging.

Return:
- a component and call-graph summary;
- all relevant files, symbols, and line ranges;
- plaintext/ciphertext/key lifetimes;
- trust boundaries and external inputs;
- missing links or code paths that could not be verified;
- targeted tests needed before security conclusions are made.

Do not report vulnerabilities yet. This is an evidence-gathering pass.
```

### 3.3 Data-structure checks prompt

```text
Review the data structures and wire formats used by the PQC-FL encryption and
decryption path. Verify types, lengths, encodings, versioning, canonical
serialization, bounds checks, validation order, malformed-input handling,
algorithm/parameter-set identifiers, and separation of metadata from
ciphertext.

Look specifically for truncation, ambiguity, type confusion, unsafe parsing,
key/ciphertext mix-ups, accidental plaintext copies, replayable messages, and
logs that expose sensitive values. Cite concrete evidence and propose focused
tests for each concern. Do not infer a vulnerability from naming alone.
```

### 3.4 Algorithm-implementation checks prompt

```text
Review how the repository invokes the approved Kyber implementation; do not
reimplement Kyber. Check parameter-set consistency, key generation,
encapsulation/decapsulation or encryption/decryption API usage, randomness
sources, failure handling, ciphertext validation, key reuse, nonce/AEAD
composition where applicable, and dependency/version pinning.

Separate library-level claims from application-integration defects. For each
finding, identify the exact precondition, affected security property, safe
reproducer or test, and smallest fix. If the implementation is correct but
the evidence is incomplete, report the missing evidence rather than a defect.
```

### 3.5 AI code-analyzer prompt

```text
Using the reconnaissance, data-structure, and algorithm-review evidence below,
correlate findings without duplicating them. Resolve contradictions by checking
the repository and tests. Rank findings by exploitability, impact, confidence,
and breadth of affected code.

Return JSON with:
{
  "scope": "...",
  "verified_paths": [],
  "findings": [
    {
      "id": "...",
      "severity": "critical|high|medium|low|info",
      "confidence": 1,
      "location": {"file": "...", "lines": "...", "symbol": "..."},
      "security_property": "...",
      "preconditions": [],
      "evidence": [],
      "recommended_fix": "...",
      "regression_tests": [],
      "residual_risk": "..."
    }
  ],
  "unknowns": [],
  "overall_assessment": "..."
}

Do not convert an unverified hypothesis into a confirmed vulnerability.
```

### 3.6 Fix-plan prompt

```text
Create a surgical remediation plan from the verified findings only. Order
work by severity and confidence, then by dependency. For each change specify:
files/symbols, behavior before and after, validation and error behavior,
tests, documentation updates, rollout/compatibility concerns, and residual
risk. Preserve the approved cryptographic library and existing public behavior
unless a security fix requires a deliberate change.

Flag any item that needs a human cryptographer or maintainer decision. Do not
mark a finding fixed until the relevant test or reproducible verification
passes.
```

### 3.7 Test and verification prompt

```text
Verify the proposed fixes against the stated security properties. Run the
smallest relevant tests first, then integration tests covering client-to-server
encrypted updates. Add negative tests for malformed, truncated, replayed,
wrong-parameter-set, and authentication-failure inputs where applicable.

Report exact commands, versions, pass/fail results, and remaining limitations.
Do not describe a test as a cryptanalytic break or proof. A passing test only
supports the behavior it actually covers.
```

## 4. Cryptanalysis loop

- [ ] Freeze the baseline commit, dependency lock state, runtime version, and
      test command output.
- [ ] Run **GPT LUNA** from the Copilot tab using the reconnaissance and
      system-instructions prompts.
- [ ] Save its output as an attributed review artifact with model/version,
      timestamp, prompt version, repository commit, and inspected files.
- [ ] Pass only the necessary code excerpts and LUNA evidence to **Claude**.
- [ ] Ask Claude to independently challenge the hypotheses, reproduce findings,
      identify false positives, and fill gaps using the data-structure and
      algorithm prompts.
- [ ] Pass the normalized evidence, not unsupported conclusions, to **Codex**.
- [ ] Ask Codex to map findings to exact code changes, tests, and README
      updates using the analyzer and fix-plan prompts.
- [ ] Have a developer review the proposed changes before applying them.
- [ ] Apply one coherent fix set at a time; keep unrelated refactors out.
- [ ] Run targeted unit/negative tests, then the end-to-end PQC-FL flow.
- [ ] Re-run the same analyzer prompts on the changed code.
- [ ] Compare the new report with the baseline:
  - [ ] Fixed findings have passing regression evidence.
  - [ ] Unfixed findings have an owner and explicit residual risk.
  - [ ] New findings are triaged rather than silently discarded.
- [ ] Repeat the loop until the exit criteria below are met.

### Required handoff record

- [ ] Provider/model and model version, if available.
- [ ] Prompt name and prompt version.
- [ ] Repository commit and dependency state.
- [ ] Files and line ranges supplied to the model.
- [ ] Commands and tests run.
- [ ] Findings accepted, rejected, deferred, or merged.
- [ ] Human reviewer and decision.

## 5. Findings and fix-plan standards

- [ ] Use consistent severities:
  - [ ] **Critical:** practical compromise of protected assets or a security
        boundary with severe impact.
  - [ ] **High:** realistic compromise of a core security property or broad
        exposure.
  - [ ] **Medium:** meaningful weakness requiring specific conditions or
        limited scope.
  - [ ] **Low:** defense-in-depth or low-impact weakness.
  - [ ] **Info:** observation, unknown, or documentation gap with no confirmed
        security impact.
- [ ] Every accepted finding includes a minimal safe reproducer or a clear
      explanation of why reproduction is unsafe.
- [ ] Every fix includes a regression test, or a documented reason a test
      cannot be automated.
- [ ] Do not close a finding solely because another model disagrees.
- [ ] Escalate disagreements involving cryptographic correctness, primitives,
      parameter choices, or security claims to a qualified human reviewer.

## 6. Loop exit criteria

- [ ] All PQC-FL encryption/decryption paths are traced or explicitly listed
      as unverified.
- [ ] No critical or high findings remain without an accepted mitigation,
      owner, and deadline.
- [ ] Medium findings are fixed or documented with residual risk and rationale.
- [ ] Key, ciphertext, plaintext, serialization, and error-handling tests pass.
- [ ] Malformed-input and replay/authentication tests cover the documented
      protocol properties.
- [ ] Dependency and parameter-set choices are recorded and reproducible.
- [ ] README prompts and system description match the implementation.
- [ ] The final report distinguishes implementation assurance from formal
      cryptanalysis or a cryptographic security proof.
- [ ] A developer and, where needed, a cryptography specialist approve the
      final residual-risk statement.

## 7. Deliverables

- [ ] Updated README system description and prompt pack.
- [ ] Baseline analysis report.
- [ ] Normalized findings report.
- [ ] Developer-reviewed fix plan.
- [ ] Code changes and regression tests.
- [ ] Final verification report with commands and results.
- [ ] Residual-risk and out-of-scope statement.

