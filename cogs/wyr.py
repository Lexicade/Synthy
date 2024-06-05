from discord.ext import commands
from discord import app_commands
import discord
import importlib

import utils
from utils import CustomSQL
importlib.reload(utils)



class WYR(commands.GroupCog, name="wyr", description="Would you rather?"):
    def __init__(self, bot):
        self.sql = CustomSQL()
        self.bot = bot

    @app_commands.command(name='addnew', description="Add a new would you rather option for this server.")
    async def addnew(self, interaction: discord.Interaction, wyr_option: str):
        sql = CustomSQL()
        await sql.run_sql('INSERT INTO "database1".synthy.wyr (guild_id, wyr_option, added_by) VALUES (%s, %s, %s);',
                          (interaction.guild.id, wyr_option, interaction.user.id,))
        await interaction.response.send_message("This has been saved for this server.", ephemeral=True)

    @app_commands.command(name='ask', description="Pose a would you rather.")
    async def ask(self, interaction: discord.Interaction):
        options = await self.sql.run_sql('SELECT wyr_option, added_by from database1.synthy.wyr WHERE guild_id = %s ORDER BY random() LIMIT 2;', (interaction.guild.id, ))
        emb = await utils.embed(interaction,
                                "Would you rather",
                                f":one: {options[0]['wyr_option']}\n<@{options[0]['added_by']}>\n\nOR\n\n:two: {options[1]['wyr_option']}\n<@{options[1]['added_by']}>")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='remove', description="Remove one of your options.")
    async def remove(self, interaction: discord.Interaction):
        raw_options = await self.sql.run_sql('SELECT wyr_option, added_by from database1.synthy.wyr WHERE guild_id = %s and added_by = %s ORDER BY wyr_option;', (interaction.guild.id, interaction.user.id))
        options = []
        for option in raw_options:
            options.append(option['wyr_option'])
        view = DropdownView(options=options)
        await interaction.response.send_message('Pick your favourite colour:', view=view, ephemeral=True)

    @app_commands.command(name='stats', description="Remove one of your options.")
    async def stats(self, interaction: discord.Interaction):
        sql_data = await self.sql.run_sql('select count(wyr_option) from database1.synthy.wyr where guild_id = %s;', (interaction.guild.id,))
        wyr_count = sql_data[0]['count']

        emb = await utils.embed(interaction, "Would you rather", f"Total options on this server: {sql_data[0]['count']}")
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


class DropdownView(discord.ui.View):
    def __init__(self, options: list):
        super().__init__()
        self.add_item(Dropdown(options_list=options))


class Dropdown(discord.ui.Select):
    def __init__(self, options_list: list):
        options = []
        for i in range(0, len(options_list)):
            print(options_list[i])
            options.append(discord.SelectOption(label=options_list[i]))

        super().__init__(placeholder='Choose one of your options to remove...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        sql = CustomSQL()
        await sql.run_sql('DELETE FROM database1.synthy.wyr WHERE guild_id = %s and added_by = %s and wyr_option = %s;',
                          (interaction.guild.id, interaction.user.id, self.values[0]))

        await interaction.response.edit_message(content=f"Removed: `{self.values[0]}`", view=None)
