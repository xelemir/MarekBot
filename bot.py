import _storage_ as stor
import _functions_ as func
import creds
import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import cpuinfo
import random
import psutil
import socket
import datetime
import time
import pylast
import os
import firebase_admin
from firebase_admin import db
import _supercell_
intents = discord.Intents.default()
intents.members = True

try: cred_obj = firebase_admin.credentials.Certificate("TODO_YOUR_LOCAL_DIRECTORY/Firebase.jso")
except: cred_obj = firebase_admin.credentials.Certificate("TODO_YOUR_LOCAL_DIRECTORY/Firebase.json")
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://dauntlessfirebase-default-rtdb.firebaseio.com/"
	})

bot = commands.Bot(command_prefix="/", intents=intents)
client = discord.Client()

# user id
admin_id = creds.admin_id
bot_id = creds.bot_id
bot_token = creds.bot_token

# Connected to bot
@bot.event
async def on_ready():
    print("Bot connected.")
    servers = []
    for guild in bot.guilds:
        servers.append(guild.name)
    print(servers)

# /marekhelp
@bot.command()
async def marekhelp(ctx):
    embedVar = func.embedFunction("Marek commands", "Nein du Lappen, ich helf' dir nicht.", stor.cmds_marek, stor.marek_img)
    await ctx.channel.send(embed = embedVar)
    func.log(ctx, "marekhelp")

# /system
@bot.command(name = 'system', aliases = ['sys', 'Sys', 'System'])
async def system(ctx):
    host = socket.gethostname()
    if host == "dauntless-1": local_or_cloud = "on Google Cloud Platform server"
    else: local_or_cloud = "locally"
    sys_dict = {"Machine:": [f"```Running {local_or_cloud} on {host}```", False],
                "CPU:": [f"```{cpuinfo.get_cpu_info()['brand_raw']}```", False],
                "Uptime:": [f"```{str(datetime.timedelta(seconds = time.time() - psutil.boot_time()))}```", False]}
    embedVar = func.embedFunction("System info", " ", sys_dict)
    await ctx.channel.send(embed = embedVar)
    func.log(ctx, "system")

# /Google Cloud Platform
@bot.command(name = 'gcp', aliases = ['GCP', 'googlecloud', 'cloud', 'Cloud', 'GoogleCloud', 'cloud.google'])
async def gcp(ctx):
    if ctx.author.id == admin_id:
        ls = []
        embedVar = discord.Embed(title = "Google Cloud logs", description = "20 most recent events", color = 0xbbb2e9)
        embedVar.set_thumbnail(url = stor.gcp_img)
        for line in open("TODO_YOUR_LOGFILE.txt", "r"):
            if not line.startswith("!"):
                ls.append(line)
        open("TODO_YOUR_LOGFILE.txt", "r").close()
        ls = ls[::-1]
        if len(ls) < 20: end_loop = len(ls)
        else: end_loop = 20
        for i,v in enumerate(ls):
            embedVar.add_field(name = i, value = f"```{v}```", inline = False)
            if i >= end_loop-1: break
        await ctx.channel.send(embed = embedVar)

    else:
        embedVar = func.embedFunction("You do not have the permission to use this command.", "Your attempt was logged.", img=stor.locked_img, footer=func.get_time("%d.%m.%Y %H:%M %Z"))
        await ctx.channel.send(embed = embedVar)
        func.log(ctx, "gcp, access denied")

# /Feedback
@bot.command()
async def feedback(ctx, *args):
    if not args:
        embedVar = func.embedFunction("Feedback", " ", {"Send message": [f"To submit your feedback or report an issue to this bot's developer type:```/feedback <your message>```", True]})
        await ctx.channel.send(embed = embedVar)
    else:
        args = ' '.join(args)
        guild = await bot.fetch_guild(str(creds.trusted_servers[0]))
        me = await guild.fetch_member(str(creds.admin_id))
        channel = await me.create_dm()
        await channel.send(f"{ctx.author} ({ctx.author.id}) in {ctx.channel} ({ctx.channel.id}) on {ctx.guild} said:\n**{args}**\n```/reply {ctx.author.id} {ctx.channel.id} {func.get_time('%d.%m.%Y_%H:%M_%Z')}```")
        await ctx.channel.send("Message has been delivered.")
    func.log(ctx, "feedback")

