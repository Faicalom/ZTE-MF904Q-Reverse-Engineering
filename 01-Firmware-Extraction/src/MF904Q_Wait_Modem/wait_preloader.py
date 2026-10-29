# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Windows PnP + fast COM fallback; passive by default. No UsbDk or MTK init."""
import argparse
import ctypes as C
from ctypes import wintypes as W
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import queue
import struct
import sys
import threading
import time
import uuid

# Loaded before readiness, never after attachment.
import serial
from serial.tools import list_ports
from protocol import HandshakeParser, bounded_handshake
from windows_usb import preloader_present
from identity_queries import query as query_identity
from readiness_protocol import readiness_handshake

ROOT = Path(__file__).resolve().parent
VID, PID = 0x0E8D, 0x2000
UPSTREAM = 'https://github.com/bkerler/mtkclient/tree/cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3'

class Log:
    def __init__(self, mode):
        self.folder = ROOT/'logs'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.folder.mkdir(parents=True)
        self.start = time.perf_counter_ns()
        self.events = (self.folder/'events.jsonl').open('w', encoding='utf-8')
        self.raw = (self.folder/'rx.bin').open('wb')
        self.text = (self.folder/'session.log').open('w', encoding='utf-8')
        self.result = {'mode': mode, 'status':'WAITING', 'port':None, 'opened':False,
                       'handshake':False, 'hw_code':None, 'hw_version':None,
                       'rx_bytes':0, 'tx_bytes':0, 'da_sent':False}
        self.event('START', upstream=UPSTREAM)
    def event(self, kind, **data):
        row={'utc':datetime.now(timezone.utc).isoformat(timespec='microseconds'),
             'elapsed_ns':time.perf_counter_ns()-self.start, 'event':kind, **data}
        self.events.write(json.dumps(row, ensure_ascii=False)+'\n'); self.events.flush()
    def say(self, message):
        print(message, flush=True)
        self.text.write(message+'\n'); self.text.flush()
    def rx(self, data):
        if data:
            offset=self.result['rx_bytes']; self.raw.write(data); self.raw.flush()
            self.result['rx_bytes']+=len(data)
            self.event('RX', offset=offset, length=len(data), hex=data.hex())
    def finish(self, status, reason):
        self.result.update(status=status, reason=reason)
        self.event('RESULT', **self.result)
        self.raw.close()
        self.result['rx_sha256']=hashlib.sha256((self.folder/'rx.bin').read_bytes()).hexdigest()
        (self.folder/'result.json').write_text(json.dumps(self.result, ensure_ascii=False, indent=2),encoding='utf-8')
        self.say(f"RESULT: {status} — {reason}")
        self.say(f"Logs: {self.folder}")
        self.events.close(); self.text.close()

class GUID(C.Structure):
    _fields_=[('data', C.c_ubyte*16)]
class FilterUnion(C.Union):
    _fields_=[('guid',GUID),('handle',W.HANDLE),('instance',W.WCHAR*200)]
class NotifyFilter(C.Structure):
    _fields_=[('size',W.DWORD),('flags',W.DWORD),('type',W.DWORD),('reserved',W.DWORD),('u',FilterUnion)]

class Pnp:
    """Callbacks do no I/O: enqueue timing and wake the inventory worker."""
    def __init__(self, wake, notifications):
        self.wake, self.notifications = wake, notifications
        self.handles=[]; self.callbacks=[]
        self.dll=C.WinDLL('cfgmgr32.dll')
        self.callback_type=C.WINFUNCTYPE(W.DWORD,W.HANDLE,C.c_void_p,W.DWORD,C.c_void_p,W.DWORD)
        self.dll.CM_Register_Notification.argtypes=[C.POINTER(NotifyFilter),C.c_void_p,self.callback_type,C.POINTER(W.HANDLE)]
        self.dll.CM_Register_Notification.restype=W.DWORD
        self.dll.CM_Unregister_Notification.argtypes=[W.HANDLE]
        self.dll.CM_Unregister_Notification.restype=W.DWORD
        try:
            for name, identifier in [('USB','a5dcbf10-6530-11d2-901f-00c04fb951ed'),
                                      ('COM','86e0d1e0-8089-11d0-9ce4-08003e301f73')]:
                def callback(handle, context, action, event_data, size, kind=name):
                    self.notifications.put((time.perf_counter_ns(),kind,int(action)))
                    self.wake.set()
                    return 0
                cb=self.callback_type(callback)
                f=NotifyFilter(); f.size=C.sizeof(f)
                f.u.guid=GUID((C.c_ubyte*16).from_buffer_copy(uuid.UUID(identifier).bytes_le))
                h=W.HANDLE()
                rc=self.dll.CM_Register_Notification(C.byref(f),None,cb,C.byref(h))
                if rc: raise RuntimeError(f'PnP {name} registration failed: CR={rc}')
                self.handles.append(h); self.callbacks.append(cb)
        except Exception:
            self.close(); raise
    def close(self):
        for h in self.handles:self.dll.CM_Unregister_Notification(h)
        self.handles=[]

