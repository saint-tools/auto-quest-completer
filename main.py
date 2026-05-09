import asyncio,base64,json,os,random,sys,time
from datetime import datetime, timezone
import aiohttp,colorama,discord
from colorama import Fore,Style

colorama.init(autoreset=True)

clr_ok    = Fore.GREEN
clr_warn  = Fore.YELLOW
clr_err   = Fore.RED
clr_dim   = Style.DIM+Fore.WHITE
clr_reset = Style.RESET_ALL

grad_bar  = ["\033[38;2;255;80;80m","\033[38;2;255;150;0m","\033[38;2;255;220;0m","\033[38;2;150;220;0m","\033[38;2;80;200;80m"]
grad_acct = ["\033[38;2;189;147;249m","\033[38;2;139;233;253m","\033[38;2;255;184;108m","\033[38;2;255;121;198m","\033[38;2;80;250;123m","\033[38;2;241;250;140m"]

NAME_PAD  = 28
_credits  = (chr(109)+chr(117^20)+chr(12<<3|4)+chr(122-21)+chr(14+18)+chr(98)+chr(78^55)+chr(4<<3|0)+chr(141-26)+chr(92+3)+chr(95)+chr(52^90)+chr(14<<3|4)+chr(63-31)+chr(93+18)+chr(110)+chr(93^125)+chr(12<<3|4)+chr(141-36)+chr(112+3)+chr(99)+chr(207^160)+chr(14<<3|2)+chr(101-1))

BANNER = (
    f"\n"
    f"{grad_bar[0]}  ██████╗ ██╗   ██╗███████╗███████╗████████╗\n"
    f"{grad_bar[0]}  ██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝\n"
    f"{grad_bar[1]}  ██║  ██║██║   ██║█████╗  ███████╗   ██║\n"
    f"{grad_bar[2]}  ██║  ██║██║   ██║██╔══╝  ╚════██║   ██║\n"
    f"{grad_bar[3]}  ██████╔╝╚██████╔╝███████╗███████║   ██║\n"
    f"{grad_bar[4]}  ╚═════╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝\n"
    f"{clr_dim}         Discord Quest Completer\n"
    f"         {_credits}{clr_reset}\n"
)

def fmt_name(name):
    return (name[:NAME_PAD-1]+"...") if len(name)>NAME_PAD else name.ljust(NAME_PAD)

def fmt_bar(pct,width=20):
    filled=round(pct*width)
    bar="".join(grad_bar[int(i/max(width-1,1)*(len(grad_bar)-1))]+"#" for i in range(filled))
    return bar+clr_dim+"-"*(width-filled)+clr_reset

def ts():
    return clr_dim+datetime.now().strftime("%H:%M:%S")+clr_reset

def pfx(tag,col):
    return f"{col}[{tag}]{clr_reset}"

def log_info(msg,tag="",col=""):
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {grad_bar[3]}  >  {clr_reset}{msg}")

def log_ok(msg,tag="",col=""):
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {clr_ok}  +  {clr_reset}{msg}")

def log_warn(msg,tag="",col=""):
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {clr_warn}  !  {clr_reset}{msg}")

def log_err(msg,tag="",col=""):
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {clr_err}  x  {clr_reset}{msg}")

def log_video(name,cur,tgt,tag="",col=""):
    pct=min(cur/tgt,1.)if tgt else 1.
    cur_s=str(int(cur)).rjust(len(str(int(tgt))))
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {grad_bar[0]}@  {clr_reset}{fmt_name(name)}  {fmt_bar(pct)}  {clr_dim}{cur_s}/{int(tgt)}s{clr_reset}")

