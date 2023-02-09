from discord.ext import commands
import discord
import importlib
import requests
import json
import datetime
import pandas as pd
import io
from datetime import timedelta
import utils
importlib.reload(utils)


class Covid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    async def covid(self, ctx, *, arg):
        """Get Covid stats from your area."""
        if arg.lower() == "jersey":
            emb = await self.get_data_jersey(ctx)
        else:
            json_return = await self.get_latest_csv()
            emb = await self.find_area(ctx, json_return, arg)
        await ctx.send(embed=emb)

    @staticmethod
    async def get_latest_csv():
        days = 0
        while True:
            cur_date = (datetime.datetime.today() - timedelta(days=days)).strftime("%m-%d-%Y")
            url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{cur_date}.csv"
            return_data = requests.get(url)
            if return_data.status_code == 200:
                # df = pd.read_csv(io.StringIO(return_data.content.decode('utf-8')))
                df = pd.read_csv(io.StringIO(return_data.content.decode('utf-8')))
                df.apply(lambda x: [x.dropna()], axis=1)
                data = json.loads(df.to_json(orient="records"))

                return data
            else:
                days = days + 1

    @staticmethod
    async def find_area(ctx, json_data, user_input):
        cur_record = None
        for record in json_data:
            prov = record["Province_State"].lower() if record["Province_State"] is not None else ""
            coun = record["Country_Region"].lower() if record["Country_Region"] is not None else ""
            ckey = record["Combined_Key"].lower() if record["Combined_Key"] is not None else ""

            if prov is "" and coun is "" and ckey == user_input.lower():
                cur_record_text = (f"Confirmed: {record['Confirmed']}" +
                                   f"Deaths: {record['Deaths']} | {round(int(record['Deaths'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Recovered: {record['Recovered']} | {round(int(record['Recovered'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Active: {record['Active']} | {round(int(record['Active'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Last Update: {record['Last_Update']}")
                cur_record = await utils.embed(ctx, f"Covid-19 cases in {record['Combined_Key']}", cur_record_text)

            elif prov is "" and coun == user_input.lower():
                cur_record_text = (f"Confirmed: {record['Confirmed']}\n" +
                                   f"Deaths: {record['Deaths']} | {round(int(record['Deaths'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Recovered: {record['Recovered']} | {round(int(record['Recovered'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Active: {record['Active']} | {round(int(record['Active'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Last Update: {record['Last_Update']}")
                cur_record = await utils.embed(ctx, f"Covid-19 cases in {record['Country_Region']}", cur_record_text)

            elif prov == user_input.lower():
                cur_record_text = (f"Confirmed: {record['Confirmed']}\n" +
                                   f"Deaths: {record['Deaths']} | {round(int(record['Deaths'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Recovered: {record['Recovered']} | {round(int(record['Recovered'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Active: {record['Active']} | {round(int(record['Active'])*100/int(record['Confirmed']), 2)}%\n" +
                                   f"Last Update: {record['Last_Update']}")
                cur_record = await utils.embed(ctx, f"Covid-19 cases in {record['Province_State']}", cur_record_text)
                break

        if cur_record is None:
            cur_record = await utils.embed(ctx, f"Nothing found", "Please check https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/")

        return cur_record

    @staticmethod
    async def get_data_jersey(ctx):
        return_data = requests.get("https://www.gov.je/Datasets/ListOpenData?ListName=COVID19&type=json")
        if return_data.status_code == 200:
            return_data = json.loads(return_data.text)
            # for covid_item in return_data['COVID19'][0]:
            #     return_data['COVID19'][0][covid_item] = 0 if return_data['COVID19'][0][covid_item] == "" else return_data['COVID19'][0][covid_item]

            txt_desc = (f"Negative tests prior Jul 01 2020: `{return_data['COVID19'][0]['TestsNegativeTestsPriorto1July2020']}`\n" +
                        f"Negative tests since Jul 01 2020: `{return_data['COVID19'][0]['TestsNegativeTestssince1July2020']}`\n" +
                        f"Pending results: `{return_data['COVID19'][0]['TestsPendingResults']}`\n" +
                        f"Known Active In: (Hospital: `{return_data['COVID19'][0]['CasesKnownCasesInHospital']}` - Care Homes: `{return_data['COVID19'][0]['CasesKnownCasesInCareHomes']}` - Community: `{return_data['COVID19'][0]['CasesKnownCasesInCommunity']}`)\n" +
                        f"Known Active Cases: `{return_data['COVID19'][0]['CasesCurrentKnownActiveCases']}` (Symptomatic: `{return_data['COVID19'][0]['CasesSymptomatic']}` - Asymptomatic: `{return_data['COVID19'][0]['CasesAsymptomatic']}`)\n" +
                        f"Known Direct Contacts: `{return_data['COVID19'][0]['CasesNumberOfKnownDirectContactsOfCurrentActiveCases']}`\n" +
                        f"Deaths: `{return_data['COVID19'][0]['MortalityTotalDeaths']}`\n" +
                        f"Date: `{return_data['COVID19'][0]['DateTime'].replace('string;#', '')}`")

            emb = await utils.embed(ctx, "Covid-19 cases in Jersey", txt_desc)
            return emb

        else:
            return None


def setup(bot):
    print("INFO: Loading [Covid]... ", end="")
    bot.add_cog(Covid(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Covid]")
