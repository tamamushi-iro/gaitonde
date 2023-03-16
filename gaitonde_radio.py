import os
import logging
import urllib, json
import asyncio, discord
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger(__name__)

load_dotenv()
MAYMAYS_BASE_URL = os.getenv('MAYMAYS_BASE_URL')

ffmpeg_options = {
	'options': '-vn -loglevel quiet'
}

class Radio(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

#	@classmethod
	def npEmbed(self):
		with open('nowPlaying.json', 'r') as jsonFile:
			data = json.load(jsonFile)
		currSong = data['d']['song']
		csTitle = '-' if currSong['title'] == "" else currSong['title']
		csAlbum = '-' if currSong['albums'] == [] else currSong['albums'][0]['name']
		csArtist = '-' if currSong['artists'] == [] else currSong['artists'][0]['name']
		csTime = '-' if currSong['duration'] == 0 else f"{int(currSong['duration']/60)}:{currSong['duration']%60:02d}"
		if currSong['albums'] == []:
			csThumb = 'https://listen.moe/_nuxt/img/blank-dark.cd1c044.png'
		else:
			if currSong['albums'][0]['image'] is not None:
				csThumb = f"https://cdn.listen.moe/covers/{urllib.parse.quote_plus(currSong['albums'][0]['image'])}"
			else:
				csThumb = 'https://listen.moe/_nuxt/img/blank-dark.cd1c044.png'
		embed = discord.Embed(title='Now Playing♪ @ LISTEN.moe', colour=discord.Colour(16712027), url='https://listen.moe')
		# embed.set_author(name='Gaitonde', url='https://listen.moe', icon_url=f'{MAYMAYS_BASE_URL}/gb.png')
		embed.add_field(name='Title', value=csTitle, inline=False)
		embed.add_field(name='Artist', value=csArtist)
		embed.add_field(name='Album', value=csAlbum)
		embed.add_field(name='Duration', value=csTime)
		if currSong['duration'] != 0:
			embed.add_field(name='Progress', value=self.progressBar(data['d']['startTime'][:-1], currSong['duration']), inline=False)
		embed.set_thumbnail(url=csThumb)
		return embed

#	@classmethod
	def progressBar(self, st, du):
		bar, dot = '▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', '🔘'
		st = datetime.fromisoformat(st)
		ct = datetime.now()
		pt = (ct.minute * 60 + ct.second) - (st.minute * 60 + st.second)
		if pt < 0: pt = 0
		cpos = round((pt * len(bar)) / du)
		if cpos < 1: cpos = 1
		return f"``{bar[:cpos - 1] + dot + bar[cpos:]}`` ``{int(pt/60)}:{pt%60:02d} / {int(du/60)}:{du%60:02d}``"

	@commands.command()
	async def moe(self, ctx):
		"""Play LISTEN.moe's J-Pop Stream."""
		if ctx.voice_client is not None:
			source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('https://listen.moe/stream', **ffmpeg_options), volume=0.5)
			ctx.voice_client.play(source, after=lambda e: logger.error(e) if e else None)

	@commands.command()
	@moe.before_invoke
	async def doumo(self, ctx):
		"""Join user's VC."""
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send('あなたはボイスチャンネルにいません。')
		elif ctx.voice_client is not None:
			return await ctx.voice_client.move_to(ctx.author.voice.channel)

	@commands.command()
	async def jp(self, ctx):
		"""Now playing on the LISTEN.moe stream."""
		await ctx.send(embed=self.npEmbed())

	@commands.command()
	async def kaero(self, ctx):
		"""Leave the VC."""
		if ctx.voice_client is not None:
			if ctx.voice_client.is_playing():
				ctx.voice_client.stop()
			await ctx.voice_client.disconnect()
