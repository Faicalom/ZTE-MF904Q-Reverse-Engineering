"""Independent local size/hash/GPT/overlap verification; never opens a device."""
import hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def hash_file(path,offset=0,length=None):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        f.seek(offset)
        while length is None or length:
            data=f.read(4*1024*1024 if length is None else min(length,4*1024*1024))
            if not data:
                if length:raise ValueError('Truncated local image')
                break
            h.update(data)
            if length is not None:length-=len(data)
    return h.hexdigest()

def check_gpt(header,table):
    assert header[:8]==b'EFI PART';size=struct.unpack_from('<I',header,12)[0]
    copy=bytearray(header[:size]);crc=struct.unpack_from('<I',copy,16)[0];copy[16:20]=bytes(4)
    assert zlib.crc32(copy)&0xffffffff==crc
    count,entry_size,table_crc=struct.unpack_from('<III',header,80)
    assert zlib.crc32(table[:count*entry_size])&0xffffffff==table_crc
    return count,entry_size

def verify():
    manifest=json.loads((ROOT/'manifest.json').read_text());failures=[];count=0
    for row in manifest['files']:
        if not row['complete']:failures.append(row['file']+': incomplete');continue
        path=ROOT/row['file']
        if not path.exists() or path.stat().st_size!=row['expected_size'] or hash_file(path)!=row['sha256']:
            failures.append(row['file']+': size/hash mismatch');continue
        checkpoint=Path(str(path)+'.checkpoint.json')
        if checkpoint.exists():
            state=json.loads(checkpoint.read_text());end=0
            for block in state['blocks']:
                if block['offset']!=end or hash_file(path,end,block['length'])!=block['sha256']:
                    failures.append(row['file']+': checkpoint block mismatch');break
                end+=block['length']
            if end!=row['expected_size']:failures.append(row['file']+': checkpoint incomplete')
        row['independent_verification']='PASS: SHA256, exact size and checkpoint blocks';count+=1
    a=(ROOT/'02_GPT/primary_header.bin').read_bytes();at=(ROOT/'02_GPT/primary_entries.bin').read_bytes()
    b=(ROOT/'02_GPT/backup_header.bin').read_bytes();bt=(ROOT/'02_GPT/backup_entries_padded.bin').read_bytes()
    assert check_gpt(a,at)==check_gpt(b,bt)==(23,128)
    assert a[56:72]==b[56:72] and at==bt[:len(at)]
    boots=[]
    for number in (1,2):
        data=(ROOT/f'03_Boot_Regions/boot{number}.bin').read_bytes();markers={}
        for magic in (b'EMMC_BOOT',b'BRLYT',b'MMM\x01',b'MTK_BLOADER_INFO',b'MTK_BIN',b'FILE_INFO'):
            offsets=[];start=0
            while True:
                pos=data.find(magic,start)
                if pos<0:break
                offsets.append(pos);start=pos+1
                if len(offsets)==32:break
            if offsets:markers[magic.decode('ascii','replace')]=offsets
        boots.append(dict(region=f'Boot{number}',sha256=hash_file(ROOT/f'03_Boot_Regions/boot{number}.bin'),markers=markers))
    (ROOT/'08_Recovery_Documentation/boot_header_inspection.json').write_text(json.dumps(boots,indent=2),encoding='utf-8')
    raw=ROOT/'06_Full_User_Backup/user.bin';raw_comparisons=[]
    if raw.exists():
        for row in manifest['files']:
            if row['region']==8 and row['complete'] and row['file']!='06_Full_User_Backup/user.bin':
                matches=hash_file(raw,row['start'],row['expected_size'])==row['sha256']
                raw_comparisons.append(dict(file=row['file'],matches=matches))
                if not matches:failures.append(row['file']+': differs from full User image')
        assert raw.stat().st_size==3825205248
        with raw.open('rb') as f:
            f.seek(512);assert f.read(512)==a
            f.seek(7471103*512);assert f.read(512)==b
    result=dict(status='PASS' if not failures else 'FAIL',verified_files=count,failures=failures,
                firmware_partitions_complete=sum(r['complete'] for r in manifest['files'] if r['file'].startswith('04_Firmware_Partitions/')),
                private_partitions_complete=sum(r['complete'] for r in manifest['files'] if r['file'].startswith('05_Private_Device_Data/')),
                gpt_primary_and_backup_valid=True,gpt_entries_identical=True,boot1_boot2_identical=boots[0]['sha256']==boots[1]['sha256'],
                full_user_present=raw.exists(),full_user_partition_comparisons=raw_comparisons,rpmb_read=False,restoration_proven=False)
    manifest['independent_verification']=result
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'07_Verification/independent_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='full_user_partition_comparisons'},indent=2))
    return result

if __name__=='__main__':verify()
