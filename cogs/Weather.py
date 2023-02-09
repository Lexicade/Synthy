import os

from discord.ext import commands
import discord
import requests
import json
import importlib
import utils
import datetime
importlib.reload(utils)


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def convert_time(time, format='%H:%M:%S'):
        return datetime.datetime.utcfromtimestamp(time).strftime(format)

    @staticmethod
    async def convert_icon(name):
        icons = {"Clear": "🌞",
                 "Clouds": "☁",
                 "Rain": "🌧️",
                 "Thunderstorm": "⛈",
                 "Mist": "🌁",
                 "Snow": "❄"}
        return icons[name]

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="location",
                    description="Enter a location tog et weather data from.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
            ],
        )
    )
    async def weather(self, ctx, location):
        """Get the weather of any area."""
        location = location.replace(" ", "%20")
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.environ.get('openweather_app_id')}&units=metric")
        json_data = json.loads(response.text)

        if json_data['cod'] == 200:
            str_sunrise = await self.convert_time(int(json_data['sys']['sunrise'] + json_data['timezone']))
            str_sunset = await self.convert_time(int(json_data['sys']['sunset'] + json_data['timezone']))
            str_st = await self.convert_time(int(json_data['dt'] + json_data['timezone']))
            icn_weather = await self.convert_icon(json_data['weather'][0]['main'])

            emb = await utils.embed(ctx, f"🗺️ Weather for {json_data['name']} from {str_st}", "")
            emb = await utils.field(emb, f"{icn_weather} Current forecast", f"{str(json_data['weather'][0]['description']).capitalize()}", inline=False)
            emb = await utils.field(emb, f"🌡️ Temperature", f"{json_data['main']['temp_min']} to {json_data['main']['temp_max']}°С", inline=True)
            emb = await utils.field(emb, f"💨 Wind", f"{json_data['wind']['speed']} m/s", inline=True)
            emb = await utils.field(emb, f"☁ Clouds", f"{json_data['clouds']['all']}%", inline=True)
            emb = await utils.field(emb, f"📏 Pressure", f"{json_data['main']['pressure']}hPa", inline=True)
            emb = await utils.field(emb, f"💦 Humidity", f"{json_data['main']['humidity']}%", inline=True)
            emb = await utils.field(emb, f"👁️ Visibility", f"{json_data['visibility']/1000}KM", inline=True)
            emb = await utils.field(emb, f"🌅 Sunrise", f"{str_sunrise}", inline=True)
            emb = await utils.field(emb, f"🌇 Sunset", f"{str_sunset}", inline=True)

        else:
            emb = await utils.embed(ctx, f"We can't find that area.", f"Check that ***`{location}`*** is spelt right and try again.")

        await ctx.send(embed=emb)

    @commands.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="location",
                    description="Enter a location to get forecast data from.",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
            ],
        )
    )
    async def forecast(self, ctx, location):
        """Get a forecast of any area."""
        location = location.replace(" ", "%20")
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={os.environ.get('openweather_app_id')}&units=metric")
        json_data1 = json.loads(response.text)

        if json_data1['cod'] == 200:
            # Get first request
            str_name = json_data1['name']
            response = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={json_data1['coord']['lat']}&lon={json_data1['coord']['lon']}&exclude=hourly,minutely,current&appid={os.environ.get('openweather_app_id')}&units=metric")
            json_data2 = json.loads(response.text)
            int_timezone = int(json_data2['timezone_offset'])

            emb = await utils.embed(ctx, f"🗺️ Forecast for {str_name}", "")

            # Get second request for lat/lon based forecast
            for day in json_data2['daily']:
                str_day = await self.convert_time(int(day['dt']) + int_timezone, '%A %d %b')
                icn_weather = await self.convert_icon(day['weather'][0]['main'])

                day_details = f"{icn_weather} {day['weather'][0]['main']}\n" + \
                              f"Chance of rain: {int(day['pop'] * 100)}%\n" + \
                              f"UV Index: {day['uvi']}\n" + \
                              f"Temp: {day['temp']['min']} to {day['temp']['max']}°С"

                emb = await utils.field(emb, f"{str_day}", day_details, inline=True)

        else:
            emb = await utils.embed(ctx, f"We can't find the forecast for that area.", f"Check that ***`{location}`*** is spelt right and try again.")

        await ctx.send(embed=emb)



def setup(bot):
    print("INFO: Loading [Weather]... ", end="")
    bot.add_cog(Weather(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Weather]")


# Tuesday 11 Aug - Rain