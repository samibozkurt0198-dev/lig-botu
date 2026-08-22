import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} online!')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(os.getenv("DISCORD_TOKEN"))
