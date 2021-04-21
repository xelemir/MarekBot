import discord
from discord.ext import commands
import random

bot = commands.Bot(command_prefix="/")
client = discord.Client()

# Discord API token
TOKEN = "<xyz>"

# Marek quotes
quotes = []
quotes.append("Oh mein Gott ich bin so geil!")
quotes.append("Mein Modegeschmack ist objektiv betrachtet schon der Beste.")
quotes.append("Junge, bist du eigentlich dumm!?")
quotes.append("Joe Biden!")
quotes.append("SHUT UP YOU CUNT, ICH MUSS AUF RATHAUS 10 RUSHEN!")

# Connected to bot
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

# /marekhelp
@bot.command()
async def marekhelp(ctx):
    await ctx.send("Nein du Lappen, ich helf' dir nicht.")
    await ctx.send("----")
    await ctx.send("'/marek' für Marek Quotes.")
    await ctx.send("'/wittmanwinter' für Mareks Meinung zu Witti.")
    await ctx.send("'/mareksearch + <Suchbegriff>' für eine Google Suche mit Marek.")
    await ctx.send("----")

# /marek
@bot.command()
async def marek(ctx):
    await ctx.send(random.choice(quotes))

# /wittmanwinter
@bot.command()
async def wittmanwinter(ctx):
    await ctx.send("OHHH, sie ist blond!")

# /mareksearch
@bot.command()
async def mareksearch(ctx, query):
    await ctx.send("https://google.com/search?q=" + query)

# /dababy
@bot.command()
async def dababy(ctx):
    embedVar = discord.Embed(title="DaBaby", description="Leezzz gooo", color=0xB42626)
    embedVar.add_field(name="<NSFW_Reddit_Links>", value="<NSFW>", inline=False)
    await ctx.send(embed=embedVar)

bot.run(TOKEN)