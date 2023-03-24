import asyncio
import datetime
import os
import random
import socket
import sys
import time

import cpuinfo
import discord
import interactions
import psutil
import pylast
import requests
import spotipy
from discord.ext import commands, tasks
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

import _functions_ as func
import creds
import storage

# Create spotify object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=creds.client_id_spotify,
                                               client_secret=creds.client_secret_spotify,
                                               redirect_uri=creds.redirect_uri_spotify,
                                               scope="user-read-playback-state, user-read-private, playlist-modify-public, ugc-image-upload, playlist-modify-private, user-top-read, user-library-modify, user-library-read, user-read-currently-playing, app-remote-control, streaming",
                                               cache_path=".spotipyoauthcache"))

# Create last.fm object
network = pylast.LastFMNetwork(
    api_key=creds.api_key_lastfm,
    api_secret=creds.api_secret_lastfm,
    username=creds.username_lastfm,
    password_hash=creds.password_hash_lastfm)

# Intents for discord.py
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.reactions = True
intents.guilds = True

# Create discord interactions object
client = interactions.Client(
    token=creds.bot_token, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

# Create discord.py object
dpy = commands.Bot(command_prefix="/", intents=intents, help_command=None)

# Connect to bot and display servers joined
@dpy.event
async def on_ready():
    print("Bot connected.")
    servers_joined = []
    for guild in dpy.guilds:
        servers_joined.append(guild.name)
    print(servers_joined)
    update_presence.start()


# Display Spotify activity as bots status
@tasks.loop(seconds=60)
async def update_presence():
    # Try to get current song from Spotify and display it as bots status
    try:
        track = sp.current_user_playing_track()
        await dpy.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'{track["item"]["name"]} by {track["item"]["artists"][0]["name"]}'))
    # If no song is playing, display "Charli XCX" as bots status
    except:
        await dpy.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Charli XCX"))
    await asyncio.sleep(60)


# /help command to get a list of all commands
@client.command(name="help", description="Get help with the bot's commands.")
async def help(ctx):
    embed_var = func.get_embed(
        f"{dpy.user.name} Commands", "Here's a list of my commands. [] signalize command options.", storage.cmds_marek, storage.marek_img)
    await ctx.send(embeds=embed_var)
    func.log(ctx, f"/help", "low")


# /system command to get info on the bot's host computer (Running on GCP or locally? CPU? Uptime?)
@client.command(name="system", description="Get info on the bot's host computer.")
async def system(ctx: interactions.CommandContext):
    host = socket.gethostname()
    if host == "dauntless-1":
        local_or_cloud = "on Google Cloud Platform server instance"
    else:
        local_or_cloud = "locally"
    sys_dict = {"Machine:": [f"```Running {local_or_cloud} on {host}```", False],
                "CPU:": [f"```{cpuinfo.get_cpu_info()['brand_raw']}```", False],
                "Uptime:": [f"```{str(datetime.timedelta(seconds=time.time() - psutil.boot_time()))}```", False]}
    embed_var = func.get_embed("System info", " ", sys_dict)
    await ctx.send(embeds=embed_var)
    func.log(ctx, f"/system", "medium")

# /logs command to get a list of all commands that were executed on the bot (Admin only)
@client.command(name="logs", description="See 21 most recent log entries from this bot's MySQL database (Admin only).")
async def logs(ctx: interactions.CommandContext):
    if ctx.user.id in creds.admin_ids:
        resp = func.readSQL(
            """SELECT author_name, command, created_at FROM discord_logs""")[::-1][:21]
        if len(resp) > 0:
            embed_var = interactions.Embed(
                title=f"{dpy.user.name} Logs", description=" ", color=0xbbb2e9)
            for log in resp:
                embed_var.add_field(
                    name=str(log[2]), value=f"```{log[1]}``` used by {log[0]}\n", inline=True)
            await ctx.send(embeds=embed_var)
            func.log(ctx, f"/logs", "medium")
    else:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback."))
        func.log(ctx, f"/logs DENIED permission missing", "high")

