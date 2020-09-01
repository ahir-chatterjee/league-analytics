#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 12:56:21 2019

@author: ahir.chatterjee
"""

import discord
from discord.ext import commands
import os
import leaderboard
import json

token = ""
if(os.path.exists("urbot_token.txt")):
    with open("urbot_token.txt",'r') as openFile:
        token = openFile.read()
base = "https://discordapp.com/api"
tQuery = "?token=" + token

client = discord.Client()
bot = commands.Bot(command_prefix='!', description="eepa")

#current solution for keeping id's of everybody
idDict = {"Ahir" : 103645519091355648,
          "Urbot" : 598931795332825108,
          "Bo" : 117344493895811076,
          "Faiz" : 181294520388943872,
          "Shubham" : 504137209926909982,
          "Khayame" : 116037813757149186,
          "Peter" : 103660164585918464,
          "Hwang" : 144319918681227264,
          "Jonathan" : 210502732300288000,
          "Denis" : 277787166388518922,
          "Andy" : 197405594754351105,
          "Austin" : 148388944386588672,
          "Vincent" : 162728387348135936,
          "Bruce" : 267064851636027396,
          "David" : 131673939930775552,
          "Ty" : 191247351162077184,
          "Louis" : 130920011429707776,
          "Gavin" : 229059675444740096,
          "Caleb" : 264566173843193857,
          "Dustin" : 167829909052325899,
          "Michael" : 114560575232671745,
          "Ben" : 324609016175263744,
          "Mason" : 121820913875288064,
          "Clayton" : 164190805924380673,
          "Paul" : 214602165552021505,
          "Isaac" : 118119026747506690,
          "Raymond" : 336683086924218379,
          "Gary" : 166038505544351744,
          "Tailer" : 153021888656834560,
          "Tanner" : 337791672614125578,
          "Vic" : 137716762316636160,
          "Kevin" : 174326208778076162,
          "James" : 192452145868570624,
          "Zane" : 136636558479589378,
          "Nabil" : 299727617379008512
          }

async def checkCommands(message):
    command = message.content[1:].split(" ")
    base = command[0]
    print((str)(message.author.id) + " used " + base)
    #print(message.guild.text_channels)
    guild = message.guild
    channel = message.channel
    msg = ""
    
    #enter switchcase for commands
    if(base == "d4"):
        '''
        Fun little command that reflects the true nature of @CrusherCake#2896.
        '''
        msg = "<@" + (str)(idDict["Ahir"]) + "> is a Hardstuck D4 Urgot Onetrick"
        await channel.send(msg)
        
    elif(base == "leaderboard"):
        '''
        Command that automatically updates the ranked leaderboard.
        Depends on the following files: 
            leaderboard.py - script for running a leaderboard update and other functions
            leaderboard_accounts.txt - all the accounts that will be used for the leaderboard
        '''
        if(await authCheck(message,channel,[idDict["Ahir"]])):
            accounts = {}
            if(os.path.exists("leaderboard_accounts.txt")): #read in the accounts for the leaderboard update
                with open("leaderboard_accounts.txt",'r') as openFile:
                    accounts = json.loads(openFile.read())
            
            accounts = leaderboard.runLeaderboard(accounts)
            
            if(os.path.exists("leaderboard_accounts.txt")): #output the updated leaderboard accounts
                with open("leaderboard_accounts.txt",'w') as openFile:
                    openFile.write(json.dumps(accounts))
                    
            await postLeaderboard(guild)
                
def getNameById(pId):
    for name in idDict:
        if((str)(idDict[name]) == pId):
            return name
            
async def authCheck(message,channel,authorizedUsers):
    if(message.author.id not in authorizedUsers):
        await channel.send("You do not have permission for this command.")
        return False
    return True
            
async def postLeaderboard(guild):
    '''
    Extra formatting for posting the leaderboard.
    To actually post it in a server, you must have a channel with the name "leaderboard" 
    and a message already posted by Urbot in the channel. 
    You can use !d4 to post that message, will be updated to be cleaner in the future.
    Requires currentLeaderboard.txt to already be populated (which is done after using leaderboard.py)
    '''
    msg = ""
    lChannel = "573231206032867357"
    
    for c in guild.text_channels: #find the leaderboard channel
        if(c.name == "leaderboard"):
            lChannel = c
            
    lMessage = "722180880520708237"
    for m in await lChannel.history().flatten(): #find a previous message created by Urbot
        if((str)(m.author.id) == client.user):
            lMessage = m.id
    
    #perform the proper formatting and edit the proper messages in the channel
    lBoard = open("currentLeaderboard.txt",'r')
    msg += "**Updated every Sunday at 9 PM Central Time**\n"
    msg += "```\n"
    msg += "Rank Name       Score       Summoner Name     Changes\n"
    i = 1
    for line in lBoard:
        msg += line
        i += 1
        if(i == 11): 
            msg += "```\n"         
            msg += "```\n"
    msg += "```\n"
    msg += """Want to get your name up here? Do you have another account you want linked to this leaderboard? Message <@103645519091355648> and get it updated."""
    await (await lChannel.fetch_message(lMessage)).edit(content=msg)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        #prevent urbot from replying to itself for any reason
        return
    elif message.content.startswith('!'):
        #a user has requested a command (or so we think)
        await checkCommands(message)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game("League of Legends"),status="online")

client.run(token)
