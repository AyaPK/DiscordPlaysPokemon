import os

import discord
from dotenv import load_dotenv
from integration.pyboy_integration import pyboy_tick
import json

REACTION_EMOJIS = {
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "arrow_left": "⬅️",
    "arrow_right": "➡️",
    "a": "🅰️",
    "b": "🅱️",
    "start": "▶️",
    "select": "📋",
}

DISCORD_TOKEN = None

def create_bot() -> discord.Client:
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        elif message.content.startswith('$tick'):
            pyboy_tick()
            await send_screenshot(message.channel)
        elif message.content.startswith('$a'):
            pyboy_tick(button="a")
            await send_screenshot(message.channel)
        elif message.content.startswith('$b'):
            pyboy_tick(button="b")
            await send_screenshot(message.channel)
        elif message.content.startswith('$up'):
            pyboy_tick(button="up")
            await send_screenshot(message.channel)
        elif message.content.startswith('$down'):
            pyboy_tick(button="down")
            await send_screenshot(message.channel)
        elif message.content.startswith('$left'):
            pyboy_tick(button="left")
            await send_screenshot(message.channel)
        elif message.content.startswith('$right'):
            pyboy_tick(button="right")
            await send_screenshot(message.channel)
        elif message.content.startswith('$start'):
            pyboy_tick(button="start")
            await send_screenshot(message.channel)
        elif message.content.startswith('$select'):
            pyboy_tick(button="select")
            await send_screenshot(message.channel)

    return client


async def send_screenshot(channel):
    file = discord.File("data/image.png", filename="image.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://image.png")
    await channel.send(file=file, embed=embed)

    valid_reactions = json.loads(
        os.getenv("VALID_REACTIONS", "[]")
    )

    reaction_message = await channel.send(
        "React to select the next input"
    )

    for reaction in valid_reactions:
        emoji = REACTION_EMOJIS.get(reaction)

        if emoji is None:
            print(f"Unknown reaction: {reaction}")
            continue

        await reaction_message.add_reaction(emoji)