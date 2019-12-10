import requests
import json
import os

API_KEY = ""

def saveFile(fileName, data, version):
    overWrite = False
    if(os.path.exists(fileName)):
        overwrite = True
    with open(fileName,'w') as outfile:
        wrapperList = []
        wrapperList.append(data)
        wrapperList.append(version)
        #format of wrapperList is [data,version]
        json.dump(wrapperList,outfile)

    if(overWrite):
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
    else:
        print("Could not find a file named " + fileName + ".")
        openFile.close()
    return wrapperList

def getApiKey():
    """
    Either loads in the API_KEY or just returns the value if already loaded.
    """
    if(len(API_KEY) == 0):
        fileName = "apikey.txt"
        if(os.path.exists("apikey.txt")):
            openFile = open(fileName,'r')
            API_KEY = openFile.readLine()
    return API_KEY

def getVersion():
    request = requests.get("https://ddragon.leagueoflegends.com/realms/na.json" + getApiKey())
    d = json.loads(request.text)
    return d["n"]

def updateChamps(version):
    f = loadFile("champs.txt")
    if(f[1] == version):
        print("champs.txt version up to date")
    else:
        request = requests.get("http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json" + getApiKey())
        d = json.loads(request.text)
        saveFile("champs.txt",champInfo,champVersion)
        print("champs.txt updated")

def updateConstants():
    version = getVersion()


"""
versionInfo = json.loads(requests.get("https://ddragon.leagueoflegends.com/realms/na.json" + api_key).text)["n"]
champVersion = versionInfo["champion"]
itemVersion = versionInfo["item"]
ssVersion = versionInfo["summoner"]

champInfo = {}
loadedInfo = loadFile("champs.txt")
if(loadedInfo[0] == champVersion):
    champInfo = loadedInfo[1]
    print("champs.txt version up to date")
else:
    champInfo = json.loads(requests.get("http://ddragon.leagueoflegends.com/cdn/" + champVersion + "/data/en_US/champion.json" + api_key).text)
    saveInfo("champs.txt",champInfo,champVersion)
    print("champs.txt updated")
    
itemInfo = {}
loadedInfo = loadFile("items.txt")
if(loadedInfo[0] == itemVersion):
    itemInfo = loadedInfo[1]
    print("items.txt version up to date")
else:
    itemInfo = json.loads(requests.get("http://ddragon.leagueoflegends.com/cdn/" + itemVersion + "/data/en_US/item.json" + api_key).text)
    print("items.txt updated")
    
ssInfo = {}
loadedInfo = loadFile("summonerSpells.txt")
if(loadedInfo[0] == itemVersion):
    ssInfo = loadedInfo[1]
    print("summonerSpells.txt version up to date")
else:
    ssInfo = json.loads(requests.get("http://ddragon.leagueoflegends.com/cdn/" + itemVersion + "/data/en_US/summoner.json" + api_key).text)
    saveInfo("summonerSpells.txt",ssInfo,ssVersion) 
    print("summonerSpells.txt updated")
    
loadedInfo = loadFile("ssId.txt")
ssDict = {}
if(loadedInfo[0] == champVersion):
    ssDict = loadedInfo[1]
    print("champId.txt version up to date")
else:
    for ss in ssInfo["data"]:
        ssDict[ssInfo["data"][ss]["key"]] = ssInfo["data"][ss]["name"]
    saveInfo("ssId.txt",ssDict,ssVersion)
    print("ssId.txt updated")
    champDict = loadFile("ssId.txt")[1]
    
loadedInfo = loadFile("champId.txt")
champDict = {}
if(loadedInfo[0] == champVersion):
    champDict = loadedInfo[1]
    print("champId.txt version up to date")
else:
    for champ in champInfo["data"]:
        champDict[champInfo["data"][champ]["key"]] = champInfo["data"][champ]["name"]
    saveInfo("champId.txt",champDict,champVersion)
    print("champId.txt updated")
    champDict = loadFile("champId.txt")[1]

loadedInfo = loadFile("SRitems.txt")
itemDict = {}
if(loadedInfo[0] == itemVersion):
    itemDict = loadedInfo[1]
    print("SRitems.txt version up to date")
else:
    for itemNum in itemInfo["data"]:
        item = itemInfo["data"][itemNum]
        if(item["maps"]["11"] == True and item["gold"]["purchasable"]):
            itemDict[item["name"]] = itemNum
    itemDict.pop("Archangel's Staff (Quick Charge)")
    itemDict.pop("Broken Stopwatch")
    itemDict.pop("Entropy Field")
    itemDict.pop("Flash Zone")
    itemDict.pop("Manamune (Quick Charge)")
    itemDict.pop("Port Pad")
    itemDict.pop("Rod of Ages (Quick Charge)")
    itemDict.pop("Shield Totem")
    itemDict.pop("Siege Ballista")
    itemDict.pop("Siege Refund")
    itemDict.pop("Tear of the Goddess (Quick Charge)")
    itemDict.pop("Tower: Beam of Ruination")
    itemDict.pop("Tower: Storm Bulwark")
    itemDict.pop("Vanguard Banner")
    tempDict = {}
    for key in itemDict:
        tempDict[itemDict[key]] = key
    itemDict = tempDict
    saveInfo("SRitems.txt",itemDict,itemVersion)
    print("SRitems.txt updated")
    itemDict = loadFile("SRitems.txt")[1]
"""