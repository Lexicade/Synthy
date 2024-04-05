from discord.ext import commands
from discord.app_commands import tree
from discord import app_commands
import discord
import importlib
import utils

importlib.reload(utils)


class Voice(commands.GroupCog, name="voice", description="Allow Synthy to create/delete channels as needed to keep things tidy"):
    def __init__(self, bot):
        self.bot = bot
    # voice_commands = app_commands.Group(name='voice', description='Allow Synthy to create/delete channels as needed to keep things tidy')

    # @commands.group()
    # async def voice(self, ctx, *arg):
    #     """Allow Synthy to create/delete channels as needed to keep things tidy"""

    @commands.has_permissions(administrator=True)
    @app_commands.command(name='setup', description='Create the initial voice channel')
    async def setup(self, interaction: discord.Interaction):
        """Create the initial voice channel"""
        channel: discord.VoiceChannel = await interaction.guild.create_voice_channel(name="VC Foyer")
        await utils.sql('INSERT INTO "database1".synthy.voice (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = %s;', (interaction.guild.id, channel.id, channel.id,))
        await interaction.response.send_message(content=f"I have created {channel.mention} for you.", ephemeral=True)

    @app_commands.command(name='name', description='Name a voice channel')
    async def name(self, interaction: discord.Interaction, name: str):
        if not interaction.user.voice:
            emb = await utils.embed(interaction, f"Voice", "You're not connected to a voice channel")
            await interaction.response.send_message(embed=emb)
            return

        elif not str(interaction.user.voice.channel.name).startswith("🔊"):
            emb = await utils.embed(interaction, f"Voice", "The voice channel you're in isn't one I should touch.")
            await interaction.response.send_message(embed=emb)
            return

        try:
            await interaction.user.voice.channel.edit(name=f"🔊 {name}")
            emb = await utils.embed(interaction, f"Voice", f"The name of your voice channel is now is now 🔊 {name}.")
        except discord.Forbidden as e:
            emb = await utils.embed(interaction, f"Voice", "I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            emb = await utils.embed(interaction, f"Voice", "I wasn't able to edit that channel, try this again. If you keep seeing this please let my [code slave](https://discord.gg/bDAa7cu) know.")
        except discord.InvalidData as e:
            emb = await utils.embed(interaction, f"Voice", "What you entered wasn't able to be used for this setting.")
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name='limit')
    async def limit(self, ctx, user_count: int):
        if not ctx.author.voice:
            emb = await utils.embed(ctx, f"Voice", "You're not connected to a voice channel")
            await ctx.send(embed=emb)
            return

        elif not str(ctx.author.voice.channel.name).startswith("🔊"):
            emb = await utils.embed(ctx, f"Voice", "The voice channel you're in isn't one I should touch.")
            await ctx.send(embed=emb)
            return

        try:
            arg = int(user_count)
            if arg < 0 or arg > 99:
                raise ValueError
            await ctx.author.voice.channel.edit(user_limit=arg)
            emb = await utils.embed(ctx, f"Voice", f"The maximum users for {ctx.author.voice.channel.name} is now {arg}.")
        except ValueError as e:
            emb = await utils.embed(ctx, f"Voice", "I can only work with 0 to 99 for this command.")
        except discord.Forbidden as e:
            emb = await utils.embed(ctx, f"Voice", "I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            emb = await utils.embed(ctx, f"Voice", "I wasn't able to edit that channel, try this again. If you keep seeing this please let my [code slave](https://discord.gg/bDAa7cu) know.")
        except discord.InvalidData as e:
            emb = await utils.embed(ctx, f"Voice", "What you entered wasn't able to be used for this setting.")
        await ctx.send(embed=emb)

    @commands.Cog.listener()
    @commands.has_permissions(manage_channels=True)
    async def on_voice_state_update(self, member: discord.Member, before, after):
        # Ahh! Shit I'm not ready!
        if not self.bot.is_ready():
            return

        # Figure out if I should care about this event
        if before.channel == after.channel:
            return

        # Figure out if this guy will cause a scene in the club
        if after.channel is not None and after.channel.name.lower() == "vc foyer":
            # Let the guy in, but make sure he ain't got a gun
            if member.display_name.capitalize().endswith("s"):
                user_name = f"{member.display_name.capitalize()}'"
            else:
                user_name = f"{member.display_name.capitalize()}'s"

            chnl = await after.channel.clone(name=f"🔊 {user_name} Chat")
            await member.edit(voice_channel=chnl)

        # Check is the club is empty.
        elif before.channel is not None and "🔊" in before.channel.name:
            # Last One Out, Get the Lights. #FinishTheFight
            if len(before.channel.members) == 0:
                await before.channel.delete()


async def setup(bot):
    print("INFO: Loading [Voice]... ", end="")
    await bot.add_cog(Voice(bot))
    print("Done!")


async def teardown(bot):
    print("INFO: Unloading [Voice]")
