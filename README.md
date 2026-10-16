# Discord Plays Pokémon

### A port of [SlackPlaysPokemon](https://github.com/AyaPK/slack-plays-pokemon) to work on Discord

## System Requirements

DiscordPlaysPokemon uses poetry for Python to create an isolated environment and manage package dependencies.
Before continuing, ensure you have installed Python version 3.12 or above.

### Poetry installation (Bash)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Poetry installation (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Poetry installation (Pip)

```bash
pip install poetry
```

You can check poetry is installed by running `poetry --version` from a terminal.

## Dependencies

The project uses a virtual environment to isolate package dependencies. To create the virtual environment and install required packages, run the following from your preferred shell:

```bash
$ poetry install
```

## Running the Python code
Once you have followed the above instructions, you can run the app using Poetry:
```bash
$ poetry run python src/main.py
```

## Emulation
This project emulates Pokémon Blue (and possibly supports Pokémon Red unofficially). You will need your own legally dumped cartridge as a `.gb` file in the `/data` folder located at the root of your project, to run it.

## Acknowledgements
- [PyBoy](https://github.com/Baekalfen/PyBoy) - Used to emulate a headless Gameboy and store the game state