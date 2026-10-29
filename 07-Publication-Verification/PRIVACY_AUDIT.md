# Privacy and repository-history audit —23October2026

The clean repository was constructed only from a verified prior file manifest and newly authored reviewed documentation/helpers. No recursive private-project copy was made. All41 historical source/build snapshots and all old tool ZIPs are outside the upload allowlist. No vendor executable, firmware/DA/LK image, raw device dump, private approval, credential, signing key, archive password or account-session file is selected.

Every selected JSON/text/helper and the only photo were checked. The photo was visually reviewed and parsed for metadata: no APP1–APP15 or JPEG-comment segment remains. It shows PCB components, not unique label identifiers or an invented unlock/UART result. Pattern scans found no actual owner-profile path, known private serial digest, standalone15-digit identifier, private-key block or common GitHub token value. A pattern scan is bounded evidence, not a universal secrecy guarantee.

The new .git was initialized with an empty template, has no commit, no remote, no hooks and no object alternates. It does not inherit the private working tree's history or account configuration into tracked content. .git is excluded from release ZIPs; hidden tracked content is limited to the reviewed .gitignore. No global Git settings were changed, no commit identity was chosen and no files were staged or uploaded.

Source-rights eligibility remains a separate release gate. The public allowlist manifest enumerates exact eligible-for-review content and hashes; owner approval of a concrete upload is still required even for a private remote repository.
