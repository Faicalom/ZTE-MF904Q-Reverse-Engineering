using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Net.Sockets;
using System.Security.Cryptography;
using MF904QMonitor;

public interface IPort { void Guard(); string Read(string command); void Reserve(); }
public static class Controlled {
 public const string Id="/system/bin/id", Monkey="/system/bin/service call activity 104", Setter="/system/bin/service call persistent_data_block 6 i32 1", Getter="/system/bin/service call persistent_data_block 7";
 public static uint[] Parcel(string s,int count) {
  var m=Regex.Match(s,@"^\s*Result:\s*Parcel\(\s*([0-9a-fA-F]{8}(?:\s+[0-9a-fA-F]{8})*)(?:\s+'[^'\r\n]*')?\s*\)\s*$");
  if(!m.Success)throw new InvalidDataException("Incomplete, exception, or unsupported Parcel; UNKNOWN");
  var w=Regex.Split(m.Groups[1].Value.Trim(),@"\s+").Select(x=>Convert.ToUInt32(x,16)).ToArray();
  if(w.Length!=count || w[0]!=0)throw new InvalidDataException("Binder exception or unexpected Parcel size"); return w;
 }
 public static bool Bool(string s){var w=Parcel(s,2);if(w[1]>1)throw new InvalidDataException("Non-boolean Binder value");return w[1]==1;}
 public static void Root(string s){var m=Regex.Match(s,@"^uid=(\d+)\([^\r\n)]*\)");if(!m.Success || m.Groups[1].Value!="0")throw new InvalidDataException("UID 0 not verified");}
 public static string Execute(IPort p){p.Guard();Root(p.Read(Id));p.Guard();if(Bool(p.Read(Monkey)))throw new InvalidDataException("monkey=true; setter forbidden");p.Guard();p.Reserve();p.Guard();Parcel(p.Read(Setter),1);return "BINDER_ACCEPTED_STORAGE_UNKNOWN";}
 public static string[] Post={Getter,"/system/bin/getprop sys.oem_unlock_allowed","/system/bin/logcat -d -b system -v threadtime 'PersistentDataBlockService:I' '*:S'"};
 public static string Wrap(string command,string nonce){if(!Regex.IsMatch(nonce,"^[a-f0-9]{32}$"))throw new InvalidDataException();return "shell:"+command+" 2>&1; rc=$?; printf '\\nMFEND_"+nonce+"=%s\\n' \"$rc\"";}
 public static string Complete(string raw,string nonce,bool eof){var m=Regex.Match(raw,@"\nMFEND_"+nonce+@"=(\d+)\r?\n\z");if(!eof || !m.Success)throw new InvalidDataException("EOF/nonce missing; execution UNKNOWN");if(m.Groups[1].Value!="0")throw new InvalidDataException("Android source RC="+m.Groups[1].Value);return raw.Substring(0,m.Index);}
 public static void ReserveFile(string path){Directory.CreateDirectory(Path.GetDirectoryName(path));using(var f=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.Read,4096,FileOptions.WriteThrough)){var b=Encoding.UTF8.GetBytes(Data.Json(Data.Obj("state","SEND_RESERVED_NEVER_RETRY","time",Data.Now(),"command",Setter,"serial_sha256",ShortRead.Serial)));f.Write(b,0,b.Length);f.Flush(true);}}
 public static string Digest(string path){using(var h=SHA256.Create())using(var f=File.OpenRead(path))return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
 public static int Main(string[] args){
  string root=AppDomain.CurrentDomain.BaseDirectory;
  if(args.Length==1 && args[0]=="--selftest")return Tests.Run(root);
  if(args.Length==0 || args[0]=="--review"){Console.WriteLine("READY_FOR_APPROVAL. No live connection. Modes: monkey, setter, post; each requires a separate bound approval file. No approval supplied.");return 0;}
  string mode=args[0];if(args.Length!=2 || !new[]{"monkey","setter","post"}.Contains(mode))return 2;
  // Approval is never created by this program. It must be prepared only after explicit future authorization.
  string expected="MF904Q_OEM_SETTER6_CONTROLLED_PREP_20261011|"+mode+"|"+Digest(System.Reflection.Assembly.GetExecutingAssembly().Location)+"|"+Data.Hash(string.Join("\n",new[]{Id,Monkey,Setter}.Concat(Post)));
  if(!File.Exists(args[1]) || File.ReadAllText(args[1]).Trim()!=expected){Console.WriteLine("APPROVAL_MISSING_OR_MISMATCH; no connection");return 3;}
  string fixedRoot=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"MF904QProject","OEM_SETTER6_20261011",ShortRead.Serial);
  // Each mode has one attempt, including failures; no automatic restart/retry.
  try{ReserveFile(Path.Combine(fixedRoot,mode+"_ATTEMPT_RESERVED.json"));}catch(Exception e){Console.WriteLine("ATTEMPT_BLOCKED "+e.Message);return 4;}
  using(var j=new Journal(root)){
   var port=new LivePort(j,Path.Combine(fixedRoot,"SEND_RESERVED.json"));
   try{
    if(mode=="setter")j.Add("outcome",Controlled.Execute(port),null);
    else if(mode=="monkey"){port.Guard();j.Add("monkey",Bool(port.Read(Monkey)),null);}
    else {bool value=false;string prop=null;for(int i=0;i<Post.Length;i++){port.Guard();string s=port.Read(Post[i]);if(i==0){value=Bool(s);j.Add("getter",value,null);}else if(i==1){prop=s.Trim();j.Add("property_supporting_only",prop=="0"||prop=="1"?prop:"UNKNOWN",null);}else {string error=RestrictedLogs.Classify(s);if(error!=null)throw new InvalidDataException(error);j.Add("restricted_service_records",RestrictedLogs.Filter(s),null);}}j.Add("outcome",PostState(value,prop),null);}
   }catch(Exception e){j.Add("stopped",Data.Obj("type",e.GetType().FullName,"exception",e.ToString(),"storage","UNKNOWN","retry",false),null);Console.WriteLine("STOPPED; no retry. "+e.Message);return 5;}
   finally{j.Dispose();var files=Directory.GetFiles(j.Folder).Select(f=>new {file=Path.GetFileName(f),sha256=Digest(f)}).ToArray();Data.Atomic(Path.Combine(j.Folder,"EVIDENCE_SHA256.json"),Data.Json(files));Console.WriteLine("Evidence: "+j.Folder);}
  }return 0;
 }
 public static string PostState(bool getter,string prop){if(prop!="0"&&prop!="1")return "PROPERTY_UNKNOWN_STOP_NO_REBOOT_NO_RETRY";if(getter!=(prop=="1"))return "CONFLICT_STOP_NO_REBOOT_NO_RETRY";return getter?"OEM_TRUE_CORROBORATED_DIGEST_DURABILITY_AND_LK_UNKNOWN":"OEM_FALSE_CORROBORATED_INTERNAL_READ_HEALTH_UNKNOWN";}
}
public sealed class LivePort:IPort {
 readonly Journal j;readonly string latch;string tid;
 public LivePort(Journal journal,string path){j=journal;latch=path;}
 void Log(string k,object x){j.Add(k,x,null);}
 public void Guard(){var a=ShortRead.Match(Log);if(tid==null)tid=a.transport_id;else ShortRead.CompareTransport(tid,a.transport_id);}
 public void Reserve(){Controlled.ReserveFile(latch);Log("setter_send_reserved",new {path=latch});}
 public string Read(string command){
  string nonce=Guid.NewGuid().ToString("N"),request=Controlled.Wrap(command,nonce);ShortRead.Body(request,null);Log("request",new {command=command,nonce=nonce,open_bytes=Encoding.UTF8.GetByteCount(request)+1});
  bool privateLog=command==Controlled.Post[2];var text=new StringBuilder();string phase="connect";var received=new MemoryStream();
  try{using(var c=ShortRead.Connect()){c.ReceiveTimeout=5000;var s=c.GetStream();phase="transport";ShortRead.Request(s,"host:transport-id:"+tid,null,Log);phase="shell_accept";ShortRead.Request(s,request,null,Log);phase="android_output";var timer=System.Diagnostics.Stopwatch.StartNew();byte[] b=new byte[4096];bool first=true,eof=false;using(var ms=received){while(true){if(timer.ElapsedMilliseconds>10000)throw new TimeoutException("Total output deadline; device execution may continue");c.ReceiveTimeout=(int)Math.Min(5000,Math.Max(1,10000-timer.ElapsedMilliseconds));int n=s.Read(b,0,b.Length);if(n==0){eof=true;break;}if(first){Log("first_android_byte",true);first=false;}ms.Write(b,0,n);if(ms.Length>262144)throw new InvalidDataException("Output bound exceeded");}text.Append(new UTF8Encoding(false,true).GetString(ms.ToArray()));}Log("EOF",eof);phase="completion_parse";if(!privateLog)Log("raw_completion_response",text.ToString());string output=Controlled.Complete(text.ToString(),nonce,eof);Log("android_rc",0);if(!privateLog)Log("raw_response",output);return output;}}
  catch(Exception e){Log("read_error",Data.Obj("phase",phase,"type",e.GetType().FullName,"exception",e.ToString(),"command_may_have_executed",command==Controlled.Setter));if(!privateLog)Log("partial_response_base64",Convert.ToBase64String(received.ToArray()));else if(text.Length>0)Log("partial_restricted_records",RestrictedLogs.Filter(text.ToString()));throw;}
 }
}
