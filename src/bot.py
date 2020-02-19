import datetime
import os
import io
import discord
import logging
import pint
import re
from cysystemd.daemon import notify, Notification
from configparser import ConfigParser
from discord import Game, Forbidden
from discord.ext import commands
from discord.ext.commands import CommandNotFound, DisabledCommand, CheckFailure, MissingRequiredArgument, \
    BadArgument, TooManyArguments, UserInputError, CommandOnCooldown

config = ConfigParser()
config.read('./config/config.ini')
logger = logging
TOKEN = os.environ['TOKEN']
prefix = config["General"]["prefix"]
version = config["Info"]["version"]
extensions = config["Extensions"]["extensions"]

start = datetime.datetime.now()
logger.basicConfig(level=logging.INFO)

bot = commands.Bot(commands.when_mentioned_or(prefix))
bot.registry = pint.UnitRegistry()
bot.quantity = bot.registry.Quantity
bot.paginator = commands.Paginator(prefix='```', suffix='```', max_size=1950)
bot.page = 0

extensions = config["Extensions"]["extensions"]
startup_extensions = []
for ext in extensions.split(', '):
    startup_extensions.append(ext)


def setup_registry():
    bot.registry.load_definitions('./config/defs.txt')


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    elif message.guild.name not in config["General"]["servers"]:
        return
    elif message.channel.name not in config["General"]["channels"]:
        return
    elif isinstance(message.channel, discord.abc.PrivateChannel):
        return

    if message.channel.id == 648282608106733569:
        num = 0
        fails = ""
        dupes = ""
        lines = str(message.content).strip('`').split("\n")
        for line in lines:
            match = re.match(
                "^`{0,3}(.+)\\s+-+\\s+(((http|https)://|)(www\\.|)youtube\\.com\\/(channel\\/|user\\/)(["
                "a-zA-Z0-9_\\-]{1,}))\\s*`{0,3}", line.strip())
            if match:
                channel = bot.get_channel(676374873186238500)
                with io.open("channels.txt", "r", encoding='utf16') as f:
                    if match.group(1).lower() in f.read().lower():
                        dupes += match.group(1)
                f.close()
                with io.open("channels.txt", "a+", encoding='utf16') as f:
                    if dupes:
                        pass
                    else:
                        num += 1
                        f.write(f"{match.group(1)} - {match.group(2)}")
                        await channel.send(f"`youtube-dl -i -f 251/140/bestaudio --write-info-json --write-thumbnail "
                                           f"--download-archive archive.txt \"{match.group(2)}\"`"
                                           f"\n\n"
                                           f"`Requested by:` {message.author.mention}\nhttps://discordapp.com/channels/"
                                           f"{message.guild.id}/{message.channel.id}/{message.id}")
                f.close()
            elif re.search("((?:https?:)?//)?((?:www|m)\\.)?((?:youtube\\.com|youtu.be))(/(?:["
                           "\\w\\-]+\\?v=|embed/|v/)?)([\\w\\-]+)(\\S+)?$", line.strip()):
                fails += "Failed on line: `" + line.strip() + "`\n"
            else:
                return

        response = ""
        if num > 0:
            response += f"Added {num} links!\n"
        if dupes:
            response += f"Your links had these duplicates: \n{dupes}\n"
        if fails:
            response += f"Failed on these links: \n{fails}\n " \
                        f"Use ~ahelp to see best way to input links."
        await message.channel.send(response)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name=prefix + "help for usage."))
    notify(Notification.READY)
    print(f" --- Logged in: {bot.user.name} | {bot.user.id} | {version} --- ")


@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Error {ctx}, {error}")
    errors = {
        CommandNotFound: 'Command not found.',
        DisabledCommand: 'Command has been disabled.',
        CheckFailure: 'Missing required permissions to issue command.',
        MissingRequiredArgument: 'Command missing required arguments.',
        BadArgument: 'Failed parsing given arguments.',
        TooManyArguments: 'Too many arguments given for command.',
        UserInputError: 'User input error.',
        CommandOnCooldown: f'{error}',
        Forbidden: 'I do not have the correct permissions.'
    }
    for error_type, text in errors.items():
        if isinstance(error, error_type):
            return await ctx.message.channel.send("Command error: " + errors[error_type])


if not os.path.exists("./config/config.ini"):
    logger.error("No configs found, please create one.")

if __name__ == '__main__':
    for extension in startup_extensions:
        print(extension)
        bot.load_extension(extension)

setup_registry()

bot.run(TOKEN)
