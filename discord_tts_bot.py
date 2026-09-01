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

# State tracking for consecutive messages by the same user
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

def detect_and_process_text(text):
    """
    Detects if text contains Arabizi/Arabic or French, and returns (processed_text, lang_code).
    """
    is_arabizi_or_arabic = bool(
        re.search(r'[\u0600-\u06FF]', text) or 
        re.search(r'\bkh\b|7|3|9|5|2', text, re.IGNORECASE)
    )

    if is_arabizi_or_arabic:
        arabic_text = convert_arabizi_to_arabic(text)
        return arabic_text, 'ar'
    else:
        return text, 'fr'

@bot.event
async def on_ready():
    print(f"[ONLINE] Echo Accessibility TTS Bot is online as: {bot.user}")
    print("Bot is ready with Arabizi Engine (7=ح, kh=خ, 3=ع, 9=ق)!")

@bot.command(name="join")
async def join_channel(ctx):
    """Join the voice channel of the user who typed !join"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined voice channel: **{channel.name}**. Echo 3rabizi Engine Active (7=ح, kh=خ)!")
    else:
        await ctx.send("You need to be in a voice channel first so I can join you!")

@bot.command(name="leave")
async def leave_channel(ctx):
    """Leave the current voice channel"""
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
        
        processed_content, msg_lang = detect_and_process_text(message.content)
        intro = "يقول:" if msg_lang == 'ar' else "a dit:"

        if last_speaker_id == message.author.id and (now - last_speaker_timestamp) < 30:
            text_to_speech = processed_content
        else:
            text_to_speech = f"{message.author.display_name} {intro} {processed_content}"
        
        last_speaker_id = message.author.id
        last_speaker_timestamp = now

        print(f"[{msg_lang.upper()}] Reading: {text_to_speech.encode('utf-8', 'ignore').decode('utf-8')}")

        tts_filename = f"tts_{message.id}.mp3"
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
        print("Please set the DISCORD_BOT_TOKEN environment variable or put your token in BOT_TOKEN!")
    else:
        bot.run(BOT_TOKEN)
