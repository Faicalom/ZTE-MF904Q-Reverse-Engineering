"""Pure identity, reply and once-only gates. No device I/O."""
import hashlib,json,pathlib,re,os
COMMAND='flashing get_unlock_ability'
SERIAL_HASH='PRIVATE_SERIAL_HASH_NOT_INCLUDED'
def digest(b):return hashlib.sha256(b).hexdigest()
def identity_serial(row):return row['instance'].split('\\')[-1]
def anchor(rows):
    hits=[r for r in rows if r['usb_id']=='VID_0E8D&PID_2005' and digest(identity_serial(r).encode())==SERIAL_HASH and r['paths']]
    if len(hits)!=1:raise ValueError('No unique current MF904Q parent with known serial fingerprint')
    return hits[0]
def preloader(rows,paths):
    hits=[r for r in rows if r['usb_id']=='VID_0E8D&PID_2000']
    if len(hits)!=1 or not set(hits[0]['paths'])&set(paths):raise ValueError('Preloader absent/ambiguous/wrong current physical path')
    return hits[0]
def bind(rows,paths,baseline):
    hits=[r for r in rows if r['fastboot']]
    if len(hits)!=1:raise ValueError('Fastboot absent or globally ambiguous')
    r=hits[0]
    if r['usb_id']!='VID_0BB4&PID_0C01' or not set(r['paths'])&set(paths) or [s.upper() for s in r['service']]!=['WINUSB']:raise ValueError('Unexpected Fastboot USB identity/path/driver')
    if any(x['fastboot'] for x in baseline):raise ValueError('Pre-existing Fastboot target')
    return r
def select_cli(stdout,row):
    parts=[s.split() for s in stdout.splitlines() if s.strip()]
    if len(parts)!=1 or len(parts[0])!=2 or parts[0][1]!='fastboot':raise ValueError('CLI target not unique')
    serial=parts[0][0]
    if serial.upper()!=identity_serial(row).upper():raise ValueError('CLI serial does not match current Windows Fastboot instance')
    return serial
def args(command,serial):
    if command!=COMMAND or not serial or serial.startswith('-') or not re.fullmatch(r'[A-Za-z0-9._-]+',serial):raise ValueError('Command/target rejected')
    return ['-s',serial,'flashing','get_unlock_ability']
def parse_reply(rc,text):
    values=re.findall(r'(?m)^\s*(?:\(bootloader\)\s*)?unlock_ability\s*=\s*(-?[0-9]+)\s*$',text)
    if rc!=0 or re.search(r'\bFAIL(?:ED)?\b|error|timeout',text,re.I) or len(values)!=1 or not re.search(r'\bOKAY\b',text):raise ValueError('Invalid/failed/incomplete Fastboot response')
    signed=int(values[0])
    if not -(2**31)<=signed<=2**31-1:raise ValueError('Outside LK signed %d word representation')
    word=signed&0xffffffff
    return {'printed_signed':signed,'word_uint32':word,'allowed':word!=0,'state':'LK_PERMISSION_NONZERO_NOT_UNLOCKED' if word else 'LK_ZERO_CONFLICT_WITH_PRIOR_ANDROID_STOP','digest':'UNKNOWN','unlocked':'NOT_QUERIED'}
def reserve(path,kind):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as f:json.dump({'kind':kind,'no_retry':True},f);f.flush();os.fsync(f.fileno())
