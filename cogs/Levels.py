from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """No Description."""
        if message.author.bot:
            return

        msg_xp = int((len(message.content)-10)/2)+8 if len(message.content) > 15 else 10
        msg_xp = 30 if msg_xp > 30 else msg_xp
        user_level = await utils.sql_get("SELECT `xp` FROM `levels` WHERE `user_id`=%s AND `guild_id`=%s;",
                                         (message.author.id, message.guild.id,))

        await utils.sql_proc("add_xp", (message.author.id, message.guild.id, msg_xp, ), True)

        # print(user_level[0])
        c_xp = int(user_level[0]["xp"])

        curr_level = 25 * c_xp * (1 + c_xp)
        new_level = 25 * c_xp+msg_xp * (1 + c_xp+msg_xp)

        # print(f"old:{curr_level} new:{new_level}")

    @commands.bot_has_permissions(embed_links=True)
    @commands.group(invoke_without_command=True)
    async def rank(self, ctx):
        """✓Check your rank in the server"""
        ranks = await utils.sql_proc("levels_ranks", (ctx.guild.id,), False)

        for rank in ranks:
            if rank["user_id"] == ctx.author.id:
                str_details = f"**Rank**: {int(rank['rank'])}/{len(ranks)} ({ctx.guild.member_count})\n" + \
                              f"**Messages**: {rank['messages']}\n" + \
                              f"**XP:** {rank['xp']}\n" + \
                              f"**Level:** {int(rank['level'])}\n"
                emb = await utils.embed(ctx, ctx.author.name, str_details)

                await ctx.send(embed=emb)
                break

    @commands.bot_has_permissions(embed_links=True)
    @commands.group(invoke_without_command=True)
    async def leaderboard(self, ctx):
        """✓Check the top 10 ranks in the server"""
        str_details = ""
        ranks = await utils.sql_proc("levels_ranks", (ctx.guild.id,), False)
        members = ctx.guild.members

        # Obtain the top 10 members
        for rank in ranks:
            for tmp_member in members:
                if rank['user_id'] == tmp_member.id:
                    member = tmp_member
                    break

            str_details = str_details + f"{int(rank['rank'])}: {member.name} - {rank['xp']}\n"

            if int(rank['rank']) == 10:
                break

        emb = await utils.embed(ctx, "", str_details)
        await ctx.send(embed=emb)


def setup(bot):
    print("INFO: Loading [Levels]... ", end="")
    bot.add_cog(Levels(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Levels]")
