# Exact-build LK technical analysis

All offsets below refer to the original 524288-byte LK with hash07ba…a596. Code base is0x41DFFE00. These are not universal physical addresses or patch points for other firmware.

| Component | Evidence-supported role | Limits |
|---|---|---|
| Preloader | initializes context and loads LK; accepts examined derived image in tested setting | arbitrary RAM execution and all signature-policy cases unproved |
| Original unlock handler | FRP/key checks, userdata erase path, then security commit | erasure may precede later commit failure |
| 0x22ED0 constructor | builds V3 default structure in RAM, clears0x1860 bytes | constructor success is not a flash write |
| 0x22F84/22F3C | scans0x3000-byte buffer for12-byte header | absent header propagates0x3001 |
| 0x2334C–234D4 commit | load/gate/constructor/crypto/write/decrypt and return paths | function returns require capture; not inferred from image diff |
| 0x2258C gate | reads sboot_config; config11 rejects, config22/0 calls hardware-bit path | previous gate1 input values were not measured |
| 0x2922C, LDR0x29234 | reads0x10206060, extracts bit1 | no eFuse write or clear-on-read proof |
| ROM_INFO config | live location0x41E5F808 in analyzed build | must not be mistaken for a disk partition offset |
| Crypto selector | byte at0x41E5F814, value1; calls hardware crypto path | algorithm/key/IV not established solely from selector |
| UART LSR | UARTbase0x11004000 +0x14; unbounded bit5 wait | LSR0 measured; not a causal proof for every failure |
| Common return0x233AE | original MOV R0,R5 required on rejection/constructor/decrypt/write routes | early NOP could leak logger length0x1A |

The corrected write-error instrumentation uses MOVS R5,R0 at0x233AA and0x2343A; it preserves the real write result for the common epilogue. N/Z equivalence to a zero comparison was checked, while C/V differences were explicitly acknowledged and examined against dependent branches. The published source is not a proof of every possible computed jump or asynchronous interrupt state.

The final context wrapper captures the actual config and word used by the gate, preserves ABI/stack/context and records caller LR plus a read-present flag. A temporary context pointer at0x41E1C510 is scratch RAM, not a storage write. Capture frame/stack analysis and local harness results are evidence of the reviewed code, not universal MMU/concurrency safety.

## Unlock marker map (hex stage IDs)

| Stage | Meaning |
|---|---|
|14 /15 | before/after original erase/commit |
|18 | earlier corrected-V3 gate return marker |
|19 /1A | before/after actual constructor |
|16 /17 | before/after encryption |
|1E /1F | before/after each actual storage write; before carries caller LR |
|28–2D | decimal40–45: config, DWORD, argument, result, callerLR, MMIO-read-present |

A stage ID1A is not itself an error0x1A. CallerLR0x41E2320B identifies the actual unlock gate call at file offset0x23406. Write callerLRs0x41E231AB and0x41E2323B distinguish the two storage paths. In the successful raw response each is followed by a zero return.

## Version matrix

| Version | SHA256 | Result |
|---|---|---|
|Factory LK|07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596|restored and independently reported unlocked=yes|
|V1|3767d4a1c3bd01a5490a83962cf52af12a8d0cde30e9cc4585c7649610551830|live config/selector/UARTbase diagnostic; not an unlock|
|Initial V3|aa5b48b4acb264c981cdc6b267b85d6c994f1cb46af8f7dcd3f17bdfb61c74e8|unlock failed0x1A; return instrumentation flawed|
|Corrected V3|0e57325503671d4e9ae6daa54f392542623477914928439097bbae3252f8f684|diagnostic passed; actual unlock gate1/header0x3001|
|Actual-reader context build|f566f0a28297f9459978a41b61c7b3ce254f5ad0e3cc4ec71fa37e094bbe8077|original unlock completed; independent yes; persistence later verified|

No patched binary is bundled. The assembler and patch builder are project-source review candidates; their ownership and derivative licensing remain subject to LICENSE_REVIEW.md.
