# token_bot.py
# pip install discord.py
# 봇 토큰: MTU2NDI0NjE5NDY4NjAwNTMwOQ.GcFmSi.wzLHc4sMoed3cjPIgsxl09kWmqAgcB-13unJpQ

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

BOT_TOKEN = "MTU2NDI0NjE5NDY4NjAwNTMwOQ.GcFmSi.wzLHc4sMoed3cjPIgsxl09kWmqAgcB-13unJpQ"
TOKEN_FILE = "token.txt"          # 유저 토큰 저장 파일
DATA_FILE = "users.json"          # 유저별 기록

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_token_to_txt(token: str):
    # 셀프봇이 읽을 token.txt (한 줄에 하나, 최신 토큰이 맨 위)
    lines = []
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
    if token not in lines:
        lines.insert(0, token)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[흑룡회 공식봇] {bot.user} 온라인")
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 {len(synced)}개 동기화")
    except Exception as e:
        print("sync error:", e)

@bot.tree.command(name="토큰입력하기", description="셀프봇에 사용할 유저 토큰 등록")
@app_commands.describe(토큰="디스코드 유저 토큰")
async def token_input(interaction: discord.Interaction, 토큰: str):
    await interaction.response.defer(ephemeral=True)
    token = 토큰.strip()
    if len(token) < 50:
        await interaction.followup.send("토큰 형식이 이상합니다.", ephemeral=True)
        return

    uid = str(interaction.user.id)
    users = load_users()
    users[uid] = {
        "token": token,
        "name": str(interaction.user),
        "updated": datetime.now().isoformat()
    }
    save_users(users)
    save_token_to_txt(token)

    await interaction.followup.send(
        "토큰 저장 완료.\n"
        "token.txt에 기록됨 → 셀프봇이 이 토큰으로 동작합니다.\n"
        "토큰이 무효화되면 다시 `/토큰입력하기` 하세요.",
        ephemeral=True
    )

@bot.tree.command(name="토큰상태", description="내 토큰 등록 여부 확인")
async def token_status(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    users = load_users()
    if uid not in users:
        await interaction.response.send_message("등록된 토큰 없음. `/토큰입력하기` 사용.", ephemeral=True)
        return
    u = users[uid]
    await interaction.response.send_message(
        f"등록됨\n유저: {u.get('name')}\n마지막 수정: {u.get('updated')}",
        ephemeral=True
    )

@bot.tree.command(name="토큰삭제", description="내 토큰 삭제")
async def token_delete(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
    await interaction.response.send_message("삭제 완료.", ephemeral=True)

bot.run(BOT_TOKEN)