# /reply (part of feedback)
@bot.command()
async def reply(ctx, author, channelid, time, *args):
    if ctx.author.id == creds.admin_id:
        args = ' '.join(args)
        channel = await bot.fetch_channel(str(channelid))
        await channel.send(f"Answer to your message ({time}) to this bot's developer:\n**{args}**\nTo answer type:```/feedback <your message>```")
        await ctx.channel.send("Message has been delivered.")
    else:
        embedVar = func.embedFunction("You do not have the permission to use this command.", "Your attempt was logged.", img=stor.locked_img, footer=func.get_time("%d.%m.%Y %H:%M %Z"))
        await ctx.channel.send(embed = embedVar)
        func.log(ctx, "reply, access denied") 
    
# /servers
@bot.command()
async def servers(ctx):
    if ctx.author.id == creds.admin_id:
        servers = []
        for guild in bot.guilds:
            servers.append(guild.name)
        await ctx.channel.send(servers)
    else:
        embedVar = func.embedFunction("You do not have the permission to use this command.", "Your attempt was logged.", img=stor.locked_img, footer=func.get_time("%d.%m.%Y %H:%M %Z"))
        await ctx.channel.send(embed = embedVar)
        func.log(ctx, "servers, access denied")
    
# /profile
@bot.command(name = 'profile', aliases = ['Profile', 'PROFILE', 'pROFILE', 'Profil', 'profil', 'Userprofile', 'userprofile', 'User', 'user'])
async def profile(ctx, *args):
    refUsers = db.reference("TODO_YOUR_FIREBASE_DIRECTORY")
    if not args: # args empty
        func.log(ctx, "profile")
        try:
            for key, value in refUsers.get().items():
                if value["ID"] == str(ctx.author.id):
                    embedVar = discord.Embed(title="User profile", description=f"Collected data for {ctx.author}", color = 0xbbb2e9)
                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                    for child_key, child_value in value.items():
                        embedVar.add_field(name = child_key, value = f'```{child_value}```', inline = False)
                    embedVar.add_field(name = "Note:", value = "If you wish to delete your profile type: ```/user delete data```", inline = False)
                    await ctx.channel.send(embed = embedVar)
                    return
            embedVar = func.embedFunction("Profile console", " ", {f"{str(ctx.author)}": ["Error: Couldn't fetch your profile. Please try again.", True]})
            await ctx.channel.send(embed = embedVar)
        except:
            embedVar = func.embedFunction("Profile console", " ", {f"{str(ctx.author)}": ["Error: Couldn't fetch your profile. Please try again.", True]})
            await ctx.channel.send(embed = embedVar)

    else: # args not empty

        if ' '.join(args) == "delete data":
            users = refUsers.get()
            for key, value in users.items():
                if(value["Name"] == str(ctx.author)):
                    refUsers.child(key).set({})
                    embedVar = func.embedFunction("Profile console", " ", {f"{str(ctx.author)}": ["Your profile data has been deleted.", True]})
                    await ctx.channel.send(embed = embedVar)
            func.log(ctx, "profile delete data")

        elif args[0] == "geo":
            users = refUsers.get()
            for key, value in users.items():
                if value["Name"] == str(ctx.author):
                    embedVarGeo = discord.Embed(title = "Geo Guesser Stats", description = value["Name"], color = 0xbbb2e9)
                    embedVarGeo.add_field(name = "Correct answers:", value = value["Geo won"], inline = True)
                    embedVarGeo.add_field(name = "Wrong answers:", value = value["Geo lost"], inline = True)
                    embedVarGeo.add_field(name = "Your win rate:", value = str(int(value["Geo won"]/(value["Geo won"]+value["Geo lost"])*100))+"%", inline = True)
                    await ctx.channel.send(embed = embedVarGeo)
            func.log(ctx, "profile geo")
        elif args[0] == "help":
            embedVar = func.embedFunction("Profile Commands", " ", stor.cmds_profile, ctx.author.avatar_url)
            await ctx.channel.send(embed = embedVar)
            func.log(ctx, "profile help")
            
        elif args[0] == "lastfm":
            func.log(ctx, "profile last.fm")
            refUsers = db.reference("YOUR_FIREBASE_DIRECTORY")
            network = pylast.LastFMNetwork(
                api_key=creds.api_key_lastfm,
                api_secret=creds.api_secret_lastfm,
                username=creds.username_lastfm,
                password_hash=creds.password_hash_lastfm)
            try:
                user_name = args[1]
                network.get_user(user_name).get_now_playing()
                for key, value in refUsers.get().items():
                        if value["ID"] == str(ctx.author.id):
                            refUsers.child(key).update({"lastfm": user_name})
                embedVar = func.embedFunction("last.fm console", " ", {f"{str(ctx.author)}": [f"Your last.fm account {str(user_name)} has been added to your Discord profile.", True]})
                await ctx.channel.send(embed = embedVar)
            except:
                embedVar = func.embedFunction("last.fm console", " ", {f"{str(ctx.author)}": ["Invalid lastfm account name. No profile was added to your Discord profile.", True]})
                await ctx.channel.send(embed = embedVar)

        else:
            embedVar = func.embedFunction("Profile Error", " ", {"Command not found": [f"{' '.join(args)} isn't one of MarekBot's profile commands. Use ```/profile help``` to see a list of profile commands.", True]})
            await ctx.channel.send(embed = embedVar)