def inventory():
    # Enumerates cached Windows COM properties; no device is opened here.
    return list(list_ports.comports())

def choose(rows):
    matches=[p for p in rows if p.vid==VID and p.pid==PID]
    if len(matches)>1:raise RuntimeError('Multiple 0E8D:2000 ports; refusing ambiguous target')
    return matches[0] if matches else None

def make_port(active):
    p=serial.Serial(port=None,baudrate=115200,bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,
                    timeout=.02,write_timeout=.2,xonxoff=False,rtscts=False,dsrdtr=False)
    p.dtr=active; p.rts=active
    # Use documented pySerial API only. Windows open() performs native PurgeComm;
    # overriding _reset_input_buffer does not stop that and was removed.
    return p

def receive(port, log, n, deadline):
    output=bytearray()
    while len(output)<n and time.monotonic()<deadline:
        data=port.read(n-len(output));log.rx(data);output.extend(data)
    if len(output)!=n:
        log.event('TIMEOUT',requested=n,received=len(output),timeout_stage='receive')
        raise TimeoutError(f'Receive timeout: {len(output)}/{n} bytes')
    return bytes(output)

def handshake(port, log, receive_driven=False):
    # One connection session, at most five bounded official-style resynchronizations.
    def transmit(value):
        log.event('TX',hex=f'{value:02x}',purpose='handshake')
        begin=time.perf_counter_ns()
        if port.write(bytes([value]))!=1:raise RuntimeError('Short handshake write')
        log.result['tx_bytes']+=1
        log.event('TX_COMPLETE',hex=f'{value:02x}',duration_ns=time.perf_counter_ns()-begin)
    def logged_read(n):
        data=port.read(n);log.rx(data);return data
    def policy_event(kind,**data):
        if kind=='ATTEMPT_START':log.result['handshake_attempts']=data['attempt']
        log.event(kind,**data)
    engine=readiness_handshake if receive_driven else bounded_handshake
    stats=engine(logged_read,transmit,policy_event,time.monotonic)
    log.result['handshake_attempts']=stats['attempts']
    log.result['handshake']=True;log.event('HANDSHAKE_OK')
    # Only GET_HW_CODE. Second word is HW version, NOT a status.
    log.event('TX',hex='fd',purpose='GET_HW_CODE')
    if port.write(b'\xfd')!=1:raise RuntimeError('Short FD write')
    log.result['tx_bytes']+=1
    # mtk_cmd in the audited upstream inserts 50ms after writing the command.
    time.sleep(.05)
    deadline=time.monotonic()+.5
    if receive(port,log,1,deadline)!=b'\xfd':raise RuntimeError('GET_HW_CODE echo mismatch')
    code,version=struct.unpack('>HH',receive(port,log,4,deadline))
    log.result.update(hw_code=f'0x{code:04X}',hw_version=f'0x{version:04X}')
    log.event('HW_CODE',code=f'0x{code:04X}',version=f'0x{version:04X}')

