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
        await asyncio.sleep(3)

        # DAKİKA DAKİKA ANLATIM AKIŞI
        o1 = random.choice(t1_kadro)
        o2 = random.choice(t2_kadro)
        o1_asist = random.choice([o for o in t1_kadro if o != o1])

        anlatimlar = [
            {
                "dakika": 28,
                "baslik": f"28' {takim1_adi} {skor1}-{skor2} {takim2_adi}",
                "detay": f"**{o1['isim']}** | {o1['bayrak']} | **{o1['mevki']} | {o1['deger']}** dönüp kaleye baktı...",
                "olay": f"💥 **GOL!** Uzaklardan harika bir füze çıkardı ve top ağlarda!",
                "skor_artisi": (1, 0),
                "golcu": o1,
                "bar": f"📍 **Pozisyon**\n🛡️ {takim1_adi} 🟩🟩🟩🟩⬜⬜⬜ 28m 🎲"
            },
            {
                "dakika": 64,
                "baslik": f"64' {takim1_adi} {skor1+1}-{skor2} {takim2_adi}",
                "detay": f"**{o1['isim']}** | {o1['bayrak']} | **{o1['mevki']} | {o1['deger']}** ← A **{o1_asist['isim']}** | {o1_asist['bayrak']} | **{o1_asist['mevki']} | {o1_asist['deger']}**",
                "olay": "🔥 **İÇERİDEEE!!!** Muazzam paslaşma ve şık bitiriş!",
                "skor_artisi": (1, 0),
                "golcu": o1,
                "asistci": o1_asist,
                "bar": f"📍 **Pozisyon**\n🛡️ {takim1_adi} 🟩🟩🟩🟩🟩🟩⬜ 17m 🎲"
            },
            {
                "dakika": 89,
                "baslik": f"89' {takim1_adi} {skor1+2}-{skor2} {takim2_adi}",
                "detay": f"**{o2['isim']}** | {o2['bayrak']} | **{o2['mevki']} | {o2['deger']}** ceza sahası dışından sert vurdu!",
                "olay": "🧤 **ÇELDİİİİ!** Kaleci topu son anda parmaklarının ucuyla çeldi!",
                "skor_artisi": (0, 0),
                "golcu": None,
                "bar": f"📍 **Pozisyon**\n🛡️ {takim2_adi} 🟩🟩🟩🟩⬜⬜⬜ 27m 🎲"
            }
        ]

        for an in anlatimlar:
            if an["golcu"]:
                an["golcu"]["gol"] += an["skor_artisi"][0]
            if "asistci" in an and an["asistci"]:
                an["asistci"]["asist"] += 1

            skor1 += an["skor_artisi"][0]
            skor2 += an["skor_artisi"][1]
            
            embed = discord.Embed(
                title=f"{an['baslik']}",
                description=f"{an['detay']}\n\n**{an['olay']}**\n\n{an['bar']}",
                color=0x000000
            )
            embed.set_footer(text=f"{takim1_adi} {skor1} - {skor2} {takim2_adi}")
            await mac_mesaji.edit(embed=embed)
            await asyncio.sleep(4)

        # MAÇ SONU İSTATİSTİKLERİ
        kazanan = takim1_adi if skor1 > skor2 else (takim2_adi if skor2 > skor1 else "Berabere")
        istatistik_embed = discord.Embed(
            title=f"🏆 {takim1_adi} {skor1} - {skor2} {takim2_adi}",
            description=f"🏆 **{kazanan} kazandı!**\n\n"
                        f"🤝 **Lig Maçı** — Sonuçlar kaydedildi.\n\n"
                        f"📊 **Maç İstatistikleri**\n"
                        f"⚡ **Topla Oynama %**\n`52%` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 `48%`\n"
                        f"💥 **Şut**\n` 8 ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` 5 `\n"
                        f"🎯 **İsabetli Şut**\n` 5 ` 🟦🟦🟦🟦🟥🟥🟥🟥🟥 ` 3 `\n"
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
