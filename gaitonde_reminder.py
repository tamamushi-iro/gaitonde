import os
import re
import logging
import sqlite3 as sql

from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)

load_dotenv()
TCS_GLD_ID = os.getenv('TCS_GLD_ID')
TCS_GENERAL_CHNL_ID = os.getenv('TCS_GENERAL_CHNL_ID')

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_name = 'gaitonde.db'
        self.db_table = 'reminders'
        self.tz_map = {
            'IST': 'Asia/Kolkata',          # Indian Standard Time
            'EST': 'America/New_York',      # Eastern Standard Time
            'EDT': 'America/New_York',      # Eastern Daylight Time
            'GMT': 'GMT',                   # Greenwich Mean Time,
            'PST': 'America/Los_Angeles',   # Pacific Standard Time
            'PDT': 'America/Los_Angeles',   # Pacific Daylight Time
            'UTC': 'UTC'                    # Coordinated Universal Time
        }
        # self.reminder_loop.start()
    
    def parse_timestamp(self, tsstr):
        m = re.match(r'(\d{1,2})[-_/](\d{1,2})[-_/](\d{2,4})[\s_T](\d{1,2}):*(\d{1,2})*\s*(am|AM|pm|PM)*\s*([a-zA-Z]{3})*', tsstr.strip())
        if m:
            date, month, year, hour, minute, time_of_day, timezone_abbr = m.groups()
            date, month, year = int(date), int(month), int(year)
            hour, minute = int(hour), int(minute) if minute else 0
            time_of_day = time_of_day.upper() if time_of_day else 'AM'
            timezone_abbr = timezone_abbr.upper() if timezone_abbr else 'IST'

            timestamp_str = f'{year + 2000 if year < 100 else year}-{month:02}-{date:02} {hour:02}:{minute:02} {time_of_day}'
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M %p')
            
            timezone = self.tz_map[timezone_abbr]
            dt = dt.replace(tzinfo=ZoneInfo(timezone))
            return dt
        else:
            logger.warning(f'parse_timestamp returned None for string: {tsstr}')
            return None
    
    # def cog_unload(self):
    # 	self.reminder_loop.cancel()
    
    @commands.command(aliases=['reminder', 'remindat'])
    async def remind(self, ctx, *, query):
        """
        Set Reminder. Usage: >remind <datetime:YYYY-MM-DD HH:MM> - <reminder note>"
        """
        if ctx.message.reference:
            remind_datetime = self.parse_timestamp(query)
            if remind_datetime:
                conn = sql.connect(self.db_name)
                cur = conn.cursor()
                count = cur.execute(f'SELECT count(id) from {self.db_table} WHERE guildID = {ctx.guild.id} AND active = 1;').fetchone()
                if count[0] >= 100:
                    await ctx.send(f'Guild Limit Reached: {count[0]}')
                    return
                cur.execute(
                    """
                    INSERT INTO {} (
                        remindDateTime, messageRefURL, addedBy, addedOn, guildID, active
                    ) VALUES (
                        :remindDateTime, :messageRefURL, :addedBy, :addedOn, :guildID, :active
                    );
                    """.format(self.db_table), {
                        'remindDateTime': remind_datetime,
                        'messageRefURL': ctx.message.reference.jump_url,
                        'addedBy': f'{ctx.author.name}<:>{ctx.author.id}',
                        'addedOn': str(datetime.now()).split('.')[0],
                        'guildID': ctx.guild.id,
                        'active': 1
                    }
                )
                conn.commit()
                conn.close()
                await ctx.send(f'Reminder Added for DateTime: {remind_datetime}')
            else:
                await ctx.send(f'Time stamp not recognised.')
        else:
            await ctx.send(
                f'Usage while replying to a message (<>* are optional): ``{ctx.prefix}{ctx.command} DD-MM-YYYY HH:<MM>* <AM/PM>* <IST>*``'
            )
    
    @commands.command(aliases=['listreminders', 'lr'])
    async def listReminders(self, ctx):
        """Show DB Entries"""
        conn = sql.connect(self.db_name)
        cur = conn.cursor()
        res = cur.execute(f'SELECT * FROM {self.db_table} WHERE guildID = {ctx.guild.id} ORDER BY remindDateTime DESC;')
        response = ''
        for i, row in enumerate(res):
            response += f"\n{i+1}. {row[1]} - {row[2]}"
        await ctx.send(f'Reminders for this Guild:\n```{response}```' if response else f'No Reminder found for this Guild.')
        conn.close()
