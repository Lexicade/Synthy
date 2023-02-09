import discord
from discord.ext import commands
import requests
import json
import datetime
import importlib
import utils
importlib.reload(utils)


class XKCD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="comic",
                    description="Obtain a comic by ID from xkcd.com",
                    type=discord.ApplicationCommandOptionType.string,
                    required=False,
                ),
                discord.ApplicationCommandOption(
                    name="latest",
                    description="Obtain the latest comic from xkcd.com",
                    type=discord.ApplicationCommandOptionType.string,
                    required=False,
                ),
            ],
        )
    )
    async def xkcd(self, ctx, comic_id):
        """Comics from xkcd.com."""

    @xkcd.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="comic_id",
                    description="The ID for the xkcd comic you want.",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                ),
            ],
        )
    )
    async def comic(self, ctx, comic_id):
        """Pull a comic from xkcd.com based on ID."""
        xkcd = await self.get_comic(f"https://xkcd.com/{comic_id}/info.0.json")
        emb = await utils.embed(ctx, xkcd["title"], xkcd["description"], image=xkcd["image_url"], url=xkcd["url"].replace('info.0.json', ''))
        await ctx.send(embed=emb)
        return

    @xkcd.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def latest(self, ctx):
        """Pull the latest XKCD comic"""
        xkcd = await self.get_comic("https://xkcd.com/info.0.json")
        emb = await utils.embed(ctx, xkcd["title"], xkcd["description"], image=xkcd["image_url"], url=xkcd["url"])
        await ctx.send(embed=emb)
        return

    @staticmethod
    async def get_comic(url):
        re_x = requests.get(url)

        if re_x.status_code == 200:
            data_x = json.loads(re_x.text)

            xkcd = {"date": datetime.date(int(data_x['year']), int(data_x['month']), int(data_x['day'])).strftime('%d %B %Y'),
                    "comic_id": data_x['num'],
                    "title": data_x["title"],
                    "description": data_x['alt'],
                    "image_url": data_x["img"],
                    "url": url}
            return xkcd
        else:
            return None


def setup(bot):
    print("INFO: Loading [XKCD]... ", end="")
    bot.add_cog(XKCD(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [XKCD]")
