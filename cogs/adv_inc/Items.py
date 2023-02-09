import pymysql
import random
import math
import importlib
import utils

import codecs
import unicodedata

importlib.reload(utils)


async def generate_equipment(params, item_code):
    # int_iteration = 0
    # item_name = str_rarity_spacing = ''
    item_code = item_code.split(':')

    # for i in range(len(item_code)):
    #     if str(i).isdigit():
    #         i = i
    #     else:
    #         i = random.choice(i.split(','))

    # Generate Rarity
    item_gen_rarity = await create_equipment_rarity(item_code[0])

    # Generate Item
    item_gen_equipment = await create_equipment_name(item_code[1])

    # Generate Enchantment (Uncommon or greater)
    item_gen_enchantment = await create_equipment_enchantment(item_code[2], item_gen_rarity['rarity_id'])

    # Generate Element (Rare or greater)
    item_gen_element = await create_equipment_element(item_code[3], item_gen_rarity['rarity_id'])

    # Attempt creating an Artifact
    item_gen_equipment = await create_equipment_artifact(params, item_code[4], item_gen_equipment)

    # print(type(item_gen_element), item_gen_equipment['permanent'], (("" if item_gen_equipment['permanent'] == 0 else "Fabled ") +
    #                                f"{item_gen_rarity['rarity_name']}" +
    #                                ("" if len(item_gen_rarity['rarity_name']) == 0 else " ") +
    #                                ("" if item_gen_element is None else item_gen_element['element_name'] + " ") +
    #                                f"{item_gen_equipment['equipment_name']} " +
    #                                ("" if item_gen_enchantment is None else item_gen_enchantment['enchant_name'])).strip())

    item_gen = {'equipment_colour': item_gen_rarity['rarity_colour'],
                'equipment_name': (("" if item_gen_equipment['permanent'] == 0 else "Fabled ") +
                                   f"{item_gen_rarity['rarity_name']}" +
                                   ("" if len(item_gen_rarity['rarity_name']) == 0 else " ") +
                                   ("" if item_gen_element is None else item_gen_element['element_name'] + " ") +
                                   f"{item_gen_equipment['equipment_name']} " +
                                   ("" if item_gen_enchantment is None else item_gen_enchantment['enchant_name'])).strip(),
                'equipment_slot': item_gen_equipment['equipment_slot'],
                'equipment_type': item_gen_equipment['equipment_type'],
                'hands_req': item_gen_equipment['hands_req'],
                'strength': math.floor((item_gen_equipment['strength'] + (0 if item_gen_enchantment is None else item_gen_enchantment['strength']) +
                                                                         (0 if item_gen_element is None else item_gen_element['strength'])) * item_gen_rarity['rarity_modifier']),
                'dexterity': math.floor((item_gen_equipment['dexterity'] + (0 if item_gen_enchantment is None else item_gen_enchantment['dexterity']) +
                                                                           (0 if item_gen_element is None else item_gen_element['dexterity'])) * item_gen_rarity['rarity_modifier']),
                'constitution': math.floor((item_gen_equipment['constitution'] + (0 if item_gen_enchantment is None else item_gen_enchantment['constitution']) +
                                                                                 (0 if item_gen_element is None else item_gen_element['constitution'])) * item_gen_rarity['rarity_modifier']),
                'intelligence': math.floor((item_gen_equipment['intelligence'] + (0 if item_gen_enchantment is None else item_gen_enchantment['intelligence']) +
                                                                                 (0 if item_gen_element is None else item_gen_element['intelligence'])) * item_gen_rarity['rarity_modifier']),
                'dodge': math.floor((item_gen_equipment['dodge'] + (0 if item_gen_enchantment is None else item_gen_enchantment['dodge']) +
                                                                   (0 if item_gen_element is None else item_gen_element['dodge'])) * item_gen_rarity['rarity_modifier']),
                'crit': math.floor((item_gen_equipment['crit'] + (0 if item_gen_enchantment is None else item_gen_enchantment['crit']) +
                                                                 (0 if item_gen_element is None else item_gen_element['crit'])) * item_gen_rarity['rarity_modifier']),
                'armour': math.floor((item_gen_equipment['armour'] + (0 if item_gen_enchantment is None else item_gen_enchantment['armour']) +
                                                                     (0 if item_gen_element is None else item_gen_element['armour'])) * item_gen_rarity['rarity_modifier']),
                'accuracy': math.floor((item_gen_equipment['accuracy'] + (0 if item_gen_enchantment is None else item_gen_enchantment['accuracy']) +
                                                                         (0 if item_gen_element is None else item_gen_element['accuracy'])) * item_gen_rarity['rarity_modifier']),
                'resistance': math.floor((item_gen_equipment['resistance'] + (0 if item_gen_enchantment is None else item_gen_enchantment['resistance']) +
                                                                             (0 if item_gen_element is None else item_gen_element['resistance'])) * item_gen_rarity['rarity_modifier']),
                'luck': math.floor((item_gen_equipment['luck'] + (0 if item_gen_enchantment is None else item_gen_enchantment['luck']) +
                                                                 (0 if item_gen_element is None else item_gen_element['luck'])) * item_gen_rarity['rarity_modifier']),
                'block': math.floor((item_gen_equipment['block'] + (0 if item_gen_enchantment is None else item_gen_enchantment['block']) +
                                                                   (0 if item_gen_element is None else item_gen_element['block'])) * item_gen_rarity['rarity_modifier']),
                'permanent': item_gen_equipment['permanent'],
                'cost': math.floor(item_gen_equipment['item_cost'] + (0 if item_gen_element is None else item_gen_element['element_cost']) +
                                                                         (0 if item_gen_enchantment is None else item_gen_enchantment['enchant_cost']) +
                                                                         (0 if item_gen_rarity is None else item_gen_rarity['rarity_cost']))}

    return item_gen


