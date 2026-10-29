# Complete unlock guide: evidence-led reconstruction of the MF904Q result

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

## Scope, evidence and reproducibility

This guide intentionally preserves the research sequence instead of compressing it into a generic five-step MediaTek unlock. It explains how the successful path was identified, why earlier attempts did not prove success, which measured values matter and how the original LK later confirmed persistence. It is tied to one board/build and its private identity records. It is not a guarantee that another modem can repeat the result.

**Do not execute this guide as a live session from the publication ZIP.** Firmware-derived binaries, the original DA, active approvals and device identities are absent by design; dependency/legal gates remain. Source commands below are recovered from historical files. `<VERIFIED_SERIAL>` and `<PINNED_FASTBOOT>` are redacted metavariables, not literal historical selector bytes. A shell command is not silently substituted when the historical step was a launcher action or an interactive token.

The decisive sources are the V3 failed-attempt reports, corrected-V3 disassembly/report, gate-context `REPORT_AR.md` and `UNLOCK_SUCCESS_REPORT_AR.md`, original response bytes rendered in `evidence/`, the actual `final_unlock_v3.py`, and the 13 October final-verification report. Their fingerprints and public derivations are recorded in the [provenance index](../07-Publication-Verification/SOURCE_PROVENANCE.json).

## Required earlier chapters — transport and OEM enablement

Read [the complete Android/OEM/Fastboot reconstruction](PRE_UNLOCK_ANDROID_AND_FASTBOOT.md) before the staged LK procedure. It preserves the exact original broadcast, Binder setter/getter, permission proof, and FASTBOOT/TOOBTSAF transition. These were distinct successful stages and must not be skipped or reduced to “enable OEM unlocking.”

## Before the unlock: preserve what was actually known

The original lock state was observed through a complete `getvar unlocked` response containing `no`. Root access in Android, a working SIM, ADB availability, a diagnostic command or a changed image hash cannot substitute for this query. The backup had already been extracted on 9 October without unlocking. Thus firmware extraction and bootloader unlocking were separate achievements, not one merged program.

Factory LK was 524288 bytes and its known hash was `07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596`. The eMMC LK range is LBA58368–59391, byte offset29884416, in User region8. These values were verified against GPT and identity, not taken from a similar model. Changing LK can prevent normal boot or Fastboot; changing Preloader may remove the available recovery transport. The project did not establish guaranteed recovery from every such failure.

The historical original seccfg was observed as zero-filled. A constructor in LK could build a V3 default structure in RAM, but its existence alone did not prove it would be invoked or committed. No random seccfg image was generated and written to claim success. After later unlock attempts reached erase/commit, absence of a write marker was not evidence that userdata remained intact. The original flow can erase userdata before a later failure.

## Discovery: how the boot chain was investigated

Preloader, LK, command registration, FRP, the hardware-key path, security configuration and constructor/crypto/commit were analyzed separately. Loading DA into RAM did not prove an arbitrary LK could run from RAM with correct DRAM/MMU/cache/stack/bootargs context. In particular, the examined LK's expectations included register context such as R4. A standalone RAM LK loader was not validated, so it was not substituted as a claimed safe method.

The research linked Preloader security config0x22 and hardware bit1=0 to an early return before a separate RSA path. This was a build-specific analysis, not a general statement that signatures never matter. The practical evidence came later: the exact derived LK was installed with full readback and actually ran. Neither observation means any patched LK will be accepted.

LK offsets here are offsets in the analyzed file. Runtime code base is 0x41DFFE00; Thumb pointers and call-return addresses must be interpreted accordingly. The original unlock handler, FRP read, KPD1 confirmation and final unlocked-state publication were retained in the successful instrumentation. Logging was not implemented by patching `getvar` to return a fabricated yes.

## Why UART and return-value handling mattered

The central UART path included an unbounded wait for bit5 of LSR at0x11004014. V2 measured LSR0 while USB INFO still worked; that supported making UART non-blocking when not ready. It did not prove every old hang was caused by UART. The eventual image retained the UART correction and original unlock handler, then added INFO markers around real control-flow stages.

An early diagnostic patch introduced a second problem: it removed `MOV R0,R5` at common return offset0x233AE as if the location only handled write errors. A rejection branch at0x234D2 also reached it after a logger call. The fatal message's length was26 (0x1A), providing a binary explanation for why logger return could leak as the visible error. No live PC trace proved that branch for the first failure, so the guide calls it a diagnostic defect with a strong explanation, not proof of a failed flash write.

