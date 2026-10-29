# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Bounded unpatched Legacy DA1 only. No transport imports, DA2, ACK or init."""
import struct
import time

class ProbeFailure(Exception):
    def __init__(self, status, reason):
        self.status=status
        super().__init__(reason)

def checksum(data):
    if len(data)%2:
        raise ValueError('Selected DA1 must have even length; no padding/patch')
    value=0
    for word in struct.iter_unpack('<H',data):value ^= word[0]
    return value

def probe(send, receive, event, blob, address, signature_length, sleep=time.sleep):
    # send/receive callbacks must impose transport deadlines. No automatic retries.
    phase='SEND'
    def echo(data):
        send(data)
        actual=receive(len(data))
        if actual!=data:raise ValueError('Echo mismatch '+actual.hex())
    def status_zero(label):
        status=struct.unpack('>H',receive(2))[0]
        if status!=0:raise ValueError(f'{label} status 0x{status:04X}; no auth/bypass fallback')
    try:
        if not blob or signature_length<=0 or signature_length>len(blob):
            raise ValueError('DA1/signature bounds invalid')
        expected=checksum(blob)
        event('DA1_PHASE',phase=phase)
        for data in (b'\xd7',struct.pack('>I',address),struct.pack('>I',len(blob)),struct.pack('>I',signature_length)):
            echo(data)
        status_zero('SEND_DA header')
        for offset in range(0,len(blob),0x400):
            send(blob[offset:offset+0x400])
        # Audited upstream upload_data waits .12s before checksum/status.
        sleep(.12)
        returned,status=struct.unpack('>HH',receive(4))
        if status!=0 or returned!=expected:
            raise ValueError(f'Upload checksum/status mismatch checksum=0x{returned:04X}, status=0x{status:04X}')
        phase='JUMP';event('DA1_PHASE',phase=phase)
        echo(b'\xd5')
        send(struct.pack('>I',address))
        if receive(4)!=struct.pack('>I',address):raise ValueError('Jump address mismatch')
        status_zero('JUMP_DA')
        sleep(.1)
        phase='SYNC';event('DA1_PHASE',phase=phase)
        if receive(1)!=b'\xc0':raise ValueError('Expected DA1 sync C0')
        phase='STORAGE';event('DA1_PHASE',phase=phase)
        nand_info=struct.unpack('>I',receive(4))[0]
        count=struct.unpack('>H',receive(2))[0]
        if count>16:raise ValueError(f'NAND ID count {count} exceeds bounded probe limit')
        nand_ids=list(struct.unpack('>'+str(count)+'H',receive(count*2))) if count else []
        emmc_info=struct.unpack('>I',receive(4))[0]
        emmc=receive(16)
        words=struct.unpack('>4I',emmc)
        # Matches upstream first-ID classification; never infer size or Kingston.
        if nand_ids and nand_ids[0]!=0:kind='nand'
        elif words[0]!=0:kind='emmc'
        else:raise ValueError('No usable initial NAND/eMMC ID; NOR classification alone is insufficient')
        result=dict(storage_type_initial=kind,nand_info=f'0x{nand_info:08X}',
                    nand_ids=nand_ids,emmc_info=f'0x{emmc_info:08X}',
                    emmc_ids_raw_hex=emmc.hex(),cid_confirmed=False,
                    capacity_known=False,da2_sent=False,ack_sent=False)
        event('DA1_INITIAL_STORAGE',values=result)
        # Critical boundary: NO 5A ACK; no set_stage2_config, EMI, DA2 or reset.
        return result
    except Exception as exc:
        code={'SEND':'DA1_REJECTED','JUMP':'DA1_REJECTED',
              'SYNC':'DA1_SYNC_FAILED','STORAGE':'DA1_STORAGE_FAILED'}[phase]
        raise ProbeFailure(code,f'{phase}: {type(exc).__name__}: {exc}') from exc
