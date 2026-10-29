"""Verify only local publication files. No device imports or network."""
from pathlib import Path
import hashlib,sys
def verify(root):
 root=Path(root).resolve();checked=0
 for line in (root/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
  if not line or line.startswith('#'):continue
  digest,name=line.split('  ',1);p=(root/name).resolve()
  if not p.is_relative_to(root):raise ValueError('Path escapes release root')
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Missing/changed file: '+name)
  checked+=1
 if not checked:raise ValueError('Empty manifest')
 return checked
if __name__=='__main__':
 print('PASS local files:',verify(sys.argv[1] if len(sys.argv)>1 else '.'))
