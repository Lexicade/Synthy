from discord.ext import commands
from discord import app_commands
import os
import discord
import requests
import json
import importlib
import utils

importlib.reload(utils)


class Define(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def define(self, interaction: discord.Interaction, word: str):
        """Gives you definitions of a word according to the Oxford English Dictionary."""
        merriam_key = os.environ.get('merriam_key')
        url_define = f"https://dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={merriam_key}"
        request_data = requests.get(url_define)
        data_define = json.loads(request_data.text)


        # for word_type in defs1:
        #     print(word_type)
        #     for defs in defs1[word_type]:
        #         print(f"• {defs}")

        if 'shortdef' in data_define[0].keys():
            word_definitions = {}
            for data_object in data_define:
                cur_word_type = data_object['fl']
                for short_def in data_object['shortdef']:
                    word_definitions.setdefault(cur_word_type, set()).add(f"• {short_def}")

            # Create embedded message
            emb = await utils.embed(interaction, f"Definitions for `{word}`", "", thumbnail="https://dictionaryapi.com/images/MWLogo_120x120.png", footer="\nPowered by Merriam-Webster's Collegiate® Dictionary")
            for item in word_definitions:
                emb = await utils.field(emb, item, "\n".join(word_definitions[item]))
            await interaction.response.send_message(embed=emb)

        else:
            # Create embedded message
            emb = await utils.embed(interaction, f"Definitions for `{word}`", "No definitions found.")
            await interaction.response.send_message(embed=emb)

    @app_commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def urban(self, interaction: discord.Interaction, word: str):
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
            str_def = str_def + f"**{i + 1})** {str_definition}\n"

        emb = await utils.embed(interaction, f"Urban definitions for `{word}`", str_def)
        await interaction.response.send_message(embed=emb)


async def setup(bot):
    print("INFO: Loading [Define]... ", end="")
    await bot.add_cog(Define(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Define]")
