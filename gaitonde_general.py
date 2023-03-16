import re, os, asyncio, requests, discord
from itertools import cycle
from dotenv import load_dotenv
from discord.ext import commands, tasks
# import logging

# logger = logging.getLogger(__name__)

load_dotenv()
MAYMAYS_BASE_URL = os.getenv('MAYMAYS_BASE_URL')
MAYMAYS_DIR_PATH = os.getenv('MAYMAYS_DIR_PATH')
CRAZY_USR_ID = os.getenv('CRAZY_USR_ID')
OSLE_USR_ID = os.getenv('OSLE_USR_ID')
CRAZY_NAME = os.getenv('CRAZY_NAME')

class General(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.activities = cycle([
			'Crazy\'s Sex Tape Vol. 3',
			'Background Noise',
			'Prince\'s Guitar',
			'Fast & Loose',
			'with the Queen of Hearts',
			'God'
		])
		self.activity_loop.start()

	@commands.command()
	async def why(self, ctx):
		await ctx.send('誰も知らないよ。')

	@commands.command()
	async def ping(self, ctx):
		await ctx.send(f'``HB to HB_ACK Latency:`` {int(self.bot.latency * 1000)} ms')

	@commands.command()
	async def rage(self, ctx):
		await ctx.send(f'<@{CRAZY_USR_ID}>\n```\nChutiya\n{CRAZY_NAME}\nLand manas\nKaat daalega\n```')

	@commands.command()
	async def tava(self, ctx):
		await ctx.send(f'<@{OSLE_USR_ID}> gand mara')

	@commands.command()
	async def rgb(self, ctx):
		await ctx.send(embed=discord.Embed(title='POV: Your RGB PC looking at you').set_image(url=f'{MAYMAYS_BASE_URL}/rgbOsle.gif'))

	@commands.command()
	async def osle(self, ctx):
		await ctx.send(content=f'<@{OSLE_USR_ID}>', file=discord.File(f'{MAYMAYS_DIR_PATH}/findingOsle.jpg'))

	@commands.command()
	async def nft(self, ctx):
		await ctx.send(content=f'<@{CRAZY_USR_ID}>', file=discord.File(f'{MAYMAYS_DIR_PATH}/nft.jpg'))

	@commands.command()
	async def thecoolernft(self, ctx):
		await ctx.send(content=f'<@{CRAZY_USR_ID}>', file=discord.File(f'{MAYMAYS_DIR_PATH}/theCoolerNFT.jpg'))

	@commands.command()
	async def kanye(self, ctx):
		await ctx.send(requests.get('https://api.kanye.rest/').json()['quote'])
	
	@commands.command()
	async def avatar(self, ctx, *, query):
		# await ctx.send(ctx.author.display_avatar)
		discordID = re.match(r'^<@(\d*)>$', query.strip()).groups()[0]
		user = await ctx.guild.fetch_member(discordID)
		await ctx.send(f'https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024')
	
	@commands.command()
	async def upparsegaya(self, ctx, *, query):
		discordID = re.match(r'^<@(\d*)>$', query.strip()).groups()[0]
		user = await ctx.guild.fetch_member(discordID)
		await ctx.send(f'https://api.popcat.xyz/jokeoverhead?image=https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png')

	# @commands.command()
	# async def addBday(self, ctx):
	# 	def checkName(msg): return len(msg) < and msg.channel == ctx.channel
	# 	name = dob = '*Some Error. Rerun command after timeout.*'
	# 	try:
	# 		questionMessage = await ctx.send("Name?")
	# 		name = await self.bot.wait_for('message', check=checkName, timeout=15)
	# 		await questionMessage.edit(content=f'Name: {name}\nDOB? (YYYY-MM-DD)')
	# 		dob = await self.bot.wait_for('message', check=checkName, timeout=15)

	@tasks.loop(minutes=10)
	async def activity_loop(self):
		await self.bot.change_presence(activity=discord.Game(name=next(self.activities)))
	
	# we need to wait for the bot to be ready
	# as failing to do so will raise an attribute error:
	# AttributeError: 'NoneType' object has no attribute 'change_presence'
	@activity_loop.before_loop
	async def before_activity_loop(self):
		await self.bot.wait_until_ready()