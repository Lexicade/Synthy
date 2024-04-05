from discord.ext import commands
from discord import app_commands
import discord
import importlib
import utils
import itertools
import math
importlib.reload(utils)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description="Shows this help message.")
    async def help(self, interaction: discord.Interaction):
        str_cmds = ""
        cmds = {}

        # Reorder list
        cmds_set = self.bot.commands

        for cmd in cmds_set:
            if not cmd.hidden:
                cmds[cmd.name] = {"help": cmd.help}

        cmds = dict(sorted(cmds.items(), key=lambda x: x[0].lower()))
        await pagify(self, cmds, 5, 2)
        for cmd in cmds:
            str_cmds = f"{str_cmds}\n•**{cmd}** - {cmds[cmd]['help']}"

        emb = await utils.embed(interaction, "Help commands", str_cmds)
        await interaction.response.send_message(embed=emb)


async def pagify(self, input, items_per_page, page_wanted=1):
    total_items = len(input)
    # total items = 25
    pages = 1

    if total_items > items_per_page:
        pages = int(math.floor(total_items / items_per_page))

    return_list = []
    for i, item in enumerate(input):
        if int(math.floor(i / pages)) == page_wanted:
            return_list.append({item: input[item]["help"]})

    print(return_list)
    return return_list


async def setup(bot):
    print("INFO: Loading [Help]... ", end="")
    await bot.add_cog(Help(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Help]")
