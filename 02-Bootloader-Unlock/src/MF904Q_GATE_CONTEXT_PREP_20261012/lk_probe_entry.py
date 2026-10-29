"""Exact diagnostic entry and one read response. No Unlock/erase/reboot command."""
import pathlib,sys,json,datetime,os,subprocess,hashlib,re,threading,time
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'MF904Q_THIRD_UNLOCK_PREP_20261012'))
import entry as historical
from entry import verify,anchor,preloader,bind,select_cli,args,parse_reply,reserve,digest,COMMAND,ProbeModel,FASTBOOT
HERE=historical.HERE
class Log(historical.Log):
 def __init__(self):
  self.folder=ROOT/'lk_entry_sessions'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');self.folder.mkdir(parents=True)
  self.f=(self.folder/'events.jsonl').open('x',encoding='utf8')
def run(approval):
 a=json.loads(pathlib.Path(approval).read_text(encoding='utf-8-sig'))
 if a.get('approved') is not True or a.get('safe_power_available') is not True or a.get('swollen_battery_excluded') is not True or a.get('scope')!='lk_diagnostic_entry_only' or a.get('accept_missed_window_android_risk') is not True or a.get('coordinated_manual_power_cycle') is not True or a.get('entry_sha256')!=digest(pathlib.Path(__file__).read_bytes()):raise ValueError('Independent explicit approval required')
 verify()
 import serial
 from serial.tools import list_ports
 from usb_metadata import snapshot
 print('No button now. A arms metadata verification only. No WPS/Reset. Q cancels.',flush=True)
 if input().strip().upper()!='A':return
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject'/'LK_GATE_CONTEXT_ENTRY_20261012'
 reserve(latch/'ATTEMPT_RESERVED.json','entry_and_one_read')
 log=Log();port=None
 try:
  initial=snapshot();paths=json.loads((HERE/'USB_REFERENCE.json').read_text())['usb']['paths']
  if any('VID_0E8D' in r['usb_id'] or r['fastboot'] for r in initial):raise ValueError('Modem must remain disconnected and powered off')
  if any(r['fastboot'] for r in initial):raise ValueError('Fastboot baseline ambiguous')
  log.add('HISTORICAL_VERIFIED_PORT_ANCHOR',paths=paths,current_device_unverified=True)
  print('COORDINATION ONLY: approved sound power source required. Never use the swollen battery. Keep modem OFF and USB disconnected. No WPS/Reset. Type OFF only when this state is confirmed.',flush=True)
  if input().strip().upper()!='OFF':raise ValueError('Power off not confirmed')
  baseline=snapshot()
  if any('VID_0E8D' in r['usb_id'] or r['fastboot'] for r in baseline):raise ValueError('Disconnected baseline not clear')
  print('READY_FOR_PRELOADER: connect powered-off modem USB ONCE, no device buttons. Missed window may boot Android. No automatic retries.',flush=True);log.add('READY_FOR_PRELOADER')
  end=time.monotonic()+120;target=None
  while time.monotonic()<end:
   ports=[p for p in list_ports.comports() if p.vid==0x0e8d and p.pid==0x2000]
   if len(ports)>1:raise ValueError('Ambiguous Preloader COM')
   if ports:target=ports[0];break
   time.sleep(.02)
  if target is None:raise TimeoutError('No Preloader window observed; no mode request')
  row=preloader(snapshot(),paths)
  if not any(target.device in s for s in row['name']):raise ValueError('COM does not match devnode label')
  log.add('PRELOADER_BOUND',com=target.device,paths=row['paths'])
  port=serial.Serial(port=None,baudrate=115200,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=.02,write_timeout=.2,xonxoff=False,rtscts=False,dsrdtr=False);port.dtr=True;port.rts=True;port.port=target.device;port.open()
  model=ProbeModel(True);sent=False;start=time.monotonic()
  while model.state in ('WAIT_READY','WAIT_ACK'):
   data=port.read(64);ms=int((time.monotonic()-start)*1000)
   if data:
    log.add('RX',hex=data.hex());n=len(model.events);model.feed(data,ms)
    if 'FASTBOOT' in model.events[n:]:raise ValueError('Unexpected echo; no retry')
   else:model.tick(ms)
   if model.planned_tx and not sent and model.state=='WAIT_ACK':
    reserve(latch/'ENTRY_TX_RESERVED.json','FASTBOOT_ASCII_8_bytes');sent=True;log.add('ENTRY_WRITE_STARTED',hex=b'FASTBOOT'.hex())
    n=port.write(b'FASTBOOT');log.add('ENTRY_WRITE_RETURNED',written=n)
    if n!=8:raise ValueError('Short mode request; no retry')
  if not sent or model.state!='ACK_RECEIVED_WAIT_USB':raise ValueError('Entry not acknowledged: '+model.state)
  log.add('ACK_TOOBTSAF');port.close();port=None
  end=time.monotonic()+10;candidate=None
  while time.monotonic()<end:
   rows=snapshot()
   if any(r['fastboot'] for r in rows):candidate=bind(rows,paths,baseline);break
   time.sleep(.02)
  if candidate is None:raise TimeoutError('Fastboot not verified. Do not retry or reboot automatically')
  r=subprocess.run([str(FASTBOOT),'devices'],capture_output=True,text=True,timeout=4)
  if r.returncode:raise ValueError('CLI enumeration failed')
  targetSerial=select_cli(r.stdout,candidate);log.add('FASTBOOT_IDENTITY_BOUND',serial_hash=digest(targetSerial.encode()),paths=candidate['paths'])
  again=bind(snapshot(),paths,baseline)
  if again['instance']!=candidate['instance']:raise ValueError('Fastboot changed before read')
  return targetSerial,candidate

 except Exception as e:
  log.add('STOP_NO_RETRY',type=type(e).__name__,message=str(e));raise
 finally:
  if port is not None and port.is_open:port.close()
  log.add('NO_EXIT_SENT',reboot_commands=0,entry_queries=0);log.close();print('Logs: '+str(log.folder),flush=True)

