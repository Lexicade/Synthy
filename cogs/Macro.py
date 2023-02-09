from discord.ext import commands
import discord
import pickle
import os
import MySQLdb
import configparser
from discord.ext.commands.cooldowns import BucketType
import time
import datetime
colours = { "default": 0,
           "teal": 0x1abc9c,
           "dark teal": 0x11806a,
           "green": 0x2ecc71,
           "dark green": 0x1f8b4c,
           "blue": 0x3498db,
           "dark blue": 0x206694,
           "purple": 0x9b59b6,
           "dark purple": 0x71368a,
           "magenta": 0xe91e63,
           "dark magenta": 0xad1457,
           "gold": 0xf1c40f,
           "dark gold": 0xc27c0e,
           "orange": 0xe67e22,
           "dark orange": 0xa84300,
           "red": 0xe74c3c,
           "dark red": 0x992d22,
           "lighter grey": 0x95a5a6,
           "dark grey": 0x607d8b,
           "light grey": 0x979c9f,
           "darker grey": 0x546e7a,
           "blurple": 0x7289da,
           "greyple": 0x99aab5}


class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global cooldown_dict
        cooldown_dict = {}

    def blacklist_check(ctx):
        # Read config
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Create database link
        db = MySQLdb.connect(host=config["mysqldb"]["host"], user=config["mysqldb"]["user"],
                             passwd=config["mysqldb"]["passwd"], db=config["mysqldb"]["db"])
        c = db.cursor()
        c.execute("SELECT `user_id` from `blacklist` WHERE `user_id` = %s" % str(ctx.author.id))
        result = c.fetchone()

        if result is None:
            return True
        else:
            return

    @staticmethod
    async def cooldown_check(ctx):
        global cooldown_dict
        # if cooldown_dict is None:
        d = datetime.datetime.now()
        unixtime = time.mktime(d.timetuple())
        cooldown_dict[ctx.author.id] = unixtime
        #await ctx.channel.send(content=int(unixtime))

        return True
        # if result is None:
        #     return True
        # else:
        #     return

    def bot_admin_check(ctx):
        # Read config
        config = configparser.ConfigParser()
        config.read('config.ini')

        results = list(map(int, config["conf"]["bot_admins"].split(",")))

        return ctx.message.author.id in list(results)

    @commands.check(blacklist_check)
    @commands.group(invoke_without_command=True)
    async def macro(self, ctx):
        """WIP."""
        prefix = await self.bot.get_prefix(ctx.message)
        prefix.remove(f"<@{self.bot.user.id}> ")
        prefix.remove(f"<@!{self.bot.user.id}> ")
        prefix = prefix[0]
        message_embed = discord.Embed(title=f"Commands for `{prefix}macro`",
                                      description="WIP",
                                      colour=colours["blue"])
        message_embed.add_field(name=f"{prefix}macro add [trigger word] [content]",
                                value="Adds a new macro for you to use.",
                                inline=False)
        message_embed.add_field(name=f"{prefix}macro list",
                                value="Get a list of your current macros", inline=False)
        message_embed.add_field(name=f"{prefix}macro remove [trigger word]",
                                value="Removes a macro from current macros.", inline=False)
        await ctx.send(embed=message_embed)
        True

    @commands.check(blacklist_check)
    @macro.command()
    async def add(self, ctx, *arg):
        arg = list(arg)

        trigger_word = arg.pop(0)
        trigger_phrase = " ".join(arg)

        try:
            user_macros = await self.load_obj(ctx.author.id)
        except EOFError:
            user_macros = {}

        if user_macros is None:
            user_macros = {trigger_word, trigger_phrase}
        else:
            user_macros = dict(user_macros)
            user_macros[trigger_word] = trigger_phrase

        await self.save_obj(user_macros, ctx.author.id)
        await ctx.send(content=f"({trigger_word})({trigger_phrase})")

    @commands.check(blacklist_check)
    @macro.command()
    async def remove(self, ctx, arg):
        arg = str(arg)

        try:
            user_macros = await self.load_obj(ctx.author.id)
        except EOFError:
            user_macros = {}

        reslt = user_macros.pop(arg, "0")
        if reslt is None:
            await ctx.send(content=f"No macro with the name {arg} exists.")
        else:
            await self.save_obj(user_macros, ctx.author.id)
            await ctx.send(content=f"Removed {reslt}")

        # if arg in user_macros:
        #     user_macros.remove(arg)
        #     await ctx.send(content=str(user_macros))
        # else:
        #     await ctx.send(content="No: " + str(user_macros))

    @commands.check(blacklist_check)
    @macro.command()
    async def list(self, ctx):
        user_dict = await self.load_obj(ctx.author.id)

        msg = ""
        offset = 1

        for item in user_dict:
            msg = f"{msg}\n{item}) {user_dict[item]}"

        embed_msg = discord.Embed(title="List of Macros",
                                  description=msg,
                                  colour=colours["blue"])

        await ctx.send(embed=embed_msg)

    # @commands.cooldown(1, 60.0, BucketType.user)
    @commands.check(blacklist_check)
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if await self.cooldown_check(ctx):
            try:
                user_macros = await self.load_obj(ctx.author.id)
            except EOFError:
                user_macros = {}

            for macro in user_macros:
                if macro == ctx.content:
                    await ctx.channel.send(content=user_macros[macro])

    @commands.check(bot_admin_check)
    @macro.command()
    async def blacklist(self, ctx, user: discord.Member):
        # Read config
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Create database link
        db = MySQLdb.connect(host=config["mysqldb"]["host"], user=config["mysqldb"]["user"],
                             passwd=config["mysqldb"]["passwd"], db=config["mysqldb"]["db"])
        c = db.cursor()
        c.execute("INSERT INTO `blacklist` (`user_id`, `reason`) VALUES (%s,'%s');" % (user.id, ""))
        db.commit()

        message_embed = discord.Embed(title=f"Blacklisted {user}",
                                      description="",
                                      colour=colours["blue"])
        await ctx.send(embed=message_embed)

    @staticmethod
    async def save_obj(obj, filename: str):
        with open(f"./macros/{filename}.pkl", 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    async def load_obj(owner_id):
        if not os.path.isfile(f"./macros/{owner_id}.pkl"):
            os.mknod(f"./macros/{owner_id}.pkl")

        with open(f"./macros/{owner_id}.pkl", "rb") as f:
            return pickle.load(f)


def setup(bot):
    print("INFO: Loading [Macro]... ", end="")
    bot.add_cog(Macro(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Macro]")