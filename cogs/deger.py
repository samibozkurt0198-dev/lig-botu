import discord
from discord.ext import commands
import random
import re

# --- ONAY BUTONLARI ---
class KapOnayView(discord.ui.View):
    def __init__(self, taci_yapan: discord.Member, hedef_oyuncu: discord.Member, form_verileri: dict):
        super().__init__(timeout=300)
        self.taci_yapan = taci_yapan
        self.hedef_oyuncu = hedef_oyuncu
        self.form = form_verileri

    @discord.ui.button(label="✅ Transferi Onayla", style=discord.ButtonStyle.green)
    async def onayla(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.hedef_oyuncu.id:
            await interaction.response.send_message("❌ Bu onay butonunu sadece transfer olan oyuncu kullanabilir!", ephemeral=True)
            return

        kap_kanal = discord.utils.get(interaction.guild.text_channels, name="kap-gelenler")
        
        embed = discord.Embed(
            title="⚽ RESMİ KAP BİLDİRİMİ",
            color=0x000000
        )
        embed.description = (
            f"👤 **Futbolcu:** {self.hedef_oyuncu.mention}\n"
            f"👔 **İşlemi Yapan TD:** {self.taci_yapan.mention}\n\n"
            f"🏛️ **Takım (Geldiği / Gittiği):** {self.form['takim']}\n"
            f"💰 **Maaş:** {self.form['maas']}\n"
            f"✍️ **İmza Parası:** {self.form['imza_parasi']}\n"
            f"💵 **Bonservis:** {self.form['bonservis']}\n"
            f"📌 **Ek Madde:** {self.form['ek_madde']}\n\n"
            f"🟢 **Durum:** *Transfer Oyuncu Tarafından Onaylandı ve Tamamlandı!*"
        )
        embed.set_footer(text="Tendo League Resmi KAP Bildirimi")

        if kap_kanal:
            await kap_kanal.send(embed=embed)
            await interaction.response.send_message("✅ Transfer başarıyla onaylandı ve `#kap-gelenler` kanalına gönderildi!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)
            await interaction.followup.send("⚠️ `kap-gelenler` adında bir kanal bulunamadığı için mesaj bu kanala atıldı.", ephemeral=True)

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Reddet", style=discord.ButtonStyle.red)
    async def reddet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.hedef_oyuncu.id:
            await interaction.response.send_message("❌ Bu butonu sadece transfer olan oyuncu kullanabilir!", ephemeral=True)
            return

        await interaction.response.send_message("❌ Transfer oyuncu tarafından reddedildi.", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)


# --- KAP FORMU MODAL ---
class KapFormuModal(discord.ui.Modal, title="📝 Transfer Teklifi Formu"):
    takim = discord.ui.TextInput(label="Takım (Geldiği / Gittiği)", placeholder="Örn: Barcelona / Real Madrid", required=True)
    maas = discord.ui.TextInput(label="Maaş", placeholder="Örn: 500k / hafta", required=True)
    imza_parasi = discord.ui.TextInput(label="İmza Parası", placeholder="Örn: 1m", required=True)
    bonservis = discord.ui.TextInput(label="Bonservis", placeholder="Örn: 5m", required=True)
    ek_madde = discord.ui.TextInput(label="Ek Madde (opsiyonel)", placeholder="Detaylar...", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, ctx, hedef_oyuncu: discord.Member):
        super().__init__()
        self.ctx = ctx
        self.hedef_oyuncu = hedef_oyuncu

    async def on_submit(self, interaction: discord.Interaction):
        form_verileri = {
            "takim": self.takim.value,
            "maas": self.maas.value,
            "imza_parasi": self.imza_parasi.value,
            "bonservis": self.bonservis.value,
            "ek_madde": self.ek_madde.value if self.ek_madde.value else "Yok"
        }

        market_kanal = discord.utils.get(interaction.guild.text_channels, name="transfermarkt")
        dedikodu_embed = discord.Embed(
            title="🚨 TRANSFER DEDİKODUSU / FLAŞ GELİŞME",
            description=(
                f"🗣️ Kulislerde konuşulanlara göre **{interaction.user.display_name}** ({interaction.user.mention}), "
                f"yıldız oyuncu **{self.hedef_oyuncu.mention}** için resmi teklif yaptı!\n\n"
                f"🏛️ **İlgilenen Kulüp / Detay:** {self.takim.value}\n"
                f"💰 **Önerilen Bonservis:** {self.bonservis.value}\n\n"
                f"⏳ *Oyuncunun teklifi onaylaması bekleniyor...*"
            ),
            color=0xFFA500
        )
        dedikodu_embed.set_footer(text="Tendo League Transfer Kulisleri")

        if market_kanal:
            await market_kanal.send(embed=dedikodu_embed)

        view = KapOnayView(taci_yapan=interaction.user, hedef_oyuncu=self.hedef_oyuncu, form_verileri=form_verileri)
        onay_embed = discord.Embed(
            title="📄 Onay Bekleyen Transfer Teklifi",
            description=(
                f"👤 {self.hedef_oyuncu.mention}, {interaction.user.mention} sana bir transfer teklifi gönderdi!\n\n"
                f"**Teklif Detayları:**\n"
                f"• Takım: `{self.takim.value}`\n"
                f"• Bonservis: `{self.bonservis.value}`\n"
                f"• Maaş: `{self.maas.value}`\n\n"
                f"İşlemi tamamlamak için aşağıdaki butonu kullan."
            ),
            color=0x000000
        )
        await interaction.response.send_message(embed=onay_embed, view=view)


class KapButonView(discord.ui.View):
    def __init__(self, ctx, hedef_oyuncu: discord.Member):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.hedef_oyuncu = hedef_oyuncu

    @discord.ui.button(label="📝 Teklif Formunu Doldur", style=discord.ButtonStyle.primary)
    async def formu_ac(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Bu butonu sadece komutu yazan teknik direktör kullanabilir!", ephemeral=True)
            return

        modal = KapFormuModal(ctx=self.ctx, hedef_oyuncu=self.hedef_oyuncu)
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
        td_rol = discord.utils.get(ctx.author.roles, name="Teknik Direktör")
        has_yetki = ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, name="Değer Yetkilisi") or td_rol

        if not has_yetki:
            await ctx.send("❌ Bu komutu sadece **Teknik Direktörler** kullanabilir.")
            return

        if not member:
            await ctx.send("⚠️ **Kullanım:** `!kap @oyuncu`")
            return

        embed = discord.Embed(
            title="📄 Transfer Teklifi Hazırlanıyor",
            description=f"{ctx.author.mention}, {member.mention} için transfer teklifi oluşturmak üzeresin.\n\nDevam etmek için aşağıdaki butona bas.",
            color=0x000000
        )
        view = KapButonView(ctx=ctx, hedef_oyuncu=member)
        await ctx.send(embed=embed, view=view)

    # --- TEKNİK DİREKTÖR KAYIT (!ktd) ---
    @commands.command()
    async def ktd(self, ctx, member: discord.Member = None, role: discord.Role = None, *, yeni_isim: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not role or not yeni_isim:
            await ctx.send("⚠️ **Kullanım:** `!ktd @oyuncu @Galatasaray Fatih Terim | GS | 0🏆`")
            return

        td_rol = discord.utils.get(ctx.guild.roles, name="Teknik Direktör")
        if not td_rol:
            await ctx.send("❌ Sunucuda **Teknik Direktör** isminde bir rol bulunamadı! Lütfen bu isimde bir rol oluşturun.")
            return

        try:
            # Tüm rolleri al, sadece yeni verilecekleri ekle
            temel_roller = [r for r in member.roles if r.managed or r.is_integration()] # Bot rolleri kalabilir
            await member.edit(nick=yeni_isim, roles=temel_roller)
            await member.add_roles(td_rol, role)
            
            embed = discord.Embed(color=0x000000)
            embed.description = (
                f"✅ **TEKNİK DİREKTÖR KAYDI TAMAMLANDI**\n\n"
                f"👤 **TD:** {member.mention}\n"
                f"🛡️ **Verilen Roller:** {td_rol.mention}, {role.mention}\n"
                f"📝 **Yeni İsim:** `{yeni_isim}`"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("❌ İşlem gerçekleştirilemedi. Botun rolü, verilecek rollerden ve kullanıcıdan üst sırada olmalıdır.")

    # --- FUTBOLCU KAYIT (!kayit) ---
    @commands.command(aliases=["kayıt"])
    async def kayit(self, ctx, member: discord.Member = None, *, yeni_isim: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not yeni_isim:
            await ctx.send("⚠️ Kullanım: `!kayit @kullanıcı V.Osimhen | 🇳🇬 | SNT | 1M`")
            return

        fut_rol = discord.utils.get(ctx.guild.roles, name="Futbolcu")
        if not fut_rol:
            await ctx.send("❌ Sunucuda **Futbolcu** isminde bir rol bulunamadı! Lütfen bu isimde bir rol oluşturun.")
            return

        try:
            temel_roller = [r for r in member.roles if r.managed or r.is_integration()]
            await member.edit(nick=yeni_isim, roles=temel_roller)
            await member.add_roles(fut_rol)

            embed = discord.Embed(color=0x000000)
            embed.description = f"✅ {member.mention} başarıyla futbolcu olarak kaydedildi!\n**Rol:** {fut_rol.mention}\n**Yeni İsim:** `{yeni_isim}`"
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Kullanıcı kaydedilemedi. Botun rol yetkilerini kontrol edin.")

    # --- KALECİ KAYIT (!kk) ---
    @commands.command()
    async def kk(self, ctx, member: discord.Member = None, *, yeni_isim: str = None):
        has_role = discord.utils.get(ctx.author.roles, name="Değer Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or has_role):
            await ctx.send("❌ Bu komutu sadece **Değer Yetkilisi** kullanabilir.")
            return

        if not member or not yeni_isim:
            await ctx.send("⚠️ Kullanım: `!kk @kullanıcı F.Muslera | 🇺🇾 | KLÇ | 1M`")
            return

        kaleci_rol = discord.utils.get(ctx.guild.roles, name="Kaleci")
        if not kaleci_rol:
            await ctx.send("❌ Sunucuda **Kaleci** isminde bir rol bulunamadı! Lütfen bu isimde bir rol oluşturun.")
            return

        try:
            temel_roller = [r for r in member.roles if r.managed or r.is_integration()]
            await member.edit(nick=yeni_isim, roles=temel_roller)
            await member.add_roles(kaleci_rol)

            embed = discord.Embed(color=0x000000)
            embed.description = f"✅ {member.mention} başarıyla kaleci olarak kaydedildi!\n**Rol:** {kaleci_rol.mention}\n**Yeni İsim:** `{yeni_isim}`"
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Kullanıcı kaydedilemedi. Botun rol yetkilerini kontrol edin.")

    # --- DİĞER KOMUTLAR ---
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
            embed.description = f"🏋️ **Antrenman yapıldı!**\n\n📊 Antrenman: **10/10**\n🎯 **Tebrikler! `#değer-iste` kanalından +3M€ talebinde bulunabilirsin!**"
        else:
            self.ant_sayac[user_id] = mevcut
            embed.description = f"🏋️ **Antrenman yapıldı!**\n\n📊 Antrenman: **{mevcut}/10**"
        await ctx.send(embed=embed)

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
        embed.description = f"✅ **DEĞER VERİLDİ**\n👤 {member.mention}\n📈 **Yeni değer:** {yeni_val}M€"
        await ctx.send(embed=embed)

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
        embed.description = f"🔻 **DEĞER SİLİNDİ**\n👤 {member.mention}\n📉 **Yeni değer:** {yeni_val}M€"
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DegerSistemi(bot))
