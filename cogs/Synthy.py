from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Synthy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.group(invoke_without_command=True)
    async def synthy(self, ctx):
        """
        Allows you to change the bots nickname for your Discord server
        """
        prefix = await self.bot.get_prefix(ctx.message)

        emb = await utils.embed(ctx, f"Commands for `{prefix[2]}{self.bot.user.name.lower()}`", "")
        emb = await utils.field(emb, f"{prefix[2]}{self.bot.user.name.lower()} nick `[nickname]`",
                                f"Change the nickname for {self.bot.user.name.lower()} on this server.")
        emb = await utils.field(emb, f"{prefix[2]}{self.bot.user.name.lower()} prefix `[prefix]`",
                                f"Change the symbol used for commands from `{prefix[2]}` to another symbol.\n" +
                                "This can be a maximum of 5 characters.")

        await ctx.message.channel.send(embed=emb)

    @commands.has_permissions(administrator=True)
    @synthy.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def nick(self, ctx, *args):
        try:
            guild = self.bot.get_guild(ctx.message.guild.id)
            member = guild.get_member(self.bot.user.id)
            await member.edit(nick=" ".join(args))
            if ctx.guild.me.permissions_in(ctx.channel).add_reactions:
                await ctx.message.add_reaction("✅")
        except discord.Forbidden as e:
            await ctx.message.channel.send(f"Forbidden: {e}")
        except discord.HTTPException as e:
            await ctx.message.channel.send(f"HTTPException: {e}")
        except Exception as e:
            await ctx.message.channel.send(f"Error: {e}")

    @commands.has_permissions(administrator=True)
    @synthy.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def activity(self, ctx, *args):
        try:
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=" ".join(args)))
        except discord.InvalidArgument as e:
            await ctx.message.channel.send(f"InvalidArgument: {e}")
        except Exception as e:
            await ctx.message.channel.send(f"Error: {e}")

    @commands.has_permissions(administrator=True)
    @synthy.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def prefix(self, ctx, arg):
        await utils.sql('INSERT INTO "database1".synthy.settings (guild_id, bot_name, prefix) VALUES (%s, %s, %s) ON CONFLICT (guild_id, bot_name) DO UPDATE SET prefix = %s;', (ctx.guild.id, self.bot.user.name, arg, arg,))
        emb = await utils.embed(ctx, self.bot.user.name, f"Server prefix set to `{arg}`")
        await ctx.send(embed=emb)
        if ctx.guild.me.permissions_in(ctx.channel).manage_messages:
            await ctx.message.delete()


def setup(bot):
    print("INFO: Loading [Synthy]... ", end="")
    bot.add_cog(Synthy(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Synthy]")
