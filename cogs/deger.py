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

    # --- TWEET KOMUTU (!tweet / .tweet mesaj) ---
    @commands.command(aliases=["tw"])
    async def tweet(self, ctx, *, icerik: str = None):
        if not icerik:
            await ctx.send("⚠️ Kullanım: `.tweet Atılacak tweet içeriği`")
            return

        embed = discord.Embed(
            description=f"{icerik}",
            color=0x000000 # Siyah renk
        )
        embed.set_author(
            name=f"{ctx.author.display_name} (@{ctx.author.name})",
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text="🐦 Twitter / X for League", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
        
        await ctx.message.delete() # Komut mesajını temizler
        await ctx.send(embed=embed)

    # --- ANTRENMAN (!ant / .ant) ---
    @commands.command(aliases=["antrenman"])
    async def ant(self, ctx):
        user_id = ctx.author.id
        mevcut = self.antrenman_sayac.get(user_id, 0) + 1
        
        embed = discord.Embed(color=0x000000) # Siyah kutu
        if mevcut >= 10:
            self.antrenman_sayac[user_id] = 0
            embed.description = (
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **10/10**\n"
                f"🎯 **Tebrikler! 10/10 antrenman tamamlandı. `#değer-iste` kanalından +3M€ talebinde bulunabilirsiniz!**"
            )
        else:
            self.antrenman_sayac[user_id] = mevcut
            embed.description = (
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **{mevcut}/10**\n"
                f"🎯 **10/10 olduğunda mevcut değere +3M€**"
            )
        await ctx.send(embed=embed)

    # --- PENALTI (!pen / .pen) ---
    @commands.command(aliases=["penalti"])
    async def pen(self, ctx):
        gol_mu = random.choice([True, False])
        embed = discord.Embed(color=0x000000)
        
        if gol_mu:
            embed.description = (
                f"⚽ **PENALTI**\n\n"
                f"🎯 Vuruş yapıldı!\n"
                f"🥅 **GOOOOL! ⚽🔥**"
            )
        else:
            embed.description = (
                f"⚽ **PENALTI**\n\n"
                f"🎯 Vuruş yapıldı!\n"
                f"🧤 Kaleci kurtardı!\n\n"
                f"❌ **PENALTI KAÇTI!**"
            )
        await ctx.send(embed=embed)

    # --- DEĞER VERME (!dver / .dver) ---
    @commands.command()
    async def dver(self, ctx, member: discord.Member = None, miktar: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not miktar:
            await ctx.send("⚠️ Doğru Kullanım: `.dver @Kullanıcı 5M`")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        eklenen_val = self.miktar_parse(miktar)
        yeni_val = eski_val + eklenen_val

        embed = discord.Embed(color=0x000000)
        embed.description = (
            f"✅ **DEĞER VERİLDİ**\n\n"
            f"👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➕ **Eklenen:** {eklenen_val}M€\n"
            f"📈 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

    # --- DEĞER SİLME (!dsil / .dsil) ---
    @commands.command()
    async def dsil(self, ctx, member: discord.Member = None, miktar: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not miktar:
            await ctx.send("⚠️ Doğru Kullanım: `.dsil @Kullanıcı 5M`")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        silinen_val = self.miktar_parse(miktar)
        yeni_val = max(0, eski_val - silinen_val)

        embed = discord.Embed(color=0x000000)
        embed.description = (
            f"🔻 **DEĞER SİLİNDİ**\n\n"
            f"👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➖ **Silinen:** {silinen_val}M€\n"
            f"📉 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))