The corrected build restored `MOV R0,R5`, and preserved write results specifically at0x233AA and0x2343A using `MOVS R5,R0`. Its Z/N flags match a zero comparison, but C/V do not; the audit checked that the subsequent examined branches relied on Z before flags were redefined. Local instruction/path tests supported this analysis, not a general proof of all hardware states.

## Gate behavior and the difference between observation and bypass

Function0x2258C reads ROM_INFO.sboot_config. Config0x11 rejects directly. Config0x22 or0 reaches0x2922C, whose real MMIO read of0x10206060 extracts bit1. With argument1 and bit1=0, the analyzed gate returns0 and can allow constructor creation after an absent seccfg header. Bit1=1 returns1 and rejects that constructor path.

Corrected V3 independently measured gate0, constructor0 and crypto0; yet an actual unlock later returned gate1 and error0x3001 before constructor. That earlier failure did not capture config and the MMIO word at the rejection, so its cause remains unknown. No eFuse change, clear-on-read behavior or crypto-induced hardware change was established. The next image measured values at the actual reader instructions instead of adding speculative MMIO reads or forcing the gate result.

The final image captured config, actual DWORD, argument, gate result, caller LR and whether an MMIO read occurred. The config was taken from the real LDR at0x22592 and the word from the real LDR at0x29234. A config0x11 case is distinguished from a genuine zero read by the read-present flag. This matters scientifically: a zero-initialized capture slot is not automatically a measured hardware zero.

## Actual sequence, with the complete operational evidence contract

Every stage below states purpose, action, files, prerequisites, expected and recorded behavior, verification, failure/stop conditions and recovery reference. Missing literal details are explicitly marked; do not fill them with a generic Internet command.

### Stage 1: Preserve and verify the factory baseline

**Purpose:** Separate backup identity from unlock state.

**Exact recovered action:** Historical stock-backup pipeline; see the extraction guide. No unlock command belongs to this stage.

**Required files:** Factory LK and full readable backup; private manifest/checkpoints and identity references.

**Preconditions:** Correct board/build, read-only transport and separately authorized private scope.

**Expected response:** Complete sizes, hashes and matching GPT.

**Actual recorded response:** 31 principal files verified, 23 partitions matched User slices; full readable backup completed before unlock.

**Success verification:** Historical independent verification PASS, not a fresh extraction.

**Failure conditions:** Missing or mismatched backup/hash; no LK patch should proceed.

**Safe stop condition:** Stop before write; do not create missing approvals.

**Recovery reference:** RECOVERY_AND_ROLLBACK.md, original-input preservation.


### Stage 2: Recover the original lock state

**Purpose:** Prove a bootloader fact rather than infer it from root or SIM operation.

**Exact recovered action:** Recovered actual argument vector: <PINNED_FASTBOOT> -s <VERIFIED_SERIAL> getvar unlocked.

**Required files:** Pinned fastboot, bound USB reference, before response streams.

**Preconditions:** Exact identity, no other fastboot process, complete capture.

**Expected response:** One unambiguous unlocked: no or yes with exit0 and EOF.

**Actual recorded response:** Before the successful attempt: unlocked: no; complete response.

**Success verification:** Parse both stdout/stderr; reject missing/contradictory values.

**Failure conditions:** Transport error, timeout, ambiguous value; UNKNOWN is not locked or unlocked.

**Safe stop condition:** Stop without sending unlock.

**Recovery reference:** Read-only query needs no restoration; altered prior LK remains its own state.


### Stage 3: Audit the unsuccessful V3 versions

**Purpose:** Do not select a file by its timestamp or friendly V3 name.

**Exact recovered action:** Review original reports and disassembly, not another live attempt.

**Required files:** V3 aa5b… and corrected V3 0e573… source/manifest records.

**Preconditions:** Retain original evidence and known image hashes.

**Expected response:** Identify where each attempt stopped.

**Actual recorded response:** First returned0x1A; corrected attempt returned gate1 and0x3001 before constructor/crypto/write.

**Success verification:** Neither report contains successful unlocked=yes after that attempt.

**Failure conditions:** Treating either failed version as successful or blaming USB despite a complete remote error.

