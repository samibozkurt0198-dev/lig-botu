import discord
from discord.ext import commands
import random
import asyncio

class Mac(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def antrenman(self, ctx):
        artiss = random.randint(1, 5)
        await ctx.send(f"⚽ **{ctx.author.display_name}** antrenmanı tamamladı! Oyuncu gelişimi: **+{artiss} Form**")

    @commands.command()
    async def penalti(self, ctx):
        sonuclar = ["⚽ GOOOL! Şut ağlarla buluştu!", "❌ KAÇTI! Şut dışarı gitti!", "🧤 KURTARILDI! Kaleci gole izin vermedi!"]
        secim = random.choice(sonuclar)
        await ctx.send(f"🥅 **{ctx.author.display_name}** penaltı atışını kullandı...\nResult: **{secim}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def macbaslat(self, ctx, takim1: str, takim2: str):
        await ctx.send(f"🏟️ **{takim1} vs {takim2}** maçı başladı!")
        await asyncio.sleep(3)
        
        gol1 = random.randint(0, 4)
        gol2 = random.randint(0, 4)
        
        embed = discord.Embed(title="⚡ Maç Sonucu", color=discord.Color.green())
        embed.add_field(name=takim1, value=str(gol1), inline=True)
        embed.add_field(name="VS", value="-", inline=True)
        embed.add_field(name=takim2, value=str(gol2), inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mac(bot))
