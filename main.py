from db import get_patterns, get_delimiter
from commands import run_command, commands
import discord
import re
import os
from random import randrange
from dotenv import load_dotenv
load_dotenv()


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

    def match_pattern(value):
        if value.startswith('user:'):
            author_id = int(value.split(':')[1])
            return author_id == message.author.id
        elif value.startswith('role:'):
            role_id = int(value.split(':')[1])
            for role in message.author.roles:
                if role_id == role.id:
                    return True
            return False
        else:
            r = re.compile(value, flags=re.I)
            return r.search(message.content)

    delimiter = None
    try:
        delimiter = get_delimiter(message.guild.id)
    except IndexError:
        delimiter = '!'

    splited_message = message.content.split(' ')
    if message.content.startswith(delimiter) and splited_message[0][len(delimiter):] in commands:
        await run_command(splited_message[0][len(delimiter):], splited_message[1:], message)
    else:
        patterns = get_patterns(message.guild.id)
        for pattern in patterns:
            try:
                value = parse_value(pattern['value'])
                pattern_chance = pattern['chance'] if 'chance' in pattern else 100
                if match_pattern(value) and randrange(0, 100) <= pattern_chance:
                    await message.channel.send(pattern['response'])
                    break
            except Exception as e:
                print('Exception: ' + str(e))

client.run(os.getenv('TOKEN'))
