import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} lig sistemiyle aktif!')

initial_extensions = [
    'cogs.kayit',
    'cogs.kadro',
    'cogs.sirket',
    'cogs.moderasyon',
    'cogs.mac',
    'cogs.ticket',
    'cogs.deger'
]

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'{extension} modülü yüklendi.')
        except Exception as e:
            print(f'{extension} yüklenirken hata oluştu: {e}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
