import time
import pymysql
import importlib
import utils

from cogs.adv_inc import Calculate

importlib.reload(utils)
importlib.reload(Calculate)


async def character_death(player_stats, params):
    # Create death entry
    sql = 'CALL adventurersinc.add_player_graveyard_death(%s, %s, %s, %s, %s, %s);'
    query_params = (params['nick'], player_stats['character_name'], player_stats['clan_name'], player_stats["total_items"], player_stats['challenge_rating'], str(params['game_version']),)
    # print(f"1 {sql % query_params}")
    await utils.sql_postgres(sql, query_params, False)

    # Delete players Inventory
    sql = 'CALL adventurersinc.del_player_inventory(%s);'
    query_params = (params['nick'],)
    # print(f"2 {sql % query_params}")
    await utils.sql_postgres(sql, query_params, False)

    # Delete players opponent
    sql = 'CALL adventurersinc.del_player_enemies(%s);'
    query_params = (params['nick'],)
    # print(f"3 {sql % query_params}")
    await utils.sql_postgres(sql, query_params, False)

    # Delete players shop
    sql = 'CALL adventurersinc.del_player_shop(%s);'
    query_params = (params['nick'],)
    # print(f"4 {sql % query_params}")
    await utils.sql_postgres(sql, query_params, False)

    # Update player record for new character + lose gold on death
    sql = 'CALL adventurersinc.set_player_death(%s);'
    query_params = (params['nick'],)
    # print(f"5 {sql % query_params}")
    await utils.sql_postgres(sql, query_params, False)
