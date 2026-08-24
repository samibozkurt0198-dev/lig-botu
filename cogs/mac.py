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
        self.istatistikler = {}  # user_id: {isim, gol, asist, sari_kart, ceza_maci, om, mvp}

    def nickname_oku(self, member: discord.Member):
        display_name = member.display_name
        
        deger_match = re.search(r'(\d+(?:\.\d+)?)\s*M', display_name, re.IGNORECASE)
        deger_str = f"{deger_match.group(1)}M" if deger_match else "1M"

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
                "om": 0,
                "mvp": 0
            }

        return {
            "id": member.id,
            "member": member,
            "isim": temiz_isim[:14],
            "mevki": mevki,
            "bayrak": bayrak,
            "deger_str": deger_str
        }

    @commands.group(name="m", invoke_without_command=True)
    async def m_group(self, ctx):
        await ctx.invoke(self.mac_yardim)

    @m_group.command(name="yardım", aliases=["yardim"])
    async def mac_yardim(self, ctx):
        embed = discord.Embed(
            title="⚽ TENDO LEAGUE — GELİŞMİŞ MAÇ & YÖNETİM BOTU",
            description="🏆 Lig, Kupa, Transfer, Oyuncu Profilleri ve TOTW Yönetim Sistemi.",
            color=0x2b2d31
        )
        embed.add_field(
            name="🏟️ TAKIM & YÖNETİM",
            value="`.takımkur <Takım>` | `.takımkadro <Takım>`\n`.oyuncuekle <Takım> @Oyuncu`\n`.transfer <YeniTakım> @Oyuncu`",
            inline=False
        )
        embed.add_field(
            name="⚽ MAÇ & KUPA",
            value="`.fikstüroluştur` | `.haftayıoynat`\n`.takımaç T1 vs T2`\n`.kupamaçı T1 vs T2` (Penaltılı Eleme)",
            inline=False
        )
        embed.add_field(
            name="📊 İSTATİSTİK & PROFİL",
            value="`.puan` | `.krallık` | `.totw` (Haftanın 5'i)\n`.profil @Oyuncu` (Oyuncu Kartı)",
            inline=False
        )
        embed.set_footer(text="Tendo League • Ultimate Engine V4.0")
        await ctx.send(embed=embed)

    @commands.command(name="takımkur", aliases=["takimkur"])
    async def takim_kur(self, ctx, *, takim_adi: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not takim_adi:
            await ctx.send("⚠️ Kullanım: `.takımkur <TakımAdı>`")
            return

        key = takim_adi.lower().strip()
        if key in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** zaten kurulmuş.")
            return

        self.takimlar[key] = {
            "orj_ad": takim_adi.strip(),
            "oyuncular": [],
            "om": 0, "g": 0, "b": 0, "m": 0,
            "ag": 0, "yg": 0, "av": 0, "puan": 0
        }
        await ctx.send(f"✅ **{takim_adi}** takımı başarıyla oluşturuldu!")

    @commands.command(name="oyuncuekle")
    async def oyuncu_ekle_direkt(self, ctx, *, argumanlar: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not argumanlar or not ctx.message.mentions:
            await ctx.send("⚠️ Kullanım: `.oyuncuekle <Takım Adı> @Oyuncu`")
            return

        member = ctx.message.mentions[0]
        takim_adi = re.sub(r'<@!?\d+>', '', argumanlar).strip()

        key = takim_adi.lower()
        if key not in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** takımı bulunamadı.")
            return

        for t_key, t_val in self.takimlar.items():
            for o in t_val["oyuncular"]:
                if o["member"].id == member.id:
                    t_val["oyuncular"].remove(o)
                    break

        o_bilgi = self.nickname_oku(member)
        self.takimlar[key]["oyuncular"].append(o_bilgi)
        await ctx.send(f"✅ **{o_bilgi['isim']}** oyuncusu **{self.takimlar[key]['orj_ad']}** kadrosuna eklendi!")

    @commands.command(name="transfer")
    async def transfer_yap(self, ctx, *, argumanlar: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not argumanlar or not ctx.message.mentions:
            await ctx.send("⚠️ Kullanım: `.transfer <YeniTakım> @Oyuncu`")
            return

        member = ctx.message.mentions[0]
        yeni_takim_ad = re.sub(r'<@!?\d+>', '', argumanlar).strip()
        key = yeni_takim_ad.lower()

        if key not in self.takimlar:
            await ctx.send(f"❌ **{yeni_takim_ad}** takımı bulunamadı.")
            return

        # Eski takımdan çıkar
        eski_takim = "Serbest"
        for t_key, t_val in self.takimlar.items():
            for o in t_val["oyuncular"]:
                if o["member"].id == member.id:
                    eski_takim = t_val["orj_ad"]
                    t_val["oyuncular"].remove(o)
                    break

        o_bilgi = self.nickname_oku(member)
        self.takimlar[key]["oyuncular"].append(o_bilgi)

        embed = discord.Embed(
            title="🔄 TRANSFER AÇIKLANDI!",
            description=f"👤 **Oyuncu:** {o_bilgi['isim']}\n"
                        f"📤 **Eski Takım:** {eski_takim}\n"
                        f"📥 **Yeni Takım:** {self.takimlar[key]['orj_ad']}",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.command(name="profil")
    async def oyuncu_profili(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        st = self.istatistikler.get(member.id)
        if not st:
            await ctx.send("❌ Oyuncu verisi bulunamadı.")
            return

        takim_adi = "Serbest Oyuncu"
        for t_val in self.takimlar.values():
            if any(o["member"].id == member.id for o in t_val["oyuncular"]):
                takim_adi = t_val["orj_ad"]
                break

        o_info = self.nickname_oku(member)
        embed = discord.Embed(
            title=f"👤 OYUNCU PROFİLİ — {st['isim']}",
            color=0x2b2d31
        )
        embed.add_field(name="🏟️ Takım", value=takim_adi, inline=True)
        embed.add_field(name="📍 Pozisyon", value=o_info["mevki"], inline=True)
        embed.add_field(name="🌐 Ülke", value=o_info["bayrak"], inline=True)
        embed.add_field(name="👕 Maç Sayısı", value=str(st["om"]), inline=True)
        embed.add_field(name="⚽ Gol", value=str(st["gol"]), inline=True)
        embed.add_field(name="🅰️ Asist", value=str(st["asist"]), inline=True)
        embed.add_field(name="🌟 MVP (Maçın Adamı)", value=f"{st['mvp']} Kez", inline=True)
        embed.add_field(name="🟨 Sarı Kart", value=str(st["sari_kart_toplam"]), inline=True)
        
        ceza_durumu = "Temiz" if st["ceza_maci"] == 0 else f"🟥 Cezalı ({st['ceza_maci']} Maç)"
        embed.add_field(name="🚨 Ceza Durumu", value=ceza_durumu, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="totw")
    async def totw_goster(self, ctx):
        en_iyiler = sorted(self.istatistikler.values(), key=lambda x: (x["mvp"], x["gol"] + x["asist"]), reverse=True)[:5]
        
        if not en_iyiler or en_iyiler[0]["mvp"] == 0:
            await ctx.send("❌ Henüz TOTW belirlenmesi için yeterli maç oynanmadı.")
            return

        txt = ""
        for idx, p in enumerate(en_iyiler, 1):
            txt += f"**{idx}.** ⭐ **{p['isim']}** — 🌟 {p['mvp']} MVP | ⚽ {p['gol']} Gol | 🅰️ {p['asist']} Asist\n"

        embed = discord.Embed(
            title="⭐ HAFTANIN EN İYİLERİ (TOTW)",
            description=txt,
            color=0x2b2d31
        )
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

    # GELİŞMİŞ MAÇ MOTORU & İSTATİSTİK
    async def simule_et(self, ctx, t1_ad, t2_ad, is_kupa=False):
        t1, t2 = self.takimlar[t1_ad.lower()], self.takimlar[t2_ad.lower()]

        def uygun_kadro(oyuncular):
            return [o for o in oyuncular if self.istatistikler[o["id"]]["ceza_maci"] == 0]

        k1_aktif = uygun_kadro(t1["oyuncular"])
        k2_aktif = uygun_kadro(t2["oyuncular"])

        skor1, skor2 = 0, 0
        stats = {
            t1["orj_ad"]: {"sut": 0, "korner": 0, "faul": 0, "pas": 0},
            t2["orj_ad"]: {"sut": 0, "korner": 0, "faul": 0, "pas": 0}
        }

        mac_skorerleri = {}  # user_id: puan
        default_p = {"id": 0, "isim": "Yedek Oyuncu"}

        embed = discord.Embed(
            title=f"🏟️ {t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}",
            description="⏱️ **Dakika:** 0'\n⚽ Hakem düdüğü çaldı, maç başladı!",
            color=0x2b2d31
        )
        canli_mesaj = await ctx.send(embed=embed)

        toplam_dakika = 90
        for dk in range(1, toplam_dakika + 1):
            atak_t = t1 if random.choice([True, False]) else t2
            defans_t = t2 if atak_t == t1 else t1
            a_kadro = k1_aktif if atak_t == t1 else k2_aktif
            d_kadro = k2_aktif if atak_t == t1 else k1_aktif

            a_ad, d_ad = atak_t["orj_ad"], defans_t["orj_ad"]
            o_atak = random.choice(a_kadro) if a_kadro else default_p
            o_hedef = random.choice(a_kadro) if a_kadro else o_atak
            o_def = random.choice(d_kadro) if d_kadro else default_p

            olay = random.choices(
                ["PAS", "SUT", "GOL", "KORNER", "FAUL", "SARI_KART", "KIRMIZI_KART"],
                weights=[45, 20, 12, 10, 8, 3, 2]
            )[0]

            olay_metni = ""
            stats[a_ad]["pas"] += random.randint(3, 8)

            if olay == "GOL":
                if atak_t == t1: skor1 += 1
                else: skor2 += 1
                stats[a_ad]["sut"] += 1
                
                if o_atak["id"] != 0:
                    self.istatistikler[o_atak["id"]]["gol"] += 1
                    mac_skorerleri[o_atak["id"]] = mac_skorerleri.get(o_atak["id"], 0) + 3
                if o_hedef["id"] != 0 and o_hedef["id"] != o_atak["id"]:
                    self.istatistikler[o_hedef["id"]]["asist"] += 1
                    mac_skorerleri[o_hedef["id"]] = mac_skorerleri.get(o_hedef["id"], 0) + 2
                
                olay_metni = f"⚽ **GOOOOL!** **{o_atak['isim']}** mükemmel vurdu ve ağları havalandırdı!"

            elif olay == "SUT":
                stats[a_ad]["sut"] += 1
                if o_atak["id"] != 0: mac_skorerleri[o_atak["id"]] = mac_skorerleri.get(o_atak["id"], 0) + 1
                olay_metni = f"🎯 **ŞUT!** **{o_atak['isim']}** kaleyi denedi, top az farkla dışarıda."

            elif olay == "KORNER":
                stats[a_ad]["korner"] += 1
                olay_metni = f"📐 **KORNER!** Savunmaya çarpan top kornere çıktı."

            elif olay == "FAUL":
                stats[d_ad]["faul"] += 1
                olay_metni = f"⚠️ **FAUL!** **{o_def['isim']}** rakibini faulle durdurdu."

            elif olay == "SARI_KART" and o_def["id"] != 0:
                stats[d_ad]["faul"] += 1
                st = self.istatistikler[o_def["id"]]
                st["sari_kart_toplam"] += 1
                if st["sari_kart_toplam"] % 2 == 0:
                    st["ceza_maci"] = 1
                    olay_metni = f"🟨🟨 **İKİNCİ SARI KART!** **{o_def['isim']}** kırmızıyı gördü!"
                else:
                    olay_metni = f"🟨 **SARI KART!** **{o_def['isim']}** sarı kartla cezalandırıldı."

            elif olay == "KIRMIZI_KART" and o_def["id"] != 0:
                self.istatistikler[o_def["id"]]["ceza_maci"] = 1
                olay_metni = f"🟥 **KIRMIZI KART!** **{o_def['isim']}** oyundan ihraç edildi!"

            else:
                olay_metni = f"🔄 **{o_atak['isim']}** orta sahada şık paslarla takımını ileri taşıyor."

            embed.title = f"🏟️ {t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}"
            embed.description = f"⏱️ **Dakika:** {dk}'\n{olay_metni}"
            await canli_mesaj.edit(embed=embed)
            await asyncio.sleep(0.7)

        # Uzatma / Penaltılar (Kupa Maçı İse)
        penalti_metni = ""
        if is_kupa and skor1 == skor2:
            await ctx.send("⏳ **90 Dakika Berabere Bitti! Penaltı Atışlarına Geçiliyor...**")
            p1, p2 = 0, 0
            for i in range(1, 6):
                if random.choice([True, False]): p1 += 1
                if random.choice([True, False]): p2 += 1
            while p1 == p2:
                if random.choice([True, False]): p1 += 1
                if random.choice([True, False]): p2 += 1
            
            kazanan_t = t1['orj_ad'] if p1 > p2 else t2['orj_ad']
            penalti_metni = f"\n\n🎯 **PENALTILAR:** {t1['orj_ad']} {p1} - {p2} {t2['orj_ad']}\n🏆 **TUR ATLAYAN:** {kazanan_t}"

        # Topla Oynama Hesabı
        t_pas = stats[t1["orj_ad"]]["pas"] + stats[t2["orj_ad"]]["pas"]
        top_1 = round((stats[t1["orj_ad"]]["pas"] / t_pas) * 100) if t_pas > 0 else 50
        top_2 = 100 - top_1

        # MVP Seçimi
        mvp_isim = "Yok"
        if mac_skorerleri:
            mvp_id = max(mac_skorerleri, key=mac_skorerleri.get)
            self.istatistikler[mvp_id]["mvp"] += 1
            mvp_isim = self.istatistikler[mvp_id]["isim"]

        # Maç Sonu Detay Tablosu
        res_embed = discord.Embed(
            title="🔔 MAÇ BİTTİ — DETAYLI SÖZLEŞME & İSTATİSTİK",
            description=f"🏁 **{t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}**{penalti_metni}\n\n🌟 **Maçın Adamı (MVP):** {mvp_isim}",
            color=0x2b2d31
        )
        
        stat_ozet = (
            f"```\n"
            f"{t1['orj_ad'][:10]:<12} | İSTATİSTİK | {t2['orj_ad'][:10]:>12}\n"
            f"───────────────────────────────────────────\n"
            f"%{top_1:<11} | Topla Oynama | %{top_2:>11}\n"
            f"{stats[t1['orj_ad']]['sut']:<12} | Toplam Şut   | {stats[t2['orj_ad']]['sut']:>12}\n"
            f"{stats[t1['orj_ad']]['korner']:<12} | Korner       | {stats[t2['orj_ad']]['korner']:>12}\n"
            f"{stats[t1['orj_ad']]['faul']:<12} | Faul         | {stats[t2['orj_ad']]['faul']:>12}\n"
            f"```"
        )
        res_embed.add_field(name="📊 MAÇ İSTATİSTİKLERİ", value=stat_ozet, inline=False)
        await ctx.send(embed=res_embed)

        # Lig puan güncellemeleri
        if not is_kupa:
            t1["om"] += 1; t2["om"] += 1
            t1["ag"] += skor1; t1["yg"] += skor2
            t2["ag"] += skor2; t2["yg"] += skor1
            t1["av"] = t1["ag"] - t1["yg"]; t2["av"] = t2["ag"] - t2["yg"]

            if skor1 > skor2: t1["g"] += 1; t1["puan"] += 3; t2["m"] += 1
            elif skor2 > skor1: t2["g"] += 1; t2["puan"] += 3; t1["m"] += 1
            else: t1["b"] += 1; t2["b"] += 1; t1["puan"] += 1; t2["puan"] += 1

            for o in t1["oyuncular"] + t2["oyuncular"]:
                st = self.istatistikler[o["id"]]
                st["om"] += 1
                if st["ceza_maci"] > 0: st["ceza_maci"] -= 1

    @commands.command(name="takımaç", aliases=["takimac"])
    async def takim_mac(self, ctx, *, argumanlar: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not argumanlar or " vs " not in argumanlar.lower():
            await ctx.send("⚠️ Kullanım: `.takımaç Takım1 vs Takım2`")
            return
        t1_ad, t2_ad = argumanlar.lower().split(" vs ")
        await self.simule_et(ctx, t1_ad.strip(), t2_ad.strip(), is_kupa=False)

    @commands.command(name="kupamaçı", aliases=["kupamaci"])
    async def kupa_maci(self, ctx, *, argumanlar: str = None):
        if not ctx.author.guild_permissions.administrator: return
        if not argumanlar or " vs " not in argumanlar.lower():
            await ctx.send("⚠️ Kullanım: `.kupamaçı Takım1 vs Takım2`")
            return
        t1_ad, t2_ad = argumanlar.lower().split(" vs ")
        await self.simule_et(ctx, t1_ad.strip(), t2_ad.strip(), is_kupa=True)

async def setup(bot):
    await bot.add_cog(MacSistemi(bot))

