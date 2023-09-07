import discord, requests, html
import os, asyncio, datetime, time, logging
# import pprint
import yt_dlp as youtube_dl
from random import choice
from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger(__name__)

load_dotenv()
NPYTT = os.getenv('NP112_YT_TOKEN')
NETHR = os.getenv('NETHR_YT_TOKEN')
MAYMAYS_BASE_URL = os.getenv('MAYMAYS_BASE_URL')
MAYMAYS_DIR_PATH = os.getenv('MAYMAYS_DIR_PATH')

ffmpeg_options = {
	'options': '-vn -loglevel quiet'
}

#class YTDLError(Exception):
#	pass

youtube_dl.utils.bug_reports_message = lambda: ''

class YTDLSource(discord.PCMVolumeTransformer):
	YTDL_OPTIONS = {
		'format': 'bestaudio/best',
		'extractaudio': True,
		# 'audioformat': 'mp3',
		'outtmpl': '%(extractor)s-%(id)-s%(title)s.%(ext)s',
		'restrictfilenames': True,
		'noplaylist': True,
		'nocheckcertificate': True,
		'ignoreerrors': False,
		'logtostderr': False,
		'quiet': True,
		'no_warnings': True,
		'default_search': 'auto',
		'soruce_address': '0.0.0.0'
	}

	FFMPEG_OPTIONS = {
		'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
		'options': '-vn -loglevel quiet'
	}

	ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

	def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
		super().__init__(source, volume)

		self.requester = ctx.author
		self.channel = ctx.channel
		# self.data = data

		self.uploader = data.get('uploader')
		self.title = data.get('title')
		# Refer to this for data.* attributes: https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template
		# print(f'Title: {data.get("title")}\nAlt Title: {data.get("alt_title ")}')
		self.thumbnail = data.get('thumbnail')
		# print(f'Title: {data.get("title")}\nDuration: {data.get("duration")}')
		self.durationSec = int(data.get('duration'))
		self.duration = self.parseDuration(self.durationSec)
		self.startTime = None
		self.url = data.get('webpage_url')
		# self.media_url = data.get('url')

	def parseDuration(self, s):
		m, s = divmod(s, 60)
		if m > 60:
			h, m = divmod(m, 60)
			return f'{h:d}:{m:02d}:{s:02d}'
		else:
			return f'{m:d}:{s:02d}'

	@classmethod
	async def fromURL(cls, ctx: commands.Context, url: str, *, loop: asyncio.BaseEventLoop = None):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download = False))
		if 'entries' in data:
			data = data['entries'][0]
		return cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data = data)

class GuildQueue():
	def __init__(self, ctx):
		self._ctx = ctx
		self.ytQueue = []
		self.npPlayer = None
	
	def playLoop(self, ctx, player):
		def afterSongEnd(e):
			logger.error(e) if e else None
			try: 
				if len(self.ytQueue) > 0:
					player = self.ytQueue.pop(0)
					self.playLoop(ctx, player)
				else:
					self.npPlayer = None
			except Exception as ex:
				logger.error(ex)
		player.startTime = datetime.datetime.now()
		self.npPlayer = player
		ctx.voice_client.play(player, after=afterSongEnd)

