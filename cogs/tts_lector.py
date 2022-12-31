import discord
from discord.ext import commands, tasks

from utils import general, tts
from utils.database import Connection


class TTSLector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_idle_time = None
        self.max_idle_time = 60*30
        self.idle_tick.start()

    def cog_unload(self):
        self.idle_tick.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)

        # Pre-condicion: Solo el canal de texto especificado
        if ctx.channel.id != self.bot.tts_channel_id:
            return

        # Pre-condicion: Ignorar mensajes de bot
        if ctx.message.author.bot:
            return

        # Pre-condicion: No hay texto
        text = message.content
        if not text:
            return

        # Pre-condicion: Silenciar el bot
        if "shh" in text.lower():
            vc = ctx.voice_client
            if vc:
                await vc.disconnect()
                await message.add_reaction("👌")
            await ctx.send(f"{ctx.author.mention}, me silenciaste 😠")
            return

        # Pre-condicion: No hay texto
        if not general.check_text(text):
            return

        # Pre-condicion: Debe estar en un VC
        if not general.get_sender_vc(ctx):
            await ctx.send(f"{ctx.author.mention}, no estas en un canal de voz")
            return

        try:
            vc = await general.connect_vc_of_author(ctx)
        except:
            try:
                await ctx.send(f"{ctx.author.mention}, tuve pedillos para unirme a tu canal de voz")
            except:
                pass
            return

        # Obtener motor y voz seleccionada, o defaultear la del Tiktok
        engine = "tiktok"
        voice = "es_mx_002"
        with Connection() as db:
            selected = db.get_user_voice(ctx.author.id)
            if selected:
                engine, voice = selected

        # Ejecutar modulo dependiendo del motor
        if engine == "tiktok":
            if not tts.generate_tiktok(self.bot.tiktok_session_id, text, voice):
                await message.add_reaction("☹")
                await ctx.send(f"{ctx.author.mention}, me quitaron la voz")
                return
        elif engine == "gtts":
            tts.generate_gtts(voice, text)

        # Reproducir mp3
        try:
            vc.play(discord.FFmpegPCMAudio("tts.mp3"))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 1
        except:
            await ctx.send(f"{ctx.author.mention}, no puedo reproducir esa madre")
        self.current_idle_time = 1

    @tasks.loop(seconds=1.0)
    async def idle_tick(self):
        if not self.current_idle_time:
            return
        self.current_idle_time += 1
        if self.current_idle_time == self.max_idle_time:
            if not self.bot.voice_clients:
                return
            for vcs in self.bot.voice_clients:
                await vcs.disconnect()
            self.current_idle_time = None
            print("Desconexion de VC por inactividad")

async def setup(bot):
    await bot.add_cog(TTSLector(bot))
    print("'TTSLector' registrado")
