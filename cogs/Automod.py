from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def automod(self, ctx, *arg):
        """Configure some server moderation for the server."""
        prefix = await utils.prefix(self.bot, ctx.message)
        emb = await utils.embed(ctx, f"Commands for `{prefix}automod`",
                                "Automod helps keep unwanted words out of the chat.")
        emb = await utils.field(emb, f"{prefix}automod add `[words / phrase]`",
                                f"Adds the given word or phrase to the word filter. These words will be deleted.")
        emb = await utils.field(emb, f"{prefix}automod list",
                                f"Shows the words Automod will remove from the chat.")
        emb = await utils.field(emb, f"{prefix}automod remove `[words / phrase]`",
                                f"Removes the given word or phrase from the filter.")
        await ctx.send(embed=emb)

    @automod.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def add(self, ctx, *, words):
        await utils.sql_set("INSERT INTO `automod_words` (guild_id, word) VALUES (%s, '%s')", (ctx.guild.id, words))
        await ctx.send(content=f"Added {words} into the word filter.")


    @automod.command()
    async def list(self, ctx):
        dict_words = await utils.sql_get("SELECT `word` from `automod_words` WHERE `guild_id` = %s", (ctx.guild.id))
        lst_words = [x['word'] for x in dict_words]

        emb = await utils.embed(ctx, "Blacklisted words:", "\n".join(lst_words))
        await ctx.send(embed=emb)

    @automod.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def remove(self, ctx, *, words):
        dict_words = await utils.sql_get("SELECT `word` from `automod_words` WHERE `guild_id` = %s", (ctx.guild.id))
        lst_words = [x['word'] for x in dict_words]

        for word in lst_words:
            if word == words:
                await utils.sql_set("DELETE FROM `automod_words` WHERE `guild_id`=%s AND `word`='%s'", (ctx.guild.id, words))
                emb = await utils.embed(ctx, "Automod - Remove complete:", f"Removed `{word}` from the filter.")
                await ctx.send(embed=emb)
                break

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        bl_words = await utils.sql_get("SELECT `word` FROM `automod_words` WHERE `guild_id` = %s", (message.guild.id,))

        lst_words = []
        for word in bl_words:
            lst_words.append(word["word"])
        lst_words = [x.lower() for x in lst_words]
        msg_words = [x.lower() for x in message.content.lower().split(' ')]
        matches = []
        for db_word in lst_words:
            if db_word.count(" ") == 0:
                for msg_word in msg_words:
                    if db_word.lower() == msg_word.lower():
                        if str(db_word).casefold() == str(msg_word).casefold():
                            print("single word match")
                            matches.append(db_word)

            elif db_word.count(" ") > 0:
                if db_word.lower() in message.content.lower():
                    print("phrase match")
                    matches.append(db_word)

        if not matches == []:   
            await message.delete()
            emb = await utils.embed(message, "Message Removed",
                                    f"[AUTOMOD] Removed a message from {message.author} as it contained a blacklisted word: `{', '.join(matches)}`",
                                    colour="orange")
            emb = await utils.footer(emb, f"{message.author.name}\n" +
                                     f"{message.content}",
                                     url=message.author.avatar_url)
            await utils.log(message.guild.id, self.bot, emb=emb)

        # result = set(lst_words).intersection(msg_words)
        #
        # #  await message.channel.send(content=result)
        # print(f"{len(result)}: {result}")
        # if len(result) > 0:
        #     await message.delete()
        #     emb = await utils.embed(message, "Message Removed", f"[AUTOMOD] Removed a message from {message.author} as it contained a blacklisted word: `{', '.join(result)}`")
        #     emb = await utils.footer(emb, f"{message.author.name}\n" +
        #                              f"{message.content}",
        #                              url=message.author.avatar_url)
        #     await utils.log(message, self.bot, emb=emb)


def setup(bot):
    print("INFO: Loading [Automod]... ", end="")
    bot.add_cog(Automod(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Automod]")
