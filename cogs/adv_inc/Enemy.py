import pymysql
import math
import random
import importlib
import utils

importlib.reload(utils)


async def create_enemy(enemy_stats, player_stats, params):
    # Update player state for combat
    await utils.sql_postgres("CALL adventurersinc.set_playerstate_combat(%s)", (params['nick'],), False)

    # If challenge_rating is an INT we'll swap for a boss
    if player_stats['challenge_rating'] == int(math.ceil(player_stats['challenge_rating'] / 4) * 4):
        str_class = "boss"
    else:
        str_class = "normal"

    # Get enemy weighting list
    all_enemies = await utils.sql_postgres(f"SELECT adventurersinc.get_all_enemies(%s)", (str_class,), True)
    int_total_weight = random.randint(1, all_enemies[0][0]['total_weight'])

    # Apply challenge rating modifier to enemy
    int_challenge_modifier = player_stats['challenge_rating'] / 2

    for enemy in all_enemies:
        int_total_weight = int_total_weight - enemy[0]['enemy_weight']
        if int_total_weight <= 0:
            # Set stats
            enemy[0]['enemy_colour'] = enemy[0]['enemy_colour']
            enemy[0]['enemy_name'] = str(enemy[0]['enemy_name'])
            enemy[0]['enemy_class'] = str(enemy[0]['enemy_class'])
            enemy[0]['unlock'] = str(enemy[0]['unlock'])
            enemy[0]['hp'] = math.floor(enemy[0]['hp'] * int_challenge_modifier)
            enemy[0]['enemy_weight'] = math.floor(enemy[0]['enemy_weight'] * int_challenge_modifier)
            enemy[0]['challenge_rating'] = math.floor(enemy[0]['challenge_rating'] * int_challenge_modifier)
            enemy[0]['gold_carried'] = math.floor(enemy[0]['gold_carried'] * int_challenge_modifier)
            enemy[0]['strength'] = math.floor(enemy[0]['strength'] * int_challenge_modifier)
            enemy[0]['dexterity'] = math.floor(enemy[0]['dexterity'] * int_challenge_modifier)
            enemy[0]['constitution'] = math.floor(enemy[0]['constitution'] * int_challenge_modifier)
            enemy[0]['intelligence'] = math.floor(enemy[0]['intelligence'] * int_challenge_modifier)
            enemy[0]['dodge'] = math.floor(enemy[0]['dodge'] * int_challenge_modifier)
            enemy[0]['crit'] = math.floor(enemy[0]['crit'] * int_challenge_modifier)
            enemy[0]['accuracy'] = math.floor(enemy[0]['accuracy'] * int_challenge_modifier)
            enemy[0]['resistance'] = math.floor(enemy[0]['resistance'] * int_challenge_modifier)
            enemy[0]['luck'] = math.floor(enemy[0]['luck'] * int_challenge_modifier)
            enemy[0]['block'] = math.floor(enemy[0]['block'] * int_challenge_modifier)
            break

    await utils.sql_postgres("CALL adventurersinc.add_player_enemy(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (params['nick'], enemy[0]['enemy_colour'], enemy[0]['enemy_name'], enemy[0]['enemy_class'], enemy[0]['unlock'], enemy[0]['hp'], enemy[0]['enemy_weight'],enemy[0]['challenge_rating'], enemy[0]['gold_carried'],
                              enemy[0]['strength'], enemy[0]['dexterity'], enemy[0]['constitution'], enemy[0]['intelligence'], enemy[0]['dodge'], enemy[0]['crit'], enemy[0]['accuracy'], enemy[0]['resistance'], enemy[0]['luck'], enemy[0]['block'],), False)

    return enemy[0]


async def get_enemy_stats(params):
    enemy = await utils.sql_postgres("SELECT adventurersinc.get_player_enemy(%s)", (params['nick'],), True)
    if enemy[0][0] is None:
        return None

    enemy[0][0]['enemy_colour'] = enemy[0][0]['enemy_colour']
    enemy[0][0]['enemy_name'] = enemy[0][0]['enemy_name']
    enemy[0][0]['enemy_class'] = enemy[0][0]['enemy_class']
    enemy[0][0]['unlock'] = enemy[0][0]['unlock']
    enemy[0][0]['hp'] = enemy[0][0]['hp']
    enemy[0][0]['gold_carried'] = enemy[0][0]['gold_carried']
    enemy[0][0]['strength'] = enemy[0][0]['strength']
    enemy[0][0]['dexterity'] = enemy[0][0]['dexterity']
    enemy[0][0]['constitution'] = enemy[0][0]['constitution']
    enemy[0][0]['intelligence'] = enemy[0][0]['intelligence']
    enemy[0][0]['dodge'] = enemy[0][0]['dodge']
    enemy[0][0]['crit'] = enemy[0][0]['crit']
    enemy[0][0]['accuracy'] = enemy[0][0]['accuracy']
    enemy[0][0]['resistance'] = enemy[0][0]['resistance']
    enemy[0][0]['luck'] = enemy[0][0]['luck']
    enemy[0][0]['block'] = enemy[0][0]['block']
    enemy[0][0]['armour'] = 0
    enemy[0][0]['unit_type'] = 'enemy'

    return enemy[0][0]
