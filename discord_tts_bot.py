import discord
from discord.ext import commands
import edge_tts
import os
import asyncio
import time
import re
import sys

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# Configure Discord Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Supported AI Neural Voices
VOICES = {
    "jamal": "ar-MA-JamalNeural",     # Moroccan Male
    "mouna": "ar-MA-MounaNeural",     # Moroccan Female
    "salma": "ar-EG-SalmaNeural",     # Egyptian Female
    "denise": "fr-FR-DeniseNeural",   # French Female
}

# Channel/Server settings tracking
server_voices = {}              # guild_id -> voice_name
last_speaker_id = None
last_speaker_timestamp = 0

def convert_arabizi_to_arabic(text):
    """
    Converts Moroccan Arabizi / Franco-Arabic numbers & letters to Arabic characters:
    - 7 -> ح
    - kh / 5 -> خ
    - 3 -> ع
    - 9 -> ق
    - 2 -> أ
    - ch / sh -> ش
    """
    text = re.sub(r'kh|KH|Kh', 'خ', text)
    text = re.sub(r'ch|CH|Ch|sh|SH|Sh', 'ش', text)
    text = re.sub(r'7', 'ح', text)
    text = re.sub(r'3', 'ع', text)
    text = re.sub(r'9', 'ق', text)
    text = re.sub(r'5', 'خ', text)
    text = re.sub(r'2', 'أ', text)
    return text

def process_text_for_tts(text):
    """
    Checks if text has Arabizi or Arabic characters and converts them.
    """
    is_arabizi_or_arabic = bool(
        re.search(r'[\u0600-\u06FF]', text) or 
        re.search(r'\bkh\b|7|3|9|5|2', re.IGNORECASE)
    )

    if is_arabizi_or_arabic:
        return convert_arabizi_to_arabic(text), True
    return text, False

@bot.event
async def on_ready():
    print(f"[ONLINE] Echo AI Neural TTS Bot is online as: {bot.user}")
    print("Available AI Neural Voices: Jamal (ar-MA), Salma (ar-EG), Mouna (ar-MA), Denise (fr-FR)")

@bot.command(name="join")
async def join_channel(ctx, voice_choice: str = "jamal"):
    """Join voice channel with chosen voice: !join Jamal, !join Salma, !join Mouna"""
    voice_key = voice_choice.lower()
    if voice_key not in VOICES:
        await ctx.send(f"⚠️ Voice '{voice_choice}' not found! Available options: **Jamal** (Moroccan), **Salma** (Egyptian), **Mouna** (Moroccan), **Denise** (French).")
        voice_key = "jamal"

    server_voices[ctx.guild.id] = VOICES[voice_key]

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"🎙️ Joined **{channel.name}** using **{voice_key.capitalize()}** voice (`{VOICES[voice_key]}`)!")
    else:
        await ctx.send("⚠️ You need to be in a voice channel first so I can join you!")

@bot.command(name="voice")
async def switch_voice(ctx, voice_choice: str):
    """Switch AI Neural Voice on the fly: !voice Salma or !voice Jamal"""
    voice_key = voice_choice.lower()
    if voice_key in VOICES:
        server_voices[ctx.guild.id] = VOICES[voice_key]
        await ctx.send(f"🔊 Switched voice to **{voice_key.capitalize()}** (`{VOICES[voice_key]}`)!")
    else:
        await ctx.send(f"⚠️ Unknown voice '{voice_choice}'. Options: **Jamal**, **Salma**, **Mouna**, **Denise**.")

@bot.command(name="leave")
async def leave_channel(ctx):
    """Leave current voice channel"""
    global last_speaker_id, last_speaker_timestamp
    last_speaker_id = None
    last_speaker_timestamp = 0
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")

@bot.event
async def on_message(message):
    global last_speaker_id, last_speaker_timestamp

    await bot.process_commands(message)

    if message.author.bot or message.content.startswith("!"):
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    if voice_client and voice_client.is_connected():
        now = time.time()
        
        # Get selected voice for this server (default: Jamal)
        selected_voice = server_voices.get(message.guild.id, VOICES["jamal"])

        processed_content, is_arabic = process_text_for_tts(message.content)
        intro = "يقول:" if is_arabic else "a dit:"

        if last_speaker_id == message.author.id and (now - last_speaker_timestamp) < 30:
            text_to_speech = processed_content
        else:
            text_to_speech = f"{message.author.display_name} {intro} {processed_content}"
        
        last_speaker_id = message.author.id
        last_speaker_timestamp = now

        print(f"[{selected_voice}] Reading: {text_to_speech.encode('utf-8', 'ignore').decode('utf-8')}")

        tts_filename = f"tts_{message.id}.mp3"
        
        # Generate neural audio using Edge-TTS
        communicate = edge_tts.Communicate(text_to_speech, selected_voice)
        await communicate.save(tts_filename)

        while voice_client.is_playing():
            await asyncio.sleep(0.3)

        def after_playing(error):
            if os.path.exists(tts_filename):
                try:
                    os.remove(tts_filename)
                except Exception:
                    pass

        audio_source = discord.FFmpegPCMAudio(tts_filename)
        voice_client.play(audio_source, after=after_playing)

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
    
    if BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        # Check if local token file exists
        token_file = "token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                BOT_TOKEN = f.read().strip()
    
    if BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("Please set your DISCORD_BOT_TOKEN environment variable or save it in token.txt!")
    else:
        bot.run(BOT_TOKEN)
