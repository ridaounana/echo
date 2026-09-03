import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import time
import re
import sys

# Ensure UTF-8 output on Windows terminal, and flush every line immediately -
# stdout is block-buffered when piped to a log file (e.g. under PM2), which was
# hiding several minutes of print() output during debugging on the VPS.
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

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

# Per-guild TTS playback queues, each drained by a single dedicated worker task.
# Playback used to be serialized by having every on_message call busy-poll
# voice_client.is_playing() in its own loop - with several messages arriving close
# together, two of those loops could both observe "not playing" at the same instant
# and race on voice_client.play(), so only one ever actually got spoken. Routing
# every message through one queue per guild removes that race entirely.
guild_tts_queues = {}
guild_tts_workers = {}

async def tts_queue_worker(guild_id):
    queue = guild_tts_queues[guild_id]
    while True:
        voice_client, tts_filename = await queue.get()
        try:
            if voice_client and voice_client.is_connected():
                done = asyncio.Event()

                def after_playing(error, _done=done, _file=tts_filename):
                    if error:
                        print(f"[PLAYBACK ERROR] {error}")
                    if os.path.exists(_file):
                        try:
                            os.remove(_file)
                        except Exception:
                            pass
                    bot.loop.call_soon_threadsafe(_done.set)

                voice_client.play(discord.FFmpegPCMAudio(tts_filename), after=after_playing)
                await done.wait()
            elif os.path.exists(tts_filename):
                os.remove(tts_filename)
        except Exception as e:
            print(f"[TTS QUEUE ERROR] {e}")
        finally:
            queue.task_done()

def has_assistance_role(member):
    """Checks if a Discord member has a Blind / Visually Impaired accessibility role."""
    if not member or getattr(member, 'bot', False):
        return False
    
    roles = getattr(member, 'roles', [])
    return any(role.name.lower() in TARGET_ROLE_NAMES for role in roles)

# Arabizi (digit-substituted Darija) -> real Arabic script, longest patterns first so
# digraphs like "kh"/"gh"/"ch" are consumed before their single-letter components are.
# gTTS's French voice has no phoneme for the consonants some of these digits stand in for
# (hamza, ayn, khe, 7a, ghain, qaf don't exist in French), so "7" was previously rewritten
# to the Latin letter 'h' and read as a silent/weak French h instead of the intended sound.
# Routing the whole message through real Arabic script + the Arabic voice instead lets that
# voice produce the actual phonemes. Spelling won't always be textbook-correct (short vowels
# aren't elided the way a human writer would), but it's phonetically far closer.
_ARABIZI_TO_ARABIC_RULES = [
    (r"3['\u2019]", '\u063A'),
    (r'kh', '\u062E'), (r'gh', '\u063A'), (r'ch', '\u0634'), (r'sh', '\u0634'), (r'dh', '\u0630'), (r'th', '\u062B'), (r'ou', '\u0648'),
    (r'8', '\u063A'), (r'7', '\u062D'), (r'9', '\u0642'), (r'5', '\u062E'), (r'3', '\u0639'), (r'2', '\u0621'),
    (r'b', '\u0628'), (r't', '\u062A'), (r'j', '\u062C'), (r'd', '\u062F'), (r'r', '\u0631'), (r'z', '\u0632'), (r's', '\u0633'),
    (r'f', '\u0641'), (r'q', '\u0642'), (r'k', '\u0643'), (r'l', '\u0644'), (r'm', '\u0645'), (r'n', '\u0646'), (r'h', '\u0647'),
    (r'w', '\u0648'), (r'y', '\u064A'), (r'a', '\u0627'), (r'i', '\u064A'), (r'o', '\u0648'), (r'u', '\u0648'), (r'e', ''),
]
_ARABIZI_TO_ARABIC_RE = re.compile('|'.join(f'({p})' for p, _ in _ARABIZI_TO_ARABIC_RULES), re.IGNORECASE)
_ARABIZI_TO_ARABIC_REPLACEMENTS = [r for _, r in _ARABIZI_TO_ARABIC_RULES]

def transliterate_arabizi_to_arabic(text):
    def repl(match):
        for i, group in enumerate(match.groups()):
            if group is not None:
                return _ARABIZI_TO_ARABIC_REPLACEMENTS[i]
        return match.group(0)
    return _ARABIZI_TO_ARABIC_RE.sub(repl, text)

