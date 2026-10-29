# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""One resumable public/private backup launcher using successful stock DA2."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OLD=ROOT.parent/'MF904Q_Wait_Modem'
sys.path.insert(0,str(OLD/'da2_probe'));sys.path.insert(0,str(OLD))
import run_da2_probe as bootstrap
import wait_preloader as watcher
from backup_core import Image,sha,atomic_json,read_range,gpt_header,entries,PUBLIC,CHUNK,SECTOR
SUCCESS=OLD/'logs/20261009_104835_647022'
EXPECTED_PREFIX='3bea55d41c1c2eeec60c0ae7e3312b7f03821871926b3abf22ba04a32b70518d'
OLD_ID=json.loads((SUCCESS/'result.json').read_text())
BINDING=hashlib.sha256(bytes.fromhex(OLD_ID['cid_wire_hex'])+bytes.fromhex(EXPECTED_PREFIX)).hexdigest()
MANIFEST=ROOT/'manifest.json'
LAST_STATUS=None

class BackupLog(bootstrap.ProbeLog):
    def rx(self,data):
        if not data:return
        offset=self.result['rx_bytes'];self.raw.write(data);self.raw.flush();self.result['rx_bytes']+=len(data)
        if len(data)<4096:self.event('RX',offset=offset,length=len(data),hex=data.hex())
        else:self.event('RX_RAW',offset=offset,length=len(data),sha256=hashlib.sha256(data).hexdigest())
    def finish(self,status,reason):
        global LAST_STATUS
        LAST_STATUS=status
        self.txraw.close();self.raw.close()
        self.result.update(status=status,reason=reason,rx_sha256=sha(self.folder/'rx.bin'),tx_attempted_sha256=sha(self.folder/'tx_attempted.bin'))
        self.event('RESULT',**self.result);atomic_json(self.folder/'result.json',self.result)
        self.say(f'RESULT: {status} — {reason}');self.say(f'Logs: {self.folder}')
        self.events.close();self.text.close()

def initialize():
    if not MANIFEST.exists():
        atomic_json(MANIFEST,dict(device='MF904Q WF904_V6.0 / HW0335',binding=BINDING,
                                  files=[],errors=[],private_scope='approval_required',restoration_proven=False))
    m=json.loads(MANIFEST.read_text())
    if m['binding']!=BINDING:raise ValueError('Manifest belongs to another device')
    return m

def record(m,path,region,offset,expected,state,sensitive=False,origin='Flash read'):
    path=Path(path);key=path.relative_to(ROOT).as_posix()
    row=dict(file=key,region=region,start=offset,expected_size=expected,
             actual_size=path.stat().st_size if path.exists() else (Path(str(path)+'.partial').stat().st_size if Path(str(path)+'.partial').exists() else 0),complete=state.get('complete',False),
             sha256=state.get('sha256'),sensitive=sensitive,source=origin,
             independent_verification=state.get('independent_verification'),error=state.get('error'))
    m['files']=[r for r in m['files'] if r['file']!=key]+[row];atomic_json(MANIFEST,m)

