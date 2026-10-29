"""Present USB devnode metadata only; never opens USB/COM or reads serial strings."""
import ctypes as C
from ctypes import wintypes as W
class Info(C.Structure):
    _fields_=[('size',W.DWORD),('guid',C.c_ubyte*16),('dev',W.DWORD),('reserved',C.c_size_t)]
dll=C.WinDLL('setupapi.dll')
dll.SetupDiGetClassDevsW.argtypes=[C.c_void_p,W.LPCWSTR,W.HWND,W.DWORD]
dll.SetupDiGetClassDevsW.restype=W.HANDLE
dll.SetupDiEnumDeviceInfo.argtypes=[W.HANDLE,W.DWORD,C.POINTER(Info)]
dll.SetupDiEnumDeviceInfo.restype=W.BOOL
dll.SetupDiGetDeviceInstanceIdW.argtypes=[W.HANDLE,C.POINTER(Info),W.LPWSTR,W.DWORD,C.POINTER(W.DWORD)]
dll.SetupDiGetDeviceInstanceIdW.restype=W.BOOL
dll.SetupDiDestroyDeviceInfoList.argtypes=[W.HANDLE]
def present_ids():
    h=dll.SetupDiGetClassDevsW(None,'USB',None,6) # PRESENT | ALLCLASSES
    if h==C.c_void_p(-1).value:raise C.WinError()
    matches=set();index=0
    try:
        while True:
            item=Info();item.size=C.sizeof(item)
            if not dll.SetupDiEnumDeviceInfo(h,index,C.byref(item)):break
            index+=1;buf=C.create_unicode_buffer(1024);needed=W.DWORD()
            if not dll.SetupDiGetDeviceInstanceIdW(h,C.byref(item),buf,1024,C.byref(needed)):continue
            if buf.value.upper().startswith('USB\\VID_0E8D'):
                matches.add(buf.value.split('\\')[1].upper())
    finally:dll.SetupDiDestroyDeviceInfoList(h)
    return sorted(matches)
def preloader_present():return any('VID_0E8D&PID_2000' in item for item in present_ids())
if __name__=='__main__':print('Present MediaTek USB identities:',present_ids())
