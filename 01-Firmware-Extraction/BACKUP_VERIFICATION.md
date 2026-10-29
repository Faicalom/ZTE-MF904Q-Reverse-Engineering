# Backup verification: what each layer establishes

1. **Exact transport length:** the receiver must return the requested aligned length, not merely some data. A short response stops the operation and retains the partial evidence.
2. **Per-range checksum:** DA2's 16-bit sum must equal the host calculation before ACK. This is transport integrity, not a signature or collision-resistant image identity.
3. **Repeated independent reads:** initial User prefix and 256 KiB of LK were read repeatedly and compared. This is stronger than repeatedly hashing one host file, but covers only the sampled ranges.
4. **Saved size and SHA256:** all completed manifest entries carry exact sizes and hashes. Intermediate files remain marked incomplete. An image with the right name but wrong length fails.
5. **GPT verification:** primary and backup header CRCs, entry-array CRCs and byte-identical entries were checked. Bounds and partition sizes were validated against the reported User geometry.
6. **Overlap verification:** every one of 23 partition dumps was compared to its offset/length in the independently saved full User image. All matched historically. This cross-check detects misaddressed or mismatched partition outputs.
7. **Private archive round trip:** all 63 archived private/recovery files were decrypted and compared by hash. Password/key retention remained the owner's responsibility; this material is not in the release.

The final summary reports 31 principal payload files, not 31 flash regions: five GPT artifacts include locally derived components. The 63-file private archive count includes recovery support and logs and is not an additional partition count.

Firmware reference hashes are in the partition table. `SHA256SUMS.txt` in this public folder hashes the distributed research files; it deliberately does not pretend factory images are included. The provided offline helper verifies a caller-selected local SHA256 manifest, but has not re-read any modem.

The original full extraction was not repeated for this publication. The current local package's integrity checks validate packaging, source syntax and selected saved evidence, not current flash state. No complete hardware restoration guarantee can be inferred.
