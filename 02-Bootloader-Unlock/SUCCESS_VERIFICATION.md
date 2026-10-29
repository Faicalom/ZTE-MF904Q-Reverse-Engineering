# Unlock success verification, without circular reasoning

1. Before the successful request, the separate query returned `unlocked: no`, exit0, complete streams.
2. The original unlock request entered `Start unlock flow`, recorded actual gate/config/word values, constructor/encryption/two write returns and commit0, then returned OKAY/exit0 in139.430s.
3. A separate query after process completion returned `unlocked: yes`, exit0, complete streams. The state publisher was not patched to manufacture that value.
4. A later DA read saved a complete524288-byte seccfg and found a valid V3 header and6202 byte differences from the earlier zero-filled state. Its raw contents and device-state digest are private; change alone is not our unlock criterion.
5. A new power/entry session with the instrumented LK returned yes at06:09:42 +01 on13October.
6. Factory LK was restored alone and completely read back at06:15:52. Exact original and readback hash: `07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596`, size524288.
7. After a new entry, factory LK returned `unlocked: yes`, exit0, query0.022s, at06:18:49. The rendered original response is in `evidence/factory_lk_unlocked.txt`.
8. The owner subsequently observed Android and demonstrated cellular Internet through Wi-Fi. That functional result is independent of merely seeing a fastboot property.

These observations separate persistent unlock from a root shell, SIM unlock, a diagnostic parser's OKAY, an in-memory flag or modified-query behavior. They establish persistence over the tested transitions, not permanent immunity to future lock/seccfg changes. No new device query was sent for this publication.
