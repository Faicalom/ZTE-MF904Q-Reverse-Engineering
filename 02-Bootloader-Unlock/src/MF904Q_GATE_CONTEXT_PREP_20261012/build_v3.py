import pathlib,subprocess,json,hashlib,struct
P=pathlib.Path(__file__).resolve().parent
LLVM=pathlib.Path('C:/Users/YOUR_WINDOWS_USER/AppData/Local/Android/Sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/windows-x86_64/bin')
ORIGINAL=P.parent/'MF904Q_STOCK_FIRMWARE_BACKUP/04_Firmware_Partitions/lk.bin'
sha=lambda d:hashlib.sha256(d).hexdigest()
def build():
 d=ORIGINAL.read_bytes();assert sha(d)=='07ba5f67df9ff0edfcae92ff0b49d874532b1f3cb6083d526f515603338ba596'
 subprocess.run([str(LLVM/'clang.exe'),'--target=armv7a-none-eabi','-mthumb','-nostdlib','-Wl,-T,'+str(P/'probe_v3.ld'),'-Wl,--entry=probe_v3',str(P/'probe_v3.S'),'-o',str(P/'probe_v3.elf')],check=True)
 syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output([str(LLVM/'llvm-nm.exe'),'-n',str(P/'probe_v3.elf')],text=True).splitlines() if len(x.split())==3}
 image=bytearray(d); patches=[]
 def patch(off,data,name):
  assert off+len(data)<=len(d)
  image[off:off+len(data)]=data;patches.append(dict(name=name,start=off,length=len(data),old_hex=d[off:off+len(data)].hex(),new_sha256=sha(data)))
 for name,off in [('diag',0x1c3dc),('body',0x1c654),('hook_erase',0x1c552),('hook_crypto1',0x2337a),('hook_write1',0x233a6),('hook_crypto2',0x233da),('hook_config',0x22592),('hook_raw',0x2922c),('hook_gate',0x23406),('hook_constructor',0x2340e),('hook_write2',0x23436)]:
  f=P/(name+'.bin');subprocess.run([str(LLVM/'llvm-objcopy.exe'),'-O','binary','--only-section=.'+name,str(P/'probe_v3.elf'),str(f)],check=True);patch(off,f.read_bytes(),name)
 # Single-poll UART: low THRE returns via original mov r0,#0/bx lr, no MMIO write.
 assert d[0x1c10:0x1c12]==bytes.fromhex('fbd5');patch(0x1c10,bytes.fromhex('0ad5'),'UART_BPL_RETURN')
 # Common epilogue reached with R0 equal to ctor/decrypt result or failed write; R5 was masking write error.
 for off in [0x233aa,0x2343a]:
  assert d[off:off+2]==bytes.fromhex('0028');patch(off,bytes.fromhex('0500'),'SAVE_WRITE_R0_TO_R5_AND_SET_Z')
 assert image[0x233ae:0x233b0]==d[0x233ae:0x233b0]
 for off,expected in [(0x485ac,0x41e1c249),(0x48778,0x41e1c289),(0x4865c,0x41e1c455)]:
  assert struct.unpack_from('<I',d,off)[0]==expected;patch(off,struct.pack('<I',0x41dffe00+syms['deny_legacy']+1),'DISABLE_REPURPOSED_CALLBACK')
 assert len(image)==524288 and image[:0x200]==d[:0x200]
 # Original Unlock intact except instrumentation call, original key scanner and FRP reader unchanged.
 assert image[0x1c504:0x1c552]==d[0x1c504:0x1c552] and image[0x1c556:0x1c61c]==d[0x1c556:0x1c61c]
 assert image[0x45dc:0x4640]==d[0x45dc:0x4640]
 (P/'lk_V3_FINAL.bin').write_bytes(image)
 m=dict(candidate_sha256=sha(image),original_sha256=sha(d),bytes=len(image),changed_bytes=sum(a!=b for a,b in zip(d,image)),patches=patches,symbols=syms,live_validated=False,unlock_requires_separate_final_confirmation=True)
 (P/'BUILD_MANIFEST.json').write_text(json.dumps(m,indent=2));print(json.dumps({k:m[k] for k in ['candidate_sha256','changed_bytes','bytes']}))
if __name__=='__main__':build()
