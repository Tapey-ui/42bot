import discord
import os

class BlackholeRequestButtons(discord.ui.View):
	def __init__(self, bot: discord.Client, mes_admin: discord.Embed, user: discord.User | discord.Member):
		super().__init__()
		self.value = None
		self.bot = bot
		self.mes_admin = mes_admin
		self.user = user

	@discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
	async def accept(self, interaction: discord.interactions, button: discord.ui.Button):
		success_embed = discord.Embed(title = "Request Success!", color = 0x77DD77)
		success_embed.add_field(name="", value=f"Hi {self.user.display_name.split('|')[1]}, your request for more blackhole days is successful!", inline=True)
		await self.user.send(embed=success_embed)

		mes_admin = discord.Embed(title = "Request Approved!", color = 0x77DD77)
		mes_admin.add_field(name="", value="Request Approved, thanks!", inline=True)
		await interaction.response.edit_message(embed=mes_admin)
		self.value = False
		self.stop()

	@discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
	async def decline(self, interaction: discord.interactions, button: discord.ui.Button):
		decline_embed = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		decline_embed.add_field(name="", value=f"Hi {self.user.display_name.split('|')[1].strip()}, your request for more blackhole days has been declined. Should you have any issues regarding blackhole days, please contact the BOCALs.", inline=True)
		await self.user.send(embed=decline_embed)

		mes_admin = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		mes_admin.add_field(name="", value="Request Declined, thanks!", inline=True)
		await interaction.response.edit_message(embed=mes_admin)
		self.value = False
		self.stop()
