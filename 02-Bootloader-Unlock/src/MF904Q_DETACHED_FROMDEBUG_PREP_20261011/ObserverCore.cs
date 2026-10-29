using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Win32;

namespace MF904QMonitor {
public static class Data {
    public static string Hash(string s) { using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(Encoding.UTF8.GetBytes(s))).Replace("-", "").ToLowerInvariant(); }
    public static Dictionary<string,object> Obj(params object[] p) { var d=new Dictionary<string,object>(); for(int i=0;i<p.Length;i+=2)d[(string)p[i]]=p[i+1]; return d; }
    public static string Json(object x) { return new JavaScriptSerializer { MaxJsonLength=4000000 }.Serialize(x); }
    public static string Now() { return DateTimeOffset.UtcNow.ToOffset(TimeSpan.FromHours(1)).ToString("o"); }
    public static void Atomic(string path, string text) { string temp=path+".tmp"; File.WriteAllText(temp,text,new UTF8Encoding(false)); if(File.Exists(path)) File.Replace(temp,path,null); else File.Move(temp,path); }
}
public sealed class Journal : IDisposable {
    readonly object gate=new object(); readonly FileStream stream; readonly Stopwatch clock=Stopwatch.StartNew(); long seq; bool closed;
    public readonly string Folder; public event Action<string> Display;
    public Journal(string parent) { Folder=Path.Combine(parent,"sessions",DateTimeOffset.UtcNow.ToOffset(TimeSpan.FromHours(1)).ToString("yyyyMMdd_HHmmss_fff")); Directory.CreateDirectory(Folder); stream=new FileStream(Path.Combine(Folder,"events.jsonl"),FileMode.CreateNew,FileAccess.Write,FileShare.Read,4096,FileOptions.WriteThrough); }
    public void Add(string kind,object payload,string message) {
        lock(gate) { if(closed)return; var row=Data.Obj("seq",++seq,"time",Data.Now(),"elapsed_ms",Math.Round(clock.Elapsed.TotalMilliseconds,3),"event",kind,"data",payload); var bytes=Encoding.UTF8.GetBytes(Data.Json(row)+"\n"); stream.Write(bytes,0,bytes.Length);stream.Flush(true); }
        var action=Display; if(action!=null && message!=null)action(DateTimeOffset.UtcNow.ToOffset(TimeSpan.FromHours(1)).ToString("HH:mm:ss.fff")+"  "+message);
    }
    public void Dispose() { lock(gate) { if(closed)return;closed=true;stream.Dispose(); } }
}
public sealed class UsbRow {
    public string token,vid,pid,name,service,driver_inf,driver_provider,driver_version,device_class,location_hash;
    public string[] compatible,interface_guids,serial_hashes;
    public uint problem_code,status_flags; public bool present,adb_candidate,adb_guid_registered;
}
public static class Usb {
    [StructLayout(LayoutKind.Sequential)] struct Info { public uint size; public Guid guid; public uint devinst; public IntPtr reserved; }
    [DllImport("setupapi.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr SetupDiGetClassDevsW(IntPtr g,string e,IntPtr w,uint flags);
    [DllImport("setupapi.dll",SetLastError=true)] static extern bool SetupDiEnumDeviceInfo(IntPtr h,uint i,ref Info info);
    [DllImport("setupapi.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool SetupDiGetDeviceInstanceIdW(IntPtr h,ref Info info,StringBuilder s,int n,out int needed);
    [DllImport("setupapi.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool SetupDiGetDeviceRegistryPropertyW(IntPtr h,ref Info info,uint key,out uint type,byte[] b,uint n,out uint needed);
    [DllImport("setupapi.dll")] static extern bool SetupDiDestroyDeviceInfoList(IntPtr h);
    [DllImport("cfgmgr32.dll")] static extern uint CM_Get_Parent(out uint p,uint d,uint flags);
    [DllImport("cfgmgr32.dll",CharSet=CharSet.Unicode)] static extern uint CM_Get_Device_IDW(uint d,StringBuilder s,int n,uint flags);
    [DllImport("cfgmgr32.dll")] static extern uint CM_Get_DevNode_Status(out uint status,out uint problem,uint d,uint flags);
    public const string AdbGuid="{F72FE0D4-CBCB-407D-8814-9ED673D0DD6B}";
    static string Prop(IntPtr h,ref Info i,uint key) { var b=new byte[8192];uint t,n;if(!SetupDiGetDeviceRegistryPropertyW(h,ref i,key,out t,b,(uint)b.Length,out n))return "";return Encoding.Unicode.GetString(b,0,(int)Math.Min(n,(uint)b.Length)).TrimEnd('\0'); }
    static string Reg(RegistryKey k,string n) { return k==null ? "" : Convert.ToString(k.GetValue(n,"")); }
    public static List<UsbRow> Snapshot(bool presentOnly) {
        var rows=new List<UsbRow>();var h=SetupDiGetClassDevsW(IntPtr.Zero,"USB",IntPtr.Zero,presentOnly ? 6u:4u);if(h==new IntPtr(-1))throw new IOException("SetupAPI enumeration failed: "+Marshal.GetLastWin32Error());
        try { for(uint index=0;;index++) {
            var i=new Info { size=(uint)Marshal.SizeOf(typeof(Info)) }; if(!SetupDiEnumDeviceInfo(h,index,ref i)) { if(Marshal.GetLastWin32Error()!=259)throw new IOException("SetupAPI incomplete enumeration"); break; }
            var b=new StringBuilder(2048);int n;if(!SetupDiGetDeviceInstanceIdW(h,ref i,b,b.Capacity,out n))continue;string id=b.ToString();var m=Regex.Match(id,@"^USB\\VID_([0-9A-F]{4})&PID_([0-9A-F]{4})",RegexOptions.IgnoreCase);if(!m.Success)continue;
            string vid=m.Groups[1].Value.ToUpperInvariant(),pid=m.Groups[2].Value.ToUpperInvariant();
            // All USB vendors are inspected to reject serial collisions with other devices.
            var serials=new HashSet<string>();uint node=i.devinst;
            for(int j=0;j<6;j++) { var s=new StringBuilder(2048);if(CM_Get_Device_IDW(node,s,s.Capacity,0)!=0)break;var sm=Regex.Match(s.ToString(),@"^USB\\VID_[0-9A-F]{4}&PID_[0-9A-F]{4}\\([^\\&]+)$",RegexOptions.IgnoreCase);if(sm.Success)serials.Add(Data.Hash(sm.Groups[1].Value));uint parent;if(CM_Get_Parent(out parent,node,0)!=0)break;node=parent; }
            // The devnode itself can retain a serial while disconnected.
            var own=Regex.Match(id,@"^USB\\VID_[0-9A-F]{4}&PID_[0-9A-F]{4}\\([^\\&]+)$",RegexOptions.IgnoreCase);if(own.Success)serials.Add(Data.Hash(own.Groups[1].Value));
            uint status,problem;uint statusResult=CM_Get_DevNode_Status(out status,out problem,i.devinst,0);
            var r=new UsbRow { token=Data.Hash(id),vid=vid,pid=pid,name=Prop(h,ref i,12),compatible=Prop(h,ref i,2).Split(new[]{'\0'},StringSplitOptions.RemoveEmptyEntries),service=Prop(h,ref i,4),device_class=Prop(h,ref i,7),serial_hashes=serials.ToArray(),present=statusResult==0 && (status&2)!=0,status_flags=status,problem_code=problem,location_hash=Data.Hash(Prop(h,ref i,13)) };
            if(r.name.Length==0)r.name=Prop(h,ref i,0);r.adb_candidate=r.compatible.Any(c=>c.IndexOf("Class_FF&SubClass_42&Prot_01",StringComparison.OrdinalIgnoreCase)>=0);
            r.interface_guids=new string[0];
            using(var dp=Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Enum\"+id+@"\Device Parameters")) { object v=dp==null?null:dp.GetValue("DeviceInterfaceGUIDs"); if(v is string[])r.interface_guids=(string[])v;else if(v is string)r.interface_guids=new[]{(string)v}; }
            r.adb_guid_registered=r.interface_guids.Any(g=>g.Equals(AdbGuid,StringComparison.OrdinalIgnoreCase));
            using(var dk=Registry.LocalMachine.OpenSubKey(@"SYSTEM\CurrentControlSet\Control\Class\"+Prop(h,ref i,9))) { r.driver_inf=Reg(dk,"InfPath");r.driver_provider=Reg(dk,"ProviderName");r.driver_version=Reg(dk,"DriverVersion"); }
            rows.Add(r);
        }} finally {SetupDiDestroyDeviceInfoList(h);}return rows;
    }
}
public sealed class AdbRow {
    public string serial_sha256,state,product,model,device,transport_id,usb_path_hash,identity;
}
public static class Adb {
    public static AdbRow Copy(AdbRow r) {return new AdbRow {serial_sha256=r.serial_sha256,state=r.state,product=r.product,model=r.model,device=r.device,transport_id=r.transport_id,usb_path_hash=r.usb_path_hash,identity=r.identity};}
    public static TcpClient Open(int port,string service) {
        if(service!="host:track-devices-l" && service!="host:version" && service!="host:server-status")throw new InvalidOperationException("Service outside observer allowlist");
        var c=new TcpClient();try {var pending=c.BeginConnect(IPAddress.Loopback,port,null,null); if(!pending.AsyncWaitHandle.WaitOne(2500))throw new IOException("Existing ADB server unavailable");c.EndConnect(pending);pending.AsyncWaitHandle.Close();c.ReceiveTimeout=3000;c.SendTimeout=3000;var s=c.GetStream();var q=Encoding.UTF8.GetBytes(service);var frame=Encoding.ASCII.GetBytes(q.Length.ToString("x4"));s.Write(frame,0,4);s.Write(q,0,q.Length);var status=Encoding.ASCII.GetString(Exact(s,4));if(status=="FAIL") {var reason=Encoding.UTF8.GetString(Frame(s));throw new IOException("ADB host service rejected: "+reason);}if(status!="OKAY")throw new IOException("Unexpected ADB host response");return c;}catch {c.Close();throw;}
    }
    public static byte[] Exact(Stream s,int n) { if(n<0 || n>1024*1024)throw new IOException("ADB frame length rejected");var b=new byte[n];int p=0;while(p<n) {int k=s.Read(b,p,n-p);if(k==0)throw new EndOfStreamException("ADB tracking connection closed");p+=k;}return b; }
    public static byte[] Frame(Stream s) { string h=Encoding.ASCII.GetString(Exact(s,4));int n;if(!int.TryParse(h,NumberStyles.HexNumber,CultureInfo.InvariantCulture,out n))throw new IOException("Invalid ADB frame header");return Exact(s,n); }
    public static List<AdbRow> Parse(string payload) {
        var rows=new List<AdbRow>();foreach(string line in payload.Split('\n')) { var m=Regex.Match(line.Trim(),@"^(\S+)\s+(\S+)(?:\s+(.*))?$");if(!m.Success)continue;string serial=m.Groups[1].Value,extra=m.Groups[3].Value;var r=new AdbRow { serial_sha256=Data.Hash(serial),state=m.Groups[2].Value,identity="UNRESOLVED",product="",model="",device="",transport_id="",usb_path_hash="" };foreach(Match field in Regex.Matches(extra,@"(\S+?):(\S+)")) {string k=field.Groups[1].Value,v=field.Groups[2].Value;if(k=="product")r.product=v;else if(k=="model")r.model=v;else if(k=="device")r.device=v;else if(k=="transport_id")r.transport_id=v;else if(k=="usb")r.usb_path_hash=Data.Hash(v);}rows.Add(r); }return rows;
    }
    public static string Identity(AdbRow a,List<UsbRow> usb) {
        if(a.product.StartsWith("serenity",StringComparison.OrdinalIgnoreCase)||a.model=="25028PC03G"||a.device=="serenity")return "POCO_C71_EXCLUDED";
        var matches=usb.Where(u=>u.adb_candidate && u.serial_hashes.Contains(a.serial_sha256)).ToList();
        bool mtk=matches.Any(u=>u.vid=="0E8D"),other=matches.Any(u=>u.vid!="0E8D");if(mtk && other)return "AMBIGUOUS_USB_SERIAL";
        if(mtk) { if(a.product.IndexOf("mf904q",StringComparison.OrdinalIgnoreCase)>=0 || a.model.IndexOf("mf904q",StringComparison.OrdinalIgnoreCase)>=0 || a.device.IndexOf("mf904q",StringComparison.OrdinalIgnoreCase)>=0)return "MODEM_USB_AND_PRODUCT_MATCH"; return "MEDIATEK_USB_SERIAL_MATCH_PRODUCT_PENDING"; }
        return "UNRESOLVED";
    }
    public static Dictionary<string,object> ServerStatus(byte[] b) {
        var d=new Dictionary<string,object>();int p=0;while(p<b.Length) {ulong key=Var(b,ref p);int field=(int)(key>>3),wire=(int)(key&7);if(wire==0) {ulong v=Var(b,ref p);if(field==1)d["usb_backend"]=v==1?"NATIVE":v==2?"LIBUSB":"UNKNOWN";if(field==2)d["usb_backend_forced"]=v!=0; }else if(wire==2) {int n=checked((int)Var(b,ref p));if(n<0||n>b.Length-p)throw new IOException("Invalid status field");if(field==5)d["version"]=Encoding.UTF8.GetString(b,p,n);if(field==6)d["build"]=Encoding.UTF8.GetString(b,p,n);if(field==7)d["server_executable_hash"]=Data.Hash(Encoding.UTF8.GetString(b,p,n));p+=n;}else if(wire==1)p+=8;else if(wire==5)p+=4;else throw new IOException("Unsupported status wire type"); }return d;
    }
    static ulong Var(byte[] b,ref int p) {ulong n=0;for(int bit=0;bit<64;bit+=7) {if(p>=b.Length)throw new IOException("Truncated status");byte v=b[p++];n|=(ulong)(v&127)<<bit;if((v&128)==0)return n;}throw new IOException("Invalid status varint");}
}

}
