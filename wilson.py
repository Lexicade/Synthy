from discord.ext import commands
import discord
import logging
import MySQLdb
import configparser
logging.basicConfig(level=logging.INFO)


def get_pre(bot, message):
    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create database link
    db = MySQLdb.connect(host=config["mysqldb"]["host"],
                         user=config["mysqldb"]["user"],
                         passwd=config["mysqldb"]["passwd"],
                         db=config["mysqldb"]["db"])
    c = db.cursor()

    # Obtain prefix for guild
    c.execute("SELECT `prefix` FROM `settings` WHERE `guild_id` = %s" % message.channel.guild.id)
    guild_prefix = c.fetchone()

    # Ensure guild_prefix gets defined correctly
    if guild_prefix is None:
        guild_prefix = "!"
    else:
        guild_prefix = guild_prefix[0]

    return commands.when_mentioned_or(guild_prefix)(bot, message)


bot = commands.Bot(command_prefix=get_pre)
# bot.remove_command('help')
obj_invites = {}
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
extension_name = "[Module Manager] "
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    print(f"Discord.py version: {discord.__version__}")
    print("------")

    # Add 'playing' status
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Cyberpunk 2077"))

    # Load extensions
    bot.load_extension("cogs.8Ball")               # v1.0.0
    # bot.load_extension("cogs.ButtBot")           # v1.0.0
    # bot.load_extension("cogs.ColouredRoles")     # v1.0.0
    bot.load_extension("cogs.Define")              # v1.0.0
    bot.load_extension("cogs.ExtensionLoader")     # v1.0.0
    bot.load_extension("cogs.Flip")                # v1.0.0
    bot.load_extension("cogs.Help")
    # bot.load_extension("cogs.Image")             # v1.0.1
    bot.load_extension("cogs.Info")                #
    bot.load_extension("cogs.Levels")
    bot.load_extension("cogs.OutstandingNeighbor") #
    # bot.load_extension("cogs.IRC")               #
    bot.load_extension("cogs.Polls")               # v1.0.0
    # bot.load_extension("cogs.Remind")            #
    # bot.load_extension("cogs.RoleManager")       #
    bot.load_extension("cogs.RollDice")            # v1.0.0
    bot.load_extension("cogs.Screenshare")         # v1.0.0
    # bot.load_extension("cogs.StacheBot")         # v1.0.0
    bot.load_extension("cogs.Starboard")           #
    bot.load_extension("cogs.Steam")               # v1.0.1
    bot.load_extension("cogs.Todo")
    bot.load_extension("cogs.Wiki")                # v1.0.0
    # bot.load_extension("cogs.xkcd")              # v1.0.0


@bot.event
async def on_message(message):
    await bot.process_commands(message)


# @bot.command()
# async def help(ctx):
#     """Produces this help message."""
#     list_help = {}
#     name_length = 0
#     msg_help = ""
#
#     # Get command info and obtain max character spacing
#     for cmd in ctx.bot.commands:
#
#         # Omit commands that are marked as hidden
#         if not cmd.hidden:
#             list_help[cmd.name] = cmd.help
#             if name_length < len(cmd.name):
#                 name_length = len(cmd.name)
#
#     # Reorder list
#     list_help = dict(sorted(list_help.items(), key=lambda x: x[0].lower()))
#
#     # Add spacing to command name
#     for item in list_help:
#         iname = item
#         idesc = "" if list_help[item] is None else list_help[item]
#         while len(iname) < name_length:
#             iname = iname + " "
#         msg_help = msg_help + f"{iname} | {idesc}\n"
#     await ctx.send(content=f"```{msg_help}```")

bot.run("NDk3ODQ3NTQ1MDMzMzkyMTI4.DuuIaQ.4ijnRP0rrXI2AmkfKWj7oKMlcgQ")