import nest_asyncio
import asyncio
from asyncio import tasks
from asyncio import futures
from asyncio.exceptions import CancelledError
import sys
import os
import dotenv
import discord
from discord.ext import commands
from utils.console import ColourfulConsole, Command

'''
Python Discord Bot.

Written with nvim.
'''

bot = commands.Bot(command_prefix="?", description="Python Discord Bot")
console = ColourfulConsole()
loop_bool = True

@bot.event
async def on_ready():
    console.initate_command_handler()
    console.log('Online')

async def shutdown_bot():
    console.log("Shutting bot down")     
    console.pause_command_listener()
    await bot.logout()


@bot.command()
async def shutdown(ctx):
    console.pause_command_listener()
    await bot.logout()
    console.log('Bot shutdown')

console.register_command(Command('shutdown', shutdown_bot))
console.log('Starting discord bot...')
dotenv.load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
console.initate_command_handler()
