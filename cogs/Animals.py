from discord.ext import commands
from discord import app_commands
import discord
import importlib
import requests
import json
import utils
importlib.reload(utils)


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='dog', description="Get a dog picture!")
    async def dog(self, interaction: discord.Interaction):
        """Get a dog picture!"""
        obj_dog = await self.get_request("https://dog.ceo/api/breeds/image/random")
        emb = await utils.embed(interaction, "Random Dog:", "", image=obj_dog["message"])
        await interaction.response.send_message(embed=emb, ephemeral=False)

    @app_commands.command(name='cat', description="Get a cat picture!")
    async def cat(self, interaction: discord.Interaction):
        obj_cat = await self.get_request("https://api.thecatapi.com/v1/images/search")
        emb = await utils.embed(interaction, "Random Cat:", "", image=obj_cat[0]["url"])
        await interaction.response.send_message(embed=emb, ephemeral=False)

    @staticmethod
    async def get_request(url):
        obj_request_get = requests.get(url)
        if obj_request_get.status_code == 200:
            obj_data = json.loads(obj_request_get.text)
            return obj_data
        else:
            return None

async def setup(bot):
    print("INFO: Loading [Animals]... ", end="")
    await bot.add_cog(Animals(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Animals]")