# /feedback command to send a message to the bot's developer
@client.command(name="feedback", description="Contact this bot's developer.")
@interactions.option()
async def feedback(ctx: interactions.CommandContext, message: str):
    channel = await dpy.fetch_channel(str(creds.admin_channel))
    embed_var = func.get_embed("Feedback", f"Message by {ctx.user} on {ctx.guild}", {"Content:": [f"```{message}```", True], f"Reply {ctx.user}:": [
                               f"```/reply {ctx.channel_id}```", False]}, footer=f"{ctx.user} ({ctx.user.id}) in #{ctx.channel} ({ctx.channel_id}) on {ctx.guild}.", dpy_embed=True)
    embed_var.set_thumbnail(url=ctx.user.avatar_url)
    await channel.send(embed=embed_var)
    await ctx.send("Your message has been delivered. \N{BALLOT BOX WITH CHECK}")
    func.log(ctx, f"/feedback {message}", "medium")


# /reply (part of feedback) command to reply to a /feedback ticket (Admin only)
@client.command(name="reply", description="Reply to a /feedback ticket (Admin only).")
@interactions.option()
@interactions.option()
async def reply(ctx: interactions.CommandContext, channel_id: str, message: str):
    if ctx.user.id in creds.admin_ids:
        channel = await dpy.fetch_channel(str(channel_id))
        guild = await dpy.fetch_guild(int(creds.trusted_servers[0]))
        support_user = await guild.fetch_member(str(creds.admin_ids[0]))
        embed_var = func.get_embed("Answer to your feedback request", f"Message answered by {support_user}", {"Content:": [
                                   f"```{message}```", True], f"Reply {support_user}:": [f"```/feedback <your message>```", False]}, dpy_embed=True)
        await channel.send(embed=embed_var)
        await ctx.send("Your message has been delivered. \N{BALLOT BOX WITH CHECK}")
        func.log(ctx, f"/reply {channel_id} {message}", "medium")
    else:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback."))
        func.log(
            ctx, f"/reply {channel_id} {message} DENIED permission missing", "high")

# /lastfm base commnd
@client.command()
async def lastfm(ctx: interactions.CommandContext):
    """Base command for /lastfm"""
    pass

# /lastfm add command to connect your last.fm account with your Discord profile
@lastfm.subcommand(name="add", description="Connect your last.fm account with your Discord profile.")
@interactions.option(name="username")
async def add(ctx: interactions.CommandContext, username: str):
    msg = await ctx.send(f"Trying to find {username} on last.fm...")
    try:
        network.get_user(username).get_now_playing()
        func.log(ctx, f"/lastfm add {username}", "medium")
        func.writeSQL(
            f"""UPDATE discord_users SET lastfm = "{username}" WHERE id='{ctx.user.id}'""")
        await msg.edit(f"{username} found.")
        await msg.edit(embeds=func.get_embed("\N{MUSICAL NOTE}  Last.fm connected  \N{MUSICAL NOTE}", f"{ctx.user}, your last.fm account {username} has been connected to your Discord profile.", color=0xbb0001))
    except:
        await msg.edit(f"Error")
        await msg.edit(embeds=func.get_embed("Last.fm user not found", f'Unfortunately, no last.fm account named "{username}" could be found. Please check for spelling and try again.', color=0xbb0001))
        func.log(
            ctx, f"/lastfm add {username} DENIED username not found", "medium")

# /lastfm disconnect command to disconnect your last.fm account from your Discord profile
@lastfm.subcommand(name="disconnect", description="Disconnect your last.fm username from your Discord profile.")
async def disconnect(ctx: interactions.CommandContext):
    resp = func.readSQL(
        f"""SELECT lastfm FROM discord_users WHERE id='{ctx.user.id}'""")
    if resp[0][0] != "None":
        func.writeSQL(
            f"""UPDATE discord_users SET lastfm = "None" WHERE id='{ctx.user.id}'""")
        await ctx.send(embeds=func.get_embed("Last.fm disconnected", f'Your last.fm account "{resp[0][0]}" has been disconnected from your Discord profile.', color=0xbb0001))
        func.log(ctx, f"/lastfm disconnect", "medium")
    else:
        await ctx.send(embeds=func.get_embed("No last.fm account added", "There seems to be no last.fm account associated with your Discord profile. Try '/lastfm add' to add your last.fm account.", color=0xbb0001))
        func.log(ctx, f"/lastfm disconnect DENIED no username added", "low")

