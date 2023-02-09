from discord.ext import commands
import importlib
import utils
importlib.reload(utils)


class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def todo(self, ctx):
        """Add todos and reminders to a personal list"""

    @commands.defer(ephemeral=True)
    @todo.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def list(self, ctx):
        dict_todo = await utils.sql('SELECT id, description FROM "database1".synthy.todo WHERE member_id = %s;', (ctx.author.id,))

        str_todo = ""
        for item in dict_todo:
            str_todo = f"{str_todo}\n{item['id']}) {item['description'].strip()}"

        emb = await utils.embed(ctx, f"Todo list for {ctx.author}:", str_todo)
        await ctx.send(embed=emb)

    @todo.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def add(self, ctx, todo_item):
        await utils.sql('INSERT INTO "database1".synthy.todo (description, member_id) VALUES (%s, %s);', (todo_item, ctx.author.id,))
        emb = await utils.embed(ctx, f"Tasks", f"Added `{todo_item.replace('`', '')}` to your list.")
        await ctx.send(embed=emb)

    @commands.defer(ephemeral=True)
    @todo.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def remove(self, ctx, task_id):
        prefix = await self.bot.get_prefix(ctx.message)

        dict_todo = await utils.sql('SELECT id, description FROM "database1".synthy.todo WHERE member_id = %s and id = %s;', (ctx.author.id, task_id,))
        if dict_todo:
            await utils.sql('DELETE FROM "database1".synthy.todo WHERE id = %s AND member_id = %s', (task_id, ctx.author.id))
            emb = await utils.embed(ctx, f"Tasks", f"Removed {dict_todo[0]['id']} from your list.", footer=f"For help on how to use this command, use {prefix[2]}todo help")
        else:
            emb = await utils.embed(ctx, f"Tasks", f"I wasn't able to find that task.", footer=f"For help on how to use this command, use {prefix[2]}todo help")

        await ctx.send(embed=emb)

    @todo.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def help(self, ctx):
        prefix = await self.bot.get_prefix(ctx.message)

        emb = await utils.embed(ctx, f"Commands for `{prefix[2]}todo`", f"`{prefix[2]}todo` helps keep track of tasks.", footer=f"For help on how to use this command, use {prefix[2]}todo help")
        emb = await utils.field(emb, f"{prefix[2]}todo add [task description]", "Add a new task to your list.")
        emb = await utils.field(emb, f"{prefix[2]}todo remove [ID]", "Removes a task from your list.")
        await ctx.send(embed=emb)


def setup(bot):
    print("INFO: Loading [Todo]... ", end="")
    bot.add_cog(Todo(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Todo]")
