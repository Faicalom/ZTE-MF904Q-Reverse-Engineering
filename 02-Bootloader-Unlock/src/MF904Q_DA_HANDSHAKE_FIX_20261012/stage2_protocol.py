# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""ACK/config requirement probe only. No EMI, DA2, reset or flash functions."""
import struct,time

def version_queries(send,receive):
    # Upstream get_blver/get_bromver return one byte WITHOUT command echo.
    send(b'\xfe');bl=receive(1)[0]
    if bl==0xfe:raise ValueError('FE indicated BootROM; target is approved Preloader only')
    send(b'\xff');brom=receive(1)[0]
    return dict(bl_version=bl,brom_version=brom)

def config_fields(bl,brom):
    if not (0<=bl<254 and 0<=brom<=255):raise ValueError('Invalid version bytes')
    return [('brom_version',bytes([brom])),('bl_version',bytes([bl])),
            ('nor_chip',struct.pack('>H',8)),('nor_select',b'\x00'),
            ('nand_acccon',struct.pack('>I',0x7007ffff)),('bmt_flag',b'\x01'),
            ('bmt_partition_size',struct.pack('>I',0)),('force_charge',b'\x01'),
            ('reset_keys',b'\x01'),('external_clock',b'\x02'),('msdc_boot_channel',b'\x00')]

def stage2_requirements(send,receive,event,bl,brom,sleep=time.sleep):
    fields=config_fields(bl,brom) # Validate all fields BEFORE sending ACK.
    send(b'\x5a')
    ack_reply=receive(3) # Upstream treats these as opaque; do not invent semantics.
    event('STAGE2_ACK_REPLY',hex=ack_reply.hex(),meaning='opaque upstream 3-byte reply')
    for name,data in fields:
        event('STAGE2_CONFIG_FIELD',name=name,hex=data.hex());send(data)
    sleep(.350) # Exact upstream settle interval, not an added retry.
    code=struct.unpack('>I',receive(4))[0]
    result=dict(stage2_config_return=f'0x{code:08X}',ack_reply_hex=ack_reply.hex(),
                ack_sent=True,stage2_config_sent=True,
                emi_sent=False,da2_sent=False,dram_geometry_verified=False)
    if code==0:
        return 'STAGE2_CONFIG_ACCEPTED',result
    if code!=0xbc3:
        return 'STAGE2_CONFIG_FAILED',result
    # Exact source framing after BC3: extra dword, 16-byte DRAM ID, BC4/count/IDs.
    result['emi_request_extra_hex']=receive(4).hex()
    result['dram_id_raw_hex']=receive(16).hex()
    marker=struct.unpack('>I',receive(4))[0]
    result['dram_nand_marker']=f'0x{marker:08X}'
    if marker!=0xbc4:raise ValueError('Invalid DRAM NAND marker; stop without EMI')
    count=struct.unpack('>H',receive(2))[0]
    if count>16:raise ValueError('DRAM NAND count exceeds 16; stop')
    result['dram_nand_ids']=list(struct.unpack('>'+str(count)+'H',receive(count*2))) if count else []
    return 'EMI_REQUIRED',result # NO E8, ACK, EMI version/data, DA2 or reset follows.