# /np command to display your current music streaming activity on last.fm and let other users rate it
@client.command(name="np", description="Display streaming activity on Spotify. (Or elsewhere - last.fm must be connected).")
async def np(ctx: interactions.CommandContext):
    resp = func.readSQL(
        f"""SELECT lastfm FROM discord_users WHERE id='{ctx.user.id}'""")
    if resp[0][0] != "None":
        try:
            msg = await ctx.send(embeds=func.get_embed("Now playing", f'Getting current music streaming activity for last.fm user "{resp[0][0]}"...', color=0x1DB954))
            user = network.get_user(resp[0][0])
            np = str(user.get_now_playing()).split(" - ")
            if len(np) > 2:
                np = [np[0], " - ".join(np[1:])]
            if np == ['None']:
                recent = user.get_recent_tracks(1)[0]
                np = str(recent.track).split(" - ")
                if len(np) > 2:
                    np = [np[0], " - ".join(np[1:])]
                np.append(recent.album)

            q = sp.search(f"{np[1]} {np[0]}", limit=5,
                          offset=0, type='track', market=None)
            for i in q["tracks"]["items"]:
                if i["album"]["album_type"] != "compilation" and i["name"].casefold() == np[1].casefold() and i["artists"][0]["name"].casefold() == np[0].casefold():
                    url = i["album"]["images"][0]["url"]
                    album = i["album"]["name"]
                    album_url = i["album"]['external_urls']['spotify']
                    break
            try:
                _ = album
            except:
                try:
                    album = network.get_album(np[0], np[2])
                except IndexError:
                    album = network.get_album(np[0], np[1])
                url = album.get_cover_image()
                album = str(album).split(" - ")[1]
                if url == None:
                    try:
                        album = network.get_album(np[0], np[1])
                        url = album.get_cover_image()
                    except:
                        pass

            response_rgb = func.get_dominant_color(url)
            embed_var = interactions.Embed(title=f"**{np[1]}**", description=" ", color=int(
                f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
            embed_var.set_author(
                name=f"{ctx.user.username} - now playing", icon_url=user.get_image())
            embed_var.set_thumbnail(url=url)
            try:
                embed_var.add_field(
                    name=f"by {np[0]}", value=f"[on {album}]({album_url})", inline=True)
            except:
                embed_var.add_field(
                    name=f"by {np[0]}", value=f"on {album}", inline=True)
            embed_var.set_footer(
                text=f"{user} has {user.get_playcount()} scrobbles.")
            extra_emoji = []
            if np[0] == "Charli XCX":
                for key, value in storage.charli_emojis.items():
                    if key == album:
                        extra_emoji.append(value)
                extra_emoji.append("CharliXCX:938156838430597150")

            if embed_var is None:
                await msg.edit(embeds=func.get_embed("Issue with listening status", "Unfortunately, an unexpected problem occured while trying to get your listening status.", img=storage.spotify_img, footer="Report this issue via /feedback.", color=0x1DB954))
                return
            emojis = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
            if extra_emoji != []:
                for emoji in extra_emoji:
                    emojis.append(emoji)
            await msg.edit(embeds=embed_var)
            for emoji in emojis:
                await asyncio.sleep(0.5)
                await msg.create_reaction(emoji)
            func.log(ctx, f"/np {np[1]} by {np[0]}", "medium")
        except:
            await ctx.send(embeds=func.get_embed("Issue with listening status", "Unfortunately, an unexpected problem occured while trying to get your listening status.", img=storage.spotify_img, footer="Report this issue via /feedback.", color=0x1DB954))
    else:
        await ctx.send(embeds=func.get_embed("No last.fm account added", "There seems to be no last.fm account associated with your Discord profile. Try '/lastfm add' to add your last.fm account.", color=0xbb0001))
        func.log(ctx, f"/np DENIED no username", "medium")

# /jkg command to get a random jkg quote or search for a quote by keyword
@client.command(name="jkg", description="Random JKG quote or search by keyword; special thanks to Anton.")
@interactions.option(name="keyphrase", required=False)
async def jkg(ctx: interactions.CommandContext, keyphrase: str = None):
    if keyphrase:
        func.log(ctx, f"/jkg {keyphrase}", "medium")
        try:
            quotes_name = {}
            for quote, url in storage.jkg_quotes.items():
                if keyphrase in quote:
                    quotes_name[quote] = url
            quote, url = random.choice(list(quotes_name.items()))
            if func.is_filter_on(ctx, client) == True and any(word in quote for word in storage.is_filter_on):
                await ctx.send(embeds=func.get_embed(f"No matching quote found.", f'No jkg quote contains the phrase "{keyphrase}" you were searching for.', footer="If you believe this is an error, submit a ticket via /feedback."))
                return
        except:
            await ctx.send(embeds=func.get_embed(f"No matching quote found.", f'No jkg quote contains the phrase "{keyphrase}" you were searching for.', footer="If you believe this is an error, submit a ticket via /feedback."))
            return
    else:
        func.log(ctx, f"/jkg", "medium")
        while True:
            quote, url = random.choice(list(storage.jkg_quotes.items()))
            if func.is_filter_on(ctx, client) == True and any(word in quote for word in storage.is_filter_on):
                continue
            break

    embed_var = interactions.Embed(title="JKG Quote", description=quote, color=0xbbb2e9)
    if type(url) == list:
        embed_var.set_thumbnail(url=random.choice(url))
    elif url is not None:
        embed_var.set_thumbnail(url=url)
    await ctx.send(embeds=embed_var)

# /spotify
@client.command()
async def spotify(ctx: interactions.CommandContext):
    """Base command for /spotify"""
    pass

# Play or pause function
def playpause():
    streaming = sp.current_playback(market=None, additional_types=None)
    track_id = streaming["item"]["id"]
    thumbnail = sp.track(track_id, market=None)["album"]["images"][2]["url"]
    response_rgb = func.get_dominant_color(thumbnail)
    if streaming["is_playing"]:
        embed_var = interactions.Embed(title="Song paused:", description=" ", color=int(
            f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
        embed_var.set_thumbnail(url=thumbnail)
        embed_var.add_field(
            name=streaming["item"]["name"], value=streaming["item"]["album"]["artists"][0]["name"], inline=True)
        sp.pause_playback()
        return embed_var

    else:
        embed_var = interactions.Embed(title="Song resumed:", description=" ", color=int(
            f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
        embed_var.set_thumbnail(url=thumbnail)
        embed_var.add_field(
            name=streaming["item"]["name"], value=streaming["item"]["album"]["artists"][0]["name"], inline=True)
        sp.start_playback()
        return embed_var

# /spotify play command to start or stop playback (Admin only)
@spotify.subcommand(name="play", description="Start/resume Spotify playback (Admin only).")
async def play(ctx: interactions.CommandContext):
    if ctx.user.id in creds.admin_ids:
        func.log(ctx, f"/spotify play", "low")
        try:
            embed_var = playpause()
            await ctx.send(embeds=embed_var)
        except:
            await ctx.send(embeds=func.get_embed("Issue with Spotify", "Unfortunately, an unexpected problem occured while trying to start/pause your playback.", img=storage.locked_img, footer="Report this issue via /feedback.", color=0x1DB954))
    else:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
        func.log(ctx, f"/spotify play DENIED permission missing", "high")

# /spotify pause command to start or stop playback (same as /spotify play) (Admin only)
@spotify.subcommand(name="pause", description="Pause Spotify playback (Admin only).")
async def pause(ctx: interactions.CommandContext):
    if ctx.user.id in creds.admin_ids:
        func.log(ctx, f"/spotify pause", "low")
        try:
            embed_var = playpause()
            await ctx.send(embeds=embed_var)
        except:
            await ctx.send(embeds=func.get_embed("Issue with Spotify", "Unfortunately, an unexpected problem occured while trying to start/pause your playback.", img=storage.locked_img, footer="Report this issue via /feedback.", color=0x1DB954))
    else:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
        func.log(ctx, f"/spotify pause DENIED permission missing", "high")

# /spotify refresh command to refresh the spoti.py playlist (Admin only)
@spotify.subcommand(name="refresh", description="Refresh spoti.py playlist (Admin only).")
async def refresh(ctx: interactions.CommandContext):
    if ctx.user.id in creds.admin_ids:
        func.log(ctx, f"/spotify refreshed", "low")
        try:
            sys.path.insert(1, '/home/gruttefien/spotify')
            import spoti
            playlist_id = spoti.get_playlist_id()
            playlist = sp.playlist(
                playlist_id, fields=None, market=None, additional_types=('track', ))
            thumbnail_url = playlist["images"][0]["url"]
            spoti.refresh_playlist(playlist_id)
            response_rgb = func.get_dominant_color(thumbnail_url)
            embed_var = interactions.Embed(title="Playlist refreshed:", description="Playlist refreshed using Discord.", color=int(
                f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
            embed_var.set_thumbnail(url=thumbnail_url)
            embed_var.add_field(
                name=playlist["name"], value=playlist["owner"]["display_name"], inline=True)
            await ctx.send(embeds=embed_var)
        except:
            await ctx.send(embeds=func.get_embed("Issue with Spotify", "Unfortunately, an unexpected problem occured while trying to refresh your playback.", img=storage.locked_img, footer="Report this issue via /feedback.", color=0x1DB954))
    else:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
        func.log(ctx, f"/spotify refresh DENIED permission missing", "high")

# /spotify cover command to get full resolution Spotify album cover art
@spotify.subcommand(name="cover", description="Get full resolution Spotify album cover art.")
@interactions.option(name="url", description="Track URL")
async def cover(ctx: interactions.CommandContext, url: str):
    func.log(ctx, f"/spotify cover {url}", "medium")
    try:
        track = sp.track(url, market=None)
        response_rgb = func.get_dominant_color(
            track["album"]["images"][1]["url"])
        embed_var = interactions.Embed(title="Spotify Album Cover", description=" ", color=int(
            f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
        embed_var.set_thumbnail(url=storage.spotify_img)
        embed_var.add_field(
            name=track["name"], value=f'by {track["artists"][0]["name"]}', inline=True)
        embed_var.set_image(url=track["album"]["images"][0]["url"])
        await ctx.send(embeds=embed_var)
    except:
        await ctx.send(embeds=func.get_embed("Invalid URL", "The supplied URL couldn't be identified as a Spotify album cover URL.", img=storage.spotify_img, footer="Report this issue via /feedback.", color=0x1DB954))

# /spotify collage command to get a collage of Jan's top streamed tracks on Spotify
@spotify.subcommand(name="collage", description="Get a collage of Jan's top streamed tracks on Spotify.")
@interactions.option(
    name="time_range",
    description="Data from this time frame will be used.",
    choices=[interactions.Choice(name="Last 4 weeks", value="short_term"), interactions.Choice(name="Last 6 months", value="medium_term"), interactions.Choice(name="Lifetime", value="long_term")])
@interactions.option(
    name="image_size",
    description="The image will have this many cover images ^2.",
    choices=[interactions.Choice(name="1", value=1), interactions.Choice(name="2", value=2), interactions.Choice(name="3", value=3), interactions.Choice(name="4", value=4), interactions.Choice(name="5", value=5), interactions.Choice(name="6", value=6), interactions.Choice(name="7", value=7)])
async def collage(ctx: interactions.CommandContext, time_range: str, image_size: int):
    msg = await ctx.send(embeds=func.get_embed("Spotify collage", "Creating collage...", color=0x1DB954))
    func.log(ctx, f"/spotify collage", "medium")
    new = Image.new("RGBA", (image_size*250, image_size*250))
    top = sp.current_user_top_tracks(
        image_size**2, offset=0, time_range=time_range)
    list1 = [v["album"]["images"][1]["url"]
             for i, v in enumerate(top["items"])]
    offsetX, offsetY = 0, 0
    for i, url in enumerate(list1):
        img = Image.open(requests.get(url, stream=True).raw)
        img = img.resize((250, 250))
        new.paste(img, (0+offsetX, 0+offsetY))
        offsetX += 250
        if offsetX == image_size*250:
            offsetY += 250
            offsetX = 0
    filepath = f"{func.get_time('%d%m%Y%H%M%S')}.png"
    new.save(filepath, "PNG")
    response_rgb = func.get_dominant_color(sp.current_user_top_tracks(
        1, offset=0, time_range=time_range)["items"][0]["album"]["images"][1]["url"])

    if time_range == "short_term":
        time_range = "Last 4 weeks"
    elif time_range == "medium_term":
        time_range = "Last 6 months"
    else:
        time_range = "Lifetime"
    embed_var = interactions.Embed(title="Top Songs", description=time_range, color=int(
        f"0x{response_rgb['r']:X}{response_rgb['g']:X}{response_rgb['b']:X}", 16))
    embed_var.set_footer(
        text=f'Top songs collage for Jan\nhttps://open.spotify.com/user/n0c39jatc5pksdv4rhxizx2xy\nas of {func.get_time("%d-%m-%Y %H:%M:%S %Z")}')
    await msg.edit(files=interactions.File(filename=filepath), embeds=embed_var)
    os.remove(filepath)

# /spotify follow command to follow an artist or user (Admin only) on Spotify
@spotify.subcommand(name="follow", description="Follow an artist or user on Spotify and be notified about new releases.")
@interactions.option(name="name", description="Artist name or profile ID.")
@interactions.option(
    name="type",
    description="Specify the type.",
    choices=[interactions.Choice(name="Artist", value="artist"), interactions.Choice(name="User", value="user")])
async def follow(ctx: interactions.CommandContext, name: str, type: str):
    if type == "artist":
        func.log(ctx, f"/spotify follow {name}", "medium")
        try:
            artist = sp.search(name, limit=1, offset=0, type='artist', market=None)[
                "artists"]["items"][0]
        except IndexError:
            await ctx.send(embeds=func.get_embed("Artist not found", f"The artist {name} could not be found on Spotify.", img=storage.spotify_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
            return
        resp = func.readSQL(
            f"""SELECT id FROM following WHERE id = '{artist['id']}'""")
        if len(resp) == 0:
            func.writeSQL(
                f"""INSERT INTO following(id, name, addedby, type) VALUES("{artist['id']}", "{artist['name']}", "{ctx.author}", "spotify_artist")""")
            await ctx.send(embeds=func.get_embed(f"\N{MUSICAL NOTE}  Now following {artist['name']}  \N{MUSICAL NOTE}", f"Server will be notified whenever {artist['name']} drops new music.", img=artist["images"][0]["url"], color=0x1DB954))
        else:
            await ctx.send(embeds=func.get_embed(f"\N{MUSICAL NOTE}  Already following {artist['name']}  \N{MUSICAL NOTE}", f"Server will be notified whenever {artist['name']} drops new music.", img=artist["images"][0]["url"], color=0x1DB954))
    elif type == "user":
        if ctx.user.id not in creds.admin_ids:
            await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
            func.log(
                ctx, f"/spotify follow {name} DENIED permission missing", "high")
        else:
            func.log(ctx, f"/spotify follow {name}", "medium")
            try:
                user = sp.user(name)
                try:
                    image = user["images"][0]["url"]
                except:
                    image = "https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png"
                resp = func.readSQL(
                    f"""SELECT id FROM following WHERE id = '{user['id']}'""")
                if len(resp) == 0:
                    func. writeSQL(
                        f"""INSERT INTO following(id, name, addedby, type) VALUES("{user['id']}", "{user['display_name']}", "{ctx.author}", "spotify_user")""")
                    await ctx.send(embeds=func.get_embed(f"\N{MUSICAL NOTE}  Now following {user['display_name']}  \N{MUSICAL NOTE}", f"You will be notified whenever {user['display_name']} creates new public playlists.", img=image, color=0x1DB954))
                else:
                    await ctx.send(embeds=func.get_embed(f"\N{MUSICAL NOTE}  Already following {user['display_name']}  \N{MUSICAL NOTE}", f"You will be notified whenever {user['display_name']} creates new public playlists.", img=image, color=0x1DB954))
            except:
                await ctx.send(embeds=func.get_embed("Issue with Spotify", "Unfortunately, an unexpected problem occured while trying to follow user.", img=storage.spotify_img, footer="Report this issue via /feedback.", color=0x1DB954))

# /spotify unfollow command to unfollow an artist or user on Spotify (Admin only)
@spotify.subcommand(name="unfollow", description="Unfollow an artist or user on Spotify (Admin only).")
@interactions.option(name="name", description="Artist name or profile ID.")
async def unfollow(ctx: interactions.CommandContext, name: str):
    if ctx.user.id not in creds.admin_ids:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
        func.log(
            ctx, f"/spotify unfollow {name} DENIED permission missing", "high")
    else:
        func.log(ctx, f"/spotify unfollow {name}", "medium")
        resp = func.readSQL(
            f"""SELECT id, name FROM following WHERE name = '{name}' OR id = '{name}'""")
        if len(resp) != 0:
            func.writeSQL(
                f"""DELETE FROM following WHERE name = '{name}' OR id = '{name}'""")
            await ctx.send(embeds=func.get_embed(f"Unfollowed {resp[0][1]}", f"You will not be notified anymore about {resp[0][1]}'s Spotify activity.", img=storage.spotify_img, color=0x1DB954))
        else:
            await ctx.send(embeds=func.get_embed(f"Not following {resp[0][1]}", f"{resp[0][1]} is not in the database. Therefore, you would not have been notified about their Spotify activity anyways.", img=storage.spotify_img, color=0x1DB954))

# /spotify following command to list followed artists and users (Admin only)
@spotify.subcommand(name="following", description="List of followed artists and users (Admin only).")
async def following(ctx: interactions.CommandContext):
    if ctx.user.id not in creds.admin_ids:
        await ctx.send(embeds=func.get_embed("Missing permission", "You do not have the permission to use this command. Your attempt was logged.", img=storage.locked_img, footer="If you believe this is an error, submit a ticket via /feedback.", color=0x1DB954))
        func.log(ctx, f"/spotify following DENIED permission missing", "high")
    else:
        func.log(ctx, f"/spotify following", "medium")
        resp = func.readSQL(f"""SELECT id, name FROM following""")
        if len(resp) != 0:
            following_str = ""
            for name in resp:
                following_str += f"{name[0]} {name[1]}\n"
            await ctx.send(embeds=func.get_embed(f"Following", f"You will be notified about these artists and users:\n\n{following_str}", img=storage.spotify_img, color=0x1DB954))
        else:
            await ctx.send(embeds=func.get_embed(f"Not following anyone", f"The database is empty. As this bot is not following anyone, you will not be notified about anyone's Spotify activity.", img=storage.spotify_img, color=0x1DB954))


loop = asyncio.get_event_loop()

task2 = loop.create_task(dpy.start(token=creds.bot_token))
task1 = loop.create_task(client._ready())

gathered = asyncio.gather(task1, task2)
loop.run_until_complete(gathered)