import discord
import requests
import os
import json

from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from datetime import datetime
from datetime import date

from blackhole_request_modal import BlackholeRequestModal
from blackhole_request_buttons import BlackholeRequestButtons

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

API_URL = "https://api.intra.42.fr"
ACCESS_TOKEN_URL = "https://api.intra.42.fr/oauth/token"

client = BackendApplicationClient(client_id=os.getenv('UID')) # to make sure no user authentication is needed. (otherwise it'll complain when you fetch_token)
life = OAuth2Session(client=client)
life.fetch_token(
    token_url=ACCESS_TOKEN_URL,
    client_secret=os.getenv('SECRET')
)



@tree.command(name='getid', description="Gets your id", guild=discord.Object(id=1159774219291344946))
async def get_intra_id(ctx):
    id = ""
    try:
        l = ctx.user.display_name.split("|")
        if len(l) != 2:
            raise Exception("Invalid username format. Please correct it according to format (NAME | INTRA_ID)")
        id = l[1].strip()
    except Exception as error:
        await ctx.response.send_message(error)
        return

    user = life.get(API_URL + f'/v2/users/{id}')
    info = {}
    try:
        info = user.json()
        info["campus"]
    except:
        await ctx.response.send_message(f"Could not find user {id}. Please correct it according to format (NAME | INTRA_ID)")
        return

    in_campus = False
    campus_name = os.getenv('CAMPUS_NAME')
    for campus in info["campus"]:
        if campus["name"] == campus_name:
            in_campus = True
            break

    if not in_campus:
        await ctx.response.send_message(f"Could not find user {id} in {campus_name}.")
        return

    if len(info["cursus_users"]) > 1:
        dt = datetime.strptime(info["cursus_users"][1]["blackholed_at"], "%Y-%m-%dT00:00:00.000Z")
        await ctx.response.send_message(f"Found user {id} in {campus_name}, they have {(dt.date() - date.today()).days} blackhole days left.", ephemeral=False)
    else:
        await ctx.response.send_message(f"Found user {id} in {campus_name}", ephemeral=False)

@tree.command(name='hello', description="Say hello", guild=discord.Object(id=1159774219291344946))
async def hello(message):
	await message.response.send_message("hey " + message.user.mention)

@tree.command(name='blackhole', description="Requests for blackhole days", guild=discord.Object(id=1159774219291344946))
async def blackhole(message, days: int):
	guild = discord.utils.get(bot.guilds, name=os.getenv('SERVER_NAME'))
	admin = discord.utils.get(guild.text_channels, name=os.getenv('ADMIN_CH'))
	# admin = await bot.fetch_channel(os.getenv('ADMIN_CH'))
	if (int(days) < 0):
		await message.response.send_message("Hi " + message.user.mention + ", please enter a valid blackhole day amount to request extension! (Must be 14 days or lower)")
	elif (int(days) > 14):
		await message.response.send_message("Hi " + message.user.mention + ", you requested for too many blackhole days! Please request a lower amount. (Must be 14 days or lower)")
	else:
		role = discord.utils.get(message.guild.roles, name = "Admin")
		mes = discord.Embed(title = "Request Sent!", color = 0xC1E1C1)
		mes_admin = discord.Embed(title = f"Request Received from {message.user.display_name.split('|')[1].strip()}!", color = 0xC1E1C1)
		mes.add_field(name="", value=f"Hi {message.user.mention}, thanks for the feedback! We will answer your request shortly! :D", inline=True)
		mes_admin.add_field(name="", value=f"Hi {role.mention}, {message.user.display_name.split('|')[1].strip()} has requested for {days} blackhole days.")
		if (role == False):
			await admin.send("test")
		button1 = BlackholeRequestButtons(bot, mes_admin, message.user)
		await message.response.send_message(embed=mes, ephemeral=True)
		await admin.send(embed=mes_admin)
		await admin.send(view=button1)

@tree.command(name='blackhole_request', description="Sends a request to extend blackhole days", guild=discord.Object(id=1159774219291344946))
async def blackhole_request(interaction: discord.Interaction):
	modal = BlackholeRequestModal(bot, title="Blackhole request form")
	await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	guild = discord.utils.get(bot.guilds, name='42bot')
	await tree.sync(guild=guild)

bot.run(os.getenv("DISCORD_TOKEN"))
