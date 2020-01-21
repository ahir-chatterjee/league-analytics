# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:17:25 2020

@author: Ahir
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:53:34 2020

@author: Ahir
"""

import dbcalls
import riotapicalls
import opggcalls
import time

"""
Given a match and a summonerId, will return the participantId of the player in the match
"""
def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    return -1

"""
createScoutingReport() is a method that takes in a teamName and multi.gg link and returns a report.
The report contains the champions that they play on, in order of using recency of play on the accounts as
increasing the importance of it, as well as all games on a champion during the season.
"""

def createScoutingReport(teamName,opgg):
    #should add lane information, using that roleml library. would require timelines to also be downloaded
    print("Creating scouting report for " + teamName + "...")
    names = opggcalls.getNamesFromOpgg(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    dbcalls.addTeamToDB(teamName,accounts)
    report = createReport(accounts)
    print("Scouting report created for " + teamName)
    return report

def createReport(accounts):
    report = {"players":{}}
    for account in accounts:
        if(account):    #if the account is a valid account
            name = account["name"]
            print("Retrieving all ranked matches from \"" + name + "\"...")
            matches = riotapicalls.getAllRankedMatchesByAccount(account)    #downloads all ranked games, takes longer
            #matches = dbcalls.fetchMatchesByAccount(account)               #only retrieves ranked games currently in db
            print((str)(len(matches)) + " ranked matches retrieved from \"" + name + "\".")
            #for match in matches:
                #timelines.append(riotapicalls.getMatchTimeline(match["gameId"]))
            data = getReportMatchData(matches,account)
            report["players"][name] = data
        else:
            print("Invalid account given.")    
    report["players"] = createChampPools(report["players"])
        
    return report

def getReportMatchData(matches,account):
    msPerWeek = 604800*1000 #milliseconds per week
    recentInterval = msPerWeek*2    #3 weeks
    now = time.time()*1000 #in milliseconds
    recent = {"lanes":{}}
    aggregate = {"lanes":{}}
    summId = account["id"]
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "player was not in their own game: " + (str)(match["gameId"]) + " | " + (str)(account["name"])
        pData = match["participants"][pId-1]
        if(now-match["gameCreation"] < recentInterval):
            addReportInfo(recent,pData)
        addReportInfo(aggregate,pData)
    analysis = {"recent":recent,"aggregate":aggregate}
    return analysis

def addReportInfo(d,pData): 
    #could be a more efficient method if updated to take in both recent and aggregate at the same time
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
        if(not item == "0"): #ensures we don't add empty inventory slots to the items dict, or outdated items
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
    
def sortChampPool(champPool,recent,aggregate):
    #Takes in a given champPool, a players recent plays, and a players aggregate plays, and sorts it
    tuples = []
    minRecentGames = 3  #minimum threshold for reaching the highRecentWeight
    highRecentWeight = 4    #each game will be x5 as important.
    recentWeight = 1    #each game will be x2 as important
    for champ in champPool:
        if(champ == "lanes"):
            tuples.append((champ,-1))
        weight = 0
        if(champ in recent):
            matches = recent[champ]["matches"]
            if(matches >= minRecentGames):
                weight += matches*highRecentWeight #guarantees at least minRecentGames*highRecentWeight of weight
            else:
                weight += matches*recentWeight
        assert champ in aggregate, champ + " was not found in aggregate."
        weight += aggregate[champ]["matches"]
        tuples.append((champ,weight))
    tuples = sorted(tuples, key=lambda tuples: tuples[1], reverse=True)
    champPool = []
    fringe = False
    fringeThreshold = minRecentGames*highRecentWeight #currently 12
    for t in tuples:
        if(not fringe):
            if t[1] < fringeThreshold:
                champPool.append("")
                fringe = True
        champPool.append(t[0])
    return champPool

def createChampPools(players):
    minGameLimit = 8   #min games to have a champ in your champ pool
    for name in players:
        player = players[name]
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
        player["champPool"] = sortChampPool(champPool,recent,aggregate)
    return players

"""
findRelatedAccounts() is a method that determines suspicious accounts that might be a player's smurf. 
It takes in a list of names and will look through all of their games 
"""