import discord
import re
import os

client = discord.Client()

patterns = ['nao', 'não']
cmd = re.compile('|'.join(patterns), re.I)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if cmd.search(message.content):
        await message.channel.send('Hello!')

client.run(os.getenv('TOKEN'))
