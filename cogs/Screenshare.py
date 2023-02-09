from discord.ext import commands
import discord
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


class Screenshare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Screenshare] "

    @commands.command()
    async def screenshare(self, ctx):
        """Allows you to start a screenshare from a voice channel."""
        guild_id = ctx.message.channel.guild.id
        voice_state = ctx.message.author.voice

        if voice_state is None:
            def_embed = discord.Embed(title=f"No voice channel found.",
                                      description=f"Make sure you're in a voice channel before sharing your screen.",
                                      colour=colours["red"])
            await ctx.message.channel.send(embed=def_embed)

        else:
            channel_url = f"https://discordapp.com/channels/{guild_id}/{voice_state.channel.id}"
            def_embed = discord.Embed(title=f"Screen Share",
                                      description=f"Screenshare in [{voice_state.channel}]({channel_url}) " +
                                                  "Be sure to connect to the voice channel first!",
                                      colour=colours["blue"])
            await ctx.message.channel.send(embed=def_embed)


def setup(bot):
    print("INFO: Loading [Screenshare]... ", end="")
    bot.add_cog(Screenshare(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Screenshare]")
