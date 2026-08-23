import discord
from discord.ext import commands
import asyncio
import random
import re

class MacSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def oyuncu_bilgi_al(self, member: discord.Member):
        display_name = member.display_name
        
        # Değer bulma (Örn: 100M€ veya 50M)
        deger_match = re.search(r'(\d+(?:\.\d+)?)\s*M', display_name, re.IGNORECASE)
        deger_sayi = float(deger_match.group(1)) if deger_match else 10.0
        
        # Mevki bulma
        mevki_match = re.search(r'\b(KL|STP|SLB|SĞB|DOS|OS|OOS|SLK|SĞK|SNT|FRV)\b', display_name, re.IGNORECASE)
        mevki = mevki_match.group(1).upper() if mevki_match else "OS"
        
        # Isim temizleme
        temiz_isim = re.sub(r'\[.*?\]|\(.*?\)', '', display_name).strip()
        temiz_isim = temiz_isim.split('|')[0].strip()

        return {
            "member": member,
            "isim": temiz_isim[:12],
            "mevki": mevki,
            "deger_sayi": deger_sayi,
            "deger_str": f"{int(deger_sayi)}M€",
            "reyting": round(random.uniform(6.0, 9.0), 1),
            "gol": 0,
            "asist": 0
        }

    # Mevki bazlı Oyuncu Seçimi Mantığı
    def golcu_sec(self, kadro):
        # Kaleciler gol atamaz
        adaylar = [o for o in kadro if o["mevki"] != "KL"]
        
        # Hücumcuların gol atma şansı daha yüksek
        forvetler = [o for o in adaylar if o["mevki"] in ["SNT", "FRV", "SLK", "SĞK"]]
        orta_sahalar = [o for o in adaylar if o["mevki"] in ["OS", "OOS", "DOS"]]
        defanslar = [o for o in adaylar if o["mevki"] in ["STP", "SLB", "SĞB"]]

        zar = random.randint(1, 100)
        if zar <= 65 and forvetler:
            return random.choice(forvetler)
        elif zar <= 90 and orta_sahalar:
            return random.choice(orta_sahalar)
        elif defanslar:
            return random.choice(defanslar)
        return random.choice(adaylar)

    def asistci_sec(self, kadro, golcu):
        adaylar = [o for o in kadro if o != golcu and o["mevki"] != "KL"]
        orta_sahalar = [o for o in adaylar if o["mevki"] in ["OS", "OOS", "SLK", "SĞK"]]

        if random.randint(1, 100) <= 70 and orta_sahalar:
            return random.choice(orta_sahalar)
        return random.choice(adaylar) if adaylar else None

    @commands.command(name="maç", aliases=["mac"])
    async def mac_baslat(self, ctx, takim1_role: discord.Role = None, takim2_role: discord.Role = None):
        yetkili_rol = discord.utils.get(ctx.author.roles, name="Maç Yetkilisi")
        if not (ctx.author.guild_permissions.administrator or yetkili_rol):
            await ctx.send("❌ Bu komutu sadece **Maç Yetkilisi** rolüne sahip kişiler kullanabilir!")
            return

        if not takim1_role or not takim2_role:
            await ctx.send("⚠️ **Kullanım:** `.maç @Takım1Rolü @Takım2Rolü`")
            return

        takim1_adi, takim2_adi = takim1_role.name, takim2_role.name

        t1_uyeler = [m for m in takim1_role.members if not m.bot]
        t2_uyeler = [m for m in takim2_role.members if not m.bot]

        t1_kadro = [self.oyuncu_bilgi_al(m) for m in t1_uyeler[:11]]
        t2_kadro = [self.oyuncu_bilgi_al(m) for m in t2_uyeler[:11]]

        # Yetersiz kadroları Kaleci ve NPC oyuncularla tamamlama
        mevkiler = ["KL", "STP", "STP", "SLB", "SĞB", "DOS", "OS", "OOS", "SLK", "SĞK", "SNT"]
        while len(t1_kadro) < 11:
            m = mevkiler[len(t1_kadro)]
            t1_kadro.append({"isim": f"NPC_{len(t1_kadro)+1}", "mevki": m, "deger_sayi": 5.0, "deger_str": "5M€", "reyting": 6.0, "gol": 0, "asist": 0, "member": None})
        while len(t2_kadro) < 11:
            m = mevkiler[len(t2_kadro)]
            t2_kadro.append({"isim": f"NPC_{len(t2_kadro)+1}", "mevki": m, "deger_sayi": 5.0, "deger_str": "5M€", "reyting": 6.0, "gol": 0, "asist": 0, "member": None})

        # Kadro Değeri & Güç Hesaplama
        t1_guc = sum(o["deger_sayi"] for o in t1_kadro)
        t2_guc = sum(o["deger_sayi"] for o in t2_kadro)

        t1_sans = int((t1_guc / (t1_guc + t2_guc)) * 100)

        skor1, skor2 = 0, 0

        baslangic_embed = discord.Embed(
            title=f"⚽ {takim1_adi} ({t1_sans}%) vs {takim2_adi} ({100-t1_sans}%)",
            description=f"🚨 **MAÇ BAŞLADI!**\n\n💰 **{takim1_adi} Kadro Gücü:** `{int(t1_guc)}M€`\n💰 **{takim2_adi} Kadro Gücü:** `{int(t2_guc)}M€`\n\nHakem 90 dakikalık düdüğü çaldı!",
            color=0x000000
        )
        mac_mesaji = await ctx.send(embed=baslangic_embed)
        await asyncio.sleep(2)

        # 90 Dakikalık Simülasyon
        olay_dakikalari = sorted(random.sample(range(3, 89), random.randint(8, 12)))

        for dk in range(1, 91):
            if dk in olay_dakikalari:
                # Güçlü olan takımın atağa çıkma ihtimali daha yüksek
                atak_takim = 1 if random.randint(1, 100) <= t1_sans else 2
                gol_mu = random.randint(1, 100) <= 35  # %35 Bitiricilik şansı

                if atak_takim == 1:
                    o = self.golcu_sec(t1_kadro)
                    asistci = self.asistci_sec(t1_kadro, o)
                    
                    if gol_mu:
                        skor1 += 1
                        o["gol"] += 1
                        o["reyting"] = min(10.0, round(o["reyting"] + 0.8, 1))
                        asist_str = f" ← (Asist: **{asistci['isim']}**)" if asistci else ""
                        if asistci: asistci["asist"] += 1
                        
                        detay = f"⚽ **{o['isim']}** | **{o['mevki']}** | `{o['deger_str']}`{asist_str}"
                        olay = "🔥 **GOOOOL!** Ceza sahasında harika vuruş ve top ağlarda!"
                    else:
                        detay = f"⚡ **{o['isim']}** | **{o['mevki']}** kaleyi karşısına aldı..."
                        olay = "🧤 **KURTARIŞ!** Kaleci harika uzandı ve gole izin vermedi!"
                else:
                    o = self.golcu_sec(t2_kadro)
                    asistci = self.asistci_sec(t2_kadro, o)
                    
                    if gol_mu:
                        skor2 += 1
                        o["gol"] += 1
                        o["reyting"] = min(10.0, round(o["reyting"] + 0.8, 1))
                        asist_str = f" ← (Asist: **{asistci['isim']}**)" if asistci else ""
                        if asistci: asistci["asist"] += 1
                        
                        detay = f"⚽ **{o['isim']}** | **{o['mevki']}** | `{o['deger_str']}`{asist_str}"
                        olay = "🔥 **GOOOOL!** Ağları havalandıran müthiş gol!"
                    else:
                        detay = f"⚡ **{o['isim']}** | **{o['mevki']}** sert vurdu!"
                        olay = "❌ **DIŞARI!** Top az farkla auta çıktı!"

                embed = discord.Embed(
                    title=f"⏱️ {dk}. Dakika | {takim1_adi} {skor1} - {skor2} {takim2_adi}",
                    description=f"{detay}\n\n**{olay}**",
                    color=0x000000
                )
                embed.set_footer(text="Tendo League 90 Dk Canlı Maç Motoru")
                await mac_mesaji.edit(embed=embed)
                await asyncio.sleep(2)
            else:
                if dk % 15 == 0:
                    embed = discord.Embed(
                        title=f"⏱️ {dk}. Dakika | {takim1_adi} {skor1} - {skor2} {takim2_adi}",
                        description="⚽ Oyun orta sahada kıran kırana devam ediyor...",
                        color=0x000000
                    )
                    await mac_mesaji.edit(embed=embed)
                    await asyncio.sleep(1)

        # MAÇ SONU
        kazanan = f"🏆 **{takim1_adi}**" if skor1 > skor2 else (f"🏆 **{takim2_adi}**" if skor2 > skor1 else "🤝 **Berabere Bitti!**")
        
        istatistik_embed = discord.Embed(
            title=f"🏁 MAÇ SONUCU: {takim1_adi} {skor1} - {skor2} {takim2_adi}",
            description=f"{kazanan}\n\n"
                        f"📊 **Kadro Gücü Etkisi:**\n"
                        f"🛡️ **{takim1_adi}:** `{int(t1_guc)}M€` (%{t1_sans} Şans)\n"
                        f"👑 **{takim2_adi}:** `{int(t2_guc)}M€` (%{100-t1_sans} Şans)",
            color=0x000000
        )
        await ctx.send(embed=istatistik_embed)

        # OYUNCU REYTİNG VE PERFORMANSLARI
        def performans_listesi(kadro):
            metin = ""
            for i, o in enumerate(kadro, 1):
                g_str = f" ⚽x{o['gol']}" if o['gol'] > 0 else ""
                a_str = f" 🅰️x{o['asist']}" if o['asist'] > 0 else ""
                metin += f"`{i:02d}` **{o['mevki']}** | ⭐ **{o['reyting']}** | **{o['isim']}** (`{o['deger_str']}`){g_str}{a_str}\n"
            return metin

        embed1 = discord.Embed(title=f"🛡️ {takim1_adi} Oyuncu Performansları", description=performans_listesi(t1_kadro), color=0x000000)
        embed2 = discord.Embed(title=f"👑 {takim2_adi} Oyuncu Performansları", description=performans_listesi(t2_kadro), color=0x000000)
        
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)

async def setup(bot):
    await bot.add_cog(MacSistemi(bot))
