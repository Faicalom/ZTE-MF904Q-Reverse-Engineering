# Real extraction failures and validated responses

| Observed error | Cause classification | Recorded response | Avoid |
|---|---|---|---|
| Missing Preloader driver | confirmed Windows driver issue | installed recorded VCOM driver, ProblemCode became0 | inferring flash protection from missing COM |
| READY without 5F | failed handshake, underlying reason not fully established | stop; review receive timing/banner parser | calling READY success or uploading DA anyway |
| 5F then A1 after excess A0 | reply alignment ambiguous | parser/source review and bounded staged exchange | asserting A1 definitely replied to0A |
| Waiting for FriendlyName | possible time-window loss, not retrospective measurement | detect VID/PID before naming | declaring measured latency when timestamps do not exist |
| Short range/checksum mismatch | transport integrity failure; exact hardware cause may be unknown | preserve partial output and stop | silent retry or accepting corrupted block |
| Changed CID/geometry/prefix | source fails identity gate | stop before additional reads | editing references to force acceptance |
| Missing private approval or insufficient disk | explicit preflight failure | no COM opened, correct host preparation | bypassing private-data scope |

No guessed workaround is labeled a successful device experiment. Later LK-specific handshake corrections belong to their own source/version; do not overwrite the successful 9 October backup transport just because a newer file exists.
