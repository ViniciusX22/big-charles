from db import set_pattern, remove_pattern, get_patterns, set_delimiter, get_total
from os import getenv
from utils import is_int
from math import ceil
from pyfiglet import Figlet, FontNotFound
from economy import commands as economy_commands

PAGE_SIZE = int(getenv('PAGE_SIZE', 30))


def pattern(args, guild, author):
    params = {
        'set': set_pattern,
        'del': remove_pattern,
    }

    if len(args) and args[0] in params:
        params[args[0]](args[1:], guild.id)


def list_patterns(args, guild, author):
    def parse_value(s):
        if s.startswith('<') and s.endswith('>'):
            return f'`{s[1:-1]}`'
        if s.startswith('\\<') and s.endswith('\\>'):
            return s[1:-2] + '>'
        return s

    def page_index(page=1):
        return f'**Página [{page}/{ceil(get_total(guild.id) / PAGE_SIZE)}]**'

    def get_patterns_at_page(page=0, limit=PAGE_SIZE):
        patterns = []
        index = 1 + PAGE_SIZE * page
        for pattern in get_patterns(guild_id, skip=page * PAGE_SIZE, limit=limit):
            value = parse_value(pattern['value'])
            patterns.append(
                f'{index} - {value} = {"(" + str(pattern["chance"]) + "%) " if "chance" in pattern else ""}{pattern["response"]}')
            index += 1
        return '\n'.join(patterns)

    if len(args) == 1:
        msgs = []
        if args[0] == 'full':
            page = 0
            msg = get_patterns_at_page(page)
            while msg != '':
                msgs.append(msg)
                page += 1
                msg = get_patterns_at_page(page)

        elif is_int(args[0]) and int(args[0]) > 0:
            msgs.append(page_index(
                int(args[0])) + '\n' + get_patterns_at_page(int(args[0]) - 1))

        return msgs
    else:
        return page_index() + '\n' + get_patterns_at_page()


def get_help(args, guild, author):
    return getenv('WIKI_URL')


def use_figlet(args, guild, author):
    if len(args) < 1:
        return

    font = None
    if args[0].startswith('f=') or args[0].startswith('font='):
        font = args[0][args[0].index('=') + 1:]

    index = 0 if not font else 1
    if not font:
        font = 'standard'

    text = ' '.join(args[index:])
    wrapper = '```'
    try:
        f = Figlet(font=font)
        return f'{wrapper}{f.renderText(text)}{wrapper}'
    except FontNotFound:
        return 'Fonte inválida bro'


commands = {
    'delimiter': set_delimiter,
    'pattern': pattern,
    'patterns': list_patterns,
    'help': get_help,
    'figlet': use_figlet,
    **economy_commands
}


def parse_args(args):
    if len(args) < 2:
        return args

    def parse_multiwords_wrapper(a):
        multiwords_wrapper = '`'
        first_index = 0
        while first_index < len(a):
            arg = a[first_index]
            if arg.startswith(multiwords_wrapper):
                last_index = None
                for index, arg in enumerate(a):
                    if arg.endswith(multiwords_wrapper):
                        last_index = index
                        break

                if last_index is not None:
                    arg = ' '.join(a[first_index:last_index+1])[1:-1]
                    a = a[:first_index] + [arg] + a[last_index+1:]

            first_index += 1
        return a

    args = parse_multiwords_wrapper(args)

    return args


async def run_command(command, args, message):
    args = parse_args(args)
    response = commands[command](args, message.guild, message.author)
    if response is not None:
        if type(response) == list:
            for line in response:
                if line:
                    await message.channel.send(line)
        elif type(response) == dict:
            await message.channel.send(**response)
        else:
            await message.channel.send(response)
