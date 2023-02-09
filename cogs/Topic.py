from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Topic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def topic(self, ctx):
        """Post the channel topic into chat."""
        txt_topic = "None" if ctx.channel.topic is None else ctx.channel.topic
        emb = await utils.embed(ctx,
                                f"Topic for {ctx.channel.name}:",
                                f"{txt_topic}")
        await ctx.send(embed=emb)

def setup(bot):
    print("INFO: Loading [Topic]... ", end="")
    bot.add_cog(Topic(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Topic]")
