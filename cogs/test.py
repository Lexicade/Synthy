import asyncio
import datetime

from discord.ext import commands
import discord
import re
import upsidedown
import importlib
import utils
importlib.reload(utils)


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        """testing"""
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="Do not click me", custom_id="bad_touch", style=discord.ButtonStyle.red)
            ),
            discord.ui.ActionRow(
                discord.ui.Button(label="Click me", custom_id="good_touch", style=discord.ButtonStyle.green)
            ),
        )
        sent_message: discord.Message = await ctx.send("Do not press this button", components=components)

        def check(interaction: discord.Interaction):
            return True

        interaction: discord.Interaction = await self.bot.wait_for("component_interaction", check=check)
        if interaction.component.custom_id == "bad_touch":
            await interaction.message.reply(content=f"{interaction.user.mention} is a nonce!")
        else:
            await interaction.message.reply(content=f"{interaction.user.mention} is an egg!")


def setup(bot):
    print("INFO: Loading [Test]... ", end="")
    bot.add_cog(Test(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Test]")
