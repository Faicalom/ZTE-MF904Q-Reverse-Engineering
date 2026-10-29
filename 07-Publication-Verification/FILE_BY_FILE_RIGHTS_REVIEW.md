# File-by-file source provenance and distribution review

51 files were examined: all41 previous snapshots plus10 matching DA dependencies.50 sources may be included under the scoped terms below; one assembly file is withheld. No firmware or upstream executable is included.

**Important:** authorship category and distribution terms are different columns. A project-written coordinator linking adapted DA code is not labeled copied merely because the combined DA program is distributed under GPLv3. Independently authored native Fastboot, Windows/ADB and offline utilities are not automatically relicensed. The owner authorized publication; no new standalone reuse license is selected for independent files. Do not advertise all repository contents as uniformly open source.

The examined upstream is the exact locally preserved git revision cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3. Direct adaptation/source-informed flow is identified in the rationale; the comparison is not a claim of verbatim copying or a legal determination. No-match results are not proof that a file was never copied from any external source.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/backup_core.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_DA_ADAPTATION_AND_PROJECT_ORIGINAL
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `517ec0081516677f6da95ceb6ff45f3514b72dbe43889d55487fc9cc8f27f8cd`

read_range: DA2 read/region/ACK/checksum sequence; gpt_header, entries, Image: independent CRC/bounds/checkpoint implementation.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/inspect_preloader.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_FORMAT_INSPECTOR
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `ec838a0231df402dd1d507b80c8bc25107f70ee664e3ad77c67528bed2c0ecfb`

Project-specific bounded FILE_INFO/EMI scanner over an owner-supplied saved Boot1; no mtkclient imports or copied code sequence established.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/open_private_archive.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_OFFLINE_UTILITY
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `595809f8f42229c5c4c2bb92ed5ed5b203bbea022c96e0f5e46c917c1989f68d`

Project encrypted-backup opener and masked password prompt; standard ctypes/filesystem use; imports project private_crypto, not mtkclient.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/private_crypto.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_OFFLINE_UTILITY
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `24948502aebbeca48f3a9125203c7ee4ce6d836ead88d7a7917019f3ba319590`

Project MF904QENC1 archive framing, streamed AES-GCM, round-trip verification and cleanup; cryptography is an external separately licensed library.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/run_stock_backup.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `c54ce82cf1e4d3cf1a3b89736aaeefb77c44af2850617d6508816e7dbd40ee0c`

Original manifest/identity/approval/backup coordinator; imports and integrates the adapted DA pipeline. GPL distribution scope is program integration, not a claim it was copied.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_STOCK_FIRMWARE_BACKUP/Tools/verify_backup.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_OFFLINE_UTILITY
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `2a72291ad4c0819d1b12c996dd767661577283a88d3d665bac77258d0742dc52`

Local-only exact size/hash/GPT/slice-overlap verifier; no DA execution/import; GPT format facts do not establish code derivation.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/audit_legacy_candidates.py

- Decision: **INCLUDE_SOURCE**
- Origin category: UPSTREAM_INFORMED_DA_FORMAT_IMPLEMENTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `2359bff0d9177a281af9e8e3234ee02410ca2a2e847fd38c9cf506a2d477d855`

Own bounded parse_entry and eligibility logic explicitly tied to mtkclient DA container revision; GPL retained conservatively for upstream-informed loader-format implementation; no claim of verbatim copying.

Upstream references: `mtkclient/Library/DA/daconfig.py`, DA lines34–74.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/da1_probe_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_DA_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `87397658dcf29d51ea10b12fcf579aa81e1019c653699c95fec2f008815e43fc`

D7 SEND_DA/echo/upload checksum and D5 jump plus legacy initial storage sequence follow upstream; comments identify audited upload_data pacing. Project adds bounded failures/events and refuses further stages.

Upstream references: `mtkclient/Library/mtk_preloader.py`, send_da lines1090–1125, `mtkclient/Library/mtk_preloader.py`, upload_data lines999–1036, `mtkclient/Library/mtk_preloader.py`, jump_da lines708–735, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, brom_send lines907–940.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/da2_probe/da2_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: EXPLICIT_UPSTREAM_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `c8b9b743d27586ea511262eac1f01e31979eb15a1ef10f6a0f5e2d08e8110f3e`

