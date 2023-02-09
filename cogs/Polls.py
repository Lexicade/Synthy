from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Polls] "

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def poll(self, ctx, *arg):
        """Set up a poll for people to vote yes/maybe/no on."""
        if len(arg) == 0:
            prefix = await self.bot.get_prefix(ctx.message)
            emb = await utils.embed(ctx, f"Help for `{prefix[2]}poll`",
                                    "Set up a poll for people to vote yes/maybe/no on.", "")
            emb = await utils.field(emb, f"{prefix[2]}poll `[text]`", "Reposts your message as a poll, whichwill have react emojis added to it.")
            await ctx.send(embed=emb)
            return
        arg = " ".join(arg)

        emb = await utils.embed(ctx, "Poll", arg)
        obj_msg = await ctx.send(embed=emb)

        # try:
        await obj_msg.add_reaction("👍")
        await obj_msg.add_reaction("🤷")
        await obj_msg.add_reaction("👎")

        # except discord.Forbidden:
        #     await ctx.message.channel.send(content=f"{extension_name} Missing `add_reactions` permission.")
        # except discord.NotFound:
        #     await ctx.message.channel.send(content=f"{extension_name} The emoji specified was not found.")
        # except discord.HTTPException:
        #     await ctx.message.channel.send(content=f"{extension_name} Failed to add the reaction.")
        # except discord.InvalidArgument:
        #     await ctx.message.channel.send(content=f"{extension_name} The emoji parameter is invalid.")

    # @poll.error
    # async def poll_error(self, ctx, error):
    #     if isinstance(error, commands.BotMissingPermissions):
    #         await ctx.send(content=f"I can't use polls without `{'`, `'.join(error.missing_perms)}`.")
    #
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         if error.param.name == 'arg':
    #             await ctx.send("Ask a question after `!poll`.")


def setup(bot):
    print("INFO: Loading [Polls]... ", end="")
    bot.add_cog(Polls(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Polls]")
