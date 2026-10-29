# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Bounded receive-driven synchronization; no OS access or mode commands."""
from protocol import HandshakeParser, ProtocolMismatch

def readiness_handshake(read,write,event,now,max_attempts=5,total_timeout=1.5,
                        phase_timeout=.12,late_grace=.04):
    end=now()+total_timeout;window=phase_timeout+late_grace
    stats={'attempts':0,'ready_count':0,'phases':0,'complete':False,'echo_count':0}
    frame=bytearray();permission=False;sent=False;phase_end=now()+window
    def transmit(value):
        nonlocal phase_end
        if now()>=end:raise TimeoutError('Readiness total deadline before TX')
        write(value);phase_end=min(end,now()+window)
    parser=HandshakeParser(transmit)
    def probe():
        nonlocal sent,permission
        stats['attempts']+=1;permission=False;sent=True
        event('ATTEMPT_START',attempt=stats['attempts'],policy='receive_driven')
        transmit(0xa0)
    event('READINESS_LISTEN',budget_seconds=window)
    while now()<end:
        # One initial synchronization probe is allowed after the existing
        # phase budget. Later probes require a fresh complete READY frame.
        if not sent and not frame and (permission or now()>=phase_end):probe()
        elif sent and not frame and parser.index==0 and permission and now()>=phase_end:
            if stats['attempts']<max_attempts:probe()
        if parser.index and now()>=phase_end:
            raise TimeoutError('Partial handshake phase deadline; no restart')
        data=read(1)
        if not data:continue
        if len(data)!=1:raise ValueError('Read adapter must return one byte')
        byte=data[0]
        if frame or byte==ord('R'):
            frame.extend(data)
            if not b'READY'.startswith(frame):raise ProtocolMismatch('Malformed READY: '+frame.hex())
            if frame==b'READY':
                frame.clear();stats['ready_count']+=1
                if stats['ready_count']>64:raise ProtocolMismatch('READY limit')
                event('READY_FRAME',proof='banner only; not handshake success')
                if parser.index==0:permission=True
            continue
        if sent and parser.index==0 and byte==0xa0:
            stats['echo_count']+=1
            event('A0_REFLECTION',count=stats['echo_count'],action='listen; no timer-only retry')
            continue
        if not sent:raise ProtocolMismatch('Unsolicited non-banner byte before TX: '+data.hex())
        parser.feed(data);stats['phases']=parser.index
        if parser.complete:
            stats['complete']=True;event('BOUNDED_HANDSHAKE_RESULT',**stats)
            return stats
    event('BOUNDED_HANDSHAKE_RESULT',**stats,reason='readiness/handshake deadline')
    raise TimeoutError('Readiness/handshake deadline; phases='+str(parser.index)+'/4')
