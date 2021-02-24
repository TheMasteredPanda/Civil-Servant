import sys
import asyncio
from colored import fg

def executed(*args, **kwargs):
    def decorator(func):
        def wrapper():
            print("Executing " + func.__name__ + ".")
            func(*args, **kwargs)
            print("Executed " + func.__name__ + ".")
        return wrapper
    return decorator

#Need to add the current date to each log message. As well as set up a logging system to store all the log messages.
class ColourfulConsole():
    def __init__(self):
        self.console_commands = []
        self.prefix = fg('247') + "[" + fg('226') + "Civil Servant" + fg('247') + "]"
        self.pause = 0

    def log(self, message):
        print(self.prefix + fg('255') + ": " + fg('250') + message)
    
    def warn(self, message):
        print(self.prefix + fg('255') + ":" + fg('222') + message)

    def error(self, message):
        print(self.prefix + fg('255') + ":" + fg('204') + message)

    def initate_command_handler(self):
        print("Initating command handler.")
        self.console_command_handler_task = asyncio.create_task(self.command_listener()) 
        print("Initated command handler.")
        print(self.console_command_handler_task)

    @executed
    def pause_command_listener(self):
        print("Pausing command listener")
        self.pause = 1

    async def command_listener(self):
        print("Command listener enabled.")

        while True:
            if (self.pause == 1):
                print("Paused command listener")
                break

            console_input = sys.stdin.readline()
            if (console_input == ' ' or console_input == '' or len(console_input.split('\n')) == 0):
                    continue
            await self.process_console_input(console_input)

    def shutdown_command_handler(self):
        self.console_command_handler_task.cancel()


    def register_command(self, command):
        for cmd in self.console_commands:
            if cmd.name == command.name:
                raise Exception(cmd.name + " is already registered in the console command list.")

        print("Registering command " + command.name + ".")
        self.console_commands.append(command)

    async def process_console_input(self, command_input):
        print("Processing console input.")
        split_input = list(filter(lambda x: (x != None and x != '' and x != ' '), command_input.split('\n')))
        print(split_input)
        for cmd in self.console_commands:
            if cmd.name == split_input[0]:
                command = split_input[0]
                split_input.remove(split_input[0])
                await cmd.on_command(command, split_input)
        



class Command:
    def __init__(self, name, func):
       self.name = name;
       self.function = func
       self.child_commands = []
       self.parent_commands = []

    def add_child_command(self, child):
        for child_command in self.child_commands:
            if child_command.name == child.name:
                raise Exception(child.name + " is alrady a child command of parent " + self.get_command_path())

        self.child_commands.append(child)


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
                    await child_command.on_command(arg, command_args)
                    return

        await self.function(*command_args)
