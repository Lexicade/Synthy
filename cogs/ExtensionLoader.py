import sys

from discord.ext import commands, tasks
import discord
import traceback
import configparser
import os
import json
import importlib
import utils
importlib.reload(utils)


class ExtensionLoader(commands.Cog, name="ExtensionLoader"):
    def __init__(self, bot):
        self.bot = bot
        self.init_load_ext.start()

    @tasks.loop(count=1)
    async def init_load_ext(self):
        # Get list of Cogs from config
        self.check_for_new_cogs(self.bot)
        lst_cogs = self.load_config(f"./config/cogs_{self.bot.user.name}.json")

        # Load all loaded Cogs
        for item in lst_cogs["loaded"]:
            if item != "ExtensionLoader":
                # await self.manage_ext("load", item)
                try:
                    await self.bot.load_extension(f"cogs.{item}")
                except:
                    True

    @staticmethod
    def bot_admin_check(ctx: discord.ext.commands.Context):
        # Read config
        config = configparser.ConfigParser()
        config.read('config.ini')

        results = list(map(int, config["synthy"]["bot_admins"].split(",")))

        if ctx.message.author.id in list(results):
            return True
        else:
            # raise commands.MissingPermissions(['Synthy Administrator'])
            True

    async def manage_ext(self, action: str, extension: str, ctx):
        try:
            if action == "load":
                await self.bot.load_extension(f"cogs.{extension}")
                await ctx.message.add_reaction("✅")

            elif action == "reload":
                await self.bot.reload_extension(f"cogs.{extension}")
                await ctx.message.add_reaction("⚔")
                print(await self.bot.tree.sync())
                await ctx.message.add_reaction("✅")

            elif action == "unload" and os.path.splitext(os.path.basename(__file__))[0] != extension:
                await self.bot.unload_extension(f"cogs.{extension}")
                await ctx.message.add_reaction("✅")

            return

        except discord.ext.commands.ExtensionNotFound as e:
            emb = await utils.embed(ctx, f"{extension}", f"The cog `{e.name}` wasn\'t found. Check this is spelt correctly.")

        except discord.ext.commands.errors.ExtensionNotLoaded as e:
            emb = await utils.embed(ctx, f"{extension} The extension `{e.name}` is not loaded.", "")

        except discord.ext.commands.errors.ExtensionAlreadyLoaded as e:
            emb = await utils.embed(ctx, f"{extension}", f"The extension `{e.name}` is already loaded.")

        except discord.ext.commands.errors.NoEntryPointError as e:
            emb = await utils.embed(ctx, f"{extension}", f"There is not entry point in extension `{e.name}`.")

        except discord.ext.commands.errors.ExtensionFailed as e:
            emb = await utils.embed(ctx, f"Failed to load {extension}", f"There is an execution error in `{e.name}`.\n{e.original}")

            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

        await ctx.send(embed=emb)

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def log(self, ctx, *, extension_name):
        result = await self.config_log_toggle(extension_name, f"./config/cogs_{self.bot.user.name}.json")
        if result:
            emb = await utils.embed(ctx, "Debug Logging", result)
            await ctx.send(embed=emb)

            # print(ctx.guild.me.guild_permissions)
            if ctx.guild.me.permissions_in(ctx.channel).manage_messages:
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction("✅")

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def load(self, ctx, *, extension_name):
        await self.load_to_config(extension_name, f"./config/cogs_{self.bot.user.name}.json")
        await self.manage_ext("load", extension_name, ctx)

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def sync(self, ctx):
        # await discord.app_commands.CommandTree.sync(self.bot)
        print(await self.bot.tree.sync())
        await ctx.message.add_reaction("✅")

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def sync(self, ctx):
        # await discord.app_commands.CommandTree.sync(self.bot)
        eggies = await self.bot.tree.sync(guild=ctx.guild)
        await ctx.message.add_reaction("🧩")
        print(f"SYNC: {eggies}")

    @commands.check(bot_admin_check)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.command(pass_context=True, hidden=True)
    async def reload(self, ctx, *, extension_name):
        await self.manage_ext("reload", extension_name, ctx)

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def unload(self, ctx, *, extension_name):
        await self.manage_ext("unload", extension_name, ctx)

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def slashunload(self, ctx):
        await ctx.message.add_reaction("⌛")
        if self.bot.user.id == 459056626377293824:
            await self.bot.register_application_commands(None)

        elif self.bot.user.id == 900672193543942144:
            guild = self.bot.get_guild(578293484843434061)
            await self.bot.register_application_commands(None, guild=guild)

        await ctx.message.add_reaction("✅")

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def slashload(self, ctx):
        if self.bot.user.id == 459056626377293824 or self.bot.user.id == 1136248096263778334:
            await ctx.message.add_reaction("⌛")
            await self.bot.register_application_commands()

        elif self.bot.user.id == 900672193543942144:
            await ctx.message.add_reaction("🔧")
            guild = self.bot.get_guild(578293484843434061)
            await self.bot.tree.sync(guild=ctx.guild)
            # await self.bot.register_application_commands(guild=guild)

        await ctx.message.add_reaction("✅")

    @commands.check(bot_admin_check)
    @commands.command(pass_context=True, hidden=True)
    async def ohno(self, ctx):
        newnum = 1 / 0

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ext.commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            print(error)
            print(error.__dict__)
            emb = await utils.embed(ctx, f'I can\'t let you do that, ~~Starfox~~ {ctx.author.display_name}!', f'This needs to be done by someone who has these permissions:\n{" ,".join(error.missing_perms)}')
            await ctx.send(embed=emb)

        elif isinstance(error, commands.MemberNotFound):
            emb = await utils.embed(ctx, f'Cannot find user', f'I couldn\'t find that user! Double check the capitalisation as this is case sensitive!')
            await ctx.send(embed=emb)
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            emb = await utils.embed(ctx, f'Unknown command', f'I couldn\'t figure out what you mean, double check the command your using isn\'t missing anything. Is this is a recurring error, you can let my [code monkey](https://discord.gg/bDAa7cu) know.')
            await ctx.send(embed=emb)
            return

        elif not (isinstance(error, commands.CommandNotFound)):
            jokes = ["99 bugs in the code, 99 bugs in the code. You take one down, patch it around... 129 bugs in the code.",
                     "I asked my master why he writes bad code. He said \"No comment.\"",
                     "A code tester walks into the bar and orders 2,147,483,648 beers."]

            # Create user error
            log = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            emb = await utils.notice("That shouldn't happen...",
                                     "I will let my code slave know so he can fix this."+
                                     "You can try this again later or visit [his home](https://discord.gg/bDAa7cu) if you want to speak to him.\n\n"+
                                     "")
            await ctx.send(embed=emb)

            # Create developer error
            err_chnl = self.bot.get_channel(740267554416885842)  # Synthy Server / #debug-synthy-beta
            # err_chnl = self.bot.get_channel(1138216297046491247)  # Lexi Server 2 / #john

            err_body_details = [f'Guild: {ctx.guild.name} ({ctx.guild.id})',
                                f'Channel: {ctx.channel.name} ({ctx.channel.id})',
                                f'Author: {ctx.author.mention} {ctx.author.name} ({ctx.author.id})',
                                f'Command: {ctx.prefix}{ctx.command}  --- Success Status:{ctx.command_failed}']
            if hasattr(ctx, 'message') and hasattr(ctx.message, 'content'):
                err_body_details.append(f'Message: {ctx.message.content}')
            else:
                slash_context = await self.bot.get_slash_context(ctx.interaction)
                err_body_details.append(f'Values: {slash_context.given_values}')
            err_body_errors = '\n'.join(err_body_details)

            err_content = f"<@&649208333626114048> {err_body_errors}"

            err_emb_title = f"{error}"[:256]
            err_emb_body = log[:2048]
            emb = await utils.notice(err_emb_title, err_emb_body)

            await err_chnl.send(content=err_content, embed=emb)

    @staticmethod
    def load_config(config_path):
        with open(config_path) as fp:
            try:
                config = json.load(fp)
            except json.JSONDecodeError as e:
                print(e)
                return None

        return config

    @staticmethod
    def save_config(config_path, config):
        with open(config_path, 'w') as fp:
            json.dump(config, fp, indent=4)

    async def load_to_config(self, cog, config_path):
        config = self.load_config(config_path)

        if cog in config["unloaded"] and not cog in config["loaded"]:
            config["unloaded"].remove(cog)
            config["loaded"].append(cog)
            self.save_config(f"./config/cogs_{self.bot.user.name}.json", config)
            return True
        return False

    async def unload_from_config(self, cog):
        config = self.load_config(config_path)

        if not cog in config["unloaded"] and cog in config["loaded"]:
            config["unloaded"].append(cog)
            config["loaded"].remove(cog)
            self.save_config(f"./config/cogs_{self.bot.user.name}.json", config)
            return True
        return False

    async def config_log_toggle(self, cog, config_path):
        config = self.load_config(config_path)

        if cog in config['debug']['inactive'] and not cog in config['debug']['active']:
            config['debug']['inactive'].remove(cog)
            config['debug']['active'].append(cog)
            self.save_config(f"./config/cogs_{self.bot.user.name}.json", config)
            return f"Logging turned on for {cog}"

        elif cog in config['debug']['active'] and not cog in config['debug']['inactive']:
            config['debug']['active'].remove(cog)
            config['debug']['inactive'].append(cog)
            self.save_config(f"./config/cogs_{self.bot.user.name}.json", config)
            return f"Logging turned off for {cog}"
        return False

    @staticmethod
    def get_cogs():
        cogs = []
        for file in os.listdir("./cogs/"):
            if file.endswith(".py") and not file.startswith("__"):
                cogs.append(file.replace(".py", ""))
        return cogs

    def check_for_new_cogs(self, bot):
        # Get Config
        config_path = f"./config/cogs_{bot.user.name}.json"

        if os.path.exists(config_path):
            config = self.load_config(config_path)
            if not config:
                return "JSON could not be read."
        else:
            config = {"unloaded": [], "loaded": ["ExtensionLoader"], "debug": {"active": [], "inactive": []}}
            with open(f"./config/cogs_{self.bot.user.name}.json", 'w') as config_file:
                json.dump(config, config_file)

        # Get cogs
        cogs = self.get_cogs()

        # Check all cogs
        for cog in cogs:
            if not cog in config["unloaded"] and not cog in config["loaded"]:
                config["unloaded"].append(cog)

            if not cog in config['debug']['active'] and not cog in config['debug']['inactive']:
                config['debug']['inactive'].append(cog)

        # Save config
        self.save_config(config_path, config)
        return "Successfully checked cogs"


async def setup(bot):
    # try:
    print("INFO --- Loading Extensions --- ", end="\n")
    await bot.add_cog(ExtensionLoader(bot))
    print("INFO --- Extensions Loaded --- ", end="\n")
    # except Exception as e:
    #     print(e)


async def teardown(bot):
    print("INFO: Unloading [ExtensionLoader]")
