# Submission draft — technical article link

**Title:** Reconstructing an MF904Q LK Unlock Path: Actual Gate Inputs, Corrected Return Instrumentation, and Persistence Under Factory LK

**Link target (placeholder, not live):**
`https://github.com/YOUR_GITHUB_USERNAME/ZTE-MF904Q-Reverse-Engineering/blob/main/02-Bootloader-Unlock/COMPLETE_UNLOCK_GUIDE.md`

**Short link description, if the current composer permits it:**
An exact-build ARM/Thumb LK investigation from failed unlock diagnostics to actual-reader context instrumentation, original constructor/crypto/write execution, independent unlocked-state queries, and persistence after restoring factory LK. Includes source-referenced offset analysis, real failed responses and explicit limits; no manufacturer binaries or private device dumps.

**Opening technical comment, only if current rules permit:**
I am the device owner preparing this research record. The interesting part is not the final fastboot verb. An early common-epilogue patch could leak a logger return; corrected instrumentation exposed a constructor-gate rejection, and a later build captured config/MMIO values at the real reader instructions without adding an extra hardware read or bypassing the gate. The eventual yes query was independently reproduced under restored factory LK. The reason for the old gate1 context remains unknown, and the article does not attribute that to an eFuse change. Later Arabic-system shutdown is a separate unresolved result, not the main claim of this submission.

Moderator's historical explanation of article/question separation: [2021 moderator post](https://www.reddit.com/r/ReverseEngineering/comments/llfvrj/). It is historical guidance, not a claim that the current rules are unchanged. The current rules page returned an empty rules shell in our check, so submission type and all current requirements still need manual review. If link articles are not allowed, do not force a self-post. Do not turn the article submission into a generic help request.


Current status correction23October2026: The saved19October2026 session confirms a complete B system restore and matching629145600-byte readback (SHA2561e7e386cef9ae14e0e2f62885fe9bbc34dbf15257d1611947a9a99a0adcb15b7). A later23October session confirms a complete restore of the distinct factory system (SHA2569bb23ccc2a0347f0a506ed3a0d2a6784593e8f0a4d4f1d01d79f2d68d56cbe80). The owner clarified on23October that the later factory restoration was prompted by slow Internet, which they subsequently attributed to their Ooredoo connection rather than the modem. This is an owner observation about that slowdown, not a demonstrated cause of the separate Arabic-system power-off. Last saved system image is factory9bb23…, not B; no live device query was made for this publication review.

Release boundary25October2026:50 reviewed tool-source files are included with per-file terms and upstream notices; one assembly source remains withheld. No vendor binary, full LK rebuild or portable executable is claimed. General reuse terms for independent code are not yet selected.


Source-review update25October2026: the prior blanket source hold is superseded.50 files are included with scoped attribution/license records, probe_v3.S is withheld, no blanket repository license is chosen, and no vendor firmware/executable or full LK-build claim is made. Posting remains subject to current forum rules and the owner's explicit final approval.
