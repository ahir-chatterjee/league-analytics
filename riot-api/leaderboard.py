# -*- coding: utf-8 -*-
"""
Created on Sat May 18 16:17:16 2019

@author: Ahir
"""

import requests
import json
import os
import riotapicalls

tiers = ["IRON","BRONZE","SILVER","GOLD","PLATINUM","DIAMOND","MASTER","GRANDMASTER","CHALLENGER"]
ranks = ["IV","III","II","I"]

def getScore(rankInfo):
    score = 0
    score += rankInfo["leaguePoints"] + 1000*(tiers.index(rankInfo["tier"])) + 100*(ranks.index(rankInfo["rank"]))
    return score

def rankName(rankInfo):
    tier = rankInfo["tier"][0]
    rank = (str)(4-(int)(ranks.index(rankInfo["rank"])))
    LP = (str)(rankInfo["leaguePoints"]) + " LP"
    if(rankInfo["tier"] == tiers[6] or rankInfo["tier"] == tiers[8]):
        rank = ""
    elif(rankInfo["tier"] == tiers[7]):
        tier = "GM"
        rank = ""
    return (str)(tier + rank + " " + LP)

def writeLeaderboard(leaderboard):
    cur = open("currentLeaderboard.txt","w")
    prev = open("prevLeaderboard.txt","r")
    prevDict = {}
    numDict = {"1":"one",
               "2":"two",
               "3":"three",
               "4":"four",
               "5":"five",
               "6":"six",
               "7":"seven",
               "8":"eight",
               "9":"nine",
               "10":"ten",
               "10+":"over ten"
               }
    for line in prev:
        fields = line.split("-")
        iden = fields[0].split(")")
        iden[1] = iden[1].strip()
        prevDict[iden[1]] = (int)(iden[0])
        #print(iden)
        
    rank = 1
    for person in leaderboard:
        output = ""
        output += (str)(rank) + ")"
        while(len(output)<5):
            output += " "
        output += person[0]
        while(len(output)<14):
            output += " "
        output += "- "
        ladder = person[1].split(" ")
        output += ladder[0] + " "
        if(ladder[0] == "M" or ladder[0] == "C"):
            output += " "
        spaces = 3-len(ladder[1])
        while(spaces>0):
            output += " "
            spaces -= 1
        output += ladder[1]
        output += " LP - "
        spaces = 16-len(person[2])
        output += person[2]
        while(spaces>0):
            output += " "
            spaces -= 1
        output += "- "
        if(person[0] in prevDict):
            change = prevDict[person[0]] - rank
            move = "up"
            if(change < 0):
                move = "down"
                change = change*-1
            if(change > 10):
                output += move + " by " + numDict["10+"]
            if(change > 0):
                output += move + " by " + numDict[(str)(change)]
        else:
            output += "new entry"
        print(output)
        cur.write(output + "\n")
        rank += 1
        
    cur.close()
    prev.close()    
    
def runLeaderboard(accounts):
    leaderboard = []
    #update all the identities (change summoner names to summonerId's)
    for name in accounts:        
        newIdentities = []
        for identity in accounts[name]: 
            if(len(identity) < 45):
                account = riotapicalls.getAccountByName(identity)
                if("id" in account):
                    newIdentities.append(account["id"])
                else:
                    print(identity + " no longer valid.")
            else:
                newIdentities.append(identity)
        accounts[name] = newIdentities
        
    #now that identities are updated to only have valid summonerId's, let's ranked them on the leaderboard
    for name in accounts:
        highAcc = ""
        highRank = ""
        highScore = -1
        for summId in accounts[name]:
            rankInfo = riotapicalls.getLeagueBySummonerId(summId)
            soloQueue = {}
            for queue in rankInfo:
                if(queue["queueType"] == "RANKED_SOLO_5x5"):
                    soloQueue = queue
            score = -1
            if(soloQueue):
                score = getScore(soloQueue)
            
            if(score > highScore):
                highAcc = riotapicalls.getAccountBySummId(summId)["name"]
                highScore = score
                highRank = rankName(soloQueue)
        leaderboard.append([name,highRank,highAcc,highScore])
    
    leaderboard.sort(key=lambda x:x[3])
    leaderboard.reverse() #sorts the leaderboard in order of the highScore
    
    writeLeaderboard(leaderboard)
                
    return accounts

def main(): 
    accounts = {}
    if(os.path.exists("leaderboard_accounts.txt")):
        with open("leaderboard_accounts.txt",'r') as openFile:
            accounts = json.loads(openFile.read())
    print("running leaderboard")
    accounts = runLeaderboard(accounts)
    print("leaderboard ran")
    if(os.path.exists("leaderboard_accounts.txt")):
        with open("leaderboard_accounts.txt",'w') as openFile:
            openFile.write(json.dumps(accounts))
    
if __name__ == '__main__':
    main()