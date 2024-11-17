import re, os, asyncio, requests, discord
# import yt_dlp as youtube_dl
from itertools import cycle
from dotenv import load_dotenv
from discord.ext import commands, tasks
import logging

logger = logging.getLogger(__name__)

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

		# self.YTDL_OPTIONS = {
		# 	# 'audioformat': 'mp3',
		# 	'outtmpl': '%(extractor)s-%(id)-s%(title)s.%(ext)s',
		# 	'restrictfilenames': True,
		# 	'noplaylist': True,
		# 	'nocheckcertificate': True,
		# 	'ignoreerrors': False,
		# 	'logtostderr': False,
		# 	'quiet': True,
		# 	'no_warnings': True,
		# 	'default_search': 'auto',
		# 	'soruce_address': '0.0.0.0'
		# }

		# self.ytdl = youtube_dl.YoutubeDL(self.YTDL_OPTIONS)

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
		await ctx.send(user.avatar)
	
	@commands.command()
	async def upparsegaya(self, ctx, *, query):
		discordID = re.match(r'^<@(\d*)>$', query.strip()).groups()[0]
		user = await ctx.guild.fetch_member(discordID)
		await ctx.send(f'https://api.popcat.xyz/jokeoverhead?image={str(user.avatar).replace("?size=1024", "")}')

	# @commands.Cog.listener('on_message')
	# async def insta_replacer(self, message):
	# 	# TODO: Refer https://instaloader.github.io/
	# 	# Images
	# 	# https://www.instagram.com/p/CnzAwydLi-1/
	# 	# https://www.instagram.com/p/Cn9bbbYNC7t/
	# 	# Reels
	# 	# https://www.instagram.com/reel/Cnaea8SK7Kn/
	# 	# https://www.instagram.com/reel/CpYYBCShGem/
	# 	if re.match(r'https://[www\.]*instagram.com/(.+?)/(.+?)/*.*', message.content.strip()):
	# 		print(f'Insta Link on_message triggered! {message.content}')
	# 		print(self.ytdl.download(message.content.strip()))

	@commands.Cog.listener('on_message')
	async def link_sanitizer(self, message):
		# print(message.author)
		# Instagram
		lnk_match = re.search(r'https://[w{3}\.]*instagram.com/(.+?)/(.+?)([/\? \n]|$)( .*)*', message.content.strip())
		if lnk_match and message.author != self.bot.user:
			# print(f'Insta Link on_message triggered! {message.content}')
			await message.channel.send(
				f'``{message.author}`` sent: https://www.instagram.com/{lnk_match.groups()[0]}/{lnk_match.groups()[1]}/{" with message: " + lnk_match.groups()[3] if lnk_match.groups()[3] else ""}'
			)
			await message.delete(delay=1)
			return
		# Twitter
		lnk_match = re.search(r'https://(x|twitter).com/(.+?)/(.+?)/(.+?)([/\? \n]|$)( .*)*', message.content.strip())
		if lnk_match and message.author != self.bot.user:
			# print(f'Twitter Link on_message triggered! {message.content}')
			await message.channel.send(
				f'``{message.author}`` sent: https://vxtwitter.com/{lnk_match.groups()[1]}/{lnk_match.groups()[2]}/{lnk_match.groups()[3]}{" with message: " + lnk_match.groups()[5] if lnk_match.groups()[5] else ""}'
			)
			await message.delete(delay=1)
			return
		# Google Search
		lnk_match = re.search(r'https://www.google.com/search\?q=(.+?)([/\? \n]|$)( .*)*', message.content.strip())
		if lnk_match and message.author != self.bot.user:
			# print(f'Google Link on_message triggered! {message.content}')
			await message.channel.send(
				f'``{message.author}`` sent: https://google.com/search?q={lnk_match.groups()[0]}{" with message: " + lnk_match.groups()[2] if lnk_match.groups()[2] else ""}'
			)
			await message.delete(delay=1)
			return
		# Amazon
		lnk_match = re.search(r'(.*)\s(https://www.amazon\.[a-z]+/[\w\-]+/dp/[0-9A-Z]{10})\S*\s(.*)', message.content.strip())
		if lnk_match and message.author != self.bot.user:
			await message.channel.send(
				f'``{message.author}`` {lnk_match.groups()[0] if lnk_match.groups()[0] else ""} {lnk_match.groups()[1]} {lnk_match.groups()[2] if lnk_match.groups()[2] else ""}'
			)
			await message.delete(delay=1)
			return
		

	@tasks.loop(minutes=10)
	async def activity_loop(self):
		await self.bot.change_presence(activity=discord.Game(name=next(self.activities)))
	
	# we need to wait for the bot to be ready
	# as failing to do so will raise an attribute error:
	# AttributeError: 'NoneType' object has no attribute 'change_presence'
	@activity_loop.before_loop
	async def before_activity_loop(self):
		await self.bot.wait_until_ready()
