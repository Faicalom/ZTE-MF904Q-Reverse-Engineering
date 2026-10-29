"""Extract bounded FILE_INFO images/EMI from copied Boot1 only; no device I/O."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def main():
    raw=(ROOT/'03_Boot_Regions/boot1.bin').read_bytes();magic=b'MMM\x01\x38\x00\x00\x00';start=0;results=[]
    while True:
        offset=raw.find(magic,start)
        if offset<0:break
        start=offset+len(magic)
        if raw[offset+8:offset+17]!=b'FILE_INFO':continue
        length=struct.unpack_from('<I',raw,offset+0x20)[0];sig=struct.unpack_from('<I',raw,offset+0x2c)[0]
        if not 56<=length<=len(raw)-offset or sig>length:continue
        image=raw[offset:offset+length];name=f'boot1_FILE_INFO_{offset:08x}.bin'
        (ROOT/'03_Boot_Regions'/name).write_bytes(image)
        result=dict(offset=offset,length=length,signature_length=sig,sha256=hashlib.sha256(image).hexdigest(),file=name,
                    source='Exact Boot1 slice selected by MediaTek FILE_INFO header length; signature not verified')
        payload=image[:length-sig] if sig else image
        if len(payload)>=4:
            size=struct.unpack_from('<I',payload,len(payload)-4)[0]
            if size==0 and len(payload)>0x804:
                payload=payload[:-0x800];size=struct.unpack_from('<I',payload,len(payload)-4)[0]
            if 0<size<=len(payload)-4:
                config=payload[-size-4:-4];bldr=b'MTK_BLOADER_INFO_v';index=config.find(bldr);binpos=config.find(b'MTK_BIN')
                if index>=0 and binpos>=0:
                    try:version=int(config[index+len(bldr):index+len(bldr)+2].rstrip(b'\0'))
                    except ValueError:version=None
                    if version is not None:
                        emi=config[binpos+12:];ename=f'boot1_EMI_{offset:08x}.bin'
                        (ROOT/'03_Boot_Regions'/ename).write_bytes(emi)
                        result.update(emi_file=ename,emi_version=version,emi_size=len(emi),emi_sha256=hashlib.sha256(emi).hexdigest(),
                                      emi_status='Offline extraction following pinned daconfig.m_extract_emi; not loaded/tested')
        results.append(result)
    (ROOT/'08_Recovery_Documentation/preloader_offline_inspection.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
