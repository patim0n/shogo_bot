import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")  # .env に TOKEN=xxxxx と書く

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

TITLE_FILE = "titles.json"

def load_titles():
    if os.path.exists(TITLE_FILE):
        with open(TITLE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_titles(data):
    with open(TITLE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_user_data(titles, user_id):
    if user_id not in titles:
        # defaultがあればそれをコピー
        if "default" in titles:
            titles[user_id] = {
                "b": titles["default"].get("b", []).copy(),
                "a": titles["default"].get("a", []).copy(),
                "current_b": "",
                "current_a": ""
            }
        else:
            titles[user_id] = {"b": [], "a": [], "current_b": "", "current_a": ""}

@tree.command(name="title-b", description="名前の前に付ける称号を確認・ランダム設定")
async def title_b(interaction: discord.Interaction):
    titles = load_titles()
    user_id = str(interaction.user.id)
    ensure_user_data(titles, user_id)

    if titles[user_id]["b"]:
        chosen = random.choice(titles[user_id]["b"])
        titles[user_id]["current_b"] = chosen
        save_titles(titles)
        await interaction.response.send_message(f"あなたの前称号は: **{chosen}** になりました。")
    else:
        await interaction.response.send_message("前に付ける称号がまだ登録されていません。/add-title-b で追加してください。")

@tree.command(name="title-a", description="名前の後に付ける称号を確認・ランダム設定")
async def title_a(interaction: discord.Interaction):
    titles = load_titles()
    user_id = str(interaction.user.id)
    ensure_user_data(titles, user_id)

    if titles[user_id]["a"]:
        chosen = random.choice(titles[user_id]["a"])
        titles[user_id]["current_a"] = chosen
        save_titles(titles)
        await interaction.response.send_message(f"あなたの後称号は: **{chosen}** になりました。")
    else:
        await interaction.response.send_message("後に付ける称号がまだ登録されていません。/add-title-a で追加してください。")

@tree.command(name="title-nick", description="称号付きの名前を表示")
async def title_nick(interaction: discord.Interaction):
    titles = load_titles()
    user_id = str(interaction.user.id)
    ensure_user_data(titles, user_id)

    b = titles[user_id]["current_b"]
    a = titles[user_id]["current_a"]
    name = interaction.user.display_name

    if b:
        full_name = f"''{b}{name}''{a}"
    else:
        full_name = f"{name}{a}"

    await interaction.response.send_message(f"あなたの称号付き名前は: **{full_name}** です！")

@tree.command(name="add-title-b", description="名前の前に付ける称号を追加")
@app_commands.describe(title="付けたい称号（例: 鋼の）")
async def add_title_b(interaction: discord.Interaction, title: str):
    titles = load_titles()
    user_id = str(interaction.user.id)
    ensure_user_data(titles, user_id)

    if title in titles[user_id]["b"]:
        await interaction.response.send_message("その称号は既に登録されています。", ephemeral=True)
        return

    titles[user_id]["b"].append(title)
    save_titles(titles)
    await interaction.response.send_message(f"称号「{title}」を前に付ける称号リストに追加しました。", ephemeral=True)

@tree.command(name="add-title-a", description="名前の後に付ける称号を追加")
@app_commands.describe(title="付けたい称号（例: 太郎）")
async def add_title_a(interaction: discord.Interaction, title: str):
    titles = load_titles()
    user_id = str(interaction.user.id)
    ensure_user_data(titles, user_id)

    if title in titles[user_id]["a"]:
        await interaction.response.send_message("その称号は既に登録されています。", ephemeral=True)
        return

    titles[user_id]["a"].append(title)
    save_titles(titles)
    await interaction.response.send_message(f"称号「{title}」を後に付ける称号リストに追加しました。", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} は起動しました。")

bot.run(TOKEN)
