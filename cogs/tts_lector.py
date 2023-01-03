import os
import string
import random
import asyncio
import traceback
import discord
from discord.ext import commands, tasks

from utils import general, tts
from utils.database import Connection


class TTSLector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LETTERS = string.ascii_letters
        self.voice_client = None
        self.current_idle_time = None
        self.max_idle_time = 60 * 30

        self.audio_queue = []
        self.is_deletable = False
        self.is_enabled = True

        self.idle_tick.start()
        asyncio.create_task(self.player_loop())

    def cog_unload(self):
        self.is_enabled = False
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
            await ctx.send(f"{ctx.author.mention}, bueno me calló pues 😠")
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
            self.voice_client = vc
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

        if not engine in tts.available_voices:
            with Connection() as db:
                db.set_user_voice(ctx.message.author.id, "tiktok", "es_mx_002")
            engine = "tiktok"
            voice = "es_mx_002"

        if not voice in [uno[0] for uno in tts.available_voices[engine]]:
            with Connection() as db:
                db.set_user_voice(ctx.message.author.id, "tiktok", "es_mx_002")
            engine = "tiktok"
            voice = "es_mx_002"

        # Nombre aleatorio
        nombre_archivo = "temp/" + ("".join(random.choice(self.LETTERS) for i in range(32))) + ".mp3"

        # Ejecutar modulo dependiendo del motor
        if engine == "tiktok":
            if not tts.generate_tiktok(self.bot.tiktok_session_id, text, nombre_archivo, voice):
                await ctx.send(f"{ctx.author.mention}, tiktok nos mando alv")
                return
        elif engine == "gtts":
            tts.generate_gtts(voice, text, nombre_archivo)

        self.audio_queue.append(nombre_archivo)
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

    async def player_loop(self):
        while self.is_enabled:
            await asyncio.sleep(0.1)

            if not self.voice_client:
                continue

            if not self.voice_client.is_playing():
                if self.is_deletable:
                    self.audio_queue.pop(0)
                    self.is_deletable = False
                    os.remove(current_mp3)

                if not self.audio_queue:
                    continue

                current_mp3 = self.audio_queue[0]
                try:
                    self.voice_client.play(discord.FFmpegPCMAudio(current_mp3), after=self.after_play)
                    self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
                    self.voice_client.source.volume = 0.1
                except:
                    print(f"[ERROR] No se pudo reproducir {current_mp3}:")
                    traceback.print_exc()
                    self.is_deletable = True

    def after_play(self, error=None):
        self.is_deletable = True


async def setup(bot):
    await bot.add_cog(TTSLector(bot))
    print("'TTSLector' registrado")
