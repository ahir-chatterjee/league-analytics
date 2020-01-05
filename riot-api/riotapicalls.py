import requests
import json
import os
import time       
import dbcalls
        
API_KEY = ""
#API_RATE_LIMIT = 120    #a standard API_KEY refreshes every 2 minutes, or 120 seconds

"""
Overall useful functions that don't necessarily relate to the Riot API.
"""

"""
depricated functions. anything that relies on these is out of data, and
should by using 'dbcalls.py' instead.

def saveFile(fileName, data):
    overwrite = False
    if(os.path.exists(fileName)):
        overwrite = True
    elif(fileName.rfind('/') > 0):
        path = fileName[0:fileName.rfind('/')]
        if(not os.path.exists(path)):
            os.makedirs(path)
    with open(fileName,'w') as outfile:
        wrapperList = []
        wrapperList.append(data)
        json.dump(wrapperList,outfile)
    if(overwrite):
        print(fileName + " saved and overwritten successfully.")
    else:
        print(fileName + " saved successfully.")

def loadFile(fileName):
    wrapperList = [] 
    if(os.path.exists(fileName)):
        tempStr = ""
        openFile = open(fileName,'r')
        for line in openFile:
            tempStr += line
        if(tempStr):    #if tempStr is not empty
            wrapperList = json.loads(tempStr)  
        else:
            print(fileName + " is an empty file.")
        openFile.close()
    else:
        print("Could not find a file named " + fileName + ".")
    return wrapperList
"""

def getApiKey():
    """
    Either loads in the API_KEY or just returns the value if already loaded.
    """
    global API_KEY
    if(not API_KEY):    #if the API_KEY is not loaded
        fileName = "apikey.txt"
        if(os.path.exists("apikey.txt")):
            openFile = open(fileName,'r')
            API_KEY = openFile.read()
        else:
            print("apikey.txt does not exist. Make one using your own apikey from https://developer.riotgames.com/")
    return "?api_key=" + API_KEY

def makeApiCall(url):
    """
    Given a url/endpoint, it will make the call, and handle any error messages
    """
    try:    #sometimes we get a handshake error. if this happens, try it again
        request = requests.get(url)
    except:
        print("Exception of request of url, trying again in 5 seconds. Failed url: " + (url))
        time.sleep(5)
        return makeApiCall(url)
    d = json.loads(request.text)
    
    if(type(d) is dict):
        if(not d.get("status") == None):    #if we have a status on our hands
            RATE_LIMIT_EXCEEDED = 429
            FORBIDDEN = 403
            NOT_FOUND = 404
            SERVER_ERROR = 500
            BAD_GATEWAY = 502
            UNAVAILABLE = 503
            GATEWAY_TIMEOUT = 504
            statusCode = d["status"]["status_code"]
            if(statusCode == RATE_LIMIT_EXCEEDED):
                #global API_RATE_LIMIT
                #print("Rate limit exceeded, waiting for " + (str)(API_RATE_LIMIT) + " seconds.")
                #time.sleep(API_RATE_LIMIT)
                time.sleep(5)
                request = requests.get(url)
                d = json.loads(request.text)
            elif(statusCode == FORBIDDEN):
                print("API_KEY is incorrect. Please update your apikey.txt from https://developer.riotgames.com")
            elif(statusCode == NOT_FOUND):
                print("No data was found using the following url: " + url)
            elif(statusCode == UNAVAILABLE):
                print("Service unavailable, trying again in 5 seconds.")
                time.sleep(5)
                return makeApiCall(url)
            elif(statusCode == GATEWAY_TIMEOUT):
                print("Gateway timeout, trying again in 5 seconds.")
                time.sleep(5)
                return makeApiCall(url)
            elif(statusCode == SERVER_ERROR):
                print("Server error, trying again in 5 seconds.")
                time.sleep(5)
                return makeApiCall(url)
            elif(statusCode == BAD_GATEWAY):
                print("Bad gateway, trying again in 5 seconds.")
                time.sleep(5)
                return makeApiCall(url)
            else:
                print("Unknown status code: " + (str)(statusCode))
    
    return d

"""
The actual Riot API calls (or datadragon calls)
"""

def getSeasons():
    d = makeApiCall("http://static.developer.riotgames.com/docs/lol/seasons.json")
    return d
    
def getVersion():
    d = makeApiCall("https://ddragon.leagueoflegends.com/realms/na.json")
    return d["n"]

def updateChamps(version):
    print("Updating champions...")
    d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json" + getApiKey())
    champs = []
    for champ in d["data"]:
        data = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion/" + champ + ".json" + getApiKey())
        champs.append(data["data"][champ])
    dbcalls.updateChamps(champs,version)
    print("champions successfully updated")
    return champs
        
def updateItems(version):
    print("Updating items...")
    d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/item.json" + getApiKey())
    dbcalls.updateItems(d["data"],version)
    print("items successfully updated")
        
def updateSpells(version):  #summoner spells
    print("Updating summoner spells...")
    d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/summoner.json" + getApiKey())
    dbcalls.updateSpells(d["data"],version)
    print("summoner spells successfully updated")

def updateConstants():
    versions = getVersion()
    updatesNeeded = dbcalls.checkForUpdates(versions)   #list with three booleans, [champs,items,summoners]
    if(updatesNeeded[0]):
        updateChamps(versions["champion"])
    if(updatesNeeded[1]):
        updateItems(versions["item"])
    if(updatesNeeded[2]):
        updateSpells(versions["summoner"])
    
"""
Summoner entpoints. Get an account's information by different methods.
"""
    
