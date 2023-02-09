import json
import os
import time
from datetime import datetime, timedelta

import psycopg2
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import csv
import requests
from pathlib import Path

from psycopg2.extras import RealDictRow
# from ratelimit import sleep_and_retry, limits

from ffxiv.pystone.definition import Definition


class ScrapeLodestone:
    def __init__(self, character_id):
        self.character_id = character_id

    @staticmethod
    def scrape_data(filename, player_id):
        # argv1 = 'lodestone-css-selectors-0.46.0'
        argv1 = 'lodestone-css-selectors-0.52.0'
        region = 'eu'

        definition_file = f'profile/{filename}.json'
        base = Path(argv1)
        path = base / definition_file

        with open(os.path.dirname(__file__) / base / 'meta.json') as f:
            meta = json.loads(f.read())

        definition = Definition(
            os.path.dirname(__file__) / path,
            meta['applicableUris'][definition_file]
        )

        definition.process((region, player_id))
        # character_definition.process({'region': region, 'id': player_id})
        return definition.to_json()

    def character(self):
        char = self.scrape_data('character', self.character_id)
        char['character']['classjobs'] = self.scrape_data('classjob', self.character_id)
        char['character']['gender'] = 'm' if char['character']['gender'] == '♂' else 'f'
        return char


class FFXIVCharacter:
    def __init__(self, character_id):
        self.character_id = character_id
        self.name = None
        self.gender = None
        self.title = None
        self.race = None
        self.free_company = None
        self.clan = None
        self.race_clan_gender = None
        self.portrait = None
        self.server = None
        self.image = None
        self.grand_company = None
        self.title_is_prefix = None
        self.get_grand_company()

        self.combat_levels_earned = 0
        self.combat_levels_max = 0
        self.crafter_levels_earned = 0
        self.crafter_levels_max = 0

        self.db_con = psycopg2.connect(database=os.environ.get('db_name'),
                                       user=os.environ.get('db_user'),
                                       password=os.environ.get('db_pass'),
                                       host=os.environ.get('db_host'),
                                       port=os.environ.get('db_port'))
        self.db_cur = self.db_con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

        self.paladin = None
        self.warrior = None
        self.darkknight = None
        self.gunbreaker = None
        self.whitemage = None
        self.scholar = None
        self.astrologian = None
        self.sage = None
        self.monk = None
        self.dragoon = None
        self.ninja = None
        self.samurai = None
        self.reaper = None
        self.bard = None
        self.machinist = None
        self.dancer = None
        self.blackmage = None
        self.summoner = None
        self.redmage = None
        self.bluemage = None
        self.carpenter = None
        self.blacksmith = None
        self.armorer = None
        self.goldsmith = None
        self.leatherworker = None
        self.weaver = None
        self.alchemist = None
        self.culinarian = None
        self.miner = None
        self.botanist = None
        self.fisher = None
        self.achievements = None
        self.mounts_max = 219
        self.mounts_owned = None
        self.minion_max = 442
        self.minion_owned = None

        self.font_job_level = ImageFont.truetype("./fonts/steelfish/steelfish bd.ttf", 33)
        self.font_job_name = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 16)
        self.font_job_experience = ImageFont.truetype("./fonts/calibri/calibri.ttf", 35)

        self.font_character_name = ImageFont.truetype("./fonts/calibri/calibri.ttf", 35)
        self.font_character_title_name = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 22)

        self.font_character_label = ImageFont.truetype("./fonts/calibri/calibrib.ttf", 15)
        self.font_character_value = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 16)

        self.font_footer_label = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 13)
        self.font_footer_value = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 12)

        self.font_colour_maxed = (240, 142, 55, 255)
        self.font_colour_job_specialist = (170, 128, 255, 255)
        self.font_colour_standard = (204, 204, 204, 255)
        self.font_colour_darkgrey = (90, 90, 90, 255)
        self.font_colour_lightblue = (170, 253, 255, 255)
        self.font_colour_text_title = (202, 175, 117, 255)
        self.font_colour_text_label = (160, 160, 160, 255)
        self.font_colour_text_value = (238, 225, 197, 255)

    async def build_character_view(self):
        # response_image = requests.get(self.portrait)
        self.base_image()
        self.image_header()
        self.image_information()
        self.image_classjobs()
        self.image_footer()

        self.image.save('character.png')

    async def build_character_portrait(self):
        # response_image = requests.get(self.portrait)
        self.base_image_portrait()
        self.image_header_portrait()
        # self.image_information()
        # self.image_classjobs()
        # self.image_footer()

        self.image.save('character_portrait.png')

    def base_image(self):
        """Generates the base image, with character portait."""
        self.image = Image.new('RGBA', (1050, 873), color='#000000')
        img_tile = Image.open("./ffxiv/bg-tile.png")
        img_tile_x, img_tile_y = img_tile.size

        cur_x, cur_y = 0, 0
        img_x, img_y = self.image.size
        while cur_x < img_x and cur_y < img_y:
            self.image.paste(img_tile, (cur_x, cur_y))

            cur_x += img_tile_x
            if cur_x > img_x and cur_y > img_y:
                break

            elif cur_x > img_x:
                cur_x = 0
                cur_y += img_tile_y

        # Place portrait onto character view
        response_image = requests.get(self.portrait)
        img_portait = Image.open(BytesIO(response_image.content))
        self.image.paste(img_portait)

        # Place frame over image
        img_frame = Image.open(f'./ffxiv/character-frame.png')
        self.image.paste(img_frame, mask=img_frame)

        self.add_corners(self.image, 24)

    def base_image_portrait(self):
        """Generates the base image, with character portait."""
        self.image = Image.new('RGBA', (646, 873), color='#000000')
        img_tile = Image.open("./ffxiv/bg-tile.png")
        img_tile_x, img_tile_y = img_tile.size

        cur_x, cur_y = 0, 0
        img_x, img_y = self.image.size
        while cur_x < img_x and cur_y < img_y:
            self.image.paste(img_tile, (cur_x, cur_y))

            cur_x += img_tile_x
            if cur_x > img_x and cur_y > img_y:
                break

            elif cur_x > img_x:
                cur_x = 0
                cur_y += img_tile_y

        # Place portrait onto character view
        response_image = requests.get(self.portrait)
        img_portait = Image.open(BytesIO(response_image.content))
        self.image.paste(img_portait)

        # Place frame over image
        img_frame = Image.open(f'./ffxiv/character-frame-portrait.png')
        self.image.paste(img_frame, mask=img_frame)

        self.add_corners(self.image, 24)

    @staticmethod
    def add_corners(im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im

    def image_header(self):
        """Add character name, title and server"""
        d = ImageDraw.Draw(self.image)

        name_w, name_h = d.textsize(self.name, font=self.font_character_name)
        title_w, title_h = d.textsize(self.title, font=self.font_character_title_name)
        realm_w, realm_h = d.textsize(self.server, font=self.font_character_value)

        # Determine title/name heights
        if self.title_is_prefix:
            char_name_offset = 23
            title_name_offset = 0
        else:
            char_name_offset = 0
            title_name_offset = 29

        x_offset = 0
        # Add text
        d.text((645 + x_offset + (376-name_w)/2, 10 + char_name_offset), self.name, font=self.font_character_name, fill=self.font_colour_text_value)
        d.text((645 + x_offset + (376-title_w)/2, 10 + title_name_offset), self.title, font=self.font_character_title_name, fill=self.font_colour_text_title)
        d.text((645 + x_offset + (376-realm_w)/2, 65), self.server, font=self.font_character_value, fill=self.font_colour_text_label)
    def image_header_portrait(self):
        """Add character name, title and server"""
        d = ImageDraw.Draw(self.image)

        # Determine title/name heights
        if self.title_is_prefix:
            char_name_offset = 23
            title_name_offset = 0
        else:
            char_name_offset = 0
            title_name_offset = 29

        x_offset = 0
        # Add text
        d.text((20, 10 + char_name_offset), self.name, font=self.font_character_name, fill=self.font_colour_text_value)
        d.text((20, 10 + title_name_offset), self.title, font=self.font_character_title_name, fill=self.font_colour_text_title)
        d.text((20, 65), self.server, font=self.font_character_value, fill=self.font_colour_text_label)

    def image_information(self):
        """Adds characters information to image"""
        x_offset = 19
        label_offset_y = 95

        # grand_company_rank = ""

        ffxiv_races = ["Hyur", "Elezen", "Lalafell", "Miqo'te", "Roegadyn", "Au Ra", "Viera", "Hrothgar"]
        for ffxiv_race in ffxiv_races:
            if ffxiv_race in self.race_clan_gender:
                self.race = ffxiv_race
                self.clan = self.race_clan_gender.split(ffxiv_race)[1]

        d = ImageDraw.Draw(self.image)

        d.text((650 + x_offset, 0 + label_offset_y), "Race", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((660 + x_offset, 15 + label_offset_y), f"{self.race}, {self.clan}", font=self.font_character_value, fill=self.font_colour_text_value)

        d.text((650 + x_offset, 50 + label_offset_y), "Free Company", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((660 + x_offset, 65 + label_offset_y), self.free_company, font=self.font_character_value, fill=self.font_colour_text_value)

        d.text((650 + x_offset, 100 + label_offset_y), "Grand Company", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((660 + x_offset, 115 + label_offset_y), self.grand_company, font=self.font_character_value, fill=self.font_colour_text_value)
        # d.text((660 + x_offset, 135 + label_offset_y), self.grand_company, font=font_character_value, fill=font_colour_text_value)+

        label_offset_x_col_r = -20
        d.text((890 + x_offset + label_offset_x_col_r, 0 + label_offset_y), "Mounts", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((900 + x_offset + label_offset_x_col_r, 15 + label_offset_y), f"{self.mounts_owned} / {self.mounts_max}", font=self.font_character_value, fill=self.font_colour_text_value)

        d.text((890 + x_offset + label_offset_x_col_r, 50 + label_offset_y), "Minions", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((900 + x_offset + label_offset_x_col_r, 65 + label_offset_y), f"{self.minion_owned} / {self.minion_max}", font=self.font_character_value, fill=self.font_colour_text_value)

        d.text((890 + x_offset + label_offset_x_col_r, 100 + label_offset_y), "Achievement Points", font=self.font_character_label, fill=self.font_colour_text_label)
        d.text((900 + x_offset + label_offset_x_col_r, 115 + label_offset_y), self.achievements, font=self.font_character_value, fill=self.font_colour_text_value)

    def image_classjobs(self):
        """Adds character class/jobs to image"""
        # Buddy up the jobs into groups for image modularity
        tank_jobs = [self.paladin, self.warrior, self.darkknight, self.gunbreaker]
        healer_jobs = [self.whitemage, self.scholar, self.astrologian, self.sage]
        dps_jobs = [self.monk, self.dragoon, self.ninja, self.samurai, self.reaper]
        rdps_jobs = [self.bard, self.machinist, self.dancer]
        mdps_jobs = [self.blackmage, self.summoner, self.redmage, self.bluemage]
        hand_jobs = [self.carpenter, self.blacksmith, self.armorer, self.goldsmith, self.leatherworker, self.weaver, self.alchemist, self.culinarian]
        land_jobs = [self.miner, self.botanist, self.fisher]
        # extra_jobs = [self.eureka, self.bozja]

        self.assemble_jobs(tank_jobs, 668, 250, True)
        self.assemble_jobs(healer_jobs, 668, 400, True)

        self.assemble_jobs(dps_jobs, 860, 250, True)
        self.assemble_jobs(rdps_jobs, 860, 433, True)
        self.assemble_jobs(mdps_jobs, 860, 550, True)

        self.assemble_jobs(land_jobs, 860, 715, False)
        self.assemble_jobs(hand_jobs, 668, 550, False)

    def image_footer(self):
        """Adds footer level totals to image"""
        x_offset = 0
        x_pos = 710
        ldata = [{"label": "DoW/DoM", "value": f"{self.combat_levels_earned}/{self.combat_levels_max} - {round((self.combat_levels_earned*100)/self.combat_levels_max, 2)}%"},
                 {"label": "DoL/DoH", "value": f"{self.crafter_levels_earned}/{self.crafter_levels_max} - {round((self.crafter_levels_earned*100)/self.crafter_levels_max, 2)}%"},
                 {"label": "Total", "value": f"{self.combat_levels_earned+self.crafter_levels_earned}/{self.combat_levels_max+self.crafter_levels_max} - {round(((self.combat_levels_earned+self.crafter_levels_earned)*100)/(self.combat_levels_max+self.crafter_levels_max), 2)}%"}]

        for l in ldata:
            label_w, label_h = self.draw.textsize(l['label'], font=self.font_footer_label)
            value_w, value_h = self.draw.textsize(l['value'], font=self.font_footer_value)

            # if "100.0%" in l['value']:
            #     font_colour = self.font_colour_maxed
            # else:
            #     font_colour = self.font_colour_standard

            self.draw.text((x_pos + x_offset + (0-label_w)/2, 836), l['label'], font=self.font_footer_label, fill=self.font_colour_text_label)
            self.draw.text((x_pos + x_offset + (0-value_w)/2, 850), l['value'], font=self.font_footer_value, fill=self.font_colour_standard)
            x_offset += 130

    def assemble_jobs(self, jobs: list, increment_x=0, increment_y=0, is_combat=True):
        # total_level_max = 0
        for job in jobs:
            # print(f"working on {job}")
            if job['unlockstate'] in ['bozja', 'eureka']:
                continue

            # Get job image
            job_icon = Image.open(f'./ffxiv/jobs/{job["unlockstate"].replace(" ", "").lower()}.png',)
            job_icon = job_icon.resize((30, 30))

            # Job XP
            job_xp = 0 if job["exp"] in ['-', '--'] else ((int(job["exp"].replace(",", "")) * 100) / int(job["exp_max"].replace(",", ""))) / 100
            # job['level'] = "0" if job["level"] == '-' else job['level']

            # Determine levels at max, and acquire total levels data
            if is_combat:
                self.combat_levels_max += int(job['max_level'])
                if job["level"] in ['-', '--']:
                    level_maxed = False
                elif str(job['level']).isnumeric() and int(job['level']) == job['max_level']:
                    self.combat_levels_earned += int(job['max_level'])
                    level_maxed = True
                else:
                    self.combat_levels_earned += int(job['level'])
                    level_maxed = False

            elif not is_combat:
                self.crafter_levels_max += int(job['max_level'])
                if job["level"] in ['-', '--']:
                    level_maxed = False
                elif int(job['level']) == job['max_level']:
                    self.crafter_levels_earned += int(job['max_level'])
                    level_maxed = True
                else:
                    self.crafter_levels_earned += int(job['level'])
                    level_maxed = False

            if 'specialist' in job and job['specialist']:
                job_colour = self.font_colour_job_specialist
            else:
                job_colour = self.font_colour_standard

            self.draw = ImageDraw.Draw(self.image)

            job_level_w, job_level_h = self.draw.textsize(job["level"], font=self.font_job_level)

            # Job Icon
            self.image.paste(job_icon, (increment_x, increment_y), mask=job_icon)
            # Job Level
            self.draw.text((increment_x + 42 - (job_level_w/2), increment_y - 7), job["level"], font=self.font_job_level, fill=self.font_colour_maxed if level_maxed else self.font_colour_standard)
            # Job Name
            self.draw.text((increment_x + 55, increment_y - 1), job['unlockstate'], font=self.font_job_name, fill=job_colour)
            # Job XP Meter
            self.draw_progress_bar(self.draw, increment_x + 53, increment_y + 20, w=110, h=5, progress=job_xp)
            increment_y += 33

    def draw_progress_bar(self, draw, x, y, w: int, h: int, progress):
        # draw background bar and progress bar
        draw.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=self.font_colour_darkgrey)
        if progress > 0:
            w *= progress
            draw.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=self.font_colour_standard)
        return draw

    def get_title(self):
        with open("./ffxiv/data/titles.csv", "r") as file:
            data = csv.reader(file, delimiter=',', quotechar='"')
            for title in data:
                if title[1] == self.title:
                    self.title_is_prefix = True if title[3] == "True" else False
                    if self.gender == 'm':
                        self.title = title[1]

                    elif self.gender == 'f':
                        self.title = title[2]
                    return
            return

    def get_grand_company(self):
        with open("./ffxiv/data/grandcompanies.csv", "r") as file:
            data = csv.reader(file, delimiter=',', quotechar='"')
            for row in data:
                if self.grand_company in ['Maelstrom', 'Adder', 'Flames'] and self.grand_company in row[1]:
                    self.grand_company = row[1]
                    return

    async def obtain_character_data(self):
        cur = self.db_con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        cur.execute('SELECT * FROM database1.synthy.ffxiv WHERE id = %s', (self.character_id,))
        character = cur.fetchone()

        if character.character_data is None or (character.character_epoch is not None and (int(time.time()) - character.character_epoch) > timedelta(hours=2).seconds):
            await self.update_character_data()
        if character.classjob_data is None or (character.classjob_epoch is not None and (int(time.time()) - character.classjob_epoch) > timedelta(hours=2).seconds):
            await self.update_classjob_data()
        if character.minion_data is None or (character.minion_epoch is not None and (int(time.time()) - character.minion_epoch) > timedelta(hours=23).seconds):
            await self.update_minion_data()
        if character.mount_data is None or (character.mount_epoch is not None and (int(time.time()) - character.mount_epoch) > timedelta(hours=23).seconds):
            await self.update_mount_data()
        if character.achievement_data is None or (character.achievement_epoch is not None and (int(time.time()) - character.achievement_epoch) > timedelta(hours=23).seconds):
            await self.update_achievement_data()

        await self.read_character_data()
        await self.read_classjob_data()
        await self.read_minion_data()
        await self.read_mount_data()
        await self.read_achievement_data()

    async def update_character_data(self):
        data_scraped = ScrapeLodestone.scrape_data('character', self.character_id)
        self.db_cur.execute('UPDATE "database1".synthy.ffxiv SET character_data = %s, character_epoch = %s WHERE id = %s', (json.dumps(data_scraped['character']), int(time.time()), self.character_id,))
        self.db_con.commit()

    async def update_classjob_data(self):
        data_scraped = ScrapeLodestone.scrape_data('classjob', self.character_id)
        self.db_cur.execute('UPDATE "database1".synthy.ffxiv SET classjob_data = %s, classjob_epoch = %s WHERE id = %s', (json.dumps(data_scraped), int(time.time()), self.character_id,))
        self.db_con.commit()

    async def update_minion_data(self):
        data_scraped = ScrapeLodestone.scrape_data('minion', self.character_id)
        self.db_cur.execute('UPDATE "database1".synthy.ffxiv SET minion_data = %s, minion_epoch = %s WHERE id = %s', (json.dumps(data_scraped['minion']), int(time.time()), self.character_id,))
        self.db_con.commit()

    async def update_mount_data(self):
        try:
            data_scraped = ScrapeLodestone.scrape_data('mount', self.character_id)
            data = json.dumps(data_scraped['mount'])
        except:
            data = json.dumps({"total": "Not Unlocked"})
        self.db_cur.execute('UPDATE "database1".synthy.ffxiv SET mount_data = %s, mount_epoch = %s WHERE id = %s', (data, int(time.time()), self.character_id,))
        self.db_con.commit()

    async def update_achievement_data(self):
        try:
            data_scraped = ScrapeLodestone.scrape_data('achievements', self.character_id)
            data = json.dumps(data_scraped['achievements'])
        except:
            data = json.dumps({"total_achievements": "Private", "achievement_points": "Private"})
        self.db_cur.execute('UPDATE "database1".synthy.ffxiv SET achievement_data = %s, achievement_epoch = %s WHERE id = %s', (data, int(time.time()), self.character_id,))
        self.db_con.commit()

    async def update_data_titles(self):
        d = requests.get('https://raw.githubusercontent.com/xivapi/ffxiv-datamining/master/csv/Title.csv')
        d = d.content.decode()
        with open("./ffxiv/data/titles.csv", "w") as file:
            file.write(d)

    async def read_character_data(self):
        self.db_cur.execute('SELECT character_data from "database1".synthy.ffxiv WHERE id = %s', (self.character_id,))
        data = json.loads(self.db_cur.fetchone()[0])
        self.name = data['name']
        self.gender = 'm' if data['gender'] == '♂' else 'f'
        self.title = data['title']
        self.free_company = "N/A" if data['free_company']['free_company']['name'] == '' else data['free_company']['free_company']['name']
        self.race_clan_gender = data['race_clan_gender']
        self.server = data['server']
        self.grand_company = data['grand_company']
        self.portrait = data['portrait']

        self.get_title()
        self.get_grand_company()

    async def read_classjob_data(self):
        self.db_cur.execute('SELECT classjob_data from "database1".synthy.ffxiv WHERE id = %s', (self.character_id,))
        data = json.loads(self.db_cur.fetchone()[0])

        self.paladin = {**data['classjob']['paladin']['paladin'], **{'max_level': 90}}
        self.warrior = {**data['classjob']['warrior']['warrior'], **{'max_level': 90}}
        self.darkknight = {**data['classjob']['darkknight']['darkknight'], **{'max_level': 90}}
        self.gunbreaker = {**data['classjob']['gunbreaker']['gunbreaker'], **{'max_level': 90}}
        self.whitemage = {**data['classjob']['whitemage']['whitemage'], **{'max_level': 90}}
        self.scholar = {**data['classjob']['scholar']['scholar'], **{'max_level': 90}}
        self.astrologian = {**data['classjob']['astrologian']['astrologian'], **{'max_level': 90}}
        self.sage = {**data['classjob']['sage']['sage'], **{'max_level': 90}}
        self.monk = {**data['classjob']['monk']['monk'], **{'max_level': 90}}
        self.dragoon = {**data['classjob']['dragoon']['dragoon'], **{'max_level': 90}}
        self.ninja = {**data['classjob']['ninja']['ninja'], **{'max_level': 90}}
        self.samurai = {**data['classjob']['samurai']['samurai'], **{'max_level': 90}}
        self.reaper = {**data['classjob']['reaper']['reaper'], **{'max_level': 90}}
        self.bard = {**data['classjob']['bard']['bard'], **{'max_level': 90}}
        self.machinist = {**data['classjob']['machinist']['machinist'], **{'max_level': 90}}
        self.dancer = {**data['classjob']['dancer']['dancer'], **{'max_level': 90}}
        self.blackmage = {**data['classjob']['blackmage']['blackmage'], **{'max_level': 90}}
        self.summoner = {**data['classjob']['summoner']['summoner'], **{'max_level': 90}}
        self.redmage = {**data['classjob']['redmage']['redmage'], **{'max_level': 90}}
        self.bluemage = {**data['classjob']['bluemage']['bluemage'], **{'max_level': 70}}
        self.carpenter = {**data['classjob']['carpenter']['carpenter'], **{'max_level': 90}}
        self.blacksmith = {**data['classjob']['blacksmith']['blacksmith'], **{'max_level': 90}}
        self.armorer = {**data['classjob']['armorer']['armorer'], **{'max_level': 90}}
        self.goldsmith = {**data['classjob']['goldsmith']['goldsmith'], **{'max_level': 90}}
        self.leatherworker = {**data['classjob']['leatherworker']['leatherworker'], **{'max_level': 90}}
        self.weaver = {**data['classjob']['weaver']['weaver'], **{'max_level': 90}}
        self.alchemist = {**data['classjob']['alchemist']['alchemist'], **{'max_level': 90}}
        self.culinarian = {**data['classjob']['culinarian']['culinarian'], **{'max_level': 90}}
        self.miner = {**data['classjob']['miner']['miner'], **{'max_level': 90}}
        self.botanist = {**data['classjob']['botanist']['botanist'], **{'max_level': 90}}
        self.fisher = {**data['classjob']['fisher']['fisher'], **{'max_level': 90}}

    async def read_minion_data(self):
        self.db_cur.execute('SELECT minion_data from "database1".synthy.ffxiv WHERE id = %s', (self.character_id,))
        data = json.loads(self.db_cur.fetchone()[0])
        self.minion_owned = data['total']

    async def read_mount_data(self):
        self.db_cur.execute('SELECT mount_data from "database1".synthy.ffxiv WHERE id = %s', (self.character_id,))
        data = json.loads(self.db_cur.fetchone()[0])
        self.mounts_owned = data['total']

    async def read_achievement_data(self):
        self.db_cur.execute('SELECT achievement_data from "database1".synthy.ffxiv WHERE id = %s', (self.character_id,))
        data = json.loads(self.db_cur.fetchone()[0])
        self.achievements = data['achievement_points']
