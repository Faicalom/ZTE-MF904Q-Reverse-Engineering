# I Unlocked the Bootloader and Dumped the Firmware of an MF904Q 4G Modem — What Worked and What Did Not

I have been reverse engineering an MF904Q/M19-E mobile modem, board WF904_V6.0, running Android6 on a MediaTek platform. The part I want to share is the process and its evidence, not a claim that a generic unlock command works on any ZTE modem.

The first firmware-backup attempt failed. Fixing the Windows Preloader driver made the port accessible, but receiving the automatic READY banner did not complete the handshake. The successful path came after reviewing the receive parser, command/response pairing and original DA flow. On9October, unmodified stock DA stages returned real flash data. The completed backup covered all23 GPT partitions, both eMMC boot regions and the full3.56GiB User area. An independent verifier checked31 main files and compared each partition against the corresponding range in User. RPMB andEXT_CSD were not captured.

Unlocking was a different investigation. I worked from the exact original LK, retained its original unlock handler and instrumented the path rather than simply forcing a reported state. An unbounded UART wait and a mistake in early error-return instrumentation mattered. One failed version showed0x1A; a corrected version showed a real gate rejection and0x3001 before storage-write stages. The final version captured actual gate inputs at their reader instructions. It completed the original flow and a separate query returned unlocked=yes.

The strongest check came afterward: original LK was restored with complete readback, and a new entry under that original LK still returned yes. Android and real mobile Internet worked after restoration. That is why I distinguish this from a root shell, a SIM setting or a patched string.

There is still an unsolved result. Arabic WebUI and LCD output appeared successfully, but persistent modified system images powered off after boot. B, a stock-derived control, was reported stable for two days. WEB_ONLY also powered off with factory LCD APK and a matching full system readback. That does not settle the cause: runtime ROOT.war/OEM cache state and the missing final shutdown trace remain important limits. I am not calling it a confirmed power, Jetty or Phone bug.

I have prepared the complete extraction/unlock history, reviewed source-referenced documentation (reviewed historical source with per-file terms), measured outputs and failure analysis. Firmware, download agents, raw dumps, identities and active approvals are excluded. Reviewed source research releases include50 source/build files; one assembly source is withheld; this documentation candidate is not a ready-to-run unlock executable.

Repository placeholder: `https://github.com/YOUR_GITHUB_USERNAME/ZTE-MF904Q-Reverse-Engineering` — replace after actual publication. The reviewed PCB close-up can accompany the post; it documents components, not a UART pinout or proof of unlock. I would particularly appreciate review of the gate-context interpretation and suggestions for obtaining a decisive shutdown record without repeating an ineffective logger experiment.

Before posting, I will recheck this community's current rules and avoid duplicate promotion or exposing private device information.


Current status correction23October2026: The saved19October2026 session confirms a complete B system restore and matching629145600-byte readback (SHA2561e7e386cef9ae14e0e2f62885fe9bbc34dbf15257d1611947a9a99a0adcb15b7). A later23October session confirms a complete restore of the distinct factory system (SHA2569bb23ccc2a0347f0a506ed3a0d2a6784593e8f0a4d4f1d01d79f2d68d56cbe80). The owner clarified on23October that the later factory restoration was prompted by slow Internet, which they subsequently attributed to their Ooredoo connection rather than the modem. This is an owner observation about that slowdown, not a demonstrated cause of the separate Arabic-system power-off. Last saved system image is factory9bb23…, not B; no live device query was made for this publication review.

Release boundary25October2026:50 reviewed tool-source files are included with per-file terms and upstream notices; one assembly source remains withheld. No vendor binary, full LK rebuild or portable executable is claimed. General reuse terms for independent code are not yet selected.


Source-review update25October2026: the prior blanket source hold is superseded.50 files are included with scoped attribution/license records, probe_v3.S is withheld, no blanket repository license is chosen, and no vendor firmware/executable or full LK-build claim is made. Posting remains subject to current forum rules and the owner's explicit final approval.
