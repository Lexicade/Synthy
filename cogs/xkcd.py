import discord
from discord.ext import commands
from discord import app_commands
import requests
import json
import datetime
import importlib
import utils
importlib.reload(utils)


class XKCD(commands.GroupCog, name='xkcd', description='Comics from xkcd.com.'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='comic', description='Pull a comic from xkcd.com based on ID.')
    async def comic(self, interaction: discord.Interaction, comic_id: int):
        xkcd = await self.get_comic(f"https://xkcd.com/{comic_id}/info.0.json")
        emb = await utils.embed(interaction, xkcd["title"], xkcd["description"], image=xkcd["image_url"], url=xkcd["url"].replace('info.0.json', ''))
        await interaction.response.send_message(embed=emb)
        return

    @app_commands.command(name='latest', description='Pull the latest XKCD comic')
    async def latest(self, interaction: discord.Interaction):
        xkcd = await self.get_comic("https://xkcd.com/info.0.json")
        emb = await utils.embed(interaction, xkcd["title"], xkcd["description"], image=xkcd["image_url"], url=xkcd["url"])
        await interaction.response.send_message(embed=emb)
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


async def setup(bot):
    print("INFO: Loading [XKCD]... ", end="")
    await bot.add_cog(XKCD(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [XKCD]")
