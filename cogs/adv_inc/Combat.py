import pymysql
import math
import re
import sys
import random
import os
import importlib
import utils

from cogs.adv_inc import PlayerStats
from cogs.adv_inc import Items
from cogs.adv_inc import Enemy
from cogs.adv_inc import PlayerDeath
from cogs.adv_inc import Calculate

importlib.reload(utils)
importlib.reload(PlayerStats)
importlib.reload(Items)
importlib.reload(Enemy)
importlib.reload(PlayerDeath)
importlib.reload(Calculate)


async def player_in_combat(params):
    player_stats = await PlayerStats.refresh_stats(params)
    enemy_stats = await Enemy.get_enemy_stats(params)
    if enemy_stats is None:
        str_output = "Combat error, returning to camp."
        await utils.sql_postgres('CALL adventurersinc.del_player_enemies(%s)', (params['nick'],), False)
        await utils.sql_postgres('CALL adventurersinc.set_player_state(%s, %s)', (params['nick'], 'rest',), False)
        return str_output

    str_attack_log = ''
    
    # Attack
    if params['cmd1'] == 'a' or params['cmd1'] == 'attack':
        # Players attack
        str_attack_log = str_attack_log + await perform_attack(player_stats, enemy_stats, params)
    
        if enemy_stats['hp'] <= 0:
            str_attack_log = str_attack_log + f"The {enemy_stats['enemy_name']} falls to the floor. "

            # Generate equipment item
            if random.randint(1, 2) == 1 and enemy_stats['enemy_class'] == 'normal':

                # Generate Shard of Chaos on Chaos kill
                if enemy_stats['unlock'] == 'chaos':
                    await utils.sql_postgres(f"CALL adventurersinc.add_shard_of_chaos(%s)", (params["nick"],), False)
                    return "You acquire a Shard of Chaos from the remains of the enemy."

                # Generate normal equipment drop
                elif enemy_stats['unlock'] == 'default':
                    # Equipment Drop Rarity:Element:Item:Enchantment:Fabled
                    item_gen = await Items.generate_equipment(params, '0:0:0:0:0')
                    str_attack_log = str_attack_log + f"You obtained a {item_gen['equipment_colour']} {item_gen['equipment_name']}. "
                    await Items.add_to_inventory(params, item_gen)

            # Generate gold drop
            if random.randint(1, 1) == 1:
                await utils.sql_postgres("CALL adventurersinc.set_player_exit_combat(%s, %s)", (enemy_stats['gold_carried'], params["nick"],), False)
                str_attack_log = str_attack_log + f"You found {enemy_stats['gold_carried']} gold. "

            await utils.sql_postgres("CALL adventurersinc.del_player_enemies(%s)", (params["nick"],), False)

            # Attempt to restock shop
            if random.randint(1, 2) == 1:
                str_attack_log = str_attack_log + "A new travelling merchant has arrived. "
                await utils.sql_postgres("CALL adventurersinc.del_player_shop(%s)", (params["nick"],), False)

                for i in range(1, (random.randint(3, 5) + 1)):
                    await Items.add_to_shop(params, await Items.generate_equipment(params, '0:0:0:0:1'))

            # # Unlock boss items
            # if enemy_stats['unlock'] is not 'default' and enemy_stats['enemy_class'] is 'boss':
            #     await utils.sql_postgres("", (params['nick'], enemy_stats['Unlock'],), True)
            #     sql_unlock_check = c.fetchone()
            #     if str(sql_unlock_check['requirement']) == '0':
            #         Items.unlock_items(params, str(enemy_stats['unlock']))
            #         return "Additional items will now begin appearing"
    
            player_stats = await PlayerStats.refresh_stats(params)
            if float(player_stats['challenge_rating']).is_integer():
                int_attribute_points = 2 + int(player_stats["challenge_rating"])
                await utils.sql_postgres("CALL adventurersinc.set_player_attribute_points(%s, %s)", (int_attribute_points, params["nick"],), False)
                str_attack_log = str_attack_log + f"You have gained {int_attribute_points} attribute points. "
        else:
            # Enemy attack
            str_attack_log = str_attack_log + await perform_attack(enemy_stats, player_stats, params)
    
            if player_stats['hp'] <= 0:
                str_attack_log = f"{str_attack_log}. You died. (http://adventurersinc.lelong.uk/graveyard/)"
                await PlayerDeath.character_death(player_stats, params)
    
        return "" + str_attack_log
    
    # flee
    elif params['cmd1'].lower() == 'f' or params['cmd1'].lower() == 'flee':
        if random.randint(1, 2) == 1:
            return await flee_combat(params)
        else:
            str_output = f"You failed to escape. {await perform_attack(enemy_stats, player_stats, params)}"
            if player_stats['hp'] <= 0:
                str_output = f"{str_output}. You were struck down as you attempted to flee. You died. (http://adventurersinc.lelong.uk/graveyard/)"
                await PlayerDeath.character_death(player_stats, params)
            return str_output
    
    # Admin commands
    elif params['cmd1'].lower() == 'admin' and input.admin:
        return perform_attack(player_stats, enemy_stats, params["nick"])
    else:
        return "Available commands: (a)ttack, (f)lee"


