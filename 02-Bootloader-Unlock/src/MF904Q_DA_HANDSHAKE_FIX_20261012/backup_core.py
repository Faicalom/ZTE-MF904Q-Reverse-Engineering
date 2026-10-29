# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Read-only Legacy eMMC ranges, checked GPT and disk-verified checkpoints."""
import hashlib,json,math,os,struct,zlib
from pathlib import Path
SECTOR=512;CHUNK=1024*1024
PUBLIC={'lk','boot','recovery','logo','tee1','tee2','system'}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*CHUNK),b''):h.update(block)
    return h.hexdigest()

def atomic_json(path,value):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('w',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(temp,path)

def exact(receive,n):
    data=receive(n)
    if len(data)!=n:raise TimeoutError(f'Partial read {len(data)}/{n}')
    return data

def ack(receive,phase):
    data=exact(receive,1)
    if data!=b'\x5a':raise RuntimeError(f'{phase}: expected ACK5A, got {data.hex()}; stop')

def read_range(send,receive,region,offset,length,region_size):
    if region not in (1,2,8) or offset<0 or length<=0 or length>CHUNK:
        raise ValueError('Range/region outside bounded read policy; RPMB is prohibited')
    if offset%SECTOR or length%SECTOR or offset+length>region_size:
        raise ValueError('Unaligned/out-of-bounds range')
    send(b'\x72');ack(receive,'USB status');speed=exact(receive,1)[0]
    if speed not in (0,1,2):raise RuntimeError('Unknown USB speed; do not reconfigure')
    send(b'\x60');ack(receive,'partition command');send(bytes([region]));ack(receive,'partition selection')
    for data in (b'\xd6',b'\x0c',b'\x02',struct.pack('>Q',offset),
                 struct.pack('>Q',length),struct.pack('>I',0x100000)):send(data)
    ack(receive,'READ_CMD');data=exact(receive,length)
    reported=int.from_bytes(exact(receive,2),'big');actual=sum(data)&0xffff
    if reported!=actual:raise RuntimeError(f'Checksum mismatch at {offset}: {reported:04X}/{actual:04X}')
    send(b'\x5a')
    return data,reported

def gpt_header(raw,expected_lba,user_size):
    if len(raw)!=512 or raw[:8]!=b'EFI PART':raise ValueError('Missing GPT header')
    size=struct.unpack_from('<I',raw,12)[0]
    if not 92<=size<=512:raise ValueError('Invalid GPT header size')
    buf=bytearray(raw[:size]);crc=struct.unpack_from('<I',buf,16)[0];buf[16:20]=bytes(4)
    if zlib.crc32(buf)&0xffffffff!=crc:raise ValueError('GPT header CRC mismatch')
    current,backup,first,last=struct.unpack_from('<4Q',raw,24)
    table_lba,count,entry_size,table_crc=struct.unpack_from('<QIII',raw,72)
    sectors=user_size//SECTOR
    if current!=expected_lba or backup>=sectors or first>last or last>=sectors:
        raise ValueError('GPT LBAs invalid')
    if not 1<=count<=4096 or entry_size<128 or entry_size%8:
        raise ValueError('GPT entry layout invalid')
    length=count*entry_size;padded=math.ceil(length/SECTOR)*SECTOR
    if padded>CHUNK or table_lba<2 or table_lba*SECTOR+padded>user_size:
        raise ValueError('GPT table range invalid')
    return dict(current=current,backup=backup,first=first,last=last,table_lba=table_lba,
                count=count,entry_size=entry_size,length=length,padded=padded,table_crc=table_crc,
                disk_guid=raw[56:72].hex())

def entries(data,header):
    table=data[:header['length']]
    if len(table)!=header['length'] or zlib.crc32(table)&0xffffffff!=header['table_crc']:
        raise ValueError('GPT entries CRC mismatch')
    parts=[];names=set()
    for i in range(header['count']):
        e=table[i*header['entry_size']:(i+1)*header['entry_size']]
        if e[:16]==bytes(16):continue
        a,b=struct.unpack_from('<QQ',e,32);name=e[56:128].decode('utf-16-le',errors='strict').split('\0')[0]
        if not name or name in names or any(c in name for c in '/\\:'):
            raise ValueError('Invalid/duplicate partition name')
        if a<header['first'] or b<a or b>header['last']:raise ValueError('Partition bounds invalid')
        names.add(name);parts.append(dict(name=name,first_lba=a,last_lba=b,offset=a*SECTOR,size=(b-a+1)*SECTOR))
    ordered=sorted(parts,key=lambda p:p['first_lba'])
    if any(a['last_lba']>=b['first_lba'] for a,b in zip(ordered,ordered[1:])):
        raise ValueError('Overlapping partitions')
    return parts

class Image:
    """One range; checksum first, fsync, then atomic checkpoint. No retry."""
    def __init__(self,path,region,offset,size,binding):
        self.path=Path(path);self.partial=Path(str(path)+'.partial');self.journal=Path(str(path)+'.checkpoint.json')
        self.identity=dict(region=region,offset=offset,expected_size=size,binding=binding)
        self.state={**self.identity,'blocks':[],'complete':False}
    def verify_disk(self):
        if self.journal.exists():
            self.state=json.loads(self.journal.read_text())
            if any(self.state.get(k)!=v for k,v in self.identity.items()):raise ValueError('Checkpoint identity mismatch')
        if self.path.exists():
            if not self.state.get('complete') or self.path.stat().st_size!=self.identity['expected_size'] or sha(self.path)!=self.state.get('sha256'):
                raise ValueError('Completed image has no valid checkpoint/hash')
            return self.identity['expected_size']
        if self.state.get('complete') and self.partial.exists():
            if self.partial.stat().st_size!=self.identity['expected_size'] or sha(self.partial)!=self.state['sha256']:
                raise ValueError('Completed partial hash invalid')
            os.replace(self.partial,self.path);return self.identity['expected_size']
        expected=0
        if self.state['blocks'] and not self.partial.exists():raise ValueError('Committed partial image missing')
        if self.partial.exists():
            with self.partial.open('rb+') as f:
                for block in self.state['blocks']:
                    if block['offset']!=expected or not 0<block['length']<=CHUNK:
                        raise ValueError('Checkpoint block layout invalid')
                    data=f.read(block['length'])
                    if len(data)!=block['length'] or hashlib.sha256(data).hexdigest()!=block['sha256']:
                        raise ValueError('Committed block hash invalid; no device retry')
                    expected+=block['length']
                if expected>self.identity['expected_size']:raise ValueError('Checkpoint beyond image size')
                # Discard only uncommitted tail after verifying every committed block.
                f.truncate(expected)
        return expected
    def run(self,read,region_size,progress=lambda *a:None):
        position=self.verify_disk()
        if position==self.identity['expected_size'] and self.path.exists():return self.state
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.partial.open('ab') as f:
            while position<self.identity['expected_size']:
                length=min(CHUNK,self.identity['expected_size']-position)
                data,checksum=read(self.identity['region'],self.identity['offset']+position,length,region_size)
                if len(data)!=length:raise TimeoutError('Reader returned a partial chunk')
                f.write(data);f.flush();os.fsync(f.fileno())
                self.state['blocks'].append(dict(offset=position,length=length,sha256=hashlib.sha256(data).hexdigest(),checksum=f'0x{checksum:04X}'))
                position+=length;atomic_json(self.journal,self.state);progress(position,self.identity['expected_size'])
        self.state.update(complete=True,sha256=sha(self.partial),actual_size=self.partial.stat().st_size,
                          independent_verification='All committed chunk hashes and size verified on disk')
        if self.state['actual_size']!=self.identity['expected_size']:raise ValueError('Image size mismatch')
        atomic_json(self.journal,self.state);os.replace(self.partial,self.path)
        return self.state
