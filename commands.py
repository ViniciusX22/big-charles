from db import set_pattern, remove_pattern, get_patterns, set_delimiter


def pattern(args, guild_id):
    params = {
        'set': set_pattern,
        'del': remove_pattern,
    }

    if len(args) and args[0] in params:
        params[args[0]](args[1:], guild_id)


def list_patterns(args, guild_id):
    patterns = []
    for pattern in get_patterns(guild_id):
        patterns.append(
            f'{pattern["value"]} = {"(" + str(pattern["chance"]) + "%) " if "chance" in pattern else ""}{pattern["response"]}')

    return '\n'.join(patterns)


commands = {
    'delimiter': set_delimiter,
    'pattern': pattern,
    'patterns': list_patterns
}


def parse_args(args):
    if len(args) < 2:
        return args

    first_index = 0
    while first_index < len(args):
        arg = args[first_index]
        if arg.startswith('`'):
            last_index = None
            for index, arg in enumerate(args):
                if arg.endswith('`'):
                    last_index = index
                    break

            if last_index is not None:
                arg = ' '.join(args[first_index:last_index+1])[1:-1]
                args = args[:first_index] + [arg] + args[last_index+1:]

        first_index += 1

    return args


async def run_command(command, args, message):
    args = parse_args(args)
    text = commands[command](args, message.guild.id)
    if text:
        await message.channel.send(text)