Docstring explicitly cites mtkclient dalegacy_lib brom_send/read_flash_info/readflash; geometry framing, pacing, branch/layout and read sequence map to that source; project bounds/checks remain modifications.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, brom_send lines907–940, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, read_flash_info lines526–552, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235, `mtkclient/Library/DA/legacy/dalegacy_flash_param.py`, Legacy_EmmcInfo lines120–159.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/da2_probe/run_da2_probe.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `748a80e003af2310c7ecf2ef82cc11f378c35a14b06a50a8a44f28699ce9dea8`

Own one-session approval, upload integrity/logging and callback orchestration linking adapted DA1/stage2/DA2 modules.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/identity_queries.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_QUERY_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `41d750d84b8aa5bbc0d8cad5e3d400caf87b73fffdbcba2994e1b7b800c088f1`

FC/D8 message layouts and flag interpretation follow upstream queries, with explicit source comment; strict length/status/error and event behavior added locally.

Upstream references: `mtkclient/Library/mtk_preloader.py`, get_hw_sw_ver lines928–930, `mtkclient/Library/mtk_preloader.py`, get_target_config lines675–706.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_UPSTREAM_HANDSHAKE_AND_PROJECT_PARSER
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `79eb3bcbe33208a0f28a57177b4d44d4e734c8745e0042b03033572ad5c320ff`

Complement-byte/restart behavior documented against upstream; READY incremental parser, bounds, recording and failure policy are project additions. GPL retained on the mixed module.

Upstream references: `mtkclient/Library/Port.py`, run_serial_handshake lines52–85, `mtkclient/Library/Port.py`, run_handshake lines128–173.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/readiness_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `09b538fb1a66f46b743788aadc2d2a5019ea9aff0b2f701d10e24bc750e86ce9`

Project receive-driven state/deadline/fresh-READY policy built on protocol.HandshakeParser; no verbatim upstream implementation established. Covered here as integrated DA-program component.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/run_da1_probe.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `41b3215a60e8dd8b40ee7c155a3c2d386904172eeb0d59a717e8f303546feb80`

Project exact-binary identity/region gating and log wrapper around adapted DA1 source; not an upstream mtkclient CLI copy.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/stage2_probe/run_stage2_requirements.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `1ed611664e1da1e50e2c093c3c63bf558d90076115d7902391ed04f0f388eb37`

Project stage-specific callback and stop-before-EMI policy over adapted DA1/config source.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/stage2_probe/stage2_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_DA_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `c707882068483bb76bc6604ec67253df9de5c3eccb564788d9773db36e9b04e8`

Original FE/FF versions, exact stage2 field order, 350ms delay and BC3/BC4 parsing follow upstream; project adds strict count/status bounds and stops before EMI.

Upstream references: `mtkclient/Library/mtk_preloader.py`, get_blver lines664–673, `mtkclient/Library/mtk_preloader.py`, get_bromver lines657–662, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, set_stage2_config lines228–403.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/wait_preloader.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_PROJECT_PNP_AND_UPSTREAM_HANDSHAKE_PACING
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `b2966dfb1503c828aedf6fe2e2bba8daad8af9b5e664480add2b1fef8a3119ba`

Project Windows CM notification/COM selection/logging code; handshake/FD pacing explicitly derived from audited upstream mtk_cmd and linked adapted query/parser modules. GPL applies to this combined module, not a claim Windows PnP was copied.

Upstream references: `mtkclient/Library/mtk_preloader.py`, get_hwcode lines880–882, `mtkclient/Library/Port.py`, mtk_cmd lines210–229.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 01-Firmware-Extraction/src/MF904Q_Wait_Modem/windows_usb.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_WINDOWS_METADATA
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `7c25cae4f56c7a9add06cfb03ee6ee9f80c781a48c3311d54531518cb43a2705`

Project ctypes SetupAPI devnode enumeration. Public Windows ABI declarations and device VID/PID facts are distinguished from mtkclient implementation; no source copying established.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/limited_da.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `59580ee2558e699fd8c363d5700fa4b0d229668706dca7f12d380048798fdba0`

Own exact transcript Guard, private identity binding, one-attempt and phase orchestration using adapted modules; additional source dependencies must accompany this file.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DETACHED_FROMDEBUG_PREP_20261011/MarkerCore.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_ADB_SUPERVISION
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `5bfe09780744fded359828e5a10b9e9fb537dd14980f132dda0414c91df98cce`

