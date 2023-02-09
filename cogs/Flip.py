from discord.ext import commands
import discord
import re
import upsidedown
import importlib
import utils
importlib.reload(utils)


class Flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Flip] "

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="unflipped_thing",
                    description="Flip friends, family, small children, that dog next door. Everything.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    async def flip(self, ctx, unflipped_thing):
        """Flip friends, family, small children, that dog next door. Everything."""
        # Check if flip is being used on a user
        str_input_re = str(re.findall(r'@!?[0-9]{15,20}', unflipped_thing))[3:-2]
        str_flip = "(╯°□°）╯︵ "

        unflipped_thing = unflipped_thing.replace("ǝuoʎɹǝʌǝ@", "ǝuoʎɹǝʌǝ").replace("ǝɹǝɥ@", "ǝɹǝɥ")

        if str_input_re == '':
            await ctx.send(str_flip + upsidedown.transform(unflipped_thing))

        elif str_input_re.startswith("!"):

            obj_member = ctx.message.guild.get_member(int(str_input_re[1:]))
            flipped_string = upsidedown.transform(str(obj_member.display_name))
            await ctx.send(str_flip + flipped_string)

        else:
            flipped_string = upsidedown.transform(self.bot.get_user(int(str_input_re)).name)
            await ctx.send(str_flip + flipped_string)


def setup(bot):
    print("INFO: Loading [Flip]... ", end="")
    bot.add_cog(Flip(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Flip]")