class YTStream(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.guildQueues = {}
		self.queueLimit = 7

	@classmethod
	def getVID(self, query):
		url = 'https://youtube.googleapis.com/youtube/v3/search'
		# Reference: https://developers.google.com/youtube/v3/docs/search/list
		params = {
			'part': 'snippet',
			'type': 'video',
			# 'videoCategoryId': '10',
			'maxResults': 1,
			'key': choice([NETHR, NPYTT]),
			'q': query
			# 'order': 'viewCount' # Note: 'relevance' by default in the youtube data api
		}
		response = requests.get(url=url, params=params).json()
		# pprint.pprint(response)
		return response['items'][0]['id']['videoId']

	@classmethod
	def estimatedTimeToPlay(self, player, guildQueue):
		# TODO: fix incorrect Wait Time bug
		ct = datetime.datetime.now()
		secs = guildQueue.npPlayer.durationSec - ((ct.minute * 60 + ct.second) - (guildQueue.npPlayer.startTime.minute * 60 + guildQueue.npPlayer.startTime.second))
		for i in range(guildQueue.ytQueue.index(player)):
			secs += guildQueue.ytQueue[i].durationSec
		return f'{int(secs/60)}:{secs%60:02d}' if secs < 3600 else datetime.timedelta(seconds=secs)

	@classmethod
	def addedToQueueEmbed(self, player, guildQueue):
		embed = discord.Embed(title=player.title, colour=discord.Colour(0xff0000), url=player.url)
		embed.set_author(name='Added to Queue♪ @ YouTube', icon_url=f'{MAYMAYS_BASE_URL}/gb.png')
		embed.add_field(name='Uploader', value=player.uploader)
		if player.durationSec > 0:
			embed.add_field(name='Duration', value=player.duration)
		embed.add_field(name='Wait Time', value=self.estimatedTimeToPlay(player, guildQueue))
		embed.set_footer(text=f'Queue Position: #{len(guildQueue.ytQueue)} | Requested by: {player.requester}')
		embed.set_thumbnail(url=player.thumbnail)
		return embed

	@classmethod
	def playEmbed(self, player):
		embed = discord.Embed(title=player.title, colour=discord.Colour(0xff0000), url=player.url)
		embed.set_author(name='Playing♪ @ YouTube', icon_url=f'{MAYMAYS_BASE_URL}/gb.png')
		embed.add_field(name='Uploader', value=player.uploader)
		if player.durationSec > 0:
			embed.add_field(name='Duration', value=player.duration)
		embed.set_thumbnail(url=player.thumbnail)
		return embed

	def getGuildQueue(self, ctx):
		if ctx.guild.id in self.guildQueues:
			guildQueue = self.guildQueues[ctx.guild.id]
		else:
			guildQueue = GuildQueue(ctx)
			self.guildQueues[ctx.guild.id] = guildQueue
		return guildQueue

	@commands.guild_only()
	@commands.command(aliases=['p'])
	async def play(self, ctx, *, query, videoId=None):
		"""Plays the requested song."""
		guildQueue = self.getGuildQueue(ctx)
		if ctx.voice_client is not None:
			if len(guildQueue.ytQueue) >= self.queueLimit: return await ctx.send(f'Queue Full. Capacity: ``{self.queueLimit}``') # check is pending
			if videoId is None: videoId = self.getVID(query)
			player = await YTDLSource.fromURL(ctx, f'https://www.youtube.com/watch?v={videoId}', loop=self.bot.loop)
			if ctx.voice_client.is_playing(): # try using if len(ytQueue) > 0: if errors, who knows?
				guildQueue.ytQueue.append(player)
				await ctx.send(embed=self.addedToQueueEmbed(player, guildQueue))
				# await ctx.send(f'``{player.title}`` added to queue position: ``#{len(guildQueue.ytQueue)}``')
			else:
				async with ctx.typing():
					await ctx.send('Bhai ne bola karne ka matlab karne ka!', embed=self.playEmbed(player))
					# await ctx.send(f'baja raha hu {player.title}')
				guildQueue.playLoop(ctx, player)

	@commands.guild_only()
	@commands.command()
	async def search(self, ctx, *, query):
		"""Queries the YouTube API and returns five results to select from."""
		params = {
			'part': 'snippet', 'type': 'video',
			# 'videoCategoryId': '10',
			'maxResults': 5, 'key': NETHR,
			'q': query
		}
		response = requests.get(url='https://youtube.googleapis.com/youtube/v3/search', params=params).json()['items']
		# pprint.pprint(response)
		songList = ''
		for i, song in enumerate(response):
			songList += f'\n**{i+1}**: {html.unescape(response[i]["snippet"]["title"])} - ``{html.unescape(response[i]["snippet"]["channelTitle"])}``'
		# Fix: if no search results are found, it'll still wait for reply and even try to play a song if one replies.
		# TODO: check if this works
		if songList == '':
			await ctx.send(f'**Search results for "{query}":** ``Kasuj na madyu :(``')
			return
		resultsMessage = await ctx.send(f'**Search results for "{query}":** ``Select from the following:``{songList}')
		def checkReply(msg): return msg.content.isdigit() and int(msg.content) in range(1, len(response) + 1) and msg.channel == ctx.channel
		try:
			choice = await self.bot.wait_for('message', check=checkReply, timeout=15) # 'message' refers to the 'on_message' event invoked by the bot. ref: https://discordpy.readthedocs.io/en/latest/api.html#event-reference
			await resultsMessage.edit(content=f'Your Choice: {choice.content}')
			if ctx.voice_client is None: await ctx.invoke(self.bot.get_command('join'))
			await ctx.invoke(self.bot.get_command('play'), query='PLACEHOLDER', videoId=response[int(choice.content) - 1]["id"]["videoId"])
		except asyncio.TimeoutError:
			await resultsMessage.edit(content='No reply. Command timed out.')
		except Exception as ex:
			logger.error(ex)

	@classmethod
	def npEmbed(self, guildQueue):
		embed = discord.Embed(title=guildQueue.npPlayer.title, colour=discord.Colour(0xff0000), url=guildQueue.npPlayer.url)
		embed.set_author(name='Now Playing♪ @ YouTube', icon_url=f'{MAYMAYS_BASE_URL}/gb.png')
		embed.add_field(name='Uploader', value=guildQueue.npPlayer.uploader)
		embed.add_field(name='Requested by', value=guildQueue.npPlayer.requester)
		if guildQueue.npPlayer.durationSec > 0:
			embed.add_field(name='Progress', value=self.progressBar(guildQueue.npPlayer.startTime, guildQueue.npPlayer.durationSec), inline=False)
		embed.set_thumbnail(url=guildQueue.npPlayer.thumbnail)
		return embed

	@classmethod
	def progressBar(self, st, du):
		bar, dot = '▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', '🔘'
		ct = datetime.datetime.now()
		pt = (ct.minute * 60 + ct.second) - (st.minute * 60 + st.second)
		if pt < 0: pt = 0
		cpos = round((pt * len(bar)) / du)
		if cpos < 1: cpos = 1
		if du < 3600:
			return f"``{bar[:cpos - 1] + dot + bar[cpos:]}`` ``{int(pt/60)}:{pt%60:02d} / {int(du/60)}:{du%60:02d}``"
		else:
			return f"``{bar[:cpos - 1] + dot + bar[cpos:]}`` ``{datetime.timedelta(seconds=pt)} / {datetime.timedelta(seconds=du)}``"

	@commands.guild_only()
	@commands.command()
	async def np(self, ctx):
		"""Now playing track"""
		guildQueue = self.getGuildQueue(ctx)
		if guildQueue.npPlayer is None:
			await ctx.send('Arree kuch baja na toh pehle...')
		else:
			await ctx.send(embed=self.npEmbed(guildQueue))

	@commands.guild_only()
	@commands.command(aliases=['q'])
	async def queue(self, ctx):
		guildQueue = self.getGuildQueue(ctx)
		if len(guildQueue.ytQueue) > 0:
			embed = discord.Embed(colour=discord.Colour(0xff0000))
			embed.set_author(name=f'Queue for {ctx.guild.name}', icon_url=f'{MAYMAYS_BASE_URL}/gb.png')
			embed.add_field(name='Now Playing', value=f'[{guildQueue.npPlayer.title}]({guildQueue.npPlayer.url}) | ``{guildQueue.npPlayer.duration}`` - ``{guildQueue.npPlayer.requester}``', inline=False)
			songList, totLen = '', 0
			for i, song in enumerate(guildQueue.ytQueue):
				songList += f'{i+1}. [{song.title}]({song.url}) | ``{song.duration}`` - ``{song.requester}``\n'
				totLen += song.durationSec
			embed.add_field(name='Up Next', value=songList)
			totLen = f'{int(totLen/60)}:{totLen%60:02d}' if totLen < 3600 else str(datetime.timedelta(seconds=totLen))
			embed.set_footer(text=f'Songs in Queue: {len(guildQueue.ytQueue)} | Total Length: {totLen}')
			await ctx.send(embed=embed)
		else:
			await ctx.send('Abe ye toh khali hai be...')

	@commands.guild_only()
	@commands.command(aliases=['rm'])
	async def remove(self, ctx, *, i):
		guildQueue = self.getGuildQueue(ctx)
		i = int(i) - 1
		if i in range(len(guildQueue.ytQueue)):
			rmSong = guildQueue.ytQueue.pop(i)
			await ctx.send(f'``{rmSong.title}`` removed from the queue position: ``{i+1}.``')
		else:
			await ctx.send('Index out of range.')

	@commands.command(aliases=['u', 'play2', 'p2'])
	async def url(self, ctx, *, url):
		"""Plays the media in the url."""
		async with ctx.typing():
			player = await YTDLSource.fromURL(ctx, url, loop=self.bot.loop)
			ctx.voice_client.play(player, after=lambda e: logger.error(e) if e else None)
		await ctx.send(f'Now playing: ``{url}``')

	@commands.command(aliases=['sb'])
	async def soundboard(self, ctx, *, code):
		"""Options: sw, ss, yay, ting, weebAsylum, rage"""
		# SoundBoard sw: Scheming Weasel, ss: Sneaky Snitch, ting: Message Tone, yay: Fluttershy Yay, weebAsylum: Weeb Asylum
		if code == 'sw': source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/SchemingWeasel.opus', **ffmpeg_options), volume=0.5)
		elif code == 'ss': source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/SneakySnitch.m4a', **ffmpeg_options), volume=0.5)
		elif code == 'yay': source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/fluttershy_yay.mp3', **ffmpeg_options), volume=0.5)
		elif code == 'ting': source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/ting.opus', **ffmpeg_options), volume=1)
		elif code == 'weebAsylum':
			await ctx.send(file=discord.File(f'{MAYMAYS_DIR_PATH}/weebAsylum.webp'))
			source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/weebAsylum.opus', **ffmpeg_options), volume=1)
		elif code == 'rage': source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('sounds/003_rage.wav', **ffmpeg_options), volume=1)
		ctx.voice_client.play(source, after=lambda e: logger.error(e) if e else None)

	@commands.command()
	@play.before_invoke
	@url.before_invoke
	@soundboard.before_invoke
	async def join(self, ctx):
		"""Join a user's VC."""
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send('You are not in any voice channel.')
		elif ctx.voice_client is not None:
			return await ctx.voice_client.move_to(ctx.author.voice.channel)

	@commands.command(aliases=['resume', 'unpause'])
	async def pause(self, ctx):
		"""Toggles Pause/Play"""
		if ctx.voice_client is not None:
			if ctx.voice_client.is_paused():
				# await ctx.send('Player already paused.')
				ctx.voice_client.resume()
			elif ctx.voice_client.is_playing():
				ctx.voice_client.pause()

	@commands.command()
	async def skip(self, ctx):
		"""Skips current track"""
		if ctx.voice_client is not None:
			if ctx.voice_client.is_playing():
				ctx.voice_client.stop()

	@commands.guild_only()
	@commands.command()
	async def stop(self, ctx):
		"""Stops playing Moozic"""
		guildQueue = self.getGuildQueue(ctx)
		guildQueue.ytQueue = []
		if ctx.voice_client is not None:
			if ctx.voice_client.is_playing():
				ctx.voice_client.stop()

	@commands.guild_only()
	@commands.command()
	async def leave(self, ctx):
		"""Leave the VC."""
		guildQueue = self.getGuildQueue(ctx)
		guildQueue.ytQueue = []
		if ctx.voice_client is not None:
			if ctx.voice_client.is_playing():
				ctx.voice_client.stop()
			await ctx.voice_client.disconnect()