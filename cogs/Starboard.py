import re

from discord.ext import commands
import discord
import importlib
import utils
importlib.reload(utils)
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


class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user:
            return

        if payload.emoji.name == "⭐":
            sql_star = await utils.sql('SELECT min_stars, sb_channel FROM starboard WHERE guild_id = %s', (payload.guild_id,))
            if sql_star is None:
                return

            obj_channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
            obj_message: discord.Message = await obj_channel.fetch_message(payload.message_id)
            obj_chnl_sb = self.bot.get_channel(int(sql_star[0]['sb_channel']))

            for reaction in obj_message.reactions:
                if reaction.emoji == "⭐" and reaction.count >= int(sql_star[0]['min_stars']):

                    # Check if message exists in Starboard
                    async for sb_msg in obj_chnl_sb.history(limit=100, before=None, after=None):
                        for embed in sb_msg.embeds:
                            if embed.description == discord.embeds.EmptyEmbed:
                                continue

                            matches = re.findall(r'[[A-Za-z]+!]\(https?://[\w./]+\)', embed.description)
                            for match in matches:
                                match_message_id = match.rsplit("/", 1)[1].replace(")", "")

                                if str(match_message_id) == str(payload.message_id):
                                    return

                    # Create the embed
                    url = f"https://discordapp.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}"

                    msg = f"**Quoted from: {obj_channel.mention}**\n\n" \
                          f"**{obj_message.author.mention} wrote:**\n" \
                          f"{obj_message.content}\n" \
                          f"[Jump to message!]({url})"

                    if obj_message.reference:
                        msg_reply: discord.Message = await obj_channel.fetch_message(obj_message.reference.message_id)
                        msg = msg + f"\n\n**Replied to {msg_reply.author.mention}**\n" \
                                    f"{msg_reply.content}\n" \
                                    f"[Jump to reply!]({obj_message.reference.jump_url})"

                    sb_emb = discord.Embed(description=msg, color=colours["gold"])
                    sb_emb.set_author(name=obj_message.author.display_name, icon_url=obj_message.author.display_avatar)

                    # Get attachment and add as embed image
                    if len(obj_message.attachments) > 0:
                        im = obj_message.attachments[0]
                        sb_emb.set_image(url=im.url)

                    # Paste to channel
                    await obj_chnl_sb.send(embed=sb_emb)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user:
            return

        if payload.emoji.name == "⭐":
            sql_star = await utils.sql('SELECT min_stars, sb_channel FROM starboard WHERE guild_id = %s', (payload.guild_id,))

            obj_channel = self.bot.get_channel(payload.channel_id)
            obj_message = await obj_channel.fetch_message(payload.message_id)
            obj_chnl_sb = self.bot.get_channel(int(sql_star[0]['sb_channel']))

            async for sb_msg in obj_chnl_sb.history(limit=100, before=None, after=None):
                for i in sb_msg.embeds:
                    if str(i.footer.text) == str(payload.message_id):

                        # If message has star reactions:
                        if "'⭐'" in str(obj_message.reactions):
                            for reaction in obj_message.reactions:
                                if reaction.emoji == "⭐" and reaction.count < int(sql_star[0]['min_stars']):
                                    await sb_msg.delete()

    @commands.group(
        invoke_without_command=True,
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="channel",
                    description="Set the Staboard channel",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="stars",
                    description="Set the minimum stars to post to the Starboard channel",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                ),
            ]
        )
    )
    async def starboard(self, ctx):
        """Let your community star it's best comments."""

    @commands.defer(ephemeral=True)
    @starboard.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx):
        await utils.sql('INSERT INTO starboard (guild_id, sb_channel) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET sb_channel = %s', (ctx.guild.id, ctx.channel.id, ctx.channel.id,))
        await ctx.send(f"The Starboard channel has been set to #{ctx.channel.mention}.")

    @commands.defer(ephemeral=True)
    @starboard.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="stars",
                    description="Set the minimum stars to post to the Starboard channel",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                )
            ],
        )
    )
    @commands.has_permissions(administrator=True)
    async def stars(self, ctx, stars: int):
        try:
            arg_int = int(stars)

        except Exception as e:
            await ctx.send(f"Please provide a valid number.")
            print(f"Starboard - stars - Error: {e}")
            return

        if arg_int <= 0:
            await ctx.send(f"The minimum stars must be at least 1`.")
            return

        await utils.sql('INSERT INTO starboard (guild_id, min_stars) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET min_stars = %s', (ctx.guild.id, arg_int, arg_int,))
        await ctx.send(f"The minimum stars required has been set to {arg_int}.")


def setup(bot):
    print("INFO: Loading [Starboard]... ", end="")
    bot.add_cog(Starboard(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Starboard]")