**Safe stop condition:** No repeated unlock to fill a documentation gap.

**Recovery reference:** Preserved stock LK and historical DA-only restoration route.


### Stage 4: Prepare the gate-context image

**Purpose:** Measure real gate inputs while preserving original security decisions.

**Exact recovered action:** Historical build_v3.py invokes clang --target=armv7a-none-eabi -mthumb -nostdlib with probe_v3.ld and probe_v3.S; see source for exact arguments.

**Required files:** Factory LK, assembly/linker source, LLVM NDK28.2.13676358; BUILD_MANIFEST.json.

**Preconditions:** Original hash must match, and patch bounds/header checks must pass.

**Expected response:** 524288-byte image; bounded patches; no altered FRP/KPD1/state publisher.

**Actual recorded response:** Final hash f566f0a28297f9459978a41b61c7b3ce254f5ad0e3cc4ec71fa37e094bbe8077, 508 bytes different from original;33/33 reported local tests.

**Success verification:** Source/manifest checks plus later live diagnostic and full readback.

**Failure conditions:** Wrong original image, code outside reserved ranges, register/flag audit failure.

**Safe stop condition:** Stop locally; no binary is distributed in this publication candidate.

**Recovery reference:** Restore source copies locally; hardware restoration is a separate step.


### Stage 5: Install only the measured LK

**Purpose:** Run the audited exact-build instrumentation, not a generic unlock payload.

**Exact recovered action:** Historical START_LK_INSTALL.cmd -> lk_da_session.py --approved-live install. The launcher required a manual ARM_LK_INSTALL token and coordinated Preloader connection.

**Required files:** Final LK, original DA, approved per-session identity/GPT references and transport.

**Preconditions:** Preexisting corrected LK hash0e573…; hardware/storage identity and GPT exact match; original LK saved.

**Expected response:** Write only LK at29884416, length524288, followed by complete readback.

**Actual recorded response:** 13October05:38:30 +01: install/readback matched f566…8077.

**Success verification:** LK_BEFORE and LK_READBACK hashes/bytes; original header checked.

**Failure conditions:** Any different current hash or partial readback; no automatic retry/reboot.

**Safe stop condition:** Stop and preserve the partial session.

**Recovery reference:** Historically verified stock-LK restore later; not a guarantee if Preloader is lost.


### Stage 6: Enter Fastboot and bind the intended device

**Purpose:** Keep the measured LK session and transport identity together.

**Exact recovered action:** The historical entry coordinator and manual transitions are preserved in source; exact physical timing sequence is NOT RECOVERABLE FROM SAVED EVIDENCE reviewed here.

**Required files:** entry.py, USB metadata references, pinned fastboot.

**Preconditions:** Only selected MF904Q; no unrelated phone target; no pending fastboot command.

**Expected response:** One matched USB identity and selector.

**Actual recorded response:** The bound target accepted the subsequent diagnostic and unlock responses.

**Success verification:** Saved identity checks and complete process captures.

**Failure conditions:** Missing/changed identity or multiple/ambiguous selector mappings.

**Safe stop condition:** Stop before a command; do not guess a serial.

**Recovery reference:** Do not use a generic reboot instruction as reconstructed history.


### Stage 7: Run the independent measured diagnostic

**Purpose:** Check constructor/crypto and observe gate context before a separate unlock decision.

**Exact recovered action:** Recovered argument vector: <PINNED_FASTBOOT> -s <VERIFIED_SERIAL> flashing get_unlock_ability, via lk_probe_entry.py.

**Required files:** Exact f566… image, BUILD_MANIFEST.json, parser and diagnostic ticket.

**Preconditions:** Independent diagnostic approval and matching installed image.

**Expected response:** Three ordered context captures, constructor0, crypto0, cleanup0; complete OKAY/exit0.

**Actual recorded response:** 13October05:42:03 +01: config22, DWORD0, argument1, gate0 in all three captures; constructor/crypto/cleanup0.

**Success verification:** Strict response parser checks marker order and caller sites; ordinary stock response is not equivalent.

**Failure conditions:** Missing marker, gate mismatch, read-present inconsistency or nonzero result.

**Safe stop condition:** No unlock if the diagnostic gate fails.

**Recovery reference:** Diagnostic is RAM/MMIO execution; no seccfg erase/commit in this request.


### Stage 8: Authorize the one actual unlock request

