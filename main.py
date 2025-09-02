import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import asyncio
import logging

# -----------------------------
# Load token and setup logging
# -----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")

# -----------------------------
# YTDL / FFMPEG Options
# -----------------------------
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch1',  # search and take first video
    'noplaylist': True,
    'ignoreerrors': True
}

ffmpeg_options = {
    'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_at_eof 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# -----------------------------
# Queue and loop state
# -----------------------------
song_queues = {}  # {guild_id: [YTDLSource, ...]}
loop_flags = {}   # {guild_id: True/False}

# -----------------------------
# YTDLSource Class
# -----------------------------
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_query(cls, query, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=not stream))
            print("yt_dlp returned:", data)
        except Exception as e:
            print("yt_dlp extraction error:", e)
            return None

        if not data:
            return None

        if 'entries' in data and len(data['entries']) > 0:
            data = data['entries'][0]

        url = data.get('url')
        if not url:
            print("❌ yt_dlp did not return a streamable URL")
            return None

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options), data=data)

# -----------------------------
# Helper to play next song
# -----------------------------
async def play_next(ctx):
    guild_id = ctx.guild.id
    if guild_id not in song_queues or len(song_queues[guild_id]) == 0:
        await ctx.voice_client.disconnect()
        return

    if loop_flags.get(guild_id, False):
        song = song_queues[guild_id][0]  # Keep current song if loop enabled
    else:
        song = song_queues[guild_id].pop(0)

    ctx.voice_client.play(
        song,
        after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
    )
    await ctx.send(f'🎶 Now cooking: **{song.title}**')

# -----------------------------
# Basic Commands
# -----------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"✅ Joined **{channel}**")
        else:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"🔄 Moved to **{channel}**")
    else:
        await ctx.send("❌ You are not in a voice channel, lil bro")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Bye lil bro!")
        # Clear the queue and loop flag
        guild_id = ctx.guild.id
        song_queues.pop(guild_id, None)
        loop_flags.pop(guild_id, None)
    else:
        await ctx.send("❌ I'm not connected to a voice channel")

# -----------------------------
# Play Command with Queue
# -----------------------------
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("❌ Join a voice channel first, lil bro")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await ctx.send(f"🔎 Trying to cook in {channel}...")
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔄 Moved to keep cooking in {channel}")

    async with ctx.typing():
        player = await YTDLSource.from_query(search, loop=bot.loop, stream=True)
        if not player:
            await ctx.send("❌ Could not find a valid video for that search or URL.")
            return

        guild_id = ctx.guild.id
        if guild_id not in song_queues:
            song_queues[guild_id] = []

        song_queues[guild_id].append(player)

        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        else:
            await ctx.send(f"➕ Ordered up: **{player.title}**")

# -----------------------------
# Loop Command
# -----------------------------
@bot.command()
async def loop(ctx):
    guild_id = ctx.guild.id
    loop_flags[guild_id] = not loop_flags.get(guild_id, False)
    state = "enabled 🔁" if loop_flags[guild_id] else "disabled ⏹"
    await ctx.send(f"Repeatedly cooking is now {state}")

# -----------------------------
# Queue Command
# -----------------------------
@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in song_queues or len(song_queues[guild_id]) == 0:
        await ctx.send("❌ The order is empty.")
        return

    msg = "🎵 **Queue:**\n"
    for i, song in enumerate(song_queues[guild_id], start=1):
        msg += f"{i}. {song.title}\n"
    await ctx.send(msg)

# -----------------------------
# Run Bot
# -----------------------------
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)