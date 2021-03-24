from datetime import datetime
from discord.ext import tasks
from threading import Thread
import sys
import asyncio
from colored import fg

#Need to add the current date to each log message. As well as set up a logging system to store all the log messages.
class ColourfulConsole():
    def __init__(self):
        self.console_commands = []
        self.prefix = fg('247') + "[" + fg('226') + "Civil Servant" + fg('247') + "]"
    def log(self, message):
        print(self.prefix + fg('255') + ": " + fg('250') + message)
    
    def warn(self, message):
        print(self.prefix + fg('255') + ":" + fg('222') + message)

    def error(self, message):
        print(self.prefix + fg('255') + ":" + fg('204') + message)
