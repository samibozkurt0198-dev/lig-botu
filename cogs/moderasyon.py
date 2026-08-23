import discord
from discord.ext import commands

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- KANAL KİLİTLE (.lock) ---
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            description="🔒 **Kanal başarıyla kilitlendi!** Üyeler artık mesaj gönderemez.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)

    # --- KANAL KİLİDİNİ AÇ (.unlock) ---
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            description="🔓 **Kanal kilidi açıldı!** Üyeler tekrar mesaj gönderebilir.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    # --- MESAJ SİLME (.sil / .clear) ---
    @commands.command(name="sil", aliases=["clear", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def sil(self, ctx, miktar: int = 10):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        deleted = await ctx.channel.purge(limit=miktar)
        embed = discord.Embed(
            description=f"🧹 **{len(deleted)}** adet mesaj başarıyla silindi.",
            color=0x000000
        )
        await ctx.send(embed=embed, delete_after=5)

    # --- ATMA (.kick) ---
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, sebep: str = "Sebep belirtilmedi"):
        if not member:
            await ctx.send("⚠️ Kullanım: `.kick @kullanıcı [sebep]`")
            return

        try:
            await member.kick(reason=sebep)
            embed = discord.Embed(
                title="👢 Kullanıcı Sunucudan Atıldı",
                description=f"**Atılan Kullanıcı:** {member.mention} (`{member.id}`)\n**Yetkili:** {ctx.author.mention}\n**Sebep:** {sebep}",
                color=0xFFA500
            )
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("❌ Kullanıcı atılamadı. Botun yetkilerini veya rol sırasını kontrol edin.")

    # --- YASAKLAMA (.ban) ---
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, sebep: str = "Sebep belirtilmedi"):
        if not member:
            await ctx.send("⚠️ Kullanım: `.ban @kullanıcı [sebep]`")
            return

        try:
            await member.ban(reason=sebep)
            embed = discord.Embed(
                title="🔨 Kullanıcı Yasaklandı",
                description=f"**Yasaklanan Kullanıcı:** {member.mention} (`{member.id}`)\n**Yetkili:** {ctx.author.mention}\n**Sebep:** {sebep}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("❌ Kullanıcı yasaklanamadı. Botun yetkilerini veya rol sırasını kontrol edin.")

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))
