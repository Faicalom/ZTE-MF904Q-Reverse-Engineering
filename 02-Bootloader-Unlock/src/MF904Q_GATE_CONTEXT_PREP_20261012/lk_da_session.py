# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""No device access by default. Separate exact approval required before live execution."""
import pathlib,sys,json,hashlib,datetime,time,os,subprocess,struct
ROOT=pathlib.Path(__file__).resolve().parent
OLD=ROOT.parent/'MF904Q_DA_HANDSHAKE_FIX_20261012'
sys.path.insert(0,str(OLD))
import limited_da as historical
from limited_da import Receiver,Log,Guard,readiness_handshake,query,check_hw,version_queries,probe,stage2_requirements,upload,geometry,check_geometry,read_range,choose_port
import lk_install_policy as policy
def transcripts(da1,da2):
 original=historical.transcripts(da1,da2)
 original={k:v for k,v in original.items() if not k.startswith('READ_')}
 original.update(READ_GPT=policy.read_frames(0,17408),READ_LK=policy.read_frames(policy.OFFSET,policy.SIZE),WRITE_LK=policy.write_frames(PAYLOAD,MODE),READBACK_LK=policy.read_frames(policy.OFFSET,policy.SIZE))
 return original
def connect_verified(port,log,da1,da2,reference,prefix):
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
 return guard,recv,phase

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def prepare(mode):
 build=json.loads((ROOT/'LK_SESSION_BUILD_SHA256.json').read_text())
 for name,digest in build.items():
  if sha(ROOT/name)!=digest:raise ValueError('LK session build changed: '+name)
 payload=policy.image(mode)
 stages=historical.prepare() # validates unchanged DA1/DA2, runtime and historical build
 return payload,stages,sha(ROOT/'LK_SESSION_BUILD_SHA256.json')
def save(log,name,data):
 path=log.folder/name
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 if sha(path)!=policy.digest(data):raise ValueError('Saved evidence hash mismatch')
 log.event('FILE_SAVED',name=name,length=len(data),sha256=sha(path))
def execute_transfer(guard,recv,phase,log,mode,payload):
 phase('READ_GPT',60);gpt,_=read_range(guard.send,recv.receive,8,0,17408,policy.USER_SIZE);guard.complete()
 parts=historical.check_gpt(gpt,(OLD/'GPT_REFERENCE.bin').read_bytes());policy.check_gpt(gpt,(OLD/'GPT_REFERENCE.bin').read_bytes(),parts);save(log,'GPT_BEFORE.bin',gpt)
 phase('READ_LK',60);current,_=read_range(guard.send,recv.receive,8,policy.OFFSET,policy.SIZE,policy.USER_SIZE);guard.complete();save(log,'LK_BEFORE.bin',current)
 if mode=='install' and policy.digest(current)!='0e57325503671d4e9ae6daa54f392542623477914928439097bbae3252f8f684':raise ValueError('Current LK differs from verified installed V3; no install')
 phase('WRITE_LK',60)
 policy.Writer(guard.send,recv.receive,log.event).write(payload,mode,approved=True,identity_verified=True,gpt_verified=True,current_saved=True);guard.complete()
 phase('READBACK_LK',60);back,_=read_range(guard.send,recv.receive,8,policy.OFFSET,policy.SIZE,policy.USER_SIZE);guard.complete();save(log,'LK_READBACK.bin',back)
 policy.check_readback(back,mode);log.result.update(status='LK_FULL_READBACK_VERIFIED',mode=mode,image_sha256=policy.digest(back))
def live(mode):
 global PAYLOAD,MODE
 MODE=mode;PAYLOAD,stages,build=prepare(mode)
 ticket=json.loads((ROOT/('LK_'+mode.upper()+'_APPROVAL.json')).read_text())
 policy.approval(ticket,mode,build)
 q=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='fastboot.exe'\").Count"],capture_output=True,check=True)
 if q.stdout.decode().strip()!='0':raise ValueError('Existing Fastboot process; no transition')
 from usb_metadata import snapshot
 import serial
 from serial.tools import list_ports
 print('Host preparation complete. No modem command yet. Type ARM_LK_'+mode.upper()+' for this exact LK image.',flush=True)
 if input().strip()!='ARM_LK_'+mode.upper():return
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject'/'LK_GATE_CONTEXT_SESSION_20261012'
 latch.mkdir(parents=True,exist_ok=True)
 policy.reserve(latch/(mode+'_ATTEMPT.json'),dict(mode=mode,build_sha256=build))
 mutex=policy.SessionMutex();mutex.__enter__()
 log=None;port=None;finished=False
 try:
  folder=ROOT/'lk_private_sessions'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
  log=Log(folder)
  print('Manual transition only: disconnect USB, power off normally, keep sound power source and modem OFF. No WPS/Reset. Type OFF once OFF and USB disconnected.',flush=True)
  if input().strip().upper()!='OFF':raise ValueError('Manual OFF confirmation missing')
  if any(r['fastboot'] or 'VID_0E8D' in r['usb_id'] for r in snapshot()):raise ValueError('USB not disconnected')
  ref=json.loads((OLD/'USB_REFERENCE.json').read_text());paths=ref['usb']['paths']
  port=serial.Serial(port=None,baudrate=115200,timeout=.02,write_timeout=.2,xonxoff=False,rtscts=False,dsrdtr=False);port.dtr=True;port.rts=True
  print('READY_FOR_PRELOADER: connect powered-off modem USB ONCE. No buttons.',flush=True);log.event('READY_FOR_PRELOADER')
  deadline=time.monotonic()+120;target=None
  while time.monotonic()<deadline:
   target=choose_port(list_ports.comports())
   if target:break
   time.sleep(.02)
  if target is None:raise TimeoutError('Preloader not found; no retry')
  rows=[r for r in snapshot() if r['usb_id']=='VID_0E8D&PID_2000']
  if len(rows)!=1 or not set(rows[0]['paths'])&set(paths) or not any(target.device in s for s in rows[0]['name']):raise ValueError('COM/physical USB mismatch')
  port.port=target.device;log.event('COM_OPEN_ONCE',com=target.device);port.open()
  guard,recv,phase=connect_verified(port,log,*stages,json.loads((OLD/'DA_SUCCESS_REFERENCE_PRIVATE.json').read_text()),(OLD/'GPT_REFERENCE.bin').read_bytes())
  port.write_timeout=15 # proven logo writer bound; 0.2s handshake bound is unsuitable for bulk LK data
  log.event('WRITE_TRANSPORT_TIMEOUT',seconds=15,source='validated original logo writer',packet_maximum=0x100000,actual_lk_chunk=policy.SIZE)
  execute_transfer(guard,recv,phase,log,mode,PAYLOAD);finished=True
 except BaseException as ex:
  if log:log.finish(ex)
  raise
 else:
  if log:log.finish()
 finally:
  if port is not None and port.is_open:port.close()
  mutex.__exit__(None,None,None) # OS lock only; never delete persistent attempt evidence.
  print('STOP. COM closed. No reboot/Unlock/automatic recovery. Evidence: '+str(log.folder if log else ROOT),flush=True)
if __name__=='__main__':
 if '--approved-live' not in sys.argv:print('OFFLINE_DEFAULT. No COM or USB inventory. Use --check-build for host validation.')
 if '--check-build' in sys.argv:
  prepare('install');prepare('restore');print('HOST_BUILD_AND_DA_HASHES_PASS. No port opened.')
 elif '--approved-live' in sys.argv:
  try:live(sys.argv[-1])
  except BaseException as ex:print('STOP_UNKNOWN_NO_RETRY '+repr(ex),flush=True)
