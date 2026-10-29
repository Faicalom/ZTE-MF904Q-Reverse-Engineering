# SPDX-License-Identifier: GPL-3.0-only
# mtkclient-derived/source-informed DA research component; see THIRD_PARTY_NOTICES.md.
# Upstream rights retained: B.Kerler and original mtkclient contributors.
# Project changes: bounded transport, exact-target guards, verification and evidence capture.
# Publication changes 2026-10-25: notices, personal-path/identity redaction; no live behavior validation.
# Distributed without warranty; full license at LICENSES/GPL-3.0-only.txt in repository root.
"""Offline DA metadata/region validation. No USB/serial imports or blob execution."""
import hashlib,json,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LOADERS=ROOT.parent/'MF904Q_Original_Firmware_Backup/tools/mtkclient/mtkclient/Loader'
REVISION='cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3'

def parse_entry(data,offset,stride=0xdc):
    if offset<0 or offset+stride>len(data):raise ValueError('Truncated entry')
    raw=data[offset:offset+stride]
    magic,code,sub,hw,sw,res,page,res2,index,count=struct.unpack_from('<10H',raw)
    if magic!=0xdada:raise ValueError('DA magic mismatch')
    if count<3 or count>(stride-20)//20:raise ValueError('Invalid region count')
    regions=[]
    for i in range(count):
        start,size,address,startoffset,sig=struct.unpack_from('<5I',raw,20+i*20)
        if start+size>len(data) or sig>size:raise ValueError('Region or signature outside bounds')
        blob=data[start:start+size]
        regions.append({'index':i,'file_offset':start,'length':size,'load_address':f'0x{address:08X}',
                        'start_offset':startoffset,'signature_length':sig,'sha256':hashlib.sha256(blob).hexdigest()})
    return {'da_code':code,'subcode':sub,'hw_version':hw,'sw_version':sw,'pagesize_field':page,
            'region_index':index,'regions':regions}

def eligibility(evidence):
    # Numeric DA selection is necessary but not board/DRAM validation.
    required=('soc_family_supported','numeric_version_eligible','board_memory_evidence',
              'dram_initialization_verified','unmodified_da_verified','bounded_read_path_audited')
    missing=[key for key in required if evidence.get(key) is not True]
    return {'upload_allowed':not missing,'missing':missing}

def audit():
    identity=json.loads((ROOT/'logs/20261009_064239_833208/result.json').read_text())
    rows=[]
    for name in ('MTK_DA_V5.bin','MTK_AllInOne_DA_mt6590.bin'):
        path=LOADERS/name;data=path.read_bytes();count=struct.unpack_from('<I',data,0x68)[0]
        if count>10000:raise ValueError('DA count out of bounds')
        for index in range(count):
            off=0x6c+index*0xdc
            if struct.unpack_from('<H',data,off+2)[0]!=0x6735:continue
            entry=parse_entry(data,off)
            entry.update(file=name,file_sha256=hashlib.sha256(data).hexdigest(),entry=index,
                         source='https://github.com/bkerler/mtkclient',revision=REVISION)
            flags={'soc_family_supported':True,
                   'numeric_version_eligible':entry['hw_version']<=int(identity['hw_version_fc'],16) and entry['sw_version']<=int(identity['sw_version'],16),
                   'board_memory_evidence':False,'dram_initialization_verified':False,
                   'unmodified_da_verified':True,'bounded_read_path_audited':False}
            entry.update(target_hw_subcode=identity['hw_subcode'],subcode_equal=entry['subcode']==int(identity['hw_subcode'],16),
                         evidence=flags,gate=eligibility(flags))
            rows.append(entry)
    report={'kind':'OFFLINE_ONLY_NO_DEVICE_ACCESS','candidates':rows,
            'stage1_equal':rows[0]['regions'][1]['sha256']==rows[1]['regions'][1]['sha256'],
            'stage2_equal':rows[0]['regions'][2]['sha256']==rows[1]['regions'][2]['sha256'],
            'firmware_files_read_from_target':0,'da_upload_attempted':False}
    out=ROOT/'storage_gate';out.mkdir(exist_ok=True)
    (out/'legacy-candidate-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':audit()
