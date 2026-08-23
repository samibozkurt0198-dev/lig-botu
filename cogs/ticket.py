import discord
from discord.ext import commands
import asyncio

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Destek Talebi Aç", style=discord.ButtonStyle.green, custom_id="ticket_button_create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Zaten açık talebi var mı kontrolü
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"⚠️ Zaten açık bir destek talebiniz bulunuyor: {existing_channel.mention}", ephemeral=True)
            return

        # Kullanıcıya ve yetkililere özel kanal izinleri
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Destek Rolü varsa izin ekle
        destek_rol = discord.utils.get(guild.roles, name="Destek Ekibi") or discord.utils.get(guild.roles, name="Değer Yetkilisi")
        if destek_rol:
            overwrites[destek_rol] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(name=f"ticket-{user.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title="🎫 DESTEK TALEBİ OLUŞTURULDU",
            description=f"Merhaba {user.mention}, talebiniz başarıyla alındı. Yetkililer en kısa sürede sizinle ilgilenecektir.\n\n🔒 **Talebi kapatmak için:** `.close` komutunu kullanabilirsiniz.",
            color=0x000000
        )
        await channel.send(content=f"{user.mention}", embed=embed)
        await interaction.response.send_message(f"✅ Destek kanalınız oluşturuldu: {channel.mention}", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- TICKET SİSTEMİ MESAJI (.ticketsistemi) ---
    @commands.command(name="ticketsistemi", aliases=["ticketkur"])
    @commands.has_permissions(administrator=True)
    async def ticketsistemi(self, ctx):
        embed = discord.Embed(
            title="🎫 DESTEK MERKEZİ",
            description="Ligle, transferlerle veya hesabınızla ilgili bir sorun mu var?\nAşağıdaki butona basarak yetkili ekibimizle özel görüşme başlatabilirsiniz.",
            color=0x000000
        )
        await ctx.send(embed=embed, view=TicketButton())

    # --- TICKET KAPATMA (.close) ---
    @commands.command(name="close", aliases=["kapat"])
    async def close(self, ctx):
        if "ticket-" in ctx.channel.name.lower():
            embed = discord.Embed(
                description="🔒 **Destek talebi kapatılıyor...** Kanal 5 saniye içinde silinecektir.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await ctx.channel.delete()
        else:
            await ctx.send("❌ Bu komutu sadece destek talebi (`ticket-`) kanallarında kullanabilirsiniz!")

async def setup(bot):
    await bot.add_cog(Ticket(bot))