Project detached-session marker/nonce/timeout/ADB framing and completion checks. The original OEM broadcast is a documented command, not copied service implementation.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DETACHED_FROMDEBUG_PREP_20261011/ObserverCore.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_WINDOWS_ADB_OBSERVATION
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `52cbe575486d2d1155c599f440ab41c02bb029ab1bacb17209073f7905adf7d9`

Project Windows device/ADB record parsing and identity matching; no mtkclient code or imports established.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DETACHED_FROMDEBUG_PREP_20261011/Program.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_ADB_SUPERVISION
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `d3150a2340582e5ec8563b35078c4c886950304bcb3ff7cadd24c254211bcef6`

Project controlled monitor/approval/capture glue for the detached OEM action; not a mtkclient transport.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/BUILD_MANIFEST.json

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_GENERATED_FACTUAL_BUILD_METADATA
- Distribution terms: FACTUAL_METADATA_NO_NEW_CODE_LICENSE
- Reviewed input SHA256: `0753e4aada0f18b23d1e7e3e12f590b10065cc59d88e0bc841a6cab46576535b`

Patch locations, symbols and hashes are provenance facts; manufacturer old_hex excerpts were already removed. Not a license to redistribute resulting firmware.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/build_v3.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_PATCH_BUILD_AUTOMATION
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `565a67b59893521eb6cec115def58d48121316dfac7b3988d23fe9f9c3ec2e2c`

Project exact-hash/bounds/LLVM build automation. Requires excluded owner-obtained factory LK; generated LK/ELF/fragments are not distributed. Assembly dependency held separately.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/capture.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_PROCESS_CAPTURE
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `729c9da8f85e15e7bb321b6c1a7cf6a65f5f55479e07e05474b288c726d61b9c`

Own dual-pipe EOF/process-exit/capture-error/timestamp helper; no USB/DA or upstream code import.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/final_unlock_v3.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_NATIVE_FASTBOOT_COORDINATOR
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `8ab919ca59c0f0a5397939a156d0e9494ea15d5e76ec0fc3c8f3d9aa4a96116d`

Own approval/diagnostic/hash/one-shot/manual-confirmation coordinator invoking separately obtained fastboot; no mtkclient imported. Tool-specific successful original source is preserved after identity/path redaction.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/lk_da_session.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `9f9b30b56fd8ba33f2e7ff859383b0848cf4b7192552d541c6bf4682e1b878b4`

Own exact LK-only read/write/readback session composed with the adapted limited_da transport; distribute matching source dependencies, not just an executable.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/lk_install_policy.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_PROJECT_GUARDS_AND_SOURCE_INFORMED_DA_FRAMING
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `c52dd318034ab50da6067150a515af51ff8fe1193916bab19183b9122076119e`

Own pinned image/once-only/Windows mutex/approval checks; read_frames/write_frames/ACK/checksum express the legacy DA transport and are distributed in its GPL-covered program.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, sdmmc_write_data lines982–1041, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, writeflash lines1089–1091.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/lk_probe_entry.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_NATIVE_FASTBOOT_DIAGNOSTIC
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `dff98bd4b1c7291a5f9fc52520e144c40a22309bd2feea947882e838531fde73`

Own identity/entry/capture/parser/ticket control for one measured native fastboot request; no mtkclient import.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/probe_v3.ld

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_LINKER_MAPPING
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `de365994bf0ea14fbabb1880fe75664e3adfa226034e2429361af5d23036c050`

Project linker sections/asserts and original-function numeric offsets; no manufacturer executable bytes. Does not establish rights to an assembled full LK.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/probe_v3.S

- Decision: **WITHHOLD**
- Origin category: UNRESOLVED_FACTORY_READER_REEMISSION
- Distribution terms: WITHHELD_RIGHTS_UNRESOLVED
- Reviewed input SHA256: `c0f2d3f7b73777c4dfc93b14c6fcaa7b5d07170343aebff9df45f8cc65b5fa39`

capture_config/capture_raw re-emit original LK load/bit-extraction instructions alongside project instrumentation. Source similarity to mtkclient cannot clear manufacturer provenance; exclude this one assembly file pending separate rights determination, without excluding the other tools.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/response_gate_context.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_MEASURED_RESPONSE_PARSER
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `5875db189b117a5ea6a46d930a24511651b316486e59378c89896b7ecbd8fb6f`

