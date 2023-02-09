from discord.ext import commands
import discord
from discord import abc
import string
import importlib
import utils
import re
importlib.reload(utils)

class Battleship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Flip] "

    @commands.command(hidden=True)
    async def grid(self, ctx, x: int, y: int):
        if (x > 20 or y > 20) or (x < 3 or y < 3):
            await ctx.send("A grid can range only from 3x3 to 20x20")
            return

        play_grid = await self.print_grid(await self.gen_grid(x, y))
        await ctx.send(play_grid)

    @staticmethod
    async def gen_grid(grid_columns, grid_rows):
        grid = {}
        grid_row = {}
        for x in range(grid_rows):
            grid[x] = {}
            for y in range(grid_columns):
                grid_row.update({y: "0"})
            grid[x] = grid_row
        return grid

    @staticmethod
    async def print_grid(grid):
        grid_out = ""
        grid_row = ""

        for x in grid:
            header = "  "
            for y in grid[x]:
                if grid[x][y] == "0":
                    grid_row = f"{grid_row}■ "

                elif grid[x][y] == "1":
                    grid_row = f"{grid_row}X "

                elif grid[x][y] == "-1":
                    grid_row = f"{grid_row}- "

                header = f"{header} {y+1}"

            grid_out = f"{grid_out}\n{x+1}{' ' if len(str(x+1))==2 else '  '}{grid_row}"
            grid_row = ""
        return f"```{header}{grid_out}```"

    async def place_ship(self):
        True
        #command requirements
        # coordinate, horizontal or veritcal, slip length
        # Command candidate !bs 3:1 h 2 (Deprecated)
        # Ships: 3x Twos, 2x Threes, 2x Fours, 1x Five

        # dict values: P = Placement, 1 = Ship, 0 = Empty, ! = P over an existing 1
        # P cannot save over a 1, only 0
        # Emojis needed: up, down, left, right, rotate, tick

    async def play_turn(self):
        True
        #
        #
        #
        #

    async def left(self):
        guild_id = 619676725818949645
        channel_id = 671427190080012298
        message_id = 676425811280003082

    async def grid_to_dict(self):
        str_grid = ("```   1 2 3 4 5 6\n" +
                    "1  ■ ■ ■ ■ ■ ■\n" +
                    "2  ■ ? ■ ■ ■ ■\n" +
                    "3  ■ ? ■ ■ ■ ■\n" +
                    "4  ■ ? ■ ■ ■ ■\n" +
                    "5  ■ ■ ■ ■ ■ ■\n" +
                    "6  ■ ■ ■ ■ ■ ■\n ```")

        dict_grid = {}

        for ir, line_row in enumerate(str_grid.splitlines()):
            line_row = re.search(r"(([■+\-?])\s?)+", line_row)
            if line_row is not None:
                line_row = line_row.group().split(" ")

                dict_grid_row = {}
                for ic, line_column in enumerate(line_row):
                    dict_grid_row.update({ic: line_column})

                dict_grid[ir - 1] = dict_grid_row
        print(dict_grid)

    @commands.command(hidden=True)
    async def bssend(self, ctx):
        await ctx.author.send("oh no")

    @commands.command(hidden=True)
    async def bsemote(self, ctx):
        msg = await abc.Messageable.fetch_message(ctx.author, 688065915790688361)
        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")
        await msg.add_reaction("\U0001F504") # counter clockwise arrows
        await msg.add_reaction("\U00002705") # white_check_mark

        # http://www.fileformat.info/info/emoji/list.htm


def setup(bot):
    print("INFO: Loading [Battleship]... ", end="")
    bot.add_cog(Battleship(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Battleship]")


# gc = 6
# gr = 4
# play_grid = gen_grid(gc, gr)
# print(play_grid)
# print(print_grid(play_grid))
# # print(print_grid({0: {0: '1', 1: '-1', 2: '-1', 3: '0', 4: '0', 5: '-1', 6: '0', 7: '0', 8: '0', 9: '0'}, 1: {0: '1', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 2: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 3: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 4: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 5: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 6: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 7: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 8: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}, 9: {0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0'}}))



#{0: {0: "B", 1: "H"}, 1: {0: "B", 1: "H"}}

# import re
#
#
# def print_grid(grid):
#     grid_out = ""
#     grid_row = ""
#     header = "  "
#
#     for x in grid:
#         header = "  "
#         for y in grid[x]:
#             grid_row = f"{grid_row}{grid[x][y]} "
#
#             header = f"{header} {y + 1}"
#
#         grid_out = f"{grid_out}\n{x + 1}{' ' if len(str(x + 1)) == 2 else '  '}{grid_row}"
#         grid_row = ""
#     return f"```{header}{grid_out}```"
#
#
# def grid_to_dict(str_grid):
#     dict_grid = {}
#
#     for ir, line_row in enumerate(str_grid.splitlines()):
#         line_row = re.search(r"(([■+\-?])\s?)+", line_row)
#         if line_row is not None:
#             line_row = line_row.group().strip().split(" ")
#
#             dict_grid_row = {}
#             for ic, line_column in enumerate(line_row):
#                 dict_grid_row.update({ic: line_column})
#
#             dict_grid[ir-1] = dict_grid_row
#     return dict_grid
#
#
# grid1 = {0: {0: '■', 1: '■', 2: '■', 3: '■', 4: '■', 5: '■'},
#          1: {0: '■', 1: '?', 2: '■', 3: '■', 4: '■', 5: '■'},
#          2: {0: '■', 1: '?', 2: '■', 3: '■', 4: '■', 5: '■'},
#          3: {0: '■', 1: '?', 2: '■', 3: '■', 4: '■', 5: '■'},
#          4: {0: '■', 1: '■', 2: '■', 3: '■', 4: '■', 5: '■'},
#          5: {0: '■', 1: '■', 2: '■', 3: '■', 4: '■', 5: '■'}}
# grid1 = print_grid(grid1)
# print(grid1)
#
# grid1 = grid_to_dict(grid1)
# print(grid1)