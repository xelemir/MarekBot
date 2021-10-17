import _storage_
import _functions_
import discord
from discord.ext import commands
import asyncio
import cpuinfo
import random
import psutil
import socket
import _supercell_
from datetime import datetime
from pytz import timezone

bot = commands.Bot(command_prefix = "/")
client = discord.Client()

# user id
admin_id = ADMINS_DC_USER_ID
bot_id = THIS_BOTS_DC_USER_ID
bot_token = YOUR_BOT_TOKEN

def embedFunction(title, description, embedDict, img=None):
    embedVar = discord.Embed(title = title, description = description, color = 0xbbb2e9)
    if img != None: embedVar.set_thumbnail(url = img)
    for key in embedDict: embedVar.add_field(name = key, value = embedDict[key][0], inline = embedDict[key][1])
    return embedVar

def get_time(format):
    now_time = datetime.now(timezone('Europe/Berlin'))
    date_time = now_time.strftime(format)
    return date_time

def log(ctx, cmd):
    if not ctx.author.id == admin_id:
        open("/home/logfile.txt", "a").write(get_time("[%d.%m.%Y %H:%M %Z]") + " /" + cmd + " used by " + str(ctx.author) + " in " + str(ctx.channel) + " on " + str(ctx.guild) + ".\n")
        open("/home/logfile.txt", "a").close()

def log_permission(ctx, cmd):
    if not ctx.author.id == admin_id:
        open("/home/logfile.txt", "a").write(get_time("[%d.%m.%Y %H:%M %Z]") + " /" + cmd + " attempted by " + str(ctx.author) + " in " + str(ctx.channel) + " on " + str(ctx.guild) + ". Permissions missing.\n")
        open("/home/logfile.txt", "a").close()

# Connected to bot
@bot.event
async def on_ready():
    print("Bot connected.")

