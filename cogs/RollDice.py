from discord.ext import commands
import discord
import re
import random
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


class RollDice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Roll Dice] "

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def roll(self, ctx, *, arg):
        """Roll whatever sided dice you need to roll."""
        demo_roll = re.sub(r'[^\d+\-d-d]', " ", arg)
        print(f"`{demo_roll.strip()}`")

        if demo_roll.strip() is not "":
            output = self.roll_dice(arg)
            await ctx.send(content=output)
        else:
            await ctx.send(content="I wasn't able to get a roll from that.")

    def roll_dice(self, str_input):
            import ast
            import operator
            _OP_MAP = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Invert: operator.neg,
            }

            class Calc(ast.NodeVisitor):

                def visit_BinOp(self, node):
                    left = self.visit(node.left)
                    right = self.visit(node.right)
                    return _OP_MAP[type(node.op)](left, right)

                def visit_Num(self, node):
                    return node.n

                def visit_Expr(self, node):
                    return self.visit(node.value)

                @classmethod
                def evaluate(cls, expression):
                    tree = ast.parse(expression)
                    calc = cls()
                    return calc.visit(tree.body[0])

            # print(f"Processing 0    : {str_input}")

            str_input = re.sub(r'[^\d+\-d-d]', " ", str_input)
            str_input = str_input.replace("+", " ").strip()
            str_input = str_input.replace("-", " -")

            # print(f"Processing 1: {str_input}")

            while "  " in str_input:
                str_input = str_input.replace("  ", " ")
            while r'- #' in str_input:
                str_input = re.sub(r'- #', r'-# ', str_input, )

            # print(f"Processing 2: {str_input}")

            str_input_search = re.search(r'- [\d+]', str_input)
            while re.search(r'- [\d+]', str_input) is not None:
                str_input_find = str(str_input_search.group(0))
                str_input_fixed = str(str_input_search.group(0)).replace(" ", "")
                str_input = re.sub(str_input_find, str_input_fixed, str_input)

                str_input_search = re.search(r'- [\d+]', str_input)

            # print(f"Post processing string: {str_input}")

            # Begin processing the rolls
            str_input_split = str_input.split(" ")
            int_roll_total = 0
            lst_current_die_rolls = []
            ls_all_die_rolls = []

            # Generate results for all rolls
            for i1, list_item in enumerate(str_input_split):
                if "d" in list_item:
                    if list_item.startswith("-"):
                        minus_if_negative = "-"
                        list_item = list_item[1:]
                    else:
                        minus_if_negative = ""

                    # Check if current item is a dice roll, and get those fuccbois
                    list_item = list_item.split("d")
                    if len(list_item) > 1:
                        i = 0
                        if list_item[0].isdigit() and list_item[1].isdigit():
                            # Eject the fuck out if the user input tries to kick our shit in
                            if int(list_item[0]) > 100000:
                                return "Please throw less dice."
                            elif int(list_item[1]) > 100000:
                                return "Please choose smaller dice."
                            else:
                                # All clear, go ahead and roll the dice
                                while i < int(list_item[0]):
                                    # Roll 1 die
                                    int_roll = random.randint(1, int(list_item[1]))

                                    # Assimilate that dank roll
                                    int_roll_total = int_roll_total + int_roll
                                    i += 1

                                    # Make a nice steamy log of rolls
                                    lst_current_die_rolls.append(str(int_roll))

                                # Make a nice steamy log out of nice steamy logs
                                ls_all_die_rolls.append(
                                    "(d" + str(list_item[1]) + ": " + ",".join(lst_current_die_rolls) + ")")
                                lst_current_die_rolls = []

                    str_input_split[i1] = minus_if_negative + str(int_roll_total)
            str_input = '+'.join(str_input_split).replace("+-", "-")
            # print("Stage 6: "+str_input)

            if len("".join(ls_all_die_rolls)) <= 100:
                # print(f"f {str_input}")
                str_output = f"Total: {Calc.evaluate(str_input)} {''.join(ls_all_die_rolls)}"
                return str_output
            else:
                str_output = f"Total: {Calc.evaluate(str_input)}"
                return str_output


def setup(bot):
    print("INFO: Loading [RollDice]... ", end="")
    bot.add_cog(RollDice(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [RollDice]")
