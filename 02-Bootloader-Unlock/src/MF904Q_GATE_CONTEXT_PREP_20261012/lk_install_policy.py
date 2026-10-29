# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Bounded DA2 LK transport. No port opening, inventory, or execution at import."""
import pathlib,hashlib,struct,json,os
P=pathlib.Path(__file__).resolve().parent
ORIGINAL=P.parent/'MF904Q_STOCK_FIRMWARE_BACKUP/04_Firmware_Partitions/lk.bin'
CANDIDATE=P/'lk_V3_FINAL.bin'
OFFSET=58368*512;SIZE=1024*512;PACKET=0x100000;USER_SIZE=3825205248
HASHES={'install':'f566f0a28297f9459978a41b61c7b3ce254f5ad0e3cc4ec71fa37e094bbe8077',
 'restore':'07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596'}
def digest(b):return hashlib.sha256(b).hexdigest()
def image(mode):
 if mode not in HASHES:raise ValueError('Unknown mode')
 b=(CANDIDATE if mode=='install' else ORIGINAL).read_bytes()
 validate(b,mode);return b
def validate(b,mode):
 if mode not in HASHES or len(b)!=SIZE or digest(b)!=HASHES[mode]:raise ValueError('Exact pinned LK image required')
def reserve(path,data):
 with pathlib.Path(path).open('x',encoding='utf8') as f:json.dump(data,f);f.flush();os.fsync(f.fileno())
class SessionMutex:
 """OS concurrency lock, released by Windows on process death; evidence locks remain."""
 def __enter__(self):
  import ctypes as c
  from ctypes import wintypes as w
  self.k=c.WinDLL('kernel32',use_last_error=True)
  self.k.CreateMutexW.argtypes=[c.c_void_p,w.BOOL,w.LPCWSTR];self.k.CreateMutexW.restype=w.HANDLE
  self.k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];self.k.WaitForSingleObject.restype=w.DWORD
  self.k.ReleaseMutex.argtypes=[w.HANDLE];self.k.CloseHandle.argtypes=[w.HANDLE]
  self.h=self.k.CreateMutexW(None,False,'Local\\MF904Q_LK_DIAGNOSTIC_SESSION')
  if not self.h:raise c.WinError(c.get_last_error())
  result=self.k.WaitForSingleObject(self.h,0)
  if result not in (0,0x80):self.k.CloseHandle(self.h);raise PermissionError('Concurrent LK session')
  return self
 def __exit__(self,*args):self.k.ReleaseMutex(self.h);self.k.CloseHandle(self.h)
def read_frames(offset,length):
 if (offset,length) not in [(0,17408),(OFFSET,SIZE)]:raise ValueError('Read outside GPT/LK')
 return [b'\x72',b'\x60',b'\x08',b'\xd6',b'\x0c',b'\x02',struct.pack('>Q',offset),struct.pack('>Q',length),struct.pack('>I',0x100000),b'\x5a']
def write_frames(b,mode):
 validate(b,mode)
 return [b'\x62',b'\x01',b'\x08',struct.pack('>Q',OFFSET),struct.pack('>Q',SIZE),struct.pack('>I',PACKET),b'\x5a',b,struct.pack('>H',sum(b)&65535)]
class Writer:
 def __init__(self,send,receive,event):self.send=send;self.receive=receive;self.event=event;self.attempted=False
 def write(self,b,mode,*,approved,identity_verified,gpt_verified,current_saved):
  validate(b,mode)
  if not all((approved,identity_verified,gpt_verified,current_saved)):raise PermissionError('Fresh gates/explicit approval required')
  if self.attempted:raise PermissionError('Attempt already consumed')
  self.attempted=True # before first TX, including a failed or short transport
  frames=write_frames(b,mode)
  self.event('LK_WRITE_ATTEMPT',mode=mode,offset=OFFSET,size=SIZE,sha256=digest(b))
  for f in frames[:6]:self.send(f)
  if self.receive(1)!=b'\x5a':raise ValueError('Write header ACK invalid; no retry')
  for f in frames[6:]:self.send(f)
  if self.receive(1)!=b'\x69':raise ValueError('Write data ACK invalid; no retry')
  self.event('LK_TRANSFER_ACKED',readback_required=True)
def check_readback(b,mode):
 validate(b,mode);return 'LK_FULL_READBACK_VERIFIED'
def check_gpt(prefix,original,parts):
 if len(prefix)!=17408 or prefix!=original:raise ValueError('Exact GPT differs')
 lk=[p for p in parts if p['name']=='lk']
 if len(lk)!=1 or (lk[0]['offset'],lk[0]['size'])!=(OFFSET,SIZE):raise ValueError('LK bounds mismatch')
 if OFFSET%512 or SIZE%512 or OFFSET+SIZE>USER_SIZE:raise ValueError('Invalid geometry')
def approval(ticket,mode,build_hash):
 if ticket!=dict(approved=True,scope='one_lk_'+mode,build_sha256=build_hash,image_sha256=HASHES[mode],accept_modified_lk_boot_risk=True):
  raise PermissionError('Separate exact LK action approval required')
