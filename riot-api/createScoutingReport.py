# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:53:34 2020

@author: Ahir
"""

import dbcalls
import riotapicalls
import opggcalls
import time

def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    return -1

def addInfo(d,pData):
    champ = dbcalls.translateChamp(pData["championId"])
    stats = pData["stats"]
    win = 1 if stats["win"] else 0
    
    #champion info
    if champ in d:
        d[champ]["matches"] += 1
        d[champ]["wins"] += win
    else:
        d[champ] = {"matches":1,"wins":win,"items":{},"lanes":{},"runes":{},"runeSets":[]}
    
    #items info (per champion)
    for num in range(0,7):
        itemNum = stats["item"+(str)(num)]
        item = dbcalls.translateItem(itemNum)
        if(not item == ""): #ensures we don't add empty inventory slots to the items dict, or outdated items
            items = d[champ]["items"]
            if item in items:
                items[item] += 1
            else:
                items[item] = 1
                
    #lane info (per champion)
    lane = pData["timeline"]["lane"]
    lanes = d[champ]["lanes"]
    overallLanes = d["lanes"]
    if lane in lanes:
        lanes[lane] += 1
    else:
        lanes[lane] = 1
    if lane in overallLanes:
        overallLanes[lane] += 1
    else:
        overallLanes[lane] = 1
        
    #rune info (per champion)
    runeSet = {"keystone":"","primaryTree":"","secondaryTree":"",
               "perk1":"","perk2":"","perk3":"","perk4":"","perk5":""}
    
    runeSet["primaryTree"] = dbcalls.translateRune(stats["perkPrimaryStyle"])
    runeSet["secondaryTree"] = dbcalls.translateRune(stats["perkSubStyle"])
    for num in range(0,6):
        perkNum = "perk"+(str)(num)
        runeNum = stats[perkNum]
        rune = dbcalls.translateRune(runeNum)
        runes = d[champ]["runes"]
        if(perkNum in runeSet): #all perks other than 0 (keystone) are in the runeSet dictionary
            runeSet[perkNum] = rune
        else:
            runeSet["keystone"] = rune
        if(not rune == ""): #ensures we don't add outdated runes that will cause an error
            if rune in runes:
                runes[rune] += 1
            else:
                runes[rune] = 1
    d[champ]["runeSets"].append(runeSet)
    
def getOverallLanes(d):
    overallLanes = {}
    
    for champ in d:
        lanes = d[champ]["lanes"]
        for lane in lanes:
            count = lanes[lane]
            if lane in overallLanes:
                overallLanes[lane] += count
            else:
                overallLanes[lane] = count
    
    return overallLanes

def scrapeMatches(matches,account):
    recent = {"lanes":{}}
    aggregate = {"lanes":{}}
    summId = account["id"]
    now = time.time()*1000 #in milliseconds
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "player was not in their own game: " + (str)(match["gameId"]) + " | " + (str)(account["name"])
        pData = match["participants"][pId-1]
        msPerWeek = 604800*1000 #milliseconds per week
        if(now-match["gameCreation"] < msPerWeek*2):   #if the match was within two weeks ago, it is "recent"
            addInfo(recent,pData)
        addInfo(aggregate,pData)
    analysis = {"recent":recent,"aggregate":aggregate}
    return analysis

def createReport(accounts):
    report = {"players":{},"flexes":{}}
    flexes = report["flexes"]
    for account in accounts:
        if(account):    #if the account is a valid account
            name = account["name"]
            print("Retrieving all ranked matches from \"" + name + "\"...")
            #matches = riotapicalls.getAllRankedMatchesByAccount(account)
            matches = dbcalls.fetchMatchesByAccount(account)
            print((str)(len(matches)) + " ranked matches retrieved from \"" + name + "\".")
            data = scrapeMatches(matches,account)
            report["players"][name] = data
        else:
            print("Invalid account given.")
            
    minGameLimit = 15   #min games to have a champ in your champ pool
    for name in report["players"]:
        player = report["players"][name]
        player["champPool"] = []
        champPool = player["champPool"]
        aggregate = player["aggregate"]
        recent = player["recent"]
        for champ in aggregate:
            if(not champ == "lanes"):   #if the champ is not literally the word "lanes"
                if(aggregate[champ]["matches"] >= minGameLimit):
                    champPool.append(champ)
        for champ in recent:
            if(not champ == "lanes" and champ not in champPool):
                champPool.append(champ)
        champPool.sort()
        for champ in champPool:
            if(champ in flexes):
                if(not name in flexes[champ]):
                    flexes[champ].append(name)
            else:
                flexes[champ] = [name]
        
    notFlexes = []
    for champ in flexes:
        if len(flexes[champ]) < 2:
            notFlexes.append(champ)
    for champ in notFlexes:
        flexes.pop(champ)
        
    return report

def createScoutingReport(teamName,opgg):
    print("Creating scouting report for " + teamName + "...")
    names = opggcalls.getNamesFromOpgg(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    dbcalls.addTeamToDB(teamName,accounts)
    report = createReport(accounts)
    print("Scouting report created for " + teamName)
    return report