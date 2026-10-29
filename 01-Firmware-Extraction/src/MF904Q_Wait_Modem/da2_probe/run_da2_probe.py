# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""One explicitly approved stock DA2 test; reuses successful Stage2 callback."""
import hashlib,json,shutil,sys,time
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sys.path.insert(0,str(BASE/'stage2_probe'));sys.path.insert(0,str(BASE))
import run_stage2_requirements as stage1
import wait_preloader as watcher
from da2_protocol import upload,geometry,read_user_prefix,partition_summary,Failure
EXPECTED_DA2='4c71c41280414374ef704655dee944a430a701f879489b87188a2e1fc70b0e57'

def prepare():
    blob,entry=stage1.prepare()
    whole=(stage1.da1.LOADERS/'MTK_DA_V5.bin').read_bytes();r=entry['regions'][2]
    da2=whole[r['file_offset']:r['file_offset']+r['length']]
    if hashlib.sha256(da2).hexdigest()!=EXPECTED_DA2:raise ValueError('Stock DA2 hash mismatch')
    if shutil.disk_usage(BASE).free<64*1024*1024:raise ValueError('Need 64MiB free for logs and bounded read')
    return blob,entry,da2

class ProbeLog(stage1.StageLog):
    def __init__(self,mode):
        super().__init__(mode);self.result['mode']='one_stock_da2_geometry_and_34_user_sectors'

def callback(blob,entry,da2):
    requirements=stage1.callback(blob,entry)
    def work(port,log):
        status,reason=requirements(port,log)
        if status!='STAGE2_CONFIG_ACCEPTED':return status,reason
        # Never bypass an EMI request or continue after a failed stage config.
        if log.result.get('stage2_config_return')!='0x00000000':
            return 'NOT_SAFE_TO_TEST','Stage2 config response mismatch; DA2 not sent'
        deadline=time.monotonic()+90;phase='HEADER'
        log.result.update(da2_attempted=True,da2_sha256=EXPECTED_DA2,flash_read_attempted=False)
        def event(kind,**values):
            nonlocal phase
            if kind=='DA2_PHASE':phase=values['phase']
            log.event(kind,**values)
        def send(data):
            if time.monotonic()>=deadline:raise TimeoutError('DA2 total deadline exceeded')
            log.event('TX',hex=data.hex(),purpose='DA2_'+phase)
            started=time.perf_counter_ns();n=port.write(data)
            log.result['tx_bytes']+=n
            log.event('TX_COMPLETE',requested=len(data),written=n,duration_ns=time.perf_counter_ns()-started)
            if n!=len(data):raise OSError('Short COM write; no retry')
            if phase=='PAYLOAD':log.result['da2_sent']=True
        def receive(n):
            if time.monotonic()>=deadline:raise TimeoutError('DA2 total deadline exceeded')
            return watcher.receive(port,log,n,min(deadline,time.monotonic()+5))
        try:
            upload(send,receive,event,da2)
            log.result['da2_start_acked']=True
            event('DA2_PHASE',phase='GEOMETRY')
            info,raw=geometry(receive)
            (log.folder/'flash_info_reply_private.bin').write_bytes(raw)
            # CID is part of the requested geometry reply; no MEID/SOCID/NVRAM commands.
            log.result.update(info,geometry_received=True,dram_geometry_verified=True)
            if shutil.disk_usage(log.folder).free<64*1024*1024:
                return 'DA2_GEOMETRY_SUCCESS','Geometry read; insufficient free space for first-sector evidence'
            log.result['flash_read_attempted']=True
            data,read_info=read_user_prefix(send,receive,event,info['user_size'])
            out=log.folder/'user_lba0_33.bin';out.write_bytes(data)
            log.result.update(read_info,flash_file=out.name,flash_sha256=hashlib.sha256(data).hexdigest(),
                              flash_file_size=out.stat().st_size)
            summary=partition_summary(data,info['user_size'])
            (log.folder/'partition_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
            log.result['partition_summary']=summary
            return 'DA2_FIRST_SECTORS_READ','Stock DA2 accepted; geometry and 34 User sectors saved. No further reads.'
        except Failure as exc:return exc.status,str(exc)
        except Exception as exc:
            return 'DA2_PROBE_FAILED',f'{type(exc).__name__}: {exc}; stop, no retry/reset/write'
    return work

def main():
    blob,entry,da2=prepare()
    approval=ROOT/'one_session_approval.json'
    if not approval.exists():raise RuntimeError('Explicit stock DA2 approval missing; no COM opened')
    decision=json.loads(approval.read_text(encoding='utf-8-sig'))
    if decision.get('approved') is not True or decision.get('scope')!='one_stock_da2_geometry_cid_and_34_user_sectors' or decision.get('da2_sha256')!=EXPECTED_DA2:
        raise RuntimeError('DA2 approval scope/hash mismatch')
    approval.rename(BASE/'logs'/('consumed-da2-approval-'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json'))
    watcher.Log=ProbeLog
    print('ONE STOCK DA2 + GEOMETRY/CID + 34 USER SECTORS. NO EMI/PATCH/FLASH WRITES.',flush=True)
    watcher.run(True,300,0,extra_identity=True,receive_driven=True,post_identity=callback(blob,entry,da2))

if __name__=='__main__':main()
