import asyncio
import json
import os
import random

import discord
from dotenv import load_dotenv
from integration.pyboy_integration import pyboy_tick
from state.state_manager import record_input, record_votes

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

current_votes = {}
VOTE_DURATION = 10

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
        super().__init__(
            label=label,
            style=style,
            custom_id=f"input_{input_name}",
            row=row,
        )
        self.input_name = input_name
        self.channel = channel
        self.voters: set[int] = set()
        self.original_label = label

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = interaction.user.id
        view: InputView = self.view

        for item in view.children:
            if isinstance(item, InputButton) and user_id in item.voters:
                item.voters.discard(user_id)
                item._update_label()

        if self.input_name not in (current_votes.get(user_id) or set()):
            self.voters.add(user_id)
            current_votes[user_id] = {self.input_name}
        else:
            current_votes.pop(user_id, None)

        self._update_label()

        first_vote = not view.voting_active
        if first_vote:
            view.voting_active = True
            asyncio.create_task(view.run_vote_timer(interaction.message))

        await interaction.edit_original_response(
            content=view.status_content(),
            view=view,
        )

        log_input(interaction)

    def _update_label(self):
        count = len(self.voters)
        self.label = f"{self.original_label} ({count})" if count > 0 else self.original_label


class InputView(discord.ui.View):
    def __init__(self, channel: discord.abc.Messageable):
        super().__init__(timeout=None)
        self.channel = channel
        self.voting_active = False

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

    def status_content(self) -> str:
        if not self.voting_active:
            return ""
        return "🗳️ Voting in progress!"

    async def run_vote_timer(self, message: discord.Message):
        await asyncio.sleep(VOTE_DURATION)

        winner = self._tally_winner()

        all_voters = [uid for item in self.children
                      if isinstance(item, InputButton)
                      for uid in item.voters]
        record_votes(all_voters)

        self.voting_active = False

        global current_votes
        current_votes = {}

        for item in self.children:
            if isinstance(item, InputButton):
                item.voters.clear()
                item._update_label()

        try:
            await message.edit(content="", view=self)
        except discord.HTTPException:
            pass

        if winner:
            record_input(winner)
            pyboy_tick(button=winner)
            await send_screenshot(self.channel)
        else:
            try:
                await message.edit(content="No votes were cast.", view=self)
            except discord.HTTPException:
                pass

    def _tally_winner(self) -> str | None:
        counts: dict[str, int] = {}
        for item in self.children:
            if isinstance(item, InputButton) and item.voters:
                counts[item.input_name] = len(item.voters)
        if not counts:
            return None
        max_votes = max(counts.values())
        winners = [k for k, v in counts.items() if v == max_votes]
        return random.choice(winners)


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
    print(current_votes)