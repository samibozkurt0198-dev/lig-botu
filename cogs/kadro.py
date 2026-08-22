import discord
from discord.ext import commands

class Kadro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Real Madrid T.D.")
    async def rmadrid(self, ctx, dizilis: str, taktik: str, gorsel_url: str):
        embed = discord.Embed(title=" Real Madrid Kadro & Taktik", color=discord.Color.gold())
        embed.add_field(name="Diziliş", value=dizilis, inline=True)
        embed.add_field(name="Taktik", value=taktik, inline=True)
        embed.set_image(url=gorsel_url)
        embed.set_footer(text=f"Güncelleyen T.D.: {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @rmadrid.error
    async def rmadrid_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(" Bu komutu sadece **Real Madrid T.D.** rolüne sahip kişiler kullanabilir!")

async def setup(bot):
    await bot.add_cog(Kadro(bot))

