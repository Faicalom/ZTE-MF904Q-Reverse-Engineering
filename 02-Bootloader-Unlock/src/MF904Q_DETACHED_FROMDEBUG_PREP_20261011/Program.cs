using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using MF904QMonitor;

namespace MF904QDetachedFromdebug {
public static class Program {
    public const string Root=@"C:/Users/YOUR_WINDOWS_USER\Documents\Codex\2026-10-08\new-chat\outputs\MF904Q_DETACHED_FROMDEBUG_PREP_20261011";
    public static string HashFile(string path) {using(var h=SHA256.Create())using(var s=File.OpenRead(path))return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();}
    public static Dictionary<string,object> Load(string path) {return new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(path));}
    public static bool Approved(Dictionary<string,object> d,string mode,string nonce,string hash) {
        return d.ContainsKey("approved") && d["approved"] is bool && (bool)d["approved"] &&
            d.ContainsKey("stage") && Convert.ToString(d["stage"])==Policy.Stage &&
            d.ContainsKey("mode") && Convert.ToString(d["mode"])==mode &&
            d.ContainsKey("nonce") && Convert.ToString(d["nonce"])==nonce &&
            d.ContainsKey("exe_sha256") && Convert.ToString(d["exe_sha256"])==hash;
    }
    public static int Main(string[] args) {
        try {
            if(args.Length==2 && args[0]=="--export-payload"){Console.Write(Policy.Launch(args[1]));return 0;}
            if(args.Length==1 && args[0]=="--selftest")return Tests.Run();
            if(args.Length==4 && args[0]=="--test-lock-child")return Policy.Reserve(args[1],args[2],"local_mock",args[3])?0:7;
            string mode=args.Length==1 && args[0]=="--live-launch"?"launch":"review";
            if(mode=="review") {
                if(args.Length>0 && !(args.Length==1 && args[0]=="--review"))return 2;
                Console.WriteLine("READY_FOR_APPROVAL - OFFLINE REVIEW ONLY. No USB enumeration or ADB connection.");
                Console.WriteLine("One detached original fromdebug Broadcast, no deliberate sleep; local baseline and ptgen gate.");
                Console.WriteLine("Separate launch and retrieval approval required. Retrieval is unavailable in this launch-only build.");
                return 0;
            }
            string exe=Assembly.GetExecutingAssembly().Location;
            if(Path.GetDirectoryName(Path.GetFullPath(exe))!=Root)throw new InvalidOperationException("Reviewed folder required");
            var prep=Load(Path.Combine(Root,"PREPARATION_STATE.json"));string nonce=Convert.ToString(prep["nonce"]);Policy.PathFor(nonce);
            string approval=Path.Combine(Root,"APPROVAL_"+mode.ToUpperInvariant()+".json");
            if(!File.Exists(approval) || !Approved(Load(approval),mode,nonce,HashFile(exe)))throw new InvalidOperationException("Explicit approval for this mode/binary/nonce is missing. No ADB connection made.");
            if(mode=="launch" && File.Exists(Path.Combine(Root,"DETACHED_FROMDEBUG_CONSUMED.json")))throw new InvalidOperationException("Launch already consumed. No retry.");
            using(var mutex=new Mutex(false,"Local\\MF904Q_DETACHED_FROMDEBUG_"+Data.Hash(Root))) {
                bool owned=false;try{owned=mutex.WaitOne(0);}catch(AbandonedMutexException){owned=true;}
                if(!owned)throw new InvalidOperationException("Another detached fromdebug monitor is running");
                try{using(var live=new Live(mode,nonce)){live.Run();}}finally{mutex.ReleaseMutex();}
            }
            return 0;
        }catch(Exception e){Console.Error.WriteLine(e.ToString());return 1;}
    }
}
public sealed class Live : IDisposable {
    readonly object gate=new object();readonly string mode,nonce;readonly Stopwatch clock=Stopwatch.StartNew();
    readonly ManualResetEvent baseline=new ManualResetEvent(false);
    readonly ManualResetEvent saved=new ManualResetEvent(false);
    delegate bool ConsoleHandler(uint kind);
    [DllImport("kernel32.dll")] static extern bool SetConsoleCtrlHandler(ConsoleHandler handler,bool add);
    [DllImport("kernel32.dll")] static extern IntPtr GetStdHandle(int id);
    [DllImport("kernel32.dll")] static extern bool GetConsoleMode(IntPtr h,out uint m);
    [DllImport("kernel32.dll")] static extern bool SetConsoleMode(IntPtr h,uint m);
    ConsoleHandler closeHandler;
    readonly Journal log;
    List<UsbRow> usb=new List<UsbRow>();List<AdbRow> adb=new List<AdbRow>();
    volatile bool running,armed,claimed;TcpClient tracker,request;Thread tracking,worker;
    string targetToken,targetTransport;bool targetPreviouslyPresent;
    double dispatch=-1,adbGone=-1,usbGone=-1,ended=-1,firstUsb=-1,stable2005Since=-1;
    string stableTransport; bool saw2005;
    Result result;string stopReason="USER_ENDED";
    public Live(string mode,string nonce){this.mode=mode;this.nonce=nonce;log=new Journal(Program.Root);log.Display+=Console.WriteLine;}
    bool Guard(AdbRow target) {
        if(!running)return false;
        var snapshot=Usb.Snapshot(true);
        lock(gate)return running && adb.Any(a=>a.transport_id==target.transport_id && Policy.Identity(a,snapshot)) && snapshot.Any(u=>u.token==targetToken && u.present && u.adb_candidate && (u.serial_hashes??new string[0]).Contains(Policy.Serial));
    }
    void SaveObservation() {
        if(mode!="launch" || !File.Exists(Path.Combine(Program.Root,"DETACHED_FROMDEBUG_CONSUMED.json")))return;
        var obs=Data.Obj("nonce",nonce,"dispatch_ms",dispatch,"adb_gone_ms",adbGone,"usb_gone_ms",usbGone,"ended_ms",ended,"session",log.Folder,"observation_complete",false);
        Policy.DurableReplace(Path.Combine(Program.Root,"LAUNCH_OBSERVATION.json"),Data.Json(obs));
    }
    void Track(){
        try{while(running){
            var next=Adb.Parse(Encoding.UTF8.GetString(Adb.Frame(tracker.GetStream())));
            lock(gate){
                bool present=targetTransport!=null && next.Any(a=>a.transport_id==targetTransport && a.serial_sha256==Policy.Serial && a.state=="device");
                if(targetPreviouslyPresent && !present && adbGone<0){adbGone=clock.Elapsed.TotalMilliseconds;SaveObservation();log.Add("target_adb_gone",Data.Obj("transport",targetTransport,"monotonic_ms",adbGone),"Target ADB transport disappeared");}
                if(stable2005Since>=0 && !next.Any(a=>a.transport_id==stableTransport && a.serial_sha256==Policy.Serial && a.state=="device")){log.Add("rndis_adb_tracking_loss",Data.Obj("transport",stableTransport,"duration_ms",clock.Elapsed.TotalMilliseconds-stable2005Since),"ADB tracking interrupted stability");stable2005Since=-1;stableTransport=null;}
                targetPreviouslyPresent=present;adb=next;log.Add("adb_snapshot",next,"ADB: "+string.Join(" | ",next.Select(a=>a.model+" "+a.state+" "+(a.serial_sha256==Policy.Serial?"candidate modem":"EXCLUDED"))));
            }
            baseline.Set();
        }}catch(Exception e){if(running){log.Add("tracker_error",e.ToString(),"Tracking failed; no reconnect");stopReason="TRACKER_FAILED";running=false;baseline.Set();}}
    }
    void TryClaim(){
        AdbRow target=null;
        lock(gate){
            if(!running || !armed || claimed)return;
            var matches=adb.Where(a=>Policy.Identity(a,usb)).ToList();if(matches.Count!=1)return;
            claimed=true;target=Adb.Copy(matches[0]);targetTransport=target.transport_id;
            targetToken=usb.Single(u=>u.adb_candidate && u.serial_hashes.Contains(Policy.Serial)).token;
            targetPreviouslyPresent=true;log.Add("identity_claimed",target,"MF904Q identity confirmed - one request only");
        }
        worker=new Thread(()=>Execute(target)){IsBackground=true};worker.Start();
    }
    void Execute(AdbRow target){
        try{
            if(!Guard(target))throw new InvalidOperationException("Identity lost before reservation");
            if(mode=="launch" && !Policy.Reserve(Program.Root,nonce,log.Folder,target.transport_id))throw new InvalidOperationException("Launch latch exists or could not be saved. No send.");
            // The child reads native getprop and gates ptgen before any settings change. Full USB/product identity
            // is already checked; guard is repeated inside Protocol.Run.
            using(var c=new TcpClient{NoDelay=true}){
                lock(gate)request=c;
                var pending=c.BeginConnect(IPAddress.Loopback,5037,null,null);
                using(pending.AsyncWaitHandle){if(!pending.AsyncWaitHandle.WaitOne(150))throw new IOException("Existing local ADB server connection timeout");c.EndConnect(pending);}
                c.SendTimeout=250;c.ReceiveTimeout=0;
                lock(gate){dispatch=clock.Elapsed.TotalMilliseconds;SaveObservation();}
                log.Add("request_dispatch",Data.Obj("monotonic_ms",dispatch,"mode",mode,"nonce",nonce,"transport",target.transport_id),null);
                result=Protocol.Run(c.GetStream(),target.transport_id,nonce,mode,()=>Guard(target),(k,v)=>log.Add("adb_protocol_"+k,v,null),250,1250);
                Policy.DurableNew(Path.Combine(log.Folder,"REQUEST_RESULT.json"),Data.Json(result));

            }
        }catch(Exception e){log.Add("attempt_error",e.ToString(),"Attempt ended - no retry: "+e.Message);}
        finally{lock(gate){request=null;ended=clock.Elapsed.TotalMilliseconds;SaveObservation();}}
    }
    public void Run(){
        try{
            Console.Title="MF904Q_DETACHED_FROMDEBUG_SINGLE_TRIAL — one launch only";
            uint inputMode;IntPtr input=GetStdHandle(-10);
            if(!GetConsoleMode(input,out inputMode) || !SetConsoleMode(input,(inputMode|0x80u)&~0x40u))throw new IOException("Could not disable console QuickEdit; no launch");
            using(var c=Adb.Open(5037,"host:version"))log.Add("existing_server_version",Encoding.UTF8.GetString(Adb.Frame(c.GetStream())),null);
            // This connects only to the existing server; it cannot start/kill it.
            usb=Usb.Snapshot(true);log.Add("usb_baseline",usb,null);
            if(usb.Any(u=>u.vid=="0E8D"))throw new IOException("Disconnect modem USB before beginning");
            tracker=Adb.Open(5037,"host:track-devices-l");tracker.ReceiveTimeout=0;running=true;
            tracking=new Thread(Track){IsBackground=true};tracking.Start();
            if(!baseline.WaitOne(4000) || !running)throw new IOException("Official ADB tracking baseline unavailable");
            closeHandler=kind=>{stopReason="CONSOLE_CLOSE_EVENT_"+kind;running=false;if(tracker!=null)tracker.Close();if(request!=null)request.Close();saved.WaitOne(3500);return true;};
            if(!SetConsoleCtrlHandler(closeHandler,true))throw new IOException("Could not register console save handler");
            log.Add("monitor_ready",Data.Obj("mode",mode,"nonce",nonce),"Monitor ready. Keep USB disconnected. Normal battery/Power boot only. Keep USB disconnected until instructed; press A only when instructed.");
            double readyAt=clock.Elapsed.TotalMilliseconds;
            while(running){
                if(Console.KeyAvailable){var key=Console.ReadKey(true).Key;
                    if(key==ConsoleKey.Q){stopReason="USER_Q";break;}
                    if(key==ConsoleKey.A && !armed){armed=true;log.Add("normal_boot_user_confirmed",true,"READY - connect modem USB once, without pressing device buttons. Q saves and stops.");}
                }
                var next=Usb.Snapshot(true);
                lock(gate){
                    foreach(var u in next.Where(u=>!usb.Any(p=>p.token==u.token))){if(u.vid=="0E8D" && firstUsb<0)firstUsb=clock.Elapsed.TotalMilliseconds;log.Add("usb_appeared",u,"USB appeared "+u.vid+":"+u.pid+" "+u.name);}
                    foreach(var u in usb.Where(u=>!next.Any(p=>p.token==u.token))){if(u.token==targetToken && usbGone<0){usbGone=clock.Elapsed.TotalMilliseconds;SaveObservation();}log.Add("usb_disappeared",Data.Obj("row",u,"monotonic_ms",clock.Elapsed.TotalMilliseconds),"USB disappeared "+u.vid+":"+u.pid);}
                    usb=next;
                }
                TryClaim();
                lock(gate){
                    double now=clock.Elapsed.TotalMilliseconds;
                    var returned=adb.Where(a=>a.transport_id!=targetTransport && Policy.Identity(a,usb) && usb.Any(u=>u.adb_candidate && u.pid=="2005" && u.serial_hashes.Contains(a.serial_sha256))).ToList();
                    bool valid=returned.Count==1;
                    if(valid && stableTransport!=returned[0].transport_id){stableTransport=returned[0].transport_id;stable2005Since=now;saw2005=true;log.Add("rndis_adb_stable_started",Data.Obj("transport",stableTransport,"monotonic_ms",now),"PID2005 and verified ADB device returned; observation only");}
                    if(!valid && stable2005Since>=0){log.Add("rndis_adb_stability_lost",Data.Obj("transport",stableTransport,"duration_ms",now-stable2005Since),"RNDIS+ADB stability interrupted");stable2005Since=-1;stableTransport=null;}
                    if(Observation.Finished(now,ended,stable2005Since)){stopReason="SINGLE_REQUEST_OBSERVATION_COMPLETE";break;}
                    if(ended<0 && firstUsb>=0 && clock.Elapsed.TotalMilliseconds-firstUsb>=120000){stopReason="NO_VERIFIED_REQUEST_WITHIN_120S";break;}
                }
                if(firstUsb<0 && clock.Elapsed.TotalMilliseconds-readyAt>900000){stopReason="NO_CONNECTION_WITHIN_15_MINUTES";break;}
                Thread.Sleep(40);
            }
        }finally{Dispose();}
    }
    bool disposed;
    public void Dispose(){
        if(disposed)return;disposed=true;running=false;
        if(tracker!=null)tracker.Close();if(request!=null)request.Close();
        if(worker!=null && worker.IsAlive)worker.Join(2500);if(tracking!=null && tracking.IsAlive)tracking.Join(2500);
        var summary=Data.Obj("stage",Policy.Stage,"mode",mode,"nonce",nonce,"reason",stopReason,"claimed",claimed,"dispatch_ms",dispatch,"adb_gone_ms",adbGone,"usb_gone_ms",usbGone,"ended_ms",ended,"request",result,"diagnostic_path",Policy.PathFor(nonce),"automatic_retry",false,"server_restarted",false,"potential_broadcasts_max",1,"broadcast_execution_proven",false,"saw_verified_pid2005_device",saw2005,"stable2005_transport",stableTransport,"stable2005_since_ms",stable2005Since,"stable2005_observed_ms",stable2005Since>=0?clock.Elapsed.TotalMilliseconds-stable2005Since:0,"verdict","PENDING_SEPARATELY_APPROVED_RETRIEVAL");
        try{
            Policy.DurableNew(Path.Combine(log.Folder,"SUMMARY.json"),Data.Json(summary));
            if(mode=="launch" && File.Exists(Path.Combine(Program.Root,"DETACHED_FROMDEBUG_CONSUMED.json")))Policy.DurableReplace(Path.Combine(Program.Root,"LAUNCH_OBSERVATION.json"),Data.Json(summary));
            log.Add("finished",summary,"Saved. No automatic next stage.");
        }finally{log.Dispose();saved.Set();if(closeHandler!=null)SetConsoleCtrlHandler(closeHandler,false);}
    }
}
}
