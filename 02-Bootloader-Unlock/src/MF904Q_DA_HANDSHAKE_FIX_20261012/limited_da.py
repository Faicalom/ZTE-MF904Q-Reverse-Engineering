# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Offline by default. No Fastboot/ADB. Exact unmodified DA + three reads."""
import pathlib,json,hashlib,struct,time,os,sys,subprocess,datetime,re,shutil
from policy import *
from readiness_protocol import readiness_handshake
from identity_queries import query
from da1_probe_protocol import probe
from stage2_protocol import version_queries,stage2_requirements
from da2_protocol import upload,geometry
from backup_core import read_range
from compare_private import summary,frp_status
ROOT=pathlib.Path(__file__).resolve().parent
def manual_off_confirmed(value):return value.strip().upper()=='OFF'

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def prepare():
 manifest=json.loads((ROOT/'BUILD_SHA256.json').read_text(encoding='utf-8-sig'))
 for name,digest in manifest.items():
  if sha(ROOT/name)!=digest:raise ValueError('Build hash mismatch: '+name)
 if shutil.disk_usage(ROOT).free<64*1024*1024:raise ValueError('Insufficient free space for raw evidence')
 cfg=json.loads((ROOT/'RUNTIME_AND_LOADER.json').read_text(encoding='utf-8-sig'))
 if pathlib.Path(sys.executable).resolve()!=pathlib.Path(cfg['python']).resolve() or sha(sys.executable)!=cfg['python_sha256']:raise ValueError('Wrong Python runtime')
 import serial
 deps=json.loads((ROOT/'SERIAL_RUNTIME.json').read_text())
 if serial.__version__!=deps['version'] or pathlib.Path(serial.__file__).resolve()!=pathlib.Path(deps['module']).resolve():raise ValueError('Serial runtime mismatch')
 for path,digest in deps['files'].items():
  if sha(path)!=digest:raise ValueError('Serial dependency changed')
 blob=pathlib.Path(cfg['loader']).read_bytes()
 if hashlib.sha256(blob).hexdigest()!=DA_CONTAINER:raise ValueError('DA container mismatch')
 raw=blob[0x6c+14*0xdc:0x6c+15*0xdc]
 vals=struct.unpack_from('<10H',raw)
 if vals[:5]!=(0xdada,0x6735,0,0xca00,0):raise ValueError('DA selection mismatch')
 stages=[]
 for idx,addr,size,digest in [(1,0x200000,98000,DA1_HASH),(2,0x40000000,222752,DA2_HASH)]:
  off,length,address,start,sig=struct.unpack_from('<5I',raw,20+idx*20)
  if (length,address,sig)!=(size,addr,256) or off+length>len(blob):raise ValueError('DA bounds mismatch')
  data=blob[off:off+length]
  if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('DA payload mismatch')
  stages.append(data)
 return stages
