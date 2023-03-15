import math
import re

from discord.ext import commands
import discord
import os
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ExifTags
import time
import mimetypes
import requests
import json
import importlib
import utils
import random
import traceback
importlib.reload(utils)


class ImageCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="template_name",
                    description="The name of the template.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    @commands.defer(ephemeral=False)
    @commands.bot_has_permissions(send_messages=True)
    async def image(self, ctx, template_name):
        """A meme creating command. Use /imagelist for available templates."""
        # Check to see if the guild has it's own image folder
        if not os.path.exists(f"./overlays/{ctx.guild.id}"):
            os.mkdir(f"./overlays/{ctx.guild.id}")
            os.mkdir(f"./overlays/{ctx.guild.id}/images")

        templates = self.get_image_template_names_listed()
        print(f"templates {templates}")
        if template_name.casefold() not in templates:
            await ctx.send(f"Image templates: {', '.join(templates)}")
            return

        image = await self.get_image(ctx, "image")
        print(f"image {image}")
        if not image:
            emb = await utils.embed(ctx, "No image found", "To use this command, an image must be within the 20 most recent messages.")
            await ctx.send(embed=emb)
            return

        overlay_return = await self.img_edit_overlay(image, template_name, ctx.guild.id, ctx)
        file = await self.pil_to_discordfile(overlay_return)
        await ctx.send(file=file)

    @classmethod
    async def pil_to_discordfile(cls, file, filename='image.png'):
        temp_image = BytesIO()
        file.save(temp_image, 'PNG')
        temp_image.seek(0)
        return discord.File(fp=temp_image, filename=filename)

    @commands.defer(ephemeral=True)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def imagelist(self, ctx):
        """Show all available templates to use with /image"""
        image_list = ImageList()
        image_list.generate_image_list()
        file = await image_list.get_image_for_discord()
        await ctx.send(file=file)

    @commands.defer(ephemeral=False)

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="top_text",
                    description="Top text for this image.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=False,
                ),
                discord.ApplicationCommandOption(
                    name="bottom_text",
                    description="Bottom text for this image.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=False,
                )
            ],
        )
    )
    async def text(self, ctx, top_text="", bottom_text=""):
        """Add a caption to the last image posted."""
        print(f"ctx {ctx}")
        top_text = "" if not 'top_text' in ctx.given_values else ctx.given_values['top_text']
        bottom_text = "" if not 'bottom_text' in ctx.given_values else ctx.given_values['bottom_text']
        print(f"top_text {top_text}")
        print(f"bottom_text {bottom_text}")
        img = await self.get_image(ctx, "image")
        try:
            if img:
                img = await self.img_edit_add_text(img, top_text, bottom_text, ctx.guild.id)
                file = await self.pil_to_discordfile(img)
                await ctx.send(file=file)

            else:
                emb = await utils.embed(ctx, f"Unable to retrieve image", "I wasn't able to see a image in the recent chat history.")
                await ctx.send(embed=emb)
        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}")
            emb = await utils.embed(ctx, f"Error", e)
            await ctx.send(embed=emb)

    @commands.defer(ephemeral=False)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def deep(self, ctx):
        """Send the last image posted through a Deep Dream"""
        print(f"ctx {ctx}")
        img = await self.get_image(ctx, "url")
        emb = await self.deep_master(ctx, img)
        await ctx.send(embed=emb)

    @commands.defer(ephemeral=False)
    @commands.context_command(name="DeepAI - Deep Dream")
    async def deep_context(self, ctx: discord.ext.commands.context.Context, message: discord.message.Message):
        """Send the last image posted through a Deep Dream - Via Context Menu"""
        if len(message.embeds) > 0 and message.embeds[0].image:
            image = message.embeds[0].image.url
        elif len(message.attachments) > 0:
            image = message.attachments[0].url
        else:
            emb = await utils.embed(ctx, f"Unable to retrieve image", "I wasn't able to see an image in the message you selected.")
            await ctx.send(embed=emb)
            return

        emb = await self.deep_master(ctx, image)
        await ctx.send(embed=emb)

    async def deep_master(self, ctx, img):
        """Send the last image posted through a Deep Dream"""
        start_time = time.time()

        if img:
            response = requests.post("https://api.deepai.org/api/deepdream",
                                     headers={'api-key': os.environ.get('deep_ai_key', '')},
                                     data={'image': img})
            return_data = json.loads(response.text)

            emb = await utils.embed(ctx,
                                    title="Deep Dream",
                                    message="",
                                    footer=f"\nDone in {round(time.time() - start_time, 2)} seconds.",
                                    image=return_data['output_url'])
        else:
            emb = await utils.embed(ctx, f"Unable to retrieve image", "I wasn't able to see a image in the recent chat history.")
        return emb

    @commands.defer(ephemeral=False)
    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def intensify(self, ctx, intensity: int = 1):
        """Shake images with intensity and violence."""
        img = await self.get_image(ctx.channel, "image")

        img.paste(img, (0, 0))

        if img:
            img_x, img_y = img.size

            max_scale = 200

            img_x = float(img_x / 100)
            img_y = float(img_y / 100)
            while img_x < max_scale or img_y < max_scale:
                img_x = img_x + float(img_x / 100)
                img_y = img_y + float(img_y / 100)
            img_x = int(img_x)
            img_y = int(img_y)
            img = img.resize((img_x, img_y), Image.ANTIALIAS)

            frames = []
            for i in range(4):
                img_x_nudge = random.randint(round(-(img_x / 100 * intensity)), (round(img_x / 100 * intensity)))
                img_y_nudge = random.randint(round(-(img_y / 100 * intensity)), (round(img_y / 100 * intensity)))

                im = Image.new('RGBA', (img_x, img_y), (255, 255, 255, 0))
                # im.convert('RGBA')
                im.paste(img, (img_x_nudge, img_y_nudge))
                # im.convert('RGBA')

                frames.append(im)
                # im.save(f'test{i}.png')

            arr = BytesIO()
            frames[0].save('test_gif1.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=0, disposal=0)
            frames[0].save('test_gif2.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=255, disposal=0)
            frames[0].save('test_gif3.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=0, disposal=1)
            frames[0].save('test_gif4.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=255, disposal=1)
            frames[0].save('test_gif5.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=0, disposal=2)
            frames[0].save('test_gif6.gif', format='GIF', save_all=True, duration=30, loop=0, transparency=255, disposal=2)
            frames[0].save('intensify.gif', format='GIF', append_images=frames[1:], save_all=True, duration=30, loop=0, disposal=0)
            # img.save(arr, format='GIF', append_images=frames[1:], save_all=True, duration=30, loop=0, transparency=0, disposal=2)

            img_debug = Image.new('RGBA', (img_x, img_y), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_debug)
            draw.ellipse((25, 25, 75, 75), fill=(255, 0, 0))
            img_debug.save(arr, format='GIF', transparency=0)

            # first_frame = frames.pop(0)
            # first_frame.save("out.gif", save_all=True, append_images=frames, duration=30, loop=0, transparency=0, disposal=2)

            arr.seek(0)
            await ctx.send(file=discord.File(arr, 'intensify.gif'))
            return
        else:
            await ctx.send(content="Cannot find image.")

    async def get_image(self, channel: discord.TextChannel, return_as: str):
        image = None
        async for message in channel.history(limit=20, before=None, after=None):
            re_matches = re.findall(r"(https?://\S+)", message.content)

            if len(message.embeds) > 0 and message.embeds[0].image:
                image = message.embeds[0].image.url
                break

            elif len(message.attachments) > 0:
                image = message.attachments[0].url
                break

            elif len(re_matches) > 0:
                for match in re_matches:
                    if '?' in match:
                        match = match.split("?")[0]

                    if match.endswith(('jpg', 'jpeg', 'png', 'gif',)):
                        image = match
                        break
                if image:
                    break

        if not image:
            return None

        if return_as == 'url':
            return image

        elif return_as == 'image':
            image = Image.open(BytesIO(requests.get(image).content))

            if image.format in ['GIF']:
                return image
            else:
                rotation = await self.get_exif_data(image)
                if rotation:
                    image = image.rotate(rotation, expand=True)
                return image

    @staticmethod
    async def send_image(ctx, file, title, message):

        emb = await utils.embed(ctx, title=title, message=message)
        await ctx.send(embed=emb, file=discord.File(file, file.name))

        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()

    @staticmethod
    async def get_exif_data(image):
        exif = image._getexif()
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        print(f"orientation {orientation}")

        if exif and orientation and exif[orientation] == 3:
            return 180
        elif exif and orientation and exif[orientation] == 6:
            return 270
        elif exif and orientation and exif[orientation] == 8:
            return 90
        else:
            return None

    @commands.defer(ephemeral=False)
    @commands.command(hidden=True)
    async def emboss(self, ctx, intensity=1):
        """Image Effect: Emboss"""
        img = await self.get_image(ctx.channel, "image")
        file = await self.img_edit_effect(img, ImageFilter.EMBOSS, ctx, intensity)
        await ctx.send(file=file)

    @commands.defer(ephemeral=False)
    @commands.command(hidden=True)
    async def blur(self, ctx, intensity=1):
        """Image Effect: Blur"""
        img = await self.get_image(ctx.channel, "image")
        file = await self.img_edit_effect(img, ImageFilter.BLUR, ctx, intensity)
        await ctx.send(file=file)

    @commands.defer(ephemeral=False)
    @commands.command(hidden=True)
    async def sharpen(self, ctx, intensity=1):
        """Image Effect: Sharpen"""
        img = await self.get_image(ctx.channel, "image")
        file = await self.img_edit_effect(img, ImageFilter.SHARPEN, ctx, intensity)
        await ctx.send(file=file)

    @staticmethod
    def is_url_image(url):
        mimetype, encoding = mimetypes.guess_type(url)
        return mimetype and mimetype.startswith('image')

    @staticmethod
    def check_url(url):
        try:
            request = requests.get(url)
            if request.status_code == 200:
                return True
        except Exception as e:
            return False

    def is_image_and_ready(self, url):
        return self.is_url_image(url) and self.check_url(url)

    @staticmethod
    def get_image_template_names(guild_id):
        template_files = []

        for file in os.listdir(f"./overlays/{guild_id}/"):
            if str(file).startswith("overlay"):
                template_files.append(f"{file.replace('overlay_', '').split('.')[0]}")
            elif str(file).startswith("frame"):
                template_files.append(f"{file.replace('frame_', '').split('.')[0]}")

        return template_files

    @staticmethod
    def get_image_template_names_listed():
        images = []

        for file in os.listdir(f"./config/images/"):
            if 'templated_image.png' in file:
                continue
            else:
                images.append(f"{file.split('.')[0]}")

        # Return formatted lists
        if len(images) > 0:
            images.sort()
            return images
        else:
            return []

    async def img_edit_add_text(self, img, top_text: str, bottom_text: str, guild_id):
        # Define images
        # str_filename = f"./overlays/{guild_id}/tmp_text.png"

        img = await self.img_edit_add_text_write(img, top_text, "top")
        print(f"Success top")
        img = await self.img_edit_add_text_write(img, bottom_text, "bottom")
        print(f"Success bottom")

        # Save Image and return
        # img.save(str_filename)
        return img

    @staticmethod
    async def img_edit_add_text_write(img, input_text, text_pos):
        # Check font is less than image width
        img_w, img_h = img.size
        img_draw = ImageDraw.Draw(img)
        int_font = 90
        font = ImageFont.truetype("./fonts/calibri/calibri.ttf", int_font)
        text_w, text_h = img_draw.textsize(input_text, font=font)

        while text_w > img_w:
            int_font = int_font - 1
            font = ImageFont.truetype("./fonts/calibri/calibri.ttf", int_font)
            text_w, text_h = img_draw.textsize(input_text, font=font)

        # Set text
        int_x = (img_w - text_w) / 2
        int_border = 3
        if text_pos == "top":
            int_y = -5
        elif text_pos == "bottom":
            int_y = img_h - text_h - 10

        # Add Text diagonals
        img_draw.text((int_x - int_border, int_y - int_border), input_text, font=font, fill="black")
        img_draw.text((int_x + int_border, int_y - int_border), input_text, font=font, fill="black")
        img_draw.text((int_x - int_border, int_y + int_border), input_text, font=font, fill="black")
        img_draw.text((int_x + int_border, int_y + int_border), input_text, font=font, fill="black")

        # Add Text straights
        img_draw.text((int_x + int_border, int_y), input_text, font=font, fill="black")
        img_draw.text((int_x - int_border, int_y), input_text, font=font, fill="black")
        img_draw.text((int_x, int_y + int_border), input_text, font=font, fill="black")
        img_draw.text((int_x, int_y - int_border), input_text, font=font, fill="black")
        img_draw.text((int_x, int_y), input_text, (255, 255, 255), font=font)  # Inner Text
        return img

    async def img_edit_overlay(self, template, overlay_name, guild_id, ctx):
        image_overlay_type = 'overlay'
        match_found = False

        # Define order for overlays
        if image_overlay_type == 'overlay':
            bg = Image.open(f"./config/images/{overlay_name}.png")
            fg = template

            img = Image.new("RGBA", bg.size)
            str_filename = f"./config/images/templated_image.png"

            im_boundry, im_topleft = self.get_image_transparency_boundry(f"./config/images/{overlay_name}.png")

            fg_scaled_x, fg_scaled_y = fg.size
            fg_scaled_x = float(fg_scaled_x / 100)
            fg_scaled_y = float(fg_scaled_y / 100)

            while fg_scaled_x < im_boundry[0] or fg_scaled_y < im_boundry[1]:
                fg_scaled_x = fg_scaled_x + float(fg_scaled_x / 100)
                fg_scaled_y = fg_scaled_y + float(fg_scaled_y / 100)

            fg_scaled_x = int(fg_scaled_x)
            fg_scaled_y = int(fg_scaled_y)
            fg_scaled_x_offset = round((fg_scaled_x - im_boundry[0]) / 2)
            fg_scaled_y_offset = round((fg_scaled_y - im_boundry[1]) / 2)

            # resize
            fg = fg.resize((fg_scaled_x, fg_scaled_y), Image.ANTIALIAS)

            # Paste image
            img.paste(fg, (im_topleft[0] - fg_scaled_x_offset, im_topleft[1] - fg_scaled_y_offset),
                      fg.convert('RGBA'))
            img.paste(bg, (0, 0), bg.convert('RGBA'))

        # elif image_overlay_type == 'frame':
        else:
            fg = Image.open(f"./config/images/{overlay_name}.png")
            bg = Image.open(img)

            img = Image.new("RGBA", bg.size)
            str_filename = f"./config/images/{overlay_name}.png"

            bg_width, bg_height = bg.size

            fg_scaled_x, fg_scaled_y = fg.size
            fg_scaled_x = float(fg_scaled_x / 100)
            fg_scaled_y = float(fg_scaled_y / 100)

            max_image_width = 15

            while fg_scaled_x < ((bg_width / 100) * max_image_width):
                fg_scaled_x = fg_scaled_x + float(fg_scaled_x / 100)
                fg_scaled_y = fg_scaled_y + float(fg_scaled_y / 100)

            fg_scaled_x = int(fg_scaled_x)
            fg_scaled_y = int(fg_scaled_y)

            # resize
            fg = fg.resize((fg_scaled_x, fg_scaled_y), Image.ANTIALIAS)

            # Paste image
            img.paste(bg, (0, 0), bg.convert('RGBA'))
            img.paste(fg, (0, 0), fg.convert('RGBA'))

        # img.save(str_filename)
        return img

    @classmethod
    async def img_edit_effect(cls, img, effect_type, ctx, cycles: int):
        while cycles >= 0:
            img = img.filter(effect_type)
            cycles = cycles-1

        return await cls.pil_to_discordfile(img)

    @staticmethod
    def get_image_transparency_boundry(image_overlay):
        im = Image.open(image_overlay)
        image_x, image_y = im.size
        iter_x = iter_y = 1
        top_co = None
        lef_co = im.size
        bot_co = [1, 1]
        rig_co = [1, 1]

        while iter_y < image_y:
            while iter_x < image_x:
                ret_pixel = im.getpixel((iter_x, iter_y))

                # if str(ret_pixel[3]) == "0":
                if int(ret_pixel[3]) < 255:
                    # top pixel will be the first y coordinate match
                    if top_co is None:
                        top_co = [iter_x, iter_y]

                    # Check the x iteration is less than lef_co
                    if iter_x < lef_co[0]:
                        lef_co = [iter_x, iter_y]

                    # Check the x iteration is less than lef_co
                    if iter_x > rig_co[0]:
                        rig_co = [iter_x, iter_y]

                    # Set bot_co to iter_y
                    bot_co = [iter_x, iter_y]

                iter_x = iter_x + 1
            iter_y = iter_y + 1
            iter_x = 1

        top_left = [lef_co[0], top_co[1]]
        bottom_right = [rig_co[0], bot_co[1]]

        boundry_size = [bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]]
        # print(f"lef_co: {lef_co}, top_co: {top_co}, rig_co: {rig_co}, bot_co: {bot_co}")
        # print(f"Co-ordinate 1: ({top_left}), Co-ordinate 2: ({bottom_right}). Boundry size: {boundry_size}")
        return boundry_size, top_left


def setup(bot):
    print("INFO: Loading [Image]... ", end="")
    bot.add_cog(ImageCmd(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Image]")


class ImageList:
    def __init__(self):
        self.image_thumbnail_scale = (100, 100)
        self.images_in_dir = []
        self.get_images()
        self.image_scale = None
        self.get_base_image_scale()

        self.x_offset = 0
        self.y_offset = 0

        self.max_x_size = 96
        self.max_y_size = 80

        self.image = Image.new('RGBA', self.image_scale, color='#202020')
        return

    def get_base_image_scale(self):
        row_count = math.ceil(len(self.images_in_dir) / math.ceil(math.sqrt(len(self.images_in_dir))))
        column_count = math.ceil(len(self.images_in_dir) / row_count)
        self.image_scale = (row_count*100, column_count*100)

    def get_images(self):
        for file in os.listdir(f"./config/images/"):
            self.images_in_dir.append(f"{file.split('.')[0]}")

        # Return formatted lists
        if len(self.images_in_dir) > 0:
            self.images_in_dir.sort()

    def generate_image_list(self):
        for image_name in self.images_in_dir:
            print(f"Processing {image_name}...")
            image_template = Image.open(f'./config/images/{image_name}.png')
            image_scale_x, image_scale_y = image_template.size
            image_scale_x_scaled = round(image_scale_x / self.image_thumbnail_scale[0])
            image_scale_y_scaled = round(image_scale_y / self.image_thumbnail_scale[1])
            while True:
                image_scale_x_scaled += round((image_scale_x / self.image_thumbnail_scale[0]))
                image_scale_y_scaled += round((image_scale_y / self.image_thumbnail_scale[1]))

                if image_scale_x_scaled >= self.max_x_size or image_scale_y_scaled >= self.max_y_size:
                    if image_scale_x_scaled > self.max_x_size:
                        image_scale_x_scaled = self.max_x_size
                    if image_scale_y_scaled > self.max_y_size:
                        image_scale_y_scaled = self.max_y_size
                    break

            # Determine the centered X of the thumbnails position
            centering_image_x = (round(self.image_thumbnail_scale[0] / 2)) - (round(image_scale_x_scaled / 2))

            # Place the green in the background
            image_green = Image.new('RGBA', (image_scale_x_scaled, image_scale_y_scaled), color='#00FF00')
            self.image.paste(image_green, (self.x_offset + centering_image_x, self.y_offset))

            # Place the template in the foreground with it's own mask to see the green
            image_template = image_template.resize((image_scale_x_scaled, image_scale_y_scaled))

            self.image.paste(image_template, (self.x_offset + centering_image_x, self.y_offset), mask=image_template)

            d = ImageDraw.Draw(self.image)
            font = ImageFont.truetype("./fonts/roboto/Roboto-Regular.ttf", 10)
            font_colour = (255, 255, 255, 255)
            name_w, name_h = d.textsize(image_name, font=font)

            d.text((self.x_offset + (100-name_w)/2, self.y_offset+80), image_name, font=font, fill=font_colour)

            self.x_offset += self.image_thumbnail_scale[0]
            if self.x_offset >= self.image_scale[0]:
                self.x_offset = 0
                self.y_offset += self.image_thumbnail_scale[0]

    async def get_image_for_discord(self, filename='image.png'):
        temp_image = BytesIO()
        self.image.save(temp_image, 'PNG')
        temp_image.seek(0)
        return discord.File(fp=temp_image, filename=filename)
