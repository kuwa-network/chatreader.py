import os
import importlib
from re import T
import re
from ssl import enum_certificates
from discord.ext.commands.core import check
from discord.utils import resolve_template
import pandas as pd
from typing import Counter, Dict
import discord
import datetime
import asyncio

import module
import pandas as pd

from urllib.parse import urlparse
from bs4 import BeautifulSoup

import yaml
import csv
import sys


client = discord.Client()
#設定ファイル読み込み
global config
with open('config.yml', encoding='utf8') as config_file:
    config = yaml.safe_load(config_file)

#データファイル読み込み
#global data
#with open('data.yml', encoding='utf8') as data_file:
#    data = yaml.safe_load(data_file)

url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

loger = module.loger#log生成モジュール短縮化

global voice_channel_list
voice_channel_list = ""

@client.event
async def on_ready():
    #起動告知
    print(config['bot']['ready_message'])
    for channel in client.get_all_channels():
        if channel.name == config['bot']['log_channel']:
            await channel.send(config['bot']['ready_message'])
####################
##BOTステータス設定##
####################
    while True:
        try:
            for num in range(1, 1000):
                if config['status'][num]['status_message'] == '':
                    print(f'ERRO config.yml command欄{num}行目のstatus_messageに空白のみのがあります')
                if config['status'][num]['status_type'] == '':
                    print(f'ERRO config.yml command欄{num}行目のstatus_typeに空白のみのがあります')
                if config['status'][num]['status_url'] == '':
                    print(f'ERRO config.yml command欄{num}行目のstatus_urlに空白のみのがあります')
                else:
                    if config['status'][num]['status_type'] == 'game':
                        await client.change_presence(activity=discord.Game(name=config['status'][num]['status_message']))
                    elif config['status'][num]['status_type'] == 'watching':
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=config['status'][num]['status_message']))
                    elif config['status'][num]['status_type'] == 'listening':
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=config['status'][num]['status_message']))
                    elif config['status'][num]['status_type'] == 'streaming':
                        await client.change_presence(activity=discord.Streaming(name=config['status'][num]['status_message'], url=config['status'][num]['status_url']))
                    await asyncio.sleep(config['status']['time'])
        except KeyError:
            pass

@client.event
async def on_message(message):
    global data
    global config
    global voice_channel_list
    #########
    #BOT退避#
    #########
    if message.author.bot:
        return
    #############
    #停止コマンド#
    #############
    if message.content.startswith("!!cr botstop"):
        if message.author.id == 713218547223887893:
            print(config['bot']['stop_message'])
            for channel in client.get_all_channels():
                if channel.name == config['bot']['log_channel']:
                    await channel.send(config['bot']['stop_message'])
            sys.exit()
    ###############
    #再起動コマンド#
    ###############
    if message.content.startswith("!!cr reload"):
        if message.author.id == 713218547223887893:
            importlib.reload(module)
            await message.delete()
            with open('config.yml', encoding='utf8') as config_file:
                config = yaml.safe_load(config_file)
            print(config['bot']['reload_message'])
            for channel in client.get_all_channels():
                if channel.name == config['bot']['log_channel']:
                    await channel.send(config['bot']['reload_message'])
                    return
        

