import discord
import re
import os
from random import randrange
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

    def parse_value(value):
        if value.startswith('<') and value.endswith('>'):
            return value[1:-1]
        if value.startswith('\\<') and value.endswith('\\>'):
            value = value[1:-2] + '>'
        return re.escape(value)

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
            try:
                value = parse_value(pattern['value'])
                r = re.compile(value, flags=re.I)
                pattern_chance = pattern['chance'] if 'chance' in pattern else 100
                if r.search(message.content) and randrange(0, 100) <= pattern_chance:
                    await message.channel.send(pattern['response'])
                    break
            except Exception as e:
                print('Exception: ' + str(e))

client.run(os.getenv('TOKEN'))
