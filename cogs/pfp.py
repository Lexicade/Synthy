from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class PFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[PFP] "

    @commands.defer(ephemeral=False)
    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    description="Post the users profile picture to chat.",
                    type=discord.ApplicationCommandOptionType.user,
                    required=True,
                ),
            ]
        )
    )
    async def pfp(self, ctx, user: discord.Member):
        """Post the users profile picture to chat."""
        await ctx.send(content=user.avatar.with_format('jpg'))


def setup(bot):
    print("INFO: Loading [PFP]... ", end="")
    bot.add_cog(PFP(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [PFP]")
