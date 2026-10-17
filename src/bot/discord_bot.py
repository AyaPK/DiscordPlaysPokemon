import os

import discord
from dotenv import load_dotenv
from integration.pyboy_integration import pyboy_tick
import json

BUTTON_LABELS = {
    "arrow_up": ("↑", "up"),
    "arrow_down": ("↓", "down"),
    "arrow_left": ("←", "left"),
    "arrow_right": ("→", "right"),
    "a": ("A", "a"),
    "b": ("B", "b"),
    "start": ("Start", "start"),
    "select": ("Select", "select"),
}

DISCORD_TOKEN = None
latest_screenshot_messages = {}


class InputButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        input_name: str,
        channel: discord.abc.Messageable,
        style: discord.ButtonStyle,
    ):
        super().__init__(label=label, style=style)
        self.input_name = input_name
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        pyboy_tick(button=self.input_name)
        await send_screenshot(self.channel)


class InputView(discord.ui.View):
    def __init__(self, channel: discord.abc.Messageable):
        super().__init__(timeout=None)

        valid_reactions = json.loads(
            os.getenv("VALID_REACTIONS", "[]")
        )

        for reaction in valid_reactions:
            if reaction not in BUTTON_LABELS:
                continue

            label, input_name = BUTTON_LABELS[reaction]

            style = (
                discord.ButtonStyle.primary
                if input_name in ("up", "down", "left", "right")
                else discord.ButtonStyle.secondary
            )

            self.add_item(
                InputButton(label, input_name, channel, style)
            )



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

        elif message.content.startswith('$tick'):
            pyboy_tick()
            await send_screenshot(message.channel)

    return client



async def send_screenshot(channel):
    previous_message = latest_screenshot_messages.get(channel.id)

    if previous_message is not None:
        await previous_message.edit(view=None)

    message = await channel.send(
        file=discord.File("data/image.png"),
        view=InputView(channel),
    )

    latest_screenshot_messages[channel.id] = message