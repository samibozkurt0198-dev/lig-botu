import discord
from discord.ext import commands

# Basit veri tutucu
bakiye_db = {}

class Sirket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sirketal(self, ctx, sirket_adi: str):
        user_id = ctx.author.id
        bakiye_db[user_id] = bakiye_db.get(user_id, 1000000) # Başlangıç bakiyesi
        
        if bakiye_db[user_id] >= 500000:
            bakiye_db[user_id] -= 500000
            await ctx.send(f" **{sirket_adi}** şirketini 500.000$ karşılığında satın aldınız! Kalan Bakiye: {bakiye_db[user_id]}$")
        else:
            await ctx.send(" Şirket almak için yeterli bakiyeniz yok! (Gerekli: 500.000$)")

    @commands.command()
    async def sponsorgeliri(self, ctx):
        user_id = ctx.author.id
        gelir = 150000
        bakiye_db[user_id] = bakiye_db.get(user_id, 0) + gelir
        await ctx.send(f" Sponsor geliriniz olan **{gelir}$** hesabınıza aktarıldı! Güncel Bakiye: {bakiye_db[user_id]}$")

async def setup(bot):
    await bot.add_cog(Sirket(bot))

