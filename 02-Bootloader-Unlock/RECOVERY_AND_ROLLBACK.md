# Recovery and rollback: proven route and unproved cases

## Preserve originals before a risky action

Retain the complete factory LK, its SHA256 and exact length, GPT reference, original DA inputs and private identity/geometry evidence in restricted storage. Back up the full readable device, not just the patched file. Keep all partial reads and operation logs; do not overwrite the last good copy with a candidate. Never publish raw calibration/security/userdata ranges.

## What was actually restored

On13October, after a separately coordinated transition into the working DA path, the original LK alone was written to its verified range. The entire524288-byte LK was read back and matched the original hash07ba…a596. A new factory-LK query still returned unlocked=yes, followed by Android/Internet functionality. This is direct evidence for that tested rollback from the instrumented image, not a generic guarantee for all LK corruption.

The source transport requires identity, GPT and current-image gates, a saved before image, a one-attempt reservation and full readback. If a write was attempted and acknowledgment/readback is incomplete, preserve all evidence and label target state UNKNOWN. Do not infer an intact image from a transfer ACK or restart a write automatically.

## What requires which interface

| Action | Necessary condition in the observed route | Not established |
|---|---|---|
|Query unlocked|working LK/Fastboot with bound identity|available if LK cannot boot|
|Restore original LK|working matched Preloader/DA transport and original inputs|recovery when Preloader is destroyed|
|Read Android runtime files|appropriate Android access and permissions|available during every short ADB window|
|Restore B system with clean WebUI|system transport plus matching runtime ROOT handling|system write alone restoring all data state|

Do not write Preloader, use format-all, relock, clone another modem's seccfg, alter NVRAM or guess an electrical connection as a fallback. No complete cold-boot rescue or authenticated RPMB restoration was proven. The original backup also omitted EXT_CSD. A reader without the tested transport and matching inputs should stop rather than treat this chapter as a guaranteed unbrick procedure.
