import discord
from discord.ext import commands
import _supercell_
from datetime import datetime
from pytz import timezone
import sys
import firebase_admin
from firebase_admin import db
import _storage_
import creds
from PIL import Image, ImageEnhance
import requests
import pylast
import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=creds.client_id_spotify,
                                               client_secret=creds.client_secret_spotify,
                                               redirect_uri="TODO_YOUR_REDIRECT_URI",
                                               scope="user-read-playback-state, user-read-private, playlist-modify-public, ugc-image-upload, playlist-modify-private, user-top-read, user-library-modify, user-library-read, user-read-currently-playing, app-remote-control, streaming",
                                               cache_path=".spotipyoauthcache"))

intents = discord.Intents.default()
intents.members = True

def embedFunction(title, desc, embedDict=None, img=None, footer=None):
    embedVar = discord.Embed(title = title, description = desc, color = 0xbbb2e9)
    if img != None: embedVar.set_thumbnail(url = img)
    if embedDict != None:
        for key in embedDict: embedVar.add_field(name = key, value = embedDict[key][0], inline = embedDict[key][1])
    if footer != None: embedVar.set_footer(text = footer)
    return embedVar

def get_time(format):
    now_time = datetime.now(timezone('Europe/Berlin'))
    date_time = now_time.strftime(format)
    return date_time

def log(ctx, cmd, geoWon = 0, geoLost = 0):
    # Log to Google Cloud file
    if ctx.author.id != creds.admin_id:
        open("TODO_YOUR_LOGFILE.txt", "a").write(f"{get_time('[%d-%m-%Y %H:%M:%S %Z]')} {cmd} used by {ctx.author} in {ctx.channel} on {ctx.guild}\n")
        open("TODO_YOUR_LOGFILE.txt", "a").close()

    # Log Message Author
    refUsers = db.reference("TODO_FIREBASE_DIRECTORY")
    try:
        for key, value in refUsers.get().items():
            if value["ID"] == str(ctx.author.id):
                refUsers.child(key).update({
                    "Name": str(ctx.author),
                    "Last request": get_time("%d-%m-%Y %H:%M:%S %Z"),
                    "Total requests": int(value["Total requests"]) + 1,
                    "Geo won": int(value["Geo won"]) + geoWon,
                    "Geo lost": int(value["Geo lost"]) + geoLost
                    })
                return
        refUsers.push().set({
            "Name": str(ctx.author),
            "Last request": get_time("%d-%m-%Y %H:%M:%S %Z"),
            "ID": str(ctx.author.id),
            "Clash of Clans ID": "None",
            "Total requests": int(1),
            "Geo won": int(geoWon),
            "Geo lost": int(geoLost),
            "lastfm": "None"
            })
    except:
        refUsers.push().set({
            "Name": str(ctx.author),
            "Last request": get_time("%d-%m-%Y %H:%M:%S %Z"),
            "ID": str(ctx.author.id),
            "Clash of Clans ID": "None",
            "Total requests": int(1),
            "Geo won": int(geoWon),
            "Geo lost": int(geoLost),
            "lastfm": "None"
            })

def activity():
    try:
        track_id = sp.current_user_playing_track()["item"]["id"]
        track = sp.track(track_id, market = None)
        return track["name"] + " by " + track["artists"][0]["name"]
    except: return "offline"

def jkg_filter(ctx,bot):
    if ctx.author.id == creds.admin_id: return False
    else:
        allowed_users = []
        for guild in bot.guilds:
            if str(guild.id) in creds.trusted_servers:
                for member in guild.members: allowed_users.append(str(member.id))
        if str(ctx.author.id) in set(allowed_users): return False
        else: return True
    
def dominant_color(url):
    response = requests.get(
        'https://api.imagga.com/v2/colors?image_url=%s' % url,
        auth=(creds.api_key_imagga, creds.api_secret_imagga))
    return response.json()["result"]["colors"]["background_colors"][0]

def getUserInfo(user):
    embedVar = discord.Embed(title=user["name"], description=" ", color=0xbbb2e9)
    embedVar.set_thumbnail(url=user["clan"]["badgeUrls"]["small"])
    embedVar.add_field(name = "Clan name", value = f'```{user["clan"]["name"]}```', inline = True)
    embedVar.add_field(name = "Clan tag", value = f'```{user["clan"]["tag"]}```', inline = True)
    embedVar.add_field(name = "Clan level", value = f'```{user["clan"]["clanLevel"]}```', inline = True)

    embedVar.add_field(name = "Town hall", value = f'```{user["townHallLevel"]}```', inline = True)
    embedVar.add_field(name = "XP level", value = f'```{user["expLevel"]}```', inline = True)
    embedVar.add_field(name = "Village ID", value = f'```{user["tag"]}```', inline = True)

    embedVar.add_field(name = "Trophies", value = f'```{user["trophies"]}```', inline = True)
    embedVar.add_field(name = "Best trophies", value = f'```{user["bestTrophies"]}```', inline = True)

    embedVar.add_field(name = "War stars", value = f'```{user["warStars"]}```', inline = True)
    embedVar.add_field(name = "Attack wins", value = f'```{user["attackWins"]}```', inline = True)
    embedVar.add_field(name = "Defense wins", value = f'```{user["defenseWins"]}```', inline = True)
    return embedVar

