from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.extension_name = "[Role Manager] "

        self.valid_roles = []
        self.role_names = []
        self.example_role = ''

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=["color"], application_command_meta=commands.ApplicationCommandMeta(options=[discord.ApplicationCommandOption(
                                                                                                                name='role_name',
                                                                                                                description='Choose a role name from the list',
                                                                                                                type=discord.ApplicationCommandOptionType.string,
                                                                                                                required=False)]))
    async def colour(self, ctx: discord.ext.commands.Context, *, role_name=""):
        """Gives users the option to pick a colour for their name"""
        await self.get_roles(ctx)

        if role_name.casefold() in self.role_names:
            for role in ctx.author.roles:
                if role.name[1:-1].casefold() in self.role_names:
                    await ctx.author.remove_roles(role)

            guild_role = discord.utils.get(ctx.guild.roles, name=f"[{role_name.lower()}]")
            await ctx.author.add_roles(guild_role)
            emb = await utils.embed(ctx, "Completed!", "")
            await ctx.send(embed=emb)

            # Send log message
            emb = await utils.notice("Colour changed",
                                    f"[COLOURS] Changed colour of {ctx.author} to {guild_role}",
                                    colour="green")
            await utils.log(ctx.guild.id, self.bot, emb=emb)

        elif len(self.valid_roles) == 0:
            emb = await utils.embed(ctx, "No roles found.",
                                    "Roles are found by naming them with [square] brackets. \n" +
                                    "For example, a role named `[red]` will allow it to be used in this command.")
            await ctx.send(embed=emb)

        # elif arg.lower().casefold() not in guild_roles:
        #     emb = await utils.embed(ctx, "Available colours:", f"`{'`, `'.join(guild_roles)}`")
        #     await ctx.send(embed=emb)

        else:
            strout = ""
            for role in self.valid_roles:
                strout += f"\n{role.name[1:-1]} ({role.mention})"
            # valid_roles = '\n'.join(guild_roles)
            emb = await utils.embed(ctx, "Available colours:", f"{strout}\n\nFor example, `/colour {self.example_role}` will change your colour")
            await ctx.send(embed=emb)

        self.valid_roles = []
        self.role_names = []
        self.example_role = ''

    async def get_roles(self, ctx):
        all_roles = ctx.guild.roles

        for role in all_roles:
            if role.name.startswith("[") and role.name.endswith("]"):
                self.valid_roles.append(role)
                self.role_names.append(role.name[1:-1])
                self.example_role = role if not self.example_role else False


def setup(bot):
    print("INFO: Loading [ColouredRoles]... ", end="")
    bot.add_cog(RoleManager(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [ColouredRoles]")
