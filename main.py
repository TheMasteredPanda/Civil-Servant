import nest_asyncio
import asyncio
from asyncio import tasks
from asyncio import futures
from asyncio.exceptions import CancelledError
import sys
import os
import dotenv
import discord
from discord.ext import commands, tasks
from utils.console import ColourfulConsole, Command
from commands.test_cmd import TestCommand

'''
Python Discord Bot.

Written with nvim.
'''

bot = commands.Bot(command_prefix="?", description="Python Discord Bot")
console = ColourfulConsole()
loop_bool = True

@bot.event
async def on_ready():
    console.log('Starting command listener.')
    console.log('Online')
    console.command_listener.start()

async def shutdown_bot():
    console.log('Shutting bot down')
    await bot.logout()

@bot.command()
async def shutdown(ctx):
    await bot.logout()
    console.log('Bot shutdown')

console.register_command('shutdown', shutdown_bot)
console.log('Starting discord bot...')
dotenv.load_dotenv()
console.log('Loaded environment variables.')
bot.add_cog(TestCommand(bot))
bot.run(os.getenv('DISCORD_TOKEN'))
