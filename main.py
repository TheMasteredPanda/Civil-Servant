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

def asyncio_run(future, as_task=True):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(_to_task(future, as_task, loop))
    else:
        nest_asyncio.apply(loop)
        return asyncio.run(_to_task(future, as_task, loop))

def _to_task(future, as_task, loop):
    if not as_task or isinstance(future, tasks.Task):
        return future
    return loop.create_task(future)

@bot.event
async def on_ready():
    console.initate_command_handler()
    console.log('Online')

async def shutdown_bot():
    console.log("Shutting bot down")     
    await asyncio_run(bot.logout())

@bot.command()
async def shutdown(ctx):
    console.log('Shutting bot down')
    console.shutdown_command_handler()
    await bot.logout()
    console.log('Bot shutdown')

console.register_command(Command('shutdown', shutdown_bot))
console.log('Starting discord bot...')
dotenv.load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
console.initate_command_handler()
