module.exports = {
  apps: [
    {
      name: "echo-tts-bot",
      script: "discord_tts_bot.py",
      interpreter: "python3",
      restart_delay: 3000,
      max_restarts: 10,
      autorestart: true
    }
  ]
};
