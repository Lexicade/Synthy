from discord.ext import commands
import discord
import aiojobs
import socket
import asyncio
import threading


class IRCBridge(commands.Cog, threading.Thread):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        extension_name = "[IRC Bridge] "
        threading.Thread.__init__(self)

    async def irc_run(self, ctx, con, sch_irc):
        data = con.recv(2048).decode('UTF-8')
        con.send(bytes("JOIN #discord\n", "UTF-8"))
        if data.startswith("PING :"):
            con.send(bytes('PONG %s\r\n' % data[6:], 'UTF-8'))

        print("cycle", data)
        await sch_irc.spawn(irc_run(ctx, con, sch_irc))
        await asyncio.sleep(0.1)

    @commands.command()
    async def irc(self, ctx):
        con = socket.socket()
        con.connect(("irc.blatech.net", 6667))
        con.send(bytes(f"USER discord1 discord2 discord3 'Hello!'\n", "UTF-8"))
        con.send(bytes('NICK %s\r\n' % "discord", 'UTF-8'))
        con.send(bytes('PASS %s\r\n' % "ircdiscord", 'UTF-8'))
        con.send(bytes('MSG NickServ IDENTIFY discordirc\r\n', 'UTF-8'))

        data = con.recv(2048).decode('UTF-8')
        if data.startswith("PING :"):
            con.send(bytes('PONG %s\r\n' % data[6:], 'UTF-8'))

        while 1:
            data = con.recv(2048).decode('UTF-8')
            con.send(bytes("JOIN #discord\n", "UTF-8"))
            if data.startswith("PING :"):
                con.send(bytes('PONG %s\r\n' % data[6:], 'UTF-8'))

            print("cycle", data)
            # await sch_irc.spawn(irc_run(ctx, con, sch_irc))
            await asyncio.sleep(0.1)



        # sch_irc = await aiojobs.create_scheduler()
        # await sch_irc.spawn(irc_run(self, ctx, con, sch_irc))


def setup(bot):
    bot.add_cog(IRCBridge(bot))




























from discord.ext import commands
import discord
import aiojobs
import socket
import asyncio
import threading
import _thread
import re
import json
import itertools
import requests
import discord
from discord import Webhook, RequestsWebhookAdapter
from datetime import datetime


