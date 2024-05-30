from discord.ext import commands, tasks
from discord import app_commands
import datetime
import discord
import importlib
import utils
importlib.reload(utils)


class DiscordInfo(commands.GroupCog, name='info', description='Get information about users or the Discord server.'):
    def __init__(self, bot):
        self.bot = bot
        # https://discordpy.readthedocs.io/en/latest/ext/tasks/
        global cached_guild_invites
        cached_guild_invites = {}
        self.initial_setup.start()
        global extension_name

    @tasks.loop(count=1)
    async def initial_setup(self):
        global cached_guild_invites
        for guild in self.bot.guilds:
            try:
                if guild.me.guild_permissions.manage_guild:
                    cached_guild_invites[guild.id] = await self.bot.get_guild(guild.id).invites()

            except discord.Forbidden as e:
                print(f"[Info Forbidden Error] Guild: {guild.name} | ID: {guild.id} | {e}")

            except discord.HTTPException as e:
                print(f"HTTPException error during initial invite info: {e}")

    @app_commands.command(name='user', description='Get information about a user.')
    async def user(self, interaction: discord.Interaction, user: discord.Member):
        print(f"member")
        print(f"member: {user}")
        emb = await utils.embed(interaction, "", "", thumbnail=user.avatar.url)
        emb = await utils.author(emb, user.name)
        emb = await utils.field(emb, "Roles:", value=str(len(user.roles)-1))
        emb = await utils.field(emb, "Created At:", value=user.created_at.strftime("%d %B %Y - %H:%M:%S"))
        emb = await utils.field(emb, "Joined:", value=user.joined_at.strftime("%d %B %Y - %H:%M:%S"))
        emb = await utils.field(emb, "Top Role:", value=user.top_role)
        emb = await utils.field(emb, "Bot:", value=user.bot)
        # emb = await utils.thumb(emb, member.avatar_url)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='server', description='Get information about the Discord server.')
    async def server(self, interaction: discord.Interaction):

        emb = await utils.embed(interaction, "", "")
        emb = await utils.field(emb, "Owner:", interaction.guild.owner)
        emb = await utils.field(emb, "Created:", interaction.guild.created_at.strftime("%d %B %Y"))
        emb = await utils.field(emb, "Stats:", value=f"{len(interaction.guild.categories)} categories\n"
                                                     f"{len(interaction.guild.text_channels)} text channels\n"
                                                     f"{len(interaction.guild.voice_channels)} voice channels.\n"
                                                     f"{interaction.guild.member_count} members.\n"
                                                     f"{len(interaction.guild.roles)} roles.\n"
                                                     f"{len(interaction.guild.emojis)} emojis.\n")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='bot', description='Get information about the bot.')
    async def bot(self, interaction: discord.Interaction):
        emb = await utils.embed(interaction, "Synthy Info - bot", f"Currently serving {len(self.bot.guilds)} guilds.")
        await interaction.response.send_message(embed=emb)
        print(self.bot.guilds)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        global cached_guild_invites
        current_guild_invites = []

        print('Member Join Event Start')

        # Obtain the current invites
        try:
            if member.guild.me.guild_permissions.manage_guild:
                guild_invites = await self.bot.get_guild(member.guild.id).invites()
            else:
                return
        except discord.Forbidden as e:
            print(f"Failed to get initial invite info: {e}")
            return
        except discord.HTTPException as e:
            print(f"HTTPException error during initial invite info: {e}")
            return

        for invite in guild_invites:
            current_guild_invites.append(invite)

        # Determine the difference
        for cachedInvite, invite in [(cachedInvite, invite) for cachedInvite in cached_guild_invites[member.guild.id] for invite in current_guild_invites]:
            print(f"Comparing {invite.code}/{invite.uses} to {cachedInvite.code}/{cachedInvite.uses}")
            if invite.code == cachedInvite.code and invite.uses > cachedInvite.uses:
                str_invite_used = str(invite.code)
                str_invite_owner = str(invite.inviter.name)
                str_invite_uses = str(invite.uses)
                break

        channel_id = await utils.sql('SELECT channel_id FROM "database1".synthy.invitedetails WHERE guild_id = %s', (member.guild.id,))
        print(f"channel_id {channel_id}")
        if not channel_id:
            print(f"channel_id []")
            return
        else:
            print(f"channel_id B {channel_id}")
            obj_channel = self.bot.get_channel(channel_id[0]["channel_id"])

            user_joined = f"**User Joined:** {member.display_name} ({member.mention})"
            invite_used = f"**Invite Used:** {str_invite_used}"
            invite_owner = f"**Invite Owner:** {str_invite_owner}"
            invite_uses = f"**Total times used:** {str_invite_uses}"
            joined_details = f"\n{user_joined}\n{invite_used}\n{invite_owner}\n{invite_uses}"

            emb = await utils.notice("New User Joined!", joined_details)
            await obj_channel.send(embed=emb)

        cached_guild_invites[member.guild.id] = current_guild_invites

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = await utils.sql('SELECT channel_id FROM "database1".synthy.invitedetails WHERE guild_id = %s', (member.guild.id,))
        if channel_id == ():
            return

        obj_channel = self.bot.get_channel(channel_id[0]["channel_id"])

        # print(obj_channel)
        # print(member.display_name)

        if channel_id is not None:
            emb = await utils.notice("User has left!", f"The user {member.name} has left the server.")
            await obj_channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_join(self):
        global cached_guild_invites
        cached_guild_invites = {}
        for guild in self.bot.guilds:
            try:
                cached_guild_invites[guild.id] = await self.bot.get_guild(guild.id).invites()
            except Exception as e:
                print(f"[INFO]on_guild_join:{guild.id}: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self):
        global cached_guild_invites
        cached_guild_invites = {}
        for guild in self.bot.guilds:
            try:
                cached_guild_invites[guild.id] = await self.bot.get_guild(guild.id).invites()
            except Exception as e:
                print(f"[INFO]on_guild_remove:{guild.id}: {e}")

    @commands.group(invoke_without_command=True)
    async def details(self, interaction: discord.Interaction):
        """Configure join/quit notices."""
        # Get guilds prefix
        prefix = await self.bot.get_prefix(interaction.message)
        chan_id = await utils.sql('SELECT channel_id FROM "database1".synthy.invitedetails WHERE guild_id = %s;', (interaction.guild.id,))

        if chan_id:
            obj_channel = self.bot.get_channel(chan_id[0]["channel_id"])
            cur_channel = f"\nThe channel I am using is #{obj_channel.name}."
        else:
            cur_channel = ""

        # Create message
        emb = await utils.embed(interaction, f"Help for `{prefix[2]}details`",
                                     "The details feature allows me to post extra info when a user joins to a " +
                                     "channel, like who joined, what invite was used and who owns that invite.")
        emb = await utils.field(emb, f"{prefix[2]}details set",
                                     f"Use this command in the channel you want me to post in.{cur_channel}")
        emb = await utils.field(emb, f"{prefix[2]}details clear",
                                     "Use this command to stop me posting join and leave messages.")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='set', description='Set the channel for join/leave messages.')
    async def set(self, interaction: discord.Interaction):
        await utils.sql('INSERT INTO "database1".synthy.invitedetails (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = %s;', (interaction.guild.id, interaction.channel.id, interaction.channel.id,))
        await interaction.response.send_message(f"I will put extra details into #{interaction.channel.name}.")

    @app_commands.command(name='clear', description='Clear the channel for join/leave messages.')
    async def clear(self, interaction: discord.Interaction):
        await utils.sql('DELETE FROM "database1".synthy.invitedetails WHERE guild_id = %s;', (interaction.guild.id,))
        await interaction.response.send_message(f"Channel has been cleared.")


async def setup(bot):
    print("INFO: Loading [Info]... ", end="")
    await bot.add_cog(DiscordInfo(bot))
    print("Done!")


async def teardown():
    print("INFO: Unloading [Info]")