async def perform_attack(attacker_stats, defender_stats, params):
    # Check if the defender dodges
    dodge_perc = await Calculate.get_dodge_chance(int(defender_stats['dexterity']), int(defender_stats['dodge']))
    if random.randint(0, 100) < math.floor(dodge_perc * 100):
        if attacker_stats['unit_type'] == 'player':
            return "You miss. "
        elif attacker_stats['unit_type'] == 'enemy':
            return f"You dodge the {attacker_stats['enemy_name']}'s attack. "

    # Check if the defender blocks
    block_perc = await Calculate.get_block_chance(defender_stats['strength'], defender_stats['block'])
    if random.randint(0, 100) < math.floor(block_perc * 100):
        if attacker_stats['unit_type'] == 'player':
            return "The enemy blocks your attack. "
        elif attacker_stats['unit_type'] == 'enemy':
            return f"You block the {attacker_stats['enemy_name']}'s attack. "

    # Generate combat values
    int_attack_damage = await Calculate.get_attack_power(attacker_stats['strength'], attacker_stats['dexterity'])
    int_armour_perc = await Calculate.get_armour_percentage(attacker_stats['armour'], attacker_stats['strength'], attacker_stats['constitution'])
    int_crit_chance = await Calculate.get_crit_percentage(attacker_stats['crit'], attacker_stats['dexterity'])
    int_final_damage = int_attack_damage - (int_attack_damage * int_armour_perc)

    # Determine if the attacker is going to crit
    if random.randint(0, 100) < (int_crit_chance * 100):
        int_final_damage = int_final_damage * 2
        str_crit = '**CRIT**'
    else:
        str_crit = 'did'

    # Round this up to avoid decimals
    int_final_damage = math.ceil(int_final_damage)

    # Update defender health
    defender_stats['hp'] = defender_stats['hp'] - int_final_damage

    # Update HP of the appropriate unit_type
    await utils.sql_postgres(f"CALL adventurersinc.set_{str(defender_stats['unit_type'])}_health(%s, %s);", (int(defender_stats['hp']), int(params['nick']),), False)

    # Assemble hit message
    if attacker_stats['unit_type'] == 'player':
        return f"You {str_crit} {int_final_damage} damage. "
    elif attacker_stats['unit_type'] == 'enemy':
        return f"The {attacker_stats['enemy_name']} {str_crit} {int_final_damage} damage. "


async def flee_combat(params):
    # Delete players opponent
    await utils.sql_postgres("CALL adventurersinc.del_player_enemies(%s);", (params['nick'],), False)

    # Update player record for player
    await utils.sql_postgres("CALL adventurersinc.set_player_state(%s,%s)", (params['nick'], 'rest',), False)

    return "You flee your enemy."
