# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""One explicitly authorized Windows DA1 session; reuses successful watcher."""
import hashlib,json,struct,time
from datetime import datetime
from pathlib import Path
import wait_preloader as watcher
from audit_legacy_candidates import LOADERS,parse_entry
from da1_probe_protocol import probe,ProbeFailure

ROOT=Path(__file__).resolve().parent
EXPECTED_FILE='aef234190ccb8145d2e3b8459741e9adb70f2caa8481aa216c1b25152afaca1f'
EXPECTED_DA1='16160bfd628e56943dccc6982da92a30187ff1bec25ad144341268df63ca0f13'

def prepare():
    data=(LOADERS/'MTK_DA_V5.bin').read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_FILE:raise ValueError('Whole DA file hash changed')
    entry=parse_entry(data,0x6c+14*0xdc)
    if (entry['da_code'],entry['subcode'],entry['hw_version'],entry['sw_version'])!=(0x6735,0,0xca00,0):
        raise ValueError('DA header changed')
    region=entry['regions'][1]
    if (region['load_address'],region['length'],region['signature_length'])!=('0x00200000',98000,256):
        raise ValueError('DA1 region changed')
    blob=data[region['file_offset']:region['file_offset']+region['length']]
    if hashlib.sha256(blob).hexdigest()!=EXPECTED_DA1:raise ValueError('DA1 hash mismatch')
    return blob,entry

class ProbeLog(watcher.Log):
    def __init__(self,mode):
        super().__init__('one_unpatched_da1_probe')
        self.txraw=(self.folder/'tx_attempted.bin').open('wb')
    def event(self,kind,**data):
        if kind=='TX' and hasattr(self,'txraw'):
            self.txraw.write(bytes.fromhex(data['hex']));self.txraw.flush()
        super().event(kind,**data)
    def finish(self,status,reason):
        self.txraw.close()
        self.result['tx_attempted_sha256']=hashlib.sha256((self.folder/'tx_attempted.bin').read_bytes()).hexdigest()
        if status=='BLOCKED':status='NOT_SAFE_TO_TEST'
        super().finish(status,reason)

def make_callback(blob,entry):
    def callback(port,log):
        expected={'hw_code':'0x0335','hw_subcode':'0x8A00','hw_version_fc':'0xCA00',
                  'sw_version':'0x0000','target_config':'0x00000000','d8_status':'0x0000'}
        if any(log.result.get(k)!=v for k,v in expected.items()):
            return 'NOT_SAFE_TO_TEST','Live identity/protection does not match approved target; D7 not sent'
        region=entry['regions'][1]
        log.result.update(da_file='MTK_DA_V5.bin',da1_sha256=EXPECTED_DA1,da2_sent=False,
                          da1_attempted=True,source_revision='cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3')
        log.event('DA1_CANDIDATE',file='MTK_DA_V5.bin',entry=14,region=region,
                  uncertainty='Subcode/board/DA1 internal initialization not proven; compatibility experiment')
        session_deadline=time.monotonic()+15
        phase='SEND'
        def event(kind,**data):
            nonlocal phase
            if kind=='DA1_PHASE':
                phase=data['phase']
                if phase=='JUMP':log.result['da1_upload_accepted']=True;log.result['da_sent']=True
                if phase=='STORAGE':log.result['da1_sync']=True
            log.event(kind,**data)
        def send(data):
            if time.monotonic()>=session_deadline:raise TimeoutError('DA1 total 15s deadline')
            log.event('TX',hex=data.hex(),purpose='DA1_'+phase)
            start=time.perf_counter_ns();written=port.write(data)
            log.result['tx_bytes']+=written
            log.event('TX_COMPLETE',requested=len(data),written=written,duration_ns=time.perf_counter_ns()-start)
            if written!=len(data):raise OSError('Short serial write; stop without retry')
        def receive(n):
            if time.monotonic()>=session_deadline:raise TimeoutError('DA1 total deadline')
            return watcher.receive(port,log,n,min(session_deadline,time.monotonic()+2))
        try:
            info=probe(send,receive,event,blob,int(region['load_address'],16),region['signature_length'])
            log.result.update(info)
            return 'DA1_SUCCESS','C0 and initial storage IDs read. No ACK, DA2, EMI, flash access or capacity read.'
        except ProbeFailure as exc:
            return exc.status,str(exc)
    return callback

def main():
    # Prepare/hash/import everything BEFORE USB readiness.
    blob,entry=prepare()
    approval=ROOT/'da1_once_approval.json'
    if not approval.exists():raise RuntimeError('No unused explicit DA1 approval; no device connection')
    value=json.loads(approval.read_text(encoding='utf-8-sig'))
    if value.get('scope')!='one_unpatched_da1_initial_ids_no_ack_no_da2' or value.get('da1_sha256')!=EXPECTED_DA1 or value.get('approved') is not True:
        raise RuntimeError('Approval scope/hash mismatch')
    (ROOT/'logs').mkdir(exist_ok=True)
    approval.rename(ROOT/'logs'/('consumed-da1-approval-'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'))
    watcher.Log=ProbeLog
    print('AUTHORIZED ONE DA1 SESSION: stock DA1 only; stop before 5A ACK; no DA2, EMI or flash commands.',flush=True)
    watcher.run(True,300,0,extra_identity=True,receive_driven=True,post_identity=make_callback(blob,entry))

if __name__=='__main__':main()
