# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Pure framing and bounded handshake policy; no OS or device access."""
class ProtocolMismatch(RuntimeError):pass
class HandshakeParser:
    TX=b'\xa0\x0a\x50\x05'
    RX=b'\x5f\xf5\xaf\xfa'
    def __init__(self,on_next=None):
        self.index=0;self.buffer=bytearray();self.ready_count=0;self.on_next=on_next
    @property
    def complete(self):return self.index==4
    def feed(self,data):
        self.buffer.extend(data)
        while self.buffer:
            if self.complete:raise ProtocolMismatch('Extra bytes after handshake: '+self.buffer.hex())
            if self.buffer[0]==ord('R'):
                available=bytes(self.buffer[:5])
                if not b'READY'.startswith(available):raise ProtocolMismatch('Malformed READY prefix: '+available.hex())
                if len(available)<5:return
                del self.buffer[:5];self.ready_count+=1
                if self.ready_count>64:raise ProtocolMismatch('READY banner limit exceeded')
                continue
            got=self.buffer.pop(0);expected=self.RX[self.index]
            if got!=expected:raise ProtocolMismatch(f'Handshake RX={got:02x}, expected={expected:02x}, phase={self.index}')
            self.index+=1
            if self.index<4 and self.on_next:self.on_next(self.TX[self.index])

def bounded_handshake(read, write, event, now, max_attempts=5,
                      total_timeout=1.5, phase_timeout=.12, late_grace=.04):
    """Bounded official-style restart, with whole READY frames and recorded drain.

    No reopen, control-line toggles, or mode commands. Transport exceptions abort
    immediately. A partial response never authorizes GET_HW_CODE.
    """
    total_end=now()+total_timeout
    stats={'attempts':0,'ready_count':0,'phases':0,'complete':False}
    last_reason='no reply'
    for attempt in range(1,max_attempts+1):
        if now()>=total_end:break
        stats['attempts']=attempt
        phase_end=now()+phase_timeout
        def transmit(value):
            nonlocal phase_end
            if now()>=total_end:raise TimeoutError('Total handshake deadline before TX')
            write(value)
            phase_end=min(total_end,now()+phase_timeout)
        parser=HandshakeParser(transmit)
        event('ATTEMPT_START',attempt=attempt)
        transmit(0xa0)
        try:
            while not parser.complete and now()<min(total_end,phase_end+late_grace):
                data=read(1)
                if data:parser.feed(data)
            if parser.complete:
                stats.update(complete=True,phases=4,ready_count=stats['ready_count']+parser.ready_count)
                event('BOUNDED_HANDSHAKE_RESULT',**stats)
                return stats
            last_reason=f'phase timeout ({parser.index}/4)'
        except ProtocolMismatch as exc:
            # Parser mismatch, not a transport failure. Restart at A0 as upstream.
            # read/write exceptions must not be converted into retryable mismatches.
            last_reason=str(exc)
        stats['ready_count']+=parser.ready_count;stats['phases']=parser.index
        event('ATTEMPT_END',attempt=attempt,reason=last_reason,
              phases=parser.index,ready_count=parser.ready_count,pending_hex=parser.buffer.hex())
        if attempt==max_attempts or now()>=total_end:break
        # Preserve every drained byte through the read adapter's RX recorder.
        # Same purpose as upstream USB retry flush, without discarding raw evidence.
        drain_end=min(total_end,now()+.04)
        drained=bytearray(parser.buffer)
        while now()<drain_end:
            data=read(1)
            if not data:break
            drained.extend(data)
        event('RETRY_DRAIN',attempt=attempt,hex=drained.hex())
        # Do not transmit in the middle of a known fragmented READY frame.
        for suffix in (b'R',b'RE',b'REA',b'READ'):
            if drained.endswith(suffix):
                event('BOUNDED_HANDSHAKE_RESULT',**stats,reason='partial READY at retry boundary')
                raise TimeoutError('Partial READY at retry boundary; no blind retransmission')
    event('BOUNDED_HANDSHAKE_RESULT',**stats,reason=last_reason)
    raise TimeoutError(f'Handshake failed after {stats["attempts"]} bounded attempts: {last_reason}')
