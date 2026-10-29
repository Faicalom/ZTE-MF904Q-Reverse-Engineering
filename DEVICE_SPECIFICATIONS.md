# Device and build scope

| Field | Evidence-supported value |
|---|---|
| Project device name | ZTE MF904Q / M19-E; owner/project identification, not an assertion of vendor endorsement |
| PCB | WF904_V6.0, historical board records |
| Reported SoC family | MT6735V / MT6735; transport HW code 0x0335, HW version 0x0000 |
| Android | Android 6, API 23, ARM |
| Android device | mf904q_v4_35m_lwtg |
| Build string | MF904Q-6.0-1-6735WM_LCD_20240123 |
| Historical host | Windows 11; exact Windows revision NOT RECOVERABLE FROM SAVED EVIDENCE reviewed here |
| Storage | eMMC; User 3825205248 bytes, Boot1 and Boot2 each 4194304 bytes |
| DRAM | DA-reported 536870912 bytes (512 MiB) |
| eMMC identification | Kingston/S10004 interpretation with CID CRC7 verification; unique CID withheld |
| GPT | 23 entries, 512-byte logical LBA, primary and backup CRC verified |
| RPMB | 4 MiB reported; not read, cloned, or authenticated |
| CSD / EXT_CSD | not read |
| Historical Preloader USB | VID 0x0E8D, PID 0x2000; COM number is dynamic |

Do not transfer raw LK offsets, identity bindings, partition addresses or approvals to another build. A matching retail name alone is insufficient. No UART pinout or electrical voltage has been established by this project.

Identity fields must retain their original query labels: the early FD exchange recorded0x0000 as its second word, while the expanded identity report records subcode0x8A00 and HW-version0xCA00. These responses must not be flattened into a single universal version value.
