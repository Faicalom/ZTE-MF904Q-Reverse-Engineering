# Complete firmware extraction guide: the actual MF904Q investigation

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

## 1. How to read this guide

This records what was done on the examined device, including the failed precursor. It does not ask the reader to attach hardware now. Commands marked **historical** were recovered from saved source or launchers; an illustrative path/selector is explicitly identified. Raw device identity values, manufacturer binaries and active approval files are absent from this publication candidate. A command can be historically correct and still be unsafe or incomplete on a different machine.

The primary sources are the failed backup result, `MF904Q_Wait_Modem/PROTOCOL_REVIEW_AR.md`, its DA2 live result, `MF904Q_STOCK_FIRMWARE_BACKUP/FINAL_REPORT_AR.md`, the stock backup runner/core, its manifest and its independent verifier. [The provenance index](../07-Publication-Verification/SOURCE_PROVENANCE.json) records fingerprints of reviewed files; the public evidence folder contains selected non-identifying results. The complete private archive was not copied into this repository.

## 2. Identify the device before discussing transport

The recorded board was WF904_V6.0 and the modem was identified as MF904Q/M19-E. The later Android identity is `mf904q_v4_35m_lwtg`, Android 6/API23, build `MF904Q-6.0-1-6735WM_LCD_20240123`. Transport queries returned hardware code 0x0335 and version 0x0000. DA geometry ultimately reported 512 MiB DRAM and 3,825,205,248 bytes of eMMC User space. These independent layers matter: a product label, an Android property and a Preloader response do not establish exactly the same fact.

The stock backup took place before the later bootloader-unlock experiments. Its report explicitly says it sent no unlock, exploit, flash-write, flash-erase or identifier-change command. Therefore a previously unlocked bootloader was not a demonstrated prerequisite for this extraction path. It is incorrect to rewrite the chronology as “unlock first, dump later.”

Never publish raw CID, Windows USB instance paths, IMEI, SIM identity, full userdata or NVRAM to demonstrate matching. The historical runner compares private device records locally. A new device requires its own identity review; deleting that comparison is not a portability fix.

## 3. Prepare the Windows host

The documented host was Windows 11. The first effort discovered that the Preloader driver was missing. Installing MediaTek VCOM 3.0.1504.0 resulted in a healthy Windows device, then COM11; the later successful session used COM12. COM numbers are assigned by Windows and are not permanent device identifiers. Do not hard-code COM12 as proof of MF904Q identity.

The source uses VID/PID detection, then bounded opening and identity/geometry checks. It preloads libraries and the port-detection machinery before asking for connection. The historical review specifically rejected waiting for a friendly name or reading five banner bytes before beginning, because that could waste the short Preloader window. The exact electrical attachment time was not measured; host monotonic/UTC observations are not oscilloscope timestamps.

The following are **new, local-only inspection commands**, not reconstructed device commands:

```powershell
Get-Command python
python --version
Get-FileHash -Algorithm SHA256 -LiteralPath .\your-legally-obtained-DA-file
Get-PSDrive -PSProvider FileSystem
```

They neither prove historical version compatibility nor authorize live access. The record does not establish a complete Python dependency lock. The launcher expected the earlier project's virtual environment; the proprietary DA input and private successful-reference JSON must already exist. Inspect [requirements](REQUIREMENTS.md) before attempting to reconstruct that environment.

## 4. Understand why the first extraction failed

The earlier `MF904Q_Original_Firmware_Backup` result was BLOCKED: no firmware extracted, no geometry, no GPT and no DA upload. Windows driver health was fixed, but receiving the automatic `READY` banner was not handshake success. One experiment sent A0 and never received its expected complement 5F. Another mixed READY characters with repeated A0 transmissions and recorded 5F then A1, not the full complementary response sequence.

The saved bytes did not have enough timing/provenance to prove that A1 was the response to 0A. The project therefore did not call this a security rejection or unsupported chip. The protocol parser was repaired and replayed locally. Receiving an unsolicited banner cannot substitute for four correctly paired handshake stages.

The reviewed sequence was A0 / 0A / 50 / 05 with responses 5F / F5 / AF / FA, one stage at a time. Extra bootstrap behavior from a different USB transport was not copied blindly into COM. Initial handshake limits and later bounded receive-driven fixes differed; [history](EXPERIMENT_HISTORY.md) keeps these versions separate rather than presenting the earliest proposal as the final implementation.

## 5. Prove the identity query before uploading a DA

After a complete handshake, FD was sent once. Its echo and two big-endian words were parsed as HW code and HW version, not “status.” The source/review included the required short pacing for the identity exchange. Subsequent protection/version results and DA selection were checked against saved expectations. There was no generic “try every MediaTek payload” loop.

