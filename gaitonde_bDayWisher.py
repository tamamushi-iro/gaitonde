# Look into discord.py's tasks: https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html - DONE
# TODO: Look into: https://stackoverflow.com/questions/1301493/setting-timezone-in-python

import os
import re
import json
import logging
import sqlite3 as sql

from time import time
from pprint import pformat
from dotenv import load_dotenv
from discord.ext import tasks, commands
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

load_dotenv()
TCS_GLD_ID = os.getenv('TCS_GLD_ID')
TCS_GENERAL_CHNL_ID = os.getenv('TCS_GENERAL_CHNL_ID')
TCS_EVERINYAN_ROLE_ID = os.getenv('TCS_EVERINYAN_ROLE_ID')

TEST_GLD_ID = os.getenv('TEST_GLD_ID')
TEST_GENERAL_CHNL_ID = os.getenv('TEST_GENERAL_CHNL_ID')

class BDayWisher(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db_name = 'bDayBoiis.db'
		self.db_table = 'birthday_boi'
		self.wishing_loop.start()

		# # get invite to a Server
		# print(type(self.bot))
		# print(self.bot.guilds)
		# print(self.bot.get_guild(TEST_GLD_ID).channels)
		# invite = await self.bot.get_guild(TEST_GLD_ID).get_channel(TEST_GENERAL_CHNL_ID).create_invite(max_uses=1)
		# print(invite.url)
	
	def cog_unload(self):
		self.wishing_loop.cancel()
	
	@commands.command(aliases=['addboii'])
	async def addBoii(self, ctx, *, query):
		"""Add BDay and Boii. Usage: <command> @<bdboi-mention> "<name>" "<nickname>" <dob:YYYY-MM-DD>"""
		query = re.match(r'<@(\d*)> *["\'](.*)["\'] *["\'](.*)["\'] *(\d{4}-\d{2}-\d{2})$', query.strip())
		if query:
			discordID, fullName, nickname, dob = query.groups()
			conn = sql.connect(self.db_name)
			cur = conn.cursor()
			count = cur.execute(f'SELECT count(id) from {self.db_table} WHERE guildID = {ctx.guild.id};').fetchone()
			if count[0] >= 50:
				await ctx.send(f'Guild Limit Reached: {count[0]}')
				return
			cur.execute(
				"""
				INSERT INTO {} (
					name, nickname, discordID, dob, addedBy, addedOn, guildID
				) VALUES (
					:name, :nickname, :discordID, :dob, :addedBy, :addedOn, :guildID
				);
				""".format(self.db_table), {
					'name': fullName,
					'nickname': nickname,
					'discordID': discordID,
					'dob': date.fromisoformat(dob),
					'addedBy': f'{ctx.author.name}<:>{ctx.author.id}',
					'addedOn': str(datetime.now()).split('.')[0],
					'guildID': ctx.guild.id
				}
			)
			conn.commit()
			conn.close()
			await ctx.send(f'BDayBoii ``{nickname}`` added with DOB: ``{dob}``')
		else:
			await ctx.send(f'Usage: \n``{ctx.prefix}{ctx.command} @<bdboi-mention> "<name>" "<nickname>" <dob:YYYY-MM-DD>``')
	
	@commands.command(aliases=['removeboii'])
	async def removeBoii(self, ctx, *, query):
		"""Remove a mentioned Boii"""
		discordID = re.match(r'^<@(\d*)>$', query.strip())
		if discordID:
			discordID = discordID.groups()[0]
			conn = sql.connect(self.db_name)
			cur = conn.cursor()
			cur.execute(f'DELETE FROM {self.db_table} WHERE discordID = {discordID} and guildID = {ctx.guild.id};')
			conn.commit()
			conn.close()
			await ctx.send(f"Removed Boii: <@{discordID}> from Guild's BDayBoii List.")
		else:
			await ctx.send(f'Usage: \n``{ctx.prefix}{ctx.command} @<bdboi-mention>``')
	
	@commands.command(aliases=['listboiis', 'listboii'])
	async def listBoiis(self, ctx):
		"""Show DB Entries"""
		conn = sql.connect(self.db_name)
		cur = conn.cursor()
		res = cur.execute(f'SELECT * FROM {self.db_table} WHERE guildID = {ctx.guild.id} ORDER BY dob DESC;')
		response = ''
		for i, row in enumerate(res):
			response += f"\n{i+1}. {row[2]} - {row[4]}"
		await ctx.send(f'Birthday Boiis for this Guild:\n```{response}```' if response else f'No BDayBoii added in this Guild.')
		conn.close()
	
	@commands.command(aliases=['showboii'])
	async def showBoii(self, ctx, *, query):
		"""Show Boii Info"""
		discordID = re.match(r'^<@(\d*)>$', query.strip())
		if discordID:
			discordID = discordID.groups()[0]
			conn = sql.connect(self.db_name)
			cur = conn.cursor()
			res = cur.execute(f'SELECT * FROM {self.db_table} WHERE discordID = {discordID} and guildID = {ctx.guild.id};').fetchone()
			response = pformat({
				'name': res[1], 'nickname': res[2],
				# 'discordID': res[3],
				# 'guild': res[7],
				'dob': res[4],
				'addedBy': res[5].split("<:>")[0],
				'addedOn': res[6]
			}, sort_dicts=False)
			for char in ['{', '}', "'", ',', '"']: response = response.replace(char, '')
			await ctx.send(f"Showing Boii: <@{res[3]}>\n``` {response}```")
			conn.close()
		else:
			await ctx.send(f'Usage: \n``{ctx.prefix}{ctx.command} @<bdboi-mention>``')
	
	@commands.command(aliases=['upcomingbday', 'upcomingbdays', 'nextbday', 'nextbdays'])
	async def nextBday(self, ctx):
		"""Show the upcoming birthdays in the Guild for the next 3 months."""
		today = (datetime.now() + timedelta(hours=5, minutes=30)).date()	# in IST
		conn = sql.connect(self.db_name)
		cur = conn.cursor()
		res = cur.execute(f'SELECT * FROM {self.db_table} WHERE guildID = {ctx.guild.id};').fetchall()
		conn.close()
		next_bdays = {}
		for row in res:
			dob = date.fromisoformat(row[4])
			dob_this_year = date(year=today.year, month=dob.month, day=dob.day)
			dob_next_year = date(year=today.year + 1, month=dob.month, day=dob.day)
			if today < dob_this_year < today + relativedelta(months=3):
				next_bdays[dob_this_year.isoformat()] = row[2]
			if today < dob_next_year < today + relativedelta(months=3):
				next_bdays[dob_next_year.isoformat()] = row[2]
		next_bdays = pformat(next_bdays, sort_dicts=True)
		for char in ['{', '}', "'", ',', '"']: next_bdays = next_bdays.replace(char, '')
		await ctx.send(f'Upcoming BDays (next 3 months):\n``` {next_bdays}```')

	@tasks.loop(minutes=1)
	async def wishing_loop(self):
		# print(self.bot.get_guild(TCS_GLD_ID).roles)
		# NOTE: CURRENT CODE FOR TCS GUILD ONLY. Start from below for loop to make it work for all guilds.
		# for guild in self.bot.guilds:
		# print(self.wishing_loop.current_loop, self.wishing_loop.next_iteration)
		# NOTE: server runs in UTC time zone
		today = datetime.now() + timedelta(hours=5, minutes=30)	# in IST
		# logger.warning(f'wishing_loop.current_loop: {self.wishing_loop.current_loop}, wishing_loop.next_iteration: {self.wishing_loop.next_iteration}')
		if today.hour == 0 and today.minute == 0:
			# logger.warning(f'wishing_loop.current_loop: {self.wishing_loop.current_loop}, wishing_loop.next_iteration: {self.wishing_loop.next_iteration}')
			chicardoChat_general = self.bot.get_guild(TCS_GLD_ID).get_channel(TCS_GENERAL_CHNL_ID)
			conn = sql.connect(self.db_name)
			cur = conn.cursor()
			res = cur.execute(f"SELECT * FROM {self.db_table} WHERE guildID = '{TCS_GLD_ID}';").fetchall()
			conn.close()
			for row in res:
				dob = date.fromisoformat(row[4])
				year, month, day = dob.year, dob.month, dob.day
				if today.month == month and today.day == day:
					# await chicardoChat_general.send(f"<@&{TCS_EVERINYAN_ROLE_ID}>\n<@{row[3]}> Happy Jayanti {row[2]}! You are {today.year - year} years old today.")
					await chicardoChat_general.send(f"<@&{TCS_EVERINYAN_ROLE_ID}>\n<@{row[3]}> Happy Jayanti {row[2]}!")

			# time_delta = datetime(today.year, today.month, today.day + 1, hour=0, minute=0, second=0) - datetime.now() - timedelta(seconds=19800)
			# self.wishing_loop.change_interval(seconds=time_delta.seconds + 1)
	
	# we need to wait for the bot to be ready
	# as failing to do so will raise an attribute error:
	# AttributeError: 'NoneType' object has no attribute 'change_presence'
	@wishing_loop.before_loop
	async def before_wishing_loop(self):
		await self.bot.wait_until_ready()