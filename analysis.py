# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:17:25 2020

@author: Ahir
"""

import dbcalls
import riotapicalls
import opggcalls
import time
import roleml
#from roleml import roleml

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
    recent["roles"] = {"top" : 0, "jungle": 0, "mid" : 0, "bot" : 0, "supp" : 0};
    aggregate = {"lanes":{}}
    aggregate["roles"] = {"top" : 0, "jungle": 0, "mid" : 0, "bot" : 0, "supp" : 0};
    summId = account["id"]
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "player was not in their own game: " + (str)(match["gameId"]) + " | " + (str)(account["name"])
        pData = match["participants"][pId-1]
        role = riotapicalls.getMatchRoles(match, riotapicalls.getMatchTimeline(match["gameId"]))[summId]
        if(now-match["gameCreation"] < recentInterval):
            addReportInfo(recent,pData,role)
        addReportInfo(aggregate,pData,role)
    analysis = {"recent":recent,"aggregate":aggregate}
    return analysis

def addReportInfo(d,pData,role): 
    #could be a more efficient method if updated to take in both recent and aggregate at the same time
    d["roles"][role] = d["roles"][role] + 1
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

def findRelatedAccounts(accounts):
    #need to add degrees of relativity, role played, as well as "duo streaks" (it's how I found USC jungler's smurf via opgg)
    susAccs = {"similarAccounts":[]}
    similarAccounts = {}
    for account in accounts:
        name = account["name"]
        matches = dbcalls.fetchMatchesByAccount(account)    #matches are fetched in order of played (oldest to newest)
        #matches = riotapicalls.getAllRankedMatchesByAccount(account)
        playedWith = getPlayedWith(matches,account["id"])
        prunePlayedWith(playedWith)
        susAccs[name] = playedWith
        
        for n in playedWith:
            playedWithAcc = playedWith[n]
            if(n not in similarAccounts):
                similarAccounts[n] = {}
            similarAccounts[n][name] = playedWithAcc
            
    susAccs["similarAccounts"] = list(sorted(similarAccounts.items(), key=lambda kv: weightFunction(kv), reverse=True))
    return susAccs

def getPlayedWith(matches,summId):
    playedWith = {}
    summIds = {}
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "didn't find pId for some reason | " + (str)(match["gameId"]) + " | " + (str)(len(playedWith))
        start = (pId//6)*5   #either 0 or 1 after divison, then 0 or 5
        assert start == 0 or start == 5, "dun goofed " + (str)(start) + " | " + (str)(pId)
        for i in range(start,start+5):  #loop through the 5 players on their team
            if(not i == pId-1): 
                player = match["participantIdentities"][i]["player"]
                pSummId = player["summonerId"]
                if pSummId not in summIds:
                    summIds[pSummId] = 1
                else:
                    summIds[pSummId] += 1
                    
    for sId in summIds:
        acc = riotapicalls.getAccountBySummId(sId)
        name = acc["name"]
        if(name in playedWith):
            playedWith[name] += 1
        else:
            playedWith[name] = 1
        
    return playedWith

def weightFunction(kv):
    value = kv[1]
    weightPerPerson = 30 #high value to ensure more people duo'd with == higher weight
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
        
"""
accountFingerprint() is a method that creates a "unique" fingerprint based off of different factors from an account
"""

global ALL_ITEMS, ACTIVE_ITEMS, ITEM_DICT
ALL_ITEMS = dbcalls.fetchAllItems()
ACTIVE_ITEMS = []
ITEM_DICT = {}
for item in ALL_ITEMS:
    name = ALL_ITEMS[item]["name"]
    if("Active" in ALL_ITEMS[item]["tags"]):
        ACTIVE_ITEMS.append(name)
    ITEM_DICT[ALL_ITEMS[item]["num"]] = name
            
def translateItem(num):
    if(num) == 0:
        return ""
    if(item in ITEM_DICT):
        return ITEM_DICT[num]
    else:
        return (str)(num)

def handleInventory(fingerprint):
    popList = []
    for item in fingerprint["itemMatrix"]:
        if(item in ACTIVE_ITEMS):
            for slot in range(0,7):
                #divide by total times item is bought to create percentages (slot 7 it total num of item)
                fingerprint["itemMatrix"][item][slot] /= fingerprint["itemMatrix"][item][7]
        else:
            popList.append(item)
#    for item in popList:    #gets rid of all the non-active items
#        fingerprint["itemMatrix"].pop(item)
    return fingerprint
    
def getFingerprint(name):
    fingerprint = {"flash":[0,0],
                   "numMatches":0,
                   "itemMatrix":{}
                   }
    
    account = riotapicalls.getAccountByName(name)
    assert "id" in account, "Invalid name given, no account found for: " + name
    summId = account["id"]
    #matches = riotapicalls.getAllRankedMatchesByAccount(account)
    matches = dbcalls.fetchMatchesByAccount(account)
    
    fingerprint["numMatches"] = len(matches)
    for match in matches:
        pId = findParticipantId(match,summId)
        p = match["participants"][pId-1]    #the info for the participant
            
        #check which key flash is typically on
        if(p["spell1Id"] == 4):  #4 is the id for flash
            fingerprint["flash"][0] += 1
        elif(p["spell2Id"] == 4):    #else statement because may not have flash
            fingerprint["flash"][1] += 1
            
        #gather item data for all the items in the inventory
        inventory = []
        for slot in range(0,7):
            itemNum = p["stats"]["item"+(str)(slot)]
            item = dbcalls.translateItem(itemNum) #if invalid item, it is an empty string
            if(not item == "" and item in ACTIVE_ITEMS):
                inventory.append(item)
                if(item not in fingerprint["itemMatrix"]):
                    fingerprint["itemMatrix"][item] = [0,0,0,0,0,0,0,0]
                fingerprint["itemMatrix"][item][slot] += 1
                fingerprint["itemMatrix"][item][7] += 1 #this is the total count of the item
    print("Done with " + name + " matches.")
        
    fingerprint = handleInventory(fingerprint)
    
    return fingerprint

def itemCheck(mainMatrix,smurfMatrix):
    #variables that need to be tuned
    sampleSizeLimit = 10
    alwaysSizeLimit = 15
    alwaysLimit = .9    #must be above highLimit
    highLimit = .6  #minimum of .5
    lowLimit = .15  #must be below highLimit
    
    alwaysSame = []
    alwaysDiff = []
    normalSame = []
    normalDiff = []
    
    #different classifications of active item uses
    
    for item in mainMatrix: #if the item is in smurfMatrix but isn't in mainMatrix, it's irrelevant
        if item in smurfMatrix:
            mainSlots = mainMatrix[item]
            smurfSlots = smurfMatrix[item]
            mainGames = mainSlots[7]
            smurfGames = smurfSlots[7]
            if mainGames >= sampleSizeLimit and smurfGames >= sampleSizeLimit:
                for slot in range(0,6):
                    
                    #check "always" items, which are items that are almost always in the same slot every game
                    if mainGames >= alwaysSizeLimit or smurfGames >= alwaysSizeLimit:
                        if((mainSlots[slot] >= alwaysLimit and smurfSlots[slot] < alwaysLimit) or 
                           (mainSlots[slot] < alwaysLimit and smurfSlots[slot] >= alwaysLimit)):
                            if(item not in alwaysDiff):
                                alwaysDiff.append(item)
                        elif(mainSlots[slot] >= alwaysLimit and smurfSlots[slot] >= alwaysLimit):
                            if(item not in alwaysSame):
                                alwaysSame.append(item)
                                
                #check "normal" items, which are items that are usually in the same slot every game, with a degree of variation
                for slot in range(0,6):
                    if((mainSlots[slot] >= highLimit and smurfSlots[slot] < highLimit) or 
                       (mainSlots[slot] < highLimit and smurfSlots[slot] >= highLimit)):  
                        if(item not in normalDiff):
                            normalDiff.append(item)
                    else:
                        if(item not in normalSame):
                            normalSame.append(item)
    
    items = {"alwaysSame":alwaysSame,
             "alwaysDiff":alwaysDiff,
             "normalSame":normalSame,
             "normalDiff":normalDiff}
    return items    

def smurfCheck(name,smurfs,fingerprints):
    main = fingerprints[name]
    results = {}
    
    for n in smurfs:
        smurf = fingerprints[n]
        results[n] = {}
        results[n]["numMatches"] = smurf["numMatches"]
        
        flashSame = False
        #check that flashes are on the same key
        if((main["flash"][0] > main["flash"][1]) and (smurf["flash"][0] > smurf["flash"][1])):
            flashSame = True
        elif((main["flash"][0] < main["flash"][1]) and (smurf["flash"][0] < smurf["flash"][1])):
            flashSame = True
        results[n]["flash"] = flashSame
        
        #check the items
        results[n]["items"] = itemCheck(main["itemMatrix"],smurf["itemMatrix"])
    
    return [results,fingerprints]
    
def checkAccounts(name,smurfs):
    fingerprints = {}
    
    fingerprints[name] = getFingerprint(name)
    for smurf in smurfs:
        fingerprints[smurf] = getFingerprint(smurf)
    
    return smurfCheck(name,smurfs,fingerprints)