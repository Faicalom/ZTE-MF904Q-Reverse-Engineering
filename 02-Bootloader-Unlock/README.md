# Bootloader unlocking: research record and tools

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

The successful build is the gate-context instrumented LK, SHA256 `f566f0a28297f9459978a41b61c7b3ce254f5ad0e3cc4ec71fa37e094bbe8077`. Earlier V3 and corrected V3 had unsuccessful unlock attempts and must not be described as the successful final method.

Read the [complete guide](COMPLETE_UNLOCK_GUIDE.md) without skipping the prerequisites, then the [technical analysis](BOOTLOADER_TECHNICAL_ANALYSIS.md), [verification](SUCCESS_VERIFICATION.md), [history](EXPERIMENT_HISTORY.md), [usage](TOOL_USAGE.md) and [recovery limitations](RECOVERY_AND_ROLLBACK.md).

This is not a generic `fastboot flashing unlock` recipe. The command was the final step in a sequence involving original-image backups, an exact-build LK investigation, UART/error-return corrections, gate-input instrumentation, a validated diagnostic query and independent post-unlock verification. Historical sources remain in the private review candidate; this upload allowlist contains their detailed research account, selected evidence and new offline helpers. Proprietary binaries and personal authorization/identity data are absent.