class IRCClient:
    def __init__(self, chan_pairs, config, discord_client):
        self.connected = False
        self.chan_pairs = chan_pairs
        self.config = config
        self.discord_client = discord_client

    def irc_connect(self, server, port, nickname):
        print("Connecting to {}:{}".format(server, port))

        ircsocket = socket.socket()

        ircsocket.connect((server, port))
        ircsocket.send(f"NICK {nickname}\r\n".encode())
        ircsocket.send(f"USER {nickname} * * {nickname}\r\n".encode())

        self.connected = True
        print("Connected.")
        self.send_to_webhook("[IRC Bridge]", "Connected!")

        return ircsocket, server, nickname

    def join_channels(self):
        for channel in [pair[0] for pair in self.chan_pairs]:
            print(f"Joining {channel}")
            self.ircsocket.send(f"JOIN {channel}\r\n".encode())
        return

    def msg_process(self, rawmsg):  # figure out what we want to do with our irc message
        prefix, command, args, msg = self.split_msg(rawmsg)

        # msg format is "nick PRIVMSG #channel :message"
        if command in ["376", "422"]:
            print("END OF MOTD")
            self.join_channels()

        elif command == "PING":
            self.ircsocket.send("PONG {}\r\n".format(msg).encode())

        elif command == "PRIVMSG":
            author = prefix.split("!")[0]

            # send message to run comm coroutine
            for pair in self.chan_pairs:
                if args[0] == pair[0]:
                    if msg.startswith("=status") and len(msg.split()) > 1:
                        name = msg.split(" ", 1)[1].lower()
                        status_msg = ""
                        for member in self.discord_client.get_channel(pair[1]).guild.members:
                            if member.name.lower() == name or (member.nick and member.nick.lower() == name):
                                status_msg += f"{ember.name} is currently {member.status}"

                        self.send_message(args[0], status_msg)
                        continue

                    clean_msg = msg
                    # clean_msg = uniformatter.ircToDiscord(msg, pair[1], self.discord_client)
                    print(rawmsg)
                    action_regex = re.match(r"\u0001ACTION (.+)\u0001", clean_msg)  # format /me
                    # if action_regex:
                    #     formatted_msg = "**\* {}** {}".format(author, action_regex.group(1))
                    # else:
                    #     formatted_msg = "**<{}>** {}".format(author, clean_msg)

                    discord_channel = self.discord_client.get_channel(pair[1])
                    # Create webhook
                    self.send_to_webhook(author, clean_msg)

        else:
            print(f"[IRC] {rawmsg}")

        return

    def split_msg(self, rawmsg):  # interpret irc message
        msgpre, sep, msg = rawmsg.partition(" :")

        if not sep:  # if sep is empty
            msg = None

        msgpre_list = msgpre.split()

        if msgpre_list[0].startswith(":"):
            prefix = msgpre_list.pop(0).lstrip(":")
        else:
            prefix = None

        command = msgpre_list.pop(0)

        args = msgpre_list

        return prefix, command, args, msg

    def irc_run(self):  # start main irc loop
        if not self.connected:
            self.s, self.server, self.nick = self.irc_connect(**self.config)

        line_buffer = ""

        while True:
            responce = self.ircsocket.recv(2048)

            line_buffer += responce.decode()
            lines = line_buffer.split("\n")

            line_buffer = lines.pop()

            for line in lines:
                line = line.rstrip()

                if line:
                    self.msg_process(line)
                else:
                    pass

    def send_to_webhook(self, author, msg):
        webhook = Webhook.partial(676940734112333847,
                                  "7TxjLhpmmGWKhTAvfBctiBcdO-T5INVkrweK39B74vH9VHvxhHy3eG_qBh368q4E4v6Z",
                                  adapter=RequestsWebhookAdapter())
        webhook.send(content=msg,
                     wait=False,
                     username=author,
                     avatar_url=None,
                     tts=False,
                     file=None,
                     files=None,
                     embed=None,
                     embeds=None)
        webhook = None

        # profile image: f"https://eu.ui-avatars.com/api/name={author}?length=1?&background=0088ff&color=FFF"

    def send_message(self, channel, msg):  # send irc message
        try:
            self.ircsocket.send("PRIVMSG {channel} :{msg}\r\n".encode())

        except BrokenPipeError as e:
            _thread.interrupt_main()
        # exit("Error in message size too large. Exiting...")
        return


