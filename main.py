import os

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MainBot(commands.Bot):
    is_ready = False
    tts_channel_id = int(os.getenv("TTS_CHANNEL_ID"))
    tiktok_session_id = os.getenv("TIKTOK_SESSIONID")

bot = MainBot(command_prefix="|", intents=intents)


@bot.event
async def on_ready():
    print(f"Cargando cogs...")
    await bot.load_extension("cogs.tts_lector")
    await bot.load_extension("cogs.tts_voces")
    bot.is_ready = True
    print(f"Iniciado")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


bot.run(os.getenv("DISCORD_TOKEN"))
