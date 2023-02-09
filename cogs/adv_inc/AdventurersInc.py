import configparser
import pymysql
from discord.ext import commands
import discord
import importlib
import utils

from cogs.adv_inc import PlayerStats
from cogs.adv_inc import PlayerCreate
from cogs.adv_inc import LevelUp
from cogs.adv_inc import Resting
from cogs.adv_inc import Combat

importlib.reload(utils)
importlib.reload(PlayerStats)
importlib.reload(PlayerCreate)
importlib.reload(LevelUp)
importlib.reload(Resting)
importlib.reload(Combat)


class AdventurersInc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def a(self, ctx, *arg):
        if "adventurers-inc" in str(ctx.channel):
            # Variables
            str_input_group = ctx.message.content.split(" ")
            try:
                str_cmd1 = ctx.message.content.split(" ")[1]
            except:
                str_cmd1 = ""
            try:
                str_cmd2 = ctx.message.content.split(" ")[2]
            except:
                str_cmd2 = ""

            # config = configparser.ConfigParser()
            # config.read(r'config.ini')
            # str_player_state = "debug"
            # params = {'LiveDB': 'AdventurersInc',
            #           'LiveVersion': '1.0',
            #           'GameVersion': '1.3.1',
            #           'Nick': ctx.author.id,
            #           "db": '5.135.189.226',
            #           'dbuser': 'adventure',
            #           'dbpass': 'egg',
            #           'cmd1': str_cmd1,
            #           'cmd2': str_cmd2,
            #           'msg': ctx.message.content[3:]}
            params = {'game_version': '1.4',
                      'nick': ctx.author.id,
                      'ctx': ctx,
                      'cmd1': str_cmd1,
                      'cmd2': str_cmd2,
                      'msg': ctx.message.content[3:]}

            player_stats = await PlayerStats.refresh_stats(params)
            # print(player_stats)

            str_output = 'Oh hi there...   \\_(:o」∠)\\_'
            # Global Commands
            if str_cmd1 == "git":
                str_output = "Adventurers Inc - git: http://www.blatech.co.uk/JasonFS/Artifact-v2"
            elif str_cmd1 == "version":
                str_output = "Adventurers Inc - alpha 0.1"
            else:
                # Actions based on player state
                if player_stats is None:
                    print("OH GOD NO")
                    str_output = await PlayerCreate.pick_character_clan(params)

                elif player_stats["player_state"] == "creation_name":
                    str_output = await PlayerCreate.pick_character_name(params, player_stats)

                elif player_stats["player_state"] == "creation_race":
                    str_output = await PlayerCreate.pick_character_race(params, player_stats)

                elif player_stats["player_state"] == "rest" and player_stats['attribute_points'] > 0:
                    str_output = await LevelUp.level_up_attributes(params)

                elif player_stats["player_state"] == "rest" and player_stats['attribute_points'] == 0:
                    str_output = await Resting.player_resting(params, player_stats)

                elif player_stats["player_state"] == "combat":
                    str_output = await Combat.player_in_combat(params)

                if str_output is not None:
                    if type(str_output) == str or type(str_output) == dict:
                        await ctx.send(content=f"{ctx.author.mention}: {str_output}")
                    else:
                        await ctx.send(content=f"{ctx.author.mention}", embed=str_output)
        else:
            await ctx.send(content=f"Wrong channel {ctx.channel}")


def setup(bot):
    print("INFO: Loading [Adventurers Inc]... ", end="")
    bot.add_cog(AdventurersInc(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Adventurers Inc]")