# /coc
@bot.command()
async def coc(ctx, *args):
    refUsers = db.reference("TODO_YOUR_FIREBASE_DIRECTORY")
    if not args:
        func.log(ctx, "coc")
        try:
            for key, value in refUsers.get().items():
                if value["ID"] == str(ctx.author.id) and value["Clash of Clans ID"] != "None":
                    user = _supercell_.user(value["Clash of Clans ID"])
                    embedVar = func.getUserInfo(user)
                    await ctx.channel.send(embed = embedVar)
                    return
            embedVar = func.embedFunction("Clash of Clans Error", " ", {f"{str(ctx.author)}": ["No Clash of Clans village added to your Discord profile. Add your village by typing: ```/coc add 2VRUUJYRO``` Choose your own village tag of course.", True]})
            await ctx.channel.send(embed = embedVar)
        except:
            embedVar = func.embedFunction("Clash of Clans Error", " ", {f"{str(ctx.author)}": ["Error: Invalid village tag. Change your village by typing: ```/coc add 2VRUUJYRO``` Choose your own village tag of course.", True]})
            await ctx.channel.send(embed = embedVar)

    else:
        if args[0] == "members":
            try: tag = args[1]
            except: tag = "2YGGPO9PO"
            members = _supercell_.clan_info(tag)
            embedVar = discord.Embed(title = members["name"], description="Members", color=0xbbb2e9)
            embedVar.set_thumbnail(url=members["badgeUrls"]["small"])
            for i in range(len(members["memberList"])):
                name = members["memberList"][i]["name"]
                role = members["memberList"][i]["role"]
                trophies = members["memberList"][i]["trophies"]
                embedVar.add_field(name=i+1, value=name, inline=True)
                embedVar.add_field(name="Role", value=role, inline=True)
                embedVar.add_field(name="Trophies", value=trophies, inline=True)
                if i % 6 == 0 and i != 0:
                    embedVar.set_footer(text = func.get_time("%d.%m.%Y %H:%M %Z"))
                    await ctx.channel.send(embed=embedVar)
                    embedVar = discord.Embed(title = members["name"], description="Members", color=0xbbb2e9)
                elif i == len(members["memberList"])-1:
                    embedVar.set_footer(text = func.get_time("%d.%m.%Y %H:%M %Z"))
                    await ctx.channel.send(embed=embedVar)
            func.log(ctx, "coc members")

        elif args[0] == "cw":
            try: tag = args[1]
            except: tag = "2YGGPO9PO"
            embedVar = func.coc_cw(tag)
            await ctx.channel.send(embed=embedVar)
            func.log(ctx, "coc cw")
            
        elif args[0] == "loot":
            embedVar = discord.Embed(title = "Clash of Cocks Loot", description = "http://clashofclansforecaster.com/", color = 0xbbb2e9)
            embedVar.set_thumbnail(url=stor.coc_img)
            await ctx.channel.send(embed = embedVar)
            func.log(ctx, "coc loot")

        elif args[0] == "attacks":
            try:
                try: tag = args[1]
                except: tag = "2YGGPO9PO"
                war = _supercell_.cw_info(tag)
                embedVar = discord.Embed(title = "Clan War Attacks", description = " ", color = 0xbbb2e9)
                embedVar.set_thumbnail(url=war["clan"]["badgeUrls"]["small"])
                for i in range(len(war["clan"]["members"])):
                    try:
                        if len(war["clan"]["members"][i]["attacks"]) == 2: attacks_completed = "attack(s) completed: " + str("```yaml\n2```")
                        else: attacks_completed = "attack(s) completed: " + str("```fix\n1```")
                        embedVar.add_field(name = war["clan"]["members"][i]["name"], value = attacks_completed, inline = False)
                    except(KeyError):
                        attacks_completed = "attack(s) completed: " + str("```diff\n- member hasn't attacked yet.```")
                        embedVar.add_field(name = war["clan"]["members"][i]["name"], value = attacks_completed, inline = False)
                    if i % 15 == 0 and i != 0:
                        embedVar.set_footer(text = func.get_time("%d.%m.%Y %H:%M %Z"))
                        await ctx.channel.send(embed=embedVar)
                        embedVar = discord.Embed(title = "Clan War Attacks", description = " ", color = 0xbbb2e9)
                    elif i == len(war["clan"]["members"])-1:
                        embedVar.set_footer(text = func.get_time("%d.%m.%Y %H:%M %Z"))
                        await ctx.channel.send(embed = embedVar)
                    func.log(ctx, "coc attacks")
            except:
                await ctx.channel.send("Clan currently not at war.")
                
        elif args[0] == "help":
            embedVar = func.embedFunction("Clash of Clans Commands", " ", stor.cmds_coc, stor.coc_img)
            await ctx.channel.send(embed = embedVar)
            func.log(ctx, "coc help")

        elif args[0] == "add":
            func.log(ctx, "coc add")
            try:
                tag = args[1]
                user = _supercell_.user(tag)
                _ = user["name"]
            except:
                embedVar = func.embedFunction("Clash of Clans Error", " ", {f"{str(ctx.author)}": ["Invalid village tag. No village was added to your Discord profile.", True]})
                await ctx.channel.send(embed = embedVar)
                return
            for key, value in refUsers.get().items():
                if value["Name"] == str(ctx.author):
                    refUsers.child(key).update({"Clash of Clans ID": tag})
            embedVar = func.embedFunction("Clash of Clans console", " ", {f"{str(ctx.author)}": [f"Your village {str(user['name'])} has been added to your Discord profile.", True]})
            await ctx.channel.send(embed = embedVar)
        else:
            embedVar = func.embedFunction("Clash of Clans Error", " ", {"Command not found": [f"{' '.join(args)} isn't one of MarekBot's Clash of Clans commands. Use ```/coc help``` to see a list of Spotify commands.", True]})
            await ctx.channel.send(embed = embedVar)

