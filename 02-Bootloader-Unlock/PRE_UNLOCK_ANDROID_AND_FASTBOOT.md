# Before the winning LK: Android access, OEM permission and native Fastboot entry

> Source review25October2026:50 reviewed historical source/build files are now included under per-file terms;24 GPL-scoped components retain upstream notices,26 independent/factual files have no new blanket license. probe_v3.S is withheld. Vendor binaries and private inputs are absent; no runnable live-tool or full LK rebuild claim. See repository-root LICENSE_REVIEW.md.

This chapter is part of the full unlock history, not an optional generic shortcut. The later successful LK procedure depended on earlier Android/OEM/transport work. No action in this chapter was executed again for publication.

## 1. Identify this actual modem, not a visually similar product

The owner's device was marketed as M19-E; an early comparison with product photographs was corrected by the owner. Read-only Windows/HTTP observations associated it with MF904Q and Jetty/i-jetty. A software hardware_version string such as MF904-V5.0_20240123 was not substituted for the actual PCB marking WF904_V6.0/20231007. A File-CD interface or its apparent zero capacity was not a measurement of eMMC capacity. No firmware from another visually similar modem was used to establish compatibility.

The original data source is `MF904Q_CHATGPT_HANDOFF_20261013/01_ORIGIN_BACKUP_ADB_OEM_AR.md`, cross-checked against stage-specific reports. The full readable backup was completed before the later unlock work, as documented separately.

## 2. Short Android ADB window and original debugging path

Historical Android access showed UID0 and SELinux Disabled. That is a measured state of this build, not a demonstrated exploit or a promise that every MF904Q offers root. The setter attempt's raw id began `uid=0(root) gid=0(root)`; it did not call `adb root` or perform an additional escalation. An initial short-window read or interface name did not establish a durable shell session.

Analysis of BatteryService and DevelopmentSettingsReceiver identified the OEM action `com.lr.usb.openclose` and its debugging/USB branches. The historical original broadcast was:

```sh
/system/bin/am broadcast --user 0 -n com.android.settings/.DevelopmentSettingsReceiver -a com.lr.usb.openclose --ei opendebug 1 --ez frombat false
```

This **changes USB/debugging state** and is not a read-only identity query. It was launched once in a detached session with redirected handles and recorded markers, because the command itself could disrupt ADB. The complete wrapper generator is recoverable from MarkerCore.cs and reproduced below. Its nonce is supplied per session; the broadcast alone is not the full launch command. This is original source, not a newly executed shell recipe.

The separately authorized retrieval on11October07:53:45–48 recovered CONTROL/START/AM_BEGIN/AM_END/END with matching nonce and boot_id, process exit0 and empty stderr. ADB device state had been observed for120.019seconds. Android readback then corroborated actual `rndis,adb` config/state and adb_enabled=1. This established success for that session, not persistence across every future reboot. It must not be repeated on the currently unlocked modem merely to read this documentation.

## 3. Why the ordinary Developer Settings route was not used

The examined Settings code gated its Developer fragment on provisioning. Recorded device_provisioned=0 caused the unavailable/empty branch. Opening an Activity directly did not bypass that original check. PackageManager DEFAULT0 was not proof of a usable visible control on the LCD. The project did not treat a missing `/system/bin/dumpsys` (exit127) as a root denial or OEM prohibition, and did not install a replacement just to hide that result.

The original Settings path and original PersistentDataBlock Binder path both reached the same OEM setter. Binder transaction numbers were recovered from this ROM's Proxy/Stub and implementation, not assumed from another Android version. A direct original service call avoided altering provisioning/Developer Settings state, but still wrote the FRP partition and digest and required explicit approval.

## 4. Establish the original service preconditions

The controlled setter tool revalidated the selected ADB transport and USB identity before each meaningful action. It used the existing ADB server at localhost5037 rather than restarting it or targeting another phone. It discovered transport_id dynamically; a historical number was not reused as identity.

The three actual Android commands in the one setter attempt were:

```sh
/system/bin/id
/system/bin/service call activity 104
/system/bin/service call persistent_data_block 6 i32 1
```

