import discord
import re
import os
from dotenv import load_dotenv
load_dotenv()

from db import add_pattern, get_patterns

client = discord.Client()

commands = {
    'setpattern': add_pattern
}

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!") and message.content.split(' ')[0][1:] in commands:
        commands[message.content.split(' ')[0][1:]](message.content.split(' ')[1:])
    else:
        patterns = get_patterns()
        for pattern in patterns:
            r = re.compile(pattern['value'], flags=re.I)
            if r.search(message.content):
                await message.channel.send(pattern['response'])
                break

client.run(os.getenv('TOKEN'))