def run(active, wait_seconds, capture_seconds, extra_identity=False, receive_driven=False, post_identity=None):
    log=Log('one_handshake_fd_fc_d8' if extra_identity else ('one_handshake_and_fd' if active else 'passive_rx_only'))
    wake=threading.Event(); notices=queue.SimpleQueue(); pnp=None; port=None
    try:
        # Construct everything before READY_TO_CONNECT; register before baseline.
        port=make_port(active); pnp=Pnp(wake,notices)
        log.event('SERIAL_SETTINGS',baudrate=port.baudrate,timeout=port.timeout,
                  write_timeout=port.write_timeout,rts=port.rts,dtr=port.dtr,
                  bytesize=port.bytesize,parity=port.parity,stopbits=port.stopbits,
                  xonxoff=port.xonxoff,rtscts=port.rtscts,dsrdtr=port.dsrdtr,
                  private_pyserial_patch=False)
        log.event('HANDSHAKE_POLICY',receive_driven=receive_driven,max_attempts=5,total_timeout=1.5)
        rows=inventory()
        if preloader_present():raise RuntimeError('USB Preloader already present: disconnect and restart launcher')
        log.event('BASELINE',target_present=False,com_count=len(rows))
        log.event('WATCH_READY',pnp_classes=['USB','COM'],fallback_ms=20)
        log.say('READY_TO_CONNECT - Connect the powered-off modem now. Do not press buttons.')
        until=time.monotonic()+wait_seconds
        target=None
        while time.monotonic()<until:
            wake.clear()
            while not notices.empty():
                stamp,kind,action=notices.get()
                log.event('PNP',callback_elapsed_ns=stamp-log.start,interface_class=kind,action=action)
            scan=time.perf_counter_ns(); target=choose(inventory()) if preloader_present() else None
            log.event('SCAN',duration_ns=time.perf_counter_ns()-scan,matched=bool(target))
            if target:break
            wake.wait(.02)
        if target is None:raise TimeoutError('No Preloader COM port within wait window')
        log.result['port']=target.device
        log.event('DETECTED',port=target.device,vid='0E8D',pid='2000',description=target.description)
        detected=time.perf_counter_ns()
        port.port=target.device
        log.event('PORT_OPEN_START',port=target.device)
        # One open with short readiness retries, no sends during those retries.
        open_until=time.monotonic()+.5
        while True:
            try:port.open();break
            except serial.SerialException as exc:
                log.event('OPEN_WAIT',reason=str(exc))
                if time.monotonic()>=open_until:raise
                time.sleep(.01)
        log.result['opened']=True
        log.event('PORT_OPENED',port=target.device,detect_to_open_ns=time.perf_counter_ns()-detected)
        log.say(f'OPENED {target.device} - Recording raw RX.')
        if active:
            handshake(port,log,receive_driven)
            if extra_identity:
                if log.result['hw_code']!='0x0335':raise RuntimeError('Unexpected HW Code; FC/D8 not sent')
                def query_send(value):
                    log.event('TX',hex=f'{value:02x}',purpose='identity_protection_query')
                    begin=time.perf_counter_ns()
                    if port.write(bytes([value]))!=1:raise RuntimeError('Short identity query write')
                    log.result['tx_bytes']+=1
                    log.event('TX_COMPLETE',hex=f'{value:02x}',duration_ns=time.perf_counter_ns()-begin)
                    time.sleep(.05)
                def query_receive(n):return receive(port,log,n,time.monotonic()+.5)
                def query_event(kind,**data):
                    if kind=='IDENTITY_QUERY_RESULT':log.result.update(data['values'])
                    log.event(kind,**data)
                values=query_identity(query_send,query_receive,query_event)
                log.result.update(values)
                if post_identity is not None:
                    status,reason=post_identity(port,log)
                    log.finish(status,reason)
                else:
                    log.finish('IDENTITY_PROTECTION_READ','FC/D8 read; no memory access, DA or identifier reads')
            else:
                log.finish('HW_CODE_READ',f"HW Code={log.result['hw_code']}, HW Version={log.result['hw_version']}")
        else:
            until=time.monotonic()+capture_seconds
            while time.monotonic()<until:
                data=port.read(max(1,min(port.in_waiting,4096))); log.rx(data)
            log.finish('PASSIVE_CAPTURE_DONE','استقبال فقط؛ لم تُرسل أي بايتات مصافحة.')
    except KeyboardInterrupt:
        log.finish('CANCELLED','أوقف المستخدم المراقبة.')
    except Exception as exc:
        # A normal Preloader disappearance can end passive capture.
        status='PASSIVE_CAPTURE_ENDED' if not active and log.result['opened'] else 'BLOCKED'
        log.finish(status,str(exc))
    finally:
        if port and port.is_open:port.close()
        if pnp:pnp.close()

def smoke(seconds):
    log=Log('smoke_no_device_open')
    wake=threading.Event();notices=queue.SimpleQueue();pnp=None
    try:
        unused_port=make_port(False);pnp=Pnp(wake,notices)
        rows=inventory();matches=[p.device for p in rows if p.vid==VID and p.pid==PID]
        log.event('WATCH_READY',target_ports=matches,pnp_registered=True,serial_open=False)
        deadline=time.monotonic()+seconds;scans=0
        while time.monotonic()<deadline:
            inventory();scans+=1;wake.wait(.02);wake.clear()
            while not notices.empty():
                stamp,kind,action=notices.get();log.event('PNP',callback_elapsed_ns=stamp-log.start,interface_class=kind,action=action)
        log.finish('SMOKE_OK',f'PnP registration and {scans} real COM scans; no port opened, no TX')
    except Exception as exc:log.finish('SMOKE_FAILED',str(exc));raise
    finally:
        if pnp:pnp.close()