def coc_cw(clan_id):
    now_datetime = datetime.strptime(str(datetime.now(timezone('UTC')))[:-13],"%Y-%m-%d %H:%M:%S")
    war = _supercell_.cw_info(clan_id)
    embedVar = discord.Embed(title = "Clan War", description = " ", color = 0xbbb2e9)

    if war["state"] == "preparation":
        embedVar.add_field(name = "State", value = "```fix\n{0}```".format("Preparation"), inline = True)
        embedVar.add_field(name = "Size", value = "```{0} vs {0}```".format(war["teamSize"]),inline = True)
        embedVar.add_field(name = "Starts in", value = "```{}```".format(datetime.strptime(war["startTime"], "%Y%m%dT%H%M%S.%fZ") - now_datetime), inline = True)
    elif war["state"] == "inWar":
        embedVar.add_field(name = "State", value = "```diff\n-{0}```".format("In war", inline = True))
        embedVar.add_field(name = "Size", value = "```{0} vs {0}```".format(war["teamSize"], inline = True))
        embedVar.add_field(name = "Ends in", value = "```{}```".format(datetime.strptime(war["startTime"], "%Y%m%dT%H%M%S.%fZ") - now_datetime), inline = True)
    elif war["state"] == "warEnded":
        embedVar.add_field(name = "State", value = "```yaml\n{0}```".format("War ended"), inline = True)
        embedVar.add_field(name = "Size", value = "```{0} vs {0}```".format(war["teamSize"]), inline = True)
    else:
        embedVar.add_field(name = "State", value = "```yaml\n{0}```".format("Not in war"), inline = True)
        return embedVar

    embedVar.set_thumbnail(url = war["clan"]["badgeUrls"]["small"])
    embedVar.add_field(name = "Clans", value = "```{0:<20} vs {1:>20}```".format(war["clan"]["name"], war["opponent"]["name"]), inline = False)

    if war["clan"]["stars"] > war["opponent"]["stars"]: embedVar.add_field(name = "Stars", value = "```yaml\n{0:<20}    {1:>20}```".format(war["clan"]["stars"], war["opponent"]["stars"]), inline = False)
    elif war["clan"]["stars"] < war["opponent"]["stars"]: embedVar.add_field(name = "Stars", value = "```diff\n-{0:<20}    {1:>20}```".format(war["clan"]["stars"], war["opponent"]["stars"]), inline = False)
    else: embedVar.add_field(name = "Stars", value = "```fix\n{0:<20}    {1:>20}```".format(war["clan"]["stars"], war["opponent"]["stars"]), inline = False)

    if war["clan"]["destructionPercentage"] > war["opponent"]["destructionPercentage"]: embedVar.add_field(name = "Destruction percentage", value = "```yaml\n{0:<20}    {1:>20}```".format(war["clan"]["destructionPercentage"], war["opponent"]["destructionPercentage"]), inline = False)
    elif war["clan"]["destructionPercentage"] < war["opponent"]["destructionPercentage"]: embedVar.add_field(name = "Destruction percentage", value = "```diff\n-{0:<20}    {1:>20}```".format(war["clan"]["destructionPercentage"], war["opponent"]["destructionPercentage"]), inline = False)
    else: embedVar.add_field(name = "Destruction percentage", value = "```fix\n{0:<20}    {1:>20}```".format(war["clan"]["stars"], war["opponent"]["stars"]), inline = False)

    embedVar.add_field(name = "Attacks", value = "```{0:<20}    {1:>20}```".format(war["clan"]["attacks"], war["opponent"]["attacks"]), inline = False)

    embedVar.set_footer(text=get_time("%d.%m.%Y %H:%M %Z"))
    return embedVar

