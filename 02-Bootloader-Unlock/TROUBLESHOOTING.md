# Actual unlock failures

| Symptom | Supported interpretation | Proven response / limit |
|---|---|---|
|LK install source missing struct import|host failure before write in that attempt|fix import locally; later independent install succeeded|
|USB diagnostic works, UART LSR0|UART unbounded wait can block examined path|single-poll/non-blocking correction retained; not proof for every hang|
|Initial V3 remote0x1A|complete remote error; shared-return patch could leak26-byte logger result|restore epilogue and preserve actual write results narrowly|
|Corrected V3 remote0x3001 plus gate1|header-load failure propagated after constructor rejection|do not call it USB or storage-write failure; capture actual gate inputs|
|Standalone diagnostic gate0 but unlock gate1|different measured outcomes, old rejection inputs absent|context capture at the actual reader; do not force config/bit|
|Missing or reordered INFO marker|capture or protocol validity unknown|strict parser rejects; OKAY alone is insufficient|
|Only root or Arabic LCD appearance|neither proves bootloader state|independent complete getvar before/after and factory-LK persistence|
|Unlock fails after erase path|userdata might already have changed|do not assert no wipe merely because no write marker arrived|

The successful run does not retroactively prove a cause for every earlier error. No repeated unlock is proposed in this publication phase.
