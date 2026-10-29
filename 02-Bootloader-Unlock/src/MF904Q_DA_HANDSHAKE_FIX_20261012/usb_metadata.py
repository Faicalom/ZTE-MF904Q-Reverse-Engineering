"""Windows present-devnode properties only. Never opens a USB endpoint."""
import ctypes as C
from ctypes import wintypes as W
import re
class Info(C.Structure):
    _fields_=[('size',W.DWORD),('guid',C.c_ubyte*16),('dev',W.DWORD),('reserved',C.c_size_t)]
dll=C.WinDLL('setupapi.dll')
dll.SetupDiGetClassDevsW.argtypes=[C.c_void_p,W.LPCWSTR,W.HWND,W.DWORD]
dll.SetupDiGetClassDevsW.restype=W.HANDLE
dll.SetupDiEnumDeviceInfo.argtypes=[W.HANDLE,W.DWORD,C.POINTER(Info)]
dll.SetupDiGetDeviceInstanceIdW.argtypes=[W.HANDLE,C.POINTER(Info),W.LPWSTR,W.DWORD,C.POINTER(W.DWORD)]
dll.SetupDiGetDeviceRegistryPropertyW.argtypes=[W.HANDLE,C.POINTER(Info),W.DWORD,C.POINTER(W.DWORD),C.c_void_p,W.DWORD,C.POINTER(W.DWORD)]
dll.SetupDiDestroyDeviceInfoList.argtypes=[W.HANDLE]
def canonical(path): return re.sub(r'#USBMI\(\d+\)$','',path.upper())
def snapshot():
    h=dll.SetupDiGetClassDevsW(None,'USB',None,6)
    if h==C.c_void_p(-1).value: raise C.WinError()
    rows=[]
    def prop(item,n):
        b=C.create_string_buffer(8192);typ=W.DWORD();size=W.DWORD()
        if not dll.SetupDiGetDeviceRegistryPropertyW(h,C.byref(item),n,C.byref(typ),b,len(b),C.byref(size)): return []
        return [s for s in b.raw[:size.value].decode('utf-16-le',errors='replace').strip('\0').split('\0') if s]
    try:
        index=0
        while True:
            item=Info();item.size=C.sizeof(item)
            if not dll.SetupDiEnumDeviceInfo(h,index,C.byref(item)):break
            index+=1;buf=C.create_unicode_buffer(1024);needed=W.DWORD()
            if not dll.SetupDiGetDeviceInstanceIdW(h,C.byref(item),buf,1024,C.byref(needed)):continue
            iid=buf.value.upper()
            if not iid.startswith('USB\\VID_'):continue
            compat=prop(item,2)
            rows.append({'instance':iid,'usb_id':iid.split('\\')[1],
                         'paths':[canonical(s) for s in prop(item,35)],
                         'compatible':compat,'name':prop(item,12) or prop(item,0),
                         'service':prop(item,4),
                         'fastboot':any('CLASS_FF&SUBCLASS_42&PROT_03' in c.upper() for c in compat)})
    finally:dll.SetupDiDestroyDeviceInfoList(h)
    return rows
