from discord.ext import commands
from discord import app_commands
import discord
import importlib
import utils
importlib.reload(utils)


class Topic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='topic', description="Post the channel topic into chat.")
    async def topic(self, interaction: discord.Interaction):
        txt_topic = "None" if interaction.channel.topic is None else interaction.channel.topic
        emb = await utils.embed(interaction,
                                f"Topic for {interaction.channel.name}:",
                                f"{txt_topic}")
        await interaction.response.send_message(embed=emb)


async def setup(bot):
    print("INFO: Loading [Topic]... ", end="")
    await bot.add_cog(Topic(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Topic]")
