# AI Cryptanalysis Todo
Princess Grogan

## Goal

Review the PQC federated-learning code, especially the CRYSTALS-Kyber
encryption and decryption flow, using Codex and then confirm the results with a
human developer.

## Tasks

- [ ] Write a short description of the system and the Kyber data flow.
- [ ] Add the review prompts to a README.
- [ ] Include prompts for:
  - [ ] Searching the codebase for security issues.
  - [ ] Checking data structures and serialization.
  - [ ] Checking the Kyber implementation and error handling.
  - [ ] Reporting files, lines, evidence, and suggested tests.
- [ ] Run the prompts with Codex's best model from the Codex extension tab.
- [ ] Save the search results and analysis findings.

## Agent + Human Review Loop

1. **Agent review:** Codex searches the codebase and reports possible issues.
2. **Human review:** A developer checks each result against the code and tests.
3. **Fix plan:** Keep confirmed issues, reject false positives, and prioritize
   the remaining work.
4. **Implementation:** Apply the approved fixes and add regression tests.
5. **Repeat:** Run Codex again and have the developer confirm that the fixes
   worked.

## Done When

- [ ] The Kyber encryption/decryption path has been reviewed.
- [ ] Findings include evidence and are confirmed by a human.
- [ ] Approved fixes and tests are complete.
- [ ] A final Codex review reports no unresolved confirmed issues.

