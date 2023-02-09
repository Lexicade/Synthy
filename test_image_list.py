import os
import math

from PIL import Image, ImageFont, ImageDraw


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

    def master_image(self):
        for image_name in self.images_in_dir:
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

        self.image.save('./imagelist.png')


ilist = ImageList().master_image()

