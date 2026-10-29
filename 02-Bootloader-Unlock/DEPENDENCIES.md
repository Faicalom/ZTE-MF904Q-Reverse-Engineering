# Historical dependency inventory — no live environment claimed

| Component | Saved version/evidence | Distribution / acquisition |
|---|---|---|
|Windows|Windows11 in live extraction report|Original host; exact OS build not reconstructed|
|Python|Archival offline check reports3.13.14 x64|Obtain separately; not proof of every historical invocation's interpreter|
|pyserial|3.5 in serial/runtime metadata|BSD metadata; acquire separately, no library tree bundled|
|cryptography|50.0.2 in preserved dist-info|Apache-2.0 OR BSD-3-Clause metadata; private archive helper only, not required by new offline validators|
|cffi / pycparser|2.1.1 /3.1 in preserved archive dependencies|Not bundled; inspect upstream notices before redistribution|
|Android fastboot|37.0.1-15733141; hashb2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86|Original SDK tool, not bundled|
|NDK LLVM|28.2.13676358 in historical builder|Obtain separately; no LK rebuilt here|
|MediaTek VCOM|3.0.1504.0 in original Windows diagnosis|Not bundled; match actual hardware/OS, do not force a historical COM number|
|mtkclient reference|cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3; local GPLv3 headers|Reference source, not vendored; derived-source redistribution gate unresolved|
|Original DA|MTK_DA_V5.bin; original stage hashes in research evidence|Legally obtained own matching input required; excluded, no universal legal download promised|
|Private project references|CID/USB path/GPT/approvals and one-shot guards|Never publish; other devices cannot reuse these values|
|C# helpers|Controlled.cs family plus referenced support assemblies|Historical source/build prerequisites not completely reconstructed; no claimed portable executable|

Only `scripts/verify_public_files.py` and `scripts/check_saved_unlock.py` in their respective folders run in the clean candidate. They use the Python standard library and read local publication files only. No `pip install` or device setup is required to use them. The AST inventory lists remaining project imports; it is deliberately not converted into a misleading tested requirements.lock. Complete historical tools cannot be promised without resolving source rights, missing identity inputs and environment paths.


## Updated source release25October2026

The earlier41-file hold is superseded by the per-file review.50 reviewed historical files are supplied, including10 additional matching DA dependencies.24 covered DA components retain GPLv3 source terms;26 independent/factual files have no newly selected blanket license. The single unresolved assembly file is withheld. Vendor DA, factory images and private identity/approval/reference files remain excluded. Source layout preserves original paths and safety gates, so these are not portable turnkey live tools. See RIGHTS_AND_RUNTIME_LIMITATIONS.md at repository root before use.
