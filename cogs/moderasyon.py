import discord
from discord.ext import commands

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(" Kanal kilitlendi.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(" Kanalın kilidi açıldı.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, sebep=None):
        await member.kick(reason=sebep)
        await ctx.send(f"**{member.display_name}** sunucudan atıldı. Sebep: {sebep}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, sebep=None):
        await member.ban(reason=sebep)
        await ctx.send(f"**{member.display_name}** yasaklandı. Sebep: {sebep}")

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))
