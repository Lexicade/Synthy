from discord.ext import commands
import discord
import re
import importlib
import utils
importlib.reload(utils)


class Requests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dr(self, ctx, *args):
        """WIP."""

        request_data = {"dinosaurs": ["herrerasaurus", "austroraptor", "baryonyx", "albertosaurus", "acrocanthosaurus", "stegosaurus", "ankylosaurus", "therizinosaurus", "avaceratops", "velociraptor", "orodromeus", "psittacosaurus"],
                        "genders": ["m", "f"],
                        "safe_logged": ["y", "n"],
                        "steamid": ""}

        if len(args) != len(request_data):
            await ctx.send(content=f"args:{len(args)}, data:{len(request_data)}")
            return

        for i, field in enumerate(request_data):
            print(f"data:{field} field:{request_data[field]} type:{type(request_data[field])}")

            if not any(args[i].casefold() == cur_arg for cur_arg in request_data[field]):
                emb = await utils.embed(ctx, "Command failed", "Command should be structured as followed: `!dr [steamid] [dinosaur] [M/F] [Y/N]`")
                emb = await utils.field(emb, "Dinosaurs", ", ".join(request_data[field]))
                await ctx.send(content=f"Failed on {field}", embed=emb)
                return

        await ctx.send(content="Yes")

        # if len(args) == arg_count:
        #     dinosaur = args[1]
        #     gender = args[2]
        #     safe_logged = args[3]
        #     steamid = args[0]
        #
        #     dino_check = any(dinosaur.casefold() == dino for dino in lst_dino)
        #     print(f"Dino check: {dino_check}")


        # else:
        #     emb = await utils.embed(ctx, "Command failed", "Command should be structured as followed: `!dr [steamid] [dinosaur] [M/F] [Y/N]`")
        #     emb = await utils.field(emb, "Dinosaurs", ", ".join(lst_dino))
        #     await ctx.send()
        #     print("Improper args")

        # validate steamid

def setup(bot):
    print("INFO: Loading [Requests]... ", end="")
    bot.add_cog(Requests(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Requests]")
