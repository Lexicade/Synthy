from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)
import random


class ButtBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[ButtBot] "

    def channel_check(ctx):
        return ctx.message.channel.id in [458613595060830238]

    @commands.Cog.listener()
    @commands.check(channel_check)
    async def on_message(self, ctx, *args):
        if ctx.author == self.bot.user:
            return

        butt_settings = await utils.sql('SELECT buttbot_on, buttbot_freq FROM buttbot WHERE guild_id = %s and bot_name = %s;', (ctx.guild.id, self.bot.user.name))
        if not butt_settings:
            return

        dice_roll = random.randint(1, butt_settings[0]["buttbot_freq"])
        word_count = len(ctx.content.split(" "))
        if dice_roll == 1 and word_count > 3 and butt_settings[0]['buttbot_on'] == 1:
            lst_words = ctx.content.split(" ")
            random_key = random.randint(1, len(lst_words)) - 1
            lst_words[random_key] = "butt"
            new_string = " ".join(lst_words)
            await ctx.channel.send(content=new_string)

    @commands.group(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="on",
                    description="Turn ButtBot On",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="off",
                    description="Turn ButtBot Off",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="frequency",
                    description="Change how often ButtBot fires",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                )
            ],
        )
    )
    async def buttbot(self, ctx):
        """Allow Synthy to add more butts to your conversations."""
        prefix = await self.bot.get_prefix(ctx.message)

        butt_settings = await utils.sql('SELECT buttbot_on, buttbot_freq FROM buttbot WHERE guild_id = %s and bot_name = %s;', (ctx.guild.id, self.bot.user.name))

        if not butt_settings:
            butt_settings = [{'buttbot_on': 0, 'buttbot_freq': 300}]

        butt_settings[0]['buttbot_on'] = "On" if butt_settings[0]['buttbot_on'] == 1 else "Off"

        emb = await utils.embed(ctx, f"Commands for `{prefix[2]}buttbot`", "ButtBot sometimes reposts a message but replaces a word with `butt`")
        emb = await utils.field(emb, f"{prefix[2]}buttbot off/on", f"Toggle ButtBot on or off. (Off by default, currently: {butt_settings[0]['buttbot_on']})")
        emb = await utils.field(emb, f"{prefix[2]}buttbot freq [number]", f"This number determines how often ButtBot will work. A lower number means more butts. (300 by default, currently: {butt_settings[0]['buttbot_freq']})")
        await ctx.send(embed=emb)

    @buttbot.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    @commands.has_permissions(administrator=True)
    async def on(self, ctx):
        """Turn ButtBot On"""
        await utils.sql('INSERT INTO buttbot (guild_id, buttbot_freq, buttbot_on, bot_name) VALUES (%s, %s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET buttbot_on = %s', (ctx.guild.id, 300, True, self.bot.user.name, True,))
        emb = await utils.embed(ctx, "ButtBot", f"ButtBot is now **on** for this server.")
        await ctx.send(embed=emb)

    @buttbot.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    @commands.has_permissions(administrator=True)
    async def off(self, ctx):
        """Turn ButtBot Off"""
        await utils.sql('INSERT INTO buttbot (guild_id, buttbot_freq, buttbot_on, bot_name) VALUES (%s, %s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET buttbot_on = %s', (ctx.guild.id, 300, False, self.bot.user.name, False,))
        emb = await utils.embed(ctx, "ButtBot", f"ButtBot is now **off** for this server.")
        await ctx.send(embed=emb)

    @buttbot.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="frequency",
                    description="Change how often ButtBot fires",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                )
            ],
        )
    )
    @commands.has_permissions(administrator=True)
    async def freq(self, ctx, frequency):
        """Change how often ButtBot fires"""
        try:
            buttbot_freq = int(frequency)
            if buttbot_freq <= 0:
                emb = await utils.embed(ctx, "ButtBot Frequency", "The frequency must be a number above 0.", colour="red")
                await ctx.send(embed=emb)
                return
        except ValueError:
            emb = await utils.embed(ctx, "ButtBot Frequency", "Please provide a valid number", colour="red")
            await ctx.send(embed=emb)
            return


        await utils.sql('INSERT INTO buttbot (guild_id, buttbot_freq, buttbot_on, bot_name) VALUES (%s, %s, %s, %s) ON CONFLICT (guild_id) DO UPDATE SET buttbot_freq = %s;',
                        (ctx.guild.id, buttbot_freq, True, self.bot.user.name, buttbot_freq,))

        emb = await utils.embed(ctx, "ButtBot Frequency", f"The ButtBot frequency has been set to `{buttbot_freq}`. Remember that the lower this is set, the more butts you'll see.")
        await ctx.send(embed=emb)


def setup(bot):
    print("INFO: Loading [ButtBot]... ", end="")
    bot.add_cog(ButtBot(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [ButtBot]")
