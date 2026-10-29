using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using MF904QMonitor;

// Independent reader. No ADB executable is invoked, so a missing server cannot be started.
public static class ShortRead {
 public const string Serial="PRIVATE_SERIAL_HASH_NOT_INCLUDED";
 public const int ConservativeLimit=1024, HistoricalTransportLimit=4096;
 public static readonly string[] Reads=new string[0];
 public static readonly string[] Names=new string[0];
 static string Root {get{return AppDomain.CurrentDomain.BaseDirectory;}}
 public static int EffectiveLimit(int? discovered){if(discovered.HasValue && discovered.Value<=0)throw new InvalidDataException("Invalid transport limit");return Math.Min(ConservativeLimit,discovered??HistoricalTransportLimit);}
 // The ADB OPEN destination is UTF-8 plus a trailing NUL. Smart-socket framing is separate.
 public static byte[] Body(string request,int? discovered){if(request==null || request.IndexOf('\0')>=0)throw new InvalidDataException("Embedded NUL rejected");byte[] b=new UTF8Encoding(false,true).GetBytes(request);if(b.Length>65535 || b.Length+1>EffectiveLimit(discovered))throw new InvalidDataException("Payload rejected before write: OPEN="+(b.Length+1)+", effective limit="+EffectiveLimit(discovered));return b;}
 public static string Command(int i,string nonce){if(i<0 || i>=Reads.Length || !Regex.IsMatch(nonce,@"^[a-f0-9]{32}$"))throw new InvalidDataException("Non-allowlisted command/index/nonce");return Reads[i]+" 2>&1; rc=$?; printf '\\nMFEND_"+nonce+"_"+i+"=%s\\n' \"$rc\"";}
 static void Trace(Action<string,object> log,string k,object data){if(log!=null)log(k,data);}
 public static byte[] Exact(Stream s,int n){if(n<0 || n>65536)throw new InvalidDataException("Invalid frame size");byte[] b=new byte[n];int p=0;while(p<n){int k=s.Read(b,p,n-p);if(k==0)throw new EndOfStreamException("Server disconnected during exact read");p+=k;}return b;}
 public static byte[] Frame(Stream s){string h=Encoding.ASCII.GetString(Exact(s,4));int n;if(!Regex.IsMatch(h,"^[0-9A-Fa-f]{4}$") || !int.TryParse(h,NumberStyles.HexNumber,CultureInfo.InvariantCulture,out n))throw new InvalidDataException("Malformed frame length");return Exact(s,n);}
 public static void Request(Stream s,string request,int? limit,Action<string,object> log){string phase="validate";try{byte[] b=Body(request,limit);Trace(log,"payload",Data.Obj("smart_socket_body_bytes",b.Length,"open_destination_bytes",b.Length+1,"smart_socket_header_bytes",4,"effective_limit",EffectiveLimit(limit),"limit_source",limit.HasValue?"supplied_verified_transport_limit":"historical_4096_with_1024_cap_not_live_discovered"));phase="header_write";s.Write(Encoding.ASCII.GetBytes(b.Length.ToString("x4")),0,4);Trace(log,"header_written",4);phase="body_write";s.Write(b,0,b.Length);Trace(log,"body_written",b.Length);phase="status_read";string status=Encoding.ASCII.GetString(Exact(s,4));Trace(log,"status",status);if(status=="FAIL"){phase="fail_reason_read";string reason=Encoding.UTF8.GetString(Frame(s));Trace(log,"explicit_fail",reason);throw new IOException("Explicit ADB FAIL: "+reason);}if(status!="OKAY")throw new InvalidDataException("Unexpected ADB status: "+status);Trace(log,"accepted",true);}catch(Exception e){Trace(log,"protocol_error",Data.Obj("phase",phase,"type",e.GetType().FullName,"exception",e.ToString()));throw;}}
 public static bool Identity(AdbRow a,List<UsbRow> usb){if(a==null || a.state!="device" || a.serial_sha256!=Serial || !Regex.IsMatch(a.transport_id??"",@"^[1-9][0-9]{0,17}$") || a.product!="MF904Q-6.0-1-6735WM_LCD_20240123" || a.model!="MF904Q_6_0_1_6735WM_LCD_20240123" || a.device!="mf904q_v4_35m_lwtg")return false;var matches=usb.Where(u=>u.adb_candidate && (u.serial_hashes??new string[0]).Contains(a.serial_sha256)).ToList();return matches.Count==1 && matches[0].present && matches[0].vid=="0E8D" && new[]{"2005"}.Contains(matches[0].pid) && matches[0].problem_code==0 && matches[0].adb_guid_registered && string.Equals(matches[0].service,"WinUSB",StringComparison.OrdinalIgnoreCase);}
 public static TcpClient Connect(){var c=new TcpClient {NoDelay=true};try{var ar=c.BeginConnect(IPAddress.Loopback,5037,null,null);using(ar.AsyncWaitHandle){if(!ar.AsyncWaitHandle.WaitOne(1000))throw new TimeoutException("Existing server connect timeout; no start/restart");c.EndConnect(ar);}c.ReceiveTimeout=2000;c.SendTimeout=1500;return c;}catch{c.Close();throw;}}
 public static AdbRow Match(Action<string,object> log){var usb=Usb.Snapshot(true);List<AdbRow> rows;using(var c=Connect()){Request(c.GetStream(),"host:track-devices-l",null,log);rows=Adb.Parse(Encoding.UTF8.GetString(Frame(c.GetStream())));}Trace(log,"identity_snapshot",Data.Obj("target_adb",rows.Where(a=>a.serial_sha256==Serial).ToArray(),"target_usb",usb.Where(u=>(u.serial_hashes??new string[0]).Contains(Serial)).ToArray()));var targets=rows.Where(a=>Identity(a,usb)).ToList();if(targets.Count!=1)throw new IOException("No unique matching authorized MF904Q transport; stop");return targets[0];}
 public static void CompareTransport(string expected,string actual){if(expected!=actual)throw new IOException("Transport changed; stop without retry");}
 public static void Guard(string tid,Action<string,object> log){CompareTransport(tid,Match(log).transport_id);}

}
