import discord
import re
import os
from dotenv import load_dotenv
load_dotenv()
from commands import run_command, commands
from db import get_patterns, get_delimiter


client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    delimiter = None
    try:
        delimiter = get_delimiter(message.guild.id)
    except IndexError:
        delimiter = '!'

    splited_message = message.content.split(' ')
    if message.content.startswith(delimiter) and splited_message[0][1:] in commands:
        await run_command(splited_message[0][1:], splited_message[1:], message)
    else:
        patterns = get_patterns(message.guild.id)
        for pattern in patterns:
            r = re.compile(pattern['value'], flags=re.I)
            if r.search(message.content):
                await message.channel.send(pattern['response'])
                break

client.run(os.getenv('TOKEN'))
