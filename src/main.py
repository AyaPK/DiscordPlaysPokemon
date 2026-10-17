import pyboy as pb
import discord

from bot.discord_bot import create_bot
from state.state_manager import set_up_data
import os

set_up_data()
client = create_bot()
print(os.getenv('DISCORD_TOKEN'))
client.run(os.getenv("DISCORD_TOKEN"))
