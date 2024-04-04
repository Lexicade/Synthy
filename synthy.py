from discord.ext import commands
import discord
import random
import logging
import importlib
import utils
import os
importlib.reload(utils)
logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} {bot.user.id}")
    print(f"Discord.py version: {discord.__version__}")
    print("------")

    await bot.load_extension(f"cogs.ExtensionLoader")

    # Add 'playing' status
    random_games = ['Metroid Prime 4', 'Hollow Knight: Silksong', 'Path of Exile 2', 'Vampire: The Masquerade – Bloodlines 2', 'Beyond Good And Evil 2']
    random_game = random.choice(random_games)

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=random_game))


@bot.event
async def on_message(message: discord.Message):
    prefix = await bot.get_prefix(message)
    words = message.content.split(" ")
    first_word = words[0].lower()

    if first_word.startswith(prefix) and first_word.replace(prefix, "") in ['load', 'unload', 'reload', 'slashload', 'slashunload', 'debugsync']:
        await bot.invoke(await bot.get_context(message))

# bot.run(os.environ.get('discord_bot_token'))
bot.run(os.environ.get('discord_bot_token_dev'))

# Thanks to:
# jagw#6619 - Assisted with command testing
# UberGinge#1809 - Assisted with command testing
# I'mJustJun#7925 - Super helpful in finding bugs and errors in testing
# allicat323#9814 - Helpful input into the help messages for commands with configurations
