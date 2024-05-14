from discord.ext import commands
from discord import app_commands
import discord
import wikipedia
import fuzzywuzzy
import importlib
import utils
importlib.reload(utils)


class Wiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def wiki(self, interaction: discord.Interaction, wiki_search: str):
        """Query Wikipedia."""
        try:
            wiki_result = wikipedia.WikipediaPage(wiki_search)
            # print(wiki_result.summary)
            wiki_summary = wiki_result.summary[:1900]
            wiki_url = wiki_result.url

            emb = await utils.embed(interaction, f"{wiki_search}", f"{wiki_summary}", url=wiki_url)
            await interaction.response.send_message(embed=emb)

        except wikipedia.DisambiguationError as e:
            emb = await utils.embed(interaction, f"{wiki_search} may refer to:", "\n".join(e.options))
            await interaction.response.send_message(embed=emb)

        except wikipedia.PageError as e:
            search_suggestions = wikipedia.search(wiki_search)

            if len(search_suggestions) > 0:
                emb = await utils.embed(interaction, f"No results found for {wiki_search}.\nDid you mean: ",
                                        "\n".join(search_suggestions))
                await interaction.response.send_message(embed=emb)
            else:
                emb = await utils.embed(interaction, f"No results found for {wiki_search}.", "")
                await interaction.response.send_message(embed=emb)



async def setup(bot):
    print("INFO: Loading [Wiki]... ", end="")
    await bot.add_cog(Wiki(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Wiki]")
