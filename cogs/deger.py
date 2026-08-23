import discord
from discord.ext import commands
import random
import re

class DegerSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ant_sayac = {}

    def miktar_parse(self, miktar_str: str) -> int:
        sayi = re.findall(r'\d+', miktar_str)
        return int(sayi[0]) if sayi else 0

    # --- TWEET KOMUTU (!tweet) ---
    @commands.command(aliases=["tw"])
    async def tweet(self, ctx, *, icerik: str = None):
        if "twitter" not in ctx.channel.name.lower():
            await ctx.send("❌ Bu komut sadece **#twitter** kanalında kullanılabilir!")
            return

        if not icerik:
            await ctx.send("⚠️ Kullanım: `!tweet Atılacak mesaj`")
            return

        embed = discord.Embed(description=f"{icerik}", color=0x000000)
        embed.set_author(name=f"{ctx.author.display_name} (@{ctx.author.name})", icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text="🐦 Twitter / X for League", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
        
        try:
            await ctx.message.delete()
        except:
            pass
            
        await ctx.send(embed=embed)

    # --- ANTRENMAN (!ant) ---
    @commands.command()
    async def ant(self, ctx):
        if "antrenman" not in ctx.channel.name.lower():
            await ctx.send("❌ Bu komut sadece **#antrenman** kanalında kullanılabilir!")
            return

        user_id = ctx.author.id
        mevcut = self.ant_sayac.get(user_id, 0) + 1
        
        embed = discord.Embed(color=0x000000)
        if mevcut >= 10:
            self.ant_sayac[user_id] = 0
            embed.description = (
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **10/10**\n"
                f"🎯 **Tebrikler! 10/10 antrenman tamamlandı. `#değer-iste` kanalından +3M€ talebinde bulunabilirsiniz!**"
            )
        else:
            self.ant_sayac[user_id] = mevcut
            embed.description = (
                f"🏋️ **Antrenman yapıldı!**\n\n"
                f"📊 Antrenman: **{mevcut}/10**\n"
                f"🎯 **10/10 olduğunda mevcut değere +3M€**"
            )
        await ctx.send(embed=embed)

    # --- PENALTI (!pen) ---
    @commands.command()
    async def pen(self, ctx):
        if "penalt" not in ctx.channel.name.lower():
            await ctx.send("❌ Bu komut sadece **#penaltı** kanalında kullanılabilir!")
            return

        gol_mu = random.choice([True, False])
        embed = discord.Embed(color=0x000000)
        
        if gol_mu:
            embed.description = f"⚽ **PENALTI**\n\n🎯 Vuruş yapıldı!\n🥅 **GOOOOL! ⚽🔥**"
        else:
            embed.description = f"⚽ **PENALTI**\n\n🎯 Vuruş yapıldı!\n🧤 Kaleci kurtardı!\n\n❌ **PENALTI KAÇTI!**"
            
        await ctx.send(embed=embed)

    # --- KAYIT (!kayit @kullanıcı Format) ---
    @commands.command(aliases=["kayıt"])
    async def kayit(self, ctx, member: discord.Member = None, *, yeni_isim: str = None):
        if not (ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")):
            await ctx.send("❌ Bu komutu sadece yetkililer kullanabilir.")
            return

        if not member or not yeni_isim:
            await ctx.send("⚠️ Kullanım: `!kayit @kullanıcı V.Osimhen | 🇳🇬 | SNT | 1M`")
            return

        try:
            await member.edit(nick=yeni_isim)
            embed = discord.Embed(color=0x000000)
            embed.description = f"✅ {member.mention} başarıyla kaydedildi!\n**Yeni İsim:** `{yeni_isim}`"
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("❌ Kullanıcının ismi değiştirilemedi. Botun rol yetkisi kullanıcıdan üstte olmalı.")

    # --- DEĞER VERME (!dver) ---
    @commands.command()
    async def dver(self, ctx, member: discord.Member = None, miktar: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not miktar:
            await ctx.send("⚠️ Kullanım: `!dver @Kullanıcı 5M`")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        eklenen_val = self.miktar_parse(miktar)
        yeni_val = eski_val + eklenen_val

        # İsmi otomatik değiştirme işlemi
        yeni_nick = re.sub(r'\b\d+M\b', f"{yeni_val}M", member.display_name)
        try:
            await member.edit(nick=yeni_nick)
        except:
            pass

        embed = discord.Embed(color=0x000000)
        embed.description = (
            f"✅ **DEĞER VERİLDİ**\n\n"
            f"👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➕ **Eklenen:** {eklenen_val}M€\n"
            f"📈 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

    # --- DEĞER SİLME (!dsil) ---
    @commands.command()
    async def dsil(self, ctx, member: discord.Member = None, miktar: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not miktar:
            await ctx.send("⚠️ Kullanım: `!dsil @Kullanıcı 5M`")
            return

        mevcut_match = re.search(r'(\d+)M', member.display_name)
        eski_val = int(mevcut_match.group(1)) if mevcut_match else 1
        
        silinen_val = self.miktar_parse(miktar)
        yeni_val = max(0, eski_val - silinen_val)

        # İsmi otomatik değiştirme işlemi
        yeni_nick = re.sub(r'\b\d+M\b', f"{yeni_val}M", member.display_name)
        try:
            await member.edit(nick=yeni_nick)
        except:
            pass

        embed = discord.Embed(color=0x000000)
        embed.description = (
            f"🔻 **DEĞER SİLİNDİ**\n\n"
            f"👤 **Oyuncu:** {member.mention}\n"
            f"💰 **Eski değer:** {eski_val}M€\n"
            f"➖ **Silinen:** {silinen_val}M€\n"
            f"📉 **Yeni değer:** {yeni_val}M€"
        )
        await ctx.send(embed=embed)

    # --- KAP BİLDİRİMİ (!kap) ---
    @commands.command()
    async def kap(self, ctx, *, icerik: str = None):
        if not icerik:
            ornek = (
                "⚠️ **Kullanım Şekli:**\n"
                "`!kap` yazıp altına şu formatta bilgileri doldurun:\n\n"
                "Oyuncu Adı: Victor Osimhen\n"
                "Mevki: SNT\n"
                "Eski Kulüp: Napoli\n"
                "Yeni Kulüp: Galatasaray\n"
                "Piyasa Değeri: 75M€\n"
                "Maaş: 6M€\n"
                "Sözleşme Süresi: 1 Yıl\n"
                "Forma Numarası: 45\n"
                "Bonservis: 10M€\n"
                "Şartlar: Zorunlu Satın Alma\n"
                "Özel Maddeler: - \n"
                "Durum: Transferli"
            )
            await ctx.send(ornek)
            return

        embed = discord.Embed(
            title="⚽ OYUNCU KAYIT FORMU (KAP)",
            description=f"```\n{icerik}\n```",
            color=0x000000
        )
        embed.set_footer(text="Tendo League Official Transfer KAP")
        await ctx.message.delete()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))
