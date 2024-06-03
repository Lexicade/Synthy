import os

import psycopg2
from psycopg2 import extras
import discord
import json
import requests


async def get_colour(colour):
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
               "greyple": 0x99aab5,
               "black": 0x000000}
    return colours[colour]


async def sql(sql: str, params: tuple):
    con = psycopg2.connect(database=os.environ.get('db_name'),
                           user=os.environ.get('db_user'),
                           password=os.environ.get('db_pass'),
                           host=os.environ.get('db_host'),
                           port=os.environ.get('db_port'),
                           options=f'-c search_path={os.environ.get("db_schema")}')
    cur = con.cursor(cursor_factory=extras.DictCursor)

    cur.execute(sql, params)
    con.commit()

    sql_out = []
    if sql.startswith("SELECT"):
        columns = [str(column[0]).lower() for column in cur.description]
        rows = cur.fetchall()
        for row in rows:
            sql_row = dict(zip(columns, row))
            sql_out.append(sql_row)

    print(f"SQL Out: {sql_out}")

    cur.close()
    con.close()
    return sql_out


class CustomSQL:
    def __init__(self):
        self.cur = None
        self.con = None
        self.sql = None
        self.params = None
        self.db_name = None
        self.sql_data_output = None

    async def _setup_sql(self):
        self.con = psycopg2.connect(database=os.environ.get('db_name'),
                                    user=os.environ.get('db_user'),
                                    password=os.environ.get('db_pass'),
                                    host=os.environ.get('db_host'),
                                    port=os.environ.get('db_port'),
                                    options=f'-c search_path={os.environ.get("db_schema")}')
        self.cur = self.con.cursor(cursor_factory=extras.DictCursor)

    async def _run_sql(self):
        self.cur.execute(self.sql, self.params)
        self.con.commit()

    async def run_sql(self, sql: str, params: tuple):
        await self._setup_sql()

        self.sql = sql
        self.params = params
        await self._run_sql()

        if self.sql.upper().startswith("SELECT"):
            await self._process_sql()

        await self._close_sql()
        return self.sql_data_output

    async def _process_sql(self):
        self.sql_data_output = []
        columns = [str(column[0]).lower() for column in self.cur.description]
        rows = self.cur.fetchall()
        for row in rows:
            sql_row = dict(zip(columns, row))
            self.sql_data_output.append(sql_row)
            print(f"process_data: {self.sql_data_output}")

    async def check_table(self, db_name: str):
        await self._setup_sql()

        self.db_name = db_name
        await self._check_table()

        await self._close_sql()
        return self.sql_data_output

    async def _check_table(self):
        self.cur.execute("select exists(SELECT relname from pg_class where relname=%s);", (self.db_name,))
        self.con.commit()
        self.sql_data_output = self.cur.fetchone()[0]

    async def _close_sql(self):
        self.cur.close()
        self.con.close()


async def notice(title, message, colour="blue", footer=None):
    embed_colour = await get_colour(colour)
    emb = discord.Embed(title=title,
                        description=message,
                        colour=embed_colour)
    if footer:
        emb.set_footer(text=footer)

    return emb


async def embed(interaction: discord.Interaction, title, message, thumbnail=None, colour="blue", footer="", url="", image=None):
    embed_colour = await get_colour(colour)
    emb = discord.Embed(title=title, description=message, url=url, colour=embed_colour)
    emb.set_footer(text=f"Requested by {interaction.user}. {footer}", icon_url=interaction.user.display_avatar)

    if image:
        emb.set_image(url=image)

    if thumbnail:
        emb.set_thumbnail(url=thumbnail)

    return emb


async def author(emb, name="", url=""):
    emb.set_author(name=name, icon_url=url)
    return emb


async def footer(emb, text, url):
    emb.set_footer(text=text, icon_url=url)
    return emb


async def field(emb, name, value, inline=False):
    emb.add_field(name=name, value=value, inline=inline)
    return emb


async def log(guild_id, bot, msg=None, emb=None):
    guild = bot.get_guild(guild_id)
    guild_channels = guild.channels
    # print(guild.channels)
    for channel in guild_channels:
        try:
            if str(channel.type) == "text" and channel.name.lower() == "synthy-log":
                if msg is not None and emb is None:
                    await channel.send(content=msg)
                elif msg is None and emb is not None:
                    await channel.send(embed=emb)
                elif msg is not None and emb is not None:
                    await channel.send(content=msg, embed=emb)
        except:
            print('Cannot write to log channel')


async def get_request(url):
    obj_request_get = requests.get(url)
    if obj_request_get.status_code == 200:
        obj_data = json.loads(obj_request_get.text)
        return obj_data
    else:
        return None
# async def debuglog(username, module, log_msg):
#     config = configparser.ConfigParser()
#     with open(f"./cogs/cogs_{username}.json") as fp:
#         config = json.load(fp)
#         if module in config["debug"]["active"]:
#             sql = await sql("""INSERT INTO `logs` (`module`, `description`) VALUES ("%s", "%s")""", (module, log_msg))
