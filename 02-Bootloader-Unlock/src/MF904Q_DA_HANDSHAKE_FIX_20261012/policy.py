# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Exact TX transcripts per phase; no arbitrary command or read-range entrypoint."""
import struct,hashlib,json,os,pathlib
from stage2_protocol import config_fields
from backup_core import gpt_header,entries
DA_CONTAINER='aef234190ccb8145d2e3b8459741e9adb70f2caa8481aa216c1b25152afaca1f'
DA1_HASH='16160bfd628e56943dccc6982da92a30187ff1bec25ad144341268df63ca0f13'
DA2_HASH='4c71c41280414374ef704655dee944a430a701f879489b87188a2e1fc70b0e57'
USER_SIZE=3825205248
RANGES=((0,17408),(83361792,524288),(111149056,1048576))
def reserve(path,data):
 path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf8') as f:json.dump(data,f);f.flush();os.fsync(f.fileno())
def range_frames(offset,length):
 if (offset,length) not in RANGES or offset%512 or length%512 or offset+length>USER_SIZE:raise ValueError('Range outside exact allowlist')
 return [b'\x72',b'\x60',b'\x08',b'\xd6',b'\x0c',b'\x02',struct.pack('>Q',offset),struct.pack('>Q',length),struct.pack('>I',0x100000),b'\x5a']
def transcripts(da1,da2):
 if hashlib.sha256(da1).hexdigest()!=DA1_HASH or hashlib.sha256(da2).hexdigest()!=DA2_HASH:raise ValueError('Unmodified DA required')
 return {'HANDSHAKE':[bytes([x]) for x in [0xa0,0x0a,0x50,0x05]],'HW':[b'\xfd'],
 'IDENTITY':[b'\xfc',b'\xd8'],'VERSIONS':[b'\xfe',b'\xff'],
 'DA1':[b'\xd7',struct.pack('>I',0x200000),struct.pack('>I',98000),struct.pack('>I',256)]+[da1[i:i+1024] for i in range(0,len(da1),1024)]+[b'\xd5',struct.pack('>I',0x200000)],
 'CONFIG':[b'\x5a']+[data for _,data in config_fields(1,255)],
 'DA2':[struct.pack('>I',v) for v in [0x40000000,222752,0x1000]]+[x for i in range(0,len(da2),4096) for x in [da2[i:i+4096]]]+[b'\x5a'],
 **{'READ_'+str(i):range_frames(*r) for i,r in enumerate(RANGES)}}
class Guard:
 def __init__(self,expected,write,event=lambda *a,**k:None):self.expected=expected;self.write=write;self.event=event;self.phase=None;self.index=0;self.visited=set();self.failed=False;self.sync_probes=0;self.fresh_ready=False
 def begin(self,phase):
  if self.failed or phase in self.visited or phase not in self.expected:raise ValueError('Phase rejected/repeat')
  if phase!=list(self.expected)[len(self.visited)]:raise ValueError('Out-of-order phase')
  if self.phase is not None and self.index!=len(self.expected[self.phase]):raise ValueError('Incomplete previous TX phase')
  self.phase=phase;self.index=0;self.visited.add(phase)
 def note_ready(self):
  if self.phase=='HANDSHAKE' and self.index==1:self.fresh_ready=True
 def send(self,data):
  if not self.failed and self.phase=='HANDSHAKE' and self.index==1 and data==b'\xa0' and self.fresh_ready and self.sync_probes==1:
   self.fresh_ready=False;self.sync_probes+=1
   self.event('TX_ATTEMPT',phase=self.phase,index=0,resynchronization=True,data=data)
   try:
    n=self.write(data)
    if n!=1:raise OSError('Short synchronization write; no retry')
    self.event('TX_COMPLETE',phase=self.phase,written=n,resynchronization=True)
   except BaseException:self.failed=True;raise
   return
  if self.failed or self.phase is None or self.index>=len(self.expected[self.phase]) or data!=self.expected[self.phase][self.index]:
   self.failed=True;raise ValueError('TX not in approved transcript')
  self.event('TX_ATTEMPT',phase=self.phase,index=self.index,data=data)
  # Mark consumed before native write: even short write/exception cannot resend.
  self.index+=1
  if self.phase=='HANDSHAKE':
   self.fresh_ready=False
   if data==b'\xa0':self.sync_probes+=1
  try:
   n=self.write(data)
   if n!=len(data):raise OSError('Short write; no retry')
   self.event('TX_COMPLETE',phase=self.phase,written=n)
  except BaseException:self.failed=True;raise
 def complete(self):
  if self.failed or self.index!=len(self.expected[self.phase]):raise ValueError('Incomplete TX transcript')
def check_hw(info):
 expected={'hw_code':'0x0335','hw_version':'0x0000','hw_subcode':'0x8A00','hw_version_fc':'0xCA00','sw_version':'0x0000','target_config':'0x00000000','d8_status':'0x0000'}
 if any(info.get(k)!=v for k,v in expected.items()):raise ValueError('HW/protection identity mismatch')
def check_geometry(info,ref):
 for k in ['cid_wire_hex','user_size','boot1_size','boot2_size','ext_ram_size','ext_ram_type','emmc_status','ext_ram_status']:
  if k not in ref or info.get(k)!=ref[k]:raise ValueError('Geometry/CID mismatch: '+k)
 if info['user_size']!=USER_SIZE:raise ValueError('Wrong User capacity')
def check_gpt(prefix,original):
 if len(prefix)!=17408 or len(original)!=17408:raise ValueError('Incomplete GPT prefix')
 h=gpt_header(prefix[512:1024],1,USER_SIZE)
 a=h['table_lba']*512;z=a+h['length']
 if z>len(prefix):raise ValueError('GPT table outside prefix')
 parts=entries(prefix[a:z],h)
 if prefix!=original:raise ValueError('GPT prefix changed from verified target')
 d={p['name']:p for p in parts}
 for name,r in zip(['seccfg','frp'],RANGES[1:]):
  if name not in d or (d[name]['offset'],d[name]['size'])!=r:raise ValueError('Partition mapping mismatch')
 return parts
