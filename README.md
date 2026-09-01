# ♿ Echo — Discord Arabizi & Accessibility TTS Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.7+-blueviolet.svg)](https://github.com/Rapptz/discord.py)

**Echo** is an open-source, community-driven Discord Text-to-Speech (TTS) Accessibility bot. It is designed to empower visually impaired and blind users in Discord communities by reading text chat messages out loud in voice channels.

Specifically crafted for **Moroccan, North African, and Arabizi/3rabizi communities**, Echo features **Automatic Role-Based Assistance** and an intelligent **3rabizi Transliteration Engine** that automatically converts number-substituted chat scripts (`7`, `kh`, `3`, `9`, `5`, `ch`) into authentic phonetic speech!

---

## 🌟 Key Features

* **♿ Hands-Free Auto-Assistance**: Automatically detects when a user with the **`Blind`** or **`Visually Impaired`** role joins any Voice Channel in your server:
  * **Auto-Follow**: Automatically follows the user into whichever Voice Channel they join or move to.
  * **Auto-Rename**: Renames the bot in the server to **`Echo ♿ (Assisting Username)`** to provide full transparency to server members.
  * **Auto-Disconnect**: Automatically leaves when all visually impaired users leave voice channels.
* **🇲🇦 Arabizi / 3rabizi Transliteration Engine**: Real-time phonetic conversion for North African & Middle Eastern chat scripts (`salam khoya`, `ach kat3awd`, `cv labas`).
* **🧠 Smart Speaker Tracking**: Reads *"Username says..."* on the first message, and reads subsequent consecutive messages from the same user cleanly with natural pauses without repeating the username.
* **🔐 Discord DAVE E2EE Support**: Built on `discord.py 2.7+` with full support for Discord's new DAVE End-to-End Encrypted voice protocol (`davey` & `PyNaCl`).

---

## 🛠️ Prerequisites

1. **Python 3.10 or newer**
2. **FFmpeg** installed and added to system PATH.

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/ridaounana/echo.git
cd echo
pip install "discord.py[voice]" gTTS PyNaCl davey
```

### 2. Set Up Discord Bot Token & Intents

1. Go to **Discord Developer Portal** > **Bot** tab.
2. Enable **Message Content Intent**, **Server Members Intent**, and **Presence Intent**.
3. Create a Discord role named **`Blind`** or **`Visually Impaired`** in your server and assign it to users who need accessibility assistance.

### 3. Run the Bot

```bash
# Set token in token.txt or environment variable
echo "YOUR_DISCORD_BOT_TOKEN" > token.txt
python discord_tts_bot.py
```

---

## 🎮 How to Use in Discord

* **Hands-Free Auto-Assistance**: Users with the **`Blind`** or **`Visually Impaired`** role don't need to type anything! The bot automatically joins their voice channel as soon as they enter.
* **Manual Commands**:
  | Command | Description |
  | :--- | :--- |
  | **`!join`** | Manually invites Echo into your current Voice Channel. |
  | **`!leave`** | Disconnects Echo from the Voice Channel. |

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

*Crafted with ❤️ for accessibility and the global Arabizi community.*
