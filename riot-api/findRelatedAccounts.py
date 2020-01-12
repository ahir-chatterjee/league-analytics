# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:04:34 2020

@author: Ahir
"""

import dbcalls
import riotapicalls
import time
import opggcalls

def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    print(summId,match["participantIdentities"][8]["player"]["summonerId"])
    return -1

def scrapeMatches(matches,summId):
    playedWith = {}
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "didn't find pId for some reason | " + (str)(match["gameId"]) + " | " + (str)(len(playedWith))
        start = (pId//6)*5   #either 0 or 1 after divison, then 0 or 5
        assert start == 0 or start == 5, "dun goofed " + (str)(start) + " | " + (str)(pId)
        for i in range(start,start+5):  #loop through the 5 players on their team
            if(not i == pId-1): 
                player = match["participantIdentities"][i]["player"]
                name = player["summonerName"]
                pSummId = player["summonerId"]
                #riotapicalls.getAccountBySummId(pSummId)
                if(name in playedWith):
                    playedWith[name] += 1
                else:
                    playedWith[name] = 1
                    
                if(pSummId in playedWith):
                    playedWith[pSummId] += 1
                else:
                    playedWith[pSummId] = 1
                
    return playedWith

def weightFunction(kv):
    value = kv[1]
    weightPerPerson = 30 #stupid high value to ensure more people duo'd with == higher weight
    weight = (len(value)-1)*weightPerPerson
    for key in value:
        weight += value[key]
    return weight

def prunePlayedWith(playedWith):
    popList = []
    minNumGames = 5 #random amount, but min number of games required to be relevant
    for name in playedWith:
        if(playedWith[name] < minNumGames):
            popList.append(name)
    for name in popList:
        playedWith.pop(name)

def findRelatedAccounts(accounts):
    similarAccounts = {}
    for account in accounts:
        name = account["name"]
        print(name)
        matches = dbcalls.fetchMatchesByAccount(account)
        #matches = riotapicalls.getAllRankedMatchesByAccount(account)
        playedWith = scrapeMatches(matches,account["id"])
        #playedWith = sorted(playedWith.items(), key=lambda kv: kv[1], reverse=True)
        prunePlayedWith(playedWith)
        
        for n in playedWith:
            playedWithAcc = playedWith[n]
            if(len(n) > 18):
                account = dbcalls.fetchAccountBySummId(n)
                if(account):
                    n = account["name"]
                if(n not in similarAccounts):
                    similarAccounts[n] = {}
                similarAccounts[n][name] = playedWithAcc
            
    similarAccounts = sorted(similarAccounts.items(), key=lambda kv: weightFunction(kv), reverse=True)
    return similarAccounts