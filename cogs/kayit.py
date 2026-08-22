import discord
from discord.ext import commands

class KayitSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Teknik Direktör", description="T.D. rolü alır."),
            discord.SelectOption(label="Kulüp Başkanı", description="Başkan rolü alır."),
            discord.SelectOption(label="Futbolcu", description="Futbolcu rolü alır."),
            discord.SelectOption(label="Üye", description="Standart üye rolü alır.")
        ]
        super().__init__(placeholder="Sistemdeki rolünüzü seçin...", options=options)

    async def callback(self, interaction: discord.Interaction):
        rol_adi = self.values[0]
        role = discord.utils.get(interaction.guild.roles, name=rol_adi)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"**{rol_adi}** rolü başarıyla verildi!", ephemeral=True)
        else:
            await interaction.response.send_message(f"'{rol_adi}' isimli rol sunucuda bulunamadı. Lütfen yöneticiye bildirin.", ephemeral=True)

class KayitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(KayitSelect())

class Kayit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kayitsistemi(self, ctx):
        await ctx.send("Lütfen ligdeki rolünüzü seçiniz:", view=KayitView())

async def setup(bot):
    await bot.add_cog(Kayit(bot))
