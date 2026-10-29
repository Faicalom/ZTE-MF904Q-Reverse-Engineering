# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Separate launcher extending approved DA1 only after new explicit consent."""
import hashlib,json,sys,time
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
sys.path.insert(0,str(BASE))
import run_da1_probe as da1
import wait_preloader as watcher
from stage2_protocol import version_queries,stage2_requirements

def prepare():
    blob,entry=da1.prepare()
    # prepare() already validates the unchanged complete V5 container hash.
    data=(da1.LOADERS/'MTK_DA_V5.bin').read_bytes();r=entry['regions'][2]
    da2=data[r['file_offset']:r['file_offset']+r['length']]
    if (r['load_address'],r['length'],r['signature_length'],hashlib.sha256(da2).hexdigest())!=('0x40000000',222752,256,'4c71c41280414374ef704655dee944a430a701f879489b87188a2e1fc70b0e57'):
        raise ValueError('DA2 region/hash changed')
    # Never return/expose the DA2 blob to the live callback.
    return blob,entry

class StageLog(da1.ProbeLog):
    def __init__(self,mode):
        super().__init__(mode)
        self.result['mode']='one_da1_then_stage2_requirements_no_emi_no_da2'

def callback(blob,entry):
    original_da1=da1.make_callback(blob,entry)
    def work(port,log):
        expected={'hw_code':'0x0335','hw_subcode':'0x8A00','hw_version_fc':'0xCA00',
                  'sw_version':'0x0000','target_config':'0x00000000','d8_status':'0x0000'}
        if any(log.result.get(k)!=v for k,v in expected.items()):
            return 'NOT_SAFE_TO_TEST','Identity mismatch; versions/DA/config not sent'
        deadline=time.monotonic()+6
        purpose='PRELOADER_VERSION_READ'
        def send(data):
            if time.monotonic()>=deadline:raise TimeoutError('Stage probe deadline')
            if purpose=='STAGE2_ACK_CONFIG_ONLY' and data==b'\x5a':
                log.result['ack_attempted']=True
            log.event('TX',hex=data.hex(),purpose=purpose)
            begin=time.perf_counter_ns();n=port.write(data);log.result['tx_bytes']+=n
            log.event('TX_COMPLETE',requested=len(data),written=n,duration_ns=time.perf_counter_ns()-begin)
            if n!=len(data):raise OSError('Short serial write; no retry')
            if purpose=='STAGE2_ACK_CONFIG_ONLY':
                log.result['stage2_tx_completed_bytes']=log.result.get('stage2_tx_completed_bytes',0)+n
                if data==b'\x5a':log.result['ack_sent']=True
        def receive(n):
            if time.monotonic()>=deadline:raise TimeoutError('Stage probe deadline')
            return watcher.receive(port,log,n,min(deadline,time.monotonic()+2))
        try:
            versions=version_queries(send,receive)
            log.result.update(versions);log.event('PRELOADER_VERSION_BYTES',values=versions)
        except Exception as exc:
            return 'VERSION_QUERY_FAILED',str(exc)
        status,reason=original_da1(port,log)
        if status!='DA1_SUCCESS':return status,reason
        if log.result.get('storage_type_initial')!='emmc':
            return 'NOT_SAFE_TO_TEST','Storage type changed; ACK/config not sent'
        deadline=time.monotonic()+6;purpose='STAGE2_ACK_CONFIG_ONLY'
        try:
            status,info=stage2_requirements(send,receive,log.event,
                                           versions['bl_version'],versions['brom_version'])
            log.result.update(info)
            log.event('STAGE2_REQUIREMENTS_RESULT',status=status,values=info)
            return status,'Stopped before EMI/DA2/flash; see logged return/request'
        except Exception as exc:
            return 'STAGE2_PROBE_FAILED',f'{type(exc).__name__}: {exc}; no retry, EMI or DA2'
    return work

def main():
    blob,entry=prepare()
    approval=ROOT/'one_session_approval.json'
    if not approval.exists():raise RuntimeError('New explicit stage-config approval missing; no COM opened')
    decision=json.loads(approval.read_text(encoding='utf-8-sig'))
    if decision.get('approved') is not True or decision.get('scope')!='one_da1_ack_stage2_config_request_no_emi_no_da2' or decision.get('da1_sha256')!=da1.EXPECTED_DA1:
        raise RuntimeError('Approval does not match exact experiment')
    approval.rename(BASE/'logs'/('consumed-stage2-request-approval-'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'))
    watcher.Log=StageLog
    print('ONE STAGE CONFIG PROBE: FE/FF + stock DA1 + ACK/config. NO EMI/DA2/FLASH.',flush=True)
    watcher.run(True,300,0,extra_identity=True,receive_driven=True,post_identity=callback(blob,entry))

if __name__=='__main__':main()
