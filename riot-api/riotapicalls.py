import requests
import json
import os
import time        
        
API_KEY = ""
API_RATE_LIMIT = 120

def saveFile(fileName, data, version):
    overwrite = False
    if(os.path.exists(fileName)):
        overwrite = True
    with open(fileName,'w') as outfile:
        wrapperList = []
        wrapperList.append(data)
        wrapperList.append(version)
        #format of wrapperList is [data,version]
        json.dump(wrapperList,outfile)
    if(overwrite):
        print(fileName + " saved and overwritten successfully.")
    else:
        print(fileName + " saved successfully.")

def loadFile(fileName):
    """
    When saved, our output is a list of [data,version], so we 
    need to return a list with special values to be certain it 
    worked and doesn't break.
    """
    wrapperList = [-1,-1] 
    if(os.path.exists(fileName)):
        tempStr = ""
        openFile = open(fileName,'r')
        for line in openFile:
            tempStr += line
        if(len(tempStr) > 0):
            wrapperList = json.loads(tempStr)  
        else:
            print(fileName + " is an empty file.")
        openFile.close()
    else:
        print("Could not find a file named " + fileName + ".")
    return wrapperList

def getApiKey():
    """
    Either loads in the API_KEY or just returns the value if already loaded.
    """
    global API_KEY
    if(len(API_KEY) == 0):
        fileName = "apikey.txt"
        if(os.path.exists("apikey.txt")):
            openFile = open(fileName,'r')
            API_KEY = openFile.read()
        else:
            print("apikey.txt does not exist. Make one using your own apikey from https://developer.riotgames.com/")
    return "?api_key=" + API_KEY

def makeApiCall(url):
    """
    Given a url/endpoint, it will make the call, but handle any error messages
    """
    request = requests.get(url)
    d = json.loads(request.text)
    
    if(type(d) is dict):
        if(not d.get("status") == None):    #if we have a status on our hands
            RATE_LIMIT_EXCEEDED = 429
            FORBIDDEN = 403
            NOTFOUND = 404
            statusCode = d["status"]["status_code"]
            if(statusCode == RATE_LIMIT_EXCEEDED):
                global API_RATE_LIMIT
                print("Rate limit exceeded, waiting for " + (str)(API_RATE_LIMIT) + " seconds.")
                time.sleep(API_RATE_LIMIT)
                request = requests.get(url)
                d = json.loads(request.text)
            elif(statusCode == FORBIDDEN):
                print("API_KEY is incorrect. Please update your apikey.txt from https://developer.riotgames.com")
            elif(statusCode == NOTFOUND):
                print("No data was found using the following url: " + url)
            else:
                print("Unknown status code: " + (str)(statusCode))
    
    return d

def getSeasons():
    d = makeApiCall("http://static.developer.riotgames.com/docs/lol/seasons.json")
    return d
    
def getVersion():
    d = makeApiCall("https://ddragon.leagueoflegends.com/realms/na.json")
    return d["n"]

def updateChamps(version):
    f = loadFile("champs.txt")
    if(f[1] == version):
        print("champs.txt version up to date")
    else:
        d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json" + getApiKey())
        saveFile("champs.txt",d,version)
        print("champs.txt updated")
        
def updateItems(version):
    f = loadFile("items.txt")
    if(f[1] == version):
        print("items.txt version up to date")
    else:
        d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/item.json" + getApiKey())
        saveFile("items.txt",d,version)
        print("items.txt updated")
        
def updateSpells(version):
    f = loadFile("spells.txt")
    if(f[1] == version):
        print("spells.txt version up to date")
    else:
        d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/summoner.json" + getApiKey())
        saveFile("spells.txt",d,version)
        print("spells.txt updated")

def updateConstants():
    versions = getVersion()
    updateChamps(versions["champion"])
    updateItems(versions["item"])
    updateSpells(versions["summoner"])
    
"""
Summoner entpoints. Get an account's information by different methods.
"""
    
def getAccountByName(name):
    d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + getApiKey())
    return d

def getAccountByAccId(accId):
    d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-account/" + accId + getApiKey())
    return d

def getAccountByPPUID(ppuid):
    d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-ppuid/" + ppuid + getApiKey())
    return d

def getAccountBySummId(summId):
    d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/" + summId + getApiKey())
    return d

"""
Match endpoints. Do different things with matches.
"""

def getMatchList(accId,queries):
    d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accId + getApiKey() + queries)
    return d

def getMatchTimeline():
    d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/" + matchId + getApiKey())
    return d

def getMatch(matchId):
    d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/matches/" + (str)(matchId) + getApiKey())
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
    seasonId = getMostRecentSeasonId()
    matches = []
    count = 0
    for match in matchList["matches"]:
        m = getMatch(match["gameId"])
        matches.append(m)
        count += 1
    return matches

def getMatchListByName(name,queries):
    summoner = getAccountByName(name)
    return getMatchList(summoner["accountId"],queries)

def getAllRankedMatchesByAccount(account):
    matches = []
    accId = account["accountId"]
    
    prevSize = 0
    queries = "&queue=420"
    matchList = getMatchList(accId,queries)
    totalGames = matchList["totalGames"]    #need to find the real amount of total games (accounting for season changes)
    
    print(totalGames)
    for num in range(0,(int)(totalGames/100)): #need the +1 because of integer division (truncation)
        matches.extend(getAllMatches(matchList))
        if(not len(matches) == 100 + prevSize): #if we didn't add 100 matches, it's because we reached the end of the season
            print(len(matches))
            return matches
        else:
            prevSize = len(matches)
        queries = "&queue=420&beginIndex=" + (str)((num+1)*100)
        matchList = getMatchList(accId,queries)
    return matches

def getAccountsByNames(names):
    accounts = []
    for name in names:
        accounts.append(getAccountByName(name))
    return accounts
