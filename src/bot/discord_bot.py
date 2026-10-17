import os

import discord
from dotenv import load_dotenv
from integration.pyboy_integration import pyboy_tick
import json

BUTTON_LABELS = {
    "arrow_up": ("↑", "up", 0),
    "arrow_down": ("↓", "down", 0),
    "arrow_left": ("←", "left", 0),
    "arrow_right": ("→", "right", 0),
    "a": ("A", "a", 1),
    "b": ("B", "b", 1),
    "start": ("Start", "start", 1),
    "select": ("Select", "select", 1),
}

DISCORD_TOKEN = None
latest_screenshot_messages = {}
MESSAGES_FILE = "src/state/messages.json"


def load_message_ids() -> dict:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_message_ids():
    with open(MESSAGES_FILE, "w") as f:
        json.dump(
            {str(ch): msg.id for ch, msg in latest_screenshot_messages.items()}, f
        )


class InputButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        input_name: str,
        channel: discord.abc.Messageable,
        style: discord.ButtonStyle,
        row: int = 0,
    ):
        super().__init__(label=label, style=style, custom_id=f"input_{input_name}", row=row)
        self.input_name = input_name
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        pyboy_tick(button=self.input_name)
        await send_screenshot(self.channel)
        log_input(interaction)


class InputView(discord.ui.View):
    def __init__(self, channel: discord.abc.Messageable):
        super().__init__(timeout=None)

        valid_reactions = json.loads(
            os.getenv("VALID_REACTIONS", "[]")
        )

        for reaction in valid_reactions:
            if reaction not in BUTTON_LABELS:
                continue

            label, input_name, row = BUTTON_LABELS[reaction]

            if input_name in ("up", "down", "left", "right"):
                style = discord.ButtonStyle.primary
            elif input_name in ("a", "b"):
                style = discord.ButtonStyle.danger
            else:
                style = discord.ButtonStyle.secondary

            self.add_item(
                InputButton(label, input_name, channel, style, row=row)
            )


def create_bot() -> discord.Client:
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        for channel_id_str, message_id in load_message_ids().items():
            channel = client.get_channel(int(channel_id_str))
            if channel is None:
                continue
            try:
                message = await channel.fetch_message(message_id)
                latest_screenshot_messages[channel.id] = message
                client.add_view(InputView(channel), message_id=message_id)
            except discord.NotFound:
                pass

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
    save_message_ids()

def log_input(interaction: discord.Interaction):
    print(interaction.user.id)