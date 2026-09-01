# ♿ Echo — Discord Arabizi & Accessibility TTS Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.7+-blueviolet.svg)](https://github.com/Rapptz/discord.py)

**Echo** is an open-source, community-driven Discord Text-to-Speech (TTS) Accessibility bot. It is designed to empower visually impaired and blind users in Discord communities by reading text chat messages out loud in voice channels.

Specifically crafted for **Moroccan, North African, and Arabizi/3rabizi communities**, Echo includes an intelligent **3rabizi Transliteration Engine** that automatically converts number-substituted chat scripts (`7`, `kh`, `3`, `9`, `5`, `ch`) into authentic Arabic phonetic speech!

---

## 🌟 Key Features

* **♿ Accessible Voice Narration**: Speaks incoming text chat messages in real-time inside your Discord Voice channel.
* **🇲🇦 Arabizi / 3rabizi Transliteration Engine**: Real-time phonetic conversion for North African & Middle Eastern chat scripts:
  * `7` ➡️ `ح` *(e.g., "7bibi" ➔ "حبيبي")*
  * `kh` / `5` ➡️ `خ` *(e.g., "khoya" ➔ "خويا")*
  * `3` ➡️ `ع` *(e.g., "3afak" ➔ "عفاك")*
  * `9` ➡️ `ق` *(e.g., "9ahwa" ➔ "قهوة")*
  * `2` ➡️ `أ` *(e.g., "so2al" ➔ "سؤال")*
  * `ch` / `sh` ➡️ `ش` *(e.g., "choukrane" ➔ "شكران")*
* **🧠 Smart Speaker Tracking**: Prevents nickname spam when a user sends multiple messages in a row (reads *"User says..."* on the first message, and reads subsequent consecutive messages cleanly with natural pauses).
* **🌐 Multilingual Auto-Detection**: Automatically switches between Arabic (`ar`) and French (`fr`) for smooth Latin-script Darija pronunciation.
* **🔐 Discord DAVE E2EE Support**: Built on `discord.py 2.7+` with full support for Discord's new DAVE End-to-End Encrypted voice protocol (`davey` & `PyNaCl`).

---

## 🛠️ Prerequisites

Before running the bot, ensure you have:

1. **Python 3.10 or newer** installed on your system.
2. **FFmpeg** installed and added to your system PATH (required for audio playback in Discord voice channels).

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies

Clone this repository or download the source code:

```bash
git clone https://github.com/ridaounana/echo.git
cd echo
```

Install the required Python packages:

```bash
pip install "discord.py[voice]" gTTS PyNaCl davey
```

---

### 2. Set Up Your Discord Bot

1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)**.
2. Click **New Application** and give your bot a name (e.g., `Echo`).
3. Go to the **Bot** section on the left sidebar:
   * Click **Reset Token** and copy your **Bot Token**.
   * Scroll down to **Privileged Gateway Intents** and enable **Message Content Intent**.
4. Go to **OAuth2 > URL Generator**:
   * Select **`bot`** scope.
   * Select Bot Permissions: **View Channels**, **Send Messages**, **Read Message History**, **Connect**, **Speak**.
   * Copy the generated URL and open it in your browser to invite the bot to your server.

---

### 3. Run the Bot

Set your Discord Bot Token as an environment variable:

```bash
# PowerShell
$env:DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"

# Linux / macOS
export DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
```

Start the bot:

```bash
python discord_tts_bot.py
```

---

## 🎮 How to Use in Discord

| Command | Description |
| :--- | :--- |
| **`!join`** | Invites Echo into your current Voice Channel to start reading chat messages. |
| **`!leave`** | Disconnects Echo from the Voice Channel. |

---

## 🚀 Open Source Roadmap

We welcome contributions from developers worldwide! Future planned enhancements include:

- [ ] **Slash Command Integration**: Migrate from `!` prefixes to native `/join` and `/leave` slash commands.
- [ ] **Expanded Arabizi Dialects**: Add support for Levantine, Egyptian, and Gulf Arabizi variations.
- [ ] **Custom Voice Speed & Pitch Controls**: Allow users to adjust TTS reading speed (`slow` / `normal` / `fast`).
- [ ] **Web Dashboard**: Simple web UI to configure server-specific TTS settings.
- [ ] **Multi-server Sharding**: Scalable infrastructure for large communities.

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create! 

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

*Crafted with ❤️ for accessibility and the global Arabizi community.*
