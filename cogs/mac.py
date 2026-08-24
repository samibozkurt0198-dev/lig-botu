import discord
from discord.ext import commands
import asyncio
import random
import re

class MacSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.takimlar = {}

    def nickname_oku(self, member: discord.Member):
        display_name = member.display_name
        
        deger_match = re.search(r'(\d+(?:\.\d+)?)\s*M', display_name, re.IGNORECASE)
        deger_str = f"{deger_match.group(1)}M" if deger_match else "0M"
        deger_sayi = float(deger_match.group(1)) if deger_match else 0.0

        mevki_match = re.search(r'\b(KL|STP|SLB|SĞB|DOS|OS|OOS|SLK|SĞK|SNT|FRV)\b', display_name, re.IGNORECASE)
        mevki = mevki_match.group(1).upper() if mevki_match else "OS"

        bayrak_match = re.search(r'[\U0001F1E6-\U0001F1FF]{2}', display_name)
        bayrak = bayrak_match.group(0) if bayrak_match else "🌐"

        temiz_isim = re.sub(r'\[.*?\]|\(.*?\)', '', display_name).strip()
        temiz_isim = temiz_isim.split('|')[0].strip()
        if "@" in temiz_isim:
            temiz_isim = temiz_isim.replace("@", "")

        return {
            "member": member,
            "isim": temiz_isim[:14],
            "mevki": mevki,
            "bayrak": bayrak,
            "deger_str": deger_str,
            "deger_sayi": deger_sayi,
            "reyting": round(random.uniform(5.5, 8.5), 1),
            "gol": 0, "asist": 0, "sut": 0, "pas": 0
        }

    # POLİTİKA: '.m' ana komut grubu oluşturuldu
    @commands.group(name="m", invoke_without_command=True)
    async def m_group(self, ctx):
        await ctx.invoke(self.mac_yardim)

    # .m yardım VEYA .maçyardım
    @m_group.command(name="yardım", aliases=["yardim"])
    async def mac_yardim(self, ctx):
        embed = discord.Embed(
            title="⚽ ZENITH LEAGUE — MAÇ BOTU",
            description="🎡 Gelişmiş takım ve maç simülasyon sistemi.\n\nOyuncu bilgileri Discord nickname'inden otomatik okunur.",
            color=0x2b2d31
        )
        embed.add_field(
            name="🏟️ TAKIM SİSTEMİ",
            value="`.takımkur Milan`\n`.takımkadro Milan`\n`.takımoyuncuekle Milan @Oyuncu`\n`.takımoyuncuçıkar Milan @Oyuncu`",
            inline=False
        )
        embed.add_field(
            name="⚽ MAÇ SİSTEMİ",
            value="`.takımaç Milan PSG` veya `.m aç Milan PSG`",
            inline=False
        )
        embed.add_field(
            name="👤 OYUNCU SİSTEMİ",
            value="Nickname formatı:\n`C.Ronaldo | 🇵🇹 | SNT | 89M`",
            inline=False
        )
        embed.set_footer(text="Zenith League • Match Engine V2.3")
        await ctx.send(embed=embed)

    @commands.command(name="takımkur", aliases=["takimkur"])
    async def takim_kur(self, ctx, *, takim_adi: str = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi:
            await ctx.send("⚠️ Kullanım: `.takımkur <TakımAdı>`")
            return

        self.takimlar[takim_adi.lower()] = {"orj_ad": takim_adi, "oyuncular": []}
        await ctx.send(f"✅ **{takim_adi}** takımı başarıyla oluşturuldu!")

    @commands.command(name="takımoyuncuekle", aliases=["takimoyuncuekle"])
    async def oyuncu_ekle(self, ctx, takim_adi: str = None, member: discord.Member = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi or not member:
            await ctx.send("⚠️ Kullanım: `.takımoyuncuekle <TakımAdı> @Oyuncu`")
            return

        key = takim_adi.lower()
        if key not in self.takimlar:
            await ctx.send(f"❌ **{takim_adi}** takımı bulunamadı.")
            return

        o_bilgi = self.nickname_oku(member)
        self.takimlar[key]["oyuncular"].append(o_bilgi)

        embed = discord.Embed(
            description=f"✅ **{o_bilgi['isim']}** takıma eklendi!\n\n"
                        f"👤 **Oyuncu:** {o_bilgi['isim']}\n"
                        f"🌐 **Ülke:** {o_bilgi['mevki']}\n"
                        f"📍 **Pozisyon:** {o_bilgi['bayrak']}\n"
                        f"💰 **Piyasa Değeri:** {o_bilgi['deger_str']}\n\n"
                        f"🏟️ **Takım:** {self.takimlar[key]['orj_ad']}\n"
                        f"👥 **Kadro:** {len(self.takimlar[key]['oyuncular'])} kişi",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.command(name="takımoyuncuçıkar", aliases=["takimoyuncucikar"])
    async def oyuncu_cikar(self, ctx, takim_adi: str = None, member: discord.Member = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not takim_adi or not member:
            await ctx.send("❌ **Kullanım:** `.takımoyuncuçıkar <TakımAdı> @Oyuncu`")
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
        oyuncular = takim["oyuncular"]

        embed = discord.Embed(
            title=f"⚽ {takim['orj_ad']} — KADRO",
            description=f"👥 **Kadro:** {len(oyuncular)} kişi\n\n📋 **OYUNCULAR**",
            color=0x2b2d31
        )

        if not oyuncular:
            embed.description += "\nHenüz oyuncu eklenmemiş."
        else:
            liste = ""
            for i, o in enumerate(oyuncular, 1):
                liste += f"**{i}.** {o['mevki']} **{o['isim']}** | {o['bayrak']} | 💰 **{o['deger_str']}**\n"
            embed.description += f"\n{liste}"

        await ctx.send(embed=embed)

    @commands.command(name="takımaç", aliases=["takimac"])
    async def takim_mac(self, ctx, t1_ad: str = None, t2_ad: str = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Bu komutu sadece yöneticiler kullanabilir.")
            return
        if not t1_ad or not t2_ad:
            await ctx.send("⚠️ Kullanım: `.takımaç <Takım1> <Takım2>`")
            return

        k1, k2 = t1_ad.lower(), t2_ad.lower()
        if k1 not in self.takimlar or k2 not in self.takimlar:
            await ctx.send("❌ Belirtilen takımlardan biri veya ikisi sistemde kayıtlı değil!")
            return

        t1 = self.takimlar[k1]
        t2 = self.takimlar[k2]

        init_embed = discord.Embed(
            title="🏟️ ZENITH LEAGUE",
            description=f"🇹🇷 **{t1['orj_ad']} 0 - 0 {t2['orj_ad']}**\n\n⏰ **Maç başlatılıyor...**",
            color=0x2b2d31
        )
        await ctx.send(embed=init_embed)
        await asyncio.sleep(2)

        start_embed = discord.Embed(
            title="🏟️ ZENITH LEAGUE — MAÇ BAŞLADI!",
            description=f"🇹🇷 **{t1['orj_ad']} 0 - 0 {t2['orj_ad']}**",
            color=0x2b2d31
        )

        def kadro_str(oyuncular):
            if not oyuncular: return "Oyuncu yok"
            return "\n".join([f"{i+1}. {o['mevki']} **{o['isim']}** | {o['bayrak']} | {o['deger_str']}" for i, o in enumerate(oyuncular)])

        start_embed.add_field(name=f"👥 {t1['orj_ad']}", value=kadro_str(t1["oyuncular"]), inline=False)
        start_embed.add_field(name=f"👥 {t2['orj_ad']}", value=kadro_str(t2["oyuncular"]), inline=False)
        start_embed.set_footer(text="⚽ Oyuncu değerleri nickname'den otomatik okunuyor.")
        await ctx.send(embed=start_embed)
        await asyncio.sleep(3)

        skor1, skor2 = 0, 0
        toplam_pas1, toplam_pas2 = 0, 0
        sut1, sut2 = 0, 0
        isabetli1, isabetli2 = 0, 0

        for dk in range(1, 90, random.randint(3, 8)):
            atak_takim = t1 if random.choice([True, False]) else t2
            defans_takim = t2 if atak_takim == t1 else t1
            
            o_atak = random.choice(atak_takim["oyuncular"]) if atak_takim["oyuncular"] else {"isim": "Oyuncu", "mevki": "OS", "bayrak": "🇹🇷", "deger_str": "1M", "reyting": 6.0}
            o_hedef = random.choice(atak_takim["oyuncular"]) if atak_takim["oyuncular"] else o_atak
            o_def = random.choice(defans_takim["oyuncular"]) if defans_takim["oyuncular"] else {"isim": "Defans", "mevki": "STP", "bayrak": "🇹🇷", "deger_str": "1M", "reyting": 6.0}

            olay = random.choices(["PAS", "PAS_HATASI", "ORTA", "ATAK", "MÜDAHALE", "ŞUT", "GOL"], weights=[30, 15, 10, 15, 10, 10, 10])[0]

            embed = discord.Embed(title=f"{dk}' {t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}", color=0x2b2d31)
            embed.set_footer(text="Zenith League • Maç Motoru V2.3")

            if olay == "PAS":
                m = random.randint(8, 35)
                if atak_takim == t1: toplam_pas1 += 1
                else: toplam_pas2 += 1
                o_atak["pas"] += 1
                embed.description = (
                    f"🎯 **PAS!**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} | 💰 {o_atak['deger_str']} oyunu kurdu.\n\n"
                    f"📏 **{m} metrelik** isabetli pasla **{o_hedef['isim']}** oyuncusunu buldu!"
                )

            elif olay == "PAS_HATASI":
                m = random.randint(10, 30)
                embed.description = (
                    f"❌ **PAS HATASI!**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} | 💰 {o_atak['deger_str']} {m} metrelik pasını gönderdi fakat top rakibe gitti!"
                )

            elif olay == "ORTA":
                m = random.randint(15, 30)
                embed.description = (
                    f"🌪️ **ORTA!**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} kanattan **{m} metreden** ortayı açtı.\n\n"
                    f"🎯 Top **{o_hedef['isim']}** oyuncusuna doğru geliyor!"
                )

            elif olay == "ATAK":
                embed.description = (
                    f"⚡ **ATAK!**\n\n"
                    f"**{atak_takim['orj_ad']}** hızlı bir şekilde rakip yarı sahaya yerleşti.\n\n"
                    f"📍 Top ceza sahasına doğru ilerliyor..."
                )

            elif olay == "MÜDAHALE":
                embed.description = (
                    f"🛡️ **MÜDAHALE!**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} atağa kalktı.\n\n"
                    f"🛡️ **{o_def['isim']}** {o_def['mevki']} | {o_def['bayrak']} zamanında kayarak topu aldı!"
                )

            elif olay == "ŞUT":
                m = random.randint(10, 28)
                if atak_takim == t1: 
                    sut1 += 1; isabetli1 += 1
                else: 
                    sut2 += 1; isabetli2 += 1
                o_atak["sut"] += 1
                embed.description = (
                    f"🎯 **İSABETLİ ŞUT!**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} | 💰 {o_atak['deger_str']} **{m} metreden** vurdu, top kalecisiz kaleye gitti ama savunma son anda çizgiden uzaklaştırdı!"
                )

            elif olay == "GOL":
                if atak_takim == t1: 
                    skor1 += 1; sut1 += 1; isabetli1 += 1
                else: 
                    skor2 += 1; sut2 += 1; isabetli2 += 1
                o_atak["gol"] += 1
                o_hedef["asist"] += 1
                o_atak["reyting"] = min(10.0, round(o_atak["reyting"] + 1.2, 1))
                m = random.randint(6, 20)

                embed.description = (
                    f"⚽ **GOOOOOLLLLL! 🔥🔥🔥**\n\n"
                    f"**{o_atak['isim']}** {o_atak['mevki']} | {o_atak['bayrak']} | 💰 {o_atak['deger_str']} savunma arkasına sarktı!\n\n"
                    f"📍 Kaleye **{m} metre** mesafeden vurdu ve top ağlarda!\n\n"
                    f"🎯 **ASİST**\n"
                    f"**{o_hedef['isim']}** {o_hedef['mevki']} | {o_hedef['bayrak']} | 💰 {o_hedef['deger_str']}"
                )

            await ctx.send(embed=embed)
            await asyncio.sleep(2.5)

        kazanan = t1['orj_ad'] if skor1 > skor2 else (t2['orj_ad'] if skor2 > skor1 else "Berabere")
        
        tum_oyuncular = t1["oyuncular"] + t2["oyuncular"]
        mvp = max(tum_oyuncular, key=lambda x: x["reyting"]) if tum_oyuncular else {"isim": "Yok", "mevki": "OS", "bayrak": "🌐", "deger_str": "0M", "reyting": 0.0}

        end_embed1 = discord.Embed(
            title="🏆 ZENITH LEAGUE — MAÇ SONA ERDİ",
            description=f"**{t1['orj_ad']} {skor1} - {skor2} {t2['orj_ad']}**\n🏆 **{kazanan}**\n\n"
                        f"📊 **MAÇ İSTATİSTİKLERİ**\n"
                        f"⚽ **Goller:** {skor1 + skor2}\n"
                        f"🎯 **Şutlar:** {sut1 + sut2}\n"
                        f"🟨 **Sarı Kart:** 0\n"
                        f"⚠️ **Fauller:** 0\n"
                        f"🎯 **Toplam Pas:** {toplam_pas1 + toplam_pas2}\n"
                        f"🅰️ **Asistler:** {skor1 + skor2}\n\n"
                        f"⭐ **MAÇIN OYUNCUSU**\n"
                        f"👑 **{mvp['isim']}**\n"
                        f"{mvp['mevki']} | {mvp['bayrak']} | 💰 {mvp['deger_str']}\n"
                        f"⭐ **{mvp['reyting']}**",
            color=0x2b2d31
        )
        end_embed1.set_footer(text="Zenith League • Değer Bazlı Match Engine")
        await ctx.send(embed=end_embed1)

        def perf_str(oyuncular):
            if not oyuncular: return "Oyuncu yok"
            res = ""
            for i, o in enumerate(oyuncular, 1):
                res += f"{i}. 🟢 **{o['reyting']}** {o['mevki']} **{o['isim']}** | {o['bayrak']} | 💰 {o['deger_str']}\n"
                res += f"   ⚽ {o['gol']} • 🅰️ {o['asist']} • 🎯 {o['sut']} şut • 🎯 {o['pas']} pas\n"
            return res

        end_embed2 = discord.Embed(
            title="📋 MAÇ OYUNCU PERFORMANSLARI",
            description=f"**{t1['orj_ad']}**\n{perf_str(t1['oyuncular'])}\n\n**{t2['orj_ad']}**\n{perf_str(t2['oyuncular'])}",
            color=0x2b2d31
        )
        await ctx.send(embed=end_embed2)

        def bar_ciz(val1, val2, emoji1="🟥", emoji2="🟦"):
            total = val1 + val2
            if total == 0: return f"{emoji1*5}{emoji2*5}"
            ratio1 = int((val1 / total) * 10)
            return f"{emoji1 * ratio1}{emoji2 * (10 - ratio1)}"

        end_embed3 = discord.Embed(
            title="📊 Performans Karşılaştırması",
            description=f"🟦 **{t1['orj_ad']}** — **{t2['orj_ad']}** 🟥\n\n"
                        f"**Şut**\n{sut1} {bar_ciz(sut1, sut2)} {sut2}\n\n"
                        f"**İsabetli Şut**\n{isabetli1} {bar_ciz(isabetli1, isabetli2)} {isabetli2}\n\n"
                        f"**Pas**\n{toplam_pas1} {bar_ciz(toplam_pas1, toplam_pas2)} {toplam_pas2}\n\n"
                        f"🏆 **Daha iyi performans:** **{kazanan}**",
            color=0x2b2d31
        )
        await ctx.send(embed=end_embed3)

async def setup(bot):
    await bot.add_cog(MacSistemi(bot))
