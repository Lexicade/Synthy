from discord.ext import commands
import discord
import importlib
import utils
import git
import os
importlib.reload(utils)


class Git(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, hidden=True, invoke_without_command=True)
    async def git(self, ctx, *arg):
        """GIT"""
        # git.init(self.__path)
        # my_repo = git.Repo('git_synthy')
        # git.pull('-f', '-u', 'origin', 'master')
        #
        # git.clone(repo, 'ssh@github.com/blah/blah.git')
        #
        # git.commit('-m', message, '.gitmodules', self.ROLES) or git("commit", "-m", "Initial commit")
        #
        # git.push('origin', 'master')
        #
        # git.add(some_file, f=True)
        #
        # git('checkout', '-b', fix_branch)
        # git('checkout', 'production')

    @git.command()
    async def commit(self, ctx, *, arg):
        cogs = []
        git_rep = git.Repo('git_synthy')

        # Add Synthy script to rep
        git_rep.index.add("synthy.py")

        # Collect cogs
        for file in os.listdir("./cogs/"):
            if file.endswith(".py") and not file.startswith("__"):
                git_rep.index.add(f"./cogs/{file}")

        # Commit
        git_rep.index.commit(arg)
        # await ctx.send(content=arg)

def setup(bot):
    print("INFO: Loading [Git]... ", end="")
    bot.add_cog(Git(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Git]")