def parse_diagnostic(raw):
 from response_gate_context import parse
 return parse(raw)

def inspect_ticket(path):
 a=json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))
 if a.get('probe_once') is not True or a.get('candidate_sha256')!='f566f0a28297f9459978a41b61c7b3ce254f5ad0e3cc4ec71fa37e094bbe8077':raise PermissionError('Exact diagnostic probe approval missing')
 hashes=json.loads((ROOT/'LK_SESSION_BUILD_SHA256.json').read_text())
 for name,expected in hashes.items():
  if digest((ROOT/name).read_bytes())!=expected:raise ValueError('Build mismatch before diagnostic entry')
 # The successful installation must have complete matching readback, not merely ACKs.
 folder=pathlib.Path(a['verified_install_session']).resolve()
 if not folder.is_relative_to((ROOT/'lk_private_sessions').resolve()):raise ValueError('Installation evidence outside session root')
 result=json.loads((folder/'RESULT.json').read_text())
 if result.get('status')!='LK_FULL_READBACK_VERIFIED' or result.get('mode')!='install' or digest((folder/'LK_READBACK.bin').read_bytes())!=a['candidate_sha256']:raise ValueError('Verified candidate installation missing')
 return a
def probe_once(ticket):
 a=inspect_ticket(ticket)
 q=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='fastboot.exe'\").Count"],capture_output=True,check=True)
 if q.stdout.decode().strip()!='0':raise ValueError('Previous Fastboot process exists')
 serial,target=run(ticket)
 if not serial:raise ValueError('Entry cancelled')
 from usb_metadata import snapshot
 paths=json.loads((HERE/'USB_REFERENCE.json').read_text())['usb']['paths']
 current=bind(snapshot(),paths,[])
 if current['instance']!=target['instance']:raise ValueError('USB identity changed before probe')
 folder=ROOT/'lk_probe_sessions'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');folder.mkdir(parents=True)
 events=(folder/'events.jsonl').open('x',encoding='utf8',buffering=1)
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject'/'LK_GATE_CONTEXT_ENTRY_20261012'
 reserve(latch/'PROBE_TX_RESERVED.json','one_diagnostic_get_unlock_ability_no_unlock')
 event_lock=threading.Lock();capture_errors=[]
 def event(kind,**kw):
  with event_lock:
   events.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),event=kind,**kw))+'\n');events.flush();os.fsync(events.fileno())
 event('PROBE_PROCESS_DISPATCH',serial_hash=digest(serial.encode()),host_dispatch_not_usb_receipt=True)
 child=subprocess.Popen([str(FASTBOOT),'-s',serial,'flashing','get_unlock_ability'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 def capture(pipe,name):
  try:
   with (folder/name).open('xb',buffering=0) as f:
    while True:
     data=os.read(pipe.fileno(),4096)
     if not data:break
     f.write(data);os.fsync(f.fileno());event('OUTPUT_CHUNK',stream=name,length=len(data),sha256=digest(data))
     try:
      with event_lock:print(data.decode('utf-8',errors='replace'),end='',flush=True)
     except OSError:pass
  except BaseException as ex:capture_errors.append(repr(ex))
  finally:pipe.close()
 threads=[threading.Thread(target=capture,args=(pipe,name)) for pipe,name in [(child.stdout,'stdout.bin'),(child.stderr,'stderr.bin')]]
 for thread in threads:thread.start()
 print('DIAGNOSTIC_REQUEST_PENDING. No buttons, second command, or automatic timeout termination. Keep power/USB and this CMD open.',flush=True)
 while child.poll() is None:
  try:time.sleep(.1)
  except KeyboardInterrupt:event('CTRL_C_IGNORED_TO_RETAIN_PIPES')
 for thread in threads:thread.join()
 event('PROCESS_EXIT',exit_code=child.returncode)
 raw=(folder/'stdout.bin').read_bytes()+(folder/'stderr.bin').read_bytes();result=dict(status='UNKNOWN',exit_code=child.returncode)
 if capture_errors:result['capture_errors']=capture_errors
 if child.returncode==0 and not capture_errors:
  try:result.update(**parse_diagnostic(raw))
  except ValueError as ex:result['error']=str(ex)
 (folder/'RESULT.json').write_text(json.dumps(result,indent=2));events.close()
 (folder/'SHA256.json').write_text(json.dumps({f.name:digest(f.read_bytes()) for f in folder.iterdir() if f.is_file()},indent=2))
 print(json.dumps(result));print('STOP. No Unlock or reboot. Evidence: '+str(folder))
if __name__=='__main__':
 if '--approved-live' not in sys.argv:print('OFFLINE_DEFAULT. No USB or COM access.')
 else:
  try:probe_once(sys.argv[-1])
  except Exception as ex:print('STOP_UNKNOWN_NO_RETRY '+repr(ex),flush=True)
