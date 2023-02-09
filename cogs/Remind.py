from discord.ext import commands, tasks
import discord
import datetime
import dateutil.parser
import importlib
import utils
importlib.reload(utils)


class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Remind] "
        self.reminder_loop.start()

    @commands.group(invoke_without_command=True)
    async def remind(self, ctx, *args):
        """Set reminders for things through Discord."""

        if len(args) == 0:
            prefix = await self.bot.get_prefix(ctx.message)
            emb = await utils.embed(ctx, f"Commands for {prefix[2]}remind", "With remind you can set events at specific dates and times.\nDates are currently in a UK date format, along with UTC +0 times.",)
            emb = await utils.field(emb, f"✴{prefix[2]}remind setutc [number]", "✴️**Not fully added in.** Set the UTC timezone your server should follow. (0 by default)")
            emb = await utils.field(emb, f"{prefix[2]}remind list", "Get a list of your Discord servers reminders")
            emb = await utils.field(emb, f"{prefix[2]}remind [date - dd/mm/yyyy] [time - hh:mm] [your reminder]", "Add a new reminder at a specific date and time.")
            await ctx.send(embed=emb)
            # 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣
        elif len(args) >= 3:
            guild_utc = await utils.sql_get('SELECT utc_timezone FROM "database1".synthy.settings WHERE guild_id = %s', (ctx.guild.id,))

            args = list(args)
            arg_date = args.pop(0)
            arg_time = args.pop(0)
            arg_msg = " ".join(args)

            big_date_target = dateutil.parser.parse(arg_date + " " + arg_time, dayfirst=True)
            big_date_current = dateutil.parser.parse(str(datetime.datetime.now()))
            # print(f"big_date_target: {big_date_target}")
            # print(f"big_date_current: {big_date_current}")

            # Check date and time is valid
            if big_date_current >= big_date_target:
                await ctx.send(content="You cannot set a reminder in the past.")

            else:
                await utils.sql('INSERT INTO "database1".synthy.remind (message_id, member_id, channel_id, guild_id, datetime, reminder) VALUES (%s, %s, %s, %s, %s, %s)',
                    (ctx.message.id, ctx.author.id, ctx.channel.id, ctx.guild.id, big_date_target, arg_msg,))

                await ctx.send(content=f"Added a reminder on {big_date_target} for: {arg_msg}")

    @remind.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def setutc(self, ctx, arg):
        utc_tz = await utils.sql_get('SELECT utc_timezone FROM "database1".synthy.settings WHERE guild_id = %s', (ctx.guild.id,))

        if utc_tz is None:
            await utils.sql_set('INSERT INTO "database1".synthy.settings (guild_id, utc_timezone) VALUES (%s, %s)', (ctx.guild.id, arg,))

            cur_time = datetime.datetime.now()
            cur_time = cur_time + datetime.timedelta(hours=int(arg))
            cur_time = str(cur_time).split(".")[0]

            await ctx.send(
                content=f"Created UTC difference for {ctx.guild}. The time remind uses will be: {cur_time}")
        else:
            await utils.sql_set('UPDATE "database1".synthy.settings SET utc_timezone = %s WHERE guild_id = %s', (arg, ctx.guild.id,))
            # db.commit()

            cur_time = datetime.datetime.now()
            cur_time = cur_time + datetime.timedelta(hours=int(arg))
            cur_time = str(cur_time).split(".")[0]

            await ctx.send(content=f"Updated UTC for {ctx.guild}. The time remind uses will be: {cur_time}")

    @remind.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def list(self, ctx):
        reminders = await utils.sql('SELECT reminder, member_id, date, time FROM "database1".synthy.remind WHERE guild_id = %s', (ctx.guild.id,))

        if not reminders == ():
            desc = ""
            for item in reminders:
                item_date = datetime.datetime.strftime(item[2], "%d/%m/%Y")
                desc = desc + f"**Author:** <@{item[1]}> ({item_date} {item[3]})\n**Reminder:** {item[0]}\n\n"
            emb = await utils.embed(ctx, '', desc)
            await ctx.send(embed=emb)
        else:
            emb = await utils.embed(ctx, 'You have no reminders.', '')
            await ctx.send(embed=emb)

    @tasks.loop(seconds=10)
    async def reminder_loop(self):
        # try:
        # await utils.log(self.bot, "Remind", "[Remind] Starting reminder_loop")
        cur_datetime = dateutil.parser.parse(str(datetime.datetime.now()))
        # await utils.log(self.bot, "Remind", f"[Remind] Current time: {cur_datetime}")

        sql_return = await utils.sql('SELECT id, channel_id, reminder FROM "database1".synthy.remind WHERE %s >= datetime', (cur_datetime,))
        # await utils.log(self.bot, "Remind", f"[Remind] SQL Reminders: {sql_return}")

        for item in sql_return:
            rmdr_channel = self.bot.get_channel(int(item["channel_id"]))
            # await utils.log(self.bot.user.name, "Remind", f"[Remind] Channel to post in: {rmdr_channel.name}/{rmdr_channel.id}")
            await rmdr_channel.send(content=item["reminder"])
            # await utils.log(self.bot, "Remind", f'[Remind] Sent {item["reminder"]} to {rmdr_channel.name}')
            await utils.sql('DELETE FROM "database1".synthy.remind WHERE id = %s', (item["id"],))
            # await utils.log(self.bot, "Remind", f'[Remind] Deleted {item["id"]} from SQL/Remind')
        # print("2", end="\r")
        # await utils.log(self.bot.user.name, "Remind", "[Remind] End of loop.")

def setup(bot):
    print("INFO: Loading [Remind]... ", end="")
    bot.add_cog(Remind(bot))
    print("Done!")


def teardown(bot):
    bot.reminder_loop.cancel()
    print("INFO: Unloading [Remind]")