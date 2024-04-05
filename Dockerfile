# This file is a template, and might need editing before it works on your project.
FROM python:3.11

# Edit with mysql-client, postgresql-client, sqlite3, etc. for your needs.
# Or delete entirely if not needed.
RUN apt-get update && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./cogs/ ./cogs/
COPY ./overlays/ ./overlays/
COPY ./config/ ./config/
COPY ./synthy.py ./synthy.py
COPY ./config.ini ./config.ini
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV discord_bot_token=""
ENV oxford_app_id=""
ENV oxford_app_key=""
ENV deep_ai_key=""
ENV openweather_app_id=""
ENV db_name=""
ENV db_user=""
ENV db_pass=""
ENV db_host=""
ENV db_schema=""
ENV db_port="5432"

COPY . /usr/src/app

CMD python3 synthy.py
