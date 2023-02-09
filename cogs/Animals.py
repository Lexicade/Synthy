from discord.ext import commands
import discord
import importlib
import requests
import json
import utils
importlib.reload(utils)


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.defer(ephemeral=False)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def dog(self, ctx):
        """Get a dog picture!"""
        obj_dog = await self.get_request("https://dog.ceo/api/breeds/image/random")
        emb = await utils.embed(ctx, "Random Dog:", "", image=obj_dog["message"])
        await ctx.send(embed=emb)

    @commands.defer(ephemeral=False)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def cat(self, ctx):
        """Get a cat picture!"""
        obj_cat = await self.get_request("https://api.thecatapi.com/v1/images/search")
        emb = await utils.embed(ctx, "Random Cat:", "", image=obj_cat[0]["url"])
        await ctx.send(embed=emb)

    @staticmethod
    async def get_request(url):
        obj_request_get = requests.get(url)
        if obj_request_get.status_code == 200:
            obj_data = json.loads(obj_request_get.text)
            return obj_data
        else:
            return None

def setup(bot):
    print("INFO: Loading [Animals]... ", end="")
    bot.add_cog(Animals(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Animals]")