Own exact V3 markers/order/caller/read-present/result consistency checker for this project instrumented LK; no mtkclient imports.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_GATE_CONTEXT_PREP_20261012/response_v3.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_MEASURED_RESPONSE_PARSER
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `5875db189b117a5ea6a46d930a24511651b316486e59378c89896b7ecbd8fb6f`

Historical duplicate parser of the same project-specific gate-context response; preserve filename/version provenance, not an independent new protocol author claim.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_OEM_SETTER6_CONTROLLED_PREP_20261011/Controlled.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_OEM_PERMISSION_COORDINATOR
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `0bf829a8c930f3af3ed88beebdea969e392ed76ac8ba35d93c3edaa4d7749ab4`

Own bounded identity/UID/monkey/once-only setter/getter orchestration. Binder transaction numbers were recovered from this firmware; numeric interface facts are not a copied framework service body.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_OEM_SETTER6_CONTROLLED_PREP_20261011/IdentitySupport.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_WINDOWS_ADB_IDENTITY
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `a13c2a325985dc7289faab8e57cf00f0d7cfb3d5d958f77ab7bfb0a45d879d41`

Own Windows SetupAPI and ADB record bindings; standard .NET/Windows API declarations, no mtkclient imports.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_OEM_SETTER6_CONTROLLED_PREP_20261011/ProtocolIdentity.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_ADB_RESPONSE_CAPTURE
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `8d10ae9d649843d949a9c468073979396ab6d53345116db515517b380973880d`

Own TCP ADB-server framing and complete response/nonce/error policy; uses documented ADB framing rather than mtkclient.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_OEM_SETTER6_CONTROLLED_PREP_20261011/RestrictedLogs.cs

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_FILTERED_LOG_ANALYSIS
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `cb27a2910bebd3d3107de907e3d75a531527bfe2e5e397c1582f13bd43ee04dd`

Own regex and canonical-message selection over PDB service logs; short observed log labels do not include a vendor implementation.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_THIRD_UNLOCK_PREP_20261012/core.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_IDENTITY_AND_ONCE_GATES
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `bc9312998f42c920a1d33a0ce0cc202810b4c182a8f07678817328e6a866b218`

Own pure USB path/selector/lock/response guards; private per-device serial fingerprint replaced by nonmatching placeholder.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_THIRD_UNLOCK_PREP_20261012/entry.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_NATIVE_MODE_ENTRY
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `d2553499210c3b438073523e16d94472f03b8e5c40bc125932d4c55cf99c654c`

Own Windows notification/identity/once-only native FASTBOOT entry and pinning of independent Android fastboot executable; not a mtkclient DA loader.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_THIRD_UNLOCK_PREP_20261012/entry_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_PRELOADER_MODE_PARSER
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `55099c9336a4901592561d255530af72663db4de6798318bc164f66e966a85f6`

Own incremental READY/FASTBOOT/TOOBTSAF state machine driven by observed native entry; not the mtkclient A0 handshake.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_THIRD_UNLOCK_PREP_20261012/usb_metadata.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_WINDOWS_METADATA
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `12ba438b0ad9a68176e2d845ec2f817f0e8f5bd6b0173b2c095033dd0b6072c5`

Own ctypes present-devnode/physical-path/identity summary; no mtkclient import or established copied source.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/backup_core.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_DA_ADAPTATION_AND_PROJECT_ORIGINAL
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `ef0a8470926599205b9f27819ba94590f2e4c8a63c06d4eca721a5f006c21e0b`

read_range: DA2 read/region/ACK/checksum sequence; gpt_header, entries, Image: independent CRC/bounds/checkpoint implementation.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/da1_probe_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_DA_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `ea0772f4a27b7e72d571a9d60e067c8cddfe2e380f4f127e4433e5a6b98c7358`

D7 SEND_DA/echo/upload checksum and D5 jump plus legacy initial storage sequence follow upstream; comments identify audited upload_data pacing. Project adds bounded failures/events and refuses further stages.

