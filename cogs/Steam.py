from discord.ext import commands
from collections import OrderedDict
import os
import discord
from fuzzywuzzy import fuzz
import requests
import json
import locale
import pickle
import importlib
import utils
importlib.reload(utils)
import time
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


class Steam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        locale.setlocale(locale.LC_ALL, '')

    # @commands.group(invoke_without_command=True)
    # async def steam(self, ctx):
    #     """Search steam for games."""
        # if search == ():
        #     # Create message
        #     prefix = await self.bot.get_prefix(ctx.message)
        #
        #     emb = await utils.embed(ctx, f"Commands for `{prefix[2]}steam`", "", "")
        #     emb = await utils.field(emb, f"{prefix[2]}steam `[text]`", "Return an SCPs info from the scp-wiki")
        #     emb = await utils.field(emb, f"{prefix[2]}steam `[game name]`", "Search for a game on steam")
        #     emb = await utils.field(emb, f"{prefix[2]}steam list `[game name]`", "Search for the closest top 10 games on Steam")
        #     emb = await utils.field(emb, f"{prefix[2]}steam list select `[id]`", "Show a games information from the search list.")
        #     await ctx.send(embed=emb)
        # if ctx.channel.permissions_for(ctx.me).manage_messages:
        #     await ctx.message.delete()

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="game_name",
                    description="Search for a game on the Steam store.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    @commands.defer(ephemeral=False)
    async def steam(self, ctx, *, game_name):
        """Search for a game on the Steam store."""
        # await ctx.channel.trigger_typing()
        # await ctx.interaction.edit_original_message(content="Searching for game...")
        search = " ".join(game_name)
        start_time = time.time()
        # Get live or cached JSON
        json_data = await self.get_json_data()

        # Get 1 match form the given search term
        new_list = await self.get_best_matches(search, 1, json_data)

        if new_list != {}:
            # Collect data for the given AppID
            message_output = await self.steam_by_app_id(new_list["1"]["app_id"])

            # Generate an embed message for the AppID
            if message_output is None:
                emb = await utils.embed(ctx, f"Unable to access information for the game `{new_list['1']['app_name']}`",
                                        "This game/app is likely hidden and will not work.")
                await ctx.send(embed=emb)

            elif type(message_output) == dict:
                emb = await self.create_embed(message_output, ctx, f"\nDone in {round(time.time() - start_time, 2)} seconds.")
                await ctx.interaction.edit_original_message(content=None, embed=emb)
        else:
            await ctx.send(content=f"I couldn't find anything similar to that")

    # @commands.defer(ephemeral=False)
    # @steam.command(invoke_without_command=True)
    # async def list(self, ctx, *search_term):
    #     await ctx.message.channel.trigger_typing()
    #     search_term = " ".join(search_term)
    #
    #     # Load steam search config
    #     try:
    #         loaded_obj = await self.load_obj("steam")
    #     except EOFError:
    #         loaded_obj = {}
    #
    #     # Get live or cached JSON
    #     json_data = await self.get_json_data()
    #     top_matches = await self.get_best_matches(search_term, 10, json_data)
    #     best_ten = ""
    #     for item in top_matches:
    #         best_ten = best_ten + f"**{item})** {top_matches[item]['app_name']} `({top_matches[item]['app_match']}%)`\n"
    #     best_ten = best_ten + "\nThese are the closest 10 matches.\nUse the list select `[id]` command to pick an item from this list."
    #
    #     search_json = {f"{ctx.guild.id}#{ctx.author.id}": top_matches}
    #     await self.save_obj(search_json, "steam")
    #
    #     # Print output
    #     message_embed = discord.Embed(title="", description=best_ten, colour=colours["blue"])
    #     message_embed.set_footer(text=f"Requested by {ctx.message.author}.")
    #     message_embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
    #
    #     await ctx.send(embed=message_embed)
    #
    # @list.command()
    # async def select(self, ctx, *, search_int):
    #     ret = await self.load_obj("steam")
    #
    #     if f"{ctx.guild.id}#{ctx.author.id}" in str(ret):
    #         for i, item in enumerate(ret[f"{ctx.guild.id}#{ctx.author.id}"].values()):
    #             if i+1 == int(search_int):
    #                 # Collect data for the given AppID
    #                 message_output = await self.steam_by_app_id(item["app_id"])
    #
    #                 # Generate an embed message for the AppID
    #                 if message_output is None:
    #                     message_embed = discord.Embed(title=f"Unable to access information for the game `{item['app_name']}`",
    #                                                   description="This game/app is likely hidden and will not work.",
    #                                                   colour=colours["blue"])
    #                     await ctx.send(embed=message_embed)
    #
    #                 elif type(message_output) == dict:
    #                     app_embed = await self.create_embed(message_output, ctx)
    #                     await ctx.send(embed=app_embed)
    #
    #                     ret.pop(f"{ctx.guild.id}#{ctx.author.id}", None)
    #                     await self.save_obj(ret, "steam")
    #
    #     else:
    #         await ctx.send(content="No search results to use.")

    async def create_embed(self, message_output, ctx, footer=""):
        message_output["description"] = message_output["description"].replace("&amp;", "&").replace("&quot;", "\"")

        emb = await utils.embed(ctx, message_output["name"], message_output["description"], url=message_output["url"], image=message_output["image"], footer=footer)
        emb = await utils.field(emb, "Price", message_output["cost"] + " " + message_output["discount"])
        emb = await utils.field(emb, "Platforms", value=message_output["support"], inline=True)
        emb = await utils.field(emb, "Reviews", value=message_output["reviews"], inline=True)

        val_release = "N/A" if message_output["releasedate"] == "" else message_output["releasedate"]
        emb = await utils.field(emb, "Release Date", value=val_release, inline=True)
        return emb

    async def get_json_data(self):
        response = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2")
        json_data = json.loads(response.text)

        if json_data == {'applist': {'apps': []}}:
            with open('./cogs/steam_app_cache.json') as json_file:
                json_data = json.load(json_file)
        return json_data

    async def get_best_matches(self, search_term, return_total, json_data):
        lst_all_results = []
        for i, item in enumerate(json_data['applist']['apps']):
            # print(f"var: {search_term}  - type:{type(search_term)}")
            # print(f"var: {str(item['name']).lower()}  - type:{type(str(item['name']).lower())}")

            app_match = fuzz.ratio(str(item['name']).lower(), search_term.lower())
            lst_all_results.append({"app_match": app_match, "app_id": str(item['appid']), "app_name": str(item['name'])})
        lst_all_results_sorted = sorted(lst_all_results, key=lambda k: k["app_match"], reverse=True)

        return_dict = {}
        for i, item in enumerate(lst_all_results_sorted[:return_total]):
            app_key = i+1

            return_dict[str(app_key)] = {"app_match": item["app_match"],
                                         "app_id": item["app_id"],
                                         "app_name": item["app_name"]}
        return return_dict

    @staticmethod
    async def steam_by_app_id(str_app_id):
        # Obtain and load the JSON
        # https://store.steampowered.com/api/appdetails?appids=204360&cc=gb&filters=price_overview

        game_req = requests.get(f"http://store.steampowered.com/api/appdetails?appids={str_app_id}&cc=gb")
        game_req_data = json.loads(game_req.text)

        if game_req_data[str_app_id]["success"]:
            # Platforms
            game_support_concat = []
            if game_req_data[str_app_id]['data']['platforms']['windows']:
                game_support_concat.append("Windows")
            if game_req_data[str_app_id]['data']['platforms']['linux']:
                game_support_concat.append("Linux")
            if game_req_data[str_app_id]['data']['platforms']['mac']:
                game_support_concat.append("Mac")
            game_support_concat = ", ".join(game_support_concat)

            # Determine price
            game_name = str(game_req_data[str_app_id]['data']['name'])
            game_free = str(game_req_data[str_app_id]['data']['is_free'])
            game_url = f"http://store.steampowered.com/app/{str_app_id}/{game_name.replace(' ', '_')}/"
            if game_free == "True":
                game_cost = "Free"
                game_discount = ""
            else:
                try:
                    game_cost = game_req_data[str_app_id]['data']['price_overview']['final_formatted']
                    game_discount = str(game_req_data[str_app_id]['data']['price_overview']['discount_percent'])
                    if game_discount == "0":
                        game_discount = ""
                    else:
                        game_discount = "(" + game_discount + "% off!)"
                except Exception as e:
                    game_cost = "No Price Listed!"
                    game_discount = ""

            # Get reviews data
            review_request = requests.get(f"https://store.steampowered.com/appreviews/{str_app_id}?json=1&language=all&purchase_type=all")
            review_request_data = json.loads(review_request.text)

            game_details = {"name": game_name,
                            "cost": game_cost,
                            "discount": game_discount,
                            "support": game_support_concat,
                            "description": str(game_req_data[str_app_id]['data']['short_description']),
                            "url": game_url,
                            "image": game_req_data[str_app_id]['data']["header_image"],
                            "reviews": review_request_data["query_summary"]["review_score_desc"],
                            "releasedate": game_req_data[str_app_id]['data']["release_date"]["date"]
                            }
        else:
            game_details = None

        return game_details

    @staticmethod
    async def save_obj(obj, filename: str):
        with open(f"{filename}.pkl", 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    async def load_obj(filename):
        if not os.path.isfile("./steam.pkl"):
            os.mknod("./steam.pkl")

        with open(f"{filename}.pkl", "rb") as f:
            return pickle.load(f)


def setup(bot):
    print("INFO: Loading [Steam]... ", end="")
    bot.add_cog(Steam(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Steam]")

