import pyboy as pb
import discord

from bot.discord_bot import create_bot
import os

client = create_bot()
print(os.getenv('DISCORD_TOKEN'))
client.run(os.getenv("DISCORD_TOKEN"))