def getAccountByName(name):
    d = dbcalls.fetchAccountByName(name)
    if(not d):  #if d is empty, make the apiCall
        d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + getApiKey())
        acc = dbcalls.fetchAccountByPuuid(d["puuid"])   #check for a potential name change
        if(acc):  #if acc is not empty, that means the user name changed
            dbcalls.updateAccountName(d["name"],d["puuid"])
            d = dbcalls.fetchAccountByPuuid(d["puuid"])
        else:
            dbcalls.addAccountToDB(d)   #store all the information for this account so we can store its history
    return d

def getAccountByAccId(accId):
    d = dbcalls.fetchAccountByAccId(accId)
    if(not d):  #if d is empty, make the apiCall
        d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-account/" + accId + getApiKey())
        dbcalls.addAccountToDB(d)   #store all the information for this account so we can store it's history
    return d

def getAccountByPuuid(puuid):
    d = dbcalls.fetchAccountByPuuid(puuid)
    if(not d):  #if d is empty, make the apiCall
        d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/" + puuid + getApiKey())
        dbcalls.addAccountToDB(d)   #store all the information for this account so we can store it's history
    return d

def getAccountBySummId(summId):
    d = dbcalls.fetchAccountBySummId(summId)
    if(not d):  #if d is empty, make the apiCall
        d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/" + summId + getApiKey())
        dbcalls.addAccountToDB(d)   #store all the information for this account so we can store it's history
    return d

"""
Match endpoints. Do different things with matches.
"""

def getMatchList(accId,queries):
    d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accId + getApiKey() + queries)
    return d

def getMatchTimeline(matchId):
    #currently not stored in the local database
    d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/" + (str)(matchId) + getApiKey())
    return d

def getMatch(matchId):
    d = dbcalls.fetchMatch(matchId)
    if(not d):
        d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/matches/" + (str)(matchId) + getApiKey())
        dbcalls.addMatchToDB(d)
    return d

"""
Important methods built on top of riotapicalls that use the above endpoints to do useful things.
"""

def getMostRecentSeasonId():
    seasons = getSeasons()
    season = seasons[len(seasons)-1]
    return season["id"]

def getAllMatches(matchList):
    """
    Get all of the matches from a matchList. Defaults to the most recent season.
    """
    if(not matchList):
        return []
    seasonId = getMostRecentSeasonId()
    matches = []
    count = 0
    for match in matchList["matches"]:
        if((int)(match["season"]) == (int)(seasonId)):
            m = getMatch(match["gameId"])
            matches.append(m)
            count += 1
    return matches

def getMatchListByName(name,queries):
    summoner = getAccountByName(name)
    return getMatchList(summoner["accountId"],queries)

def getAllRankedMatchesByAccount(account):
    accId = account["accountId"]
    queries = "&queue=420"
    matchList = getMatchList(accId,queries)
    totalGames = matchList["totalGames"]
    
    matches = []
    count = 0
    while(count < totalGames):
        matches.extend(getAllMatches(matchList))
        count += 100
        queries = "&queue=420&beginIndex=" + (str)(count)
        matchList = getMatchList(accId,queries)
        totalGames = matchList["totalGames"]
        
    return matches
"""
old version that used loadFile and saveFile instead of the sqlite3 db
def getAllRankedMatchesByAccount(account):
    matches = []
    accId = account["accountId"]
    name = account["name"]
    seasonId = getMostRecentSeasonId()
    fileName = "summoners/"+name+"S"+(str)(seasonId)+".txt"
    
    f = loadFile(fileName)
    lastGameId = 0
    if(f and f[0]["seasonId"] == seasonId): #if the file is not empty and the seasonId is correct
        lastGameId = f[0]["matches"][0]["gameId"]
        print((str)(len(f[0]["matches"])) + " ranked matches already downloaded.")
    
    prevSize = 0
    queries = "&queue=420"
    matchList = getMatchList(accId,queries)
    totalGames = matchList["totalGames"]    #need to find the real amount of total games (accounting for season changes)
    
    print((str)(totalGames) + " total ranked games possible to download.")
    for num in range(0,(int)(totalGames/100)): #need the +1 because of integer division (truncation)
        matchList = checkGameIds(matchList,lastGameId)
        matches.extend(getAllMatches(matchList))
        if(not len(matches) == 100 + prevSize): #if we didn't add 100 matches, it's because we reached the end of the season, a duplicate match, or the last set of games
            break
        else:
            prevSize = len(matches)
            
        queries = "&queue=420&beginIndex=" + (str)((num+1)*100)
        matchList = getMatchList(accId,queries)
        
    matchesDownloaded = len(matches)
    if(not matches):    #if matches is empty
        print("No ranked matches downloaded.")
        return f[0]["matches"]
    else:
        print((str)(matchesDownloaded) + " ranked matches actually downloaded.")
        if(f and f[0]["seasonId"] == seasonId): #if the file is loaded and the seasonId matches
            matches.extend(f[0]["matches"])    #add back the matches we loaded in at the beginning
        
    saveFile(fileName,{"matches":matches,"seasonId":seasonId})
    return matches

def checkGameIds(matchList,lastGameId):
    newMatchList = {"matches":[]}
    for match in matchList["matches"]:
        if(match["gameId"] == lastGameId):  #found the last match that is the same, we don't need to keep going, so we're done
            break
        else:
            newMatchList["matches"].append(match)
    return newMatchList
"""

def getAccountsByNames(names):
    accounts = []
    for name in names:
        accounts.append(getAccountByName(name))
    return accounts