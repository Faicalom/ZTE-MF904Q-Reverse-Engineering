# Project status —23October2026

| Result | Evidence level |
|---|---|
|Firmware backup:23 GPT partitions, two boot regions, full User|Confirmed from historical independent verification; RPMB/EXT_CSD not backed up|
|Persistent bootloader unlock|Original flow + separate yes; original LK restored/readback matched; original-LK new-entry yes|
|B operated normally for two days|Owner-confirmed historical observation|
|B restored19October|Newly located complete saved write/readback matches1e7e…15b7|
|Factory system restored23October|Later complete saved write/readback matches9bb23…be80; distinct image from B|
|Reason for later factory restore|Owner explains slow Internet prompted restore; later attributed slowdown to Ooredoo rather than modem|
|Arabic WebUI and LCD output|Successful appearance confirmed; permanent stability failed|
|WEB_ONLY/LCD_ONLY/combined power-off|Owner observations; flash and clean runtime isolation proof differ between trials|
|Shutdown root cause|UNRESOLVED; not explained by the separate Ooredoo slowdown|
|Public release status|DOCS_READY_FOR_OWNER_REVIEW; original source/tool releases held for licensing decision|

Read [latest baseline](CURRENT_BASELINE_20261023.md) and the detailed guides. No device was contacted, rebooted, unlocked, reflashed or read anew in this publication task. Historical source names remain documented even when their files are not in the current upload allowlist. No license was imposed on the owner's code or third-party code.
