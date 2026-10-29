"""One original Unlock, only after verified V3 diagnosis + final human token. No automatic WPS/reboot/retry."""
import pathlib,json,hashlib,sys,subprocess,threading,time,datetime,os
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'MF904Q_THIRD_UNLOCK_PREP_20261012'))
from entry import bind,select_cli,FASTBOOT,verify
from usb_metadata import snapshot
from capture import Capture
import lk_install_policy as policy
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def ready(ticket):
 a=json.loads(pathlib.Path(ticket).read_text())
 if a.get('approved') is not True or a.get('scope')!='one_original_unlock_v3_after_final_manual_confirmation':raise PermissionError('Independent final approval missing')
 if a['image_sha256']!=policy.HASHES['install']:raise ValueError('Wrong image')
 hashes=json.loads((P/'FINAL_UNLOCK_BUILD_SHA256.json').read_text())
 for n,h in hashes.items():
  if sha(P/n)!=h:raise ValueError('Build changed: '+n)
 folder=pathlib.Path(a['diagnostic_session']).resolve()
 if not folder.is_relative_to((P/'lk_probe_sessions').resolve()):raise ValueError('Wrong diagnostic session root')
 r=json.loads((folder/'RESULT.json').read_text())
 if r.get('status')!='CONSTRUCTOR_AND_CRYPTO_RETURNED' or r.get('exit_code')!=0 or r.get('constructor_return')!=0 or r.get('crypto_return')!=0 or r.get('gate_return')!=0:raise ValueError('Diagnostic gate not passed')
 from response_gate_context import parse
 parsed=parse((folder/'stdout.bin').read_bytes()+(folder/'stderr.bin').read_bytes())
 if parsed['status']!='CONSTRUCTOR_AND_CRYPTO_RETURNED' or parsed.get('gate_return')!=0:raise ValueError('Raw diagnostic not complete')
 return a

def run(ticket):
 a=ready(ticket)
 verify()
 processes=subprocess.run(['powershell.exe','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='fastboot.exe'\").Count"],capture_output=True,check=True)
 if processes.stdout.decode().strip()!='0':raise ValueError('Pending Fastboot; STOP')
 paths=json.loads((P.parent/'MF904Q_THIRD_UNLOCK_PREP_20261012/USB_REFERENCE.json').read_text())['usb']['paths']
 target=bind(snapshot(),paths,[])
 listed=subprocess.run([str(FASTBOOT),'devices'],capture_output=True,text=True,timeout=4)
 if listed.returncode:raise ValueError('Enumeration failure')
 serial=select_cli(listed.stdout,target)
 if hashlib.sha256(serial.encode()).hexdigest()!=a['serial_sha256']:raise ValueError('Serial mismatch')
 folder=P/'unlock_sessions'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');folder.mkdir(parents=True)
 def query(label,command):
  child=subprocess.Popen([str(FASTBOOT),'-s',serial]+command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);capture=Capture(child,folder,label)
  while child.poll() is None:
   try:time.sleep(.1)
   except KeyboardInterrupt:capture.event('CTRL_C_IGNORED')
  return capture.finish()
 if bind(snapshot(),paths,[])['instance']!=target['instance']:raise ValueError('Identity changed before query')
 pre=query('before',['getvar','unlocked'])
 if pre['rc']!=0 or not pre['eof'] or pre['errors']:raise ValueError('Pre-query UNKNOWN; no Unlock')
 import re
 values=re.findall(r'(?m)^\s*(?:\(bootloader\)\s*)?unlocked:\s*(yes|no)\s*$',pre['text'])
 if values==['yes']:print('ALREADY_UNLOCKED_STOP');return
 if values!=['no']:raise ValueError('Unlocked ambiguous; STOP')
 print('Current unlocked=no. Type SEND_UNLOCK_V3 to send ONE original flashing unlock. Userdata erase and seccfg writes possible. No WPS requested yet.',flush=True)
 if input().strip()!='SEND_UNLOCK_V3':print('CANCELLED_BEFORE_DISPATCH');return
 if bind(snapshot(),paths,[])['instance']!=target['instance']:raise ValueError('Device changed before dispatch')
 latch=pathlib.Path(os.environ['LOCALAPPDATA'])/'MF904QProject/LK_GATE_CONTEXT_FINAL_UNLOCK_20261013';latch.mkdir(parents=True,exist_ok=True)
 policy.reserve(latch/'UNLOCK_ATTEMPT.json',dict(image_sha256=a['image_sha256'],session=str(folder)))
 child=subprocess.Popen([str(FASTBOOT),'-s',serial,'flashing','unlock'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 cap=Capture(child,folder,'unlock');cap.event('HOST_DISPATCH_NOT_RECEIPT',pid=child.pid)
 print('WAIT_FOR_LCD. No automatic WPS. Keep CMD/power/USB. Mark LCD_DIALOG_SEEN or LCD_4G; decide WPS separately.',flush=True)
 controls=threading.Event();controls.clear()
 def markers():
  decided=False
  while child.poll() is None:
   try:v=input().strip()
   except EOFError:return
   if child.poll() is not None:return
   cap.event('HUMAN_MARKER',value=v,physical_timestamp_not_measured=True)
   if v in ['LCD_DIALOG_SEEN','DECIDE_WPS_WITHOUT_LCD']:decided=True;print('Separate WPS decision recorded. If you accept erase/seccfg writes, type ACCEPT_ERASE_AND_SECCFG_WRITE.',flush=True)
   elif v=='ACCEPT_ERASE_AND_SECCFG_WRITE' and decided:
    if controls.is_set():print('Already requested once; no repeat.',flush=True);continue
    controls.set();print('PRESS_WPS_ONCE: press and release manually once. Mark WPS_PRESSED / WPS_RELEASED when possible. Never repeat.',flush=True)
 thread=threading.Thread(target=markers,daemon=True);thread.start()
 while child.poll() is None:
  try:time.sleep(.1)
  except KeyboardInterrupt:cap.event('CTRL_C_IGNORED_RETAIN_PIPES')
 result=cap.finish();(folder/'UNLOCK_RESULT.json').write_text(json.dumps(result,indent=2))
 if result['rc']!=0 or not result['eof'] or result['errors'] or 'FAILED' in result['text']:print('UNLOCK_UNKNOWN_ERROR_STOP. No query/retry automatically.');return
 if bind(snapshot(),paths,[])['instance']!=target['instance']:raise ValueError('Identity changed after Unlock; no query')
 after=query('after',['getvar','unlocked'])
 values=re.findall(r'(?m)^\s*(?:\(bootloader\)\s*)?unlocked:\s*(yes|no)\s*$',after['text'])
 status=values[0] if after['rc']==0 and after['eof'] and not after['errors'] and len(values)==1 else 'UNKNOWN'
 (folder/'FINAL_RESULT.json').write_text(json.dumps(dict(unlocked=status,response=after),indent=2))
 print('LK unlocked: '+status+'. STOP; no reboot/storage read/retry. seccfg read requires a separately coordinated DA transition.')
 (folder/'SHA256.json').write_text(json.dumps({f.name:sha(f) for f in folder.iterdir() if f.is_file()},indent=2))
if __name__=='__main__':
 if '--approved-live' not in sys.argv:print('OFFLINE_DEFAULT')
 else:
  try:run(sys.argv[-1])
  except Exception as e:print('STOP_UNKNOWN_NO_RETRY '+repr(e))
