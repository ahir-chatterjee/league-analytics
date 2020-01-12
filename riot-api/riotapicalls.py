import requests
import json
import os
import time       
import dbcalls
        
API_KEY = ""
#API_RATE_LIMIT = 120    #a standard API_KEY refreshes every 2 minutes, or 120 seconds

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
            BAD_REQUEST = 400
            FORBIDDEN = 403
            NOT_FOUND = 404
            SERVER_ERROR = 500
            BAD_GATEWAY = 502
            UNAVAILABLE = 503
            GATEWAY_TIMEOUT = 504
            statusCode = d["status"]["status_code"]
            if(statusCode == RATE_LIMIT_EXCEEDED):
                #old way of doing this
                #global API_RATE_LIMIT
                #print("Rate limit exceeded, waiting for " + (str)(API_RATE_LIMIT) + " seconds.")
                #time.sleep(API_RATE_LIMIT)
                #request = requests.get(url)
                #d = json.loads(request.text)
                #common enough that we don't want to spam print status messages out
                time.sleep(5)
                return makeApiCall(url)
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
            elif(statusCode == BAD_REQUEST):
                return {}
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
    
def updateRunes(version):
    print("Updating runes...")
    d = makeApiCall("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/runesReforged.json" + getApiKey())
    if(d):
        dbcalls.updateRunes(d)
        print("runes successfully updated")
    else:
        print("Error with updating runes.")
    
def updateConstants():
    versions = getVersion()
    updatesNeeded = dbcalls.checkForUpdates(versions)   #list with three booleans, [champs,items,summoners]
    if(updatesNeeded[0]):
        updateChamps(versions["champion"])
    if(updatesNeeded[1]):
        updateItems(versions["item"])
    if(updatesNeeded[2]):
        updateSpells(versions["summoner"])
    updateRunes(versions["champion"])   #there's no way to be sure runes don't need an update, so update them everytime
    
"""
Summoner endpoints. Get an account's information by different methods.
"""
    
def getAccountByName(name):
    d = dbcalls.fetchAccountByName(name)
    if(not d):  #if d is empty, make the apiCall
        d = makeApiCall("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + getApiKey())
        if(not "puuid" in d):
            return d
        acc = dbcalls.fetchAccountByPuuid(d["puuid"])   #check for a potential name change
        if(acc):  #if acc is not empty, that means the user name changed
            if(not acc["name"] == d["name"]):
                print("name change found! From " + (str)(acc["name"]) + " to " + (str)(d["name"]))
                dbcalls.updateAccountName(name,d["puuid"])
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
    d = dbcalls.fetchTimeline(matchId)
    if(not d):
        d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/" + (str)(matchId) + getApiKey())
        dbcalls.addTimelineToDB(d,matchId)
    return d

def getMatch(matchId):
    d = dbcalls.fetchMatch(matchId)
    if(not d):
        d = makeApiCall("https://na1.api.riotgames.com/lol/match/v4/matches/" + (str)(matchId) + getApiKey())
        dbcalls.addMatchToDB(d)
        getMatchTimeline(matchId)
    return d

"""
League endpoints.
"""

def getLeagueExp(queue,tier,division,page):
    url = "https://na1.api.riotgames.com/lol/league-exp/v4/entries/"
    url += queue + "/" + tier + "/" + division + getApiKey() + "&page=" + (str)(page)
    print(url)
    return makeApiCall(url)

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

def getAccountsByNames(names):
    accounts = []
    for name in names:
        account = getAccountByName(name)
        if("puuid" in account):
            accounts.append(account)
    return accounts

def downloadFromLadder():
    queue = "RANKED_SOLO_5x5"
    tiers = ["CHALLENGER","GRANDMASTER","MASTER","DIAMOND","PLATINUM"]
    divisons = ["II","III","IV"]#["I","II","III","IV"]
    for tier in tiers:
        for division in divisons:
            page = 1
            league = getLeagueExp(queue,tier,division,page)
            while(league):
                for entry in league:
                    print(entry["summonerName"],end=", ")
                    account = getAccountByName(entry["summonerName"])
                    getAllRankedMatchesByAccount(account)
                page += 1
                print()
                #print()
                league = getLeagueExp(queue,tier,division,page)