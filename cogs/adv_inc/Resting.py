#Python modules
import math
import re
import sys
import os
import importlib
import utils

from cogs.adv_inc import PlayerStats
from cogs.adv_inc import Enemy
from cogs.adv_inc import Items

importlib.reload(utils)
importlib.reload(PlayerStats)
importlib.reload(Enemy)
importlib.reload(Items)


async def player_resting(params, player_stats):
    # Inventory
    if params["cmd1"].lower() == 'i' or params["cmd1"].lower() == 'inventory':
        try:
            params["cmd2"] = int(params["cmd2"])
        except ValueError:
            params["cmd2"] = 1

        obj_player_inventory = await utils.sql_postgres("SELECT adventurersinc.get_player_inventory(%s, %s);", (params["nick"], (int(params["cmd2"]) * 5) - 5,), True)
        # print(f"obj_player_inventory {obj_player_inventory}")
        if not obj_player_inventory:
            return "You have no items."
        int_total_pages = int(math.ceil(obj_player_inventory[0][0]["total_items"] / 5))

        str_output = ""
        # print("#total pages", int_total_pages)
        if 0 < params["cmd2"] <= int_total_pages:
            str_output = f'Page {params["cmd2"]} of {int_total_pages}. (http://adventurersinc.lelong.uk/inventory/{params["nick"]})\n'
            # print(str_output)

            for item in obj_player_inventory:
                str_equipped = 'Equipped    ' if item[0]["equipped"] == 1 else 'Unequipped'
                str_hands = "--" if str(item[0]["hands_req"]) == '0' else str(item[0]["hands_req"]) + "H"

                str_output = f"{str_output}{item[0]['item_id']} {str_equipped} {str_hands} {item[0]['equipment_colour']} {item[0]['equipment_name']}\n"
            return str_output
    
    # Equip WIP
    elif params["cmd1"].lower() == 'e' or params["cmd1"].lower() == 'equip':
        # Check to un-equip
        if params["cmd2"] == 'u' or params["cmd2"] == 'unequip':
            await utils.sql_postgres("CALL adventurersinc.set_player_unequip_all(%s)", (params["nick"],), False)
            return "All items have been unequipped."

        elif params["cmd2"].isdigit():
            # Check to see if an ID was supplied
            sql_item = await utils.sql_postgres("SELECT adventurersinc.get_player_inventory_item(%s,%s);", (params["nick"], params["cmd2"],), True)
            if sql_item[0][0] is not None:
                # If selected item is weapon
                if sql_item[0][0]['equipment_type'] == 'weapon':
                    sql_hands_used = await utils.sql_postgres("SELECT adventurersinc.get_player_equip_hands_used(%s)", (params["nick"],), True)
                    if sql_hands_used[0][0] is None:
                        sql_hands_used[0][0]["hands_req"] = 0

                    if sql_hands_used[0][0]["hands_req"] + sql_item[0][0]['hands_req'] <= 2 and sql_item[0][0]['equipped'] == 0:
                        await utils.sql_postgres("CALL adventurersinc.set_player_equipped_item(%s, %s, %s);", (params["cmd2"], True, params["nick"],), False)
                        return f"Equipping your {sql_item[0][0]['equipment_colour']}{sql_item[0][0]['equipment_name']}."

                    elif sql_item[0][0]['equipped'] == 1:
                        await utils.sql_postgres("CALL adventurersinc.set_player_equipped_item(%s, %s, %s);", (params["cmd2"], False, params["nick"],), False)
                        return f"Unequipping your {sql_item[0][0]['equipment_colour']}{sql_item[0][0]['equipment_name']}."

                    else:
                        return "You can only wield one two-handed weapon, or two one-handed weapons."
    
                # If selected item is Armor
                elif sql_item[0][0]['equipment_type'] == 'armour':
                    sql_armour = await utils.sql_postgres("SELECT adventurersinc.get_player_equip_armour_slot(%s, %s)", (params["nick"], sql_item[0][0]['equipment_slot'],), True)

                    # print(sql_armour)
                    if sql_item[0][0]['equipped'] is False and sql_armour[0][0] is None:
                        await utils.sql_postgres("CALL adventurersinc.set_player_equipped_item(%s, %s, %s);", (params["cmd2"], True, params["nick"],), False)
                        return f"Equipping your {sql_item[0][0]['equipment_colour']}{sql_item[0][0]['equipment_name']}."

                    elif sql_item[0][0]['equipped'] is True:
                        await utils.sql_postgres("CALL adventurersinc.set_player_equipped_item(%s, %s, %s);", (params["cmd2"], False, params["nick"],), False)
                        return f"Unequipping your {sql_item[0][0]['equipment_colour']}{sql_item[0][0]['equipment_name']}."

                    else:
                        return "You already have an item in this slot."
            else:
                return "This item does not exist."
    
        # All other checks failed, print help message
        else:
            return "Available commands: e (u)nequip all, e <ID to equip/unequip>"
    
    # Destroy WIP
    elif params["cmd1"].lower() == 'd' or params["cmd1"].lower() == 'destroy':
        if re.match("^[0-9]+$", params["cmd2"]):
            c.execute("SELECT ID,nick,EquipmentColour,EquipmentSlot,equipment_type,EquipmentName,equipped,hands_req FROM Items_PlayerInventory WHERE nick='%s' AND ID=%s",(params["nick"], params["cmd2"],))
            sql_item = c.fetchone()
            item_name = sql_item['EquipmentName']
            item_colour = sql_item['EquipmentColour']
            if sql_item is not None:
                c.execute("DELETE FROM Items_PlayerInventory WHERE nick='%s' AND ID=%s",(params["nick"], params["cmd2"]));db.commit();
                return f"Your {item_name} has been destroyed."
    
    # Battle
    elif params["cmd1"].lower() == 'b' or params["cmd1"].lower() == 'battle':
        enemy = {}
        if player_stats['challenge_rating'] == int(math.ceil(player_stats['challenge_rating'] / 4) * 4):
            enemy = await Enemy.create_enemy(enemy, player_stats, params)
            return f"Your fighting has caught the attention of the {enemy['enemy_name']}."
        else:
            enemy = await Enemy.create_enemy(enemy, player_stats, params)
            return f"You've been attacked by {enemy['enemy_name']}."
    
    # Character
    elif params["cmd1"].lower() == 'c' or params["cmd1"].lower() == 'character':
        return await PlayerStats.print_stats(params)
    
    # Shop
    elif params["cmd1"].lower() == 's' or params["cmd1"].lower() == 'shop':
        if params["cmd2"] is '':
            sql_shop_inventory = await utils.sql_postgres("SELECT adventurersinc.get_player_shop_all(%s, %s);", (params["nick"], '%'), True)
            str_output = f"You have {player_stats['currency']} gold.\n"
            for sql_itm in sql_shop_inventory:
                str_output = f"{str_output}" + \
                             f"{sql_itm[0]['shop_id']} " + \
                             f"{sql_itm[0]['equipment_colour']} " + \
                             f"{sql_itm[0]['equipment_name']} " + \
                             f"{sql_itm[0]['shop_cost']} gold\n"
            return str_output
        else:
            sql_shop_items = await utils.sql_postgres("SELECT adventurersinc.get_player_shop_all(%s, %s);", (params["nick"], params["cmd2"],), True)
            # Check is sql_shop_items returns None
            if not sql_shop_items:
                return "The shopkeep doesn't know what item you ask for."
            else:
                chosen_item = None
                for item in sql_shop_items:
                    if int(item[0]['shop_id']) == int(params['cmd2']):
                        chosen_item = item[0]

            # Check if chosen item cost can be purchased
            if player_stats['currency'] < chosen_item['shop_cost']:
                return "You cannot afford this item."

            # Proceed with purchase
            await Items.add_to_inventory(params, chosen_item)
            await utils.sql_postgres("CALL adventurersinc.del_player_shop_item(%s, %s);", (str(params["nick"]), params["cmd2"],), False)
            await utils.sql_postgres("CALL adventurersinc.set_player_gold(%s, %s);", (chosen_item['shop_cost'], params["nick"],), False)
            return f"The {chosen_item['equipment_colour']}{chosen_item['equipment_name']} has been added to your inventory."
    
    # Heal
    elif params["cmd1"].lower() == 'r' or params["cmd1"].lower() == 'rest':
        player_stats = await PlayerStats.refresh_stats(params)
        if player_stats['rested_heal'] == 0:
            if player_stats['hp'] >= player_stats['max_hp']:
                await utils.sql_postgres("CALL adventurersinc.set_player_health(%s, %s)", (player_stats['hp'], params["nick"],), False)
                return "You rest. You are already at max HP."

            # If heal is an over-heal, heal to max instead
            elif round(player_stats['max_hp']/2 + player_stats['hp']) > player_stats['max_hp']:
                int_hp_gained = player_stats['max_hp']
                await utils.sql_postgres("CALL adventurersinc.set_player_health(%s, %s)", (int_hp_gained, params["nick"],), False)
                return "You rest and your wounds heal completely."

            # Otherwise heal 50%
            elif player_stats['hp'] < player_stats['max_hp']:
                int_hp_gained = round(player_stats['max_hp']/2 + player_stats['hp'])
                await utils.sql_postgres("CALL adventurersinc.set_player_health(%s, %s)", (int_hp_gained, params["nick"],), False)
                return f"You rest and you recover {round(player_stats['max_hp']/2)}HP."

        else:
            return "You rest."
    
    # DEBUG - CREATE WEAPON
    elif params["cmd1"].lower() == '_viewitem':
        return await Items.generate_equipment(params, params["cmd2"])

    # DEBUG - TEST ITEM GEN WEAPON
    elif params["cmd1"].lower() == '_fabled':
        return await Items.item_test()
    
    # DEBUG - Resolve an itemcode
    elif params["cmd1"].lower() == '_mergeitemcodes':
        item_codes = params["cmd2"].split('_')
        return Items.MergeItemCodes(item_codes[0], item_codes[1])
    
    # Version
    elif params["cmd1"].lower() == 'v' or params["cmd1"].lower() == 'version':
        return "Version 1.3 - Notes can be found at: http://www.lexicade.uk/dev.php?view=patchnotes"
    
    # Admin commands
    elif params["cmd1"].lower() == 'genitem' and params["nick"] == 182588470135488512:
        await Items.add_to_inventory(params, await Items.generate_equipment(params, '0:0:0:0:1'))
    
    # Death
    elif params["cmd1"].lower() == 'suicide':
        CharacterDeath(player_stats, params)
        return "You committed suicide."
    
    else:
        return "Available commands: (i)nventory, (e)quip, (b)attle, (c)haracter, (s)hop, (r)est, (v)ersion, (d)estroy."
