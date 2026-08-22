import discord
from discord.ext import commands
import random

class DegerSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antrenman_sayac = {} # {user_id: count}

    # --- ANTRENMAN KOMUTU (.ant) ---
    @commands.command(aliases=["antrenman"])
    async def ant(self, ctx):
        user_id = ctx.author.id
        mevcut = self.antrenman_sayac.get(user_id, 0) + 1
        
        if mevcut >= 10:
            self.antrenman_sayac[user_id] = 0
            await ctx.send(
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **10/10**\n"
                f"🎯 **Tebrikler! 10/10 antrenman tamamlandı. `#değer-iste` kanalından +3M€ talebinde bulunabilirsiniz!**"
            )
        else:
            self.antrenman_sayac[user_id] = mevcut
            await ctx.send(
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **{mevcut}/10**\n"
                f"🎯 10/10 olduğunda mevcut değerine **+3M€** eklenecek."
            )

    # --- PENALTI KOMUTU (.pen) ---
    @commands.command(aliases=["penalti"])
    async def pen(self, ctx):
        sonuclar = [
            ("🎯 Vuruş yapıldı!\n🧤 Kaleci kurtardı!\n\n❌ **PENALTI KAÇTI!**", False),
            ("🎯 Vuruş yapıldı!\n🥅 **GOOOOL! ⚽🔥**", True)
        ]
        metin, gol_mu = random.choice(sonuclar)
        
        if gol_mu:
            metin += "\n\n✨ **+2M€** değer kazanmak için `#değer-iste` kanalına bildirin!"
            
        await ctx.send(f"⚽ **PENALTI**\n\n{metin}")

    # --- DEĞER VERME KOMUTU (.dver @kullanici miktar) ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dver(self, ctx, member: discord.Member, miktar: str):
        # Takma addan mevcut değeri çekme veya varsayılan belirleme
        mevcut_isim = member.display_name
        
        embed = discord.Embed(
            title="✅ DEĞER VERİLDİ",
            color=discord.Color.green()
        )
        embed.description = (
            f"\n👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** 1M€\n"
            f"➕ **Eklenen:** {miktar}\n"
            f"📈 **Yeni değer:** {miktar}"
        )
        await ctx.send(embed=embed)

    # --- NICKNAME / İSİM DEĞİŞTİRME (.dsil / .takmaad) ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dsil(self, ctx, member: discord.Member, yeni_isim: str):
        await member.edit(nick=yeni_isim)
        await ctx.send(f"✅ **{member.name}**'in takma adı **{yeni_isim}** olarak değiştirildi!")

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))
