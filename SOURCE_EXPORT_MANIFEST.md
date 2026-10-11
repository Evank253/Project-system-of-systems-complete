# Source Export Manifest

**Project:** Project System of Systems Complete  
**Manifest version:** 0.1-draft  
**Prepared:** 2026-10-10  
**Status:** INCOMPLETE — source payload has not yet been transferred into this repository.

## Purpose

This manifest is the inventory control point for a future source export intended for independent technical review. It must list the actual files included in the export, their provenance, and their integrity hashes. Do not mark this export complete until the source files and supporting materials have been transferred and checked.

## Repository contents currently established

The following project-level documentation files have been added to this repository:

| Path | Purpose | Status |
|---|---|---|
| `README.md` | Project overview and source-package status | Present |
| `LICENSE` | Proprietary review-use notice | Present; legal review recommended |
| `COPYRIGHT.md` | Copyright and provenance notice | Present; ownership depends on provenance |
| `TRADEMARKS.md` | Trademark and brand-use notice | Present; no registration claimed |
| `PATENT-NOTICE.md` | Patent-status notice | Present; no patent-pending claim made |

These files are administrative notices. They are not the KETCHUM-SOS application source export.

## Source material inventory

The following source materials are expected for review. Their presence in this repository is **not yet established**:

| Material group | Expected contents | Status |
|---|---|---|
| Application backend | EIL, lifecycle, KSI, API server, AI assistant, related modules | NOT_TRANSFERRED |
| Frontend | Components, pages, configuration, package/dependency files | NOT_TRANSFERRED |
| Tests | Acceptance, adversarial, EIL adversarial, external TEVV/reproduction tests | NOT_TRANSFERRED |
| Constitution and governance | Authoritative constitutional docs, policy, delegation rules | NOT_TRANSFERRED |
| Evidence and provenance | Evidence records, ledger exports, hashes, source manifests | NOT_TRANSFERRED |
| Supporting documentation | Architecture, known limitations, test reports, prior findings | NOT_TRANSFERRED |
| Build/runtime configuration | Dependency manifests and non-secret configuration | NOT_TRANSFERRED |
| Secrets | API keys, passwords, tokens, private credentials | EXCLUDED — do not export |

## Required provenance fields

For each transferred file, record:

- Exact relative path in the export.
- Original source repository or upload/source location.
- Original commit, version, or timestamp if known.
- SHA-256 hash computed from the actual exported file.
- File size.
- Classification: source, documentation, test, evidence, configuration, or third-party.
- Review status: inventoried, inspected, reproduced, or NOT_MEASURED.
- Any redactions, omissions, or known truncation.

Do not invent provenance, commit identifiers, hashes, test outcomes, or completeness claims.

## Integrity procedure

After source files are transferred:

1. Preserve a read-only copy of the original input package.
2. Inventory every file, including nested files.
3. Exclude credentials and secrets; document exclusions without copying their values.
4. Compute SHA-256 for every included file.
5. Generate a sorted `SHA256SUMS.txt` from the actual files.
6. Verify the generated checksums against the exported files.
7. Record the source revision and export timestamp where known.
8. Compare the final inventory with the input inventory and list every omission.
9. Keep the source export separate from any later remediation copy.
10. Only change status to COMPLETE after the inventory and checksums have been independently checked.

## Current conclusion

This repository is **not yet a complete source export**. The current files establish the project-level notices and a manifest template only. Do not submit this repository as the complete technical source package for an adversarial review until the actual source and supporting artifacts are transferred.