Stop if responses are short, echo differs, hardware identity changes, phase deadlines expire, or the source binary's pinned hash fails. Do not continue to DA upload on READY alone. The complete literal command line of every intermediate identity experiment is **NOT RECOVERABLE FROM SAVED EVIDENCE** reviewed here; the source-level wire sequence is available and must not be passed off as an independently recorded terminal invocation.

## 6. Load the original DA stages into RAM

The successful session was `20261009_104835_647022`, on 9 October. Original unmodified DA1 executed, the Stage 2 configuration returned zero, and Region 2 from `MTK_DA_V5.bin` was sent to RAM at 0x40000000. Fifty-five upload packets and the final acknowledgment were accepted. The transmitted DA2 digest was checked against the audited candidate: `4c71c41280414374ef704655dee944a430a701f879489b87188a2e1fc70b0e57`.

No EMI blob, patched DA or exploit was sent in this successful extraction. Finding FILE_INFO/EMI later inside Boot1 does not mean it was required or used for this upload. Similarly, executing DA in RAM is not a flash write, but it does execute code and configure hardware. Do not describe the complete transport as “no changes anywhere.”

The live result `DA2_FIRST_SECTORS_READ` and independent `REAL_DA2_FLASH_INTEGRITY_PASS` established more than an ACK: actual flash-sector bytes were obtained and checked. A DA that only uploads successfully is not yet a firmware extraction.

## 7. First sectors and storage geometry

DA2 reported User 3825205248 bytes, Boot1 and Boot2 each 4194304, RPMB capacity 4194304 and DRAM 536870912. The first 34 sectors (17408 bytes) included protective metadata, the primary GPT header and its entries. The CID manufacturer/product interpretation used a word-byte-order correction and CRC7 validation; the unique CID is withheld. It established Kingston/S10004 as the documented interpretation, not an exact full memory part number.

The logical 512-byte sector was supported by GPT placement and read behavior. The report explicitly says DA2 did not provide that size as a standalone field. Physical-sector size, CSD and EXT_CSD were not established. RPMB capacity was reported but its contents, keys and counters were not read.

## 8. Expand into a complete, bounded backup

The actual successful backup launcher was `MF904Q_STOCK_FIRMWARE_BACKUP/START_STOCK_BACKUP.bat`, calling `Tools/run_stock_backup.py` with the prior virtual-environment Python. Its body forwards `%*` rather than silently selecting private scope. The recovered script has a `--private` option and requires a separate, identity-bound private approval and encryption password before connection. The saved report proves private scope completed; an exact typed command line for its final invocation is **NOT RECOVERABLE FROM SAVED EVIDENCE** reviewed here. Do not invent one.

Historical launcher action, expressed without the original user's path:

```text
START_STOCK_BACKUP.bat
  -> prior virtual-environment Python -u Tools/run_stock_backup.py [forwarded arguments]
```

This is a launcher reconstruction, not a portable invocation. The source retains the complete control flow. The public package deliberately omits personal approvals and successful-session CID references; copying a sample JSON with `approved=true` would not reconstruct verified identity.

## 9. Validate GPT, twice

The runner verifies the primary header CRC, table CRC, bounds and entries, then reads the backup header at the primary's recorded alternate LBA. It checks that the backup points to LBA1 and agrees on disk geometry, usable range, entry count/size and disk GUID. It reads the padded backup array, checks its CRC and requires the entry bytes to match the primary table.

The actual backup table begins at LBA7470080 and its header is LBA7471103. There are 23 partitions. The primary prefix is 17408 bytes; the meaningful 23×128-byte entry array is 2944 bytes, while storage reads use sector alignment. Do not mistake those different lengths for truncation. [The full table](PARTITION_LAYOUT.md) lists real offsets, output names, sizes and firmware reference digests. Private hashes are withheld intentionally, not “unknown.”

## 10. Independent transport stability before long reads

Before full extraction, the runner rereads the initial prefix independently and requires byte equality. It then reads a 256 KiB LK range twice and requires equality. These are actual repeated device reads, distinct from hashing one host file twice. Their success supported proceeding but did not prove every future transfer would succeed.

No unbounded reconnect loop is the remedy for mismatch. A short transfer or differing identity stops the current operation. Checkpoint resume is a separate controlled process and must preserve which blocks were accepted. Do not concatenate partial files by assumed position.

## 11. Actual DA2 range operation

