from discord.ext import commands
from discord import abc
import discord
import importlib
import re
import requests
import pandas as pd
import io
import json
import utils
importlib.reload(utils)


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[Role Manager] "

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.update_roles(payload.guild_id, payload.message_id, payload.channel_id, payload.user_id, payload.emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.update_roles(payload.guild_id, payload.message_id, payload.channel_id, payload.user_id, payload.emoji)

    async def update_roles(self, guild_id, message_id, channel_id: int, user_id, react_emoji: discord.PartialEmoji):
        if user_id == self.bot.user.id:
            return

        sql_msg_parent = await utils.sql('SELECT id FROM "database1".synthy.menu_parent WHERE guild_id = %s AND message_id = %s', (guild_id, message_id,))
        if sql_msg_parent:
            guild = self.bot.get_guild(guild_id)
            print(f"guild{guild}")
            member = guild.get_member(user_id)
            print(f"member{member}")
            member_self = guild.get_member(self.bot.user.id)
            print(f"member_self{member_self}")
            channel = self.bot.get_channel(channel_id)
            print(f"channel{channel}")

            if react_emoji.is_unicode_emoji():
                role_emoji = await self.translate_unicode_emoji(str(react_emoji), "emoji")
            else:
                role_emoji = f"<:{react_emoji.name}:{react_emoji.id}>"

            sql_msg_roles = await utils.sql('SELECT emoji_id, role_id FROM "database1".synthy.menu_child WHERE parent_id = %s AND emoji_id = %s', (sql_msg_parent[0]["id"], role_emoji,))
            sql_msg_roles = [item for item in sql_msg_roles]
            if not sql_msg_roles:

                # emb = await utils.notice("Auto-roles - Warning",
                #                          f"The role {role_emoji} does not have an associated role. ",
                #                          colour="orange")
                # await utils.log(guild_id, self.bot, emb=emb)
                return

            role = guild.get_role(sql_msg_roles[0]["role_id"])

            if member_self.top_role < role:
                message_embed = discord.Embed(title=f"Unable to add/remove {role} as it's ranked higher than mine. Move my role above {role} to fix this.", description="")
                await channel.send(embed=message_embed, delete_after=10.0)

            else:
                if str(sql_msg_roles[0]["role_id"]) in str(member.roles):
                    await member.remove_roles(role)
                    message_embed = discord.Embed(title=f"Removing {role} from {member.name}", description="")
                    await channel.send(embed=message_embed, delete_after=10.0)
                    emb = await utils.notice("Role Removed",
                                             f"[ROLES] Removed @{role} from {member.name}",
                                             colour="green")
                    await utils.log(guild_id, self.bot, emb=emb)
                else:
                    await member.add_roles(role)
                    message_embed = discord.Embed(title=f"Added {role} to {member.name}", description="")
                    await channel.send(embed=message_embed, delete_after=10.0)
                    emb = await utils.notice("Role Removed",
                                             f"[ROLES] Added @{role} to {member.name}",
                                             colour="green")
                    await utils.log(guild_id, self.bot, emb=emb)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def menu(self, ctx):
        """Customise roles to be given/removed on a reaction"""
        prefix = await self.bot.get_prefix(ctx.message)
        emb = await utils.embed(ctx, f"Commands for {prefix[2]}menu", "Manage menus to grant roles")
        emb = await utils.field(emb, f"{prefix[2]}menu new [menu name]", "Create a new roles menu for your server.")
        emb = await utils.field(emb, f"{prefix[2]}menu list", "List all currently used menus.")
        emb = await utils.field(emb, f"{prefix[2]}menu list [menu name]", "List all roles for the chosen menu.")
        emb = await utils.field(emb, f"{prefix[2]}menu addrole [menu name] [emoji] [role]", "Add a new option to an existing menu.")
        emb = await utils.field(emb, f"{prefix[2]}menu removerole [menu name] [role]", "Remove an option from an existing menu.")
        await ctx.send(embed=emb)

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def list(self, ctx, *menu):
        sql_return = await utils.sql('SELECT id, menu_name FROM "database1".synthy.menu_parent WHERE guild_id = %s', (ctx.guild.id,))
        sql_return = [item for item in sql_return]
        # print(sql_return)

        guild_menus = ""
        if not sql_return:
            guild_menus = "No menus have been created for this server."
        else:
            for iter in sql_return:
                guild_menus = f"{iter['menu_name']}\n{guild_menus}".strip()

        if len(menu) == 0:
            emb = await utils.embed(ctx, f"Menus for {ctx.guild.name}", guild_menus)
            await ctx.send(embed=emb)
        else:
            # Validate Menu Parent
            menu_name = menu_id = None
            for sql_menu in sql_return:
                # print(f"Checking {sql_menu['menu_name']} against {menu[0]}")
                if sql_menu["menu_name"] == menu[0]:
                    menu_name = sql_menu["menu_name"]
                    menu_id = sql_menu["id"]
                    break

            if menu_id:
                guild_menus = await utils.sql('SELECT role_id, emoji_id FROM "database1".synthy.menu_child WHERE parent_id = %s', (menu_id,))
                menu_items = [item for item in guild_menus]

                # all_items = ""
                role_list = []
                for item in menu_items:
                    role_list.append(f"{item['emoji_id']} <@&{item['role_id']}>")
                    # all_items = f"<@&{item['role_id']}>\n{all_items}"

                emb = await utils.embed(ctx, "", " \n".join(role_list))
                await ctx.send(embed=emb)

            else:
                await ctx.send("failed")

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def new(self, ctx, menu_name):
        await utils.sql('INSERT INTO "database1".synthy.menu_parent (guild_id, menu_name) VALUES (%s, %s)', (ctx.guild.id, menu_name,))

        emb = await utils.embed(ctx, f"Created the {menu_name} menu.", "")
        await ctx.send(embed=emb)

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def addrole(self, ctx, menu_name, emoji, role):
        # Validate Menu Parent
        guild_menus = await utils.sql('SELECT id FROM "database1".synthy.menu_parent WHERE guild_id = %s and menu_name = %s', (ctx.guild.id, menu_name,))
        menu_id = [item['id'] for item in guild_menus][0]

        if menu_id is None:
            emb = await utils.embed(ctx, f"Menu does not exist.", "")
            await ctx.send(embed=emb)
            return

        print()

        # Validate Emoji
        # Check if custom animated
        if re.search(r"<a:", emoji):
            emb = await utils.embed(ctx, f"Animated emojis currently not supported.", "")
            await ctx.send(embed=emb)
            return

        # Check if custom static
        elif re.search(r"<:\D+:\d+>", emoji):
            emoji_custom = emoji.replace("<:", "").replace(">", "").split(":")[1]
            emoji_custom = self.bot.get_emoji(int(emoji_custom))

            # emoji.guild.id is not ctx.guild.id
            if emoji_custom is None:
                # Try to find standard emoji
                emb = await utils.embed(ctx, f"You must use an emoji from this Discord server", "")
                await ctx.send(embed=emb)

            else:
                emoji_id = emoji_custom

        # Check if default static
        elif await self.translate_unicode_emoji(emoji, "emoji"):
            # emoji_id = emoji.encode("raw_unicode_escape")
            emoji_id = await self.translate_unicode_emoji(emoji, "emoji")
            if not emoji_id:
                return
                # emoji_id = emoji

        # Fail
        else:
            await ctx.send("fail")
            return

        # Validate Role
        role = ctx.guild.get_role(int(role.replace("<@&", "").replace(">", "")))
        if role is None or role == "":
            emb = await utils.embed(ctx, f"Role is invalid.", "")
            await ctx.send(embed=emb)
            return

        await utils.sql('INSERT INTO "database1".synthy.menu_child (emoji_id, role_id, parent_id) VALUES (%s, %s, %s)', (emoji_id, role.id, menu_id,))

        emb = await utils.embed(ctx, f"Added {role} to {menu_name}.", "")
        await ctx.send(embed=emb)

    @commands.command(pass_context=True)
    async def tt(self, ctx, emoji):

        emoji = await self.translate_unicode_emoji(emoji, "emoji")
        if emoji:
            await ctx.send(f"Name: \\{emoji} {emoji}")
            # print(f"is_unicode_emoji: {emoji.is_unicode_emoji}")
            # print(f"id: {emoji.id}")

        else:
            print("Failed")

    @staticmethod
    async def translate_unicode_emoji(emoji, field):
        return_data = requests.get("https://raw.githubusercontent.com/rainyear/emoji-query/master/emoji.map.json")
        # JSON fields: emoji(:emoji:), description:long unicode desc), unicode(Unicode char/str), tags(ignore)

        if return_data.status_code == 200:
            data = json.loads(return_data.content.decode())
            output = None

            for i, json_emoji in enumerate(data["names"]):
                if emoji == json_emoji["unicode"]:
                    output = json_emoji[field]
                    break
                elif emoji == json_emoji["emoji"]:
                    output = json_emoji[field]
                    break

            # print(emoji, field, output)
            return output

        else:
            return "Cannot verify emoji. Please try again later."

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def removerole(self, ctx, menu_name, role):
        # Validate Menu Parent
        guild_menus = await utils.sql('SELECT id FROM "database1".synthy.menu_parent WHERE guild_id = %s and menu_name = %s', (ctx.guild.id, menu_name,))
        menu_id = [item['id'] for item in guild_menus][0]

        # Validate Role
        role = ctx.guild.get_role(int(role.replace("<@&", "").replace(">", "")))
        if role is None or role == "":
            emb = await utils.embed(ctx, f"Role is invalid.", "")
            await ctx.send(embed=emb)
            return

        await utils.sql('DELETE FROM "database1".synthy.menu_child WHERE parent_id=%s and role_id=%s', (menu_id, role.id,))

        emb = await utils.embed(ctx, "", f"Removed {role.id} from {menu_name}.")
        await ctx.send(embed=emb)

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def channel(self, ctx, menu_name, channel_id):
        menu_message = await utils.sql('SELECT message_id, id FROM "database1".synthy.menu_parent WHERE guild_id = %s AND menu_name = %s', (ctx.guild.id, menu_name,))
        if not menu_message:
            emb = await utils.embed(ctx, f"Menu does not exist.", "")
            await ctx.send(embed=emb)
            return

        # Validate the channel ID
        channel_id = channel_id.replace("<#", "").replace(">", "")
        channel_object = self.bot.get_channel(int(channel_id))
        if channel_object is None:
            emb = await utils.embed(ctx, f"Channel cannot be found", "")
            await ctx.send(embed=emb)
            return
        await utils.sql('UPDATE "database1".synthy.menu_parent SET channel_id = %s WHERE guild_id = %s AND menu_name = %s', (channel_object.id, ctx.guild.id, menu_name,))

        # Send return message
        emb = await utils.embed(ctx, f"Channel has been set to #{channel_object.name}.", "")
        await ctx.send(embed=emb)

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def send(self, ctx, menu_name):
        # Get Channel
        menu_message = await utils.sql('SELECT id, channel_id FROM "database1".synthy.menu_parent WHERE guild_id = %s AND menu_name = %s', (ctx.guild.id, menu_name,))
        channel_object = self.bot.get_channel(int(menu_message[0]["channel_id"]))

        # Create the Menu
        if channel_object.permissions_for(ctx.guild.me).embed_links:
            emb = await utils.embed(ctx, f"Role Menu", "")
            message_sent = await channel_object.send(embed=emb)
            await utils.sql('UPDATE "database1".synthy.menu_parent SET message_id = %s WHERE guild_id = %s AND menu_name = %s', (message_sent.id, ctx.guild.id, menu_name,))
        else:
            await ctx.send("I can't post to this channel. I need embedded links.")

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def update(self, ctx, menu_name):
        # Get Channel
        menu_data = await utils.sql('SELECT id, message_id, channel_id FROM "database1".synthy.menu_parent WHERE guild_id = %s AND menu_name = %s', (ctx.guild.id, menu_name,))
        menu_id = menu_data[0]['id']
        menu_message = menu_data[0]['message_id']
        menu_channel = menu_data[0]['channel_id']

        # Apply Emojis to the new menu
        menu_emojis = await utils.sql('SELECT emoji_name, emoji_id FROM "database1".synthy.menu_child WHERE parent_id = %s', (menu_id,))
        # print(menu_emojis)

        if not menu_message:
            emb = await utils.embed(ctx, 'This menu has no items.', "")
            await ctx.send(embed=emb)
            return

        for item in menu_emojis:
            set_channel = self.bot.get_channel(int(menu_channel))
            set_message = await set_channel.fetch_message(int(menu_message))

            # print(f"item['emoji_id'][{item['emoji_id']}]")
            if str(item['emoji_id']).startswith(":"):
                emoji_unicode = await self.translate_unicode_emoji(item['emoji_id'], "unicode")
                # print(f"emoji_unicode[{emoji_unicode}]")
                await set_message.add_reaction(emoji_unicode)

            else:
                await set_message.add_reaction(item['emoji_id'])

    @menu.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    async def body(self, ctx, menu_name, *, body):
        # Get Channel
        menu_data = await utils.sql('SELECT message_id, channel_id FROM "database1".synthy.menu_parent WHERE guild_id = %s AND menu_name = %s', (ctx.guild.id, menu_name,))
        obj_channel = self.bot.get_channel(menu_data[0]['channel_id'])
        obj_message = await obj_channel.fetch_message(menu_data[0]['message_id'])

        await obj_message.edit(content=body)


def setup(bot):
    print("INFO: Loading [RoleManager]... ", end="")
    bot.add_cog(RoleManager(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [RoleManager]")


# INSERT INTO menu_parent(guild_id, menu_name)
#     SELECT 415594259232849920, 'roles2'
#         FROM dual
#         WHERE NOT EXISTS (SELECT * FROM menu_parent
#                              WHERE guild_id = 415594259232849920
#                                AND menu_name = 'roles2')
