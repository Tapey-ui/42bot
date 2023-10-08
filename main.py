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

from datetime import datetime, timedelta
from datetime import date

from blackhole_request_modal import BlackholeRequestModal

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

API_URL = "https://api.intra.42.fr"
ACCESS_TOKEN_URL = "https://api.intra.42.fr/oauth/token"

headers = {'Content-type':'application/json'}
r = requests.post(ACCESS_TOKEN_URL + f"?grant_type=client_credentials&client_id={os.getenv('UID')}&client_secret={os.getenv('SECRET')}", headers=headers)
access_token = r.json()['access_token']

client = BackendApplicationClient(client_id=os.getenv('UID')) # to make sure no user authentication is needed. (otherwise it'll complain when you fetch_token)
life = OAuth2Session(client=client)
life.fetch_token(
    token_url=ACCESS_TOKEN_URL,
    client_secret=os.getenv('SECRET')
)
class Button(discord.ui.View):
    def __init__(self, bot, mes_admin, name, day: int):
        super().__init__()
        self.value = None
        self.bot = bot
        self.mes_admin = mes_admin
        self.name = name
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
        intra = self.name.split('|')[1]
        self.edit_days()
        stu = await bot.fetch_channel(os.getenv('STUDENT_CH'))
        suc = discord.Embed(title = "Request Success!", color = 0x77DD77)
        suc.add_field(name="", value=f"Hi {intra}, your request is successful!", inline=True)
        mes_admin = discord.Embed(title = "Request Appoved!", color = 0x77DD77)
        mes_admin.add_field(name="", value="Request Appoved, thanks!", inline=True)
        await stu.send(embed=suc)
        await interaction.response.edit_message(embed=mes_admin)
        self.value = False
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.interactions, button: discord.ui.Button):
        stu = await bot.fetch_channel(os.getenv('STUDENT_CH'))
        suc = discord.Embed(title = "Request Declined!", color = 0xFF6961)
        suc.add_field(name="", value=f"Hi {self.name.split('|')[1].strip()}, your request has been declined. Should you have any issues regarding blackhole days, please contact the BOCALs.", inline=True)
        mes_admin = discord.Embed(title = "Request Declined!", color = 0xFF6961)
        mes_admin.add_field(name="", value="Request Declined, thanks!", inline=True)
        await stu.send(embed=suc)
        await interaction.response.edit_message(embed=mes_admin)
        self.value = False
        self.stop()

# @tasks.loop(hours=24)
# async def import_user():
# 	i = 0
# 	name_amount = 100
# 	list = []
# 	if os.path.exists("test.json"):
# 		os.remove("test.json")
# 	while name_amount == 100:
# 		url = life.get(API_URL + f'/v2/campus/34/users?per_page=100&page={i}&access_token={access_token}')
# 		list += url.json()
# 		name_amount = len(url.json())
# 		i += 1
# 		print(name_amount)
# 	with open('test.json', "w") as w:
# 		w.write(json.dumps(list))

@tasks.loop(seconds=10)
async def test_task():
	print("checking users now!")
	guild = discord.utils.get(bot.guilds, name='42bot')

	async def remove_role_from_user(user, role_name):
		role = discord.utils.get(guild.roles, name=role_name)
		if not role or not discord.utils.get(user.roles, name=role_name):
			return
		await user.remove_roles(role)
		print(f'removed {user.display_name} from {role_name}')

	async def add_role_to_user(user, role_name):
		if discord.utils.get(user.roles, name=role_name):
			return
		role = discord.utils.get(guild.roles, name=role_name)
		await user.add_roles(role)
		print(f'added {user.display_name} to {role_name}')

	for user in guild.members:
		try:
			l = user.display_name.split("|")
			id = l[1].strip()
		except:
			await add_role_to_user(user, "INVALID USER")
			await remove_role_from_user(user, "Pisciner")
			await remove_role_from_user(user, "CADET")
			continue

		req = life.get(API_URL + f'/v2/users/{id}')
		try:
			info = req.json()['cursus_users']
		except:
			await add_role_to_user(user, "INVALID USER")
			await remove_role_from_user(user, "Pisciner")
			await remove_role_from_user(user, "CADET")
			continue

		if len(info) > 1:
			await add_role_to_user(user, "CADET")
			await remove_role_from_user(user, "Pisciner")
		elif len(info) == 1:
			await add_role_to_user(user, "Pisciner")
			await remove_role_from_user(user, "CADET")

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
    user = life.get(API_URL + f'/v2/users/{id.lower()}')
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
        dt = datetime.strptime(info["cursus_users"][1]["blackholed_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        await ctx.response.send_message(f"Found user {id} in {campus_name}, they have {(dt.date() - date.today()).days} blackhole days left.", ephemeral=False)
    else:
        await ctx.response.send_message(f"Found user {id} in {campus_name}", ephemeral=False)

@tree.command(name='hello', description="Say hello", guild=discord.Object(id=1159774219291344946))
async def hello(message):
	await message.response.send_message("hey " + message.user.mention)

@tree.command(name='blackhole', description="Requests for blackhole days", guild=discord.Object(id=1159774219291344946))
async def blackhole(message, days: int):
    info = []
    admin = await bot.fetch_channel(os.getenv('ADMIN_CH'))
    id = ""
    try:
        l = message.user.display_name.split("|")
        if len(l) != 2:
            raise Exception("Invalid username format. Please correct it according to format (NAME | INTRA_ID)")
        id = l[1].strip()
    except Exception as error:
        await message.response.send_message(error)
        return
    user = life.get(API_URL + f'/v2/users/{id.lower()}')
    info = {}
    if os.path.exists("test.json"):
        os.remove("test.json")
    try:
        info = user.json()
        with open('user.json', "w") as w:
            w.write(json.dumps(info))
    except:
        await message.response.send_message(f"Could not find user {id}. Please correct it according to format (NAME | INTRA_ID)")
        return
    if len(info["cursus_users"]) > 1:
        dt = datetime.strptime(info["cursus_users"][1]["blackholed_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
    bd = (dt.date() - date.today()).days
    if (bd > 50):
        await message.response.send_message(f"Hi {message.user.mention}, you still have {bd} days left, which is more than enough for a project. Should you want to extend you blackhole days, please contact the BOCALs or consider taking AGU. :D")
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
        button1 = Button(bot, mes_admin, message.user.display_name, days)
        await message.response.send_message(embed=mes)
        await admin.send(embed=mes_admin)
        await admin.send(view=button1)

@tree.command(name='blackhole_request', description="Sends a request to extend blackhole days", guild=discord.Object(id=1159774219291344946))
async def blackhole_request(interaction: discord.Interaction):
	modal = BlackholeRequestModal(bot, title="Blackhole request form")
	await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
	test_task.start()
	print('We have logged in as {0.user}'.format(bot))
	guild = discord.utils.get(bot.guilds, name='42bot')
	await tree.sync(guild=guild)

bot.run(os.getenv("DISCORD_TOKEN"))
