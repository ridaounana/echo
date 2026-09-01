#!/bin/bash
# Echo TTS Bot — 1-Click VPS Update & Deploy Script

echo "=========================================="
echo "🚀 Updating Echo Bot on VPS..."
echo "=========================================="

# Navigate to script directory
cd "$(dirname "$0")"

# Pull latest changes from GitHub
echo "📥 Pulling latest open-source code from GitHub..."
git pull origin main

# Install/Update dependencies
echo "📦 Verifying Python dependencies..."
pip3 install "discord.py[voice]" gTTS PyNaCl davey --break-system-packages

# Reload/Restart with PM2
echo "🔄 Reloading PM2 process..."
pm2 restart ecosystem.config.js --update-env

# Save PM2 state
pm2 save

echo "=========================================="
echo "✅ Echo Bot successfully deployed and running!"
echo "=========================================="
pm2 status
