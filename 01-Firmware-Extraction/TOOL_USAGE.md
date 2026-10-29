# Extraction tool usage and source provenance

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

## Historical device pipeline (not runnable from this ZIP alone)

`src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/run_stock_backup.py` is the successful coordinator. It imports `backup_core`, the earlier `MF904Q_Wait_Modem/da2_probe/run_da2_probe.py`, and `wait_preloader.py`. Those import further audited protocol and dependency files. It reads the successful reference session before allowing a matching device. The original launcher and private scope are documented in the complete guide.

The public source preserves historical layout under `src/`; a tools ZIP is not a substitute for the old working directory. Original DA files, their legal provenance, runtime/dependency packages, reference geometry/CID, GPT binary reference and active approval are omitted. Some transitive helper modules or input files remain absent. Do not execute the historical runner to discover whether dependencies are complete. No source-copy validation here claims live portability.

## Offline helper supplied for publication review

From this folder, on the computer only:

```powershell
python scripts/verify_public_files.py .
```

It checks `SHA256SUMS.txt`, refuses missing or changed distributed files and performs no device enumeration or network access. Output `PASS` validates the release's local files, not the modem or factory dump. The helper is new packaging code, not the historical extraction engine.

## Existing independent backup verifier

`verify_backup.py` never opens a device. In the original private backup tree it expects `manifest.json`, payload files and checkpoint metadata and verifies hashes, sizes, GPT and overlap. Those files must not be uploaded into the public source tree just to make the script run. Its historical PASS is preserved in a selected JSON summary.


## Updated source release25October2026

The earlier41-file hold is superseded by the per-file review.50 reviewed historical files are supplied, including10 additional matching DA dependencies.24 covered DA components retain GPLv3 source terms;26 independent/factual files have no newly selected blanket license. The single unresolved assembly file is withheld. Vendor DA, factory images and private identity/approval/reference files remain excluded. Source layout preserves original paths and safety gates, so these are not portable turnkey live tools. See RIGHTS_AND_RUNTIME_LIMITATIONS.md at repository root before use.
