# Persistent bootloader unlock was demonstrated

The successful original LK flow completed at05:47:42 +01 on13October2026 using the gate-context image f566…8077. A separate complete query returned `unlocked: yes`, exit0. This was followed by a new-entry persistence check, original-LK restoration with a full524288-byte readback, and another complete yes response under factory LK at06:18:49. Android and mobile Internet were subsequently observed.

The important result is not merely a command returning OKAY. The research distinguishes confirmation input, actual gate/constructor/crypto/write returns, a separate state query, persistence, restored factory code and later functionality. Earlier failed0x1A and0x3001 attempts remain documented, as does the unresolved reason for their context difference. See the [complete guide](../02-Bootloader-Unlock/COMPLETE_UNLOCK_GUIDE.md).