def callback(blob,entry,da2,private=False):
    connect=bootstrap.callback(blob,entry,da2)
    def work(port,log):
        m=initialize();phase='BOOTSTRAP'
        status,reason=connect(port,log)
        if status!='DA2_FIRST_SECTORS_READ':return status,reason
        if log.result.get('cid_wire_hex')!=OLD_ID['cid_wire_hex']:
            return 'BACKUP_STOPPED','eMMC identity changed; no further reads'
        if any(log.result.get(k)!=OLD_ID[k] for k in ('user_size','boot1_size','boot2_size','ext_ram_size')):
            return 'BACKUP_STOPPED','Storage/DRAM geometry changed; no further reads'
        prefix=(log.folder/'user_lba0_33.bin').read_bytes()
        if hashlib.sha256(prefix).hexdigest()!=EXPECTED_PREFIX:
            return 'BACKUP_STOPPED','Initial range changed from successful reference; stop'
        user=log.result['user_size'];deadline=0
        def send(data):
            if time.monotonic()>deadline:raise TimeoutError('Chunk deadline exceeded')
            log.event('TX',hex=data.hex(),purpose='BACKUP_READ_'+phase)
            start=time.perf_counter_ns();n=port.write(data);log.result['tx_bytes']+=n
            log.event('TX_COMPLETE',requested=len(data),written=n,duration_ns=time.perf_counter_ns()-start)
            if n!=len(data):raise OSError('Short COM write; no retry')
        def receive(n):
            return watcher.receive(port,log,n,min(deadline,time.monotonic()+30))
        def read(region,offset,length,size):
            nonlocal deadline
            deadline=time.monotonic()+60
            log.event('FLASH_RANGE',region=region,offset=offset,length=length,phase=phase)
            data,checksum=read_range(send,receive,region,offset,length,size)
            log.event('FLASH_RANGE_VERIFIED',region=region,offset=offset,length=length,
                      checksum=f'{checksum:04X}',sha256=hashlib.sha256(data).hexdigest())
            return data,checksum
        def image(path,region,offset,size,region_size,sensitive=False):
            path=ROOT/path;item=Image(path,region,offset,size,BINDING)
            log.say(f'COPY {path.name}: {size} bytes')
            last=[0.0]
            def progress(done,total):
                now=time.monotonic()
                if now-last[0]>10 or done==total:
                    log.say(f'PROGRESS {path.name}: {done}/{total} ({100*done/total:.1f}%)');last[0]=now
            try:state=item.run(read,region_size,progress)
            except Exception as exc:
                state=dict(complete=False,error=f'{type(exc).__name__}: {exc}')
                record(m,path,region,offset,size,state,sensitive);raise
            record(m,path,region,offset,size,state,sensitive);log.say(f'VERIFIED {path.name}: {state["sha256"]}')
        def raw(path,data,region,offset,origin):
            target=ROOT/path
            if target.exists() and target.read_bytes()!=data:raise ValueError('Existing verified metadata differs')
            target.write_bytes(data)
            record(m,target,region,offset,len(data),dict(complete=True,sha256=sha(target),
                   independent_verification='CRC/identity and file bytes verified'),origin=origin)
        try:
            phase='STABILITY_AND_GPT'
            primary=gpt_header(prefix[512:1024],1,user)
            table=prefix[primary['table_lba']*SECTOR:primary['table_lba']*SECTOR+primary['length']]
            parts=entries(table,primary);byname={p['name']:p for p in parts}
            if not PUBLIC.issubset(byname):raise ValueError('Expected public firmware partitions missing')
            # Independent same-range repeat, then a larger known non-sensitive lk range twice.
            repeated,_=read(8,0,len(prefix),user)
            if repeated!=prefix:raise ValueError('Initial stability SHA mismatch')
            lk=byname['lk'];a,_=read(8,lk['offset'],256*1024,user);b,_=read(8,lk['offset'],256*1024,user)
            if a!=b:raise ValueError('256KiB lk stability range mismatch')
            atomic_json(ROOT/'07_Verification/stability.json',dict(session=log.folder.name,
                        prefix_sha256=hashlib.sha256(repeated).hexdigest(),larger_range_sha256=hashlib.sha256(a).hexdigest(),
                        larger_range_offset=lk['offset'],larger_range_length=len(a),independent_reads_equal=True))
            raw('02_GPT/primary_prefix.bin',prefix,'User',0,'Independent matching prefix read')
            raw('02_GPT/primary_header.bin',prefix[512:1024],'User',512,'Derived from primary prefix')
            raw('02_GPT/primary_entries.bin',table,'User',primary['table_lba']*SECTOR,'Derived from primary prefix')
            head,_=read(8,primary['backup']*SECTOR,SECTOR,user)
            backup=gpt_header(head,primary['backup'],user)
            if backup['backup']!=1 or any(backup[k]!=primary[k] for k in ('disk_guid','count','entry_size','first','last')):
                raise ValueError('Backup GPT geometry/GUID differs')
            array,_=read(8,backup['table_lba']*SECTOR,backup['padded'],user)
            entries(array,backup)
            if array[:backup['length']]!=table:raise ValueError('Backup GPT entries differ')
            raw('02_GPT/backup_header.bin',head,'User',backup['current']*SECTOR,'Backup GPT read, header CRC verified')
            raw('02_GPT/backup_entries_padded.bin',array,'User',backup['table_lba']*SECTOR,'Backup GPT read, table CRC verified')
            atomic_json(ROOT/'02_GPT/comparison_public.json',dict(headers_crc_valid=True,entries_crc_valid=True,
                        names_bounds_guids_equal=True,partition_count=len(parts),backup_header_lba=backup['current'],
                        backup_table_lba=backup['table_lba'],logical_sector_size=SECTOR,
                        sector_size_evidence='Source protocol and GPT header at byte512/LBA1 agree; not an explicit DA2 response field'))
            atomic_json(ROOT/'01_Device_Info/partition_layout.json',parts)
            phase='PUBLIC_FIRMWARE'
            for p in sorted((byname[name] for name in PUBLIC),key=lambda p:(p['size'],p['offset'])):
                image(f'04_Firmware_Partitions/{p["name"]}.bin',8,p['offset'],p['size'],user)
            phase='BOOT_REGIONS'
            for region in (1,2):
                size=log.result[f'boot{region}_size']
                image(f'03_Boot_Regions/boot{region}.bin',region,0,size,size)
            if private:
                phase='PRIVATE_DATA'
                for p in parts:
                    if p['name'] not in PUBLIC:
                        image(f'05_Private_Device_Data/{p["name"]}.bin',8,p['offset'],p['size'],user,True)
                phase='FULL_USER'
                image('06_Full_User_Backup/user.bin',8,0,user,user,True)
                m['private_scope']='approved_and_read';atomic_json(MANIFEST,m)
                return 'RAW_BACKUP_COMPLETE','All requested readable ranges copied; private archive encryption is the next local step'
            m['private_scope']='approval_required';atomic_json(MANIFEST,m)
            return 'PUBLIC_BACKUP_COMPLETE','7 Firmware partitions + Boot1/Boot2 + both GPT copies verified. Private/User not read.'
        except Exception as exc:
            m['errors'].append(dict(session=log.folder.name,phase=phase,error=f'{type(exc).__name__}: {exc}'))
            atomic_json(MANIFEST,m)
            return 'BACKUP_STOPPED',f'{phase}: {type(exc).__name__}: {exc}; no retry/reset/write'
    return work

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--private',action='store_true');args=parser.parse_args()
    blob,entry,da2=bootstrap.prepare();initialize()
    if args.private:
        approval=ROOT/'private_read_approval.json'
        if not approval.exists():raise RuntimeError('Separate sensitive-data/User approval required; no COM opened')
        decision=json.loads(approval.read_text(encoding='utf-8-sig'))
        if decision.get('approved') is not True or decision.get('binding')!=BINDING:
            raise RuntimeError('Private approval identity mismatch')
        import private_crypto
        encryption_key,salt=private_crypto.ask_password() # Before READY/USB attachment.
    if shutil.disk_usage(ROOT).free<(20 if args.private else 3)*1024**3:
        raise RuntimeError('Insufficient disk space including raw RX logs')
    watcher.ROOT=ROOT/'09_Logs';watcher.Log=BackupLog
    print('STOCK BACKUP: READ ONLY, CHECKPOINTED. NO FLASH WRITES / RESET / RPMB.',flush=True)
    watcher.run(True,600,0,extra_identity=True,receive_driven=True,post_identity=callback(blob,entry,da2,args.private))
    if args.private and LAST_STATUS=='RAW_BACKUP_COMPLETE':
        from datetime import datetime
        import verify_backup
        print('MODEM SESSION CLOSED. Independently verifying full User and partition copies.',flush=True)
        if verify_backup.verify()['status']!='PASS':raise RuntimeError('Independent backup verification failed')
        target=ROOT/'05_Private_Device_Data'/('private_backup_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip.aesgcm')
        print('MODEM SESSION CLOSED. Encrypting and verifying private local archive.',flush=True)
        verified=private_crypto.archive(ROOT,encryption_key,salt,target,lambda s:print(s,flush=True))
        verified['sha256']=sha(target);atomic_json(ROOT/'07_Verification/private_archive_verification.json',verified)
        print('PRIVATE_ARCHIVE_VERIFIED. Password is required for recovery; raw originals remain locally ACL-protected.',flush=True)

if __name__=='__main__':main()
