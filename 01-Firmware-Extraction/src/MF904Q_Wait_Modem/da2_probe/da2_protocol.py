# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Bounded stock Legacy DA2 framing, flash geometry and 34 User sectors.

Source: MTKClient cd25cf9 dalegacy_lib.py, brom_send/read_flash_info/readflash.
No transports, patches, EMI, erase/write commands or USB reconfiguration.
"""
import struct,time,zlib

class Failure(Exception):
    def __init__(self,status,message):super().__init__(message);self.status=status

def exact(receive,n):
    data=receive(n)
    if len(data)!=n:raise TimeoutError(f'Partial reply: {len(data)}/{n}')
    return data

def ack(receive,phase):
    response=exact(receive,1)
    if response!=b'\x5a':raise Failure('DA2_REJECTED',f'{phase} expected 5A, received {response.hex()}')

def upload(send,receive,event,blob,sleep=time.sleep):
    if len(blob)!=222752:raise ValueError('Wrong stock DA2 size')
    event('DA2_PHASE',phase='HEADER')
    for value in (0x40000000,len(blob),0x1000):send(struct.pack('>I',value))
    ack(receive,'header')
    for offset in range(0,len(blob),0x1000):
        event('DA2_PHASE',phase='PAYLOAD',offset=offset)
        send(blob[offset:offset+0x1000]);ack(receive,f'packet at {offset}')
    sleep(.5) # Upstream interval after the last accepted packet.
    event('DA2_PHASE',phase='START')
    send(b'\x5a');ack(receive,'stage2 start')
    # No recovery ACK is sent after a rejected packet (upstream can fall through).

def geometry(receive):
    source_receive=receive;chunks=[]
    def receive(n):
        data=source_receive(n);chunks.append(data);return data
    nor=exact(receive,28);nand=exact(receive,17)
    count64=int.from_bytes(nand[15:17],'big')
    carry=bytearray()
    if count64:
        count=count64;layout=64
    else:
        # Upstream chooses the 32-bit layout when the 64-bit count is zero.
        # Its 17-byte read already contains 4 bytes after the 13-byte header.
        count=int.from_bytes(nand[11:13],'big');layout=32;carry.extend(nand[13:17])
    if count>16:raise Failure('DA2_GEOMETRY_FAILED','NAND ID count exceeds bounded parser')
    def take(n):
        have=min(n,len(carry));data=bytes(carry[:have]);del carry[:have]
        return data+exact(receive,n-have) if n>have else data
    ids=take(count*2);nand2=take(9);emmc=take(92);sdc=take(28);config=take(38);passed=take(10)
    if carry:raise Failure('DA2_GEOMETRY_FAILED','Unconsumed geometry bytes')
    # Same final-pass framing as upstream; only consume the optional extra byte.
    if passed[0]!=0x5a:
        if int.from_bytes(passed[1:5],'big')&255!=0x5a:
            raise Failure('DA2_GEOMETRY_FAILED','Flash-info final pass ACK missing')
        take(1)
    ret,*sizes=struct.unpack('>I8Q',emmc[:68])
    ext_ret=int.from_bytes(config[8:12],'big');ext_size=int.from_bytes(config[14:22],'big')
    if ret!=0 or sizes[-1]<34*512 or sizes[-1]%512:
        raise Failure('DA2_GEOMETRY_FAILED','eMMC status/capacity invalid; no flash read')
    if ext_ret!=0 or ext_size==0:
        raise Failure('DA2_GEOMETRY_FAILED','External RAM status/size invalid; no flash read')
    raw=b''.join(chunks)
    return dict(emmc_status=ret,boot1_size=sizes[0],boot2_size=sizes[1],rpmb_size=sizes[2],
                gp_sizes=sizes[3:7],user_size=sizes[7],ext_ram_status=ext_ret,
                ext_ram_type=config[12],ext_ram_size=ext_size,
                nand_layout=layout,nand_count=count,
                cid_wire_hex=emmc[68:84].hex(),emmc_fw_hex=emmc[84:92].hex()),raw

def read_user_prefix(send,receive,event,user_size):
    length=34*512
    if user_size<length or user_size%512:raise ValueError('Invalid bounded read geometry')
    event('DA2_PHASE',phase='READ_USER_PREFIX')
    send(b'\x72');ack(receive,'USB status query')
    speed=exact(receive,1)[0]
    if speed not in (0,1,2):raise Failure('DA2_READ_FAILED','Unexpected USB speed status; no reconfiguration')
    # User partition selection is volatile; no eMMC programming command.
    send(b'\x60');ack(receive,'partition switch command')
    send(b'\x08');ack(receive,'User partition selection')
    # Exact upstream READ_CMD framing uses host=0C even on Windows.
    for part in (b'\xd6',b'\x0c',b'\x02',struct.pack('>Q',0),
                 struct.pack('>Q',length),struct.pack('>I',0x100000)):send(part)
    ack(receive,'read command')
    data=exact(receive,length);reported=int.from_bytes(exact(receive,2),'big')
    calculated=sum(data)&0xffff
    if reported!=calculated:
        raise Failure('DA2_READ_FAILED',f'Read checksum mismatch: {reported:04X}/{calculated:04X}')
    send(b'\x5a')
    return data,dict(read_offset=0,read_length=length,read_checksum=f'0x{reported:04X}',usb_speed_status=speed)

def partition_summary(data,user_size):
    """Validate GPT present in captured prefix; do not expose unique GUIDs."""
    out={'mbr_signature':len(data)>=512 and data[510:512]==b'\x55\xaa',
         'gpt_header_present':data[512:520]==b'EFI PART','gpt_complete':False}
    if not out['gpt_header_present']:return out
    h=data[512:1024];size=int.from_bytes(h[12:16],'little')
    if not 92<=size<=512:return dict(out,gpt_error='Invalid header size')
    copy=bytearray(h[:size]);expected=int.from_bytes(copy[16:20],'little');copy[16:20]=bytes(4)
    if zlib.crc32(copy)&0xffffffff!=expected:return dict(out,gpt_error='Header CRC mismatch')
    current,backup,first,last=struct.unpack_from('<4Q',h,24)
    table_lba,count,entry_size,table_crc=struct.unpack_from('<QIII',h,72)
    if current!=1 or backup>=user_size//512 or first>last or last>=user_size//512:
        return dict(out,gpt_error='Header LBA range invalid')
    out.update(gpt_header_crc_valid=True,entry_count=count,entry_size=entry_size,table_lba=table_lba)
    if count==0 or count>4096 or entry_size<128 or entry_size%8:
        return dict(out,gpt_error='Entry layout outside parser bounds')
    start=table_lba*512;end=start+count*entry_size
    if start<1024 or end>len(data):return dict(out,gpt_error='Complete entry array outside captured prefix')
    table=data[start:end]
    if zlib.crc32(table)&0xffffffff!=table_crc:return dict(out,gpt_error='Entry CRC mismatch')
    parts=[]
    for i in range(count):
        entry=table[i*entry_size:(i+1)*entry_size]
        if entry[:16]==bytes(16):continue
        a,b=struct.unpack_from('<QQ',entry,32)
        if a<first or b<a or b>last:return dict(out,gpt_error='Partition LBA range invalid')
        parts.append(dict(name=entry[56:128].decode('utf-16-le',errors='replace').split('\0')[0],
                          first_lba=a,last_lba=b,size=(b-a+1)*512))
    return dict(out,gpt_complete=True,gpt_entries_crc_valid=True,partitions=parts)
