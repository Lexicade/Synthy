from discord.ext import commands
import discord
import random
colours = {"default": 0,
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


class Train(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Train] "

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def train(self, ctx):
        """Release your anger and flip everything."""
        t1 = random.randint(6, 16)
        t2 = random.randint(5, 8)
        t3 = random.randint(6, 16)
        train = "W"

        i=0
        while i < t1:
            train = train + "O"
            i = i + 1

        i=0
        while i < t2:
            train = train + "o"
            i = i + 1

        i=0
        while i < t3:
            train = train + "O"
            i = i + 1

        await ctx.send(train)


def setup(bot):
    print("INFO: Loading [Train]... ", end="")
    bot.add_cog(Train(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Train]")
