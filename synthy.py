import asyncio

from discord.ext import commands
import discord
import logging
import importlib
import utils
import random
import psycopg2
import os
import json
import configparser
importlib.reload(utils)
logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.members = True


# bot = commands.Bot(command_prefix=get_pre, intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} {bot.user.id}")
    print(f"Discord.py version: {discord.__version__}")
    print("------")

    bot.load_extension(f"cogs.ExtensionLoader")

    # Add 'playing' status
    random_games = ['Breath of the Wild 2', 'Metroid Prime 4', 'Bayonetta 3', 'Hollow Knight: Silksong', 'Overwatch 2', 'Path of Exile 2', 'Vampire: The Masquerade – Bloodlines 2', 'Beyond Good And Evil 2']
    random_game = random.choice(random_games)

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=random_game))


@bot.event
async def on_message(message: discord.Message):
    prefix = await bot.get_prefix(message)
    words = message.content.split(" ")
    first_word = words[0].lower()

    if first_word.startswith(prefix) and first_word.replace(prefix, "") in ['load', 'unload', 'reload', 'slashload', 'slashunload']:
        await bot.invoke(await bot.get_context(message))

bot.run(os.environ.get('discord_bot_token'))

# Thanks to:
# jagw#6619 - Assisted with command testing
# UberGinge#1809 - Assisted with command testing
# I'mJustJun#7925 - Super helpful in finding bugs and errors in testing
# allicat323#9814 - Helpful input into the help messages for commands with configurations
