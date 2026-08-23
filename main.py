import discord
from discord.ext import commands
import os
import asyncio

# Bot ayarları (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Bot nesnesi ve Prefix (".")
bot = commands.Bot(command_prefix=".", intents=intents)

# Varsayılan yardım komutunu kaldırıyoruz
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı!")
    print("Tendo League lig sistemiyle aktif! Tüm komutlar '.' ile çalışıyor.")
    
    # Botun durum mesajı (Activity)
    activity = discord.Activity(type=discord.ActivityType.playing, name=".yardım | Tendo League")
    await bot.change_presence(status=discord.Status.online, activity=activity)

# --- ŞIK YARDIM KOMUTU (.yardım) ---
@bot.command(name="yardim", aliases=["yardım", "help"])
async def yardim(ctx):
    embed = discord.Embed(
        title="🏆 Tendo League Bot — Komut Menüsü",
        description="Aşağıda sunucuda kullanabileceğiniz tüm komutlar kategorize edilmiştir. Komut prefix'i: `.`",
        color=0x000000
    )
    
    embed.add_field(
        name="⚽ Transfer & Değer (.deger)",
        value="`.kap` • `.ktd` • `.kayit` • `.kk` • `.dver` • `.dsil` • `.tweet` • `.ant` • `.pen`",
        inline=False
    )
    
    embed.add_field(
        name="🏟️ Maç & Lig (.mac)",
        value="`.mac` • `.skor` • `.canli` • `.puan` • `.fikstur` • `.kirmizi` • `.sari` • `.sakatlik` • `.itiraz`",
        inline=False
    )

    embed.add_field(
        name="📋 Kadro & Taktik (.kadro)",
        value="`.kadro` • `.rmadrid`",
        inline=False
    )

    embed.add_field(
        name="🏢 Şirket & Ekonomi (.sirket)",
        value="`.sirketal` • `.sponsorgeliri` • `.bakiye`",
        inline=False
    )

    embed.add_field(
        name="🎫 Destek & Kayıt Sistemi",
        value="`.kayitsistemi` • `.ticketsistemi` • `.close`",
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderasyon",
        value="`.lock` • `.unlock` • `.sil` • `.kick` • `.ban`",
        inline=False
    )

    embed.set_footer(text=f"Sorgulayan: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else discord.Embed.Empty)
    await ctx.send(embed=embed)

# Cogs (Modül) yükleme fonksiyonu
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            extension_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension_name)
                print(f"{extension_name} modülü yüklendi.")
            except Exception as e:
                print(f"{extension_name} yüklenirken hata oluştu: {e}")

async def main():
    async with bot:
        await load_extensions()
        # Buraya kendi bot token'ını yazabilir veya Railway / Replit ortam değişkenlerinden (Environment Variables) çekebilirsin.
        # Örn: os.getenv("DISCORD_TOKEN")
        token = os.getenv("DISCORD_TOKEN") 
        if not token:
            print("❌ HATA: Bot token bulunamadı! Lütfen ortam değişkenlerine (Environment Variables) 'DISCORD_TOKEN' ekleyin.")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
