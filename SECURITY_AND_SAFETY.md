# Safety and publication boundaries

The guides are a historical reconstruction, not authorization to operate a reader's device. Unlocking can erase user data and changes security state. LK or Preloader mistakes can prevent boot and may destroy the transport required for recovery. A complete backup is not proof of an available rescue path.

The extraction source reads flash but uploads the original DA into RAM: “read-only” refers to flash persistence, not zero execution or zero RAM/MMIO writes. The unlock path can erase userdata and writes security configuration through the original LK flow. These are different operations with different approvals and risks.

Use only an owned or explicitly authorized device. Never use these materials to access someone else's data, credentials or accounts. Do not alter device identifiers. Preserve NVRAM/NVDATA and calibration. Do not relock an altered device as a generic recovery step. No automatic retries, resets, unlocking, flashing, formatting or cache deletion are supplied as a publication shortcut.

This documentation-first allowlist omits all41 historical source snapshots pending the rights decision, as well as original firmware/DA inputs, active approval tickets, private identity references and site-specific dependencies. Do not recreate missing approvals from examples. Obtain binaries from your own legally obtained matching package or authorized backup; if provenance or redistribution rights are unclear, stop. There is no universal download URL established for the exact factory DA.

For suspected documentation mistakes, open an Issue containing redacted output, file hashes and the exact build. Do not upload raw eMMC, seccfg, NVRAM, userdata, tokens, SIM data or a serial-bearing screenshot. There is no private security-report mailbox configured in this local candidate.
