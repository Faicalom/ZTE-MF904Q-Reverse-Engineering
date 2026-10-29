# Verified partition map

| Partition | First–last LBA | Byte offset | Bytes | Output | SHA256 | Verification |
|---|---:|---:|---:|---|---|---|
| proinfo | 1024–7167 | 524288 | 3145728 | `05_Private_Device_Data/proinfo.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| nvram | 7168–17407 | 3670016 | 5242880 | `05_Private_Device_Data/nvram.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| protect1 | 17408–37887 | 8912896 | 10485760 | `05_Private_Device_Data/protect1.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| protect2 | 37888–58367 | 19398656 | 10485760 | `05_Private_Device_Data/protect2.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| lk | 58368–59391 | 29884416 | 524288 | `04_Firmware_Partitions/lk.bin` | `07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596` | Historical PASS |
| para | 59392–60415 | 30408704 | 524288 | `05_Private_Device_Data/para.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| boot | 60416–93183 | 30932992 | 16777216 | `04_Firmware_Partitions/boot.bin` | `4754bb57ddca9bc0780bfbb1093702713c5829f50773793945eccf002513d6a2` | Historical PASS |
| recovery | 93184–125951 | 47710208 | 16777216 | `04_Firmware_Partitions/recovery.bin` | `b9e477fdeba6cf75a00e1df30bc5e14b62ed42309733385707417202476836e0` | Historical PASS |
| logo | 125952–142335 | 64487424 | 8388608 | `04_Firmware_Partitions/logo.bin` | `b703c7b9e24a80069006b3ccce87ae9b109f3cff596ec2aa9ff25dded6ab524a` | Historical PASS |
| expdb | 142336–162815 | 72876032 | 10485760 | `05_Private_Device_Data/expdb.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| seccfg | 162816–163839 | 83361792 | 524288 | `05_Private_Device_Data/seccfg.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| oemkeystore | 163840–167935 | 83886080 | 2097152 | `05_Private_Device_Data/oemkeystore.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| secro | 167936–180223 | 85983232 | 6291456 | `05_Private_Device_Data/secro.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| keystore | 180224–196607 | 92274688 | 8388608 | `05_Private_Device_Data/keystore.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| tee1 | 196608–206847 | 100663296 | 5242880 | `04_Firmware_Partitions/tee1.bin` | `8485339e418cd1151e02e6f35391b08059052c1fd6cfc3678768fa1a4807e125` | Historical PASS |
| tee2 | 206848–217087 | 105906176 | 5242880 | `04_Firmware_Partitions/tee2.bin` | `8485339e418cd1151e02e6f35391b08059052c1fd6cfc3678768fa1a4807e125` | Historical PASS |
| frp | 217088–219135 | 111149056 | 1048576 | `05_Private_Device_Data/frp.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| nvdata | 219136–284671 | 112197632 | 33554432 | `05_Private_Device_Data/nvdata.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| metadata | 284672–360447 | 145752064 | 38797312 | `05_Private_Device_Data/metadata.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| system | 360448–1589247 | 184549376 | 629145600 | `04_Firmware_Partitions/system.bin` | `9bb23ccc2a0347f0a506ed3a0d2a6784593e8f0a4d4f1d01d79f2d68d56cbe80` | Historical PASS |
| cache | 1589248–2408447 | 813694976 | 419430400 | `05_Private_Device_Data/cache.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| userdata | 2408448–7437311 | 1233125376 | 2574778368 | `05_Private_Device_Data/userdata.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |
| flashinfo | 7437312–7470079 | 3807903744 | 16777216 | `05_Private_Device_Data/flashinfo.bin` | `WITHHELD_PRIVATE_PARTITION_DIGEST` | Historical PASS |

All rows use the historical bounded DA2 read API documented in COMPLETE_EXTRACTION_GUIDE.md. Private partition hashes are intentionally withheld; their completeness is attested by the independently verified historical manifest. Firmware hash entries are reference fingerprints, not redistributed images. LBA units are 512 bytes; this is not a claim about physical sector size.
