# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:17:25 2020

@author: Ahir
"""

import dbcalls
import riotapicalls
import opggcalls
import time
from roleml import roleml

"""
Parameters: 
    match - a match object from the Riot API
    summId - a unique summonerId
Returns:
    The summId's participantId within the given match
"""
def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    return -1

"""
Parameters:
    match - a match object from the Riot API
    timeline - a timeline object from the Riot API
Returns:
    A dictionary of players and their roles (top,mid,etc.) in the game. 
    The keys of the dictionary are the player's summonerId.
    See roleml library for more details.
"""
def getMatchRoles(match,timeline):
    prediction = roleml.predict(match,timeline)
    roles = {}
    for p in match["participantIdentities"]:
        roles[p["player"]["summonerId"]] = prediction[p["participantId"]]
    return roles

"""
Parameters:
    multi - a multi op.gg link in the format "https://na.op.gg/multi/query="
Returns:
    Nothing.
    Downloads all of the ranked games for each of the accounts in the multi.
"""
def downloadRankedGamesFromMulti(multi):
    accounts = getAccountsFromMulti(multi)
    for account in accounts:
        print("Downloading from " + account["name"] + "...")
        matches = riotapicalls.getAllRankedMatchesByAccount(account)
        print((str)(len(matches)) + " matches downloaded for " + account["name"])
        
"""
Parameters:
    multi - a multi op.gg link in the format "https://na.op.gg/multi/query="
Returns:
    A list of the Riot API accounts corresponding to the names listed in the multi.
"""
def getAccountsFromMulti(multi):
    names = opggcalls.getNamesFromMulti(multi)
    accounts = riotapicalls.getAccountsByNames(names)
    return accounts

"""
Overview:
    createScoutingReport is a method that takes in a teamName and multi.gg link and returns a report.
    The report contains the champions that they play in ranked.
    These champions are sorted, using both recency of games as well as number of games on a champion during the season.
Parameters:
    teamName - name of the team, just a simple string, can be anything
    opgg - a multi op.gg link in the format "https://na.op.gg/multi/query="
Returns:
    report - a scouting report with weighted champ pools of each player, as well as item and rune information
The following methods are all part of createScoutingReport:
    createReport, getReportMatchData, addReportInfo, sortChampPool, createChampPools
"""
def createScoutingReport(teamName,opgg):
    #should add lane information, using that roleml library. would require timelines to also be downloaded
    print("Creating scouting report for " + teamName + "...")
    names = opggcalls.getNamesFromMulti(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    dbcalls.addTeamToDB(teamName,accounts)
    report = createReport(accounts)
    print("Scouting report created for " + teamName)
    return report
"""
Parameters:
    accounts - a list of Riot API accounts of the given team
Returns:
    report - a scouting report with weighted champ pools of each player, as well as item and rune information
"""
def createReport(accounts):
    report = {"players":{}}
    for account in accounts:
        if(account):    #if the account is a valid account (accounts for summoner name changes)
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
            print("Invalid account given.")    #summoner name must have changed, check op.gg
    report["players"] = createChampPools(report["players"])
        
    return report

"""
Parameters:
    matches - all of the ranked matches of a given player
    accounts - the account of a given player (same playe as the matches)
Returns:
    analysis - champ pool, item, and rune information of the player
"""
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

"""
Parameters: 
    d - a passed in dictionary. Either "aggregate" or "recent" that are used to return analysis on a player.
    pData - data from a match of a given player (includes champ played, runes, items, etc.)
Returns:
    Nothing.
    Edits d such that it contains all the information it needs (champ played, runes, items, etc.).
    Each method call to this will add one game's worth of data to d.
"""
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
    runeSet["secondaryTree"] = dbcalls.translateRune(stats["perkSubStyle"]) if "perkSubStyle" in stats else ""
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
    
"""
Parameters:
    champPool - a champPool created by createChampPools
    recent - the champions rececntly played by a given player
    aggregate - the champions played for the entire season by a given player
Returns:
    champPool but sorted using the weighted algorithm contained within the method
"""
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

"""
Parameters:
    players - a dictionary of all of the players on a team
Returns:
    players, but updated so that they all have sorted champPools. 
    A champ is considered within a player's champ pool if they have either a minimum number of games on them
    OR if they played the champion recently.
