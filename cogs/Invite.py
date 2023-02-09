from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def invite(self, ctx, *arg):
        """Invite me to another server!"""
        emb = await utils.embed(ctx,
                                "Invite Link:",
                                "[Invite Synthy to join your server.](https://discordapp.com/oauth2/authorize?client_id=459056626377293824&scope=bot&permissions=335932512)")
        await ctx.send(embed=emb)

def setup(bot):
    print("INFO: Loading [Invite]... ", end="")
    bot.add_cog(Invite(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Invite]")