async def create_equipment_name(item_code):
    # If item_code is specified, find the base item and return.
    if int(item_code) != 0:
        base_item = await utils.sql_postgres("SELECT AdventurersInc.get_item_equipment(%s)", (item_code,), True)

    # If item_code is 0, roll the standard random generation
    else:
        base_item = await utils.sql_postgres("SELECT AdventurersInc.get_item_equipment(%s)", ('%',), True)

    return base_item[0][0]


async def create_equipment_element(item_code, rarity_id):
    # Get a random element from the given item_code
    if int(item_code) != 0:
        element = await utils.sql_postgres("SELECT AdventurersInc.get_item_elements(%s)", (item_code,), True)
        return element[0][0]

    # Roll for a random enchant for any item Rare or greater
    else:
        if rarity_id >= 4 and random.randint(1, 3) == 1:
            element = await utils.sql_postgres("SELECT AdventurersInc.get_item_elements(%s)", ('%',), True)
            return element[0][0]


async def create_equipment_rarity(item_code):
    # If item_code is specified, find the rarity and return.
    if int(item_code) != 0:
        # item_code = 1 if item_code <= 0 or item_code >= 7 else item_code
        rarity = await utils.sql_postgres("SELECT AdventurersInc.get_item_rarities(%s)", (item_code,), True)
        return rarity[0][0]

    # If item_code is 0, roll the standard random generation
    elif int(item_code) == 0:
        # Get all rarities
        base_rarities = await utils.sql_postgres("SELECT AdventurersInc.get_item_rarities(%s)", ('%',), True)

        # Get the dice roll for this random generation cycle
        rarity_dice_roll = random.randint(1, base_rarities[0][0]["total_weight"])

        # Determine the rarity
        for rarity in base_rarities:
            rarity_dice_roll = rarity_dice_roll - rarity[0]["rarity_weight"]
            if rarity_dice_roll <= 0:
                return rarity[0]


async def create_equipment_enchantment(item_code, rarity_id):
    # Get a random enchant from the given item_code
    if int(item_code) != 0:
        enchant = await utils.sql_postgres("SELECT adventurersinc.get_item_enchantment(%s)", (item_code,), True)
        return enchant[0][0]

    # Roll for a random enchant for any item Uncommon or greater
    else:
        if rarity_id >= 3 and random.randint(1, 3) == 1:
            enchant = await utils.sql_postgres("SELECT adventurersinc.get_item_enchantment(%s)", ('%',), True)
            return enchant[0][0]


