# Which evidence can distinguish the MF904Q post-boot shutdown from internal logger termination?

This discussion concerns the permanent Arabic system experiments, not the independently verified bootloader-unlock result. Start with `03-Research-Results/CUSTOM_ROM_FAILURE_ANALYSIS.md` and the full source/evidence limits.

The owner reports B stable for two days. Combined WEB+LCD and WEB_ONLY images booted then powered off; Arabic LCD appeared in the relevant runs. WEB_ONLY retained factory TeleService.apk and passed complete system readback. LCD_ONLY was separately built, but the clean stock-runtime WebUI transition was blocked; owner-reported behavior must not be treated as a fully controlled TLR/ROOT/cache isolation experiment.

OEM USB/ADB changes mean ADB loss is not proof of shutdown. A persistent ARM logger was confirmed STARTED and recovered later; the hardened capture's last BEFORE_SYNC at uptime30.891903 lacked an AFTER_SYNC, terminal record or decisive IO_ERROR. This can reflect several different endings and does not prove fsync caused power-off.

Questions for review:

1. Which existing retained kernel/platform logs could distinguish reboot/power-off from a lost collector on this build, without assuming pstore is configured?
2. What additional observation would specifically distinguish a blocked fsync from SIGKILL or abrupt loss, given this trace?
3. What exact invariants must hold across TLR.db, runtime ROOT.war, open JarFile objects and extracted/work cache for an LCD-only trial to be interpretable?
4. Is there a documented OEM shutdown mechanism that would produce positive evidence in the already saved buffers, rather than simply treating absence of panic as proof of power failure?

Please provide source/build references and keep hypotheses separate from observations. Do not upload private dumps, suggest another device's seccfg, or request a format-all experiment. No further physical test or live firmware change is authorized by this discussion draft.


Current status correction23October2026: The saved19October2026 session confirms a complete B system restore and matching629145600-byte readback (SHA2561e7e386cef9ae14e0e2f62885fe9bbc34dbf15257d1611947a9a99a0adcb15b7). A later23October session confirms a complete restore of the distinct factory system (SHA2569bb23ccc2a0347f0a506ed3a0d2a6784593e8f0a4d4f1d01d79f2d68d56cbe80). The owner clarified on23October that the later factory restoration was prompted by slow Internet, which they subsequently attributed to their Ooredoo connection rather than the modem. This is an owner observation about that slowdown, not a demonstrated cause of the separate Arabic-system power-off. Last saved system image is factory9bb23…, not B; no live device query was made for this publication review.

Release boundary25October2026:50 reviewed tool-source files are included with per-file terms and upstream notices; one assembly source remains withheld. No vendor binary, full LK rebuild or portable executable is claimed. General reuse terms for independent code are not yet selected.


Source-review update25October2026: the prior blanket source hold is superseded.50 files are included with scoped attribution/license records, probe_v3.S is withheld, no blanket repository license is chosen, and no vendor firmware/executable or full LK-build claim is made. Posting remains subject to current forum rules and the owner's explicit final approval.
