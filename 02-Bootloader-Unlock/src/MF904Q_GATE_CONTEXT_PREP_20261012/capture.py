"""Continuous pipe ownership; no timeout detaches a live child."""
import threading,os,time,pathlib,json,datetime
class Capture:
 def __init__(self,p,folder,label,display=True):
  self.p=p;self.folder=pathlib.Path(folder);self.label=label;self.display=display;self.errors=[];self.eof={};self.threads=[];self.buffers={};self.lock=threading.Lock()
  self.events=(self.folder/(label+'_events.jsonl')).open('x',encoding='utf8',buffering=1)
  for name,stream in [('stdout',p.stdout),('stderr',p.stderr)]:
   self.buffers[name]=bytearray();self.eof[name]=False
   t=threading.Thread(target=self.read,args=(name,stream),daemon=False);t.start();self.threads.append(t)
 def event(self,kind,**data):
  with self.lock:
   self.events.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonic':time.monotonic(),'host_receive_time_only':True,'event':kind,**data})+'\n');self.events.flush();os.fsync(self.events.fileno())
 def read(self,name,stream):
  try:
   with (self.folder/(self.label+'_'+name+'.bin')).open('xb',buffering=0) as f:
    while True:
     chunk=os.read(stream.fileno(),4096)
     if not chunk:break
     f.write(chunk);os.fsync(f.fileno());self.buffers[name].extend(chunk);self.event('OUTPUT_CHUNK',stream=name,bytes=len(chunk),text=chunk.decode('utf8','replace'))
     if self.display:
      try:print(chunk.decode('utf8','replace'),end='',flush=True)
      except (OSError,UnicodeError):self.display=False
   self.eof[name]=True;self.event('PIPE_EOF',stream=name)
  except BaseException as ex:self.errors.append(repr(ex));self.event('PIPE_ERROR',stream=name,error=repr(ex))
 def finish(self):
  # Called only after native child exit. Never discards a live child's pipes.
  if self.p.poll() is None:raise ValueError('Cannot finish while process pending')
  for t in self.threads:t.join(5)
  if any(t.is_alive() for t in self.threads):raise ValueError('EOF not complete; retain collector')
  self.p.stdout.close();self.p.stderr.close()
  self.event('PROCESS_EXIT',rc=self.p.returncode,eof=self.eof,errors=self.errors)
  result={'rc':self.p.returncode,'eof':all(self.eof.values()),'errors':self.errors,'text':bytes(self.buffers['stdout']+b'\n'+self.buffers['stderr']).decode('utf8','replace')}
  self.events.close();return result
