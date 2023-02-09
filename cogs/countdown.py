from discord.ext import commands
import discord
import importlib
import utils
from datetime import datetime, timedelta
import time
importlib.reload(utils)


class Countdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.defer(ephemeral=False)
    @commands.group()
    async def countdown(self, ctx):
        """Get a countdown for this server."""

    @commands.defer(ephemeral=False)
    @countdown.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def show(self, ctx, reminder_name: str, year: int = datetime.now().year, month: int = datetime.now().month, day: int = datetime.now().day, hour: int = 0, minute: int = 0):
        """Get a countdown for this server."""
        print(f"123")
        unix = await utils.sql(f'SELECT epoch, title FROM "database1".synthy.countdown WHERE guild_id = %s and title ilike %s;', (ctx.guild.id, reminder_name,))
        if unix:
            dt = timedelta(seconds=unix[0]['epoch'] - int(time.time()))
            # hours, remainder = divmod(dt.seconds, 3600)
            # minutes, seconds = divmod(remainder, 60)

            # f"Timer: {dt.days} days, {hours} hours, {minutes} minutes, {seconds} seconds."
            emb = await utils.embed(ctx, f"Countdown for {unix[0]['title']}",
                                    f"**Date:** <t:{unix[0]['epoch']}:F>\n"
                                    f"**Timer:** <t:{unix[0]['epoch']}:R>")

            await ctx.send(embed=emb)
        else:
            await ctx.send(content=f"Cannot find this countdown.")

    @commands.defer(ephemeral=False)
    @countdown.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def new(self, ctx, reminder_name: str, year=datetime.now().year, month: int = datetime.now().month, day: int = datetime.now().day, hour: int = 0, minute: int = 0):
        """Set a countdown for this server, all entries should be numeric."""
        slash_context = await self.bot.get_slash_context(ctx.interaction)
        year = int(slash_context.given_values['year']) if 'year' in slash_context.given_values.keys() else int(datetime.now().year)
        month = int(slash_context.given_values['month']) if 'month' in slash_context.given_values.keys() else int(month)
        day = int(slash_context.given_values['day']) if 'day' in slash_context.given_values.keys() else int(day)
        hour = int(slash_context.given_values['hour']) if 'hour' in slash_context.given_values.keys() else int(hour)
        minute = int(slash_context.given_values['minute']) if 'minute' in slash_context.given_values.keys() else int(minute)

        dt = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=0)
        unix_epoch = int(time.mktime(dt.timetuple()))
        await utils.sql('INSERT INTO "database1".synthy.countdown (guild_id, title, epoch) VALUES (%s, %s, %s);', (ctx.guild.id, reminder_name, unix_epoch,))
        await ctx.send(content="Done!")


def setup(bot):
    print("INFO: Loading [PFP]... ", end="")
    bot.add_cog(Countdown(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [PFP]")
