# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Only FC/D8 query framing. No MTK init, memory writes, DA or identifier reads."""
import struct
def decode_versions(data):
    if len(data)!=8:raise ValueError('FC requires exactly 8 bytes')
    sub,hw,sw,status=struct.unpack('>HHHH',data)
    value={'hw_subcode':f'0x{sub:04X}','hw_version_fc':f'0x{hw:04X}',
           'sw_version':f'0x{sw:04X}','fc_trailing_word':f'0x{status:04X}'}
    # Upstream returns all four words but init uses only the first three.
    # Do not assert a meaning for word four; conservatively stop if nonzero.
    if status:raise ValueError('FC nonzero trailing word; interpretation unconfirmed: '+value['fc_trailing_word'])
    return value
def decode_config(data):
    if len(data)!=6:raise ValueError('D8 requires exactly 6 bytes')
    flags,status=struct.unpack('>IH',data)
    if status:raise ValueError(f'D8 nonzero status 0x{status:04X}; protection unknown')
    bits={'sbc':1,'sla':2,'daa':4,'epp':8,'cert':16,'memread_auth':32,'memwrite_auth':64,'cmd_c8_blocked':128}
    return {'target_config':f'0x{flags:08X}','d8_status':f'0x{status:04X}',
            'protection_flags':{key:bool(flags&bit) for key,bit in bits.items()},
            'unknown_bits':f'0x{flags&~255:08X}'}
def query(send,receive,event):
    result={}
    for command,size,decoder,label in [(0xfc,8,decode_versions,'GET_HW_SW_VER'),(0xd8,6,decode_config,'GET_TARGET_CONFIG')]:
        event('IDENTITY_QUERY',command=f'{command:02x}',name=label)
        send(command)
        echo=receive(1)
        if echo!=bytes([command]):raise ValueError(f'{label} echo mismatch: {echo.hex()}')
        data=receive(size)
        value=decoder(data);result.update(value)
        event('IDENTITY_QUERY_RESULT',name=label,values=value)
    return result
