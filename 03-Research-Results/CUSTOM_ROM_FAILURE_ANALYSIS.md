# Permanent modified-system power-off: unresolved investigation

## Baseline and controlled file differences

| Image | SHA256 | Intended change from B | Observed / verified limit |
|---|---|---|---|
|B|1e7e386cef9ae14e0e2f62885fe9bbc34dbf15257d1611947a9a99a0adcb15b7|stock-derived control|owner reports two days stable|
|Combined Arabic|cc6775cb9d4e93649c8e51b831dacae568947c81912ceb7a7b15bf2a6cfabfe9|TeleService resource APK +TLR.db|full system write/readback documented; Arabic appeared then power-off|
|WEB_ONLY|25481c15fc53ef8755b6a10796146fa8499a785f8a3b52e9d04a41aab90dabdf|TLR.db only|629145600-byte write/readback matched; factory APK; owner reported power-off|
|LCD_ONLY|5ca98f12a1191bac5bbd4586ebe57d074289e3cd721a236fa1e4bb2a0c492bcc|TeleService resource APK only|local build verified; owner reports shutdown; complete clean runtime-isolation proof absent|

All image sizes are629145600 bytes. The independently derived WEB_ONLY andLCD_ONLY inventories compared1474 paths with B. Only the intended payload differed;54 ODEX files and86 Framework entries remained identical, and reviewed security metadata/geometry were preserved. ext4 checks passed. These host results do not by themselves prove a valid verity boot or all runtime behavior.

The companion boot used by the reviewed trials has system verify absent from its fstab. Its hash47d82d2581fdb916e79875a422e703de395d24528d4bf8d036bff8ce65804582 was retained before/after the reviewed WEB_ONLY flash. Preserved factory verity-tail bytes do not create a new valid tree for modified files; arbitrary verified boot configurations are not supported by this observation.

## Runtime WebUI is a separate experimental variable

OEM reads `/system/etc/TLR.db` and prepares `/data/media/0/lrserver/webapps/ROOT.war` (also visible through emulated storage). A system-only change does not prove the runtime WAR, Jar cache and extracted/work directories match. Last direct recorded runtime ROOT was Arabic; no current read was performed for publication. A clean LCD_ONLY test plan was explicitly blocked pending a proven transaction/quiescence procedure, because replacing an open ZIP or allowing OEM recopy could mix variants.

Consequently the WEB_ONLY result shows modified LCD APK in system was not necessary for that observed power-off, but it does not prove TLR content is the sole cause. The owner-reported LCD_ONLY result must not be relabeled as a controlled web-stock test without runtime evidence.

## Captures, events and limitations

Earlier saved logs establish Android completed boot in an observed Arabic run. The owner reported Arabic LCD followed by full power-off around10seconds after the UI, with a period of charging cycling in some trials and later steady charging. These physical observations were not derived from ADB status.

OEM `com.lr.usb.openclose`/`setAdbEnabled` behavior explained an ADB visibility limit. Loss of ADB is therefore not an independent proof of a crash, power-off or reboot. An earlier host watcher also searched log content for “disconnected” and could misclassify a normal kernel `HWDISCONNECTED` line; that diagnostic defect was repaired separately.

An internal native logger was confirmed STARTED and later its eight files were recovered. Its last FLUSH was around uptime31.116279, with no COMPLETE orFAILED. A hardened logger's nine recovered files totaled721611 bytes. It had29 BEFORE_SYNC versus28 AFTER_SYNC markers; the final marker at uptime30.891903 began syncing the logcat descriptor, after a prior completed sync around30.433404. It recorded no decisive errno/IO_ERROR or terminal completion.

That unmatched marker means completion was not recorded. It does **not** prove fsync permanently hung, an I/O failure occurred, the logger was killed, or power collapsed at that instant. Buffered tails and missing final records leave several possibilities. Child-exit0 events were not evidence that Phone or the system crashed. Captured PGID/SID differed from adbd, and the collector had been observed after adbd disappeared; cgroup samples did not establish that shutting ADB killed it.

## What has been excluded, and what has not

* A pure failure to display Arabic is excluded for the owner-observed LCD runs: Arabic actually appeared.
* A mismatched or incomplete system transfer is excluded for the fully matched specific WEB_ONLY and combined sessions, not for every unnamed attempt.
* Modified LCD APK in system is not necessary for the observed WEB_ONLY shutdown. Runtime/data state remains a confound.
* There is no decisive captured kernel panic, watchdog reset, Phone/System Server crash causing shutdown, explicit Android shutdown request or voltage-collapse trace.
* Passing ext4, unchanged ODEX and successful readback do not exclude runtime incompatibility, power events or an uncaptured kernel failure.

## Questions suitable for other researchers

What durable shutdown evidence can this kernel retain once OEM disables ADB? Can the final sync marker be distinguished from sudden process/power loss without another same-method logger? Which OEM Jetty source/runtime/cache preconditions are necessary for a valid one-file comparison? Are there platform-specific shutdown paths not emitted to the captured buffers? What evidence would establish the last actual power transition rather than only last logged activity?

These are research questions, not invitations to flash unrelated images, modify power settings or assume a cause. UART pin mapping was not established and no physical measurement was performed in this publication task.
