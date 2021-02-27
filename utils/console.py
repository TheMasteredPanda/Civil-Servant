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

    @tasks.loop(seconds=1.0)
    async def command_listener(self):
        console_input = list(filter(lambda x: (x != '' and x != ' '), sys.stdin.readline().split('\n')))

        if (len(console_input) > 0):
            for command in self.console_commands:
                if (command.get_name() == console_input[0]):
                    cmd_string = console_input[0]
                    console_input.pop(0)
                    await command.on_command(cmd_string, console_input)

    def register_command(self, name, func):
        for command in self.console_commands:
            if (command.get_name() == name):
                raise Exception("Command name " + name + " has already been used")
        self.console_commands.append(Command(self, name, func))

class Command:
    def __init__(self, console, name, func):
       self.name = name;
       self.function = func
       self.child_commands = []
       self.parent_commands = []
       self.console = console

    def add_child_command(self, child):
        for child_command in self.child_commands:
            if child_command.name == child.name:
                raise Exception(child.name + " is alrady a child command of parent " + self.get_command_path())

        self.child_commands.append(child)

    def get_name(self):
        return self.name

    def add_parent_command(self, parent):
        self.parent_commands.append(parent)

    def get_command_path(self):
        path = ""

        for parent in self.parent_commands:
            path += parent.name + " "

        for child in self.child_commands:
            path += child.name + " "

        return path

    async def on_command(self, command, command_args):
        for arg in command_args:
            for child_command in self.child_commands:
                if command == child_command.name:
                    command.args.remove(arg)
                    child_command.on_command(arg, command_args)
                    return
        await self.function(*command_args)
