from discord.ext import commands
import discord
import importlib
import utils
import requests
import json
importlib.reload(utils)


class Scoresaber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def scoresaber(self, ctx, username):
        """Find players on ScoreSaber (For Beat Saber!)"""
        key = "EA2DF5B468A5BF0A350F01ECDE34C5FA"
        steam_search_response = requests.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={key}&vanityurl={username}")
        steam_search = json.loads(steam_search_response.text)

        if steam_search["response"]["success"] == 1:
            scoresaber_search_response = requests.get(f"https://new.scoresaber.com/api/player/{steam_search['response']['steamid']}/full")
            saberdata = json.loads(scoresaber_search_response.text)

            emb = await utils.embed(ctx, f"Scoresaber Rankings",
                                         f"Player: [{saberdata['playerInfo']['playerName']}](https://steamcommunity.com/id/{saberdata['playerInfo']['playerName']})")
            emb = await utils.field(emb, "Player Ranking:", f"[{saberdata['playerInfo']['rank']:,}](https://scoresaber.com/global) **-** [{saberdata['playerInfo']['country']} #{saberdata['playerInfo']['countryRank']:,}](https://scoresaber.com/global?country={saberdata['playerInfo']['country']})")
            emb = await utils.field(emb, "Performance Points:", f"{saberdata['playerInfo']['pp']:,}pp")
            emb = await utils.field(emb, "Play Count:", f"{saberdata['scoreStats']['totalPlayCount']}")
            emb = await utils.field(emb, "Total Score:", f"{saberdata['scoreStats']['totalScore']:,}")

            await ctx.send(embed=emb)
        elif steam_search["response"]["success"] == 42:
            emb = await utils.embed(ctx,
                                    f"Scoresaber Rankings",
                                    f"No player exists by this name. Make sure you're using the proper Steam name for this user.")
            await ctx.send(embed=emb)

def setup(bot):
    print("INFO: Loading [Scoresaber]... ", end="")
    bot.add_cog(Scoresaber(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Scoresaber]")


# {
#   "playerInfo": {
#     "playerid": "76561198037337491",
#     "pp": 2148.14,
#     "banned": 0,
#     "inactive": 0,
#     "name": "Lexicade",
#     "country": "JE",
#     "role": "",
#     "badges": [],
#     "history": "999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,
#     999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,
#     999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,999999,8928,8386,8409,8425,
#     8433,8449,8461",
#     "avatar": "/api/static/avatars/76561198037337491.jpg",
#     "rank": 8432,
#     "countryRank": 1
#   },
#   "scoreStats": {
#     "totalScore": 302062168,
#     "totalRankedScore": 11682847,
#     "averageRankedAccuracy": 72.89048058163223,
#     "totalPlayCount": 695,
#     "rankedPlayCount": 43
#   }
# }