The second queries the original monkey condition, not an input-event injection. Its response was `Parcel(00000000 00000000 ...)`: no exception, boolean false. The controlled tool refused the setter if root was absent, monkey was true, the target changed or the one-attempt latch already existed. It reserved the send before transaction6 and did not automatically execute the post-check.

Required files included the reviewed C# sources/executable, per-scope authorization and the exact-bound device reference. The successful executable fingerprint was0aeca462626fd54bef6d9cc7c46275fd18f7a1a35667e566b1cd40f34d2d9bef. Its C# source snapshots are preserved outside this upload allowlist for rights review; the executable and personal approvals are not distributed. Missing a safe target or authorization meant stop, not selecting the first ADB transport.

## 5. Distinguish Binder acceptance from stored OEM permission

The setter ran11October14:16:55.778–14:16:56.219 +01. Each request reached EOF with the expected nonce and exit0. The setter returned `BINDER_ACCEPTED_STORAGE_UNKNOWN`: no visible Binder exception. The report explicitly did **not** call that a successful bootloader unlock, verified FRP digest or durable flash write.

A separately approved post stage at14:24:54 sent only:

```sh
/system/bin/service call persistent_data_block 7
/system/bin/getprop sys.oem_unlock_allowed
/system/bin/logcat -d -b system -v threadtime 'PersistentDataBlockService:I' '*:S'
```

Getter7 returned true and the property returned1, with complete exit0/EOF. The filtered log request completed with zero retained messages. Its absence of output did not prove no error occurred. The post result was `OEM_TRUE_CORROBORATED_DIGEST_DURABILITY_AND_LK_UNKNOWN`; a later bounded DA investigation corroborated FRP checksum/OEM state separately. No raw FRP image was manufactured or copied from another device.

These stages preserve the original permission path. They are not a claim of bypassing FRP, and they are not “read-only setup”: transaction6 intentionally changes persistent security-related state. The factory LK unlock still had its original FRP/key/gate requirements afterward. The retained source from the Android setter and the final fastboot unlock are distinct tools with distinct side effects.

## 6. Enter Fastboot through the modem's actual Preloader path

The original10October live entry did not use an invented button chord or a generic `adb reboot bootloader`. After the host monitor was ready and the owner connected the powered-off modem, it observed Preloader0E8D:2000. It opened the matched COM port and waited for the bounded READY parser, then sent exactly eight ASCII bytes:

```text
TX ASCII: FASTBOOT
TX HEX:   46 41 53 54 42 4F 4F 54
RX ASCII: READYREADYTOOBTSAF
RX HEX:   52 45 41 44 59 52 45 41 44 59 54 4F 4F 42 54 53 41 46
```

This entry command is different from the A0 complementary handshake used to load the DA. TOOBTSAF acknowledged the Preloader request but was not alone proof of Fastboot operation. The COM port was closed; Windows then observed a new Fastboot interface, VID0BB4/PID0C01, descriptor FF/42/03, using WinUSB. An `Android ADB Interface` friendly name did not mean the protocol was ADB.

The historical timings in UTC were: COM detection06:41:41.670516, open06:41:41.967503, READY06:41:41.989920, transmit completion06:41:41.990143, ACK06:41:42.021753, first Fastboot observation06:41:46.843724. These are host observations, not precise electrical switching times. Complete Fastboot queries subsequently established actual protocol access.

The original runner stopped conservatively when an extra assumed VID gate rejected a legitimate changed VID; the saved response still existed. Later versions used physical-path/identity binding and strict selector matching rather than that false assumption. The winning flow's `entry.py` retains the actual FASTBOOT/TOOBTSAF protocol and one-shot guards. A missing acknowledgment, short write, ambiguous identity, an unrelated Fastboot device or missed window stops the flow without automatic retry/reboot.

## 7. Known host tools and version distinctions

