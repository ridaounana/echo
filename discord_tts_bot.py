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

# Configure Discord Intents (members & voice_states required for role tracking)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Target Role Names for Auto-Assistance
TARGET_ROLE_NAMES = ["blind", "visually impaired", "accessibility", "mou3aq"]

# State tracking
last_speaker_id = None
last_speaker_timestamp = 0

def has_assistance_role(member):
    """Checks if a Discord member has a Blind / Visually Impaired accessibility role."""
    if not member or getattr(member, 'bot', False):
        return False
    
    roles = getattr(member, 'roles', [])
    return any(role.name.lower() in TARGET_ROLE_NAMES for role in roles)

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
        processed = text
        processed = re.sub(r'7', 'h', processed)
        processed = re.sub(r'3', 'a', processed)
        processed = re.sub(r'9', 'k', processed)
        processed = re.sub(r'5', 'kh', processed)
        return processed, 'fr'

@bot.event
async def on_ready():
    print(f"[ONLINE] Echo Auto-Assistance Accessibility Bot is online as: {bot.user}")
    print("Auto-Assistance Active: Tracking users with 'Blind' or 'Visually Impaired' roles!")

@bot.event
async def on_voice_state_update(member, before, after):
    """
    Auto-Assistance Engine with J2C (Join to Create) Protection:
    When a member with the 'Blind' role joins a voice channel, waits 1.5s for any
    Join-To-Create bot to move them into their final custom channel before following!
    """
    if member.bot or not has_assistance_role(member):
        return

    # User joined a channel or moved
    if after.channel is not None and (before.channel != after.channel):
        # Ignore initial Join To Create trigger channels
        channel_name_lower = after.channel.name.lower()
        if "join to create" in channel_name_lower or "j2c" in channel_name_lower:
            print(f"[AUTO-ASSIST] User clicked '{after.channel.name}'. Waiting 1.5s for J2C relocation...")
            await asyncio.sleep(1.5)

        # Re-fetch latest voice channel of the member after delay
        if not member.voice or not member.voice.channel:
            return

        final_channel = member.voice.channel
        
        # Don't join the generator channel if user is still in it for some reason
        if "join to create" in final_channel.name.lower() or "j2c" in final_channel.name.lower():
            return

        print(f"[AUTO-ASSIST] Following blind user '{member.display_name}' into final channel '{final_channel.name}'")

        guild = member.guild
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)

        if voice_client and voice_client.is_connected():
            if voice_client.channel != final_channel:
                await voice_client.move_to(final_channel)
        else:
            await final_channel.connect()

        # Update bot nickname to show assistance
        try:
            bot_member = guild.me
            await bot_member.edit(nick=f"Echo ♿ ({member.display_name})")
        except Exception as e:
            print(f"Nickname edit info: {e}")

    # Blind user left voice entirely
    elif after.channel is None and before.channel is not None:
        await asyncio.sleep(1.0)
        guild = member.guild
        voice_client = discord.utils.get(bot.voice_clients, guild=guild)
        
        if voice_client and voice_client.is_connected():
            current_channel = voice_client.channel
            remaining_assisted_users = [
                m for m in current_channel.members 
                if not m.bot and has_assistance_role(m)
            ]
            
            if not remaining_assisted_users:
                print(f"[AUTO-ASSIST] Disconnecting from '{current_channel.name}' (no remaining blind users)")
                await voice_client.disconnect()
                try:
                    bot_member = guild.me
                    await bot_member.edit(nick="Echo ♿")
                except Exception:
                    pass

@bot.command(name="join")
async def join_channel(ctx):
    """Join voice channel manually"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"🎙️ Joined **{channel.name}**! Echo Accessibility Active.")
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
