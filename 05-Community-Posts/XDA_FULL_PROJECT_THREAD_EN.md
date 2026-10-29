# [PROJECT] ZTE MF904Q / M19-E — Bootloader Unlocked, Verified Firmware Extraction and Android 6 Reverse Engineering

I have been investigating an MF904Q/M19-E mobile modem built around the WF904_V6.0 board and an Android6/MediaTek platform. I am preparing the research record because this device had no procedure I could simply trust and repeat. The useful result is the chain of evidence: how a short Windows Preloader window became a verified readable backup, how unsuccessful LK experiments were corrected, and how the final unlock was verified again after restoring factory LK.

Repository placeholder, to replace only after publication: `https://github.com/YOUR_GITHUB_USERNAME/ZTE-MF904Q-Reverse-Engineering`.

## Hardware and starting point

The examined device reports Android6/API23, device `mf904q_v4_35m_lwtg`, build `MF904Q-6.0-1-6735WM_LCD_20240123`. The transport hardware code was0x0335; DA reported512MiB DRAM, a3825205248-byte eMMC User area and two4194304-byte boot regions. The board/build scope is deliberate: I am not claiming support for every ZTE or MediaTek modem with a similar name.

The project began with firmware access and localization research. The initial backup controller did not extract firmware. A missing Windows Preloader driver was corrected, but the automatic READY banner still did not establish a successful handshake. Some early responses were partial or ambiguously paired with repeated transmit bytes. Instead of treating that as proof of security rejection, the transport parser and pacing were reviewed.

## From a working DA to a verified backup

On9October, original unmodified DA stages from the examined MTK_DA_V5 input ran successfully on Windows and returned actual flash sectors. The first successful read covered34sectors and the primary GPT. The later backup coordinator verified identity/geometry, repeated a prefix and256KiB LK sample independently, checked primary and backup GPT CRCs, and extracted all23 GPT partitions, both boot regions and the full User area.

The independent final verification covered31 principal files and matched every partition against its corresponding slice in the complete User image. That matters more than a progress bar reaching100%. It is still not a copy of everything in the eMMC: RPMB was not read, and CSD/EXT_CSD were not captured. The private backup, identities and raw RX material are not being published.

The extraction and unlock tools are separate. Extraction succeeded before unlocking. Their documented source provenance and environment constraints are documented separately rather than bundled into an unexplained executable.

## How the unlock research developed

The successful path used an exact-build LK derivative that retained the original unlock handler, FRP/key confirmation and state publisher. It was not a generic command recipe. Early instrumentation established live config/crypto-selector/UART information. A later measurement showed UART LSR0 while USB INFO still worked, exposing an unbounded UART wait in the examined path.

An initial V3 attempt returned0x1A. Auditing the instrumentation revealed that removing a common `MOV R0,R5` could leak a logger's26-byte return on another path. The patch was corrected narrowly so actual write errors were preserved without corrupting constructor/gate errors. The corrected attempt then returned0x3001 after the gate rejected default seccfg construction; it had not reached the measured write stages.

The key next step was measurement rather than bypass. The final LK captured config and the hardware word from the actual reader instructions, together with argument, gate result, callerLR and a read-present flag. It did not force a gate result, write an eFuse, replace the key scanner or make getvar print a fabricated yes. Earlier rejection inputs were missing, so their cause remains explicitly unresolved.

On13October the final measured build completed the original unlock after separate manual confirmation. The recorded gate/config/word permitted constructor, encryption and both write paths; all returned success. The request completed in139.430seconds. A separate query then returned `unlocked: yes` with complete channels and exit0.

## Why I consider the unlock verified

A later new-entry test still returned yes under the instrumented LK. Factory LK was then restored with a full524288-byte readback matching its original hash. Another new entry under factory LK returned `unlocked: yes` again. Android subsequently booted and I demonstrated actual cellular Internet through the modem. Those checks distinguish persistent bootloader unlock from root, SIM status, an INFO marker or an OKAY response alone.

The repository includes the detailed chronology, source references, selected response transcripts and complete limitations. Manufacturer DA and firmware binaries are excluded. Reviewed source research releases include50 source/build files with one assembly source withheld and are not advertised as production-ready packages.

## Arabic localization: visible success, unresolved stability

Temporary Arabic WebUI and LCD output worked, including the hotspot label. Persistent modified system images booted far enough to show Arabic but subsequently powered off. B, a stock-derived control system, was reported stable for two days. The combined system changed a resource APK and TLR.db; separately built variants changed one file each. In the verified WEB_ONLY flash, factory TeleService.apk was present and the full system readback matched, but the modem still powered off.

That narrows a comparison; it does not prove Jetty, power, TeleService or TLR is the cause. ROOT.war on data, OEM recopy and Jar/extracted cache must also be controlled. The clean LCD_ONLY plan was blocked without that runtime guarantee, so I do not present every owner-observed LCD_ONLY shutdown as an isolated experiment.

Logcat/kernel/internal logger work did not capture a decisive final cause. ADB loss was separately affected by OEM USB/ADB behavior and is not itself proof of power-off. The hardened logger's final unmatched BEFORE_SYNC record is also not proof that fsync caused shutdown. The cause remains unresolved, and permanent Arabic firmware is not being advertised as stable.

## Current status and what would help

See CURRENT_BASELINE_20261023.md for the newly recovered B restore and later distinct factory restore; current physical state was not probed.

I would welcome review from people familiar with this generation of MediaTek LK, ZTE-style Android modem services, and Jetty/ROOT.war runtime preparation. In particular: what durable evidence would distinguish abrupt power loss from software shutdown after ADB is disabled, and what is the smallest defensible source/runtime/cache isolation plan? The detailed technical article and failure analysis are linked from the repository. Please do not send raw private dumps or cross-device seccfg images.

Publication note: this text is prepared locally. The proposed XDA section and its current rules still require manual confirmation before posting. No thread URL exists yet.


Current status correction23October2026: The saved19October2026 session confirms a complete B system restore and matching629145600-byte readback (SHA2561e7e386cef9ae14e0e2f62885fe9bbc34dbf15257d1611947a9a99a0adcb15b7). A later23October session confirms a complete restore of the distinct factory system (SHA2569bb23ccc2a0347f0a506ed3a0d2a6784593e8f0a4d4f1d01d79f2d68d56cbe80). The owner clarified on23October that the later factory restoration was prompted by slow Internet, which they subsequently attributed to their Ooredoo connection rather than the modem. This is an owner observation about that slowdown, not a demonstrated cause of the separate Arabic-system power-off. Last saved system image is factory9bb23…, not B; no live device query was made for this publication review.

Release boundary25October2026:50 reviewed tool-source files are included with per-file terms and upstream notices; one assembly source remains withheld. No vendor binary, full LK rebuild or portable executable is claimed. General reuse terms for independent code are not yet selected.


Source-review update25October2026: the prior blanket source hold is superseded.50 files are included with scoped attribution/license records, probe_v3.S is withheld, no blanket repository license is chosen, and no vendor firmware/executable or full LK-build claim is made. Posting remains subject to current forum rules and the owner's explicit final approval.
