from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)
import random


class Magic8Ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="8ball",
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="question",
                    description="Ask the 8ball a question.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    async def _8ball(self, ctx, question):
        """Ask it a question."""
        if hasattr(ctx, 'given_values'):
            content = ctx.given_values['question']
        else:
            content = ctx.message.content

        if content.endswith("?"):
            lst_8_ball = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
                          "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
                          "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
                          "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                          "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
                          "Very doubtful."]
            str_response = lst_8_ball[random.randint(0, len(lst_8_ball) - 1)]
            emb = await utils.embed(ctx, "\🎱 8 Ball \🎱", f"\🇶: {question}\n\n\🇦: {str_response}")
            await ctx.send(embed=emb)
        else:
            emb = await utils.embed(ctx, "8 Ball", "Ask a question!")
            await ctx.send(embed=emb)


def setup(bot):
    print("INFO: Loading [8ball]... ", end="")
    bot.add_cog(Magic8Ball(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [8ball]")