################
##helpコマンド##
################
    if message.content.startswith("!!cr help"):
        helps = discord.Embed(title=config['help']['title'],color=0x9AFE2E)    
        try:
            for num in range(1, 1000):
                if config['help'][num]['name'] == '':
                    print(f'ERRO config.yml help欄{num}行目に空白のみのがあります')
                else:
                    helps.add_field(name=config['help'][num]['name'],value=config['help'][num]['value'],inline=config['help'][num]['inline'])
        except KeyError:
            await message.channel.send(embed=helps)
            return

    ##読み上げBOT##
    if message.content.startswith("!!cr set"):
        out = loger.message_log(message)
        print(out)
        if message.author.voice is None:
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="ユーザー",value=message.author, inline=True)
            error.add_field(name="コマンド",value=message.content, inline=True)
            error.add_field(name="詳細",value="ボイスチャットに接続していません！", inline=False)
            await message.channel.send(embed=error)
            return
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect()#接続
            voice_channel_list += "\n"+str(message.channel.id)+","+str(message.author.voice.channel.id)+","+message.author.name#読み上げチャンネルリストに追加する
            print(voice_channel_list)
            action = discord.Embed(title="読み上げを開始します！",color=0x00ff7f)
            action.add_field(name="ユーザー",value=message.author, inline=True)
            action.add_field(name="読み上げるチャンネル",value=message.channel, inline=False)
            await message.channel.send(embed=action)
            return
        else:
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="ユーザー",value=message.author, inline=True)
            error.add_field(name="コマンド",value=message.content, inline=True)
            error.add_field(name="詳細",value="既に接続されています", inline=False)
            error.add_field(name="接続していないのに出る場合",value="Discordの性質上の問題です\n時間をおいてもう一度お試しください", inline=False)
            await message.channel.send(embed=error)
            return

    if message.content.startswith("!!"):
        pass
    else:
        try:
            for out in voice_channel_list.split("\n"):
                if str(message.channel.id) in out.split(","):
                    await module.voice_generator.voice_send(client,message,voice_speed=0.8,voice_pitch=-5.0,voice_type="mei_normal",)
        except:
            pass

    if message.content.startswith("!!cr test1"):
        await message.guild.voice_client.disconnect()
        return

    if message.content.startswith("!!cr test2"):
        await message.author.voice.channel.connect()
        return

    if message.content.startswith("!!cr stop"):
        out = loger.message_log(message)
        print(out)
        if message.guild.voice_client is None:
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="ユーザー",value=message.author, inline=True)
            error.add_field(name="コマンド",value=message.content, inline=True)
            error.add_field(name="詳細",value="ボイスチャットに接続していません！", inline=False)
            await message.channel.send(embed=error)
            return
        await message.guild.voice_client.disconnect()#切断

        out_list = ""
        for out in voice_channel_list.split("\n"):#vcリストから消去
            print(out)
            print(out.split(","))
            if str(message.channel.id) in out.split(","):
                continue
            else:
                out_list += "\n"+out
        voice_channel_list = out_list
        print(voice_channel_list)
        action = discord.Embed(title="読み上げを停止しました",color=0xff4500)
        action.add_field(name="ユーザー",value=message.author, inline=True)
        action.add_field(name="停止したチャンネル",value=message.channel, inline=False)
        await message.channel.send(embed=action)
        return

    if message.content.startswith("!!cr r add "):#word_replacement
        txt_lsit = message.content.replace("!!cr r add ","")
        txt_lsit = txt_lsit.split(" ")
        csv_path = 'data/word_replacement/'+str(message.guild.id)+".csv"

        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists('data/word_replacement'):
            os.makedirs('data/word_replacement')
    
        try:
            with open(csv_path, "r",encoding="utf-8") as file:#すでに設定済みかの判断
                txt_csv = csv.reader(file)
                for word_replacement in txt_csv:
                    print(word_replacement)
                    if word_replacement[0] == txt_lsit[0]:
                        if word_replacement[1] == txt_lsit[1]:#設定済み
                            error = discord.Embed(title="エラー",color=0xFF0000)
                            error.add_field(name="ユーザー",value=message.author, inline=True)
                            error.add_field(name="コマンド",value=message.content, inline=True)
                            error.add_field(name="詳細",value="すでに置き換えられています！", inline=False)
                            await message.channel.send(embed=error)
                            return
                        else:
                            error = discord.Embed(title="エラー",color=0xffa500)
                            error.add_field(name="ユーザー",value=message.author, inline=True)
                            error.add_field(name="コマンド",value=message.content, inline=True)
                            error.add_field(name="詳細",value="他の単語に置き換えられています！", inline=False)
                            await message.channel.send(embed=error)
                            return
        except:
            pass

        with open(csv_path, "a",encoding='utf8', newline='') as file:
            file = csv.writer(file)
            file.writerow([txt_lsit[0],txt_lsit[1],message.author])
        action = discord.Embed(title="単語置き換えを設定しました！",color=0x00ff7f)
        action.add_field(name="ユーザー",value=message.author, inline=True)
        action.add_field(name="変更した単語",value=txt_lsit[0], inline=False)
        action.add_field(name="変更後",value=txt_lsit[1], inline=False)
        await message.channel.send(embed=action)
        return

    if message.content.startswith("!!cr r remove "):#word_replacementの解除
        remove_txt = message.content.replace("!!cr r remove ","")
        path = 'data/word_replacement/'+str(message.guild.id)+".csv"
        try:  
            with open(path, "r",encoding="utf-8") as file:
                txt_csv = csv.reader(file)
                for word_replacement in txt_csv:
                    if word_replacement[0] == remove_txt:#文字があるかどうか
                        with open(path,"r",encoding='utf8') as file:#消去処理
                            out = ""
                            for i in file:
                                if i.startswith(remove_txt):
                                    continue
                                else:
                                    out += i
                        with open(path,"w",encoding='utf8') as files:#ここまで
                            files.write(out)
                        action = discord.Embed(title="単語置き換えを消去しました！",color=0x00ff7f)
                        action.add_field(name="ユーザー",value=message.author, inline=True)
                        action.add_field(name="消去された置き換え",value=word_replacement[0], inline=False)
                        action.add_field(name="置き換えられていた単語",value=word_replacement[1], inline=False)
                        await message.channel.send(embed=action)
                        return
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="ユーザー",value=message.author, inline=True)
            error.add_field(name="コマンド",value=message.content, inline=True)
            error.add_field(name="詳細",value="単語置き換えリスト内に単語がありません！", inline=False)
            await message.channel.send(embed=error)
            return
        except:
            pass

    if message.content.startswith("!!cr r list"):#word_replacementの変換リスト
        path = 'data/word_replacement/'+str(message.guild.id)+".csv"
        try:#割り当てられてなかったときように
            with open(path, "r",encoding="utf-8") as file:
                txt_csv = csv.reader(file)
                action = discord.Embed(title="単語置き換えリスト",color=0x00ff7f)
                action.add_field(name="ユーザー",value=message.author, inline=False)
                for word_replacement in txt_csv:
                    action.add_field(name="変更したユーザー",value=word_replacement[2], inline=True)
                    action.add_field(name="変更した単語",value=word_replacement[0], inline=True)
                    action.add_field(name="変更後",value=word_replacement[1], inline=True)
            await message.channel.send(embed=action)
            return
        except:
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="ユーザー",value=message.author, inline=True)
            error.add_field(name="コマンド",value=message.content, inline=True)
            error.add_field(name="詳細",value="置き換えリストがありません！", inline=False)
            await message.channel.send(embed=error)
            return

    if message.content.startswith("!! "):#ボイスタイプ
        txt_lsit = message.content.replace("!!cr r add ","")
        txt_lsit = txt_lsit.split(" ")
        csv_path = 'data/voice_setting/'+str(message.guild.id)+".csv"

        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists('data/word_replacement'):
            os.makedirs('data/word_replacement')

    if message.content.startswith('!!cr2'):#crbot避けるよう
        return
    if message.content.startswith('!!cr3'):#crbot2避けるよう
        return

    elif message.content.startswith('!!cr'):
        error = discord.Embed(title="エラー",color=0xFF0000)
        error.add_field(name="コマンド",value="```"+message.content+"```")
        error.add_field(name="詳細",value="コマンドが間違っています！")
        await message.channel.send(embed=error)
        dt_now = datetime.datetime.now()
        time = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        print(f"[{time}]command erra<{message.guild}|{message.channel}|{message.author}>{message.content}")

