from discord.ext import commands
from discord import app_commands
import discord
import importlib
import utils
importlib.reload(utils)


class PFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='pfp', description='Post the users profile picture to chat.')
    async def pfp(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(content=user.avatar.with_format('jpg'))


async def setup(bot):
    print("INFO: Loading [PFP]... ", end="")
    await bot.add_cog(PFP(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [PFP]")
