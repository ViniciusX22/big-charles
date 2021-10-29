from db import set_pattern, remove_pattern, get_patterns, set_delimiter


def pattern(args, guild_id):
    params = {
        'set': set_pattern,
        'del': remove_pattern,
    }

    if len(args) and args[0] in params:
        params[args[0]](args[1:], guild_id)


def list_patterns(args, guild_id):
    def parse_value(s):
        if s.startswith('<') and s.endswith('>'):
            return f'`{s[1:-1]}`'
        if s.startswith('\\<') and s.endswith('\\>'):
            return s[1:-2] + '>'
        return s

    patterns = []
    index = 1
    for pattern in get_patterns(guild_id):
        value = parse_value(pattern['value'])
        patterns.append(
            f'{index} - {value} = {"(" + str(pattern["chance"]) + "%) " if "chance" in pattern else ""}{pattern["response"]}')
        index += 1

    return '\n'.join(patterns)


commands = {
    'delimiter': set_delimiter,
    'pattern': pattern,
    'patterns': list_patterns
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
    text = commands[command](args, message.guild.id)
    if text:
        await message.channel.send(text)