"""
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
Overview:
    findRelatedAccounts is a method that determines suspicious accounts that might be a player's smurf. 
    In short, it uses common duo partners to determine if an account is connected to another one.
Parameters:
    multi - a multi op.gg link in the format "https://na.op.gg/multi/query="
Returns:
    relatedAccounts - a dictionary of all of the passed in accounts and the accounts that may be related to them
The following methods are all part of createScoutingReport:
    determineSusAccounts, syncDuos, findDuos
"""
def findRelatedAccounts(multi):
    #step 1
    accounts = getAccountsFromMulti(multi)
    relatedAccounts = {}
    print("Done with step 1.")
    #step 2
    for account in accounts:
        name = account["name"]
        print(name)
        accInfo = {"sus":{},"mostSus":{}}
        matches = riotapicalls.getAllRankedMatchesByAccount(account)
        accInfo["duos"] = findDuos(matches,account)
        relatedAccounts[name] = accInfo
    print("Almost done with step 2.")
    relatedAccounts["duos"] = syncDuos(relatedAccounts) #puts all unique duo partners into relatedAccounts["duos"]
    print("Done with step 2.")
    #step 3
    for duo in relatedAccounts["duos"]:
        if relatedAccounts["duos"][duo]["partners"] > 2 or relatedAccounts["duos"][duo]["games"] > 20:
            account = riotapicalls.getAccountByName(duo)
            if "name" not in account:
                print("error with: " + duo)
            name = account["name"]
            print(name)
            matches = riotapicalls.getAllRankedMatchesByAccount(account)
            #step 4
            relatedAccounts["duos"][name]["duos"] = findDuos(matches,account) #need to decode these duos as well
    print("Almost done with step 4.")
    relatedAccounts["duos"]["duos"] = syncDuos(relatedAccounts["duos"])
    print("Done with step 4.")
    #step 5
    determineSusAccounts(relatedAccounts) #fills in for each original player the "sus" and "mostSus" dicts

    return relatedAccounts

"""
Parameters:
    relatedAccounts - a dictionary containing account names, 
                        and for each one has accounts that are two degrees away from them with the number of duo games.
Returns:
    Nothing.
    Modifies the relatedAccounts such that there are "sus" and "mostSus" accounts for each player.
"""
def determineSusAccounts(relatedAccounts):
    for player in relatedAccounts:
        if not player == "duos":
            partners = relatedAccounts[player]["duos"]
            for partner in partners:
                if "duos" in relatedAccounts["duos"][partner] and partner not in relatedAccounts: #if we have this duo partners games downloaded (essentially)
                    for duo in relatedAccounts["duos"][partner]["duos"]:
                        if duo not in relatedAccounts[player]["sus"]:
                            relatedAccounts[player]["sus"][duo] = [partner]
                        else:
                            relatedAccounts[player]["sus"][duo].append(partner)
                            relatedAccounts[player]["mostSus"][duo] = relatedAccounts[player]["sus"][duo]

"""
Parameters:
    relatedAccounts - a dictionary containing accounts names, and for each one has account summonerId's two degrees away
Returns:
    duos - a dictionary of all the unique duo partners of this account
    Also modifies all of the duos to use a summoner name rather than summonerId's, since this needs to be human readable
"""
def syncDuos(relatedAccounts):
    duos = {}
    for name in relatedAccounts:
        if "duos" in relatedAccounts[name]:
            changeDict = {}
            partners = relatedAccounts[name]["duos"]
            for summId in partners:
                account = riotapicalls.getAccountBySummId(summId)
                dName = account["name"]
                changeDict[dName] = summId
                duoStats = partners[summId]
                if dName not in duos:
                    duoInfo = {"games":duoStats["games"],"partners":1}
                    duoInfo[name] = duoStats
                    duos[dName] = duoInfo
                else:
                    duos[dName]["games"] += duoStats["games"]
                    duos[dName][name] = duoStats
                    duos[dName]["partners"] += 1
                        
            for name in changeDict:
                summId = changeDict[name]
                partners[name] = partners[summId]
                del partners[summId]
    return duos

"""
Parameters:
    matches - all of the ranked matches of an account from the Riot API
    account - a Riot API account of a player (same player as the matches)
Returns:
    duos - a dictionary of all of the summonerId's of a duo, containing:
            number of matches and streaks (sessions with 2 or more games in a row)
"""
def findDuos(matches,account):
    summId = account["id"]
    duos = {} #once someone is confirmed as a duo, they are marked in here
    streaks = {} #used for keeping track of duo streaks/sessions
    minGames = 2
    
    for match in matches:
        if "status" not in match:
            pId = findParticipantId(match,summId)
            team = pId//6 #will either be a 0 or a 1
            startIndex = team*5 #will either be a 0 or 5
            for i in range(startIndex,startIndex+5): #loops through the 5 players on the person's team
                if(not i == pId-1):
                    tId = match["participantIdentities"][i]["player"]["summonerId"]
                        
                    #handle duo streaks/sessions
                    if(tId in streaks):
                        streaks[tId]["games"] += 1
                    else:
                        streaks[tId] = {"games":1}
                    streaks[tId]["active"] = 1
                        
            #clean duo streaks/sessions
            inactive = []
            for duo in streaks:
                if(streaks[duo]["active"] == 0):
                    inactive.append(duo) #if a duo is inactive, we will remove it below
                else:
                    streaks[duo]["active"] = 0 #mark the remaining duos as inactive
            for duo in inactive:
                games = streaks[duo]["games"]
                if(games > minGames): #if a duo partner is now inactive but had more than min games in a row, mark that
                    if duo not in duos:
                        duos[duo] = {"games":games,"sessions":[games]} #keep track of the total games played and each session length
                    else:
                        duos[duo]["games"] += games
                        duos[duo]["sessions"].append(games)
                streaks.pop(duo)
                
    return duos
        
"""
accountFingerprint() is a method that creates a "unique" fingerprint based off of different factors from an account.
This suite of methods is fairly experimental, so there are currently limited comments. Use at your own risk.
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
    matches = riotapicalls.getAllRankedMatchesByAccount(account)
    
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