import asyncio
from asyncio import tasks
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

@bot.event
async def on_ready():
    console.log('Online')
    await asyncio.create_task(command_listener())

async def command_listener():
    print("Command listener enabled")

    while True:
        console_input = sys.stdin.readline()
        await console.process_console_input(console_input)
        pass

async def shutdown_bot():
    console.log("Shutting bot down") 
    await bot.close()
    sys.exit()
    

console.register_command(Command('shutdown', shutdown_bot))
console.log('Starting discord bot...')
dotenv.load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
asyncio.run(command_listener())
