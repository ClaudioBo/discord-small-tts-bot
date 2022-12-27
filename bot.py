import os

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from gtts import gTTS

import utils

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

is_ready = False

bot = commands.Bot(command_prefix="*", intents=intents)


@bot.event
async def on_ready():
    global is_ready
    print(f"{bot.user} successfully connected to Discord.")
    is_ready = True


@bot.event
async def on_message(message):
    if not is_ready:
        print(f"Not ready")
        return

    ctx = await bot.get_context(message)
    
    if ctx.channel.id != 978057613554098257:
        return

    text = message.content

    if "shh" in text.lower():
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
            await message.add_reaction("😶")
        return

    if not text:
        print(f"Ao {ctx.author.mention}, give me something to say first!")
        return
    
    if not utils.check_text(text):
        return

    if not utils.get_sender_vc(ctx):
        print(f"not connected")
        return

    vc = await utils.connect_vc_of_author(ctx)

    file_name = "tts.mp3"
    tts = gTTS(text=text, lang="es", tld="com.mx", slow=True)
    tts.save(file_name)

    try:
        vc.play(discord.FFmpegPCMAudio(file_name))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 1
    finally:
        pass


@bot.command(name="disconnect")
async def disconnect(ctx):
    vc = ctx.voice_client
    if not vc:
        print("I'm not in a voice channel!")
        return

    await vc.disconnect()
    print("I have left the voice channel, bb")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

bot.run(os.getenv("DISCORD_TOKEN"))
