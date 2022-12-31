import base64
import os

import discord
import requests
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

bot = commands.Bot(command_prefix="|", intents=intents)
channel_id = int(os.getenv("CHANNEL_ID"))


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

    global channel_id
    if ctx.channel.id != channel_id:
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
    # generate_gtts(text)
    if not generate_tiktok(text):
        await message.add_reaction("💀")
        return

    try:
        vc.play(discord.FFmpegPCMAudio("tts.mp3"))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 1
    except:
        await message.add_reaction("🙅‍♂️")

def generate_gtts(text):
    tts = gTTS(text=text, lang="es", tld="com.mx", slow=True)
    tts.save("tts.mp3")

def generate_tiktok(text):
    voice = "es_mx_002"
    text = text.replace("+", "mas")
    text = text.replace(" ", "+")
    text = text.replace("&", "y")

    headers = {
        'User-Agent': 'com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)',
        'Cookie': f'sessionid={os.getenv("TIKTOK_SESSIONID")}'
    }
    url = f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker={voice}&req_text={text}&speaker_map_type=0&aid=1233"

    r = requests.post(url, headers=headers)
    if r.json()["message"] == "Couldn't load speech. Try again.":
        return False
    
    vstr = [r.json()["data"]["v_str"]][0]
    b64d = base64.b64decode(vstr)
    with open("tts.mp3", "wb") as out:
        out.write(b64d)

    return True

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
