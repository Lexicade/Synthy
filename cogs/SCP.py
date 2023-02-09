from discord.ext import commands
import discord
import requests
import re
from bs4 import BeautifulSoup as soup
import importlib
import utils
importlib.reload(utils)


class SCP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.defer(ephemeral=False)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def scp(self, ctx, scp_id):
        # Ensure url is given a three digit ID
        wiki_url = f"http://www.scp-wiki.net/scp-{scp_id.rjust(3, '0')}"

        # Test if page exists
        scp_html = requests.get(wiki_url)
        if scp_html.status_code == 404:
            scp_embed = discord.Embed(title=f"The SCP foundation has not published this file.",
                                      description="")
            await ctx.send(embed=scp_embed)
            return

        # Collect data for the SCP
        scp_url = await self.get_title_url(scp_id)
        if scp_url is None:
            scp_embed = discord.Embed(title=f"No information currently exists for SCP-{scp_id}.",
                                      description="")
            await ctx.send(embed=scp_embed)
            return

        scp_class, scp_desc = await self.get_details(scp_html)
        scp_name = await self.get_name(scp_id, scp_url)

        emb = await utils.embed(ctx, f"{scp_name}", "", url=wiki_url)

        try:
            scp_classification_name = scp_class.split(": ")[0]
        except Exception as e:
            print(f"scp_class:{scp_class} --- e:{e}")
            scp_classification_name = "Class: "

        try:
            scp_classification_type = scp_class.split(": ")[1]
        except Exception as e:
            print(f"scp_class:{scp_class} --- e:{e}")
            scp_classification_type = "Unknown"

        emb = await utils.field(emb, scp_classification_name, scp_classification_type)
        emb = await utils.field(emb, "Description:", scp_desc)

        await ctx.send(embed=emb)

    async def get_details(self, scp_html):
        scp_soup = soup(scp_html.text, 'html.parser')
        # scp_soup = .replace('style="text-decoration: line-through;"', "~~")
        scp_p = scp_soup.find_all("p")
        scp_class = None
        scp_desc = None

        html_purge = {'<span style="text-decoration: line-through;">': '~~',
                      '<span style="font-size:0%;">': '~~',
                      '</span>': '~~',
                      '<p>': '',
                      '</p>': '',
                      '<strong>': '',
                      '</strong>': ''}

        for i in scp_p:

            class_list = ["<strong>Object Class:</strong>",
                          "<strong>Object Class</strong>:",
                          "<strong>Anomaly Class:</strong>",
                          "<strong>Anomaly Class</strong>:",
                          "<strong>Library Class:</strong>",
                          "<strong>Library Class</strong>:"]

            # for class_item in class_list:
            #     print(i, class_item, class_item in i)

            if any(ext in str(i) for ext in class_list):
                for tag_name in html_purge:
                    i = str(i).replace(tag_name, html_purge[tag_name])
                scp_class = str(i)

            elif "<strong>Description:</strong>" in str(i):
                if "text-decoration: line-through" in str(i):
                    for tag_name in html_purge:
                        i = str(i).replace(tag_name, html_purge[tag_name])
                scp_desc = i.get_text().replace("Description: ", "")
                if len(scp_desc) > 950:
                    scp_desc = scp_desc[:950] + "[...]"

        if scp_class is None:
            scp_span = scp_soup.find_all("span")
            for i in scp_span:
                if "<strong>Object Class:</strong>" in str(i):
                    print(f"i{i}")
                    scp_class = str(i).replace("Object Class: ", "")

                elif "<strong>Anomaly Class:</strong>" in str(i):
                    print(f"i{i}")
                    scp_class = str(i).replace("Anomaly Class: ", "")

                elif "<strong>Library Class:</strong>" in str(i):
                    print(f"i{i}")
                    scp_class = str(i).replace("Library Class: ", "")

        scp_class = self.cleanhtml(scp_class)
        scp_desc = self.cleanhtml(scp_desc)
        return scp_class, scp_desc

    async def get_title_url(self, id):
        if str(id).lower().endswith("-j"):
            return "http://www.scp-wiki.net/joke-scps"

        elif int(id) <= 0:
            return None

        elif int(id) <= 999:
            return "http://www.scp-wiki.net/scp-series"

        elif int(id) <= 1999:
            return "http://www.scp-wiki.net/scp-series-2"

        elif int(id) <= 2999:
            return "http://www.scp-wiki.net/scp-series-3"

        elif int(id) <= 3999:
            return "http://www.scp-wiki.net/scp-series-4"

        elif int(id) <= 4999:
            return "http://www.scp-wiki.net/scp-series-5"

        else:
            return None

    async def get_name(self, id, url):
        scp_html = requests.get(url)
        scp_soup = soup(scp_html.text, 'html.parser')

        scp_p = scp_soup.find_all("li")
        scp_name = None

        for i in scp_p:
            if str(id) in str(i.get_text()):
                scp_name = i.get_text()
        return scp_name

    def cleanhtml(self, raw_html: str):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(str(cleanr), '||', str(raw_html))
        cleantext = cleantext.replace("~~", "||")
        return cleantext


def setup(bot):
    print("INFO: Loading [SCP]... ", end="")
    bot.add_cog(SCP(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [SCP]")
