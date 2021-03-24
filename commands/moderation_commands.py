import re
import os
import json
from enum import Enum
from discord.ext import commands
from discord.ext.commands import UserConverter, MemberConverter, Bot
from discord import Role, User, Member, Guild
from database import Database
from datetime import datetime
import utils.time as timeutils
from utils.time import TimeUnit
class PunishmentType(Enum):
    MUTE = 'mute'
    WARN = 'warn'
    BAN = 'ban'
    TEMP_BAN = 'tempban'
    TEMP_MUTE = 'tempmute'

    @classmethod
    def from_name(cls, name: str):
        for ptype in cls:
            if name.upper() == ptype.name:
                return ptype

#Model used for data stored in the MariaDB Punishment database. 
class Punishment():
    def __init__(self, punishment_id: float, bot: Bot, database: Database, user_id: float, guild_id: float, punishment_type: str, reason: str, duration: float, active: bool, started_at: str, updated_at: str):
        self.id = punishment_id
        self.guild: Guild = filter(lambda g: g.id == guild_id, bot.guilds)[0]
        self.member = self.guild.get_member(user_id)
        self.punishment_type: PunishmentType = PunishmentType.from_name(punishment_type)
        self.reason: str = reason
        self.duration: float = duration
        self.active: bool = active
        f = '%Y-%m-%d %H:%M:%S'
        self.started_at = datetime.strftime(started_at, f)
        self.updated_at = datetime.strftime(updated_at, f)
        self.deleted = False

        def get_guild():
            return self.guild

        def get_member():
            return self.member

        def get_punishment_type():
            return self.punishment_type

        def get_reason():
            return self.reason

        def get_duration():
            return self.duration

        def get_active():
            return self.active

        def get_started_at():
            return self.started_at

        def get_updated_at():
            return self.updated_at
    
        #Deletes this punishment entry in the table.
        def delete():
            passed = self.database.execute('delete from punishments where id=?', (self.id))
            if passed is True: self.deleted = True

        #If the punishment entry is an active punishment, this method will render the punishment inactive.
        def end_punishment():
            now = datetime.now()
            passed = self.database.execute('update punishments set updated_at=?, active=0 where id=?', (now.time().isoformat(), self.id))
            if passed is True:
                self.updated_at = now
                self.active = False 

