from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw
from ratelimit import limits, sleep_and_retry
import discord
import importlib
import utils
import csv
import json
import requests
import asyncio
from ffxiv.ffxiv_core import FFXIVCharacter, ScrapeLodestone
from io import BytesIO
importlib.reload(utils)


class FFXIV(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="findme",
                    description="Find your FFXIV character",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="character",
                    description="View your character with their levels and data",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="portrait",
                    description="View just the appearance of your character",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
            ],
        )
    )
    async def ffxiv(self, ctx):
        True

    @commands.defer(ephemeral=False)
    @ffxiv.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="fname",
                    description="The first name of this character",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="lname",
                    description="The last name of your character",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="server",
                    description="The homeworld of your character",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    async def findme(self, ctx, fname, lname, server):
        """Find and save a character from the FFXIV Lodestone"""
        member = ctx.interaction.user
        msg = await ctx.send(f'Searching for {fname} {lname} on {server}...')

        url = f"https://xivapi.com/character/search?name={fname}%20{lname}&server={server}"
        data = await utils.get_request(url)
        if data and len(data["Results"]) > 0:
            data_id = data["Results"][0]["ID"]
            print(f'Remembering {data["Results"][0]}')
            print(f'Remembering {data["Results"][0]["Name"]}')
            print(f'Remembering {data["Results"][0]["ID"]}')
            await utils.sql('INSERT INTO "database1".synthy.ffxiv (member_id, id) VALUES (%s, %s) ON CONFLICT (member_id) DO UPDATE SET id = %s;', (member.id, data_id, data_id,))
            await msg.edit(content=f'I have found {data["Results"][0]["Name"]} on {data["Results"][0]["Server"]}. From now on you can use `showme` to view your character.')
        else:
            await msg.edit(content=f'Unable to find a character with this name.')
            return

    @commands.defer(ephemeral=False)
    @ffxiv.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def character(self, ctx):
        "View your character with their levels and data"""
        member = ctx.interaction.user
        user_id = await utils.sql(f'SELECT id FROM "database1".synthy.ffxiv WHERE member_id = %s;', (member.id,))
        if user_id and len(user_id) == 1 and 'id' in user_id[0]:
            user_id = user_id[0]['id']
        else:
            await ctx.send("Unable to find your character. Please try using /findme `firstname` `lastname` `server` first")
            return

        character = FFXIVCharacter(character_id=user_id)
        await character.obtain_character_data()
        await character.build_character_view()

        with open('./character.png', 'rb') as fp:
            await ctx.interaction.edit_original_message(content=None, file=discord.File(fp, "image.png"))
            return


    @commands.defer(ephemeral=False)
    @ffxiv.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def portrait(self, ctx):
        "View just the appearance of your character"""
        member = ctx.interaction.user
        user_id = await utils.sql(f'SELECT id FROM "database1".synthy.ffxiv WHERE member_id = %s;', (member.id,))
        if user_id and len(user_id) == 1 and 'id' in user_id[0]:
            user_id = user_id[0]['id']
        else:
            await ctx.send("Unable to find your character. Please try using /findme `firstname` `lastname` `server` first")
            return

        character = FFXIVCharacter(character_id=user_id)
        await character.obtain_character_data()
        await character.build_character_portrait()

        with open('./character_portrait.png', 'rb') as fp:
            await ctx.interaction.edit_original_message(content=None, file=discord.File(fp, "image.png"))
            return


def setup(bot):
    print("INFO: Loading [FFXIV]... ", end="")
    bot.add_cog(FFXIV(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [FFXIV]")

