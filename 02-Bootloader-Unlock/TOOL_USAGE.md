# Tool map, dependencies and historical actions

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

| Source | Purpose | Execution status of public copy |
|---|---|---|
|build_v3.py + probe_v3.S/.ld|exact-original-LK patch build|historical source; no proprietary input included; not rebuilt here|
|lk_da_session.py / lk_install_policy.py|bounded LK-only install/restore and full readback|historical source; missing private approval/input/reference chain|
|lk_probe_entry.py|single context diagnostic query|historical source; private identity/diagnostic authorization absent|
|final_unlock_v3.py|one original unlock with separate human confirmation, then independent state query|actual successful coordinator; not a general-purpose standalone executable|
|capture.py|complete stdout/stderr/process-exit capture|historical support code|
|response_gate_context.py / response_v3.py|strict measured-diagnostic parser|offline parser; requires matching BUILD_MANIFEST.json|
|scripts/check_saved_unlock.py|publication offline evidence validator|new local helper; no USB/network access|

## Safe local review invocation

```powershell
python scripts/check_saved_unlock.py .
```

The helper requires the exact successful stage sequence and a separate `unlocked: yes` response plus the factory-LK response. It does not unlock anything. Passing it only validates the included evidence, not a current device.

The actual historical terminal actions were `START_LK_INSTALL.cmd`, the diagnostic launcher and `START_FINAL_UNLOCK.cmd`. The latter called the earlier environment's Python with `final_unlock_v3.py --approved-live FINAL_UNLOCK_APPROVAL.json`; the final interactive token was `SEND_UNLOCK_V3`. These are reconstructed actions with original parameters, not instructions to invent approval JSON in this public snapshot.

`final_unlock_v3.py` imports earlier `entry` and `usb_metadata`; its environment contains pinned fastboot and Windows USB references. `lk_da_session.py` imports `limited_da`, whose original DA/reference and other transport dependencies are external. The supplied code list is a reviewed research subset, not a transitive live-runtime closure. Third-party SDK/runtime/vendor files and unique reference data are PRIVATE_NOT_INCLUDED. No claim is made that moving these files into a fresh directory yields a usable live flasher.

Source path redaction is documented in the provenance manifest: personal `C:/Users/...` paths become `C:/Users/YOUR_WINDOWS_USER`. Some references to historical source folders intentionally remain so researchers can trace imports. No active ticket, one-shot latch, original device selector or secret is included. No executable is offered without source or described as original project-owned code when provenance is unresolved.


## Updated source release25October2026

The earlier41-file hold is superseded by the per-file review.50 reviewed historical files are supplied, including10 additional matching DA dependencies.24 covered DA components retain GPLv3 source terms;26 independent/factual files have no newly selected blanket license. The single unresolved assembly file is withheld. Vendor DA, factory images and private identity/approval/reference files remain excluded. Source layout preserves original paths and safety gates, so these are not portable turnkey live tools. See RIGHTS_AND_RUNTIME_LIMITATIONS.md at repository root before use.
