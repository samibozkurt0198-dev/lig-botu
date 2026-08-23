import discord
from discord.ext import commands
import random
import re

# --- KAP FORMU MODAL ---
class KapFormuModal(discord.ui.Modal, title="📝 Transfer Teklifi Formu"):
    takim = discord.ui.TextInput(
        label="Takım (Geldiği / Gittiği)",
        placeholder="Örn: Barcelona / Real Madrid",
        required=True
    )
    maas = discord.ui.TextInput(
        label="Maaş",
        placeholder="Örn: 500k / hafta",
        required=True
    )
    imza_parasi = discord.ui.TextInput(
        label="İmza Parası",
        placeholder="Örn: 1m",
        required=True
    )
    bonservis = discord.ui.TextInput(
        label="Bonservis",
        placeholder="Örn: 5m",
        required=True
    )
    ek_madde = discord.ui.TextInput(
        label="Ek Madde (opsiyonel)",
        placeholder="Opsiyonel maddeler veya detaylar...",
        style=discord.TextStyle.paragraph,
        required=False
    )

    def __init__(self, hedef_oyuncu: discord.Member):
        super().__init__()
        self.hedef_oyuncu = hedef_oyuncu

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚽ TRANSFER KAP BİLDİRİMİ",
            color=0x000000
        )
        embed.description = (
            f"👤 **Transfer Edilen Oyuncu:** {self.hedef_oyuncu.mention}\n"
            f"👔 **İşlemi Yapan TD:** {interaction.user.mention}\n\n"
            f"🏛️ **Takım (Geldiği / Gittiği):** {self.takim.value}\n"
            f"💰 **Maaş:** {self.maas.value}\n"
            f"✍️ **İmza Parası:** {self.imza_parasi.value}\n"
            f"💵 **Bonservis:** {self.bonservis.value}\n"
            f"📌 **Ek Madde:** {self.ek_madde.value if self.ek_madde.value else 'Yok'}"
        )
        embed.set_footer(text="Tendo League Resmi KAP Bildirimi")
        await interaction.response.send_message(embed=embed)


# --- KAP BUTONU ---
class KapButonView(discord.ui.View):
    def __init__(self, sahibi: discord.Member, hedef_oyuncu: discord.Member):
        super().__init__(timeout=120)
        self.sahibi = sahibi
        self.hedef_oyuncu = hedef_oyuncu

    @discord.ui.button(label="📝 Teklif Formunu Doldur", style=discord.ButtonStyle.primary)
    async def formu_ac(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.sahibi.id:
            await interaction.response.send_message("❌ Bu butonu sadece komutu yazan teknik direktör kullanabilir!", ephemeral=True)
            return

        modal = KapFormuModal(hedef_oyuncu=self.hedef_oyuncu)
        await interaction.response.send_modal(modal)


# --- COG SINIFI ---
class DegerSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ant_sayac = {}

    def miktar_parse(self, miktar_str: str) -> int:
        sayi = re.findall(r'\d+', miktar_str)
        return int(sayi[0]) if sayi else 0

    # --- KAP BİLDİRİMİ (!kap @Oyuncu) ---
    @commands.command()
    async def kap(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("⚠️ **Kullanım:** `!kap @oyuncu`")
            return

        embed = discord.Embed(
            title="📄 Transfer Teklifi Hazırlanıyor",
            description=(
                f"{ctx.author.mention}, {member.mention} için transfer teklifi oluşturmak üzeresin.\n\n"
                f"Devam etmek için aşağıdaki butona bas ve formu doldur.\n\n"
                f"*(Bu butonu sadece sen kullanabilirsin.)*"
            ),
            color=0x000000
        )
        view = KapButonView(sahibi=ctx.author, hedef_oyuncu=member)
        await ctx.send(embed=embed, view=view)

    # --- TEKNİK DİREKTÖR KAYIT (!ktd @kullanıcı @TakımRolü Yeniİsim) ---
    @commands.command()
    async def ktd(self, ctx, member: discord.Member = None, role: discord.Role = None, *, yeni_isim: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not role or not yeni_isim:
            await ctx.send("⚠️ **Kullanım:** `!ktd @oyuncu @Galatasaray Fatih Terim | GS | 0🏆`")
            return

        try:
            await member.edit(nick=yeni_isim)
            await member.add_roles(role)
            
            embed = discord.Embed(color=0x000000)
            embed.description = (
                f"✅ **TEKNİK DİREKTÖR KAYDI TAMAMLANDI**\n\n"
                f"👤 **TD:** {member.mention}\n"
                f"🛡️ **Verilen Rol:** {role.mention}\n"
                f"📝 **Yeni İsim:** `{yeni_isim}`"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("❌ Kullanıcı ismi veya rolü güncellenemedi. Botun rol yetkilerini kontrol edin.")

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

    # --- KAYIT (!kayit) ---
    @commands.command(aliases=["kayıt"])
    async def kayit(self, ctx, member: discord.Member = None, *, yeni_isim: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
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

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))

