import math
import random


async def get_dodge_chance(dexterity, dodge, coefficient=110):
    system_percentage = (dodge + (dexterity / 3)) / ((dodge+(dexterity / 3)) + coefficient)
    return system_percentage


async def get_block_chance(strength, block, coefficient=30):
    strength_bonus = 0 if strength < 17 else math.floor((strength-17) / 3)
    system_percentage = (block + (strength_bonus / 3)) / ((block + (strength_bonus / 3)) + coefficient)
    return system_percentage


async def get_luck_chance(luck, coefficient=50):
    luck_rolls = round((luck / (luck + coefficient)) * 15, 0)
    return int(luck_rolls)


async def get_attack_power(strength, dexterity):
    str_bonus = strength * 1
    dex_bonus = math.floor(dexterity / 2)
    attack_power = random.uniform((str_bonus + dex_bonus) * 1.1, (str_bonus + dex_bonus) * 0.9)
    return math.floor(attack_power)


async def get_hit_chance(dexterity, accuracy, coefficient=50):
    system_percentage = (accuracy + (dexterity / 3)) / ((accuracy + (dexterity / 3)) + coefficient)
    return system_percentage


async def get_max_life(strength, constitution):
    str_bonus = math.floor(strength / 3)
    con_bonus = constitution * 2
    max_life = con_bonus + str_bonus
    return math.floor(max_life)


async def get_armour_percentage(armour, strength, constitution, coefficient=80):
    strength_bonus = 0 if strength < 20 else math.floor((strength-16) / 4)
    constitution_bonus = 0 if constitution < 20 else math.floor((constitution-16) / 4)
    armour_bonus = armour * 3
    armour_perc = (strength_bonus + constitution_bonus + armour_bonus / 3) / ((strength_bonus + constitution_bonus + armour_bonus / 3) + coefficient)
    return round(armour_perc, 2)


async def get_crit_percentage(dexterity, critical, coefficient=100):
    critical = critical * 2
    dexterity_bonus = math.floor(dexterity / 3)
    critical_chance = (critical + dexterity_bonus / 3) / ((critical + dexterity_bonus / 3) + coefficient)
    return round(critical_chance, 2)
