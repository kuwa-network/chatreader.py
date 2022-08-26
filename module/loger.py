import discord
import datetime

client = discord.Client()

def discord_log(guild, channel, name, message):
    dt_now = datetime.datetime.now()
    time = dt_now.strftime('%Y/%m/%d %H:%M:%S')
    log = f"[{time}]<{guild}|{channel}|{name}>{message}"
    return log

def message_log(message):
    dt_now = datetime.datetime.now()
    time = dt_now.strftime('%Y/%m/%d %H:%M:%S')
    log = f"[{time}]<{message.channel.guild}|{message.channel.name}|{message.author}>{message.content}"
    return log