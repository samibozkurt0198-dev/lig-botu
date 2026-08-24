import discord
from discord.ext import commands
import asyncio
import random
import re

class MacSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.takimlar = {}
        self.fikstur = []
        self.aktif_hafta = 0
        self.istatistikler = {}  # user_id: {isim, gol, asist, sari_kart, ceza_maci, sakatlik_maci}

    def nickname_oku(self, member: discord.Member):
        display_name = member.display_name
        
        deger_match = re.search(r'(\d+(?:\.\d+)?)\s*M', display_name, re.IGNORECASE)
        deger_str = f"{deger_match.group(1)}M" if deger_match else "1M"
        deger_sayi = float(deger_match.group(1)) if deger_match else 1.0

        mevki_match = re.search(r'\b(KL|STP|SLB|SĞB|DOS|OS|OOS|SLK|SĞK|SNT|FRV)\b', display_name, re.IGNORECASE)
        mevki = mevki_match.group(1).upper() if mevki_match else "OS"

        bayrak_match = re.search(r'[\U0001F1E6-\U0001F1FF]{2}', display_name)
        bayrak = bayrak_match.group(0) if bayrak_match else "🌐"

        temiz_isim = re.sub(r'\[.*?\]|\(.*?\)', '', display_name).strip()
        temiz_isim = temiz_isim.split('|')[0].strip()
        if "@" in temiz_isim:
            temiz_isim = temiz_isim.replace("@", "")

        if member.id not in self.istatistikler:
            self.istatistikler[member.id] = {
                "isim": temiz_isim[:14],
                "gol": 0,
                "asist": 0,
                "sari_kart_toplam": 0,
                "ceza_maci": 0,
                "sakatlik_maci": 0
            }

        return {
            "id": member.id,
            "member": member,
            "isim": temiz_isim[:14],
            "mevki": mevki,
            "bayrak": bayrak,
            "deger_str": deger_str,
            "deger_sayi": deger_sayi,
            "reyting": round(random.uniform(5.5, 8.5), 1),
            "gol": 0, "asist": 0, "sut": 0, "pas": 0
        }

    # '.m' ana komut grubu
    @commands.group(name="m", invoke_without_command=True)
    async def m_group(self, ctx):
        await ctx.invoke(self.mac_yardim)

    @m_group.command(name="yardım", aliases=["yardim"])
    async def mac_yardim(self, ctx):
        embed = discord.Embed(
            title="⚽ TENDO LEAGUE — MAÇ & YÖNETİM BOTU",
            description="🎡 Gelişmiş takım, fikstür, kart/sakatlık ve lig simülasyonu.",
            color=0x2b2d31
        )
        embed.add_field(
            name="🏟️ TAKIM & OYUNCU YÖNETİMİ",
            value="`.takımkur Milan` | `.takımkadro Milan`\n`.oyuncu ekle Milan @Oyuncu` (Yetkili)\n`.oyuncu çıkar Milan @Oyuncu` (Yetkili)",
            inline=False
        )
        embed.add_field(
            name="📅 FİKSTÜR SİSTEMİ",
            value="`.fikstüroluştur` | `.fikstür` | `.haftayıoynat`",
            inline=False
        )
        embed.add_field(
            name="📊 İSTATİSTİK & SİSTEM",
            value="`.puan` (Puan Durumu)\n`.krallık` (Gol ve Asist Krallığı)",
            inline=False
        )
        embed.set_footer(text="Tendo League • Match Engine V3.1")
        await ctx.send(embed=embed)

    @commands.command(name="takımkur", aliases=["takimkur"])
    async def takim_kur(self, ctx, *, takim_adi: str = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi:
            await ctx.send("⚠️ Kullanım: `.takımkur <TakımAdı>`")
            return

        key = takim_adi.lower()
        if key in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** zaten kurulmuş.")
            return

        self.takimlar[key] = {
            "orj_ad": takim_adi,
            "oyuncular": [],
            "om": 0, "g": 0, "b": 0, "m": 0,
            "ag": 0, "yg": 0, "av": 0, "puan": 0
        }
        await ctx.send(f"✅ **{takim_adi}** takımı başarıyla oluşturuldu!")

    # OYUNCU KOMUT GRUBU (.oyuncu ekle <takım> @oyuncu)
    @commands.group(name="oyuncu", invoke_without_command=True)
    async def oyuncu_group(self, ctx):
        await ctx.send("⚠️ Kullanım: `.oyuncu ekle <Takım> @Oyuncu` veya `.oyuncu çıkar <Takım> @Oyuncu`")

    @oyuncu_group.command(name="ekle")
    async def oyuncu_ekle_sub(self, ctx, takim_adi: str = None, member: discord.Member = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi or not member:
            await ctx.send("⚠️ Kullanım: `.oyuncu ekle <TakımAdı> @Oyuncu`")
            return

        key = takim_adi.lower()
        if key not in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** takımı bulunamadı.")
            return

        # Oyuncu başka takımda var mı kontrolü
        for t_key, t_val in self.takimlar.items():
            for o in t_val["oyuncular"]:
                if o["member"].id == member.id:
                    t_val["oyuncular"].remove(o)
                    break

        o_bilgi = self.nickname_oku(member)
        self.takimlar[key]["oyuncular"].append(o_bilgi)

        embed = discord.Embed(
            description=f"✅ **{o_bilgi['isim']}** takıma eklendi!\n\n"
                        f"👤 **Oyuncu:** {o_bilgi['isim']}\n"
                        f"🌐 **Ülke:** {o_bilgi['bayrak']}\n"
                        f"📍 **Pozisyon:** {o_bilgi['mevki']}\n"
                        f"💰 **Piyasa Değeri:** {o_bilgi['deger_str']}\n\n"
                        f"🏟️ **Takım:** {self.takimlar[key]['orj_ad']}\n"
                        f"👥 **Kadro:** {len(self.takimlar[key]['oyuncular'])} kişi",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @oyuncu_group.command(name="çıkar", aliases=["cikar"])
    async def oyuncu_cikar_sub(self, ctx, takim_adi: str = None, member: discord.Member = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi or not member:
            await ctx.send("⚠️ Kullanım: `.oyuncu çıkar <TakımAdı> @Oyuncu`")
            return

        key = takim_adi.lower()
        if key not in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** takımı bulunamadı.")
            return

        kadro = self.takimlar[key]["oyuncular"]
        yeni_kadro = [o for o in kadro if o["member"].id != member.id]
        
        if len(kadro) == len(yeni_kadro):
            await ctx.send(f"❌ Bu oyuncu **{self.takimlar[key]['orj_ad']}** kadrosunda yok.")
            return

        self.takimlar[key]["oyuncular"] = yeni_kadro
        o_bilgi = self.nickname_oku(member)
        await ctx.send(f"✅ **{o_bilgi['isim']}** oyuncusu **{self.takimlar[key]['orj_ad']}** takımından çıkarıldı.")

    # Alternatif Doğrudan Komut (.oyuncuekle)
    @commands.command(name="oyuncuekle")
    async def oyuncu_ekle_direkt(self, ctx, takim_adi: str = None, member: discord.Member = None):
        await ctx.invoke(self.oyuncu_ekle_sub, takim_adi=takim_adi, member=member)

    @commands.command(name="takımkadro", aliases=["takimkadro"])
    async def takim_kadro(self, ctx, *, takim_adi: str = None):
        if not takim_adi:
            await ctx.send("⚠️ Kullanım: `.takımkadro <TakımAdı>`")
            return

        key = takim_adi.lower()
        if key not in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** takımı bulunamadı.")
            return

        takim = self.takimlar[key]
        embed = discord.Embed(
            title=f"⚽ {takim['orj_ad']} — KADRO",
            description=f"👥 **Kadro:** {len(takim['oyuncular'])} kişi\n\n📋 **OYUNCULAR**",
            color=0x2b2d31
        )

        if not takim["oyuncular"]:
            embed.description += "\nHenüz oyuncu yok."
        else:
            liste = ""
            for i, o in enumerate(takim["oyuncular"], 1):
                st = self.istatistikler[o["id"]]
                durum = ""
                if st["ceza_maci"] > 0: durum += f" 🟥 (Cezalı: {st['ceza_maci']} Maç)"
                if st["sakatlik_maci"] > 0: durum += f" 🏥 (Sakat: {st['sakatlik_maci']} Maç)"
                
                liste += f"**{i}.** {o['mevki']} **{o['isim']}** | {o['bayrak']} | 💰 {o['deger_str']}{durum}\n"
            embed.description += f"\n{liste}"

        await ctx.send(embed=embed)

    # FİKSTÜR VE İLERLEME
    @commands.command(name="fikstüroluştur", aliases=["fiksturolustur"])
    async def fikstur_olustur(self, ctx):
        if not ctx.author.guild_permissions.administrator: return
        takim_listesi = [t["orj_ad"] for t in self.takimlar.values()]
        if len(takim_listesi) < 2:
            await ctx.send("❌ En az 2 takım gereklidir.")
            return
        if len(takim_listesi) % 2 != 0:
            takim_listesi.append("BAY")

        n = len(takim_listesi)
        haftalar = []
        for hafta in range(n - 1):
            maclar = []
            for i in range(n // 2):
                t1, t2 = takim_listesi[i], takim_listesi[n - 1 - i]
                if t1 != "BAY" and t2 != "BAY":
                    maclar.append((t1, t2))
            haftalar.append(maclar)
            takim_listesi.insert(1, takim_listesi.pop())

        self.fikstur = haftalar
        self.aktif_hafta = 0
        await ctx.send(f"📅 **{len(haftalar)} Haftalık** Fikstür Başarıyla Oluşturuldu!")

    @commands.command(name="fikstür", aliases=["fikstur"])
    async def fikstur_goster(self, ctx):
        if not self.fikstur:
            await ctx.send("❌ Fikstür oluşturulmamış.")
            return
        embed = discord.Embed(title="📅 TENDO LEAGUE — FİKSTÜR", color=0x2b2d31)
        for idx, hafta in enumerate(self.fikstur, 1):
            durum = " (Oynandı)" if idx <= self.aktif_hafta else ""
            mac_metni = "".join([f"⚽ **{t1}** vs **{t2}**\n" for t1, t2 in hafta])
            embed.add_field(name=f"📍 {idx}. Hafta{durum}", value=mac_metni, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="haftayıoynat", aliases=["haftayioynat"])
    async def haftayi_oynat(self, ctx):
        if not ctx.author.guild_permissions.administrator: return
        if not self.fikstur or self.aktif_hafta >= len(self.fikstur):
            await ctx.send("❌ Oynanacak hafta kalmadı veya fikstür yok.")
            return

        hafta_maclari = self.fikstur[self.aktif_hafta]
        self.aktif_hafta += 1
        await ctx.send(f"📢 **{self.aktif_hafta}. HAFTA MAÇLARI BAŞLIYOR!**")

        for t1_ad, t2_ad in hafta_maclari:
            await self.simule_et(ctx, t1_ad, t2_ad)
            await asyncio.sleep(2)

    # GOL & ASİST KRALLIĞI
    @commands.command(name="krallık", aliases=["krallik"])
    async def krallik_goster(self, ctx):
        golculer = sorted(self.istatistikler.values(), key=lambda x: x["gol"], reverse=True)[:5]
        asistciler = sorted(self.istatistikler.values(), key=lambda x: x["asist"], reverse=True)[:5]

        gol_txt = "\n".join([f"⚽ **{p['isim']}**: {p['gol']} Gol" for p in golculer if p['gol'] > 0]) or "Henüz gol yok."
        asist_txt = "\n".join([f"🅰️ **{p['isim']}**: {p['asist']} Asist" for p in asistciler if p['asist'] > 0]) or "Henüz asist yok."

        embed = discord.Embed(title="👑 TENDO LEAGUE — İSTATİSTİK KRALLIĞI", color=0x2b2d31)
        embed.add_field(name="🎯 GOL KRALLIĞI", value=gol_txt, inline=False)
        embed.add_field(name="🅰️ ASİST KRALLIĞI", value=asist_txt, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="puan", aliases=["puandurumu"])
    async def puan_durumu(self, ctx):
        if not self.takimlar:
            await ctx.send("❌ Takım bulunmuyor.")
            return

        siralama = sorted(self.takimlar.values(), key=lambda x: (x["puan"], x["av"], x["ag"]), reverse=True)
        tablo = "```\n"
        tablo += f"{'#':<3} {'Takım':<14} {'OM':<3} {'G':<3} {'B':<3} {'M':<3} {'AG':<4} {'YG':<4} {'AV':<4} {'P':<3}\n"
        tablo += "─" * 50 + "\n"
        for idx, t in enumerate(siralama, 1):
            tablo += f"{idx:<3} {t['orj_ad'][:13]:<14} {t['om']:<3} {t['g']:<3} {t['b']:<3} {t['m']:<3} {t['ag']:<4} {t['yg']:<4} {t['av']:<4} {t['puan']:<3}\n"
        tablo += "```"

        embed = discord.Embed(title="🏆 TENDO LEAGUE — PUAN DURUMU", description=tablo, color=0x2b2d31)
        await ctx.send(embed=embed)

    # MAÇ MOTORU
    async def simule_et(self, ctx, t1_ad, t2_ad):
        t1, t2 = self.takimlar[t1_ad.lower()], self.takimlar[t2_ad.lower()]

        def uygun_kadro(oyuncular):
            uygun = []
            for o in oyuncular:
                st = self.istatistikler[o["id"]]
                if st["ceza_maci"] > 0 or st["sakatlik_maci"] > 0:
                    continue
                uygun.append(o)
            return uygun

        k1_aktif = uygun_kadro(t1["oyuncular"])
        k2_aktif = uygun_kadro(t2["oyuncular"])

        skor1, skor2 = 0, 0
        default_p = {"id": 0, "isim": "Yedek Oyuncu", "mevki": "OS", "bayrak": "🌐", "deger_str": "1M", "reyting": 6.0}

        await ctx.send(f"🏟️ **{t1['orj_ad']} vs {t2['orj_ad']}** Maçı Başladı!")

        for dk in range(1, 90, random.randint(4, 9)):
            atak_t = t1 if random.choice([True, False]) else t2
            defans_t = t2 if atak_t == t1 else t1
            a_kadro = k1_aktif if atak_t == t1 else k2_aktif
            d_kadro = k2_aktif if atak_t == t1 else k1_aktif

            o_atak = random.choice(a_kadro) if a_kadro else default_p
            o_hedef = random.choice(a_kadro) if a_kadro else o_atak
            o_def = random.choice(d_kadro) if d_kadro else default_p

            olay = random.choices(["PAS", "ŞUT", "GOL", "SARI_KART", "KIRMIZI_KART", "SAKATLIK"], weights=[35, 20, 15, 10, 5, 5])[0]
            embed = discord.Embed(title=f"{dk}' {t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}", color=0x2b2d31)

            if olay == "GOL":
                if atak_t == t1: skor1 += 1
                else: skor2 += 1
                if o_atak["id"] != 0:
                    self.istatistikler[o_atak["id"]]["gol"] += 1
                if o_hedef["id"] != 0 and o_hedef["id"] != o_atak["id"]:
                    self.istatistikler[o_hedef["id"]]["asist"] += 1
                embed.description = f"⚽ **GOOOOL!** **{o_atak['isim']}** fileleri havalandırdı!"

            elif olay == "SARI_KART" and o_def["id"] != 0:
                st = self.istatistikler[o_def["id"]]
                st["sari_kart_toplam"] += 1
                if st["sari_kart_toplam"] % 2 == 0:
                    st["ceza_maci"] = 1
                    embed.description = f"🟨🟨 **İKİNCİ SARI KART!** **{o_def['isim']}** kırmızı kart gördü ve cezalı duruma düştü!"
                else:
                    embed.description = f"🟨 **SARI KART!** **{o_def['isim']}** sert müdahalesi nedeniyle sarı kart gördü."

            elif olay == "KIRMIZI_KART" and o_def["id"] != 0:
                self.istatistikler[o_def["id"]]["ceza_maci"] = 1
                embed.description = f"🟥 **DİREKT KIRMIZI KART!** **{o_def['isim']}** oyundan ihraç edildi!"

            elif olay == "SAKATLIK" and o_atak["id"] != 0:
                s_sure = random.randint(1, 3)
                self.istatistikler[o_atak["id"]]["sakatlik_maci"] = s_sure
                embed.description = f"🏥 **SAKATLIK!** **{o_atak['isim']}** sakatlandı! ({s_sure} maç yok)"

            elif olay == "ŞUT":
                embed.description = f"🎯 **ŞUT!** **{o_atak['isim']}** sert vurdu ancak top az farkla dışarıda."

            else:
                embed.description = f"🔄 **{o_atak['isim']}** orta sahada şık bir pas çıkardı."

            if olay in ["GOL", "SARI_KART", "KIRMIZI_KART", "SAKATLIK"]:
                await ctx.send(embed=embed)
                await asyncio.sleep(2)

        t1["om"] += 1; t2["om"] += 1
        t1["ag"] += skor1; t1["yg"] += skor2
        t2["ag"] += skor2; t2["yg"] += skor1
        t1["av"] = t1["ag"] - t1["yg"]; t2["av"] = t2["ag"] - t2["yg"]

        if skor1 > skor2:
            t1["g"] += 1; t1["puan"] += 3; t2["m"] += 1
        elif skor2 > skor1:
            t2["g"] += 1; t2["puan"] += 3; t1["m"] += 1
        else:
            t1["b"] += 1; t2["b"] += 1; t1["puan"] += 1; t2["puan"] += 1

        for o in t1["oyuncular"] + t2["oyuncular"]:
            st = self.istatistikler[o["id"]]
            if st["ceza_maci"] > 0: st["ceza_maci"] -= 1
            if st["sakatlik_maci"] > 0: st["sakatlik_maci"] -= 1

        res_embed = discord.Embed(
            title="🔔 MAÇ SONUCU",
            description=f"🏁 **{t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}**",
            color=0x2b2d31
        )
        await ctx.send(embed=res_embed)

    @commands.command(name="takımaç", aliases=["takimac"])
    async def takim_mac(self, ctx, t1_ad: str = None, t2_ad: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not t1_ad or not t2_ad:
            await ctx.send("⚠️ Kullanım: `.takımaç <Takım1> <Takım2>`")
            return
        await self.simule_et(ctx, t1_ad, t2_ad)

async def setup(bot):
    await bot.add_cog(MacSistemi(bot))
