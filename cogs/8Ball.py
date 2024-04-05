from discord.ext import commands
from discord import app_commands
import discord
import importlib
import utils
importlib.reload(utils)
import random


class Magic8Ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='8ball', description='Ask the 8 ball a question')
    async def _8ball(self, interaction: discord.Interaction, question: str):
        if question.endswith("?"):
            lst_8_ball = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
                          "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
                          "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
                          "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                          "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
                          "Very doubtful."]
            emb = await utils.embed(interaction, "\🎱 8 Ball \🎱", f"\🇶: {question}\n\n\🇦: {random.choice(lst_8_ball)}")
        else:
            emb = await utils.embed(interaction, "8 Ball", "Ask a question that ends with `?`.")
        await interaction.response.send_message(embed=emb, ephemeral=False)


async def setup(bot):
    print("INFO: Loading [8ball]... ", end="")
    await bot.add_cog(Magic8Ball(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [8ball]")
