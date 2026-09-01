# ♿ Echo — Discord Arabizi & Accessibility Neural TTS Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.7+-blueviolet.svg)](https://github.com/Rapptz/discord.py)
[![Edge-TTS](https://img.shields.io/badge/Edge--TTS-AI%20Neural-green.svg)](https://github.com/rany2/edge-tts)

**Echo** is an open-source, community-driven Discord Text-to-Speech (TTS) Accessibility bot powered by **Microsoft Edge AI Neural Voices**. It is designed to empower visually impaired and blind users in Discord communities by reading text chat messages out loud in voice channels.

Specifically crafted for **Moroccan, North African, and Arabizi/3rabizi communities**, Echo features **high-definition AI Neural Voices** and an intelligent **3rabizi Transliteration Engine** that automatically converts number-substituted chat scripts (`7`, `kh`, `3`, `9`, `5`, `ch`) into authentic Arabic phonetic speech!

---

## 🌟 Key Features

* **♿ Accessible AI Neural Voice Narration**: Ultra-realistic, human-like AI voice playback inside your Discord Voice channel.
* **🎙️ Selectable AI Voices**:
  * **`Jamal`** (`ar-MA-JamalNeural`) — Moroccan Male AI Voice *(Default)*
  * **`Salma`** (`ar-EG-SalmaNeural`) — Egyptian Female AI Voice
  * **`Mouna`** (`ar-MA-MounaNeural`) — Moroccan Female AI Voice
  * **`Denise`** (`fr-FR-DeniseNeural`) — French Female AI Voice
* **🇲🇦 Arabizi / 3rabizi Transliteration Engine**: Real-time phonetic conversion for North African & Middle Eastern chat scripts:
  * `7` ➡️ `ح` *(e.g., "7bibi" ➔ "حبيبي")*
  * `kh` / `5` ➡️ `خ` *(e.g., "khoya" ➔ "خويا")*
  * `3` ➡️ `ع` *(e.g., "3afak" ➔ "عفاك")*
  * `9` ➡️ `ق` *(e.g., "9ahwa" ➔ "قهوة")*
  * `2` ➡️ `أ` *(e.g., "so2al" ➔ "سؤال")*
  * `ch` / `sh` ➡️ `ش` *(e.g., "choukrane" ➔ "شكران")*
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
pip install "discord.py[voice]" edge-tts PyNaCl davey
```

### 2. Set Up Discord Bot Token

```bash
# PowerShell
$env:DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
```

### 3. Run the Bot

```bash
python discord_tts_bot.py
```

---

## 🎮 How to Use in Discord

| Command | Description |
| :--- | :--- |
| **`!join`** | Joins your voice channel using the default **Jamal** (Moroccan Male) voice. |
| **`!join Jamal`** | Joins your voice channel using **Jamal** (Moroccan Male Neural Voice). |
| **`!join Salma`** | Joins your voice channel using **Salma** (Egyptian Female Neural Voice). |
| **`!join Mouna`** | Joins your voice channel using **Mouna** (Moroccan Female Neural Voice). |
| **`!voice Salma`** | Switch to Salma's voice on the fly without leaving the voice channel. |
| **`!voice Jamal`** | Switch back to Jamal's Moroccan voice on the fly. |
| **`!leave`** | Disconnects Echo from the Voice Channel. |

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

*Crafted with ❤️ for accessibility and the global Arabizi community.*