# /spotify
@bot.command(name = 'spotify', aliases = ['Spotify', 'spotipy', 'Spotipy', 's', 'S'])
async def spotify(ctx, cmd, *args):
    # Spotify command handling
    try:
        if cmd == "collage":
            try:
                file, embedVar, filepath = func.spotify_cmds(ctx, cmd, *args)
                await ctx.channel.send(file=file, embed = embedVar)
                import os
                os.remove(filepath)
            except:
                func.embedFunction("Spotify Error", " ", {"Command not found": [f"{cmd} isn't one of MarekBot's Spotify commands. Use ```/spotify help``` to see a list of Spotify commands.", True]})
        else:
            embedVar = func.spotify_cmds(ctx, cmd, *args)
            await ctx.channel.send(embed = embedVar)

    # User offline or other error
    except:
        embedVar = func.embedFunction("Spotify Error", "Common error: User offline or in locked listening session", img=stor.spotify_img, footer=func.get_time("%d.%m.%Y %H:%M %Z"))
        await ctx.channel.send(embed = embedVar)
    func.log(ctx, f"spotify {cmd}")

# /np
@bot.command(name = 'np', aliases = ['playing', 'nowplaying'])
async def np(ctx):
    refUsers = db.reference("TODO_YOUR_FIREBASE_DIRECTORY")
    try:
        for key, value in refUsers.get().items():
            if value["ID"] == str(ctx.author.id) and value["lastfm"] != "None":
                embedVar, extra_emoji = func.nowplaying(ctx, value["lastfm"])
                if embedVar == None:
                    await ctx.channel.send(embed = func.embedFunction("Now Playing Error", "User offline or in locked listening session", img=stor.spotify_img, footer=func.get_time("%d.%m.%Y %H:%M %Z")))
                    return
                emojis = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
                if extra_emoji != None: emojis.append(extra_emoji)
                message = await ctx.channel.send(embed = embedVar)
                for emoji in emojis:
                    await message.add_reaction(emoji)
                return
        embedVar = func.embedFunction("last.fm console", " ", {f"{str(ctx.author)}": ["No last.fm account added to your Discord profile. Add your account by typing: ```/profile lastfm xelemir``` Choose your own last.fm user name of course.", True]})
        await ctx.channel.send(embed = embedVar)
    except:
        embedVar = func.embedFunction("last.fm console", " ", {f"{str(ctx.author)}": ["Error: Invalid last.fm user name.", True]})
        await ctx.channel.send(embed = embedVar)
    func.log(ctx, "np")
    
