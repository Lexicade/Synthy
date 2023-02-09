from discord.ext import commands
import discord
import re
import operator
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


class OutstandingNeighbor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Outstanding Neighbor] "

    @commands.command(pass_context=True, hidden=True)
    async def on(self, ctx, *arg):
        """Release your anger and flip everything."""
        # Purge comment code
        str_cnl = self.bot.get_channel(451575153185390643)
        lst_users = {}
        int_vote_count = 0

        async for message_scan in str_cnl.history(limit=100, before=None, after=None):
            if not message_scan.pinned:
                str_msg = await str_cnl.fetch_message(message_scan.id)

                msg_string = re.search(r'@!?[0-9]{15,20}', str_msg.content)
                if msg_string is None:
                    continue
                msg_string = str(re.search(r'[0-9]{15,20}', str(msg_string)).group())

                obj_user = self.bot.get_user(int(msg_string))

                if len(arg) > 0 and arg[0] == obj_user.name:
                    continue

                try:
                    lst_users[obj_user.name] = int(lst_users[obj_user.name]) + 1
                except Exception as e:
                    lst_users[obj_user.name] = 1
                int_vote_count = int_vote_count + 1

        lst_users_sorted = sorted(lst_users.items(), key=operator.itemgetter(1), reverse=True)

        str_msg = "```"
        # intTotal = len(lst_users_sorted)

        for item in lst_users_sorted:
            str_count = str(item[1])
            str_name = str(item[0])
            int_percent = round((item[1] * 100) / int_vote_count, 2)
            str_percent = str(int_percent) + "%"
            while len(str_percent) < 6:
                str_percent = str_percent + " "

            str_msg = str_msg + str_count + " | " + str_percent + " | " + str_name + "\r\n"

        str_msg = str_msg + "Total: " + str(int_vote_count) + "\r\n"

        str_msg = str_msg+"```"
        await ctx.send(str_msg)

    @commands.command()
    async def site(self, ctx):
        await ctx.send(content="http://streamneighborhood.com")


def setup(bot):
    print("INFO: Loading [OutstandingNeighbor]... ", end="")
    bot.add_cog(OutstandingNeighbor(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [OutstandingNeighbor]")
