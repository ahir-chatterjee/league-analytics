# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 15:52:02 2018

@author: ahirc
"""
import riotapicalls
import dbcalls

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
    
def calcGameTime(time):
    mins = (str)(round(time/60000))
    secs = (str)(round((time%60000)/1000))
    if(len(secs) == 1):
        secs = "0" + secs
    return (str)((mins + ":" + secs))

def assistString(assistList, identities):
    if(len(assistList) == 0):
        return " solo"
    elif(len(assistList) == 1):
        return " with " + (identities[assistList[0]])
    elif(len(assistList) == 2):
        return " with " + (identities[assistList[0]]) + " and " + (identities[assistList[1]])
    else:
        returnStr = " with " + (identities[assistList[0]])
        for num in range(1,len(assistList)):
            if(num == len(assistList)-1):
                returnStr = returnStr + ", and " + identities[assistList[num]]
            else:
                returnStr = returnStr + ", " + identities[assistList[num]]
        return returnStr
    
def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    return -1

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
                        
#                if(not hasHL):
#                    #if no high limit was found (item is spread out), try lower limits
#                    for num in range(0,6):
#                        i = itemsMatrix[item][num]
#                        si = sitemsMatrix[item][num]
#                        if((i < highLimit and i >= lowLimit) or (si < highLimit and si >= lowLimit)):
#                            #if between high and low limit
#                            if(not((i < highLimit and i >= lowLimit) and (si < highLimit and si >= lowLimit))):
#                                #if the other element is not also between hugh and low limit
#                                if(not item in itemsDifferent):
#                                    #add it to itemsDifferent if it already hasn't been added
#                                    itemsDifferent.append(item)
#                                    if(item in matchingItems):
#                                        #if the item was already present in matching items, remove it
#                                        matchingItems.remove(item)
#                            elif(not item in matchingItems and (not item in itemsDifferent)):
#                                #otherwise put it into matchingItems
#                                matchingItems.append(item)
    

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

smurfDetection = checkAccounts("Celsius heat",["lickitloveit","melllo","noodlz","keep it mello","horny and giad","lpoklpok","poopsers"])

#    matchNumber = 100
#    itemNumber = 2
#    relatedChance = 1
#    if len(itemsChecked) == 0:
#        itemsChecked.append("none")
#    itemRatio = 1/len(itemsChecked)
#    if(not flashSame):
#        relatedChance = 0.0
#    if(len(itemsBadlyDifferent) > 0 or len(reallyBad) > 0):
#        relatedChance = 0.0
#    if(relatedChance > 0):
#        for item in itemsDifferent:
#            relatedChance -= itemRatio
##            for item in itemsBadlyDifferent:
##                relatedChance -= itemRatio*3.5
#    if(relatedChance < 0):
#        relatedChance = 0.0
#    if(matchesChecked < matchNumber):
#        relatedChance /= 2
#        print("WARNING: low sample size of matches on " + summonerName + ".")
#    if(smatchesChecked < matchNumber):
#        relatedChance /= 2
#        print("WARNING: low sample size of matches on " + smurf + ".")
#    if(not len(itemsChecked) > itemNumber):
#        relatedChance /= 2
#        print("WARNING: low sample size of items in common.")
#    print((str)(round(relatedChance*100,1)) + "% chance that " + summonerName + " and " + smurf + " are the same.")
#    
#    for num in range(0,len(inventories)):
#        searchItem = "Stopwatch"
#        found = False
#        for item in inventories[num]:
#            if(item == searchItem):
#                found = True
#        if not found:
#            inventories[num] = []
    
    
#def analyzeDownloadedGames():
#    d = datetime.utcnow()
#    unixtime = calendar.timegm(d.utctimetuple())
#    daysConstant = 1000*(60)*(60)*(24) #seconds to minutes, minutes to hours, hours to days
#    season = (int)(input("Enter season to track: " ))
#    trackChamp = ""#input("Enter champ name: ")
#    numDays = (int)(input("Enter number of days to check: "))
#    startPatch = 10000#input("Enter startPatch: ")
#    endPatch = -1#input("Enter endPatch to track: ")
#    lane = input("Enter lane to check: ").upper()
#    loadedInfo = loadFile(summonerName + "S" + (str)(season) + "games.txt")    
#    if(loadedInfo[0] != season+3):
#        print("Games for " + summonerName + " not previously downloaded for season " + (str)(season) + ".")
#        return
#    matchesList = loadedInfo[1]
#    champFreq = {}
#    champRoles = {}
#    for key in champDict:
#        champFreq[champDict[key]] = 0
#    count = 0
#    for match in matchesList:
#        count += 1
#        curVersion = (int)(match["gameVersion"].split('.')[1])
#        #print((((unixtime*1000)-(int)(match["gameCreation"]))/daysConstant))
#        if((((unixtime*1000)-(int)(match["gameCreation"]))/daysConstant) > numDays):
#            print((str)(count) + " total games in the past " + (str)(numDays) + " days.")
#            break
#        if(not(curVersion > (int)(startPatch))):
#            if(not(curVersion >= (int)(endPatch))):
#                #print(match["gameVersion"].split('.'))
#                #print(patch)
#                break
#            pId = 0
#            for p in match["participantIdentities"]:
#                if(p["player"]["summonerId"] == summonerID):
#                    pId = p["participantId"]
#            for p in match["participants"]:
#                if(p["participantId"] == pId and champDict[(str)(p["championId"])] == trackChamp):
#                    if(p["timeline"]["lane"] not in champRoles):
#                        champRoles[p["timeline"]["lane"]] = {p["timeline"]["role"]:1}
#                    elif(p["timeline"]["role"] in champRoles[p["timeline"]["lane"]]):
#                        champRoles[p["timeline"]["lane"]][p["timeline"]["role"]] += 1
#                    else:
#                        champRoles[p["timeline"]["lane"]][p["timeline"]["role"]] = 1
#                if(p["participantId"] == pId and p["timeline"]["lane"] == lane):
#                    champ = champDict[(str)(p["championId"])]
#                    champFreq[champ] += 1          
#    for champ in sorted(champFreq, key=champFreq.get, reverse=True):
#        if(champFreq[champ] > 0):
#            print(champ)
#    for champ in sorted(champFreq, key=champFreq.get, reverse=True):
#        if(champFreq[champ] > 0):
#            print(champFreq[champ])
#    #print(champRoles)
#    return matchesList
#         
##matchesList = analyzeDownloadedGames()
##itemsMatrix = findFingerprint(summonerID)
#    
##for match in matches["matches"]:
##    if(count > limit):
##        break
##    matchID = (str)(match["gameId"])
##    matchRequest = json.loads(requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + matchID + api_key).text)
##    #matchTimeline = json.loads(requests.get("https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/" + matchID + api_key).text)
##    #printTeams(matchRequest)
##    #printTimeline(matchRequest, matchTimeline)
##    print(count)
##    count += 1

