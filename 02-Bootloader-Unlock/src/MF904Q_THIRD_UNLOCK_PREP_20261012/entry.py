"""Native Preloader entry then ONE LK read. No ADB, no automatic exit."""
import argparse,datetime,hashlib,json,os,pathlib,subprocess,time
from core import anchor,preloader,bind,select_cli,args,parse_reply,reserve,digest,COMMAND
from entry_protocol import ProbeModel
HERE=pathlib.Path(__file__).resolve().parent
FASTBOOT=pathlib.Path(r'C:/Users/YOUR_WINDOWS_USER\AppData\Local\Android\Sdk\platform-tools\fastboot.exe')
FBHASH='b2d9cbff4ce9ae7eb448cfc831bafc867935f50f5be38f8f81057fd7eb3b8d86'
class Log:
 def __init__(self):
  self.folder=HERE/'sessions'/datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).strftime('%Y%m%d_%H%M%S_%f');self.folder.mkdir(parents=True);self.f=(self.folder/'events.jsonl').open('x',encoding='utf8')
 def add(self,kind,**data):
  self.f.write(json.dumps({'time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).isoformat(),'kind':kind,**data},ensure_ascii=False)+'\n');self.f.flush();os.fsync(self.f.fileno())
 def close(self):
  self.f.close();(self.folder/'SHA256.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in self.folder.iterdir() if p.is_file()},indent=2))
def verify():
 manifest=json.loads((HERE/'APPROVED_BUILD_HASHES.json').read_text(encoding='utf-8-sig'))
 for name,value in manifest.items():
  if digest((HERE/name).read_bytes())!=value:raise ValueError('Prepared artifact mismatch: '+name)
 import serial
 from serial.tools import list_ports
 deps=json.loads((HERE/'SERIAL_RUNTIME.json').read_text())
 if serial.__version__!=deps['version']:raise ValueError('Serial library version mismatch')
 for name,value in deps['files'].items():
  if digest(pathlib.Path(name).read_bytes())!=value:raise ValueError('Serial dependency hash mismatch')
 if pathlib.Path(serial.__file__).resolve()!=pathlib.Path(deps['module']).resolve():raise ValueError('Serial import came from unexpected runtime')
 if digest(FASTBOOT.read_bytes())!=FBHASH:raise ValueError('Fastboot tool changed')
 stock=HERE.parent/'MF904Q_STOCK_FIRMWARE_BACKUP'
 for rel,sha in [('03_Boot_Regions/boot1.bin','1aa86a3230a91d4678e154e757bbe7a49b64287906b7d43ed3e875d3f8b1d744'),('04_Firmware_Partitions/lk.bin','07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596')]:
  if digest((stock/rel).read_bytes())!=sha:raise ValueError('Stock boot evidence changed')
def run(approval):
 a=json.loads(pathlib.Path(approval).read_text(encoding='utf-8-sig'))
 if a.get('approved') is not True or a.get('safe_power_available') is not True or a.get('swollen_battery_excluded') is not True or a.get('scope')!='third_entry_checks_interactive_unlock' or a.get('accept_missed_window_android_risk') is not True or a.get('coordinated_manual_power_cycle') is not True or a.get('entry_sha256')!=digest(pathlib.Path(__file__).read_bytes()):raise ValueError('Independent explicit approval required')
 verify()
 import serial
 from serial.tools import list_ports
 from usb_metadata import snapshot
 print('No button now. A arms metadata verification only. No WPS/Reset. Q cancels.',flush=True)
 if input().strip().upper()!='A':return
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject'/'THIRD_UNLOCK_ENTRY_20261012'
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
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--approved-live');a=p.parse_args()
 if a.approved_live:run(a.approved_live)
 else:print('READY_FOR_APPROVAL. Offline default. No live entry, query, or exit.')
