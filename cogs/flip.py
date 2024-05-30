from discord.ext import commands
from discord import app_commands
import discord
import re
import upsidedown
import importlib
import utils
importlib.reload(utils)


class Flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='flip', description='Flip friends, family, small children, that dog next door. Everything.')
    async def flip(self, interaction: discord.Interaction, unflipped_thing: str):
        # Check if flip is being used on a user
        str_input_re = str(re.findall(r'@!?[0-9]{15,20}', unflipped_thing))[3:-2]
        str_flip = "(╯°□°）╯︵ "

        unflipped_thing = unflipped_thing.replace("ǝuoʎɹǝʌǝ@", "ǝuoʎɹǝʌǝ").replace("ǝɹǝɥ@", "ǝɹǝɥ")

        if str_input_re == '':
            await interaction.response.send_message(str_flip + upsidedown.transform(unflipped_thing))

        elif str_input_re.startswith("!"):

            obj_member = interaction.message.guild.get_member(int(str_input_re[1:]))
            flipped_string = upsidedown.transform(str(obj_member.display_name))
            await interaction.response.send_message(str_flip + flipped_string)

        else:
            flipped_string = upsidedown.transform(self.bot.get_user(int(str_input_re)).name)
            await interaction.response.send_message(str_flip + flipped_string)


async def setup(bot):
    print("INFO: Loading [Flip]... ", end="")
    await bot.add_cog(Flip(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Flip]")
