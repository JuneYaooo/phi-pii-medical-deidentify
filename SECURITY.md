# Security Policy

## Reporting a vulnerability

Do not open a public issue containing real patient data, PHI, PII, credentials, unredacted screenshots, or production audit artifacts.

Report vulnerabilities through the repository host's private security-advisory channel when available. Include a minimal synthetic reproduction, affected version or commit, impact, and proposed mitigation. If no private channel is configured, open a public issue containing only a request for a private contact path and no sensitive technical details.

## Sensitive test material

- Use synthetic names, identifiers, images, and documents.
- Remove metadata before sharing files.
- Treat thumbnails and contact sheets as potentially sensitive even after automated redaction.
- Do not attach source documents or deterministic hashes of short sensitive values.

## Scope

Security reports may cover identifier leakage, reversible masking, unsafe path handling, audit-log exposure, residual-verification bypass, dependency issues, or output/source confusion.

This repository does not itself provide authentication, authorization, encryption at rest, key management, retention enforcement, legal review, or HIPAA compliance certification. Deployers are responsible for those controls.
