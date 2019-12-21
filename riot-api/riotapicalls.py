import requests
import json
import os
import time

class apiCallList():
    def __init__(self):
        self.list = []  #filled with apiCalls, up to 200
        self.API_RATE_LIMIT = 120   #API rate limit for our key type (standard access)
        self.API_CALL_LIMIT = 200   #API call limit for our key type (standard access)
    def makeCall(self):
        if(len(self.list) == self.API_CALL_LIMIT-5):   #if we're at the API_CALL_LIMIT, then we need to evict the first call. A little less to be safe
            now = time.time()
            timeDelta = now-self.list[0]
            if(timeDelta <= self.API_RATE_LIMIT+5):   #we can only evict the first call if it's been long enough, otherwise we need to wait. we add 5 seconds to be safe, though it does make it slower overall
                print("about to wait on an api call for  " + (str)(timeDelta) + " seconds.")
                time.sleep(timeDelta)
                print("waited on an api call for " + (str)(timeDelta) + " seconds.")
            self.list.pop(0)    #evict the first call since it's been long enough
        self.list.append(time.time())
        print(len(self.list))
        
        
API_KEY = ""
API_CALL_LIST = apiCallList()

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
            print("apikey.txt does not exist")
    return "?api_key=" + API_KEY

def getVersion():
    API_CALL_LIST.makeCall()
    request = requests.get("https://ddragon.leagueoflegends.com/realms/na.json" + getApiKey())
    d = json.loads(request.text)
    return d["n"]

def updateChamps(version):
    f = loadFile("champs.txt")
    if(f[1] == version):
        print("champs.txt version up to date")
    else:
        API_CALL_LIST.makeCall()
        request = requests.get("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json" + getApiKey())
        d = json.loads(request.text)
        saveFile("champs.txt",d,version)
        print("champs.txt updated")
        
def updateItems(version):
    f = loadFile("items.txt")
    if(f[1] == version):
        print("items.txt version up to date")
    else:
        API_CALL_LIST.makeCall()
        request = requests.get("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/item.json" + getApiKey())
        d = json.loads(request.text)
        saveFile("items.txt",d,version)
        print("items.txt updated")
        
def updateSpells(version):
    f = loadFile("spells.txt")
    if(f[1] == version):
        print("spells.txt version up to date")
    else:
        API_CALL_LIST.makeCall()
        request = requests.get("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/summoner.json" + getApiKey())
        d = json.loads(request.text)
        saveFile("spells.txt",d,version)
        print("spells.txt updated")

def updateConstants():
    versions = getVersion()
    updateChamps(versions["champion"])
    updateItems(versions["item"])
    updateSpells(versions["summoner"])
    
def getAccountByName(name):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + getApiKey())
    d = json.loads(request.text)
    return d

def getAccountByAccId(accId):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-account/" + accId + getApiKey())
    d = json.loads(request.text)
    return d

def getAccountByPPUID(ppuid):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-ppuid/" + ppuid + getApiKey())
    d = json.loads(request.text)
    return d

def getAccountBySummId(summId):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/" + summId + getApiKey())
    d = json.loads(request.text)
    return d

def getMatchList(accId,queries):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accId + getApiKey() + queries)
    d = json.loads(request.text)
    return d

def getMatchListByName(name,queries):
    summoner = getAccountByName(name)
    return getMatchList(summoner["accountId"],queries)

def getMatch(matchId):
    API_CALL_LIST.makeCall()
    request = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + (str)(matchId) + getApiKey())
    d = json.loads(request.text)
    return d

def getAllMatches(matchList):
    matches = []
    count = 0
    for match in matchList["matches"]:
        m = getMatch(match["gameId"])
        matches.append(m)
        print("Got match #" + (str)(count))
        count += 1
    return matches

def getLast100GamesByName(name,queries):
    matchList = getMatchListByName(name,queries)
    return getAllMatches(matchList)

updateConstants()
ahir = getLast100GamesByName("CrusherCake","")
saveFile("ahir.txt",ahir,-1)
print("doing denis")
denis = getLast100GamesByName("Avoxin","")
saveFile("denis.txt",denis,-1)