def nowplaying(ctx, user_name):
    network = pylast.LastFMNetwork(
        api_key=creds.api_key_lastfm,
        api_secret=creds.api_secret_lastfm,
        username=creds.username_lastfm,
        password_hash=creds.password_hash_lastfm,)

    try:
        user = network.get_user(user_name)
        np = repr(user.get_now_playing()).split("'")
        try:
            q = sp.search(f"{str(np[3])} {str(np[1])}", limit=1, offset=0, type='track', market=None)["tracks"]["items"][0]
            url = q["album"]["images"][0]["url"]
            album = str(q["album"]["name"])
        except:
            album = network.get_album(str(np[1]), str(np[3]))
            url = album.get_cover_image()
        response_rgb = dominant_color(url)
        embedVar = discord.Embed(title = f"Now playing", description = " ", color = discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
        embedVar.set_author(name = f"{user} - {ctx.author}", icon_url = user.get_image())
        embedVar.set_thumbnail(url = url)
        embedVar.add_field(name = f"**{np[3]}**", value = f'By **{np[1]}** on **{album}**', inline = True)
        if np[1] == "Charli XCX":
            for key, value in _storage_.charli_emojis.items():
                if key == album: extra_emoji = value
        else: extra_emoji = None
    except: return None, None
    return embedVar, extra_emoji
            
def spotify_cmds(ctx, cmd, *args):
    if cmd in ["pause", "play", "skip", "collage"]:
        if ctx.author.id == creds.admin_id:
            devices = sp.devices()
            for i in range(len(devices["devices"])):
                if devices["devices"][i]["is_active"]: device_id = devices["devices"][i]["id"]
            streaming = sp.current_playback(market = None, additional_types = None)
            track_name = streaming["item"]["name"]
            track_artist = streaming["item"]["album"]["artists"][0]["name"]
            track_id = streaming["item"]["id"]
            thumbnail = sp.track(track_id, market = None)["album"]["images"][2]["url"]
            response_rgb = dominant_color(thumbnail)
            if cmd == "pause" or cmd == "play":
                if streaming["is_playing"]:
                    embedVar = discord.Embed(title = "Song paused:", description = " ", color = discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
                    embedVar.set_thumbnail(url = thumbnail)
                    embedVar.add_field(name = track_name, value = track_artist, inline = True)
                    sp.pause_playback(device_id)
                    return embedVar
                else:
                    embedVar = discord.Embed(title = "Song resumed:", description = " ", color = discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
                    embedVar.set_thumbnail(url = thumbnail)
                    embedVar.add_field(name = track_name, value = track_artist, inline = True)
                    sp.start_playback(device_id, context_uri = None, uris = None, offset = None, position_ms = None)
                    return embedVar

            elif cmd == "skip":
                embedVar = discord.Embed(title = "Song skipped:", description = " ", color = discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
                embedVar.set_thumbnail(url = thumbnail)
                embedVar.add_field(name = track_name, value = track_artist, inline = True)
                sp.next_track(device_id)
                return embedVar

            elif cmd == "collage":
                try:
                    if args[1] == "short_term": time_period, time_range = "last 4 weeks", args[1]
                    elif args[1] == "medium_term": time_period, time_range = "last 6 months", args[1]
                    elif args[1] == "long_term": time_period, time_range = "lifetime", args[1]
                    else: time_period, time_range = "*not specified*: last 4 weeks", "short_term"
                except: time_period, time_range = "*not specified*: last 4 weeks", "short_term"
                try:
                    side = int(args[0])
                    if side < 1 or side > 7: side = 3
                except: side = 3
                new = Image.new("RGBA", (side*250, side*250))
                top = sp.current_user_top_tracks(side**2, offset=0, time_range=time_range)
                list1 = [v["album"]["images"][1]["url"] for i, v in enumerate(top["items"])]
                offsetX, offsetY = 0, 0
                for i, url in enumerate(list1):
                    img = Image.open(requests.get(url, stream=True).raw)
                    img = img.resize((250, 250))
                    new.paste(img, (0+offsetX, 0+offsetY))
                    offsetX += 250
                    if offsetX == side*250:
                        offsetY += 250
                        offsetX = 0
                filepath = f"{get_time('%d%m%Y%H%M%S')}.png"
                new.save(filepath,"PNG")
                response_rgb = dominant_color(sp.current_user_top_tracks(1, offset=0, time_range=time_range)["items"][0]["album"]["images"][1]["url"])
                embed = discord.Embed(title="Top Songs", description=time_period, color=discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
                file = discord.File(filepath, filename=filepath)
                embed.set_image(url=f"attachment://{filepath}")
                return file, embed, filepath

        else:
            log(ctx, "spotify, access denied")
            return embedFunction("You do not have the permission to use this command.", "Your attempt was logged.", img=_storage_.locked_img, footer=get_time("%d.%m.%Y %H:%M %Z"))
    else:
        if cmd == "cover":
            try:
                track = sp.track(' '.join(args), market=None)
                response_rgb = dominant_color(track["album"]["images"][1]["url"])
                embedVar = discord.Embed(title = "Spotify Album Cover", description = " ", color = discord.Color.from_rgb(response_rgb["r"], response_rgb["g"], response_rgb["b"]))
                embedVar.set_thumbnail(url = _storage_.spotify_img)
                embedVar.add_field(name = track["name"], value = f'by {track["artists"][0]["name"]}', inline = True)
                embedVar.set_image(url = track["album"]["images"][0]["url"])
                return embedVar
            except:
                embedVar = discord.Embed(title = "Spotify Error", description = " ", color = 0xbbb2e9)
                embedVar.set_thumbnail(url = _storage_.spotify_img)
                embedVar.add_field(name = "Invalid URL", value = f"{' '.join(args)} doesn't qualify as a valid Spotify song URL. The URL should look similar to ```https://open.spotify.com/track/6PZpNMstpIiRenGK5UyG5D?si=2239da1894b64ef8```", inline = True)
                return embedVar

        elif cmd == "help":
            embedVar = embedFunction("Spotify Commands", " ", _storage_.cmds_spotify, _storage_.spotify_img)
            log(ctx, "spotify help")
            return embedVar

        else:
            return embedFunction("Spotify Error", " ", {"Command not found": [f"{cmd} isn't one of MarekBot's Spotify commands. Use ```/spotify help``` to see a list of Spotify commands.", True]})
