# ZTE MF904Q / M19-E Reverse Engineering

Detailed evidence-led research on one WF904_V6.0 Android6 modem: verified readable firmware extraction, an original LK unlock flow and persistent unlocked state under restored factory LK. Arabic WebUI/LCD appeared, but permanent modified systems powered off; cause remains unresolved.

## Read the full technical history

1. [Complete firmware extraction guide](01-Firmware-Extraction/COMPLETE_EXTRACTION_GUIDE.md): Windows identity/transport, actual DA stages, all23 partitions, Boot1/Boot2, full User and independent verification.
2. [Android, OEM permission and native Fastboot entry](02-Bootloader-Unlock/PRE_UNLOCK_ANDROID_AND_FASTBOOT.md): the actual original service calls, separate permission checks, detached broadcast and FASTBOOT/TOOBTSAF path.
3. [Complete unlock guide](02-Bootloader-Unlock/COMPLETE_UNLOCK_GUIDE.md):13 full stages, each with purpose, recovered action, files, prerequisites, expected/actual responses, verification, failures, safe stop and recovery reference.
4. [Exact-build LK analysis](02-Bootloader-Unlock/BOOTLOADER_TECHNICAL_ANALYSIS.md), [success verification](02-Bootloader-Unlock/SUCCESS_VERIFICATION.md), and [unresolved modified-ROM analysis](03-Research-Results/CUSTOM_ROM_FAILURE_ANALYSIS.md).
5. [Latest restoration evidence and owner correction](CURRENT_BASELINE_20261023.md), [status](PROJECT_STATUS.md), [safety](SECURITY_AND_SAFETY.md), [rights gate](LICENSE_REVIEW.md).

## Distribution scope — reviewed source research release

50 reviewed historical source/build files are included across the two tool folders:24 GPL-scoped DA components and26 independently authored/factual files. Original contributor notices and the complete GPLv3 text are preserved. The per-file [rights report](07-Publication-Verification/FILE_BY_FILE_RIGHTS_REVIEW.md) distinguishes adaptation from original integration and remaining uncertainty.

One assembly file, probe_v3.S, is withheld because its manufacturer-reader re-emission provenance remains unresolved. The successful unlock coordinator and extraction source are included; full LK regeneration and live-runtime portability are not claimed. Manufacturer firmware/DA/LK binaries and private inputs are excluded. See [runtime limits](RIGHTS_AND_RUNTIME_LIMITATIONS.md).

No blanket repository license is imposed. Independent code has no newly selected general reuse license, so this is not advertised as a uniformly open-source or complete integrated executable product. No executable/firmware release is included.

The full extraction guide,13-stage unlock guide, prerequisite chapter, failed experiments and original-LK persistence evidence remain intact. The latest saved factory-system restore and the owner's Ooredoo slowdown clarification are documented separately from the unresolved Arabic-system shutdown.

Repository URL placeholder: `https://github.com/YOUR_GITHUB_USERNAME/ZTE-MF904Q-Reverse-Engineering` (not published). Repository creation, upload, Public visibility, every Release and every community post require distinct explicit approvals. Login completion is not publication approval.
