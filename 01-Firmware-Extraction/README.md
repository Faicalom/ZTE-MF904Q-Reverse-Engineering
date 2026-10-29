# Firmware extraction research tools

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

The successful route was the 9 October stock DA2 backup pipeline, not the earlier failed `MF904Q_Original_Firmware_Backup` controller and not the later GUI flasher. Read the [complete guide](COMPLETE_EXTRACTION_GUIDE.md), [requirements](REQUIREMENTS.md), [usage](TOOL_USAGE.md), [partition map](PARTITION_LAYOUT.md), [verification](BACKUP_VERIFICATION.md), and [history](EXPERIMENT_HISTORY.md).

Reviewed historical source snapshots are present; `src/README.md` explains their scope and exclusions. They preserve the historical relative project folders; they are not a portable device-access package. Private identity references and proprietary DA binaries are deliberately absent. The `scripts/` helper can verify local files without contacting a device. No executable or active approval is included.
