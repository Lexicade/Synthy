import os

from discord.ext import commands
import discord
import requests
import json
import importlib
import utils
importlib.reload(utils)


class Define(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Define] "

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="word",
                    description="The word you want a definition for.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    @commands.bot_has_permissions(embed_links=True)
    async def define(self, ctx, word):
        """Gives you definitions of a word according to the Oxford English Dictionary."""
        app_id = os.environ.get('oxford_app_id')
        app_key = os.environ.get('oxford_app_key')
        language = "en-gb"

        url_define = f"https://od-api.oxforddictionaries.com:443/api/v2/entries/{language}/{word.lower()}"
        result_define = requests.get(url_define, headers={"app_id": app_id, "app_key": app_key})
        print(result_define.text)
        data_define = json.loads(result_define.text)

        def_dict = {}
        if "error" in data_define:
            # Create embedded message
            emb = await utils.embed(ctx, f"Definitions for `{word}`", "No definitions found.")
            await ctx.send(embed=emb)

        else:
            for lexicalEntries in data_define["results"][0]["lexicalEntries"]:
                category = lexicalEntries["lexicalCategory"]["text"]
                def_dict[category] = ""

                # Added this check as some words appear to have 'subsenses' instead of 'senses'. Fuckers.
                # print(f"{lexicalEntries['entries'][0]}")
                if 'definitions' in lexicalEntries['entries'][0]['senses'][0]:
                    for i, definition in enumerate(lexicalEntries['entries'][0]['senses'], start=1):
                        def_dict[category] = f"{def_dict[category]}**{i})** {definition['definitions'][0]}\n"
                # elif 'subsenses' in lexicalEntries['entries'][0]['senses'][0]:
                #     for i, definition in enumerate(lexicalEntries['entries'][0]['senses'][0]['subsenses'], start=1):
                #         def_dict[category] = f"{def_dict[category]}**{i})** {definition['definitions'][0]}\n"
                else:
                    for i, definition in enumerate(lexicalEntries['entries'][0]['senses'][0]['crossReferenceMarkers'], start=1):
                        def_dict[category] = f"{def_dict[category]}**{i})** {definition}\n"

            # Create embedded message
            emb = await utils.embed(ctx, f"Definitions for `{word}`", "")
            for item in def_dict:
                emb = await utils.field(emb, item, def_dict[item])
            await ctx.send(embed=emb)

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="word",
                    description="The word you want a definition for.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    @commands.bot_has_permissions(embed_links=True)
    async def urban(self, ctx, word):
        """Gives you definitions of a word according to the Urban Dictionary."""
        url_urban = f"http://api.urbandictionary.com/v0/define?term={word.lower()}"
        result_urban = requests.get(url_urban)
        data_urban = json.loads(result_urban.text)
        str_def = ""

        for i, item in enumerate(data_urban["list"]):
            char_trail = "..."
            char_limit = 187 - len(char_trail)

            if len(item['definition']) > char_limit:
                item_def = f"{item['definition'][:char_limit]}..."
            else:
                item_def = f"{item['definition']}"

            str_definition = item_def.replace('\r', '').replace('\n', ' ')
            str_def = str_def + f"**{i+1})** {str_definition}\n"

        emb = await utils.embed(ctx, f"Urban definitions for `{word}`", str_def)
        await ctx.send(embed=emb)


def setup(bot):
    print("INFO: Loading [Define]... ", end="")
    bot.add_cog(Define(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Define]")
