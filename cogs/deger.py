import discord
from discord.ext import commands
import random
import re

class DegerSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antrenman_sayac = {}

    def miktar_parse(self, miktar_str: str) -> int:
        sayi = re.findall(r'\d+', miktar_str)
        return int(sayi[0]) if sayi else 0

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

    @commands.command()
    async def dver(self, ctx, member: discord.Member, miktar: str):
        # Yetki Kontrolü (Yönetici veya Değer Yetkilisi rolü olanlar)
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir!")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        eklenen_val = self.miktar_parse(miktar)
        yeni_val = eski_val + eklenen_val

        embed = discord.Embed(title="✅ DEĞER VERİLDİ", color=discord.Color.green())
        embed.description = (
            f"\n👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➕ **Eklenen:** {eklenen_val}M€\n"
            f"📈 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def dsil(self, ctx, member: discord.Member, miktar: str):
        # Yetki Kontrolü
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir!")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        silinen_val = self.miktar_parse(miktar)
        yeni_val = max(0, eski_val - silinen_val)

        embed = discord.Embed(title="🔻 DEĞER SİLİNDİ / DÜŞÜRÜLDÜ", color=discord.Color.red())
        embed.description = (
            f"\n👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➖ **Silinen:** {silinen_val}M€\n"
            f"📉 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))