Upstream references: `mtkclient/Library/mtk_preloader.py`, send_da lines1090–1125, `mtkclient/Library/mtk_preloader.py`, upload_data lines999–1036, `mtkclient/Library/mtk_preloader.py`, jump_da lines708–735, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, brom_send lines907–940.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/da2_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: EXPLICIT_UPSTREAM_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `38c0e0b9675bf908a8287f3d095b2cc21e8a6c58bb8b358297f744dd05d64157`

Docstring explicitly cites mtkclient dalegacy_lib brom_send/read_flash_info/readflash; geometry framing, pacing, branch/layout and read sequence map to that source; project bounds/checks remain modifications.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, brom_send lines907–940, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, read_flash_info lines526–552, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235, `mtkclient/Library/DA/legacy/dalegacy_flash_param.py`, Legacy_EmmcInfo lines120–159.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/identity_queries.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_QUERY_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `5d0e33b6e813ee20888fd5b55a563c88a50c1add97ce95f8b01e00dccb3d9440`

FC/D8 message layouts and flag interpretation follow upstream queries, with explicit source comment; strict length/status/error and event behavior added locally.

Upstream references: `mtkclient/Library/mtk_preloader.py`, get_hw_sw_ver lines928–930, `mtkclient/Library/mtk_preloader.py`, get_target_config lines675–706.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_UPSTREAM_HANDSHAKE_AND_PROJECT_PARSER
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `56df194f9473f1d2224a1fef72d204cf7d46dcf2e7c96f2dec613f0c27fb6119`

Complement-byte/restart behavior documented against upstream; READY incremental parser, bounds, recording and failure policy are project additions. GPL retained on the mixed module.

Upstream references: `mtkclient/Library/Port.py`, run_serial_handshake lines52–85, `mtkclient/Library/Port.py`, run_handshake lines128–173.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/readiness_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_GPL_DA_PROGRAM_COMPONENT
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `7284a9d1dfe5daafc92d2f3a2f714517af8108ce3e9a7ad7c067ea3337c6ad3b`

Project receive-driven state/deadline/fresh-READY policy built on protocol.HandshakeParser; no verbatim upstream implementation established. Covered here as integrated DA-program component.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/stage2_protocol.py

- Decision: **INCLUDE_SOURCE**
- Origin category: SOURCE_INFORMED_DA_ADAPTATION
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `af96b3986ad6177e35ff076bb56c5a4afcd007bbf3f667d2a72dbb28ba40c9ce`

Original FE/FF versions, exact stage2 field order, 350ms delay and BC3/BC4 parsing follow upstream; project adds strict count/status bounds and stops before EMI.

Upstream references: `mtkclient/Library/mtk_preloader.py`, get_blver lines664–673, `mtkclient/Library/mtk_preloader.py`, get_bromver lines657–662, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, set_stage2_config lines228–403.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/usb_metadata.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_WINDOWS_METADATA
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `bf050a881cee704ec718e65e85525831e51ec841827319aa29ecee865b250b0e`

Own ctypes present-devnode/physical-path/identity summary; no mtkclient import or established copied source.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/policy.py

- Decision: **INCLUDE_SOURCE**
- Origin category: MIXED_PROJECT_TRANSCRIPT_GUARDS_AND_DA_FRAMING
- Distribution terms: GPL-3.0-only
- Reviewed input SHA256: `96684dca6a4ff871af06c0f6158ea1e67bcd58fa53e64757f814455971ced57f`

Own allowlist/order/one-attempt state machine with exact source-informed DA message transcript and config module integration; distribute as covered DA-program component.

Upstream references: `mtkclient/Library/DA/legacy/dalegacy_lib.py`, readflash lines1131–1235, `mtkclient/Library/DA/legacy/dalegacy_lib.py`, brom_send lines907–940.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

## 02-Bootloader-Unlock/src/MF904Q_DA_HANDSHAKE_FIX_20261012/compare_private.py

- Decision: **INCLUDE_SOURCE**
- Origin category: PROJECT_ORIGINAL_LOCAL_STATE_COMPARISON
- Distribution terms: NO_NEW_STANDALONE_LICENSE_SELECTED
- Reviewed input SHA256: `3245c3e33bf08fdc3074e7841da8446b728154b4618924a89f5b6937d336c8f1`

Own byte-span/checksum/state summary over caller-selected private files; no dump or device value embedded; not a vendor security configuration generator.

Nontrivial identical-line matches in selected upstream paths: 0. This is supplementary evidence only.

