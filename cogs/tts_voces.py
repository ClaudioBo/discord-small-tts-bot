import discord
from discord.ext import commands

from utils import tts
from utils.database import Connection


class TTSVoces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def voces(self, ctx):
        output = "Escribe el nombre de la voz con el comando `|set_voz <motor> <voz>`\n"
        output += "Ejemplo: `|set_voz tiktok es_mx_002`\n\n"
        output += "Lista de voces disponibles:\n"
        output += "```yml\n"
        for motor in tts.available_voices:
            output += f"{motor}:\n"
            for voices in tts.available_voices[motor]:
                output += f"- {voices[0]}: {voices[1]}\n"
            output += f"\n"
        output += "```"
        await ctx.send(output)

    @commands.command()
    async def set_voz(self, ctx, engine: str = None, voice: str = None):
        if not engine:
            await ctx.send(f"{ctx.message.author.mention} debes especificar un motor")
            return

        if not voice:
            await ctx.send(f"{ctx.message.author.mention} debes especificar una voz")
            return
        
        if not engine in tts.available_voices:
            await ctx.send(f"{ctx.message.author.mention} motor no encontrado")
            return

        if not voice in [uno[0] for uno in tts.available_voices[engine]]:
            await ctx.send(f"{ctx.message.author.mention} voz no encontrada")
            return
            

        with Connection() as db:
            db.set_user_voice(ctx.message.author.id, engine.lower(), voice.lower())
            await ctx.send(f"{ctx.message.author.mention} estableci tu voz a `{voice}` con el motor `{engine}`")


async def setup(bot):
    await bot.add_cog(TTSVoces(bot))
    print("'TTSVoces' registrado")