class Log:
 def __init__(self,folder):
  self.folder=folder;folder.mkdir(parents=True,exist_ok=False)
  # Private binary logs inherit no broad ACL; fail before any modem I/O if ACL fails.
  q=subprocess.run(['whoami.exe','/user','/fo','csv','/nh'],capture_output=True,check=True)
  sid=re.search(r'S-1-5-\d+(?:-\d+)+',q.stdout.decode(errors='replace'))
  if not sid:raise ValueError('Unable to determine owner SID')
  subprocess.run(['icacls.exe',str(folder),'/inheritance:r','/grant:r','*'+sid[0]+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F'],capture_output=True,check=True)
  self.events=(folder/'events.jsonl').open('x',encoding='utf8',buffering=1)
  self.rxfile=(folder/'RX_PRIVATE.bin').open('xb',buffering=0);self.txfile=(folder/'TX_PRIVATE.bin').open('xb',buffering=0)
  self.phase='PREPARING';self.result={'status':'UNKNOWN','completed':[]};self.files=[]
 def event(self,kind,**data):
  raw=data.pop('data',None)
  if raw is not None:
   self.txfile.write(raw);data.update(length=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  self.events.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic':time.monotonic(),'event':kind,**data})+'\n');self.events.flush();os.fsync(self.events.fileno())
 def rx(self,data):
  if data:self.rxfile.write(data);self.event('RX',phase=self.phase,length=len(data),sha256=hashlib.sha256(data).hexdigest())
 def finish(self,error=None):
  if error:self.result.update(status='PARTIAL_UNKNOWN' if self.result['completed'] or self.phase.startswith('READ_') else 'UNKNOWN',error=repr(error))
  for f in [self.rxfile,self.txfile,self.events]:f.flush();os.fsync(f.fileno());f.close()
  (self.folder/'RESULT.json').write_text(json.dumps(self.result,indent=2),encoding='utf8')
  hashes={f.name:sha(f) for f in self.folder.iterdir() if f.is_file()}
  (self.folder/'SHA256.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
class Receiver:
 def __init__(self,port,log):self.port=port;self.log=log;self.deadline=0
 def receive(self,n):
  b=bytearray()
  while len(b)<n and time.monotonic()<self.deadline:
   d=self.port.read(n-len(b));self.log.rx(d);b.extend(d)
  if len(b)!=n:
   self.log.event('INCOMPLETE_RX',requested=n,received=len(b));raise TimeoutError('Partial response; saved in RX_PRIVATE.bin')
  return bytes(b)
def run_session(port,log,da1,da2,reference,prefix):
 recv=Receiver(port,log)
 def native_write(data):
  if time.monotonic()>=recv.deadline:raise TimeoutError('Phase deadline before TX; no retry')
  return port.write(data)
 guard=Guard(transcripts(da1,da2),native_write,log.event)
 def phase(name,seconds):log.phase=name;log.event('PHASE',name=name);guard.begin(name);recv.deadline=time.monotonic()+seconds
 phase('HANDSHAKE',2)
 def one_read(n):d=port.read(n);log.rx(d);return d
 def sync_event(kind,**data):
  if kind=='READY_FRAME':guard.note_ready()
  log.event(kind,**data)
 readiness_handshake(one_read,lambda v:guard.send(bytes([v])),sync_event,time.monotonic,max_attempts=2,total_timeout=1.5)
 guard.complete()
 phase('HW',1);guard.send(b'\xfd');time.sleep(.05)
 if recv.receive(1)!=b'\xfd':raise ValueError('FD echo mismatch')
 hw,ver=struct.unpack('>HH',recv.receive(4));info={'hw_code':f'0x{hw:04X}','hw_version':f'0x{ver:04X}'}
 if info!={'hw_code':'0x0335','hw_version':'0x0000'}:raise ValueError('HW mismatch; no further identity or DA')
 phase('IDENTITY',2)
 def identity_send(v):guard.send(bytes([v]));time.sleep(.05)
 info.update(query(identity_send,recv.receive,log.event));check_hw(info);log.event('HW_IDENTITY_CONFIRMED',values=info)
 phase('VERSIONS',2);versions=version_queries(guard.send,recv.receive)
 if versions!={'bl_version':1,'brom_version':255}:raise ValueError('Preloader version changed')
 phase('DA1',15);initial=probe(guard.send,recv.receive,log.event,da1,0x200000,256)
 if initial['storage_type_initial']!='emmc' or initial['emmc_ids_raw_hex']!=reference['emmc_ids_raw_hex'] or initial['emmc_info']!=reference['emmc_info']:raise ValueError('DA1 storage identity mismatch')
 phase('CONFIG',6);status,config=stage2_requirements(guard.send,recv.receive,log.event,1,255)
 if status!='STAGE2_CONFIG_ACCEPTED' or config['stage2_config_return']!='0x00000000':raise ValueError('Stage2 failed/EMI requested; no DA2')
 phase('DA2',90);upload(guard.send,recv.receive,log.event,da2);guard.complete();log.phase='GEOMETRY';recv.deadline=time.monotonic()+5
 geom,raw=geometry(recv.receive);check_geometry(geom,reference);log.event('CID_GEOMETRY_CONFIRMED',cid_sha256=hashlib.sha256(bytes.fromhex(geom['cid_wire_hex'])).hexdigest(),user_size=geom['user_size'])
 for i,((offset,length),name) in enumerate(zip(RANGES,['GPT_PREFIX_CURRENT','seccfg_CURRENT','frp_CURRENT'])):
  phase('READ_'+str(i),60)
  data,checksum=read_range(guard.send,recv.receive,8,offset,length,USER_SIZE);guard.complete()
  if i==0:check_gpt(data,prefix)
  path=log.folder/(name+'.bin')
  with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  if path.stat().st_size!=length or sha(path)!=hashlib.sha256(data).hexdigest():raise ValueError('Disk verification failed')
  log.result['completed'].append({'name':name,'length':length,'offset':offset,'sha256':sha(path),'checksum':checksum})
  log.event('RANGE_SAVED',name=name,offset=offset,length=length,sha256=sha(path))
 log.result['status']='LIMITED_READ_COMPLETE'
def choose_port(ports):
 hits=[p for p in ports if p.vid==0x0e8d and p.pid==0x2000]
 if len(hits)>1:raise ValueError('Ambiguous Preloader COM')
 return hits[0] if hits else None
def live():
 stages=prepare()
 approval=json.loads((ROOT/'LIVE_APPROVAL.json').read_text(encoding='utf-8-sig'))
 if approval.get('approved') is not True or approval.get('scope')!='one_da_three_ranges' or approval.get('build_manifest_sha256')!=sha(ROOT/'BUILD_SHA256.json') or approval.get('accept_power_and_missed_window_risk') is not True:raise ValueError('Separate live approval missing')
 q=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='fastboot.exe'\").Count"],capture_output=True,check=True)
 if q.stdout.decode().strip()!='0':raise ValueError('Fastboot process pending; STOP before manual power coordination')
 print('Files verified. No USB command. Power interruption risks unfinished writes; missed Preloader can boot Android and change FRP. No WPS/Reset. Type ARM_DA_READ to reserve one attempt.',flush=True)
 if input().strip()!='ARM_DA_READ':return
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject' /'DA_HANDSHAKE_FIX_20261012'/'ATTEMPT_RESERVED.json'
 reserve(latch,{'scope':'one_da_three_ranges','build_manifest_sha256':sha(ROOT/'BUILD_SHA256.json')})
 reserve(ROOT/'ATTEMPT_RESERVED.json',{'global_lock':str(latch)})
 session=ROOT/'private_sessions'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');log=Log(session);port=None
 try:
  import serial
  from serial.tools import list_ports
  from usb_metadata import snapshot
  ref=json.loads((ROOT/'USB_REFERENCE.json').read_text());paths=ref['usb']['paths']
  print('Approved manual transition: disconnect USB; power off normally; remove battery after off. Then insert battery with modem OFF; keep USB disconnected. Type OFF. No Power-on/WPS/Reset.',flush=True)
  if not manual_off_confirmed(input()):raise ValueError('Off/battery coordination not confirmed')
  baseline=snapshot()
  if any(r['fastboot'] or 'VID_0E8D' in r['usb_id'] for r in baseline):raise ValueError('USB must be disconnected')
  port=serial.Serial(port=None,baudrate=115200,timeout=.02,write_timeout=.2,xonxoff=False,rtscts=False,dsrdtr=False);port.dtr=True;port.rts=True
  print('READY_FOR_PRELOADER: connect powered-off modem USB ONCE. No buttons. No automatic retries.',flush=True);log.event('READY_FOR_PRELOADER')
  end=time.monotonic()+120;target=None
  while time.monotonic()<end:
   target=choose_port(list_ports.comports())
   if target:break
   time.sleep(.02)
  if target is None:raise TimeoutError('Preloader not found')
  rows=[r for r in snapshot() if r['usb_id']=='VID_0E8D&PID_2000']
  if len(rows)!=1 or not set(rows[0]['paths'])&set(paths) or not any(target.device in s for s in rows[0]['name']):raise ValueError('Preloader physical path/COM mismatch')
  port.port=target.device;log.event('COM_OPEN_ONCE',com=target.device,paths=rows[0]['paths']);port.open()
  run_session(port,log,*stages,json.loads((ROOT/'DA_SUCCESS_REFERENCE_PRIVATE.json').read_text()),(ROOT/'GPT_REFERENCE.bin').read_bytes())
 except BaseException as ex:log.finish(ex);raise
 else:log.finish()
 finally:
  if port is not None and port.is_open:port.close()
  print('STOP. Logs: '+str(session)+'. No reset/reboot/exit command. No retries.',flush=True)
 # Local analysis only after COM is closed and transport evidence finalized.
 if log.result['status']=='LIMITED_READ_COMPLETE':
  compare_saved(session)
def compare_saved(folder):
 base=ROOT.parent/'MF904Q_STOCK_FIRMWARE_BACKUP'/'05_Private_Device_Data'
 results={}
 for name,length in [('seccfg',524288),('frp',1048576)]:
  original=base/(name+'.bin');current=folder/(name+'_CURRENT.bin')
  expected={'seccfg':'07854d2fef297a06ba81685e660c332de36d5d18d546927d30daad6d7fda1541','frp':'eccfa95f82fcbfbf9c15a9f2f50749a33b6fd5d66604c0768ec8daa1612e7a36'}
  if sha(original)!=expected[name]:raise ValueError('Original baseline hash changed; no comparison')
  if current.stat().st_size!=length:raise ValueError('Saved image incomplete')
  before=original.read_bytes();after=current.read_bytes()
  result=summary(before,after)
  if name=='frp':result['structure']=frp_status(after)
  else:
   start=after.find(b'AND_SECCFG_v');result['header_offset']=start
   if 0<=start and start+0x1860<=len(after):
    result['structure']={'magic':hex(struct.unpack_from('<I',after,start+0x10)[0]),'version':struct.unpack_from('<I',after,start+0x14)[0],'size':struct.unpack_from('<I',after,start+0x18)[0],
     'write_stage_marker_22_23':after[start+0x22:start+0x24].hex(),'endflag':hex(struct.unpack_from('<I',after,start+0x185c)[0]),'decrypted_attr':'UNKNOWN'}
   result['warning']='No decryption/hardware crypto called; header alone does not prove valid unlocked storage'
  results[name]=result
 with (folder/'OFFLINE_COMPARISON.json').open('x',encoding='utf8') as f:json.dump(results,f,indent=2)
 with (folder/'REPORT_AR.md').open('x',encoding='utf8') as f:
  f.write('# نتائج قراءة DA المحدودة\n\nاكتملت النطاقات الثلاثة وتحقق الحجم/checksum وبصمات الملفات.\n\n'+json.dumps(results,indent=2)+'\n\nالاختلاف لا يثبت زمن الكتابة أو نجاح Unlock. لا يوجد أمر كتابة أو انتقال آلي بعد القراءة.\n')
 hashes={f.name:sha(f) for f in folder.iterdir() if f.is_file() and f.name!='SHA256.json'}
 (folder/'SHA256.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
if __name__=='__main__':
 if '--approved-live' not in sys.argv:print('OFFLINE_DEFAULT. No inventory, COM, or device connection.')
 else:
  try:live()
  except BaseException as ex:print('STOP_UNKNOWN_NO_RETRY '+repr(ex),flush=True)