# /marekhelp
@bot.command()
async def marekhelp(ctx):
    embedDict = {"Random marek quote:":["```/marek```", False],
                 "Random JKG quote; special thanks to Anton:":["```/jkg```", False],
                 "List of Clash of Clans commands:":["```/cochelp```", False],
                 "List of Spotify commands:":["```/spotifyhelp```", False],
                 "System info of bot's host machine:":["```/system```", False],
    embedVar = embedFunction("Marek commands", "Nein du Lappen, ich helf' dir nicht.", embedDict)
    await ctx.channel.send(embed = embedVar)
    log(ctx, "marekhelp")

# /cochelp Clash of Clans
@bot.command()
async def cochelp(ctx):
    embedDict = {"Info on the clan members:":["```/coc members```", False],
                 "Info on the current clan war:":["```/coc cw```", False],
                 "List of members who haven't attacked in the current clan war yet:":["```/coc attacks```", False],
                 "Clash of Clans loot:":["```/loot```", False],
                 "Important:":["Add clan id (without '#') after command to target a specific clan. Leave empty to target the DaBaByClan by default.", False]}
    embedVar = embedFunction("Clash of Clans commands", " ", embedDict, _storage_.coc_img)
    await ctx.channel.send(embed = embedVar)
    log(ctx, "cochelp")

# /spotifyhelp
@bot.command()
async def spotifyhelp(ctx):
    embedDict = {"Skip current track:":["```/spotify skip```", False],
                 "Pause current track:":["```/spotify pause```", False],
                 "Play current track:":["```/spotify play```", False],
    embedVar = embedFunction("Spotify commands", "Note: These commands can only be used by specific users.", embedDict)
    await ctx.channel.send(embed = embedVar)
    log(ctx, "spotifyhelp")

# /marek
@bot.command()
async def marek(ctx):
    await ctx.send(random.choice(_storage_.quotes))
    log(ctx, "marek")

# /system
@bot.command(name = 'system', aliases = ['sys', 'Sys', 'System'])
async def system(ctx):
    embedVar = discord.Embed(title = "System info", description = " ", color = 0xbbb2e9)
    embedVar.add_field(name = "Machine name:", value = "```running locally on {}```".format(socket.gethostname()), inline = False)
    embedVar.add_field(name = "CPU:", value = "```{}```".format(cpuinfo.get_cpu_info()["brand_raw"]), inline = False)
    import datetime
    import time
    embedVar.add_field(name = "Uptime:", value = "```{}```".format(str(datetime.timedelta(seconds = time.time() - psutil.boot_time()))), inline = False)
    await ctx.channel.send(embed = embedVar)
    log(ctx, "system")

# /loot
@bot.command()
async def loot(ctx):
    embedVar = discord.Embed(title = "Clash of Cocks Loot", description = "http://clashofclansforecaster.com/", color = 0xbbb2e9)
    await ctx.channel.send(embed = embedVar)
    log(ctx, "loot")

# /coc
@bot.command()
async def coc(ctx, cmd, clan_id = "2YGGPO9PO"):

    if cmd == "members":
        members = _supercell_.clan_info(clan_id)
        embedVar = discord.Embed(title = "DaBaby Clan", description = "Members", color = 0xbbb2e9)
        embedVar.set_thumbnail(url = members["badgeUrls"]["small"])
        for i in range(len(members["memberList"])):
            name = members["memberList"][i]["name"]
            role = members["memberList"][i]["role"]
            trophies = members["memberList"][i]["trophies"]
            embedVar.add_field(name = i + 1, value = name, inline = True)
            embedVar.add_field(name = "Role", value = role, inline = True)
            embedVar.add_field(name = "Trophies", value = trophies, inline = True)
            if i % 6 == 0 and i != 0:
                await ctx.channel.send(embed = embedVar)
                embedVar = discord.Embed(title = "DaBaby Clan", description = "Members", color = 0xbbb2e9)
            elif i == len(members["memberList"])-1: await ctx.channel.send(embed = embedVar)
            log(ctx, "coc members")

    elif cmd == "cw":
        try:
            embedVar = _functions_.coc_cw(clan_id)
            await ctx.channel.send(embed=embedVar)
            log(ctx, "coc cw")
        except:
            await ctx.send("Clan currently not at war.")

    elif cmd == "attacks":
        try:
            war = _supercell_.cw_info(clan_id)
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
                    await ctx.channel.send(embed=embedVar)
                    embedVar = discord.Embed(title = "Clan War Attacks", description = " ", color = 0xbbb2e9)
                elif i == len(war["clan"]["members"])-1: await ctx.channel.send(embed = embedVar)
                log(ctx, "coc attacks")

        except:
            await ctx.send("Clan currently not at war.")

# /spotify
@bot.command(name = 'spotify', aliases = ['Spotify', 'spotipy', 'Spotipy', 's', 'S'])
async def spotify(ctx,cmd):
    if ctx.author.id == admin_id:

        # Spotify command handling
        try:
            embedVar = _functions_.spotify_cmds(cmd)
            await ctx.channel.send(embed = embedVar)

        # User offline or other error
        except:
            embedVar = discord.Embed(title = "User is currently offline.", description = " ", color = 0xbbb2e9)
            embedVar.set_thumbnail(url = _storage_.offline_img)
            await ctx.channel.send(embed = embedVar)
    
    # No permission Spotify
    else:
        embedVar = discord.Embed(title = "You do not have the permission to use this command.", description = "Your attempt was logged.", color = 0xbbb2e9)
        embedVar.set_thumbnail(url = _storage_.locked_img)
        await ctx.channel.send(embed = embedVar)
        log_permission(ctx, "spotify")

# /jkg
@bot.command(name = 'jkg', aliases = ['JKG', 'Jkg'])
async def jkg(ctx):
    quote = random.choice(_storage_.jkg_quotes)
    embedVar = discord.Embed(title = "JKG Quotes", description = quote, color=0xbbb2e9)
    embedVar.set_thumbnail(url = _functions_.jkg_img(quote))
    await ctx.channel.send(embed = embedVar)
    log(ctx, "jkg")

# General messages screening
@bot.event
async def on_message(message):
    try:
        if message.author.id == bot_id:
            return
        
        # Detect words in messages
        elif any(word in message.content for word in _storage_.amogus):
            await message.channel.send("sus")
            print(message.author, "in", message.channel, "on", message.guild, "triggered Amogus")
        elif any(word in message.content for word in _storage_.amongus):
            await message.channel.send("Ich korrigiere, es heißt Amogus!")
            print(message.author, "in", message.channel, "on", message.guild, "couldn't spell Amogus")

        # Filter words
        if any(word in message.content for word in _storage_.filter_list):
            await message.delete()
            channel = await message.author.create_dm()
            await channel.send(random.choice(_storage_.insult))
            response = "Never try this again!"
            msg_by_bot = await message.channel.send(response, tts = True)
            await asyncio.sleep(10)
            await msg_by_bot.delete()
            print(message.author, "in", message.channel, "on", message.guild, "got censored for saying '", message.content, "' ,", get_time("%d.%m.%Y at %H:%M %Z."))
        await bot.process_commands(message)
    except:
        return

bot.run(bot_token)