**Purpose:** Separate an accepted diagnostic from permission to erase data and write security state.

**Exact recovered action:** Historical START_FINAL_UNLOCK.cmd -> final_unlock_v3.py --approved-live FINAL_UNLOCK_APPROVAL.json; interactive token SEND_UNLOCK_V3.

**Required files:** Fresh approval, verified diagnostic session, FINAL_UNLOCK_BUILD_SHA256.json and bound device.

**Preconditions:** The runner verifies every pinned file, diagnostic path/result/raw parse, USB identity and no competing fastboot process.

**Expected response:** Read unlocked=no, consume one-shot latch, then dispatch one original command.

**Actual recorded response:** Request began13October05:45:22.755 +01.

**Success verification:** One-shot reservation before process launch; dispatch timestamp is host dispatch, not device receipt.

**Failure conditions:** Already yes => stop; incomplete pre-query => no dispatch; wrong hash/identity => reject.

**Safe stop condition:** Cancel before token; once submitted preserve capture and do not launch a second command.

**Recovery reference:** RECOVERY_AND_ROLLBACK.md; userdata erase is possible even if a later phase fails.


### Stage 9: Submit original flashing unlock and confirm manually

**Purpose:** Use the original LK handler and real KPD1 path, not a forced yes response.

**Exact recovered action:** Actual recovered command: <PINNED_FASTBOOT> -s <VERIFIED_SERIAL> flashing unlock. Then separate human decision and one manual WPS press, as recorded by runner tokens.

**Required files:** Running fastboot capture, original unlock handler and KPD1/FRP logic.

**Preconditions:** Explicit separate acceptance of userdata erase and seccfg writes; no automatic button injection.

**Expected response:** Start unlock flow after KPD1 accepted; complete measured original flow.

**Actual recorded response:** Start unlock flow received, gate/config/word measured in the actual commit path; physical WPS time was not instrumented.

**Success verification:** Successful write-return markers and later independent lock query, not LCD prompt alone.

**Failure conditions:** Missing/partial output, FAILED, capture error or unexpected marker sequence.

**Safe stop condition:** No repeated WPS, command retry or automatic power cycle.

**Recovery reference:** Preserve bytes and observe current state before any separately approved recovery.


### Stage 10: Read the successful original-flow measurements

**Purpose:** Distinguish function returns from inferred storage contents.

**Exact recovered action:** Analyze saved unlock_stdout/unlock_stderr; no new device command.

**Required files:** evidence/unlock_stderr.txt, marker map and technical analysis.

**Preconditions:** Complete channels and exit status are required.

**Expected response:** config22, actual word0, argument1, gate0; successful constructor/encryption/two writes/commit.

**Actual recorded response:** Stage40..45 measured actual gate context; two stage30 caller LRs41e231ab/41e2323b each followed by stage31=0; commit0.

**Success verification:** Return values show original paths completed; they are not standalone DA readback of seccfg.

**Failure conditions:** A single OKAY or changed seccfg hash without a lock query is insufficient.

**Safe stop condition:** Keep interpretation bounded; do not declare eFuse repaired.

**Recovery reference:** Later independent security-state read and original-LK persistence provide stronger evidence.


### Stage 11: Require a separate unlocked-state response

**Purpose:** Prove the command changed the state LK reports.

**Exact recovered action:** Recovered actual follow-up: <PINNED_FASTBOOT> -s <VERIFIED_SERIAL> getvar unlocked.

**Required files:** after response streams and FINAL_RESULT.json.

**Preconditions:** Unlock exit0, EOF on both pipes, no capture error, target identity still matched.

**Expected response:** Exactly unlocked: yes with exit0.

**Actual recorded response:** Completed unlock05:47:42.243 +01, duration139.430s; then unlocked: yes, query0.020s.

**Success verification:** Unmodified state-publishing path, independent query rather than parsing OKAY.

**Failure conditions:** Contradiction, duplicate values, capture/transport error => UNKNOWN.

**Safe stop condition:** Stop after capture; no automatic reboot or storage read.

**Recovery reference:** Later verification stages were independently coordinated, not part of this final request.


### Stage 12: Verify persistence and restore original LK

**Purpose:** Rule out success that exists only in a diagnostic LK session.

