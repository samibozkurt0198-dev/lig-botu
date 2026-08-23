import discord
from discord.ext import commands
import asyncio
import random
import re

class MacSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def oyuncu_bilgi_al(self, member: discord.Member):
        """Oyuncunun sunucu adından mevkisini ve değerini çekmeye çalışır."""
        display_name = member.display_name
        
        # Değer bulma (Örn: 100M€ veya 50M)
        deger_match = re.search(r'(\d+(?:\.\d+)?M(?:€)?)', display_name, re.IGNORECASE)
        deger = deger_match.group(1) if deger_match else "10M€"
        
        # Mevki bulma (Örn: SNT, OOS, STP, KL, OS, SĞK, SLK)
        mevki_match = re.search(r'\b(KL|STP|SLB|SĞB|DOS|OS|OOS|SLK|SĞK|SNT|FRV)\b', display_name, re.IGNORECASE)
        mevki = mevki_match.group(1).upper() if mevki_match else "OS"
        
        # Isim temizleme
        temiz_isim = re.sub(r'\[.*?\]|\(.*?\)', '', display_name).strip()
        temiz_isim = temiz_isim.split('|')[0].strip()

        return {
            "member": member,
            "isim": temiz_isim[:12],
            "bayrak": "🇹🇷",
            "mevki": mevki,
            "deger": deger,
            "reyting": round(random.uniform(5.5, 9.5), 1),
            "gol": 0,
            "asist": 0
        }

    @commands.command(name="maç", aliases=["mac"])
    async def mac_baslat(self, ctx, takim1_role: discord.Role = None, takim2_role: discord.Role = None):
        # 1. YETKİ KONTROLÜ (Sadece Maç Yetkilisi veya Yönetici)
        yetkili_rol = discord.utils.get(ctx.author.roles, name="Maç Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or yetkili_rol):
            await ctx.send("❌ Bu komutu sadece **Maç Yetkilisi** rolüne sahip kişiler kullanabilir!")
            return

        # 2. PARAMETRE KONTROLÜ
        if not takim1_role or not takim2_role:
            await ctx.send("⚠️ **Kullanım:** `.maç @Takım1Rolü @Takım2Rolü`\nÖrnek: `.maç @RealMadrid @Arsenal`")
            return

        takim1_adi = takim1_role.name
        takim2_adi = takim2_role.name

        # Rollere sahip üyeleri çekme
        t1_uyeler = [m for m in takim1_role.members if not m.bot]
        t2_uyeler = [m for m in takim2_role.members if not m.bot]

        # Oyuncu listelerini oluşturma
        t1_kadro = [self.oyuncu_bilgi_al(m) for m in t1_uyeler[:11]]
        t2_kadro = [self.oyuncu_bilgi_al(m) for m in t2_uyeler[:11]]

        # Kadro yetersizse varsayılan NPC ekleme
        while len(t1_kadro) < 11:
            t1_kadro.append({"isim": f"NPC_{len(t1_kadro)+1}", "bayrak": "🌐", "mevki": "OS", "deger": "1M€", "reyting": 6.0, "gol": 0, "asist": 0, "member": None})
        while len(t2_kadro) < 11:
            t2_kadro.append({"isim": f"NPC_{len(t2_kadro)+1}", "bayrak": "🌐", "mevki": "OS", "deger": "1M€", "reyting": 6.0, "gol": 0, "asist": 0, "member": None})

        skor1, skor2 = 0, 0

        # BAŞLANGIÇ MESAJI
        baslangic_embed = discord.Embed(
            title=f"⚽ {takim1_adi} vs {takim2_adi}",
            description=f"🚨 **MAÇ BAŞLADI!**\n\n**{takim1_role.mention}** 🆚 **{takim2_role.mention}**\nHakem düdüğünü çaldı, iki takıma da başarılar!",
            color=0x000000
        )
        mac_mesaji = await ctx.send(embed=baslangic_embed)
        await asyncio.sleep(2)

        # 1'DEN 90'A KADAR CANLI DAKİKA AKIŞI
        olay_dakikalari = sorted(random.sample(range(5, 88), 5)) # Maç içi 5 kritik pozisyon üretir

        for dk in range(1, 91):
            if dk in olay_dakikalari:
                takim = random.choice([1, 2])
                gol_mu = random.choice([True, False])

                if takim == 1:
                    o = random.choice(t1_kadro)
                    asistci = random.choice([x for x in t1_kadro if x != o])
                    if gol_mu:
                        skor1 += 1
                        o["gol"] += 1
                        asistci["asist"] += 1
                        detay = f"**{o['isim']}** | {o['bayrak']} | **{o['mevki']} | {o['deger']}** ← A **{asistci['isim']}** | {asistci['bayrak']} | **{asistci['mevki']} | {asistci['deger']}**"
                        olay = "💥 **GOL!** Harika organizasyon ve top ağlarda!"
                    else:
                        detay = f"**{o['isim']}** | {o['bayrak']} | **{o['mevki']} | {o['deger']}** ceza sahası dışından sert vurdu!"
                        olay = "🧤 **ÇELDİİİİ!** Kaleci topu son anda çeldi!"
                    bar = f"📍 **Pozisyon**\n🛡️ {takim1_adi} 🟩🟩🟩🟩🟩⬜⬜ {random.randint(15, 30)}m 🎲"
                else:
                    o = random.choice(t2_kadro)
                    asistci = random.choice([x for x in t2_kadro if x != o])
                    if gol_mu:
                        skor2 += 1
                        o["gol"] += 1
                        asistci["asist"] += 1
                        detay = f"**{o['isim']}** | {o['bayrak']} | **{o['mevki']} | {o['deger']}** ← A **{asistci['isim']}** | {asistci['bayrak']} | **{asistci['mevki']} | {asistci['deger']}**"
                        olay = "💥 **GOL!** Şık bitirişle top ağlarla buluştu!"
                    else:
                        detay = f"**{o['isim']}** | {o['bayrak']} | **{o['mevki']} | {o['deger']}** dönüp kaleye baktı..."
                        olay = "🧤 **KURTARIŞ!** Kaleci çizgi üzerinde kontrol etti!"
                    bar = f"📍 **Pozisyon**\n🛡️ {takim2_adi} 🟩🟩🟩🟩⬜⬜⬜ {random.randint(15, 30)}m 🎲"

                embed = discord.Embed(
                    title=f"{dk}' {takim1_adi} {skor1}-{skor2} {takim2_adi}",
                    description=f"{detay}\n\n**{olay}**\n\n{bar}",
                    color=0x000000
                )
                embed.set_footer(text=f"{takim1_adi} {skor1} - {skor2} {takim2_adi}")
                await mac_mesaji.edit(embed=embed)
                await asyncio.sleep(3)
            else:
                # Aradaki normal dakikaların hızlı akışı
                if dk % 15 == 0 or dk == 90:
                    embed = discord.Embed(
                        title=f"{dk}' {takim1_adi} {skor1}-{skor2} {takim2_adi}",
                        description=f"🔄 Top orta saha mücadelesiyle devam ediyor...",
                        color=0x000000
                    )
                    embed.set_footer(text=f"{takim1_adi} {skor1} - {skor2} {takim2_adi}")
                    await mac_mesaji.edit(embed=embed)
                    await asyncio.sleep(1)

        # MAÇ SONU İSTATİSTİKLERİ
        kazanan = takim1_adi if skor1 > skor2 else (takim2_adi if skor2 > skor1 else "Berabere")
        istatistik_embed = discord.Embed(
            title=f"🏆 {takim1_adi} {skor1} - {skor2} {takim2_adi}",
            description=f"🏆 **{kazanan} kazandı!**\n\n"
                        f"🤝 **Lig Maçı** — Sonuçlar kaydedildi.\n\n"
                        f"📊 **Maç İstatistikleri**\n"
                        f"⚡ **Topla Oynama %**\n`52%` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 `48%`\n"
                        f"💥 **Şut**\n` {skor1 + 4} ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` {skor2 + 3} `\n"
                        f"🎯 **İsabetli Şut**\n` {skor1 + 2} ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` {skor2 + 1} `\n"
                        f"🚩 **Korner**\n` 3 ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` 2 `\n"
                        f"⚠️ **Faul**\n` 7 ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` 9 `\n",
            color=0x000000
        )
        await ctx.send(embed=istatistik_embed)

        # OYUNCU PERFORMANS KARTLARI & REYTİNGLER
        t1_metin = ""
        for i, o in enumerate(t1_kadro, 1):
            gol_str = f" ⚽{o['gol']}" if o['gol'] > 0 else ""
            asist_str = f" A{o['asist']}" if o['asist'] > 0 else ""
            t1_metin += f"`{i}` 🌟 **{o['reyting']}** {o['mevki']} **{o['isim']}** | {o['bayrak']} | **{o['mevki']}** | **{o['deger']}**{gol_str}{asist_str}\n"

        t2_metin = ""
        for i, o in enumerate(t2_kadro, 1):
            gol_str = f" ⚽{o['gol']}" if o['gol'] > 0 else ""
            asist_str = f" A{o['asist']}" if o['asist'] > 0 else ""
            t2_metin += f"`{i}` 🟧 **{o['reyting']}** {o['mevki']} **{o['isim']}** | {o['bayrak']} | **{o['mevki']}** | **{o['deger']}**{gol_str}{asist_str}\n"

        t1_ort = round(sum(o['reyting'] for o in t1_kadro) / len(t1_kadro), 2)
        t2_ort = round(sum(o['reyting'] for o in t2_kadro) / len(t2_kadro), 2)

        reyting_embed1 = discord.Embed(
            title=f"🛡️ {takim1_adi} — ort. {t1_ort}",
            description=t1_metin,
            color=0x000000
        )
        await ctx.send(embed=reyting_embed1)

        reyting_embed2 = discord.Embed(
            title=f"👑 {takim2_adi} — ort. {t2_ort}",
            description=t2_metin,
            color=0x000000
        )
        await ctx.send(embed=reyting_embed2)

        # DM PERFORMANS RAPORLARI
        dm_sayac = 0
        for o in t1_kadro + t2_kadro:
            if o["member"]:
                try:
                    dm_embed = discord.Embed(
                        title="📊 MAÇ PERFORMANS RAPORUN",
                        description=f"**Maç:** {takim1_adi} {skor1} - {skor2} {takim2_adi}\n"
                                    f"⭐ **Maç Reytingin:** {o['reyting']}\n"
                                    f"⚽ **Attığın Gol:** {o['gol']}\n"
                                    f"🎯 **Yaptığın Asist:** {o['asist']}",
                        color=0x000000
                    )
                    await o["member"].send(embed=dm_embed)
                    dm_sayac += 1
                except:
                    pass

        await ctx.send(f"📢 **{dm_sayac} oyuncuya performans raporu DM olarak gönderildi.**")

async def setup(bot):
    await bot.add_cog(MacSistemi(bot))

