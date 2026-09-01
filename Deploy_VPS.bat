@echo off
title Deploy Echo Bot on VPS
echo ========================================================
echo 🚀 Deploying Latest Echo Bot Features to PM2
echo ========================================================
echo.

echo 📥 Pulling latest code from GitHub...
git pull origin main

echo 📦 Installing dependencies...
pip install "discord.py[voice]" gTTS PyNaCl davey

echo 🔄 Restarting bot under PM2...
pm2 restart ecosystem.config.js --update-env
pm2 save

echo.
echo ========================================================
echo ✅ Echo Bot Deployed and Restarted Successfully!
echo ========================================================
pause