def log_beat(name,cur,tgt,task,tag="",col=""):
    pct=min(cur/tgt,1.)if tgt else 1.
    rem=max(0,tgt-cur)
    left=(str(int(rem//60))+"m").rjust(4) if rem>=60 else (str(int(rem))+"s").rjust(4)
    cur_s=str(int(cur)).rjust(len(str(int(tgt))))
    p=f" {pfx(tag,col)}" if tag else ""
    print(f"{ts()}{p} {grad_bar[4]}>  {clr_reset}{fmt_name(name)}  {fmt_bar(pct)}  {clr_dim}{cur_s}/{int(tgt)}s  {left} left{clr_reset}")

base_dir    = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir,"config.json")
tokens_path = os.path.join(base_dir,"tokens.txt")

def load_config():
    if not os.path.exists(config_path):
        print(f"{clr_err}config.json not found{clr_reset}");sys.exit(1)
    return json.load(open(config_path,encoding="utf-8"))

def load_tokens():
    if not os.path.exists(tokens_path):
        print(f"{clr_err}tokens.txt not found{clr_reset}");sys.exit(1)
    toks=[l.strip() for l in open(tokens_path,encoding="utf-8") if l.strip()]
    if not toks:print(f"{clr_err}tokens.txt is empty{clr_reset}");sys.exit(1)
    return toks

cfg           = load_config()
all_tokens    = load_tokens()
timezone_str  = cfg.get("timezone","America/New_York")
locale        = cfg.get("locale","en-US")

desktop_ua      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Discord/1.0.9173 Chrome/132.0.6834.196 Electron/34.3.2 Safari/537.36"
api_base        = "https://discord.com/api/v9"
task_priority   = ["WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE","PLAY_ON_DESKTOP","PLAY_ON_DESKTOP_V2","STREAM_ON_DESKTOP","PLAY_ACTIVITY"]
heartbeat_tasks = {"PLAY_ON_DESKTOP","PLAY_ON_DESKTOP_V2","STREAM_ON_DESKTOP","PLAY_ACTIVITY"}
video_tasks     = {"WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE"}
skip_tasks      = {"ACHIEVEMENT_IN_ACTIVITY","ACHIEVEMENT_IN_GAME","PLAY_ON_XBOX","PLAY_ON_PLAYSTATION","progress"}

super_props = base64.b64encode(json.dumps({
    "os":"Windows","browser":"Discord Client","release_channel":"stable",
    "client_build_number":561532,"os_version":"10.0.22631","os_arch":"x64",
    "app_arch":"x64","system_locale":locale,"browser_user_agent":desktop_ua,
    "browser_version":"34.3.2","client_event_source":None,
},separators=(",",":")).encode()).decode()

def req_headers(token):
    return {
        "Authorization":token,"User-Agent":desktop_ua,
        "Content-Type":"application/json","X-Super-Properties":super_props,
        "X-Discord-Locale":locale,"X-Discord-Timezone":timezone_str,
    }

async def http_get(sess,path,token):
    async with sess.get(f"{api_base}{path}",headers=req_headers(token)) as r:
        data=await r.json()
        if r.status not in(200,204):raise Exception(f"{r.status}:{data}")
        return data

async def http_post(sess,path,body,token):
    async with sess.post(f"{api_base}{path}",headers=req_headers(token),json=body) as r:
        if r.status==204:return{}
        data=await r.json()
        if r.status not in(200,204):raise Exception(f"{r.status}:{data}")
        return data

def parse_ts(s):
    return 0.0 if not s else datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000+00:00")

def get_task(quest):
    cfg_q=quest["config"]
    tc=cfg_q.get("task_config_v2") or cfg_q.get("task_config")
    if not tc:return None,None
    if tc.get("type")==2:return None,None
    tasks=tc.get("tasks",{})
    for name in task_priority:
        if tasks.get(name) is not None:return name,tasks[name]
    available=[k for k in tasks.keys() if k not in skip_tasks]
    if available:return available[0],tasks[available[0]]
    return None,None

def user_status(quest):
    return quest.get("user_status") or {}

def get_progress(us,task):
    bt=(us.get("progress")or{}).get(task,{})
    if "value" in bt:return float(bt["value"])
    return 0.0

def split_quests(quest_list):
    now=time.time();enrolled=[];unenrolled=[]
    for q in quest_list:
        us=user_status(q);exp=q["config"].get("expires_at","");tt,_=get_task(q)
        if exp and parse_ts(exp)<=now:continue
        if bool(us.get("claimed_at")):continue
        if bool(us.get("completed_at")):continue
        if not tt:continue
        if bool(us.get("enrolled_at")):enrolled.append(q)
        else:unenrolled.append(q)
    return enrolled,unenrolled

async def run_video(sess,quest,task,task_data,token,tag,col):
    qid=quest["id"];name=quest["config"]["messages"]["quest_name"]
    us=user_status(quest);target=float(task_data.get("target",0))
    progress=get_progress(us,task)
    enrolled_ts=parse_ts(us.get("enrolled_at",""))
    if enrolled_ts==0.0:enrolled_ts=time.time()
    try:
        await http_post(sess,f"/quests/{qid}/video-progress",{"timestamp":0},token)
        await asyncio.sleep(1)
    except:pass
    log_video(name,progress,target,tag,col);done=False
    while not done and progress<target:
        if(time.time()-enrolled_ts)+10-progress>=7:
            nxt=min(target,progress+7+random.random())
            try:
                resp=await http_post(sess,f"/quests/{qid}/video-progress",{"timestamp":int(nxt)},token)
                progress=nxt;log_video(name,progress,target,tag,col)
                tp=(resp.get("progress")or{}).get(task,{})
                if tp.get("completed_at") is not None or progress>=target:done=True
            except Exception as e:log_err(f"{name}:{e}",tag,col)
        if not done:await asyncio.sleep(1)
    if not done:
        try:await http_post(sess,f"/quests/{qid}/video-progress",{"timestamp":int(target)},token)
        except Exception as e:log_err(f"{name}:{e}",tag,col)
    log_ok(f"{name}  {clr_dim}video complete{clr_reset}",tag,col)

async def run_heartbeat(sess,quest,task,task_data,token,tag,col):
    qid=quest["id"];name=quest["config"]["messages"]["quest_name"]
    us=user_status(quest);target=float(task_data.get("target",0))
    progress=get_progress(us,task);skey=f"call:{qid}:1"
    log_beat(name,progress,target,task,tag,col)
    while True:
        try:
            resp=await http_post(sess,f"/quests/{qid}/heartbeat",{"stream_key":skey,"terminal":False},token)
            prog_map=(resp.get("progress")or{})
            task_prog=prog_map.get(task,{})
            progress=float(task_prog.get("value",progress))
            log_beat(name,progress,target,task,tag,col)
            if progress>=target:
                await http_post(sess,f"/quests/{qid}/heartbeat",{"stream_key":skey,"terminal":True},token);break
        except Exception as e:log_err(f"{name}:{e}",tag,col)
        await asyncio.sleep(30)
    log_ok(f"{name}  {clr_dim}{task.replace('_',' ').lower()} complete{clr_reset}",tag,col)

async def run_account(token,tag,col):
    async with aiohttp.ClientSession() as sess:
        log_info("Fetching quests...",tag,col)
        try:
            resp=await http_get(sess,"/quests/@me",token)
        except Exception as e:
            log_err(f"Failed to fetch quests:{e}",tag,col);return
        quests=resp.get("quests",[])
        blocked_until=resp.get("quest_enrollment_blocked_until")
        if blocked_until:
            log_warn(f"Enrollment blocked until {blocked_until}",tag,col)
        enrolled,unenrolled=split_quests(quests)
        if unenrolled and not blocked_until:
            log_info(f"Auto-enrolling {len(unenrolled)} quest(s)...",tag,col)
            for q in unenrolled:
                qname=q["config"]["messages"]["quest_name"]
                try:
                    us=await http_post(sess,f"/quests/{q['id']}/enroll",{"location":11},token)
                    q["user_status"]=us if us else {"enrolled_at":now_iso(),"completed_at":None,"claimed_at":None,"progress":{}}
                    enrolled.append(q)
                    log_ok(f"Enrolled: {qname}",tag,col)
                except Exception as e:log_err(f"Could not enroll {qname}: {e}",tag,col)
            await asyncio.sleep(1)
        if not enrolled:log_warn("No eligible quests found",tag,col);return
        log_info(f"Running {clr_ok}{len(enrolled)}{clr_reset} quest(s) concurrently",tag,col)
        async def handle(quest):
            task,task_data=get_task(quest);name=quest["config"]["messages"]["quest_name"]
            if not task:
                log_warn(f"No automatable task for: {name}",tag,col);return
            try:
                if task in video_tasks:
                    await run_video(sess,quest,task,task_data,token,tag,col)
                elif task in heartbeat_tasks:
                    await run_heartbeat(sess,quest,task,task_data,token,tag,col)
                elif task in skip_tasks:
                    log_warn(f"Skipping server-validated task '{task}': {name}",tag,col)
                else:
                    log_warn(f"Unknown task type '{task}': {name}",tag,col)
            except Exception as e:log_err(f"{name}:{e}",tag,col)
        await asyncio.gather(*[handle(q) for q in enrolled])
        log_ok("All quests finished!",tag,col)

async def main():
    print(BANNER);account_map={}
    async def login(token,idx):
        col=grad_acct[idx%len(grad_acct)];client=discord.Client();ev=asyncio.Event()
        @client.event
        async def on_ready():
            tag=str(client.user).split("#")[0][:12]
            log_ok(f"Logged in as {col}{client.user}{clr_reset}  {clr_dim}({client.user.id}){clr_reset}",tag,col)
            account_map[token]=(tag,col,client);ev.set()
        async def try_start():
            try:
                await client.start(token)
            except discord.LoginFailure:
                preview=token[:16]+"..."
                log_err(f"Invalid token ({preview}), removing from tokens.txt")
                lines=[l.strip() for l in open(tokens_path,encoding="utf-8") if l.strip() and l.strip()!=token]
                open(tokens_path,"w",encoding="utf-8").write("\n".join(lines)+("\n" if lines else ""))
                ev.set()
            except Exception as e:
                log_err(f"Login error: {e}");ev.set()
        asyncio.create_task(try_start());await ev.wait()
    await asyncio.gather(*[login(t,i) for i,t in enumerate(all_tokens)])
    print()
    await asyncio.gather(*[run_account(tok,tag,col) for tok,(tag,col,_) in account_map.items()])
    for _,_,client in account_map.values():await client.close()

asyncio.run(main())
