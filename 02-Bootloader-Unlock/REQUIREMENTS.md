# Unlock requirements

* Examined WF904_V6.0 build and original LK SHA256 `07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596`, 524288 bytes. Any mismatch invalidates the patch offsets.
* Verified complete private backup and original LK before modification; documented independent DA transport plus a reviewed LK-only recovery action. The working extraction transport is not itself an unlock tool.
* Windows host, historical Python environment, fastboot binary verified by the original `entry.verify()` path, correct USB metadata/reference and isolated device selector. The10October report pins fastboot37.0.1-15733141 and its SHA256; this was recovered during the subsequent F archive review.
* Original unmodified DA1/DA2 inputs and source-level dependencies, not distributed here. Successful LK install was conditional on the preceding LK digest and matching GPT/storage identity.
* Build source uses NDK `28.2.13676358` LLVM, `--target=armv7a-none-eabi`, Thumb, and the supplied linker script. Source path to the original user's SDK was replaced by an explicit `YOUR_WINDOWS_USER` placeholder in publication copies; it is not a tested portable build configuration.
* Final measured image f566…8077; diagnostic response must be complete, ordered and successful before a separately authorized unlock.
* Separate explicit decisions for LK installation, diagnostic transition, unlock submission, manual WPS confirmation, and later persistence/restoration testing. Unlock can erase userdata and write seccfg.

No UART wire, test point, hardware opening, eFuse write, FRP bypass, generic exploit or direct seccfg synthesis is established as a necessary action in the successful flow. Historical photographs of an open PCB are not evidence that an electrical connection was used.


## Additional archival version evidence recovered from F

The preserved offline check records Python3.13.14 x64 and pyserial3.5; the unlock serial manifest also pins pyserial3.5. The10October entry report pins fastboot37.0.1-15733141, SHA256b2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86. This updates earlier missing-version notes: that Fastboot version is recoverable. A complete environment lock across every historical extraction attempt remains unestablished. See the prerequisite chapter in the unlock folder for exact evidence distinctions.
