import sys
import math
import os
import importlib
import utils

from cogs.adv_inc import Calculate

importlib.reload(utils)
importlib.reload(Calculate)


async def print_stats(params):
    player_stats = await refresh_stats(params)

    dodge_perc = await Calculate.get_dodge_chance(player_stats['dexterity'], player_stats['dodge'])
    luck_chance = await Calculate.get_luck_chance(player_stats['luck'])
    armour_perc = await Calculate.get_armour_percentage(player_stats['armour'], player_stats['strength'], player_stats['constitution'])
    crit_perc = await Calculate.get_crit_percentage(player_stats['dexterity'], player_stats['crit'])
    block_perc = await Calculate.get_block_chance(player_stats['strength'], player_stats['block'])

    emb = await utils.embed(params["ctx"], f"Stats of {player_stats['character_name']} {player_stats['clan_name']}", "")
    emb = await utils.field(emb, "Race", f"{player_stats['race']}", True)
    emb = await utils.field(emb, "HP", f"{player_stats['hp']}/{player_stats['max_hp']}", True)
    emb = await utils.field(emb, "STR", f"{player_stats['strength']}", True)
    emb = await utils.field(emb, "Challenge Rating", f"{player_stats['challenge_rating']}", True)
    emb = await utils.field(emb, "DEX", f"{player_stats['dexterity']}", True)
    emb = await utils.field(emb, "CON", f"{player_stats['constitution']}", True)
    emb = await utils.field(emb, "INT", f"{player_stats['intelligence']}", True)
    emb = await utils.field(emb, "Gold", f"{player_stats['currency']}", True)
    emb = await utils.field(emb, "Dodge", f"{player_stats['dodge']} / ({math.floor(dodge_perc * 100)}%)", True)
    emb = await utils.field(emb, "Crit", f"{player_stats['crit']} / ({math.floor(crit_perc * 100)}%)", True)
    emb = await utils.field(emb, "Armour", f"{player_stats['armour']} / ({math.floor(armour_perc * 100)}%)", True)
    emb = await utils.field(emb, "Accuracy", f"{player_stats['accuracy']}", True)
    emb = await utils.field(emb, "Resistance", f"{player_stats['resistance']}", True)
    emb = await utils.field(emb, "Luck", f"{player_stats['luck']} / ({luck_chance})", True)
    emb = await utils.field(emb, "Block", f"{player_stats['block']} / ({math.floor(block_perc * 100)}%)", True)
    emb = await utils.field(emb, "Items", f"{player_stats['total_items']}", True)

    return emb


async def refresh_stats(params):
    sql_player_info = await utils.sql_postgres("SELECT adventurersinc.get_player_info(%s);", (params['nick'],), True)
    sql_player_stats = await utils.sql_postgres("SELECT adventurersinc.get_player_stats(%s);", (params['nick'],), True)

    # print(f"sql_player_info: {sql_player_info}")
    # print(f"sql_player_info[0][0]: {sql_player_info[0][0]}")

    if sql_player_info[0][0] is None:
        return None
    else:
        player_stats = {'nick': sql_player_info[0][0]['nick'],
                        'currency': sql_player_info[0][0]['currency'],
                        'clan_name': sql_player_info[0][0]['clan_name'],
                        'character_name': sql_player_info[0][0]['character_name'],
                        'player_state': sql_player_info[0][0]['player_state'],
                        'alive': sql_player_info[0][0]['alive'],
                        'challenge_rating': sql_player_info[0][0]['challenge_rating'],
                        'rested_heal': sql_player_info[0][0]['rested_heal'],
                        'hp': sql_player_info[0][0]['hp'],
                        'max_hp': int(sql_player_stats[0][0]['constitution'] * 2),
                        'attribute_points': sql_player_info[0][0]['attribute_points'],
                        'hands_req': sql_player_stats[0][0]['hands_req'],
                        'unit_type': 'player',
                        'strength': sql_player_stats[0][0]['strength'],
                        'dexterity': sql_player_stats[0][0]['dexterity'],
                        'constitution': sql_player_stats[0][0]['constitution'],
                        'intelligence': sql_player_stats[0][0]['intelligence'],
                        'dodge': sql_player_stats[0][0]['intelligence'],
                        'crit': sql_player_stats[0][0]['crit'],
                        'armour': sql_player_stats[0][0]['armour'],
                        'accuracy': sql_player_stats[0][0]['accuracy'],
                        'resistance': sql_player_stats[0][0]['resistance'],
                        'luck': sql_player_stats[0][0]['luck'],
                        'block': sql_player_stats[0][0]['block'],
                        'total_items': sql_player_info[0][0]['total_items'],
                        'race': sql_player_info[0][0]['race']}
        return player_stats
