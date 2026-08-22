import discord
from discord.ext import commands

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Destek Talebi Aç", style=discord.ButtonStyle.green, custom_id="ticket_button")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Kullanıcıya özel kanal oluşturma
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        await channel.send(f"Merhaba {user.mention}, destek talebiniz oluşturuldu. Yetkililer en kısa sürede ilgilenecektir.\nKapatmak için `!close` yazabilirsiniz.")
        await interaction.response.send_message(f"Destek kanalınız oluşturuldu: {channel.mention}", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketsistemi(self, ctx):
        embed = discord.Embed(title="🎫 Destek Sistemi", description="Yetkililerle iletişime geçmek için aşağıdaki butona tıklayın.", color=discord.Color.blue())
        await ctx.send(embed=embed, view=TicketButton())

    @commands.command()
    async def close(self, ctx):
        if "ticket-" in ctx.channel.name:
            await ctx.send("Kanal 5 saniye içinde siliniyor...")
            await asyncio.sleep(5)
            await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))
