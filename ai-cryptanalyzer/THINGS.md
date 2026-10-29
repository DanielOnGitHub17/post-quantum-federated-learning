# post-quantum-federated-learning
1. PQC-Enabled Federated Learning
We train machine learning models locally across decentralized devices using partitioned datasets. Once local updates are finished, we securely transmit the weights and gradients to a central server using CRYSTALS-Kyber for encryption and decryption, protecting the transit against interception.

2. AI-Based Cryptanalysis of PQC
Before relying on these communication channels, we stress-test and evaluate our PQC algorithms using advanced AI models like Claude Opus and top-tier Gemini and ChatGPT versions. This involves simulating extreme conditions and automated cryptanalytic pressure to ensure the encryption primitives are completely foolproof.

3. Trustworthy AI & Authentication
Once the central server aggregates the final model, we generate its binary hash and use Falcon post-quantum signatures to create a secure digital certificate. We then provide a verification tool where users can check the authenticity of downloaded binaries, ensuring the model hasn't been tampered with or spoofed.

![Post-quantum federated learning architecture](./PQC-FL.png)


## AI Cryptanalysis and Security Review

### System Description and Kyber Data Flow

This project uses post-quantum cryptography to help protect communications in a federated-learning system. Clients train machine-learning models locally and send model updates to a central server for aggregation. The cryptographic code must be reviewed to determine how keys are generated, how shared secrets are established, and how model updates are protected during transmission.

The review will trace the actual implementation of Kyber or ML-KEM, including key generation, encapsulation and decapsulation, encryption and decryption, data serialization, and error handling. Codex will help identify potential security concerns, but a human developer must verify each finding before it is treated as confirmed.

### Review Rules

- Review the actual source code and cite the exact file paths and line numbers.
- Do not edit files during the initial review.
- Do not execute code or tests without developer approval.
- Do not expose private keys, credentials, or other secrets.
- Separate potential issues from confirmed vulnerabilities.
- Include evidence, possible impact, confidence, and suggested tests for every finding.
- Do not claim a test passed unless it was actually run.

### Prompt A: General Security Review

Review this repository for potential security weaknesses related to post-quantum federated learning. Examine cryptographic key handling, authentication, data integrity, model-update transmission, input validation, error handling, logging, and dependencies where relevant.

For each potential issue, provide the title, exact file path, line numbers, code evidence, possible impact, assumptions, confidence level, and a suggested verification test. Do not modify files or execute commands. Label unverified concerns clearly.

### Prompt B: Data Structures and Serialization

Inspect the data structures and serialization methods used to exchange model updates and cryptographic values between clients and the server. Look for unsafe deserialization, malformed or truncated inputs, incorrect byte encoding and decoding, inconsistent message formats, missing validation, unexpected data types, and data-integrity concerns.

For each potential issue, identify the file and lines, supporting evidence, possible impact, and a suggested test. Do not modify files or run tests.

### Prompt C: Kyber / ML-KEM and Error Handling

Trace the actual Kyber or ML-KEM implementation in this repository. Examine key generation, encapsulation and decapsulation where applicable, and any subsequent encryption or decryption of model updates.

Identify the cryptographic library and algorithms used. Check how public keys, private keys, ciphertexts, and shared secrets are handled; whether data encryption and integrity protection are appropriate; and whether malformed inputs and cryptographic failures are handled safely.

Support every observation with exact source-code evidence. Do not assume an issue is a vulnerability without sufficient evidence. Do not modify files or execute code.

### Prompt D: Findings and Test Plan

Produce a structured report of potential security findings. For each finding, include:

- Unique ID and short title.
- Severity and confidence, with justification.
- Exact file path and line numbers.
- Code evidence and possible impact.
- Verification steps for a human developer.
- Suggested test and expected result.
- Status: unverified, confirmed, rejected, or needs investigation.

Prioritize findings by risk. Do not invent test results or claim vulnerabilities are confirmed without adequate evidence.

### Human Verification and Fixes

A developer must inspect each finding and verify it against the source code and appropriate tests. Document false positives and the reasons for rejecting them. Prioritize confirmed issues, approve fixes, and add regression tests. After changes are approved and tested, run another Codex review and have a human developer confirm the results.

### Completion Criteria

The review is complete when the Kyber / ML-KEM data flow has been examined, findings have supporting evidence and human-reviewed statuses, approved fixes and regression tests are complete, and the final review documents whether any confirmed issues remain unresolved within the review scope.
