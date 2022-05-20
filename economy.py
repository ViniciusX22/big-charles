import re
from db import get_db
from os import getenv
from random import randrange
from decimal import Decimal
from time import time
import discord

DAILY_MIN = float(getenv('DAILY_MIN', 50))
DAILY_MAX = float(getenv('DAILY_MAX', 100))
CURRENCY = getenv('CURRENCY', '$')

ONE_DAY = 86400


def format_money(money):
    money = int(money) if int(money) == money else round(money, 2)
    return '{} {:n}'.format(CURRENCY, Decimal(str(money)))


def format_time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds % 60
    return f'{0 if h < 10 else ""}{h}h{0 if m < 10 else ""}{m}m{0 if s < 10 else ""}{s}s'


def error_embed(msg, color=discord.Colour.red()):
    return {'embed': discord.Embed(title=msg, color=color)}


def get_bank():
    return get_db()['bank']


def get_user_bank(user_id):
    user = get_bank().find_one({'user_id': user_id})
    if not user:
        return {'balance': 0}
    return user


def get_balance(args, guild, author):
    other_user = None
    if len(args) == 1:
        other_user = re.match('<@(\d+)>', args[0])
        if other_user:
            other_user = int(other_user.group(1))
            other_user = guild.get_member(other_user)
    user = other_user or author

    user_bank = get_user_bank(user.id)

    formatted_balance = format_money(user_bank['balance'])

    embed = discord.Embed(
        title=f'Saldo: {formatted_balance}', color=discord.Colour.blue())
    embed.set_footer(icon_url=user.avatar_url, text=user.name)

    return {'embed': embed}


def get_daily(args, guild, author):
    user_bank = get_user_bank(author.id)
    if 'last_daily' in user_bank and time() - user_bank['last_daily'] < ONE_DAY:
        return error_embed(f'Próximo bônus disponível em {format_time(ONE_DAY - (time() - user_bank["last_daily"]))}', color=discord.Colour.blurple())

    daily = randrange(DAILY_MIN, DAILY_MAX + 1)
    new_balance = user_bank['balance'] + daily

    get_bank().update_one({'user_id': author.id}, {
        '$inc': {'balance': daily},  '$set': {'last_daily': int(time())}}, upsert=True)

    formatted_daily = format_money(daily)
    formatted_balance = format_money(new_balance)

    embed = discord.Embed(
        title=f'Bônus diário: {formatted_daily}', description=f'Saldo: {formatted_balance}', color=discord.Colour.green())
    embed.set_footer(icon_url=author.avatar_url, text=author.name)

    return {'embed': embed}


def pix(args, guild, author):
    if len(args) != 2:
        return error_embed('Sintaxe inválida')

    receiver = re.match('<@(\d+)>', args[0])
    if not receiver:
        return error_embed('Destinatário inválido')

    receiver = guild.get_member(int(receiver.group(1)))
    if not receiver:
        return error_embed('Destinatário inválido')

    amount = None
    try:
        amount = float(args[1].replace(',', '.'))
        if amount <= 0:
            return error_embed('Valor deve ser maior que 0')
    except ValueError:
        return error_embed('Sintaxe inválida')

    sender_bank = get_user_bank(author.id)

    if sender_bank['balance'] >= amount:
        # Decreases sender's balance
        get_bank().update_one({'user_id': author.id}, {
            '$inc': {'balance': -amount}})

        # Increases receiver's balance
        get_bank().update_one({'user_id': receiver.id}, {
            '$inc': {'balance': amount}}, upsert=True)

        embed = discord.Embed(
            title=f'Pix de {format_money(amount)} feito para {receiver.name}!', description=f'Saldo: {format_money(sender_bank["balance"] - amount)}', color=discord.Colour.teal())
        embed.set_thumbnail(url=receiver.avatar_url)
        embed.set_footer(icon_url=author.avatar_url, text=author.name)

        return {'embed': embed}
    else:
        return error_embed('Saldo insuficiente')


commands = {
    'balance': get_balance,
    'daily': get_daily,
    'pix': pix
}
