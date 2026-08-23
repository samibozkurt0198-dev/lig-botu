import discord
from discord.ext import commands

class Kadro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- GENEL KADRO / TAKTİK DUYURU KOMUTU (.kadro) ---
    @commands.command(name="kadro")
    async def kadro(self, ctx, dizilis: str = None, taktik: str = None, gorsel_url: str = None):
        # Yetki veya Rol Kontrolü (Teknik Direktör veya Yönetici)
        td_rol = discord.utils.get(ctx.author.roles, name="Teknik Direktör")
        if not (ctx.author.guild_permissions.administrator or td_rol or any("T.D." in r.name for r in ctx.author.roles)):
            await ctx.send("❌ Bu komutu sadece **Teknik Direktör** rolüne sahip kişiler kullanabilir!")
            return

        if not dizilis or not taktik:
            await ctx.send("⚠️ **Kullanım:** `.kadro <Diziliş> <Taktik> [Görsel_URL]`\nÖrnek: `.kadro 4-3-3 'Hücum / Yüksek Pres' https://image-link.com/kadro.png`")
            return

        embed = discord.Embed(
            title=f"📋 {ctx.author.display_name} — Kadro & Taktik",
            color=0x000000
        )
        embed.add_field(name="📐 Diziliş", value=f"`{dizilis}`", inline=True)
        embed.add_field(name="🧠 Taktik", value=f"`{taktik}`", inline=True)
        
        if gorsel_url:
            embed.set_image(url=gorsel_url)
            
        embed.set_footer(text=f"Güncelleyen T.D.: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # --- REAL MADRID ÖZEL KOMUTU (.rmadrid) ---
    @commands.command(name="rmadrid")
    @commands.has_role("Real Madrid T.D.")
    async def rmadrid(self, ctx, dizilis: str, taktik: str, gorsel_url: str = None):
        embed = discord.Embed(title="👑 Real Madrid Kadro & Taktik", color=0x000000)
        embed.add_field(name="📐 Diziliş", value=f"`{dizilis}`", inline=True)
        embed.add_field(name="🧠 Taktik", value=f"`{taktik}`", inline=True)
        
        if gorsel_url:
            embed.set_image(url=gorsel_url)
            
        embed.set_footer(text=f"Güncelleyen T.D.: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @rmadrid.error
    async def rmadrid_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("❌ Bu komutu sadece **Real Madrid T.D.** rolüne sahip kişiler kullanabilir!")

async def setup(bot):
    await bot.add_cog(Kadro(bot))