# /jkg
@bot.command(name = 'jkg', aliases = ['JKG', 'Jkg', 'Marek', 'marek'])
async def jkg(ctx, *args):
    if args:
        try:
            quotes_name = {}
            for quote, url in stor.jkg_quotes.items():
                if ' '.join(args) in quote: quotes_name[quote] = url
            quote, url = random.choice(list(quotes_name.items()))
            if func.jkg_filter(ctx,bot) == True and any(word in quote for word in stor.jkg_filter): return
            func.log(ctx, "jkg " + ''.join(args))
        except:
            return
    else:
        while True:
            quote, url = random.choice(list(stor.jkg_quotes.items()))
            if func.jkg_filter(ctx,bot) == True and any(word in quote for word in stor.jkg_filter): continue
            break
        func.log(ctx, "jkg")

    embedVar = discord.Embed(title = "JKG Quote", description = quote, color = 0xbbb2e9)
    if type(url) == list: embedVar.set_thumbnail(url = random.choice(url))
    elif url != None: embedVar.set_thumbnail(url = url)
    await ctx.channel.send(embed = embedVar)

# /GeoGuesser
@bot.command(name = 'GeoGuesser', aliases = ['g', 'geo'])
async def GeoGuesser(ctx, *args):
    rndm_country, capital = random.choice(list(stor.countries.items()))

    embedVar = discord.Embed(title = "Geo Guesser", description = " ", color = 0xbbb2e9)
    embedVar.add_field(name = "Guess this country's capital:", value = rndm_country, inline = False)
    await ctx.channel.send(embed = embedVar)

    def check(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            return m.content
    msg = await bot.wait_for("message", check=check)

    if capital in msg.content:
        judgement = "Yes, " + capital + " is the capital of " + rndm_country + "."
        func.log(ctx, "capital", geoWon = 1)
    else:
        judgement = "Nope, " + msg.content + " is not the capital of " + rndm_country + ". The correct answer is " + capital + "."
        func.log(ctx, "capital", geoLost = 1)

    embedVarNew = discord.Embed(title = "Geo Guesser", description = judgement, color = 0xbbb2e9)
    await ctx.channel.send(embed = embedVarNew)

# General messages screening
@bot.event
async def on_message(ctx):
    try:
        if ctx.author.id == bot_id:
            return

        # Detect words in messages
        elif any(word in ctx.content for word in stor.charliE):
            await ctx.channel.send("It's Charli, without the E you dumb bitch.", tts = True)
        elif any(word in ctx.content for word in stor.dababy):
            await ctx.channel.send("Get in DaBed. TIME TO SEX.", tts = True)
        elif any(word in ctx.content for word in stor.amogus):
            await ctx.channel.send("sus")
        elif any(word in ctx.content for word in stor.amongus):
            await ctx.channel.send("Ich korrigiere, es heißt Amogus!")

        # Filter words
        if any(word in ctx.content for word in stor.filter_list):
            func.log(ctx, f"Word violation ({ctx.content})")
            await ctx.delete()
            channel = await ctx.author.create_dm()
            await channel.send(f"Your message in {ctx.channel} on {ctx.guild} contained a word which goes against this bot's code of conduct. Furthermore this incident (including the used words) was logged. Never do this again.")
            response = f"Warning: {ctx.author.mention}. Do not use this word again."
            msg_by_bot = await ctx.channel.send(response, tts = True)
            await asyncio.sleep(10)
            await msg_by_bot.delete()
        await bot.process_commands(ctx)
    except:
        return

bot.run(bot_token)
