# Open technical questions

1. Why did the earlier corrected unlock attempt observe gate1 when a standalone diagnostic observed0? Inputs at the old rejection were not captured; later success does not explain them.
2. What event powers off or resets the persistent Arabic system after boot? The trace does not establish panic, watchdog, explicit shutdown, service crash or electrical cause.
3. Why did internal logger evidence stop around30–31seconds without a terminal record? The unmatched final BEFORE_SYNC is not proof of an indefinitely blocked fsync.
4. How can ROOT.war source/runtime/extracted cache be made transactionally consistent without adding a new firmware variable? The existing plan describes requirements but did not prove its deployment guard.
5. Is the owner-reported LCD_ONLY attempt a clean stock-WebUI comparison? Not without saved runtime hashes/cache proof.
6. Can a matching B restore result and runtime ROOT state be added from existing later records? No new device access is requested here.
7. Which source portions are fully project-owned and which require upstream/vendor permission or attribution? A repository license remains the owner's decision.
8. What is the full reproducible live dependency/environment closure? The current source snapshot is reviewable, not a tested portable deployment kit.