**Exact recovered action:** Separate approved DA read, new-entry getvar, LK-only original restore and another new-entry getvar. Exact terminal line for each final verifier is NOT RECOVERABLE FROM SAVED EVIDENCE reviewed here; source actions and results are preserved.

**Required files:** Post-unlock seccfg evidence, original LK, full readback, complete query streams.

**Preconditions:** Independent approvals/transitions and correct identity.

**Expected response:** Persistent yes under modified LK and again under original LK.

**Actual recorded response:** 06:09:42 yes after new entry;06:15:52 original LK full-readback verified;06:18:49 factory LK yes, exit0, query0.022s.

**Success verification:** Restored LK hash07ba… matches original bytes; factory response rendering included.

**Failure conditions:** Different restored image, incomplete query, loss of transport or any relock.

**Safe stop condition:** No relock attempt; no claim of rescue from every failed image.

**Recovery reference:** RECOVERY_AND_ROLLBACK.md, tested route vs untested failure modes.


### Stage 13: Verify Android and actual networking

**Purpose:** Keep bootloader success separate from modem functionality.

**Exact recovered action:** Owner observed Android boot and performed a mobile Internet speed test; no invented ADB command.

**Required files:** Private recovery/network photos and final verification report.

**Preconditions:** Original LK restored, new Android boot; network access actually routed through modem.

**Expected response:** Normal UI, Wi-Fi connection, cellular registration and successful public Internet traffic.

**Actual recorded response:** 13October07:46: owner screenshot reported13.04Mbps down/10.44Mbps up and46ms ping.

**Success verification:** One historic functional demonstration; identifying network images are withheld from public release.

**Failure conditions:** Local ping alone or captive operator page does not prove general Internet; one speed test does not prove days of stability.

**Safe stop condition:** No repeated test or configuration changes for publication.

**Recovery reference:** Later B and Arabic-system work are a separate research phase.


## Interactive confirmation was not an automated button sequence

The actual runner prints `WAIT_FOR_LCD`, accepts an observation/decision marker (`LCD_DIALOG_SEEN` or `DECIDE_WPS_WITHOUT_LCD`), then requires `ACCEPT_ERASE_AND_SECCFG_WRITE` before printing `PRESS_WPS_ONCE`. `WPS_PRESSED` and `WPS_RELEASED` are human markers, not electrical measurements. It does not itself press WPS, change the key scanner, or infer a physical event timestamp from its own print time. A front-panel confirmation may take time; the139.430-second result is the full request interval, not a measured button-hold duration.

The source also retains output pipes across Ctrl+C handling rather than declaring success when a UI window closes. This is important for distinguishing a pending device command from a lost host monitor. For the successful trial, process exit0 and EOF on both channels were recorded. For failed trials, complete remote error responses were preserved; those are different from a USB transport disappearing.

## What the successful result does and does not explain

The final trial proves that real gate inputs permitted the original constructor/crypto/write path and that the subsequent original state query reported yes. Later original-LK persistence strengthens this substantially. It does not prove why the previous corrected trial saw gate1. There was no matching config/DWORD measurement at that earlier rejection. Logging may affect timing; success after instrumentation is not proof that logging repaired hardware or changed an eFuse.

The UART wait and earlier R5-return defect are supported by specific analysis and observations. They must not be inflated into a universal explanation of every unsuccessful unlock. The project did not bypass FRP, replace KPD1 with a fabricated key, force the gate to return0, synthesize a stored unlocked structure externally or patch getvar to print yes. These distinctions are the scientific value of the record.

## After the unlock: do not confuse later custom-ROM failure with lock failure

Arabic localization later demonstrated visible WebUI/LCD output, but persistent modified system images shut down after boot. That unresolved issue is documented separately. A custom system shutting down does not negate the original-LK unlocked query; conversely, an unlocked bootloader does not guarantee arbitrary modified system compatibility. B's reported two-day stability is a baseline observation, not proof that a specific APK or Jetty event caused shutdown.

## Missing items and responsible reuse

The public snapshot omits factory-derived executables, identity-bound approvals, unique device selectors and some private working-tree dependencies. It is therefore a research source release, not a turnkey unlock kit. Literal historical commands not recovered are marked above. A future port must reconstruct its own legal inputs and compatibility gates and preserve failure conditions, rather than remove hashes/identity checks or substitute a generic vendor command. No physical console pinout, guaranteed debrick method or model-wide support claim is supplied.
