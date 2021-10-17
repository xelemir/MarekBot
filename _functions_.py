# File looks messy but works

import discord
from discord.ext import commands
import _supercell_
from datetime import datetime
from pytz import timezone
import sys
import _storage_
import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-read-playback-state, user-read-currently-playing, app-remote-control, streaming",
                                               cache_path=".spotipyoauthcache"))

def coc_cw(clan_id):
    war = _supercell_.cw_info(clan_id)
    now_time_str = str(datetime.now(timezone('UTC')))[:-13]
    now_datetime = datetime.strptime(now_time_str,"%Y-%m-%d %H:%M:%S")
    deadline_now_datetime = datetime.strptime(war["startTime"], "%Y%m%dT%H%M%S.%fZ")
    if war["state"] == "inWar": deadline_now_datetime = datetime.strptime(war["endTime"], "%Y%m%dT%H%M%S.%fZ")
    difference_time = deadline_now_datetime-now_datetime

    embedVar = discord.Embed(title = "Clan War", description = " ", color = 0xbbb2e9)
    embedVar.set_thumbnail(url = war["clan"]["badgeUrls"]["small"])
    valueClan = "```yaml\n{}```".format(war["clan"]["name"])
    valueEnemy = "```diff\n- {}```".format(war["opponent"]["name"])
    embedVar.add_field(name = "clan", value = valueClan, inline = True)
    embedVar.add_field(name = "-", value = "vs.", inline = True)
    embedVar.add_field(name = "enemy", value = valueEnemy, inline = True)
    valueWarState = "```fix\n{}```".format(war["state"])
    if war["state"] == "inWar": valueWarState = "```diff\n- in war```"
    elif war["state"] == "warEnded": valueWarState = "```yaml\n{}```".format("war ended")
    valueTeamSize = "```{}```".format(war["teamSize"])
    embedVar.add_field(name = "------------------------------", value = "```general info```", inline = False)
    embedVar.add_field(name = "state", value = valueWarState, inline = True)
    embedVar.add_field(name = "team size", value = valueTeamSize, inline = True)
    if war["state"] == "inWar": embedVar.add_field(name = "war ends in:", value = "```{}```".format(difference_time), inline = False)
    elif war["state"] == "preparation": embedVar.add_field(name = "war starts in:", value = "```{}```".format(difference_time), inline = False)
    valueClanStars = "```fix\n{}```".format(war["clan"]["stars"])
    valueEnemyStars = "```fix\n{}```".format(war["opponent"]["stars"])
    if war["clan"]["stars"] > war["opponent"]["stars"]:
        valueClanStars = "```yaml\n{}```".format(war["clan"]["stars"])
        valueEnemyStars = "```{}```".format(war["opponent"]["stars"])
    elif war["clan"]["stars"] < war["opponent"]["stars"]:
        valueClanStars = "```{}```".format(war["clan"]["stars"])
        valueEnemyStars = "```diff\n- {}```".format(war["opponent"]["stars"])
    embedVar.add_field(name = "------------------------------", value = "```stars```", inline = False)
    embedVar.add_field(name = "clan", value = valueClanStars, inline = True)
    embedVar.add_field(name = "enemy", value = valueEnemyStars, inline = True)
    valueClanPercentage = "```fix\n{}%```".format(war["clan"]["destructionPercentage"])
    valueEnemyPercentage = "```fix\n{}%```".format(war["opponent"]["destructionPercentage"])
    if war["clan"]["destructionPercentage"] > war["opponent"]["destructionPercentage"]:
        valueClanPercentage = "```yaml\n{}%```".format(war["clan"]["destructionPercentage"])
        valueEnemyPercentage = "```{}%```".format(war["opponent"]["destructionPercentage"])
    elif war["clan"]["destructionPercentage"] < war["opponent"]["destructionPercentage"]:
        valueClanPercentage = "```{}%```".format(war["clan"]["destructionPercentage"])
        valueEnemyPercentage = "```diff\n- {}%```".format(war["opponent"]["destructionPercentage"])
    embedVar.add_field(name = "------------------------------", value = "```destruction percentage```", inline = False)
    embedVar.add_field(name = "clan", value=valueClanPercentage, inline = True)
    embedVar.add_field(name = "enemy", value=valueEnemyPercentage, inline = True)
    valueClanStars = "```{}```".format(war["clan"]["attacks"])
    valueEnemyStars = "```{}```".format(war["opponent"]["attacks"])
    embedVar.add_field(name ="------------------------------", value = "```attacks```", inline = False)
    embedVar.add_field(name = "clan", value=valueClanStars, inline = True)
    embedVar.add_field(name = "enemy", value=valueEnemyStars, inline = True)
    return embedVar

def spotify_cmds(cmd):
    devices = sp.devices()
    for i in range(len(devices["devices"])):
        if devices["devices"][i]["is_active"]: device_id = devices["devices"][i]["id"]
    streaming = sp.current_playback(market = None, additional_types = None)
    track_name = streaming["item"]["name"]
    track_artist = streaming["item"]["album"]["artists"][0]["name"]
    track_id = streaming["item"]["id"]
    thumbnail = sp.track(track_id, market = None)["album"]["images"][2]["url"]
    if cmd == "pause" or cmd == "play":
        if streaming["is_playing"]:
            embedVar = discord.Embed(title = "Song paused:", description = " ", color = 0xbbb2e9)
            embedVar.set_thumbnail(url = thumbnail)
            embedVar.add_field(name = track_name, value = track_artist, inline = True)
            sp.pause_playback(device_id)
            return embedVar
        else:
            embedVar = discord.Embed(title = "Song resumed:", description = " ", color=0xbbb2e9)
            embedVar.set_thumbnail(url = thumbnail)
            embedVar.add_field(name = track_name, value = track_artist, inline = True)
            sp.start_playback(device_id, context_uri = None, uris = None, offset = None, position_ms = None)
            return embedVar

    elif cmd == "skip":
        embedVar = discord.Embed(title = "Song skipped:", description = " ", color = 0xbbb2e9)
        embedVar.set_thumbnail(url = thumbnail)
        embedVar.add_field(name = track_name, value = track_artist, inline = True)
        sp.next_track(device_id)
        return embedVar

def jkg_img(quote):
    if "keyword0" in quote: return _storage_.keyword0
    elif "keyword1" in quote: return _storage_.keyword1
    elif "keyword2" in quote: return _storage_.keyword2
    elif "keyword3" in quote: return _storage_.keyword3
    else: return _storage_.no_keyword
