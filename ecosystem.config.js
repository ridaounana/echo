module.exports = {
  apps: [
    {
      name: "echo-tts-bot",
      script: "discord_tts_bot.py",
      interpreter: "python3",
      env: {
        DISCORD_BOT_TOKEN: "YOUR_DISCORD_BOT_TOKEN_HERE"
      },
      restart_delay: 3000,
      max_restarts: 10,
      autorestart: true
    }
  ]
};
