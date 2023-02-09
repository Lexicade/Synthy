import pymysql
import sys
import os
import importlib
import utils

from cogs.adv_inc import PlayerStats

importlib.reload(PlayerStats)


async def level_up_attributes(params):
    # In the event no valid value is given, assume the points to assign will be 1
    try:
        params['cmd2'] = int(params['cmd2'])
    except ValueError:
        params['cmd2'] = 1

    # Get players attribute points
    player_attribute_points = await utils.sql_postgres("SELECT adventurersinc.get_player_attribute_points(%s);", (params["nick"],), True)

    # Prevent over-allocation
    if int(params['cmd2']) > player_attribute_points[0][0]['attribute_points']:
        return "You cannot apply more points than you have."

    # Attribute allocation
    else:
        if params['cmd1'].lower() == 's':
            await utils.sql_postgres("CALL adventurersinc.set_player_attribute_strength(%s, %s)", (params['cmd2'], params["nick"],), False)
        elif params['cmd1'].lower() == 'd':
            await utils.sql_postgres("CALL adventurersinc.set_player_attribute_dexterity(%s, %s)", (params['cmd2'], params["nick"],), False)
        elif params['cmd1'].lower() == 'c':
            await utils.sql_postgres("CALL adventurersinc.set_player_attribute_constitution(%s, %s)", (params['cmd2'], params["nick"],), False)
        elif params['cmd1'].lower() == 'i':
            await utils.sql_postgres("CALL adventurersinc.set_player_attribute_intelligence(%s, %s)", (params['cmd2'], params["nick"],), False)

        player_stats = await PlayerStats.refresh_stats(params)

        # await utils.sql_postgres("CALL adventurersinc.set_player_attribute_intelligence(%s, %s)", (int_attribute_points, params["nick"],), False)
        # c.execute("UPDATE Players SET HP = %s WHERE Nick='%s';", (player_stats['MaxHP'], params["Nick"]));db.commit();
        return f"Attribute Points: {player_stats['attribute_points']}   (S)tr:{player_stats['strength']}   (D)ex:{player_stats['dexterity']}   (C)on:{player_stats['constitution']}   (I)nt:{player_stats['intelligence']}"
