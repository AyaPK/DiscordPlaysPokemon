import os

import discord
from dotenv import load_dotenv
from integration.pyboy_integration import pyboy_tick

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


    return client


async def send_screenshot(channel):
    file = discord.File("data/image.png", filename="image.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://file.png")
    await channel.send(file=file, embed=embed)