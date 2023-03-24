import socket
from datetime import datetime
from urllib.error import HTTPError

import discord
import interactions
import mysql.connector
import requests
from discord.ext import commands
from mysql.connector import Error
from pytz import timezone

import creds
import storage


def create_connection():
    try:
        host_local = socket.gethostname()
        if host_local == "dauntless-1":
            connection = mysql.connector.connect(**creds.gcpConfig)
        else:
            connection = mysql.connector.connect(**creds.localConfig)
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")


def writeSQL(query):
    connection = create_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")
    connection.close()


def readSQL(query):
    connection = create_connection()
    cursor = connection.cursor(buffered=True)
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    connection.close()


def get_embed(title, desc, embedDict=None, img=None, footer=None, dpy_embed=False, color=0xbbb2e9):
    if dpy_embed is True:
        embedVar = discord.Embed(title=title, description=desc, color=color)
    else:
        embedVar = interactions.Embed(
            title=title, description=desc, color=color)
    if img != None:
        embedVar.set_thumbnail(url=img)
    if embedDict != None:
        for key in embedDict:
            embedVar.add_field(
                name=key, value=embedDict[key][0], inline=embedDict[key][1])
    if footer != None:
        embedVar.set_footer(text=footer)
    return embedVar


def get_time(format):
    now_time = datetime.now(timezone('Europe/Berlin'))
    date_time = now_time.strftime(format)
    return date_time


def log(ctx, command, priority, dpy=False):
    resp = readSQL(
        f"""SELECT id FROM discord_users WHERE id = '{ctx.user.id}'""")
    if len(resp) == 0:
        writeSQL(
            f"""INSERT INTO discord_users (id, name) VALUES ("{ctx.user.id}", "{ctx.user.username}#{ctx.user.discriminator}")""")

    if ctx.user.id not in creds.admin_ids:
        command = (command[:190] + '..') if len(command) > 190 else command
        if dpy is False:
            writeSQL(
                f"""INSERT INTO discord_logs(id, author_name, author_id, guild, channel, command, priority) VALUES("{ctx.id}", "{ctx.user.username}#{ctx.user.discriminator}", "{ctx.user.id}", "{ctx.guild}", "{ctx.channel}", "{command}", "{priority}")""")


def is_filter_on(ctx, bot):
    if ctx.user.id in creds.admin_ids:
        return False
    else:
        allowed_users = []
        for guild in bot.guilds:
            if str(guild.id) in creds.trusted_servers:
                for member in guild.members:
                    allowed_users.append(str(member.id))
        if str(ctx.user.id) in set(allowed_users):
            return False
        else:
            return True


def get_dominant_color(url):
    try:
        response = requests.get(
            'https://api.imagga.com/v2/colors?image_url=%s' % url,
            auth=(creds.api_key_imagga, creds.api_secret_imagga))
        return response.json()["result"]["colors"]["background_colors"][0]
    except:
        return {"r": 187, "g": 178, "b": 233}
