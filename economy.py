import re
from db import get_db
from os import getenv
from random import randrange
from decimal import Decimal
from time import time
from datetime import timedelta

DAILY_MIN = float(getenv('DAILY_MIN', 50))
DAILY_MAX = float(getenv('DAILY_MAX', 100))
CURRENCY = getenv('CURRENCY', '$')

ONE_DAY = 86400


def format_money(money):
    return '{} {:n}'.format(CURRENCY, Decimal(str(round(money, 2))))


def format_time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds % 60
    return f'{0 if h < 10 else ""}{h}h{0 if m < 10 else ""}{m}m{0 if s < 10 else ""}{s}s'


def get_bank():
    return get_db()['bank']


def get_user_bank(user_id):
    user = get_bank().find_one({'user_id': user_id})
    if not user:
        return {'balance': 0}
    return user


def get_balance(args, guild_id, author_id):
    other_user = None
    if len(args) == 1:
        other_user = re.match('<@(\d+)>', args[0])
        if other_user:
            other_user = int(other_user.group(1))
    user_id = other_user or author_id

    user_bank = get_user_bank(user_id)

    return format_money(user_bank['balance'])


def get_daily(args, guild_id, author_id):
    user_bank = get_user_bank(author_id)
    if 'last_daily' in user_bank and time() - user_bank['last_daily'] < ONE_DAY:
        return f'Próxima diária disponível em {format_time(ONE_DAY - (time() - user_bank["last_daily"]))}'

    daily = randrange(DAILY_MIN, DAILY_MAX + 1)
    new_balance = user_bank['balance'] + daily

    get_bank().update_one({'user_id': author_id}, {
        '$inc': {'balance': daily},  '$set': {'last_daily': int(time())}}, upsert=True)

    return format_money(daily)


def pix(args, guild_id, author_id):
    if len(args) != 2:
        return 'Sintaxe inválida'

    receiver = re.match('<@(\d+)>', args[0])
    if not receiver:
        return 'Destinatário inválido'

    receiver = int(receiver.group(1))

    amount = float(args[1].replace(',', '.'))
    if amount <= 0:
        return 'Valor deve ser maior que 0'

    sender_bank = get_user_bank(author_id)

    if sender_bank['balance'] >= amount:
        # Decreases sender's balance
        get_bank().update_one({'user_id': author_id}, {
            '$inc': {'balance': -amount}})

        # Increases receiver's balance
        get_bank().update_one({'user_id': receiver}, {
            '$inc': {'balance': amount}}, upsert=True)

        return f'Pix feito! Saldo restante: {format_money(sender_bank["balance"] - amount)}'
    else:
        return 'Saldo insuficiente'


commands = {
    'balance': get_balance,
    'daily': get_daily,
    'pix': pix
}
