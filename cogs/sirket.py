import discord
from discord.ext import commands

# Basit bakiye veritabanı
bakiye_db = {}

class Sirket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- ŞİRKET SATIN ALMA (.sirketal <Şirket Adı>) ---
    @commands.command(name="sirketal")
    async def sirketal(self, ctx, *, sirket_adi: str = None):
        if not sirket_adi:
            await ctx.send("⚠️ **Kullanım:** `.sirketal <Şirket Adı>`\nÖrnek: `.sirketal Tendo Sport A.Ş.`")
            return

        user_id = ctx.author.id
        bakiye_db[user_id] = bakiye_db.get(user_id, 1000000) # Varsayılan başlangıç bakiyesi: 1.000.000$

        fiyat = 500000
        if bakiye_db[user_id] >= fiyat:
            bakiye_db[user_id] -= fiyat
            embed = discord.Embed(
                title="🏢 Şirket Satın Alındı!",
                description=(
                    f"🎉 **{ctx.author.mention}**, **{sirket_adi}** şirketini kurdu!\n\n"
                    f"💵 **Ödenen Tutar:** `{fiyat:,}$`\n"
                    f"💰 **Kalan Bakiye:** `{bakiye_db[user_id]:,}$`"
                ),
                color=0x000000
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"❌ Şirket almak için yeterli bakiyeniz yok!\n\n💵 **Gerekli:** `{fiyat:,}$` | 💰 **Mevcut:** `{bakiye_db[user_id]:,}$`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    # --- SPONSOR GELİRİ TOPLAMA (.sponsorgeliri) ---
    @commands.command(name="sponsorgeliri", aliases=["sponsor"])
    async def sponsorgeliri(self, ctx):
        user_id = ctx.author.id
        gelir = 150000
        bakiye_db[user_id] = bakiye_db.get(user_id, 0) + gelir

        embed = discord.Embed(
            title="💼 Sponsor Geliri Aktarıldı",
            description=(
                f"📈 **{ctx.author.mention}**, sponsor anlaşması ödemesini aldı!\n\n"
                f"💵 **Kazanılan:** `+{gelir:,}$`\n"
                f"💰 **Güncel Bakiye:** `{bakiye_db[user_id]:,}$`"
            ),
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    # --- BAKİYE SORGULAMA (.bakiye) ---
    @commands.command(name="bakiye", aliases=["para", "wallet"])
    async def bakiye(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        user_bakiye = bakiye_db.get(target.id, 1000000)

        embed = discord.Embed(
            title="💳 Hesap Bakiyesi",
            description=f"👤 **Kullanıcı:** {target.mention}\n💰 **Toplam Bakiye:** `{user_bakiye:,}$`",
            color=0x000000
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sirket(bot))