class Command(commands.Cog):
    def __init__(self, bot: commands.Bot, database, console, settings):
        self.settings = settings #type: ignore
        self.bot = bot
        self.database: Database = database
        self.console = console
        self.database.execute("""
                CREATE TABLE IF NOT EXISTS punishments(
                    id INTEGER AUTO_INCREMENT PRIMARY KEY, 
                    user_id BIGINT NOT NULL, 
                    guild_id BIGINT NOT NULL,
                    type ENUM('mute', 'warn', 'ban', 'tempban', 'tempmute', 'tempwarn') not null, 
                    reason varchar(100) not null, 
                    duration INTEGER, 
                    active BOOLEAN DEFAULT FALSE,
                    started_at DATETIME, 
                    updated_at DATETIME)
                """)

    def add_punishment(self, ctx, accused: Member, punishment_type: PunishmentType, active = True, reason: str = "No Reason", duration: int = -1):
            self.database.execute("INSERT INTO punishments (user_id, guild_id, type, reason, duration, active, started_at, updated_at) VALUES (?,?,?,?,?,?,?,?)", (accused.id, ctx.guild.id, punishment_type.name, reason, duration, active, datetime.now().date().isoformat(), datetime.now().date().isoformat()))

    def is_muted(self, member: Member):
        result_set = self.database.execute("select count(*) from punishments where user_id=? and active=true", (member.id,))
        return False if result_set is None else result_set.rowcount > 0

    def convert_to_time(self, arg: str):
        sections = re.findall('\\d{1,2}\\w{1}', arg)
        total_value = 0

        for section in sections:
            split_section = re.split('(\\d)', section)
            total_value = total_value + timeutils.convert(int(split_section[0]), TimeUnit.from_name(split_section[1]), TimeUnit.MILISECONDS) 
            
        return total_value
    
    def get_active_punishments(self, guild_id: float, member_id: float):
        results = self.database.execute('select * from punishments where user_id=? and guild_id=? and active=1', (member_id, guild_id))
        punishments = list()

        if results is None or isinstance(results, bool):
            return punishments

        for entry in results:
            punishments.append(Punishment(entry.id, self.bot, self.database, entry.user_id, entry.guild_id, entry.type, entry.reason, entry.duration, True if entry.active == 1 else False, entry.started_at, entry.updated_at))

        return punishments

    #Checks if a user is banned. 
    async def is_banned(self, guild: Guild, member: Member):
        bans = await guild.bans()
        
        for entry in bans:
            if entry.user.id == member.id:
                return True

        return False

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        mute_role_id = self.settings.get()['punishments']['muterole']
        if len(filter(lambda r: r.id == mute_role_id, before.roles)) == 0:
            return

        if len(filter(lambda r: r.id == mute_role_id, after.roles)) != 0:
            return

        for entry in self.get_active_punishments(before.guild.id, before.id):
            if entry.get_punishment_type() == PunishmentType.MUTE or entry.get_punishment_type() == PunishmentType.TEMP_MUTE:
                entry.end_punishment()
                self.console.log('Ending {} mute of {} as mute role was manually removed.'.format('permanent' if entry.get_punishment_type() == PunishmentType.MUTE else 'temporary', str(after.user)))
    
    @commands.group()
    async def mod(self, ctx):
        pass


    @mod.command()
    async def ban(self, ctx, member: MemberConverter, delete_msg_days: int = 0, *args):
        if await self.is_banned(ctx.guild, member) is True:
            await ctx.send('User {} has already been banned.'.format(str(member.user)))
            return

        reason = "No reason"
        if len(args) > 0: reason = " ".join(args[:])
        self.add_punishment(ctx, member, PunishmentType.BAN, True, reason)
        member.ban(delete_message_days=delete_msg_days, reason=reason)
        msg = 'Permanently banned member {} for {}.'.format(str(member.user), reason)
        self.console.log(msg)
        await ctx.send(msg)

    @mod.command()
    async def temp_ban(self, ctx, member: MemberConverter, delete_msg_days: int = 0, duration: str = '1h', *args):
        if await self.is_banned(ctx.guild, member) is True:
            await ctx.send('User {} has already been banned.'.format(str(member.user)))
            return

        if re.march('\\d{1,2}\\w{1}', duration) is False:
            await ctx.send('Format for duration of ban is incorrect: Example: 1d10m4s.')
            return

        if self.settings.get()['punishments']['tempbanrole'] is None:
            await ctx.send('There is no role set to temp ban members')
            return
        
        converted_duration = self.convert_to_time(duration)
        reason = "No reason"
        if len(args) > 0: reason = " ".join(args[:])
        self.add_punishment(ctx, member, PunishmentType.TEMP_BAN, True, reason, converted_duration)
        msg = "Temporarily banned {} for {} for".format(str(member.user), reason, timeutils.format_time(timeutils.convert(converted_duration, TimeUnit.MILISECONDS, TimeUnit.SECONDS)))
        self.console.log(msg)
        await ctx.send(msg)
    
    @mod.command()
    async def mute(self, ctx, member: MemberConverter, *args):
        if self.is_muted(member) is True:
            await ctx.send("Member {} is muted.".format(member.name))
            return

        await member.add_roles(ctx.guild.get_role(self.settings.get()['punishments']['muterole']))
        self.add_punishment(ctx, member, PunishmentType.MUTE)
        reason = "No reason"
        if len(args) > 0: reason = " ".join(args[:])
        msg = "Permanently muted member {} for {}.".format(str(member.user), reason)
        self.console.log(msg)
        await ctx.send(msg)

    @mod.command(name="tempmute")
    async def temp_mute(self, ctx, member: MemberConverter, duration: str, *args):
        if self.is_muted(member) is True:
            await ctx.send("Member {} is not muted.".format(member.name))
            return

        if re.match('\\d{1,2}\\w{1}', duration) is False:
            await ctx.send('Format for duration of mute is incorrect. Example: 1d10m4s')
            return

        if (self.settings.get()['punishments']['muterole'] is None):
            await ctx.send("There is no role set to mute members.")
            return

        await member.add_roles(ctx.guild.get_role(self.settings.get()['punishments']['muterole']))
        converted_duration = self.convert_to_time(duration)
        reason = "No reason"
        if len(args) > 0: reason = " ".join(args[:])
        msg = "Temporarily muted {} for {}".format(str(member.user), timeutils.format_time(converted_duration))
        self.add_punishment(ctx, PunishmentType.TEMP_MUTE, reason, self.convert_to_time(duration))
        await ctx.send(msg)
        self.console.log(msg)

    @mod.command()
    async def warn(self, ctx, member: MemberConverter, *args):
        reason = "No reason"
        if len(args) > 0: reason = " ".join(args[:])
        self.add_punishment(ctx, member, PunishmentType.WARN, False, reason)
        msg = 'Warned {} for {}'.format(str(member.user), reason)
        await ctx.send(msg)
        self.console.log(msg)


    @mod.group()
    async def settings(self, ctx):
        pass

    @settings.group()
    async def set(self, ctx):
        pass
    
    @set.command(name="muterole")
    async def mute_role(self, ctx, role: Role):
        temp_settings = self.settings.get()
        temp_settings['punishments']['muterole'] = role.id #type: ignore
        self.settings.set(temp_settings)
        self.settings.save()
        await ctx.send('Set role to {}'.format(role.mention)) #type: ignore

    @set.command(name='tempbanrole')
    async def temp_ban_role(self, ctx, role: Role):
        temp_settings = self.settings.get()
        temp_settings['punishments']['tempbanrole'] = role.id
        self.settings.set(temp_settings)
        self.settings.save()
        await ctx.send('Set role to {}'.format(role.mention))
