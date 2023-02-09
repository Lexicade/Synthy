import discord
from discord.ext import commands
import requests
import json
import datetime
import importlib
import utils
import re
importlib.reload(utils)


class URLFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.defer(ephemeral=False)
    @commands.context_command(name="Discord Media URL Fix")
    async def urlfix(self, ctx: discord.ext.commands.context.Context, message: discord.message.Message):
        """Send the last image posted through a Deep Dream - Via Context Menu"""
        found_urls = re.findall(r'(https?://.+)', message.content)
        found_urls = found_urls + message.attachments
        if not found_urls:
            emb = await utils.embed(ctx, f"Unable to find links", "I wasn't able to see an image in the message you selected.")
            await ctx.send(embed=emb)
            return

        fixed_urls = []
        for url in found_urls:
            fixed_urls.append(str(url).replace('media.discordapp.net/', 'cdn.discordapp.com/'))

        urls = '\n'.join(fixed_urls)
        content = f"Original message from: {message.author.mention}\n[Jump to message!]({message.jump_url})\n\n{urls}"

        await ctx.send(content=content)


def setup(bot):
    print("INFO: Loading [URLFix]... ", end="")
    bot.add_cog(URLFix(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [URLFix]")
