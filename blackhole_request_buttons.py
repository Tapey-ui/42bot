import discord
import os
import json
from datetime import datetime, timedelta, date

class BlackholeRequestButtons(discord.ui.View):
	def __init__(self, bot: discord.Client, mes_admin: discord.Embed, user, day: int):
		super().__init__()
		self.value = None
		self.bot = bot
		self.mes_admin = mes_admin
		self.user = user
		self.day = day

	def edit_days(self):
		filename = 'user.json'
		with open(filename, 'r+') as f:
			data = json.load(f)
			if len(data["cursus_users"]) > 1:
				dt = datetime.strptime(data["cursus_users"][1]["blackholed_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
			data["cursus_users"][1]["blackholed_at"] = dt + timedelta(days=self.day)
			new_data = json.dumps(data, default=str)
			f.seek(0)
			f.truncate()
			f.write(new_data)

	@discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
	async def accept(self, interaction: discord.interactions, button: discord.ui.Button):
		intra = self.user.display_name.split('|')[1]
		self.edit_days()
		success_embed = discord.Embed(title = "Request Success!", color = 0x77DD77)
		success_embed.add_field(name="", value=f"Hi {intra}, your request for more blackhole days is successful!")
		await self.user.send(embed=success_embed)

		mes_admin = discord.Embed(title = "Request Approved!", color = 0x77DD77)
		mes_admin.add_field(name="", value="Request Approved, thanks!")
		await interaction.response.edit_message(embed=mes_admin, view=None)
		self.value = False
		self.stop()

	@discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
	async def decline(self, interaction: discord.interactions, button: discord.ui.Button):
		decline_embed = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		decline_embed.add_field(name="", value=f"Hi {self.user.display_name.split('|')[1].strip()}, your request for more blackhole days has been declined. Should you have any issues regarding blackhole days, please contact the BOCALs.", inline=True)
		await self.user.send(embed=decline_embed)

		mes_admin = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		mes_admin.add_field(name="", value="Request Declined, thanks!", inline=True)
		await interaction.response.edit_message(embed=mes_admin, view=None)
		self.value = False
		self.stop()
