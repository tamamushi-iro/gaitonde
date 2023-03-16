import os, asyncio, discord
import logging
# import pprint
from dotenv import load_dotenv
from discord.ext import commands
from gaitonde_radio import Radio
from gaitonde_general import General
from gaitonde_ytstream import YTStream
from gaitonde_bDayWisher import BDayWisher

logging.basicConfig(filename='.errors/gaitonde_error.log', level=logging.WARNING, format='[%(asctime)s] %(levelname)s {%(pathname)s:%(lineno)d} %(name)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('GAITONDE_TOKEN')

prefix = '>'

intents = discord.Intents.default()
# intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), description='"Apun Bhagwan tha, ek tayme, bahut pehle." - Gaitonde probably', intents=intents)

@bot.event
async def on_ready():
	logger.warning(f'Bot Connected. Name: {bot.user.name}, ID: {bot.user.id}')

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		return
	if isinstance(error, commands.CommandInvokeError):
		logger.error(f'command: {prefix}{ctx.command} | kwargs: {str(ctx.args[1].kwargs)} | error: {error}')
		return
	if isinstance(error, commands.MissingRequiredArgument):
		return await ctx.send(f'Command "{ctx.command}": A required argument is missing.')
	logger.error(f'command: {prefix}{ctx.command} | error: {error}')

bot.add_cog(General(bot))
bot.add_cog(Radio(bot))
bot.add_cog(YTStream(bot))
bot.add_cog(BDayWisher(bot))

bot.run(TOKEN)
