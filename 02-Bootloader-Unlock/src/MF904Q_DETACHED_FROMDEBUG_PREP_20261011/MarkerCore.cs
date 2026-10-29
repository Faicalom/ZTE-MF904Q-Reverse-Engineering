using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using MF904QMonitor;

namespace MF904QDetachedFromdebug {
public static class Policy {
    public const string Stage = "MF904Q_DETACHED_FROMDEBUG_SINGLE_TRIAL";
    public const string Serial = "PRIVATE_SERIAL_HASH_NOT_INCLUDED";
    public static bool Identity(AdbRow a, List<UsbRow> usb) {
        if(a==null || a.state!="device" || a.serial_sha256!=Serial || !Regex.IsMatch(a.transport_id??"",@"^[1-9][0-9]{0,17}$"))return false;
        if(a.product!="MF904Q-6.0-1-6735WM_LCD_20240123" || a.model!="MF904Q_6_0_1_6735WM_LCD_20240123" || a.device!="mf904q_v4_35m_lwtg")return false;
        var m=usb.Where(u=>u.adb_candidate && (u.serial_hashes??new string[0]).Contains(a.serial_sha256)).ToList();
        return m.Count==1 && m[0].present && m[0].vid=="0E8D" && new[]{"2003","2005","201C"}.Contains(m[0].pid) && m[0].problem_code==0 && m[0].adb_guid_registered && string.Equals(m[0].service,"WinUSB",StringComparison.OrdinalIgnoreCase);
    }
    public static string PathFor(string nonce) {
        if(nonce==null || !Regex.IsMatch(nonce,@"\A[0-9a-f]{32}\z"))throw new ArgumentException("Invalid nonce");
        return "/data/local/tmp/mf904q_fromdebug_"+nonce+".log";
    }
    public const string Forward="/system/bin/am broadcast --user 0 -n com.android.settings/.DevelopmentSettingsReceiver -a com.lr.usb.openclose --ei opendebug 1 --ez frombat false";
    public static string Launch(string nonce) {
        string path=PathFor(nonce);
        string child = "trap \"\" HUP\np=$1\nn=$2\n"+
            "mark() { IFS=\" \" read u rest </proc/uptime || return 21; IFS= read b </proc/sys/kernel/random/boot_id || return 22; echo \"$1 nonce=$n boot=$b up=$u $2\" >>\"$p\"; }\n"+
            "IFS=\" \" read pid comm state ppid pgid sid rest </proc/$$/stat || exit 23\n"+
            "mark START \"pid=$pid pgid=$pgid sid=$sid\" || exit 24\n"+
            "ptgen=$(/system/bin/getprop ro.big.ptgen) || { mark GATE_ERROR \"ptgen_read_failed\"; mark END \"rc=29 sent=0\"; exit 29; }\n"+
            "[ \"$ptgen\" = 1 ] || { mark GATE_REJECTED \"ptgen=$ptgen\"; mark END \"rc=29 sent=0\"; exit 29; }\n"+
            "sys=$(/system/bin/getprop sys.usb.config) || { mark BASELINE_ERROR \"sys_read_failed\"; mark END \"rc=30 sent=0\"; exit 30; }\n"+
            "persist=$(/system/bin/getprop persist.sys.usb.config) || { mark BASELINE_ERROR \"persist_read_failed\"; mark END \"rc=30 sent=0\"; exit 30; }\n"+
            "mark BASELINE \"ptgen=$ptgen sys.usb.config=$sys persist.sys.usb.config=$persist adb_enabled=UNKNOWN_NOT_QUERIED\" || exit 31\n"+
            "mark AM_BEGIN \"\" || exit 26\n"+
            "/system/bin/toybox timeout -k 1 10 "+Forward+" >\"$p.stdout\" 2>\"$p.stderr\"\n"+
            "rc=$?\nmark AM_END \"rc=$rc\" || exit 27\n"+
            "mark END \"rc=$rc\" || exit 28\n";
        return "umask 077\np="+path+"\n"+
            "( set -C; echo 'MF904Q_FROMDEBUG_CONTROL nonce="+nonce+"' > \"$p\" && : >\"$p.stdout\" && : >\"$p.stderr\" ) || exit 20\n"+
            "trap '' HUP\n/system/bin/setsid /system/bin/sh -c '"+child+"' _ \"$p\" "+nonce+" </dev/null >/dev/null 2>>\"$p\" &\n"+
            "echo 'LAUNCHED nonce="+nonce+"'\n";
    }
    public static bool CommandAllowed(string command,string nonce,string mode) {
        return mode=="launch" && command==Launch(nonce);
    }
    public static void DurableNew(string path,string text) {
        using(var f=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.Read,4096,FileOptions.WriteThrough)) {
            byte[] b=Encoding.UTF8.GetBytes(text);f.Write(b,0,b.Length);f.Flush(true);
        }
    }
    public static void DurableReplace(string path,string text) {
        string temp=path+"."+Guid.NewGuid().ToString("N")+".tmp";
        DurableNew(temp,text);
        if(File.Exists(path))File.Replace(temp,path,null);else File.Move(temp,path);
    }
    public static bool Reserve(string root,string nonce,string session,string transport) {
        try { DurableNew(System.IO.Path.Combine(root,"DETACHED_FROMDEBUG_CONSUMED.json"),Data.Json(Data.Obj("stage",Stage,"nonce",nonce,"path",PathFor(nonce),"session",session,"transport",transport,"time",Data.Now(),"no_retry",true,"command",Launch(nonce))));return true; }
        catch(IOException) { return false; }
    }
}
public static class Observation {
    public static bool Finished(double now,double ended,double stableSince) {
        if(ended<0 || now-ended<120000)return false;
        return stableSince<0 || now-stableSince>=120000 || now-ended>=240000;
    }
}
public sealed class Result {
    public string outcome,stage,exception_type,exception_message,exception_full,output="",fail_reason;
    public bool transport_okay,header_written,body_written,service_okay,eof,timeout,first_output;
    public double elapsed_ms;
}
public static class Protocol {
    static byte[] Exact(Stream s,int n) {
        byte[] b=new byte[n];int p=0;while(p<n){int k=s.Read(b,p,n-p);if(k==0)throw new EndOfStreamException("Incomplete ADB response "+p+"/"+n);p+=k;}return b;
    }
    static string Text(Stream s,int n) {return Encoding.UTF8.GetString(Exact(s,n));}
    public static Result Run(Stream stream,string transport,string nonce,string mode,Func<bool> guard,Action<string,object> log,int acceptMs,int outputMs) {
        var r=new Result();var clock=Stopwatch.StartNew();var lockTimer=new object();bool finished=false;
        string command=Policy.Launch(nonce);
        if(!Regex.IsMatch(transport??"",@"^[1-9][0-9]{0,17}$") || !Policy.CommandAllowed(command,nonce,mode))throw new InvalidOperationException("Command/transport rejected");
        Action<string> stage=v=>{r.stage=v;log(v,Data.Obj("elapsed_ms",clock.Elapsed.TotalMilliseconds));};
        using(var timer=new Timer(o=>{lock(lockTimer){if(finished)return;r.timeout=true;try{stream.Close();}catch{}}},null,acceptMs,Timeout.Infinite)) {
            try {
                if(!guard())throw new InvalidOperationException("Identity lost before transport");
                string[] requests={"host:transport-id:"+transport,"exec:"+command};
                for(int i=0;i<requests.Length;i++) {
                    if(i==1 && !guard())throw new InvalidOperationException("Identity lost before exec request");
                    string label=i==0?"transport":"exec";
                    byte[] b=Encoding.UTF8.GetBytes(requests[i]);byte[] h=Encoding.ASCII.GetBytes(b.Length.ToString("x4",CultureInfo.InvariantCulture));
                    stage(label+".header_write");stream.Write(h,0,4);if(i==1)r.header_written=true;
                    log(label+".header_written",Data.Obj("bytes",4,"android_receipt_proven",false));
                    stage(label+".body_write");stream.Write(b,0,b.Length);if(i==1)r.body_written=true;
                    log(label+".body_written",Data.Obj("bytes",b.Length,"android_receipt_proven",false));
                    stage(label+".status_read");string status=Text(stream,4);log(label+".status",status);
                    if(status=="FAIL") {
                        int n=int.Parse(Text(stream,4),NumberStyles.HexNumber,CultureInfo.InvariantCulture);
                        if(n>4096)throw new IOException("Oversized FAIL");
                        r.fail_reason=Text(stream,n);r.outcome="EXPLICIT_ADB_FAIL";return r;
                    }
                    if(status!="OKAY")throw new IOException("Unexpected ADB response: "+status);
                    if(i==0)r.transport_okay=true;else r.service_okay=true;
                }
                timer.Change(outputMs,Timeout.Infinite);stage("exec.output_read");
                using(var output=new MemoryStream()) {
                    byte[] b=new byte[1024];int n;
                    while((n=stream.Read(b,0,b.Length))!=0) {
                        if(!r.first_output){r.first_output=true;log("exec.first_output",Data.Obj("elapsed_ms",clock.Elapsed.TotalMilliseconds));}
                        output.Write(b,0,n);r.output=Encoding.UTF8.GetString(output.ToArray());
                        if(output.Length>32768)throw new IOException("Output limit reached");
                    }
                    r.eof=true;r.output=Encoding.UTF8.GetString(output.ToArray());
                }
                r.outcome=r.output.Length==0?"ACCEPTED_EMPTY_EOF_UNKNOWN":"OUTPUT_EOF_REQUIRES_VALIDATION";
            }catch(Exception e) {
                r.exception_type=e.GetType().FullName;r.exception_message=e.Message;r.exception_full=e.ToString();
                r.outcome=r.timeout?"LOCAL_DEADLINE_"+r.stage:"EXCEPTION_"+r.stage;
            }finally {lock(lockTimer){finished=true;timer.Change(Timeout.Infinite,Timeout.Infinite);}r.elapsed_ms=clock.Elapsed.TotalMilliseconds;log("request_result",r);}
        }
        return r;
    }
}
}