@client.event
async def on_voice_state_update(member,before,after):
    global voice_channel_list
    if member.bot:#もしBOT入ってきたら
        if member.id == config['bot_id']:#このBOTだったら
            if before.channel is None:#BOTがもともと接続されていたか
                return
            if after.channel is None:
                error_reason = "BOTが強制的に切断されたため読み上げを停止します！"
            else:#botVC移動
                out_list = ""
                for out in voice_channel_list.split("\n"):#vcリストから消去
                    if str(before.channel.id) in out.split(","):#もし強制切断されたVCのIDがリストにあったら
                        channel = member.guild.get_channel(int(out.split(",")[0]))#抜けましたaction用のチャンネル取得
                        out_list += "\n"+out.replace(out.split(",")[1],str(after.channel.id))
                    else:
                        out_list += "\n"+out
                voice_channel_list = out_list
                action = discord.Embed(title="VCを移動しました！",color=0x00ff7f)
                action.add_field(name="読み上げていたチャンネル",value=before.channel, inline=False)
                action.add_field(name="移動先のチャンネル",value=after.channel, inline=False)
                await channel.send(embed=action)
                return print(voice_channel_list)
                # error_reason = "BOTが強制的に移動されたため読み上げを停止します！"                
                # await asyncio.sleep(0.2)#たまに落とされないことあるから
                # await member.guild.voice_client.disconnect()#切断

            out_list = ""
            channel = None#初期値用
            for out in voice_channel_list.split("\n"):#vcリストから消去
                if str(before.channel.id) in out.split(","):#もし強制切断されたVCのIDがリストにあったら
                    channel = member.guild.get_channel(int(out.split(",")[0]))#抜けましたaction用のチャンネル取得
                    continue
                else:
                    out_list += "\n"+out
            voice_channel_list = out_list
            if channel is None:
                return
            error = discord.Embed(title="エラー",color=0xFF0000)
            error.add_field(name="詳細",value=error_reason, inline=False)
            await channel.send(embed=error)
            print(voice_channel_list)
            return
        else:#BOTが出入りした時に反応しないように
            return

    check = 0#ユーザーいるか判定する用
    check2 = 0#ボイスチャンネルにBOTだけいる状態の判別用
    channel = None#初期値用

    if before.channel is None:
        return
    if before.channel.members == []:#BOTも何もいないときに落ちた時何もしない
        return
    for user in before.channel.members:
        if user is None:
            return
        if not user.bot:#もしBOT以外の人がいたら
            check = 1


    if check == 0:#BOT以外いなかったら
        if member is None:
            return
        await member.guild.voice_client.disconnect()#切断

        for user in before.channel.members:
            if user.bot:#もしBOTが残ってるのなら
                print(user.name)
                check2 += 1

        out_list = ""
        for out in voice_channel_list.split("\n"):#vcリストから消去
            if str(before.channel.id) in out.split(","):#もし抜けた人の接続していたVCのIDがリストにあったら
                channel = member.guild.get_channel(int(out.split(",")[0]))#抜けましたaction用のチャンネル取得
                continue
            else:
                out_list += "\n"+out
        voice_channel_list = out_list
        
        print(voice_channel_list)
        if channel is None:
            return
        action = discord.Embed(title="読み上げを停止しました",color=0xff4500)
        if check2 > 1:
            action.add_field(name="|)彡",value="ボイスチャンネルにBOT以外誰もいなくなりました！", inline=True)
        else:
            action.add_field(name="シーン...",value="ボイスチャンネルに誰もいなくなりました！", inline=True)
        action.add_field(name="停止したチャンネル",value=before.channel, inline=False)
        await channel.send(embed=action)
        return

client.run(config['token'])