There was no generic terminal `dd` command. The project called `backup_core.read_range(send, receive, region, offset, length, region_size)` within a guarded DA session. The core limits regions to 1, 2 or 8; disallows RPMB; requires sector alignment, positive length, at most 1 MiB, and valid bounds.

The recovered operation sends USB-status query 0x72, requires ACK5A and an accepted speed status; sends partition command 0x60 and the selected region with ACKs; then sends D6, 0C, 02, big-endian 64-bit offset and length, and a big-endian 32-bit 0x100000 transfer size. After READ ACK it receives exactly the range and a two-byte big-endian additive checksum. Only a matching `sum(data)&0xFFFF` is acknowledged with 5A.

This sequence is a source-level protocol description, not permission to transmit isolated bytes from a terminal. It depends on the original DA state and preceding setup. A 16-bit checksum detects transfer errors but is not cryptographic authenticity. SHA256 and size checks are additionally applied to the saved files.

## 12. Keep the backup classes distinct

* **Seven firmware partitions:** lk, boot, recovery, logo, tee1, tee2, system. The runner orders these by size/offset, not by an assumed Android block-device name.
* **Sixteen other GPT partitions:** extracted only in the approved private scope, including userdata and calibration/security-bearing ranges. Their presence does not grant a right to redistribute them.
* **Boot1 and Boot2:** separate eMMC hardware regions, each 4 MiB. They are not `/boot` and `/recovery`, and their bytes were not identical.
* **Full User area:** exactly 3825205248 bytes, including all GPT partitions and inter-partition gaps. It is not the entire physical eMMC including every special region, and excludes RPMB.
* **System image:** a 629145600-byte partition image; much smaller than User and insufficient as a complete device backup.
* **Preloader-derived slices:** FILE_INFO at Boot1 offset2048 and an EMI slice were extracted locally after reading Boot1. They are derived files, not extra flash reads and not a separately verified executable rescue image.

## 13. Save progressively and resume conservatively

`Image` uses partial output and durable checkpoint metadata. A new accepted block has its range/checksum/content identity recorded; a resumed read must match the same device binding and validate the existing file state. Exact reads reject short data. `atomic_json` flushes and fsyncs a temporary metadata file before replacement; do not describe that as a universal power-loss guarantee for the parent directory.

The runner updates a manifest row with expected/actual size, completion, SHA256, source and errors. On failure it records `BACKUP_STOPPED`, with no automatic reset, retry or flash write. The public code is an inspection snapshot; no newly packaged live attempt was run to validate reconstructed dependency paths.

## 14. Verify on the computer independently

The final historical check returned PASS for 31 principal files: 23 partitions, two boot regions, one User image and five GPT files. It checked precise sizes, hashes and checkpoints, both GPT CRCs and equal entry arrays, then compared all 23 standalone partition files with their corresponding slices of the complete User image. Every comparison matched. See [verification detail](BACKUP_VERIFICATION.md).

Android image structure and the validity of ext4 metadata are separate from transport correctness. A hash-matched dump can preserve an already corrupt filesystem; conversely a parseable ext4 image can be an incomplete or wrong-build backup. The historic `system` was later inspected and used in controlled rebuild/restoration work, but no universal boot guarantee follows from its header.

## 15. Protect private storage and preserve limitations

The final report records AES-256-GCM archival, verified decryption and SHA256 comparison of all 63 files inside that private archive. Keys and passwords were not stored. Original raw material remained in a restricted NTFS location. These facts do not authorize publication of the encrypted archive: its data and logs remain private even if encrypted.

The original extraction completed without a flash-restore test. Do not rewrite the 9 October report to claim restoration was proven then. Later LK restoration and system readback work are separately dated evidence. There is no verified rescue from a destroyed Preloader, no RPMB clone and no complete EXT_CSD boot configuration backup. Preserve these gaps alongside the successful extraction.

## 16. Reader stop checklist

Stop before a live reconstruction if exact identity, matching original DA, input provenance, available space, dependency versions, privacy handling or approval scope cannot be established. Stop during a read on timeout, short response, invalid ACK/checksum, changed geometry, GPT mismatch or unexpected writable operation. Do not turn a research guide into a tool that retries silently. A future portability contribution should add explicit tests and a reviewed configuration mechanism, not remove the historical safety bindings.


## Additional archival version evidence recovered from F

The preserved offline check records Python3.13.14 x64 and pyserial3.5; the unlock serial manifest also pins pyserial3.5. The10October entry report pins fastboot37.0.1-15733141, SHA256b2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86. This updates earlier missing-version notes: that Fastboot version is recoverable. A complete environment lock across every historical extraction attempt remains unestablished. See the prerequisite chapter in the unlock folder for exact evidence distinctions.
