from discord.ext import commands
import discord
import re
import upsidedown
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


class Flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Flip] "

    @commands.command()
    async def flip(self, ctx, *, arg):
        """Release your anger and flip everything."""
        str_input_re = str(re.findall(r'@!?[0-9]{15,20}', arg))[3:-2]
        str_flip = "(╯°□°）╯︵ "

        arg = arg.replace("ǝuoʎɹǝʌǝ@", "ǝuoʎɹǝʌǝ").replace("ǝɹǝɥ@", "ǝɹǝɥ")

        if str_input_re == '':
            await ctx.message.channel.send(str_flip + upsidedown.transform(arg))

        elif str_input_re.startswith("!"):

            obj_member = ctx.message.guild.get_member(int(str_input_re[1:]))
            flipped_string = upsidedown.transform(str(obj_member.display_name))
            await ctx.message.channel.send(str_flip + flipped_string)

        else:
            flipped_string = upsidedown.transform(self.bot.get_user(int(str_input_re)).name)
            await ctx.message.channel.send(str_flip + flipped_string)


def setup(bot):
    print("INFO: Loading [Flip]... ", end="")
    bot.add_cog(Flip(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Flip]")
