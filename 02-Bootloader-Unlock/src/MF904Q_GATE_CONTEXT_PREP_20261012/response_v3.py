"""Strict parser for exact-reader gate contexts; never infer Unlock success."""
import re,json,pathlib
def parse(raw):
 if re.search(rb'FAILED|fastboot: error|usb_read|timeout',raw,re.I):raise ValueError('Remote/transport failure: UNKNOWN')
 if not re.search(rb'(?m)^OKAY(?: |\[|$)',raw):raise ValueError('Terminal OKAY missing')
 pairs=[tuple(int(x,16) for x in m) for m in re.findall(rb'V3:([0-9a-fA-F]{8}):([0-9a-fA-F]{8})(?![0-9a-fA-F])',raw)]
 if [s for s,v in pairs]!=list(range(40,46))+[3]+list(range(40,46))+[6]+list(range(40,46))+[7]:raise ValueError('Incomplete or out-of-order context transcript')
 m=json.loads((pathlib.Path(__file__).parent/'BUILD_MANIFEST.json').read_text());samples=[]
 for k,index in enumerate([0,7,14]):
  cfg,word,arg,result,site,read=[v for s,v in pairs[index:index+6]]
  if site!=m['probe_call_sites'][k] or arg!=1 or cfg not in (0,0x11,0x22):raise ValueError('Caller/argument/config mismatch')
  if read!=(0 if cfg==0x11 else 1):raise ValueError('Unexpected number of actual MMIO reads')
  expected=1 if cfg==0x11 else (word>>1)&1
  if result!=expected:raise ValueError('Original gate decision inconsistent with captured inputs')
  samples.append(dict(phase=['before_constructor','before_crypto','after_crypto'][k],config=cfg,dword=word if read else None,argument=arg,result=result,caller_lr=site,mmio_read=bool(read)))
 if pairs[6][1]!=0 or pairs[13][1]!=0 or pairs[20][1]!=0:raise ValueError('Constructor/crypto/cleanup returned an error')
 return dict(status='CONSTRUCTOR_AND_CRYPTO_RETURNED',constructor_return=0,crypto_return=0,gate_return=samples[-1]['result'],samples=samples,storage_write_tested=False,unlocked_measured=False,ciphertext_validated=False,gate_input_changed=samples[1]['config']!=samples[2]['config'] or samples[1]['dword']!=samples[2]['dword'])
