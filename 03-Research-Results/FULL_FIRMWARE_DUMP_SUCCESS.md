# Verified readable firmware extraction

The9October stock-DA Windows pipeline saved all23 GPT partitions, Boot1 andBoot2, and the full3825205248-byte eMMC User area. The independent final verification checked31 principal files and matched each partition against its full-User slice. GPT primary/backup CRCs and entries were verified; the two4MiB boot regions differed and were retained separately.

This is a complete backup of the requested readable ranges, not a clone of RPMB or every eMMC register. RPMB contents/keys/counters, CSD andEXT_CSD were not read. The archive remains private. Derived FILE_INFO/EMI slices were not extra flash reads or proven rescue loaders. See the [complete extraction guide](../01-Firmware-Extraction/COMPLETE_EXTRACTION_GUIDE.md).