def self_test():
    """Protocol safety tests use a fake transport, never Windows device handles."""
    class Fake:
        def __init__(self,rx):self.rxbuf=bytearray(rx);self.tx=bytearray()
        def write(self,data):self.tx.extend(data);return len(data)
        def read(self,n):
            data=bytes(self.rxbuf[:n]);del self.rxbuf[:n]
            if not data:time.sleep(.001)
            return data
    class Journal:
        def __init__(self):self.result={'tx_bytes':0};self.received=bytearray()
        def event(self,*args,**kwargs):pass
        def rx(self,data):self.received.extend(data)
    good=Fake(b'READYREADY\x5f\xf5\xaf\xfa\xfd\x03\x21\xca\x00');j=Journal()
    handshake(good,j)
    assert bytes(good.tx)==b'\xa0\x0a\x50\x05\xfd'
    assert j.result['hw_code']=='0x0321' and j.result['hw_version']=='0xCA00'
    gated=Fake(b'READYREADY\x5f\xf5\xaf\xfa\xfd\x03\x35\x00\x00');j=Journal()
    handshake(gated,j,True)
    assert bytes(gated.tx)==b'\xa0\x0a\x50\x05\xfd' and j.result['hw_code']=='0x0335'
    bad=Fake(b'\x00');j=Journal()
    try:handshake(bad,j)
    except TimeoutError:pass
    else:raise AssertionError('Mismatch accepted')
    assert 1<=len(bad.tx)<=5 and set(bad.tx)=={0xa0} and not j.result.get('handshake')
    empty=Fake(b'');j=Journal();start=time.monotonic()
    try:handshake(empty,j)
    except TimeoutError:pass
    else:raise AssertionError('Timeout missing')
    assert time.monotonic()-start<2 and 1<=len(empty.tx)<=5 and set(empty.tx)=={0xa0}
    print('SELF_TEST_OK: READY framing, HW version, bounded resynchronization and timeout. No devices accessed.')

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    ap=argparse.ArgumentParser()
    ap.add_argument('--smoke',type=float,default=0)
    ap.add_argument('--self-test',action='store_true')
    ap.add_argument('--wait-seconds',type=float,default=300)
    ap.add_argument('--capture-seconds',type=float,default=8)
    args=ap.parse_args()
    if args.self_test:self_test()
    elif args.smoke:smoke(args.smoke)
    else:
        active=False;extra_identity=False;receive_driven=False
        approval=ROOT/'next_attempt_approval.json'
        if approval.exists():
            approved=json.loads(approval.read_text(encoding='utf-8-sig'))
            if approved.get('scope') in ('one_connection_bounded_handshake_then_hw_code','one_connection_identity_protection_fc_d8','one_connection_readiness_fd_fc_d8') and approved.get('approved') is True:
                approval.rename(ROOT/'logs'/('consumed-approval-'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'))
                active=True
                extra_identity=approved['scope'] in ('one_connection_identity_protection_fc_d8','one_connection_readiness_fd_fc_d8')
                receive_driven=approved['scope']=='one_connection_readiness_fd_fc_d8'
                print('APPROVED ONE SESSION: max 5 sync attempts / 1.5s, then FD. No DA.')
                if extra_identity:print('ADDITIONAL APPROVED READ QUERIES: FC (versions), D8 (protection). No MEID/SOCID.')
                if receive_driven:print('READINESS V3: bounded receive-driven synchronization; reflected A0 is not success.')
        if not active:
            print('1 = استقبال فقط (افتراضي)\n2 = جلسة واحدة؛ حتى5 محاولات خلال1.5 ثانية ثم HW Code؛ لا DA')
            selected=input('اختر قبل توصيل المودام [1]: ').strip()
            if selected=='2':
                print('المراجعة: حتى5 محاولات لمزامنة A0/0A/50/05 خلال1.5 ثانية، ثم FD فقط بعد الردود الأربعة. READY ليست نجاحًا.')
                active=input('للموافقة على إرسال هذه البايتات فقط اكتب APPROVE: ').strip()=='APPROVE'
                if not active:print('لا توجد موافقة صريحة؛ سيعمل الاستقبال فقط.')
        print('MF904Q BOUNDED-RETRY V2 + IDENTITY FC/D8 | COM only | max_attempts=5 | deadline=1.5s',flush=True)
        run(active,args.wait_seconds,args.capture_seconds,extra_identity,receive_driven)
