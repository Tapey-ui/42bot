import discord
import os

from blackhole_request_buttons import BlackholeRequestButtons

class BlackholeRequestModal(discord.ui.Modal):
	def __init__(self, client: discord.Client, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.client = client
		self.add_item(discord.ui.TextInput(label="How many blackhole days", placeholder='14'))
		self.add_item(discord.ui.TextInput(label="Reason for the request", placeholder='Lazy'))

	async def on_submit(self, interaction: discord.Interaction):
		try:
			int(self.children[0].value)
		except:
			interaction.response.send_message("Please enter numeric string for number of blackhole days", ephemeral=True)
			return

		if int(self.children[0].value) > 14 and int(self.children[0].value) < 1:
			interaction.response.send_message("Please enter a value between 1 - 14", ephemeral=True)

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
