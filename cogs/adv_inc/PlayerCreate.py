# Embedded file name: /home/bouncer/sassbot/modules/advinc/PlayerCreate.py
import pymysql
import importlib
import utils

from cogs.adv_inc import PlayerStats
from cogs.adv_inc import Items

importlib.reload(utils)
importlib.reload(PlayerStats)
importlib.reload(Items)


async def pick_character_clan(params):
    if params['cmd1'] == '':
        return 'Name your Clan.'

    elif len(params['cmd1']) < 3:
        return 'Your Clan Name must be at least three characters.'

    else:
        await utils.sql_postgres('CALL adventurersinc.set_player_character_new(%s,%s)', (params['nick'], params['msg'].strip(),), False)
        return f"The adventure for the {params['msg'].strip()} clan begins."


async def pick_character_name(params, player_stats):
    if params['cmd1'] == '':
        return 'Give yourself a name.'
    
    elif len(params['cmd1']) < 3:
        return 'Your name must be at least three characters.'

    else:
        await utils.sql_postgres('CALL adventurersinc.set_player_character_name(%s, %s)', (params['cmd1'].strip(), params['nick'],), False)
        return f"You are {params['cmd1'].strip()} {player_stats['clan_name']}. Pick a race: (H)uman, (O)rc, (E)lf, (D)warf, (L)izard"


async def pick_character_race(params, player_stats):
    # Get chosen race
    str_race_selected = None
    if params['cmd1'].lower() == 'h':
        str_race_selected = 'Human'
    elif params['cmd1'].lower() == 'o':
        str_race_selected = 'Orc'
    elif params['cmd1'].lower() == 'e':
        str_race_selected = 'Elf'
    elif params['cmd1'].lower() == 'd':
        str_race_selected = 'Dwarf'
    elif params['cmd1'].lower() == 'l':
        str_race_selected = 'Lizard'
    else:
        return 'Pick a race: (H)uman, (O)rc, (E)lf, (D)warf, (L)izard'

    if str_race_selected is not None:
        race_stats = await utils.sql_postgres('SELECT adventurersinc.get_race_stats(%s)', (str_race_selected,), True)
        await utils.sql_postgres('CALL adventurersinc.set_player_character_race(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (race_stats[0][0]['strength'],
                                 race_stats[0][0]['dexterity'], race_stats[0][0]['constitution'], race_stats[0][0]['intelligence'], race_stats[0][0]['dodge'], race_stats[0][0]['crit'], race_stats[0][0]['armour'],
                                 race_stats[0][0]['accuracy'], race_stats[0][0]['resistance'], race_stats[0][0]['luck'], race_stats[0][0]['block'], params['nick'], str_race_selected), False)

        player_stats = await PlayerStats.refresh_stats(params)
        await utils.sql_postgres("CALL adventurersinc.set_player_health(%s,%s)", (player_stats['max_hp'], params['nick'],), False)

        return f"{player_stats['character_name']} {player_stats['clan_name']} the {str_race_selected} begins their adventure"
    else:
        return
