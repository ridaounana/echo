import discord
from discord.ext import commands
from gtts import gTTS
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

# State tracking
last_speaker_id = None
last_speaker_timestamp = 0

def preprocess_moroccan_text(text):
    """
    Preprocesses text for Moroccan users:
    - If message contains Arabic characters -> Use Arabic voice ('ar')
    - If message contains Latin text (e.g., 'salam khoya', 'ach kat3awd', 'cv labas') -> Use French voice ('fr')
    """
    has_arabic_script = bool(re.search(r'[\u0600-\u06FF]', text))

    if has_arabic_script:
        return text, 'ar'
    else:
        # Convert 3rabizi numbers into French-phonetic equivalents for smooth Latin Darija reading
        processed = text
        processed = re.sub(r'7', 'h', processed)
        processed = re.sub(r'3', 'a', processed)
        processed = re.sub(r'9', 'k', processed)
        processed = re.sub(r'5', 'kh', processed)
        return processed, 'fr'

@bot.event
async def on_ready():
    print(f"[ONLINE] Echo Original Moroccan TTS Bot is online as: {bot.user}")
    print("Engine: Classic gTTS (French for Latin Darija 'salam khoya' & Arabic for Arabic script)")

@bot.command(name="join")
async def join_channel(ctx):
    """Join voice channel"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"🎙️ Joined **{channel.name}**! Classic Moroccan TTS Active (Latin Darija + Arabic).")
    else:
        await ctx.send("⚠️ You need to be in a voice channel first so I can join you!")

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

        processed_content, msg_lang = preprocess_moroccan_text(message.content)
        intro = "يقول:" if msg_lang == 'ar' else "a dit:"

        if last_speaker_id == message.author.id and (now - last_speaker_timestamp) < 30:
            text_to_speech = processed_content
        else:
            text_to_speech = f"{message.author.display_name} {intro} {processed_content}"
        
        last_speaker_id = message.author.id
        last_speaker_timestamp = now

        print(f"[{msg_lang.upper()}] Original: '{message.content}' -> Reading: {text_to_speech.encode('utf-8', 'ignore').decode('utf-8')}")

        tts_filename = f"tts_{message.id}.mp3"
        
        # Original gTTS Engine
        tts = gTTS(text=text_to_speech, lang=msg_lang, slow=False)
        tts.save(tts_filename)

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
        token_file = "token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                BOT_TOKEN = f.read().strip()
    
    if BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("Please set your DISCORD_BOT_TOKEN environment variable or save it in token.txt!")
    else:
        bot.run(BOT_TOKEN)
