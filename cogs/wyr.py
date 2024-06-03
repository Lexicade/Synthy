import os
import uuid

import psycopg2
from discord.ext import commands
from discord import app_commands
import discord
import importlib

# from psycopg2 import extras
# extras.register_uuid()

import utils
from utils import CustomSQL
importlib.reload(utils)


class WYR(commands.GroupCog, name="wyr", description="Would you rather?"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='addnew', description="Add a new would you rather option for this server.")
    async def addnew(self, interaction: discord.Interaction, wyr_option: str):
        sql = CustomSQL()
        await sql.run_sql('INSERT INTO "database1".synthy.wyr (guild_id, wyr_option, added_by) VALUES (%s, %s, %s);',
                          (interaction.guild.id, wyr_option, interaction.user.id,))
        await interaction.response.send_message("Would you rather...")

    @app_commands.command(name='ask', description="Pose a would you rather.")
    async def ask(self, interaction: discord.Interaction):
        sql = CustomSQL()
        options = await sql.run_sql('SELECT wyr_option, added_by from database1.synthy.wyr WHERE guild_id = %s ORDER BY random() LIMIT 2;', (interaction.guild.id, ))
        emb = await utils.embed(interaction,
                                "Would you rather",
                                f":one: {options[0]['wyr_option']}\n<@{options[0]['added_by']}>\n\nOR\n\n:two: {options[1]['wyr_option']}\n<@{options[1]['added_by']}>")
        await interaction.response.send_message(embed=emb)


async def setup(bot):
    print("INFO: Loading [WYR]... ", end="")

    sql = CustomSQL()
    if not await sql.check_table('wyr'):
        print(f"Table WYR not found, creating WYR... ", end="")
        await sql.run_sql("CREATE TABLE synthy.wyr (wyr_id bigint generated always as identity, guild_id int8 not null, wyr_option varchar not null, added_by int8 not null);", ())

    await bot.add_cog(WYR(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [WYR]")
