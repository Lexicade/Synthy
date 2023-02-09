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

    def irc_connect(self, server, port, nickname, password):
        print("Connecting to {}:{}".format(server, port))

        s = socket.socket()

        s.connect((server, port))
        s.send(f"NICK {nickname}\r\n".encode())
        s.send(f"USER {nickname} * * {nickname}\r\n".encode())
        s.send(f"PASS {nickname}:{password}\r\n".encode())

        self.connected = True
        print("Connected.")
        self.send_to_webhook("[IRC Bridge]", "Connected!")

        return s, server, nickname

    def join_channels(self):
        for channel in [pair[0] for pair in self.chan_pairs]:
            print(f"Joining {channel}")
            self.s.send(f"JOIN {channel}\r\n".encode())
        return

    def msg_process(self, rawmsg):  # figure out what we want to do with our irc message
        prefix, command, args, msg = self.split_msg(rawmsg)
        print(f"[IRC] {rawmsg}")

        # msg format is "nick PRIVMSG #channel :message"
        if command in ["376", "422"]:
            print("END OF MOTD")
            self.join_channels()

        elif command == "PING":
            self.s.send("PONG {}\r\n".format(msg).encode())
            print("PONG'd")

        elif command == "PRIVMSG":
            author = prefix.split("!")[0]

            # send message to run comm coroutine
            for pair in self.chan_pairs:
                if args[0] == pair[0]:
                    if msg.startswith("?status") and len(msg.split()) > 1:
                        name = msg.split(" ", 1)[1].lower()
                        status_msg = ""
                        for member in self.discord_client.get_channel(pair[1]).guild.members:
                            if member.name.lower() == name or (member.nick and member.nick.lower() == name):
                                status_msg += "{} is currently {}".format(member.name, str(member.status))

                        self.send_message(args[0], status_msg)
                        continue

                    elif msg.startswith("?optin"):
                        cfg = GlobalMethods.get_config()
                        if author not in cfg["users"]:
                            print("a")
                            cfg["users"].append(author)
                            with open("./cogs/config_sb.json", 'w') as fp:
                                json.dump(cfg, fp, indent=4)
                            response = "Added to THE BRIDGE!"
                        else:
                            response = "You're already on THE BRIDGE!"
                            print("b")
                        print("c")
                        self.send_message(args[0], response)
                        continue

                    elif msg.startswith("?optout"):
                        cfg = GlobalMethods.get_config()
                        if author in cfg["users"]:
                            cfg["users"].remove(author)
                            with open("./cogs/config_sb.json", 'w') as fp:
                                json.dump(cfg, fp, indent=4)
                            response = "Removed from THE BRIDGE!"
                        else:
                            response = "You've not opted into THE BRIDGE!"
                        self.send_message(args[0], response)
                        continue

                    # Check allowed user
                    config = GlobalMethods.get_config()

                    # Clean message
                    clean_msg = GlobalMethods.irc_to_discord(msg)

                    # clean_msg = GlobalMethods.irc_to_discord(msg, pair[1], self.discord_client)
                    action_regex = re.match(r"\u0001ACTION (.+)\u0001", clean_msg)  # format /me
                    # if action_regex:
                    #     formatted_msg = "**\* {}** {}".format(author, action_regex.group(1))
                    # else:
                    #     formatted_msg = "**<{}>** {}".format(author, clean_msg)

                    discord_channel = self.discord_client.get_channel(pair[1])
                    # Create webhook
                    self.send_to_webhook(author, clean_msg)

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
            responce = self.s.recv(2048)

            line_buffer += responce.decode()
            lines = line_buffer.split("\n")

            line_buffer = lines.pop()

            for line in lines:
                line = line.rstrip()

                if line:
                    self.msg_process(line)
                else:
                    pass

    def stop_irc(self):
        self._Thread_stop()

    def send_to_webhook(self, author, msg):
        config = GlobalMethods.get_config()

        opt_ins = GlobalMethods.get_opts()
        if author not in opt_ins:
            return

        webhook = Webhook.partial(config["webhook"][0]["id"],
                                  config["webhook"][0]["key"],
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
            # self.send("PRIVMSG {} :{}\r\n".format(channel, msg).encode())
            self.s.send("PRIVMSG {} :{}\r\n".format(channel, msg).encode())

        except BrokenPipeError as e:
            _thread.interrupt_main()
        # exit("Error in message size too large. Exiting...")
        return


class GlobalMethods:
    def discordToIrc_deprec(msg):
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

    def ircToDiscord_deprec(msg, channel, discord_client):
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

    def discord_to_irc(self, msg):
        # Clean up emoji IDs
        for emoji_match in re.findall(r"<a?:\D+:\d+>", msg.content):
            clean_match = re.search(r"a?:\D+:", emoji_match)
            msg.content = msg.content.replace(emoji_match, clean_match.group()).strip()

        # Clean up channel IDs
        for channel_match in re.findall(r"<#\d+>", msg.content):
            channel_id = re.search(r"\d+", channel_match)
            channel = self.bot.get_channel(int(channel_id.group()))
            msg.content = msg.content.replace(channel_match, f"#{channel.name}/Discord").strip()

        # Clean up user IDs
        for user_match in re.findall(r"<@!?\d+>", msg.content):
            user_id = re.search(r"\d+", user_match)
            user = self.bot.get_user(int(user_id.group()))
            msg.content = msg.content.replace(user_match, f"@{user.name}").strip()

        # Check up on the URLs
        # for url_match in re.findall(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", msg):
        for attachment in msg.attachments:
            msg.content = f"{msg.content} {attachment.url}".strip()

        return msg

    @staticmethod
    def irc_to_discord(msg):
        if msg.startswith("!") or msg.startswith("sb!"):
            msg = f".{msg}"
        return msg

    @staticmethod
    def get_config():
        with open("./cogs/config_sb.json") as fp:
            config = json.load(fp)

        return config

    @staticmethod
    async def get_opts():
        cfg = GlobalMethods.get_config()
        response = ", ".join(cfg["users"])
        return response

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
        config = GlobalMethods.get_config()
        chan_pairs = [(pair["irc_channel"], pair["discord_channel"]) for pair in config["pairs"]]
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
        # if message.channel.id == 547581821957701632 and len(message.content) > 0:
        #     # Create webhook
        #     webhook = Webhook.partial(676475492202709033, "MDwKMQhB6zB6qol-U7k9pdKbEmp_B1s-LjoXNslyFJ_CZrO7CST2GdFpDFmz8nSNuBCZ", adapter=RequestsWebhookAdapter())
        #
        #     # Send temperature as text
        #     webhook.send(content=u"" + message.content + "",
        #                  wait=False,
        #                  username=message.author.name,
        #                  avatar_url=f"https://eu.ui-avatars.com/api/name={message.author.name}?length=1?&background=0088ff&color=FFF",
        #                  tts=False,
        #                  file=None,
        #                  files=None,
        #                  embed=None,
        #                  embeds=None)
        #
        #
        #     #https://discordapp.com/api/webhooks/676475492202709033/MDwKMQhB6zB6qol-U7k9pdKbEmp_B1s-LjoXNslyFJ_CZrO7CST2GdFpDFmz8nSNuBCZ
        #
        # elif message.channel.id == 654002737167597588:
        #     print(f"{message.author.name}:{message.content}")
        # print(f"[IRC] {message}")

        if message.webhook_id is not None:
            return

        if len(message.embeds) == 1 and message.content == "":
            # message.content = message.embeds[0].description
            message.content = "Embedded. Cannot show this message."

        if irc_client is not None:
            # print(f"Message from bot: {message.author != self.bot.user}")
            # print(f"Message is webhook: {message.webhook_id is None}")
            # if message.author != self.bot.user:
            config = GlobalMethods.get_config()

            chan_pairs = [(pair["irc_channel"], pair["discord_channel"]) for pair in config["pairs"]]
            if chan_pairs[0][1] == message.channel.id:
                # Check for username shenannigans
                # ?

                # Ensure message content gets cleaned up
                message = GlobalMethods.discord_to_irc(self, message)

                msg_string = f"{message.author.name}: {message.content}"

                irc_client.send_message(chan_pairs[0][0], msg_string)

        if message.content == "sb!shutdown":
            global irc_thread
            irc_thread.stop_irc()


def setup(bot):
    print("INFO: Loading [IRC_SB]... ", end="")
    bot.add_cog(IRCBridge(bot))
    print("Done!")


def teardown(bot):
    # global irc_thread
    # global irc_client
    # irc_client.shutdown()
    # irc_thread.stop()
    # irc_client = None
    # irc_thread = None

    print("INFO: Unloading [IRC_SB]")
