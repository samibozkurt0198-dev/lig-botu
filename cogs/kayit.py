import discord
from discord.ext import commands

class KayitSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Teknik Direktör", description="T.D. rolü alır.", emoji="👔"),
            discord.SelectOption(label="Kulüp Başkanı", description="Başkan rolü alır.", emoji="💼"),
            discord.SelectOption(label="Futbolcu", description="Futbolcu rolü alır.", emoji="⚽"),
            discord.SelectOption(label="Üye", description="Standart üye rolü alır.", emoji="👤")
        ]
        super().__init__(placeholder="Sistemdeki rolünüzü seçin...", options=options, custom_id="kayit_select_menu")

    async def callback(self, interaction: discord.Interaction):
        rol_adi = self.values[0]
        role = discord.utils.get(interaction.guild.roles, name=rol_adi)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ **{rol_adi}** rolü başarıyla üzerinize tanımlandı!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Sunucuda `{rol_adi}` isimli bir rol bulunamadı. Lütfen yöneticiye bildirin.", ephemeral=True)

class KayitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(KayitSelect())

class Kayit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kayitsistemi", aliases=["kayitmesaj"])
    @commands.has_permissions(administrator=True)
    async def kayitsistemi(self, ctx):
        embed = discord.Embed(
            title="🏆 LİG KAYIT VE ROL SEÇİMİ",
            description="Aşağıdaki menüyü kullanarak sunucudaki lig rolünüzü anında alabilirsiniz.",
            color=0x000000
        )
        await ctx.send(embed=embed, view=KayitView())

async def setup(bot):
    await bot.add_cog(Kayit(bot))
