import importlib
import asyncio
from asyncio import tasks
from asyncio import futures
from asyncio.exceptions import CancelledError
import sys
import os
import dotenv
import discord
from discord.ext import commands, tasks
from utils.console import ColourfulConsole
from database import Database
import utils.config as config
from settings import Settings

'''
Python Discord Bot.

Written with nvim.
'''

bot = commands.Bot(command_prefix="?", description="Python Discord Bot")
console = ColourfulConsole()
database = Database(config.load_config()['MARIADB'])
settings = Settings('settings.json')

@bot.event
async def on_ready():
    console.log('Starting command listener.')
    console.log('Online')

@tasks.loop(seconds=2.0)
async def test_task():
    console.log('Hello')

async def shutdown_bot():
    console.log('Shutting bot down')
    await bot.logout()

@bot.command()
async def shutdown(ctx):
    await bot.logout()
    console.log('Bot shutdown')

for command_script in os.listdir('commands'): 
    if command_script.endswith('.py') is False:
            continue
    script = importlib.import_module("commands.{}".format(command_script).replace('.py', ''))
    command_class = getattr(script, 'Command')
    if command_class is None:
        raise Exception("Couldn't find class named 'Command' in script {}".format(script))
    bot.add_cog(command_class(bot, database, console, settings))
    console.log('Loaded command: {}'.format(command_script.replace('.py', '')))


console.log('Starting discord bot...')
dotenv.load_dotenv()
console.log('Loaded environment variables.')
bot.run(os.getenv('DISCORD_TOKEN'))