The saved Fastboot entry report identifies platform-tools fastboot37.0.1-15733141, SHA256b2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86. The ADB discovery report records ADB1.0.41 from the same platform-tools version. The preserved third-entry serial manifest records pyserial3.5. The archive's offline runtime check on F records Python3.13.14 x64 and pyserial3.5; that is an archival compatibility check, not a fresh modem run or necessarily a complete historical OS/runtime lock for every earlier attempt.

F was explicitly designated for preservation, not live execution. Complete private source/session dependencies are inside encrypted archives; they were not decrypted or copied into the public package. The14-entry historical tool catalog confirms the successful branches while warning that exact-copy archival does not make every live tool portable.

## 8. Continue only to the exact-build LK investigation

With native Fastboot access and OEM permission separately established, the remaining failed-unlock work investigated KPD1, UART, seccfg loading, constructor, crypto and commit as detailed in COMPLETE_UNLOCK_GUIDE.md. Preloader WPS read transitions were supporting evidence, not proof that LK had identical keypad initialization. Reset was not silently substituted for WPS. No UART connection or unverified test-point short formed this successful software path.

The main guide's staged checks then cover image-specific installation/readback, a measured independent diagnostic, one original unlock request and stock-LK persistence. Skipping this chapter would lose the distinction between gaining transport, granting Android OEM permission and actually changing the bootloader's persistent lock state.


## Exact preserved detached-wrapper generator

Source: MarkerCore.cs, Policy.Launch. The nonce/path guard is defined immediately before this function in the distributed source. This exact function shows the HUP/session/descriptor handling, ptgen gate, progressive marks and am timeout. It is not a newly proposed transport command.

```csharp
    public static string Launch(string nonce) {
        string path=PathFor(nonce);
        string child = "trap \"\" HUP\np=$1\nn=$2\n"+
            "mark() { IFS=\" \" read u rest </proc/uptime || return 21; IFS= read b </proc/sys/kernel/random/boot_id || return 22; echo \"$1 nonce=$n boot=$b up=$u $2\" >>\"$p\"; }\n"+
            "IFS=\" \" read pid comm state ppid pgid sid rest </proc/$$/stat || exit 23\n"+
            "mark START \"pid=$pid pgid=$pgid sid=$sid\" || exit 24\n"+
            "ptgen=$(/system/bin/getprop ro.big.ptgen) || { mark GATE_ERROR \"ptgen_read_failed\"; mark END \"rc=29 sent=0\"; exit 29; }\n"+
            "[ \"$ptgen\" = 1 ] || { mark GATE_REJECTED \"ptgen=$ptgen\"; mark END \"rc=29 sent=0\"; exit 29; }\n"+
            "sys=$(/system/bin/getprop sys.usb.config) || { mark BASELINE_ERROR \"sys_read_failed\"; mark END \"rc=30 sent=0\"; exit 30; }\n"+
            "persist=$(/system/bin/getprop persist.sys.usb.config) || { mark BASELINE_ERROR \"persist_read_failed\"; mark END \"rc=30 sent=0\"; exit 30; }\n"+
            "mark BASELINE \"ptgen=$ptgen sys.usb.config=$sys persist.sys.usb.config=$persist adb_enabled=UNKNOWN_NOT_QUERIED\" || exit 31\n"+
            "mark AM_BEGIN \"\" || exit 26\n"+
            "/system/bin/toybox timeout -k 1 10 "+Forward+" >\"$p.stdout\" 2>\"$p.stderr\"\n"+
            "rc=$?\nmark AM_END \"rc=$rc\" || exit 27\n"+
            "mark END \"rc=$rc\" || exit 28\n";
        return "umask 077\np="+path+"\n"+
            "( set -C; echo 'MF904Q_FROMDEBUG_CONTROL nonce="+nonce+"' > \"$p\" && : >\"$p.stdout\" && : >\"$p.stderr\" ) || exit 20\n"+
            "trap '' HUP\n/system/bin/setsid /system/bin/sh -c '"+child+"' _ \"$p\" "+nonce+" </dev/null >/dev/null 2>>\"$p\" &\n"+
            "echo 'LAUNCHED nonce="+nonce+"'\n";
    }
```
