using System;using System.Collections.Generic;using System.Linq;using System.Text.RegularExpressions;using System.IO;using MF904QMonitor;
public static class RestrictedLogs {
 public static List<Dictionary<string,object>> Filter(string text){var records=new List<Dictionary<string,object>>();foreach(string line in text.Split('\n')){
  var h=Regex.Match(line.TrimEnd('\r'),@"^(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d{3,6})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+PersistentDataBlockService\s*:\s*(.*)$");if(!h.Success)continue;
  string msg=h.Groups[6].Value,kind=null,canonical=null;
  if(msg=="doGetOemUnlockEnabled, return false"||msg=="doGetOemUnlockEnabled, return true"){kind="getter_return";canonical=msg;}
  else if(msg=="doGetOemUnlockEnabled in"){kind="getter_begin";canonical=msg;}
  else if(msg=="partition not available"||msg.StartsWith("partition not available:")||msg=="partition not available?"){kind="partition_missing";canonical="partition not available";}
  else if(msg=="unable to access persistent partition"||msg.StartsWith("unable to access persistent partition:")){kind="partition_io_error";canonical="unable to access persistent partition";}
  else if(msg=="enforceChecksumValidity, return true"||msg=="enforceChecksumValidity, return false"){kind="checksum_result";canonical=msg;}
  else if(msg=="mService::setOemUnlockEnabled, enabled=true"||msg=="mService::setOemUnlockEnabled, enabled=false"){kind="setter_entry_history";canonical=msg;}
  else if(msg=="computeAndWriteDigestLocked, return true"||msg=="computeDigestLocked in"||msg=="computeDigestLocked, start read partition"||msg=="computeDigestLocked, end read partition"||msg=="computeDigestLocked out"){kind="digest_history";canonical=msg;}
  else if(msg=="Formatting FRP partition..."||msg=="formatPartitionLocked"||msg=="formatIfOemUnlockEnabled"||msg.StartsWith("formatPartitionLocked init data, PARTITION_TYPE_MARKER=428873843, size=0")){kind="format_policy_history";canonical=msg.StartsWith("formatPartitionLocked init")?"formatPartitionLocked init data, PARTITION_TYPE_MARKER=428873843, size=0":msg;}
  else if(msg=="failed to format block"||msg=="failed to read partition"||msg=="failed to write block checksum"||msg=="SHA-256 not supported?"){kind="checksum_or_partition_error";canonical=msg;}
  if(kind==null)continue;
  string date=h.Groups[1].Value,time=h.Groups[2].Value;
  records.Add(Data.Obj("date_no_year",date,"android_clock",time,"pid",h.Groups[3].Value,"tid",h.Groups[4].Value,"priority",h.Groups[5].Value,"category",kind,"message",canonical,"attribution","UNCONFIRMED_ANDROID_CLOCK_YEAR_BOOT_AND_PID_CORRELATION"));if(records.Count>4096)throw new InvalidDataException("RECORD_LIMIT");
 }return records;}
 public static string Classify(string text){string source=string.Join("\n",text.Split('\n').Where(line=>!Regex.IsMatch(line,@"\s[VDIWEF]\s+PersistentDataBlockService\s*:")));if(Regex.IsMatch(source,@"Permission Denial|Permission denied|SecurityException",RegexOptions.IgnoreCase))return "PERMISSION_DENIED";if(Regex.IsMatch(source,@"logcat:|unknown option|invalid option|not found|No such file",RegexOptions.IgnoreCase))return "LOGCAT_SOURCE_DIAGNOSTIC_ERROR";return null;}

}
