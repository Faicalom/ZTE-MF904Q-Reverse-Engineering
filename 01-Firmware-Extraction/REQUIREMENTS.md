# Extraction requirements and exact historical scope

1. Examined MF904Q/WF904_V6.0 with the saved build and expected geometry. Exact hardware identity was checked, not just the model label.
2. Windows 11. MediaTek VCOM driver 3.0.1504.0 (`oem65.inf` in the early local installation) corrected a missing driver. INF published names vary by host; do not uninstall or replace unrelated device drivers to reproduce that name.
3. Python environment used by `START_STOCK_BACKUP.bat` in the earlier backup project's `tools/venv/Scripts/python.exe`. The complete Python/pyserial version lock is NOT RECOVERABLE FROM SAVED EVIDENCE reviewed here; do not invent a tested version. The current publication validator's interpreter is not evidence of the 9 October runtime.
4. Original, hash-pinned `MTK_DA_V5.bin`, original DA1 and DA2 regions and their audited parsing metadata. They were uploaded to RAM unmodified. No EMI input was sent during the successful extraction.
5. Historical transport modules and private reference session `20261009_104835_647022`, including original geometry/CID and 34-sector prefix. These references are not public because they bind the particular device.
6. Free space: the historical launcher required at least 3 GiB for its non-private scope or 20 GiB for private/full User scope, including raw RX overhead. Do not equate the 3.56 GiB User image with total backup workspace.
7. Encrypted private-data storage and a separately retained password. Original code used AES-256-GCM and verified decryption; no key/password is distributed.

Linux, UsbDk, alternate DA agents, RAM LK loaders, UART and generic mtkclient unlock commands are not verified requirements for the successful Windows extraction. They must not be silently added as equivalent steps.


## Additional archival version evidence recovered from F

The preserved offline check records Python3.13.14 x64 and pyserial3.5; the unlock serial manifest also pins pyserial3.5. The10October entry report pins fastboot37.0.1-15733141, SHA256b2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86. This updates earlier missing-version notes: that Fastboot version is recoverable. A complete environment lock across every historical extraction attempt remains unestablished. See the prerequisite chapter in the unlock folder for exact evidence distinctions.
