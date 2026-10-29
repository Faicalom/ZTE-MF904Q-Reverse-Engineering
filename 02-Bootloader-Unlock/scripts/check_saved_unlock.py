"""Inspect saved textual evidence only; never contact a device."""
from pathlib import Path
import re,sys,json
def check(root):
 root=Path(root)
 status=json.loads((root/'evidence/capture_status.json').read_text())
 for phase in ['unlock','after']:
  if status[phase]!={'rc':0,'eof':True,'errors':[]}:raise ValueError('Incomplete/failed captured process')
 if status['factory_query']!={'status':'UNLOCKED_YES','exit_code':0,'unlocked':'yes'}:raise ValueError('Factory query failed')
 raw=(root/'evidence/unlock_stderr.txt').read_text()
 if re.search(r'FAILED|fastboot: error|timeout',raw,re.I):raise ValueError('Failed/ambiguous response')
 pairs=[(int(a,16),int(b,16)) for a,b in re.findall(r'V3:([a-fA-F0-9]{8}):([a-fA-F0-9]{8})',raw)]
 expected=[(20,0),(40,0x22),(41,0),(42,1),(43,0),(44,0x41e2320b),(45,1),(25,0),(26,0),(22,0),(23,0),(30,0x41e231ab),(31,0),(30,0x41e2323b),(31,0),(21,0)]
 if pairs!=expected or not re.search(r'(?m)^OKAY\b',raw):raise ValueError('Missing/out-of-order measurement')
 before=(root/'evidence/before_stderr.txt').read_text()
 if re.findall(r'(?m)^unlocked:\s*(yes|no)\s*$',before)!=['no']:raise ValueError('Before state not no')
 for name in ['after_stderr.txt','factory_lk_unlocked.txt']:
  if re.findall(r'(?m)^unlocked:\s*(yes|no)\s*$',(root/'evidence'/name).read_text())!=['yes']:raise ValueError('Independent yes missing')
 return 'PASS saved original-flow and independent-state evidence; not a live device check'
if __name__=='__main__':print(check(sys.argv[1] if len(sys.argv)>1 else '.'))
