#!/bin/bash
# Echo TTS Bot — 1-Click Linux VPS Deployment Script

echo "=========================================="
echo "🚀 Updating Echo Bot on Linux VPS..."
echo "=========================================="

# Navigate to project directory
cd "$(dirname "$0")"

# Pull latest open-source code from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Install/Update Python dependencies with PEP 668 override
echo "📦 Verifying Python dependencies..."
pip3 install "discord.py[voice]" gTTS PyNaCl davey --break-system-packages

# Reload & Restart with PM2
echo "🔄 Reloading PM2 process..."
pm2 restart ecosystem.config.js --update-env

# Save PM2 state
pm2 save

echo "=========================================="
echo "✅ Echo Bot Deployed & Running on VPS!"
echo "=========================================="
pm2 status