class uniformatter:
    def discordToIrc(msg):
        def replaceFormatting(form, replacement, string):
            start_form = re.escape(form)
            end_form = re.escape(form[::-1])  # reverse it

            pattern = r"{}((?:(?!{}).)*?){}".format(start_form, start_form, end_form)
            str_split = re.split(pattern, string)

            if len(str_split) == 1:  # no formatting required
                return str_split[0]

            new_str = ""
            for idx, part in enumerate(str_split):
                if idx % 2 == 1:
                    if re.search(r"https?:\/\/[^ \n]*$", new_str):  # make sure this formatting is not part of a url
                        new_str += "{}{}{}".format(form, part, form[::-1])
                    else:
                        new_str += "{}{}\x0F".format(replacement, part)
                else:
                    new_str += part

            return new_str

        def createHaste(code):
            response = requests.post("https://hastebin.com/documents", data=code)
            key = response.json()["key"]
            url = "https://hastebin.com/" + key
            return url

        formatting_table = [  # comment lines of this table to disable certain types of formatting relay
            ("***__", "\x02\x1D\x1F"),  # ***__UNDERLINE BOLD ITALICS__***
            ("__***", "\x02\x1D\x1F"),  # __***UNDERLINE BOLD ITALICS***__
            ("**__", "\x02\x1F"),  # **__UNDERLINE BOLD__**
            ("__**", "\x02\x1F"),  # __**UNDERLINE BOLD**__
            ("*__", "\x1D\x1F"),  # *__UNDERLINE ITALICS__*
            ("__*", "\x1D\x1F"),  # __*UNDERLINE ITALICS*__
            ("***", "\x02\x1D"),  # ***BOLD ITALICS***
            ("**_", "\x02\x1D"),  # **_BOLD ITALICS_**
            ("_**", "\x02\x1D"),  # _**BOLD ITALICS**_
            ("__", "\x1F"),  # __UNDERLINE__
            ("**", "\x02"),  # **BOLD**
            ("*", "\x1D"),  # *ITALICS*
            ("_", "\x1D"),  # _ITALICS_
            ("`", "\x11"),  # `MONOSPACE`
            ("~~", "\x1e")  # ~~STRIKETHROUGH~~
        ]

        # replace codeblocks
        msg = re.sub(r"```(?:\w+\n|\n)?(.+?)```", lambda m: createHaste(m.group(1)), msg, flags=re.S)

        # replace newlines
        if "\n" in msg:
            msg = msg.replace("\n", " ")

        # replace formatting
        for form in formatting_table:
            msg = replaceFormatting(form[0], form[1], msg)

        # clean up emotes
        msg = re.sub(r"<(:\w+:)\d+>", lambda m: m.group(1), msg)

        return msg

    def ircToDiscord(msg, channel, discord_client):
        # print(f"[IRC] {msg}")
        msg = re.sub(r"\x03\d{0,2}(?:,\d{0,2})?", "", msg)

        formatting_table = [
            (["\x02", "\x1D", "\x1F"], "***__"),  # bold italics underline
            (["\x1D", "\x1F"], "*__"),  # italics underline
            (["\x02", "\x1F"], "**_"),  # bold underline
            (["\x02", "\x1D"], "***"),  # bold italics
            (["\x02"], "**"),  # bold
            (["\x1D"], "*"),  # italics
            (["\x1F"], "__"),  # underline
            (["\x11"], "`"),  # code
            (["\x1e"], "~~")  # strikethrough
        ]

        for form in formatting_table:
            # check for matches for all permutation of the list
            perms = itertools.permutations(form[0])
            for perm in perms:
                if "\x0F" not in msg:
                    msg += "\x0F"
                msg = re.sub(r"{}(.*?)\x0F".format("".join(perm)),
                             lambda m: "{}{}{}".format(form[1], m.group(1), form[1][::-1]), msg)

        for char in ["\x02", "\x1D", "\x1F", "\x0F"]:
            msg = msg.replace(char, "")

        mentions = re.findall(r"@(\S+)", msg)
        if mentions:
            def mentionGetter(name_match):
                name = name_match.group(1)
                for member in discord_client.get_channel(channel).guild.members:  # dota2mods serverid
                    if member.name.lower() == name.lower() or (member.nick and member.nick.lower() == name.lower()):
                        return member.mention
                # user was not found, just return original text
                return "@" + name

            msg = re.sub(r"@(\S+)", mentionGetter, msg)

        return msg


class IRCBridge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global extension_name
        global irc_client
        irc_client = None
        extension_name = "[IRC Bridge] "

        # sch_irc = await aiojobs.create_scheduler()
        # await sch_irc.spawn(irc_run(self, ctx, con, sch_irc))

    @commands.command(hidden=True)
    async def irc(self, ctx):
        """Create a link to an IRC channel"""
        with open("./cogs/config.json") as fp:
            config = json.load(fp)

        chan_pairs = [(pair["irc_channel"], pair["discord_channel"]) for pair in config["pairs"]]
        print(chan_pairs)
        client = self.bot

        global irc_thread
        global irc_client
        irc_client = IRCClient(chan_pairs=chan_pairs, config=config["irc"], discord_client=client)
        irc_thread = None

        irc_thread = threading.Thread(target=irc_client.irc_run, daemon=True)
        irc_thread.start()

    @commands.Cog.listener('on_message')
    async def irc_on_message(self, message):
        global irc_client
        if message.webhook_id is not None:
            return

        if len(message.embeds) == 1 and message.content == "":
            # message.content = message.embeds[0].description
            message.content = "Embedded. Cannot show this message."

        if irc_client is not None:
            # print(f"Message from bot: {message.author != self.bot.user}")
            # print(f"Message is webhook: {message.webhook_id is None}")
            # if message.author != self.bot.user:
            with open("./cogs/config.json") as fp:
                config = json.load(fp)

            chan_pairs = [(pair["irc_channel"], pair["discord_channel"]) for pair in config["pairs"]]
            if chan_pairs[0][1] == message.channel.id:
                msg_string = f"{message.author}: {message.content}"
                irc_client.send_message(chan_pairs[0][0], msg_string)


def setup(bot):
    print("INFO: Loading [IRC]... ", end="")
    bot.add_cog(IRCBridge(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [IRC]")
