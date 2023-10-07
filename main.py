import discord

import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = 'MTE1OTc3OTg3Njc0ODkzMTE0NA.GhIFM6.CDYq9gpmcwRE4ax5Ah8Dy0RnqCjuNBa51Nh10M'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

class Button(discord.ui.View):
	def __init__(self, bot, mes_admin, name):
		super().__init__()
		self.value = None
		self.bot = bot
		self.mes_admin = mes_admin
		self.name = name
	
	@discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
	async def accept(self, interaction: discord.interactions, button: discord.ui.Button):
		stu = await bot.fetch_channel('1159776099455221820')
		suc = discord.Embed(title = "Request Success!", color = 0x77DD77)
		suc.add_field(name="", value=f"Hi {self.name}, your request is successful!", inline=True)
		mes_admin = discord.Embed(title = "Request Appoved!", color = 0x77DD77)
		mes_admin.add_field(name="", value="Request Appoved, thanks!", inline=True)
		await stu.send(embed=suc)
		await interaction.response.edit_message(embed=mes_admin)
		self.value = False
		self.stop()

	@discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
	async def decline(self, interaction: discord.interactions, button: discord.ui.Button):
		stu = await bot.fetch_channel('1159776099455221820')
		suc = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		suc.add_field(name="", value=f"Hi {self.name}, your request has been declined. Should you have any issues regarding blackhole days, please contact the BOCALs.", inline=True)
		mes_admin = discord.Embed(title = "Request Declined!", color = 0xFF6961)
		mes_admin.add_field(name="", value="Request Declined, thanks!", inline=True)
		await stu.send(embed=suc)
		await interaction.response.edit_message(view=None)
		await interaction.response.edit_message(embed=mes_admin)
		self.value = False
		self.stop()

@bot.command()
async def hello(message):
	await message.send("hey " + message.author.mention)

@bot.command()
async def blackhole(message, days):
	admin = await bot.fetch_channel('1160103537817165845')
	if (days.isdigit() == False or int(days) < 0):
		await message.send("Hi " + message.author.mention + ", please enter a valid blackhole day amount to request extension! (Must be 14 days or lower)")
	elif (int(days) > 14):
		await message.send("Hi " + message.author.mention + ", you requested for too many blackhole days! Please request a lower amount. (Must be 14 days or lower)")
	else:
		role = discord.utils.get(message.guild.roles, name = "Admin")
		mes = discord.Embed(title = "Request Sent!", color = 0xC1E1C1)
		mes_admin = discord.Embed(title = f"Request Received from {message.author.display_name}!", color = 0xC1E1C1)
		mes.add_field(name="", value=f"Hi {message.author.mention}, thanks for the feedback! We will answer your request shortly! :D", inline=True)
		mes_admin.add_field(name="", value=f"Hi {role.mention}, {message.author.display_name} has requested for {days} blackhole days.")
		if (role == False):
			await admin.send("test")
		button1 = Button(bot, mes_admin, message.author.display_name)
		await message.send(embed=mes)
		await admin.send(embed=mes_admin)
		await admin.send(view=button1)

bot.run(DISCORD_TOKEN)