async def create_equipment_artifact(params, item_code, item_gen_equipment):
    # Gen for Artifact item:
    player_fabled = await utils.sql_postgres("SELECT adventurersinc.get_player_artifact_count(%s);", (params['nick'],), True)

    # 0 - Will attempt to add an artifact randomly and not exceed the standard limit
    if player_fabled[0][0]['perm_can_drop']:
        if random.randint(1, 100) == 1 and int(item_code) == 0:
            item_gen_equipment['permanent'] = 1

        # 1 - Will not generate item as an artifact
        elif int(item_code) == 1:
            item_gen_equipment['permanent'] = 0

        else:
            item_gen_equipment['permanent'] = 0

        # 2 - Will force the item to become an artifact and exceed the limit of 2 artifacts
    elif int(item_code) == 2:
        item_gen_equipment['permanent'] = 1

    return item_gen_equipment


# def create_item(enemy_stats, player_stats, params):
#     # Get random element
#     c.execute("SELECT loot_name,ItemType,Potency FROM GenLoot WHERE Locked=0 ORDER BY RAND() LIMIT 1")
#     sql_rarity = c.fetchone()
#     str_loot_name = sql_rarity['loot_name']
#     str_item_type = sql_rarity['ItemType']
#     int_potency = sql_rarity['Potency']
#
#     if str_item_type == 'Quantity':
#         int_potency = enemy_stats['GoldCarried'] + int(random.uniform(float(enemy_stats['GoldCarried']) * -0.3, float(enemy_stats['GoldCarried']) * 0.3))
#
#     return str_loot_name, int_potency


async def add_to_shop(params, item):
    sql = 'CALL adventurersinc.add_to_player_shop(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    params = (params['nick'], item['cost'], item['equipment_colour'], item['equipment_name'], item['equipment_slot'],
              item['equipment_type'], bool(item['permanent']), item['hands_req'], item['strength'], item['dexterity'],
              item['constitution'], item['intelligence'], item['dodge'], item['crit'], item['armour'],
              item['accuracy'], item['resistance'], item['luck'], item['block'],)
    await utils.sql_postgres(sql, params, False)
    return


async def add_to_inventory(params, item):
    sql = 'CALL adventurersinc.add_to_player_inventory(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    params = (item['equipment_colour'], item['equipment_name'], item['equipment_slot'], item['equipment_type'], bool(item['permanent']), item['hands_req'],
              item['strength'], item['dexterity'], item['constitution'], item['intelligence'], item['dodge'], item['crit'],
              item['armour'], item['accuracy'], item['resistance'], item['luck'], item['block'], params['nick'])
    await utils.sql_postgres(sql, params, False)
    return


def merge_item_codes(item_code1, item_code2):
    str_output = ""
    item_code1 = item_code1.split(':')
    item_code2 = item_code2.split(':')

    for i in range(len(item_code1)):
        if str(item_code1[i]) == "0" or str(item_code2[i]) == "0":
            str_output = str_output + str(int(item_code1[i]) + int(item_code2[i]))
        else:
            str_output = str_output + random.choice([item_code1[i], item_code2[i]])

    return str_output


# def unlock_items(params, unlocked_set):
#     c_select.execute("SELECT equipment_name, equipment_slot, equipment_type, hands_req, Locked, strength, dexterity, constitution, intelligence, dodge, crit, armour, Requirement FROM base_items WHERE Requirement=%s", (unlocked_set,))
#     while sql_item is not None:
#         c_insert.execute("INSERT INTO Items_PlayerPool(equipment_name,Nick) VALUES (%s,%s)",(sql_item['equipment_name'], params['Nick'],));db.commit();
#     return "Updated."


async def item_test():
    params = {'nick': 182588470135488512}
    item_code = '0:0:0:0:0'
    max_loops = 100
    totals = {'Ruined': 0, 'Normal': 0, 'Uncommon': 0, 'Rare': 0, 'Epic': 0, 'Legendary': 0 }
    for loop in range(1, max_loops):
        item = await generate_equipment(params, item_code)
        if item['permanent'] == 1:
            if item['equipment_colour'] == '⚫':
                rarity = 'Ruined'
            elif item['equipment_colour'] == '⚪':
                rarity = 'Normal'
            elif item['equipment_colour'] == '🟢':
                rarity = 'Uncommon'
            elif item['equipment_colour'] == '🔵':
                rarity = 'Rare'
            elif item['equipment_colour'] == '🟣':
                rarity = 'Epic'
            elif item['equipment_colour'] == '🟠':
                rarity = 'Legendary'

            totals[rarity] = totals[rarity] + 1
    return totals
