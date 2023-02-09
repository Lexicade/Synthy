import asyncio
from datetime import timedelta

import psycopg2
import time
from ffxiv.ffxiv_core import FFXIVCharacter

character = FFXIVCharacter(character_id=16948279)  # Hoptimus
# character = FFXIVCharacter(character_id=31356200)  # Leonieros
# character = FFXIVCharacter(character_id=24587891)  # Lille
# character = FFXIVCharacter(character_id=36388961)  # Cleftin
# character = FFXIVCharacter(character_id=42094919)  # Bekuh (Maddie)

asyncio.run(character.obtain_character_data())
# asyncio.run(character.build_character_view())
asyncio.run(character.build_character_portrait())

# epoch = 1654714864
# delta = timedelta(hours=23).seconds
# ctime = int(time.time())
# print((ctime - epoch) > delta)
# print(f"epoch: {epoch}")
# print(f"delta: {delta}")
# print(f"ctime: {ctime}")
# print(f"ctime - epoch: {(ctime - epoch)}")
# print(f"ctime - epoch: {(ctime - epoch) > delta}")