def preprocess_moroccan_text(text):
    """
    Preprocesses text for Moroccan users:
    - If message contains Arabic characters -> Use Arabic voice ('ar')
    - If message contains Arabizi digits (7/3/9/5/8/2/3') -> transliterate to Arabic script -> Use Arabic voice ('ar')
    - Otherwise (plain Latin text, e.g. English/French) -> Use French voice ('fr') unchanged
    """
    if re.search(r'[\u0600-\u06FF]', text):
        return text, 'ar'

    if re.search(r'[235789]', text):
        return transliterate_arabizi_to_arabic(text), 'ar'

    return text, 'fr'

def resolve_discord_syntax(message):
    """
    Replaces raw Discord markup (<@id> mentions, <#id> channels, <a:name:id> emoji) with
    human-readable text, so TTS reads names instead of garbled numeric snowflake IDs
    (which also protects those digits from the Arabizi digit transliteration below).
    """
    content = message.content

    for user in message.mentions:
        content = re.sub(rf'<@!?{user.id}>', f'@{user.display_name}', content)
    for role in message.role_mentions:
        content = re.sub(rf'<@&{role.id}>', f'@{role.name}', content)
    for channel in message.channel_mentions:
        content = re.sub(rf'<#{channel.id}>', f'#{channel.name}', content)

    content = re.sub(r'<a?:(\w+):\d+>', r':\1:', content)

    return content

@bot.event
async def on_ready():
    print(f"[ONLINE] Echo Auto-Assistance Accessibility Bot is online as: {bot.user}")
    print("Auto-Assistance Active: Tracking users with 'Blind' or 'Visually Impaired' roles!")

@bot.event
async def on_voice_state_update(member, before, after):
    """
    Auto-Assistance Engine with J2C Protection:
    When a member with the 'Blind' role joins a voice channel, waits 1.5s for any
    Join-To-Create bot to move them into their final custom channel before following!
    Renames bot to '[Username] ECHO'.
    """
    if member.bot or not has_assistance_role(member):
        return

    # User joined a channel or moved
    if after.channel is not None and (before.channel != after.channel):
        channel_name_lower = after.channel.name.lower()
        if "join to create" in channel_name_lower or "j2c" in channel_name_lower:
            print(f"[AUTO-ASSIST] User clicked '{after.channel.name}'. Waiting 1.5s for J2C relocation...")
            await asyncio.sleep(1.5)

        if not member.voice or not member.voice.channel:
            return

        final_channel = member.voice.channel
        
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

        # Update bot nickname in the server to '[Username] ECHO'
        try:
            bot_member = guild.me
            new_nickname = f"{member.display_name} ECHO"
            print(f"[NICKNAME] Renaming bot to '{new_nickname}' in server '{guild.name}'")
            await bot_member.edit(nick=new_nickname)
        except Exception as e:
            print(f"[NICKNAME ERROR] {e}")

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
                    await bot_member.edit(nick="Echo")
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
        author_voice_channel = getattr(message.author.voice, 'channel', None)
        is_same_voice_channel = (author_voice_channel == voice_client.channel)
        is_voice_chat_text_channel = (message.channel.id == voice_client.channel.id)

        if not (is_same_voice_channel or is_voice_chat_text_channel):
            print(f"[SKIP] '{message.author}' message ignored - not in bot's voice channel ({message.channel})")
            return

        now = time.time()

        processed_content, msg_lang = preprocess_moroccan_text(resolve_discord_syntax(message))
        intro = "يقول:" if msg_lang == 'ar' else "a dit:"

        if last_speaker_id == message.author.id and (now - last_speaker_timestamp) < 30:
            text_to_speech = processed_content
        else:
            text_to_speech = f"{message.author.display_name} {intro} {processed_content}"

        last_speaker_id = message.author.id
        last_speaker_timestamp = now

        print(f"[{msg_lang.upper()}] Original: '{message.content}' -> Reading: {text_to_speech.encode('utf-8', 'ignore').decode('utf-8')}")

        tts_filename = f"tts_{message.id}.mp3"

        try:
            # gTTS.save() blocks on a network call to Google; running it in a thread
            # keeps the bot's event loop (and every other guild/message) responsive
            # instead of freezing the whole bot for the duration of the request.
            await asyncio.to_thread(gTTS(text=text_to_speech, lang=msg_lang, slow=False).save, tts_filename)
        except Exception as e:
            print(f"[TTS GENERATION ERROR] {e}")
            return

        if message.guild.id not in guild_tts_queues:
            guild_tts_queues[message.guild.id] = asyncio.Queue()
            guild_tts_workers[message.guild.id] = bot.loop.create_task(tts_queue_worker(message.guild.id))

        await guild_tts_queues[message.guild.id].put((voice_client, tts_filename))

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        token_file = "token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                BOT_TOKEN = f.read().strip()
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("Please set your DISCORD_BOT_TOKEN environment variable or save it in token.txt!")
    else:
        bot.run(BOT_TOKEN)
