import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

# Takımların canlı kadro verilerini tutan hafıza
kadro_verileri = {}

# Pozisyonların saha üzerindeki (X, Y) koordinatları
POZISYON_KOORDINATLARI = {
    "GK": (250, 520),
    "STP1": (180, 430), "STP2": (320, 430),
    "SLB": (70, 390), "SGB": (430, 390),
    "DOS": (250, 320),
    "OS1": (170, 240), "OS2": (330, 240),
    "SLK": (90, 140), "SGK": (410, 140),
    "SNT": (250, 80)
}

# --- CANLI SAHA RESMİ ÇİZME FONKSİYONU ---
def saha_gorseli_olustur(takim_adi, kadro_dict):
    # 500x600 Yeşil Tuval
    img = Image.new("RGB", (500, 600), color=(34, 112, 56))
    draw = ImageDraw.Draw(img)

    # Saha Çizgileri
    draw.rectangle([20, 20, 480, 580], outline=(255, 255, 255), width=3)
    draw.line([(20, 300), (480, 300)], fill=(255, 255, 255), width=2)
    draw.ellipse([190, 240, 310, 360], outline=(255, 255, 255), width=2)
    draw.rectangle([140, 20, 360, 120], outline=(255, 255, 255), width=2)
    draw.rectangle([140, 480, 360, 580], outline=(255, 255, 255), width=2)

    # Başlık
    draw.text((160, 30), f"--- {takim_adi.upper()} ---", fill="white")

    # Oyuncuları Saha Üzerine Çiz
    for pos_kod, (x, y) in POZISYON_KOORDINATLARI.items():
        oyuncu_adi = kadro_dict.get(pos_kod, "Boş")

        # Daire & Pozisyon
        draw.ellipse([x-12, y-12, x+12, y+12], fill=(0, 0, 0), outline=(255, 255, 255), width=2)
        draw.text((x-8, y-6), pos_kod[:2], fill="white")

        # Oyuncu Adı
        draw.text((x-25, y+15), oyuncu_adi[:12], fill="yellow")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="kadro.png")

# --- OYUNCU YERLEŞTİRME MODAL (FORM) ---
class KadroModal(discord.ui.Modal, title="⚽ Kadroya Oyuncu Yerleştir"):
    pozisyon = discord.ui.TextInput(
        label="Pozisyon (GK, STP1, STP2, SLB, SGB...)",
        placeholder="Örn: SNT",
        max_length=5,
        required=True
    )
    oyuncu = discord.ui.TextInput(
        label="Oyuncu Adı",
        placeholder="Örn: Icardi",
        max_length=15,
        required=True
    )

    def __init__(self, takim_adi: str):
        super().__init__()
        self.takim_adi = takim_adi

    async def on_submit(self, interaction: discord.Interaction):
        pos = self.pozisyon.value.upper().strip()

        if pos not in POZISYON_KOORDINATLARI:
            kullanilabilir = ", ".join(POZISYON_KOORDINATLARI.keys())
            await interaction.response.send_message(f"❌ Geçersiz pozisyon! Kullanılabilir: `{kullanilabilir}`", ephemeral=True)
            return

        if self.takim_adi not in kadro_verileri:
            kadro_verileri[self.takim_adi] = {}

        # Kadroya kaydet
        kadro_verileri[self.takim_adi][pos] = self.oyuncu.value.strip()

        # Yeni resmi çizip mevcut mesajı güncelle
        yeni_resim = saha_gorseli_olustur(self.takim_adi, kadro_verileri[self.takim_adi])

        await interaction.response.defer()
        await interaction.message.edit(attachments=[yeni_resim])

# --- KADRO BUTON SİSTEMİ ---
class KadroButonView(discord.ui.View):
    def __init__(self, takim_adi: str):
        super().__init__(timeout=None)
        self.takim_adi = takim_adi

    @discord.ui.button(label="⚙️ Oyuncu Yerleştir / Güncelle", style=discord.ButtonStyle.blurple, custom_id="kadro_yerlestir_btn")
    async def yerlestir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(KadroModal(self.takim_adi))

# --- COG SINIFI ---
class Kadro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- CANLI GÖRSELİLİ KADRO KOMUTU (.kadro) ---
    @commands.command(name="kadro")
    async def kadro(self, ctx, *, takim_adi: str = None):
        td_rol = discord.utils.get(ctx.author.roles, name="Teknik Direktör")
        has_yetki = ctx.author.guild_permissions.administrator or td_rol or any("T.D." in r.name for r in ctx.author.roles)

        if not has_yetki:
            await ctx.send("❌ Bu komutu sadece **Teknik Direktörler** kullanabilir!")
            return

        if not takim_adi:
            await ctx.send("⚠️ **Kullanım:** `.kadro <Takım Adı>`\nÖrnek: `.kadro Real Madrid`")
            return

        if takim_adi not in kadro_verileri:
            kadro_verileri[takim_adi] = {}

        resim = saha_gorseli_olustur(takim_adi, kadro_verileri[takim_adi])
        view = KadroButonView(takim_adi)

        await ctx.send(file=resim, view=view)

    # --- REAL MADRID ÖZEL KOMUTU (.rmadrid) ---
    @commands.command(name="rmadrid")
    @commands.has_role("Real Madrid T.D.")
    async def rmadrid(self, ctx):
        takim_adi = "Real Madrid"
        if takim_adi not in kadro_verileri:
            kadro_verileri[takim_adi] = {}

        resim = saha_gorseli_olustur(takim_adi, kadro_verileri[takim_adi])
        view = KadroButonView(takim_adi)

        await ctx.send(file=resim, view=view)

    @rmadrid.error
    async def rmadrid_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("❌ Bu komutu sadece **Real Madrid T.D.** rolüne sahip kişiler kullanabilir!")

async def setup(bot):
    await bot.add_cog(Kadro(bot))
