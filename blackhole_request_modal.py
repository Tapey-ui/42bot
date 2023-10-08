import discord
import os
import json
from datetime import datetime, date, timedelta

from blackhole_request_buttons import BlackholeRequestButtons

class BlackholeRequestModal(discord.ui.Modal):
	def __init__(self, client: discord.Client, session,  *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.client = client
		self.session = session
		self.add_item(discord.ui.TextInput(label="How many blackhole days", placeholder='14'))
		self.add_item(discord.ui.TextInput(label="Reason for the request", placeholder='Lazy'))

	async def on_submit(self, interaction: discord.Interaction):
		info = []
		guild = discord.utils.get(self.client.guilds, name=os.getenv('SERVER_NAME'))
		admin = discord.utils.get(guild.text_channels, name=os.getenv('ADMIN_CH'))
		id = ""
		try:
			l = interaction.user.display_name.split("|")
			if len(l) != 2:
				raise Exception("Invalid username format. Please correct it according to format (NAME | INTRA_ID)")
			id = l[1].strip()
		except Exception as error:
			await interaction.response.send_message(error)
			return
		user = self.session.get(os.getenv('API_URL') + f'/v2/users/{id.lower()}')
		info = {}
		try:
			info = user.json()
			with open('user.json', "w") as w:
				w.write(json.dumps(info))
		except:
			await interaction.response.send_message(f"Could not find user {id}. Please correct it according to format (NAME | INTRA_ID)")
			return
		if len(info["cursus_users"]) > 1:
			dt = datetime.strptime(info["cursus_users"][1]["blackholed_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
		bd = (dt.date() - date.today()).days
		if (bd > 50):
			await interaction.response.send_message(f"Hi {interaction.user.mention}, you still have {bd} days left, which is more than enough for a project. Should you want to extend you blackhole days, please contact the BOCALs or consider taking AGU. :D")
		if (int(self.children[0].value) < 0):
			await interaction.response.send_message("Hi " + interaction.user.mention + ", please enter a valid blackhole day amount to request extension! (Must be 14 days or lower)")
		elif (int(self.children[0].value) > 14):
			await interaction.response.send_message("Hi " + interaction.user.mention + ", you requested for too many blackhole days! Please request a lower amount. (Must be 14 days or lower)")
		else:

			role = discord.utils.get(interaction.guild.roles, name='Admin')

			user_embed: discord.Embed = discord.Embed(title="Request Sent", color=0xC1E1C1)
			user_embed.add_field(name="", value=f"Hi {interaction.user.mention}, thanks for the feedback! We will answer your request shortly! :D", inline=True)

			admin_embed: discord.Embed = discord.Embed(title="Blackhole days request")
			admin_embed.add_field(name="User", value=interaction.user.display_name.split('|')[1])
			admin_embed.add_field(name="How many blackhole days", value=self.children[0].value, inline=False)
			admin_embed.add_field(name="Reason for the request", value=self.children[1].value, inline=False)

			guild = discord.utils.get(self.client.guilds, name=os.getenv('SERVER_NAME'))
			admin_channel =	discord.utils.get(guild.text_channels, name=os.getenv('ADMIN_CH'))
			await interaction.response.send_message(embed=user_embed, ephemeral=True)
			await admin_channel.send(role.mention)
			await admin_channel.send(embed=admin_embed)
			await admin_channel.send(view=BlackholeRequestButtons(self.client, admin_embed, interaction.user, int(self.children[0].value)))
