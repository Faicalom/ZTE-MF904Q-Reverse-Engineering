# Unlock research chronology and failed branches

1. **Before LK work:** Windows firmware extraction succeeded without unlocking. The saved baseline and factory LK were retained.
2. **Original unlock investigation:** complete lock queries reported no; command dispatch, physical confirmation and a pending response were treated separately. A host launch timestamp did not prove command receipt.
3. **KPD1 and USB analysis:** the real confirmation path was investigated; no fabricated electrical pinout or automated key press became the method.
4. **V1 diagnostic:**100 changed bytes, measured config22/selector1/UARTbase11004000. An initial source `struct` import defect prevented writing; it was corrected separately before a later successful install/readback. A host exception before write is not a failed LK image boot.
5. **V2:** live UART LSR0 while USB INFO worked. Its guard skipped constructor/crypto, so neither routine's success nor failure was measured. V2 repurposed callbacks and was incompatible with an older unlock runner.
6. **Initial V3:** UART correction, original unlock handler restored, stage instrumentation. Actual request returned0x1A before crypto/write stages. Later audit identified the shared epilogue logging defect; prior error was not reliable evidence of a failed write.
7. **Corrected V3:** restored MOV R0,R5 and narrowed preservation of real write status. Local76/76 tests included128 low-level flag cases across their harness; these are different counts/scopes, not 204 independent live tests. Diagnostic gate0/constructor0/crypto0; subsequent unlock gate1 and header error0x3001. Config/word at rejection absent.
8. **Final gate-context image:** captured the inputs from real reader instructions, no speculative extra MMIO read or gate bypass.33/33 local checks were reported.13October05:38:30 install/readback matched f566…8077;05:42:03 independent diagnostic measured three consistent contexts.
9. **13October actual successful unlock:**05:45:22.755 request;05:47:42.243 completion; separate yes query. Actual constructor/crypto/two writes/commit returned0. WPS physical timing was not instrumented.
10. **Persistence and original restoration:** new-entry yes, original LK full readback, original-LK new-entry yes, then Android and real mobile Internet. These later results supersede earlier “modified LK remains installed” notes.

The successful context measurement does not explain the older gate1 event. That unresolved causal question is retained rather than rewritten as a deterministic fix to eFuse or hardware security policy.
