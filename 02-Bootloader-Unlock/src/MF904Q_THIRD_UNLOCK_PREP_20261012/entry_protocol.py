"""Pure offline state machine. No transport, COM, USB, subprocess or device I/O.
The returned planned_tx must never be interpreted as an executed command.
"""
class ProbeModel:
    TOKENS = (b'READY', b'FASTBOOT', b'TOOBTSAF', b'METAFORB', b'METASLA')
    def __init__(self, approved=False):
        self.approved = approved
        self.state = 'WAIT_READY'
        self.buffer = b''
        self.received = 0
        self.planned_tx = []
        self.events = []
        self.deadline = 1500
    def fail(self, why):
        self.state = why
        self.events.append(why)
    def tick(self, ms):
        if self.state in ('WAIT_READY','WAIT_ACK','ACK_RECEIVED_WAIT_USB') and ms >= self.deadline:
            self.fail('TIMEOUT_' + self.state)
    def feed(self, data, ms):
        self.tick(ms)
        if self.state not in ('WAIT_READY','WAIT_ACK'): return
        self.received += len(data)
        if self.received > 4096:
            self.fail('RX_LIMIT'); return
        self.buffer += data
        while self.buffer and self.state in ('WAIT_READY','WAIT_ACK'):
            if self.buffer[0] in (10,13):
                self.buffer = self.buffer[1:]; continue
            token = next((t for t in self.TOKENS if self.buffer.startswith(t)),None)
            if token is None:
                if any(t.startswith(self.buffer) for t in self.TOKENS): return
                self.fail('UNEXPECTED_RX'); return
            self.buffer = self.buffer[len(token):]
            self.events.append(token.decode('ascii'))
            if token in (b'METAFORB',b'METASLA'):
                self.fail('FORBIDDEN_OR_AUTH_REQUIRED'); return
            if self.state == 'WAIT_READY':
                if token != b'READY': self.fail('UNEXPECTED_BEFORE_READY'); return
                if not self.approved: self.fail('APPROVAL_REQUIRED'); return
                self.planned_tx.append(b'FASTBOOT')
                self.state = 'WAIT_ACK'; self.deadline = ms + 1500
            elif token == b'TOOBTSAF':
                self.state = 'ACK_RECEIVED_WAIT_USB'; self.deadline = ms + 10000
                if self.buffer.strip(b'\r\n'): self.fail('TRAILING_RX')
                return
            # READY repetition and FASTBOOT reflection are not acknowledgements.
    def disconnected(self):
        if self.state in ('WAIT_READY','WAIT_ACK'): self.fail('USB_LOST_BEFORE_ACK')
        elif self.state == 'ACK_RECEIVED_WAIT_USB': self.events.append('EXPECTED_REENUMERATION')
    def observe_fastboot_interface(self, same_physical_target=False, class_code=None, subclass=None, protocol=None, ms=0):
        self.tick(ms)
        if self.state != 'ACK_RECEIVED_WAIT_USB': return
        if same_physical_target and (class_code,subclass,protocol)==(0xff,0x42,0x03):
            self.state='FASTBOOT_INTERFACE_OBSERVED'
        else: self.events.append('UNRELATED_OR_UNCONFIRMED_INTERFACE')
